import queue as Queue
from threading import Thread
from dataclasses import dataclass

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
        self.animator.timeout = timeout
        self.pattern = None
        self.is_running = False
        self.set_pattern(pattern) 
        
    def run(self):
        self.is_running = True
        while self.is_running:
            pattern = self.queue.get()
            self.animator.run(pattern.func, **pattern.kwargs)

    def on_start(self, **kwargs):
        self.queue.put(Pattern(func=self.pattern.on_start,
                               kwargs=kwargs)
        )

    def on_error(self, **kwargs):
        self.queue.put(Pattern(func=self.pattern.on_error,
                               kwargs=kwargs)
        )

    def listen(self, **kwargs):
        self.queue.put(Pattern(func=self.pattern.listen,
                               kwargs=kwargs)
        )

    def think(self, **kwargs):
        self.queue.put(Pattern(func=self.pattern.think,
                               kwargs=kwargs)
        )

    def speak(self, **kwargs):
        self.queue.put(Pattern(func=self.pattern.speak,
                               kwargs=kwargs)
        )

    def on_mute(self, **kwargs):
        self.queue.put(Pattern(func=self.pattern.on_mute,
                               kwargs=kwargs)
        )
    
    def on_volume_change(self, **kwargs):
        self.queue.put(Pattern(func=self.pattern.on_volume_change,
                               kwargs=kwargs)
        )

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
