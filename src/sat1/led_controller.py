import queue as Queue
from threading import Thread
from time import sleep

from sat1.led.animator import Animator

class LedController(Thread):
    def __init__(self, pattern="default", 
                       timeout=60):
        super(LedController, self).__init__(daemon=True)
        self.queue = Queue.Queue()
        self.animator = Animator(timeout)
        self.pattern = None
        self.is_running = False
        self.set_pattern(pattern) 
        
    def run(self):
        self.is_running = True
        while self.is_running:
            func = self.queue.get()
            self.animator.run(func)

    def on_start(self):
        self.queue.put(self.pattern.on_start)

    def on_error(self):
        self.queue.put(self.pattern.on_error)

    def listen(self):
        self.queue.put(self.pattern.listen)
        
    def think(self):
        self.queue.put(self.pattern.think)

    def speak(self):
        self.queue.put(self.pattern.speak)

    def off(self):
        self.animator.stop()
        
    def set_pattern(self, pattern):
        if pattern == "default":
            from sat1.led.pattern.default_pattern import DefaultPattern
            self.pattern = DefaultPattern(self.animator)
        else:
            raise ValueError(f"Pattern {pattern} not found")

    def stop(self):
        self.off()
        self.is_running = False
