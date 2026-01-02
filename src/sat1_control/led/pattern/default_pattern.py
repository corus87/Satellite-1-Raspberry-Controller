class DefaultPattern:
    def __init__(self, animator):
        self.animator = animator

    def on_start(self, **kwargs):
        self.animator.rainbow_cycle(
            speed=kwargs.get("speed", 1400),
            repeat=kwargs.get("repeat", 5),
        )

    def on_error(self, **kwargs):
        self.animator.blink(
            color=kwargs.get("color", (255, 0, 0)),
            min_brightness=kwargs.get("min_brightness", 2),
            max_brightness=kwargs.get("max_brightness", 20),
            speed=kwargs.get("speed", 300),
            repeat=kwargs.get("repeat", 2),
        )

    def listen(self, **kwargs):
        self.animator.breath(
            color=kwargs.get("color", (0, 0, 255)),
            min_brightness=kwargs.get("min_brightness", 2),
            max_brightness=kwargs.get("max_brightness", 25),
            speed=kwargs.get("speed", 20),
        )

    def speak(self, **kwargs):
        self.animator.breath(
            color=kwargs.get("color", (0, 255, 255)),
            min_brightness=kwargs.get("min_brightness", 2),
            max_brightness=kwargs.get("max_brightness", 25),
            speed=kwargs.get("speed", 40),
        )

    def think(self, **kwargs):
        self.animator.rotate(
            color=kwargs.get("color", (0, 0, 200)),
            speed=kwargs.get("speed", 30),
            trail=kwargs.get("trail", 3),
            brightness=kwargs.get("brightness", 50),
        )

    def on_mute(self, **kwargs):
        self.animator.blink(
            color=kwargs.get("color", (100, 0, 0)),
            min_brightness=kwargs.get("min_brightness", 2),
            max_brightness=kwargs.get("max_brightness", 20),
            speed=kwargs.get("speed", 300),
            repeat=kwargs.get("repeat", 2),
        )

    def on_volume_change(self, **kwargs):
        self.animator.segment(
            color=kwargs.get("color", (0, 100, 0)),
            num_leds=kwargs.get("num_leds", 10),
        )