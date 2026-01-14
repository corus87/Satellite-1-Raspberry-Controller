import spidev
from threading import Lock

SPI_SPEED_HZ = 100_000

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
        self.spi.max_speed_hz = SPI_SPEED_HZ
        self.spi.mode = 0b00

        self.dc_status = [0, 0, 0, 0]
        self._initialized = True

    def write(self, res_id, command, payload=None):
        payload = payload or []
        tx = [res_id, command, len(payload), *payload]
        while len(tx) < 7:
            tx.append(0)

        with self._lock:
            result = self.spi.xfer2(tx)

        return result

    def request_status_register_update(self):
        tx = [1, 0x80, 0, 0, 0, 0, 0]

        with self._lock:
            rx = self.spi.xfer2(tx)

        status = rx[2:6]

        if status == [0, 0, 0, 0]:
            return False  # no update

        self.dc_status = status
        return True

    def get_status_register(self, index: int) -> int:
        return self.dc_status[index]
