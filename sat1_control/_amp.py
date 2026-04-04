import logging
from smbus2 import SMBus

log = logging.getLogger(__name__)

_ADDR = 0x3F
_BUS  = 1

_PAGE   = 0x00
_RESET  = 0x01
_MODE   = 0x02
_CHNL   = 0x03
_DCBLK  = 0x04
_TDM2   = 0x0A
_TDM5   = 0x0E
_TDM6   = 0x0F
_DVC    = 0x1A
_IMSK1  = 0x3C
_IMSK2  = 0x40
_IMSK3  = 0x41
_IMSK4  = 0x3D
_ICLK   = 0x5C
_UVLO   = 0x71
_P1_LSR   = 0x19
_P1_INI0  = 0x17
_P1_INI1  = 0x21
_P1_INI2  = 0x35
_PFD_INI3 = 0x3E

_MODE_ACTIVE   = 0x00
_MODE_SHUTDOWN = 0x02
_BOP_SRC       = 0x80
_MODE_MASK     = 0x07
_AMP_LVL_SHIFT = 1
_AMP_LVL_MASK  = 0x1F << 1
_CDS_SHIFT     = 6
_CDS_MASK      = 0x03 << 6
_VBAT_SHIFT    = 7
_TDM_MIX       = 0x03 << 4
_TDM_W32       = 0x03 << 2
_TDM_S32       = 0x02
_DVC_MUTE      = 0xC9
_DVC_MAX       = 0xC8

_POWER_MODES = [(2, 0), (0, 0), (3, 1), (1, 0)]


class _TAS2780:
    def __init__(self, i2c_bus: int = _BUS, address: int = _ADDR,
                 amp_level: int = 8, power_mode: int = 0):
        self._bus       = SMBus(i2c_bus)
        self._addr      = address
        self.amp_level  = amp_level
        self.power_mode = power_mode
        self._volume: float = 0.8
        self._muted: bool   = False

    def close(self):
        self._bus.close()

    def setup(self):
        self._init()
        self._w(_MODE, (_BOP_SRC & ~_MODE_MASK) | _MODE_SHUTDOWN)

    def activate(self):
        self._init()
        self._write_volume()
        self._w(_MODE, (_BOP_SRC & ~_MODE_MASK) | _MODE_ACTIVE)

    def deactivate(self):
        self._w(_MODE, (_BOP_SRC & ~_MODE_MASK) | _MODE_SHUTDOWN)

    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))
        if not self._muted:
            self._write_volume()

    def mute_on(self):
        self._muted = True
        self._w(_DVC, _DVC_MUTE)

    def mute_off(self):
        self._muted = False
        self._write_volume()

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def is_muted(self) -> bool:
        return self._r(_DVC) == _DVC_MUTE

    @property
    def is_active(self) -> bool:
        return (self._r(_MODE) & _MODE_MASK) == _MODE_ACTIVE

    def _init(self):
        self._w(_PAGE, 0x00)
        self._w(_RESET, 0x01)

        chip_id = self._r(0x05)
        if chip_id != 0x41:
            raise RuntimeError(f"TAS2780 not found (chip id 0x{chip_id:02X})")

        self._w(_TDM5, 0x44)
        self._w(_TDM6, 0x40)

        self._w(_PAGE, 0x01)
        self._w(_P1_LSR,  0x00)
        self._w(_P1_INI0, 0xC8)
        self._w(_P1_INI1, 0x00)
        self._w(_P1_INI2, 0x74)

        self._w(_PAGE, 0xFD)
        self._w(0x0D, 0x0D)
        self._w(_PFD_INI3, 0x4A)
        self._w(0x0D, 0x00)

        self._w(_PAGE, 0x00)
        self._w(_UVLO, 0x03)
        self._w(_IMSK1, 0xFF)
        self._w(_IMSK2, 0xFF)
        self._w(_IMSK3, 0xFF)
        self._w(_IMSK4, 0xFF)
        self._w(_ICLK, self._r(_ICLK) & ~0x03)
        self._set_power_mode()
        self._apply_amp_level()

    def _set_power_mode(self):
        cds, vbat = _POWER_MODES[self.power_mode]
        self._w(_CHNL, (self._r(_CHNL) & ~_CDS_MASK) | (cds << _CDS_SHIFT))
        self._w(_DCBLK, (self._r(_DCBLK) & ~(1 << _VBAT_SHIFT)) | (vbat << _VBAT_SHIFT))

    def _apply_amp_level(self):
        val = (self._r(_CHNL) & ~_AMP_LVL_MASK) | (self.amp_level << _AMP_LVL_SHIFT)
        self._w(_CHNL, val)
        self._w(_TDM2, _TDM_MIX | _TDM_W32 | _TDM_S32)

    def _write_volume(self):
        code = max(0, min(_DVC_MAX, int(round((1.0 - self._volume) * 100))))
        self._w(_DVC, code)

    def _w(self, reg: int, val: int):
        try:
            self._bus.write_byte_data(self._addr, reg, val)
        except OSError as e:
            log.error("TAS2780 write 0x%02X: %s", reg, e)

    def _r(self, reg: int) -> int:
        try:
            return self._bus.read_byte_data(self._addr, reg)
        except OSError as e:
            log.error("TAS2780 read 0x%02X: %s", reg, e)
            return 0
