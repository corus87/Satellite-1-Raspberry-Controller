from smbus2 import SMBus


class I2cInterface:
    def __init__(self, address):
        self.address = address

    def write(self, register, data):
        with SMBus(1) as bus:
            bus.write_byte_data(self.address, register, data)

    def read(self, register):
        with SMBus(1) as bus:
            return bus.read_byte_data(self.address, register)