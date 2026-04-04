from __future__ import annotations

import time
import logging

from sat1_control.led.animator import Animator
from sat1_control.led.patterns import DefaultPattern
from sat1_control._xmos import _XMOSTransport

log = logging.getLogger(__name__)

_PATTERNS = {"default": DefaultPattern}


class LedController:
    """
    Controls LED ring animations for voice assistant states.

    Args:
        pattern:   Animation pattern to use. Currently "default".
        timeout:   Seconds before an animation auto-stops. Default 60.
        transport: Shared _XMOSTransport instance. Created automatically if not given.

    Example::

        led = LedController(timeout=30)
        led.listen()
        led.wait()
        led.off()
    """

    def __init__(self, pattern: str = "default", timeout: int = 60, transport: _XMOSTransport | None = None):
        self.animator = Animator(transport=transport)
        self.animator.default_timeout = timeout
        self.pattern = self._load_pattern(pattern)

    @property
    def animation_is_running(self) -> bool:
        return self.animator.is_running

    def on_start(self, **kwargs):
        self.animator.run(self.pattern.on_start, **kwargs)

    def on_error(self, **kwargs):
        self.animator.run(self.pattern.on_error, **kwargs)

    def listen(self, **kwargs):
        self.animator.run(self.pattern.listen, **kwargs)

    def think(self, **kwargs):
        self.animator.run(self.pattern.think, **kwargs)

    def speak(self, **kwargs):
        self.animator.run(self.pattern.speak, **kwargs)

    def on_mute(self, **kwargs):
        self.animator.run(self.pattern.on_mute, **kwargs)

    def on_volume_change(self, **kwargs):
        self.animator.run(self.pattern.on_volume_change, reset_leds=False, timeout=5, **kwargs)

    def off(self):
        self.animator.stop()

    def stop(self):
        self.animator.stop()

    def wait(self):
        while self.animator.is_running:
            time.sleep(0.05)

    def set_pattern(self, pattern: str):
        self.pattern = self._load_pattern(pattern)

    def _load_pattern(self, name: str):
        cls = _PATTERNS.get(name)
        if cls is None:
            raise ValueError(f"Unknown pattern {name!r}. Available: {list(_PATTERNS)}")
        return cls(self.animator)
