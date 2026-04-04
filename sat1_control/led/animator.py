from __future__ import annotations

import time
import threading
import logging
from typing import Callable

from sat1_control._xmos import _XMOSTransport

log = logging.getLogger(__name__)

NUM_LEDS = 24


class Animator:
    """
    Drives the 24-LED WS2812 ring on the Satellite1 HAT.

    Colors are (R, G, B) tuples 0–255. Brightness is 0–100, applied at render time.
    Animations run in a daemon thread and stop automatically after `default_timeout` seconds.
    """

    def __init__(self, transport: _XMOSTransport | None = None):
        self._xmos = transport or _XMOSTransport()
        self.num_leds = NUM_LEDS
        self.image: list[tuple[int, int, int]] = [(0, 0, 0)] * self.num_leds
        self._brightness = 100
        self._is_running = False
        self._animation_thread: threading.Thread | None = None
        self._timeout_thread: threading.Thread | None = None
        self.default_timeout = 60

    @property
    def is_running(self) -> bool:
        return self._is_running

    def run(self, func: Callable, *, reset_leds: bool = True, timeout: int | None = None, **kwargs):
        if self._is_running:
            self.stop(reset_leds)

        if self._timeout_thread and self._timeout_thread.is_alive():
            self._timeout_thread.join(timeout=1.0)

        if reset_leds:
            self.image = [(0, 0, 0)] * self.num_leds

        effective_timeout = timeout if isinstance(timeout, int) else self.default_timeout
        self._is_running = True

        self._timeout_thread = threading.Thread(
            target=self._run_timeout, args=(effective_timeout,), daemon=True
        )
        self._timeout_thread.start()

        self._animation_thread = threading.Thread(
            target=func, kwargs=kwargs, daemon=True, name="sat1-animation"
        )
        self._animation_thread.start()

    def stop(self, clear_leds: bool = True):
        self._is_running = False
        if self._animation_thread and self._animation_thread.is_alive():
            self._animation_thread.join(timeout=2.0)
        if clear_leds:
            self.clear()

    def show(self):
        brightness = max(0.0, min(1.0, self._brightness / 100))
        buf = bytearray()
        for r, g, b in self.image:
            buf.extend((int(g * brightness), int(r * brightness), int(b * brightness)))
        self._xmos.write_leds(bytes(buf))

    def clear(self):
        self.image = [(0, 0, 0)] * self.num_leds
        self.show()

    def set_color(self, index: int, color: tuple[int, int, int]):
        self.image[index] = color

    def fill(self, color: tuple[int, int, int]):
        self.image = [color] * self.num_leds

    def set_brightness(self, value: int):
        self._brightness = max(0, min(100, value))

    def get_brightness(self) -> int:
        return self._brightness

    def _run_timeout(self, seconds: int):
        deadline = time.monotonic() + seconds
        while self._is_running:
            if time.monotonic() >= deadline:
                self.stop()
                break
            time.sleep(0.1)

    def rainbow_cycle(self, speed: int = 1000, repeat: int = 0):
        count = 0
        while self._is_running:
            if repeat > 0 and count >= repeat:
                self._is_running = False
                break
            for j in range(255):
                for i in range(self.num_leds):
                    if not self._is_running:
                        return
                    self.image[i] = self._wheel((i * 256 // self.num_leds + j) & 255)
                self.show()
                time.sleep(1.0 / max(1, abs(speed)))
            if repeat > 0:
                count += 1

    def breath(self, color=(0, 0, 200), min_brightness=5, max_brightness=20, speed=40):
        self.image = [color] * self.num_leds
        self.set_brightness(min_brightness)
        direction = 1
        while self._is_running:
            bri = self.get_brightness()
            if bri >= max_brightness:
                direction = -1
            elif bri <= min_brightness:
                direction = 1
            self.set_brightness(bri + direction)
            self.show()
            time.sleep(1.0 / max(1, abs(speed)))

    def rotate(self, color=(0, 0, 200), speed=30, trail=0, brightness=50):
        self.image = [(0, 0, 0)] * self.num_leds
        self.image[0] = color
        if trail > 0:
            for i in range(1, self.num_leds // trail):
                self.image[i] = color
        self.set_brightness(brightness)
        while self._is_running:
            time.sleep(1.0 / max(1, abs(speed)))
            self.image.insert(0, self.image.pop())
            self.show()

    def blink(self, color=(200, 0, 0), min_brightness=5, max_brightness=30, speed=100, repeat=0):
        self.image = [color] * self.num_leds
        self.set_brightness(min_brightness)
        count = 0
        while self._is_running:
            if repeat > 0 and count >= repeat:
                self._is_running = False
                break
            while self._is_running and self.get_brightness() < max_brightness:
                self.set_brightness(self.get_brightness() + 1)
                self.show()
                time.sleep(1.0 / max(1, abs(speed)))
            while self._is_running and self.get_brightness() > min_brightness:
                self.set_brightness(self.get_brightness() - 1)
                self.show()
                time.sleep(1.0 / max(1, abs(speed)))
            if repeat > 0:
                count += 1

    def segment(self, color=(0, 100, 0), num_leds=10, brightness=20):
        self.image = [(0, 0, 0)] * self.num_leds
        for i in range(min(num_leds, self.num_leds)):
            self.image[i] = color
        self.set_brightness(brightness)
        self.show()

    @staticmethod
    def _wheel(pos: int) -> tuple[int, int, int]:
        if pos < 85:
            return int(pos * 3), int(255 - pos * 3), 0
        elif pos < 170:
            pos -= 85
            return int(255 - pos * 3), 0, int(pos * 3)
        else:
            pos -= 170
            return 0, int(pos * 3), int(255 - pos * 3)
