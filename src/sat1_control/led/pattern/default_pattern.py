
class DefaultPattern:
    def __init__(self, animator):
        self.animator = animator
    
    def on_start(self):
        self.animator.rainbow_cycle(speed=1400, repeat=5)

    def on_error(self):
        self.animator.blink(color=(255, 0, 0), min_brightness=2, max_brightness=20, speed=300, repeat=2)

    def listen(self):
        self.animator.breath(color=(0, 0, 255), min_brightness=2, max_brightness=25, speed=20)

    def speak(self):
        self.animator.breath(color=(0, 255, 255), min_brightness=2, max_brightness=25, speed=40)

    def think(self):
        self.animator.rotate(trail=3)
