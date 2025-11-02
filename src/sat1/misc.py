from sat1.utils.spi_interface import SpiInterface

DFU_CONTROLLER_SERVICER_RESID = 240
CONTROL_CMD_READ_BIT = 0x80

class Misc:
    def __init__(self):
        self.spi = SpiInterface()
    
    def get_version(self):
        rx = self.spi.write(DFU_CONTROLLER_SERVICER_RESID, 88 | CONTROL_CMD_READ_BIT, [1])
        print(rx)