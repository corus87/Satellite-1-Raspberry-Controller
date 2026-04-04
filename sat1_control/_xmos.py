import logging
from time import sleep
from threading import Lock

import spidev

log = logging.getLogger(__name__)

_CMD_READ_BIT = 0x80
_CNTRL_RES_ID = 0x01
_RET_IGNORED = 0x07
_STATUS_REG_LEN = 4

LED_RES_ID = 200
LED_CMD = 0x00


class _XMOSTransport:
    def __init__(self, bus: int = 0, device: int = 0, speed_hz: int = 8_000_000):
        self._lock = Lock()
        self._status = bytearray(_STATUS_REG_LEN)

        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)
        self._spi.mode = 0b11
        self._spi.bits_per_word = 8
        self._spi.max_speed_hz = speed_hz

    def close(self):
        self._spi.close()

    def write_leds(self, grb_buf: bytes) -> bool:
        tx = [LED_RES_ID, LED_CMD, len(grb_buf), *grb_buf]
        with self._lock:
            self._spi.xfer2(tx)
        return True

    def request_status_update(self) -> bool:
        tx = [_CNTRL_RES_ID, _CMD_READ_BIT, 0, 0, 0, 0, 0]
        with self._lock:
            rx = self._spi.xfer2(tx)
        status = rx[2:2 + _STATUS_REG_LEN]
        if all(b == 0 for b in status):
            return False
        self._status[:] = status
        return True

    def get_status(self, index: int) -> int:
        return self._status[index]
