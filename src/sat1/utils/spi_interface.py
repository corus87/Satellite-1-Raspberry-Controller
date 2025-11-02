import spidev

SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED_HZ = 10000000 #10 MHz
REGISTER_LEN = 4
CONTROL_CMD_READ_BIT = 0x80
DC_STATUS_REGISTER_LEN = 4

class SpiInterface:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = SPI_SPEED_HZ
        self.spi.mode = 0b00

    def write(self, res_id, command, payload=[]):
        tx_buffer = [res_id, command, len(payload)]
        tx_buffer.extend(payload)
        while len(tx_buffer) < DC_STATUS_REGISTER_LEN + 3:
            tx_buffer.append(0)
        return self.spi.xfer2(tx_buffer)
    
    def request_status_register_update(self):
        rx = self.write(0, 0)
        return rx[2:2 + DC_STATUS_REGISTER_LEN]
