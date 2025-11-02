from sat1.utils.spi_interface import SpiInterface

LED_RES_ID = 200
CMD_WRITE_LED_RING_RAW = 0

class Interface:
    num_leds = 24

    def __init__(self):
        self.spi = SpiInterface()
        self.colors = [(0, 0, 0) for _ in range(self.num_leds)]
        self.set_brightness(1)

    def clear_leds(self):
        for led in range(self.num_leds):
            self.colors[led] = (0,0,0)
        self.show()

    def set_brightness(self, value):
        self.brightness = value

    def get_brightness(self):
        return self.brightness

    def show(self):
        payload = bytearray()
        brightness = min(max(self.brightness / 100, 0.0), 1.0)

        for r, g, b in self.colors:
            payload.extend((
                int(g * brightness),
                int(r * brightness),
                int(b * brightness)
            ))

        self.spi.write(LED_RES_ID, CMD_WRITE_LED_RING_RAW, payload)

    def set_color(self, led_idx, color):
        self.colors[led_idx] = color

    def fill(self, color):
        for led in range(self.num_leds):
            self.colors[led] = color 
