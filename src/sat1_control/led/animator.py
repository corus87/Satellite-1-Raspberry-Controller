
from sat1_control.led.interface import Interface

from time import sleep, time
from threading import Thread

class Animator(Interface):
    def __init__(self, timeout):
        super(Animator, self).__init__()
        self.is_running = False
        self.animation_thread = None
        self.timeout_thread = None
        self.timeout = timeout

    def run(self, func):
        if self.is_running:
            self.stop()

        if self.timeout_thread:
            while self.timeout_thread.is_alive():
                sleep(0.01)

        self.image = [(0, 0, 0) for _ in range(self.num_leds)]

        self.is_running = True
        
        self.timeout_thread = Thread(target=self.timeout_timer, daemon=True)
        self.timeout_thread.start()

        self.animation_thread = Thread(target=func, daemon=True)
        self.animation_thread.start()

    def timeout_timer(self):
        timeout = time() + self.timeout
        while self.is_running:
            if timeout < time():
                break
            sleep(0.1)
        self.stop()

    def wheel(self, pos):
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b)

    def rainbow_cycle(self, speed=1000, repeat=0):
        count = 0
        while self.is_running:

            if count > repeat:
                self.is_running = False

            for j in range(255):
                for i in range(self.num_leds):
                    if not self.is_running:
                        return

                    pixel_index = (i * 256 // self.num_leds) + j
                    self.set_color(i, self.wheel(pixel_index & 255))
                    
                self.show()
                sleep(1.0 / abs(speed))

            if repeat > 0:
                count += 1

    def breath(self, color=(0, 0, 200), min_brightness=5, max_brightness=20, speed=40):
        for i in range(self.num_leds):
            self.image[i] = color
        
        self.set_brightness(min_brightness)

        direction = 1
        while self.is_running:
            bri = self.get_brightness()
            if bri >= max_brightness:
                direction = -1
            elif bri <= min_brightness:
                direction = 1

            self.set_brightness(bri + direction)
            self.set_image()

            sleep(1.0 / abs(speed))

    def rotate(self, color=(0, 0, 200), speed=30, trail=0, brightness=50):
        self.image[0] = color

        if trail > 0:
            _trail = int(self.num_leds / trail)
            for i in range(1, _trail):
                self.image[i] = color

        while self.is_running:
            sleep(1.0 / abs(speed))
            self.image.insert(0, self.image.pop())
            self.set_image()
            
    def blink(self, color, min_brightness=5, max_brightness=30, speed=100, repeat=0):
        for i in range(self.num_leds):
            self.image[i] = color

        self.set_brightness(min_brightness)
        count = 0

        while self.is_running:

            if count > repeat:
                self.is_running = False

            bri = self.get_brightness()
            
            while self.is_running and bri < max_brightness:
                bri = self.get_brightness()                 
                self.set_brightness(bri + 1)
                self.set_image()
                sleep(1.0 / abs(speed))

            while self.is_running and bri > min_brightness:
                bri = self.get_brightness()
                self.set_brightness(bri - 1)
                self.set_image()
                sleep(1.0 / abs(speed))

            if repeat > 0:
                count += 1

    def stop(self):
        self.is_running = False
        if self.animation_thread:
            while self.animation_thread.is_alive():
                sleep(0.01)

        self.clear_leds()
        
    def set_image(self):
        for led, color in enumerate(self.image[:self.num_leds]):
            self.set_color(led, color)
    
        self.show()
