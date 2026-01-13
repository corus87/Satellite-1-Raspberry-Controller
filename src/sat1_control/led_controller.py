import queue as Queue
from threading import Thread
from dataclasses import dataclass
from time import sleep
from sat1_control.led.animator import Animator

@dataclass
class Pattern:
    func: callable
    kwargs: dict

class LedController(Thread):
    def __init__(self, pattern="default", 
                       timeout=60):
        super(LedController, self).__init__(daemon=True)
        self.queue = Queue.Queue()
        self.animator = Animator()
        self.animator.default_timeout = timeout
        self.pattern = None
        self.is_running = False
        self.set_pattern(pattern) 
        
    def run(self):
        self.is_running = True
        while self.is_running:
            pattern = self.queue.get()
            self.animator.run(pattern.func, **pattern.kwargs)

    def _dispatch(self, func, *, blocking=False, **kwargs):
        pattern = Pattern(func=func, kwargs=kwargs)
        if blocking:
            self.animator.run(pattern.func, **pattern.kwargs)
            while self.animator.is_running:
                sleep(0.1)
        else:
            self.queue.put(pattern)

    def on_start(self, **kwargs):
        self._dispatch(self.pattern.on_start, **kwargs)

    def on_error(self, **kwargs):
        self._dispatch(self.pattern.on_error, **kwargs)

    def listen(self, **kwargs):
        self._dispatch(self.pattern.listen, **kwargs)

    def think(self, **kwargs):
        self._dispatch(self.pattern.think, **kwargs)

    def speak(self, **kwargs):
        self._dispatch(self.pattern.speak, **kwargs)

    def on_mute(self, **kwargs):
        self._dispatch(self.pattern.on_mute, **kwargs)

    def on_volume_change(self, **kwargs):
        self._dispatch(self.pattern.on_volume_change, **kwargs)

    def off(self):
        self.animator.stop()

    def set_pattern(self, pattern):
        if pattern == "default":
            from sat1_control.led.pattern.default_pattern import DefaultPattern
            self.pattern = DefaultPattern(self.animator)
        else:
            raise ValueError(f"Pattern {pattern} not found")

    def stop(self):
        self.off()
        self.is_running = False

    @property
    def animation_is_running(self):
        if (
            self.animator.animation_thread and
            self.animator.animation_thread.is_alive()
        ):
            return True
        return False
