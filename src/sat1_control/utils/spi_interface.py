import spidev
from threading import Lock

SPI_SPEED_STATUS = 100_000      # stable for GPIO / status
SPI_SPEED_LED    = 8_000_000    # fast for LED animations

CONTROL_RESOURCE_ID = 1
CONTROL_CMD_READ_BIT = 0x80


class SpiInterface:
    _instance = None
    _initialized = False
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.mode = 0b00
        self.spi.bits_per_word = 8
        self.spi.max_speed_hz = SPI_SPEED_STATUS

        self.dc_status = [0, 0, 0, 0]
        self._initialized = True

    def _set_speed(self, hz: int):
        if self.spi.max_speed_hz != hz:
            self.spi.max_speed_hz = hz

    def write(self, res_id, command, payload=None):
        payload = payload or []
        tx = [res_id, command, len(payload), *payload]

        while len(tx) < 7:
            tx.append(0)

        with self._lock:
            self._set_speed(SPI_SPEED_LED)
            result = self.spi.xfer2(tx)
            self._set_speed(SPI_SPEED_STATUS)

        return result

    def request_status_register_update(self):
        tx = [
            CONTROL_RESOURCE_ID,
            CONTROL_CMD_READ_BIT,
            0, 0, 0, 0, 0
        ]

        with self._lock:
            self._set_speed(SPI_SPEED_STATUS)
            rx = self.spi.xfer2(tx)

        status = rx[2:6]

        # ignore invalid / empty frames
        if status == [0, 0, 0, 0]:
            return False

        self.dc_status = status
        return True

    def get_status_register(self, index: int) -> int:
        return self.dc_status[index]
