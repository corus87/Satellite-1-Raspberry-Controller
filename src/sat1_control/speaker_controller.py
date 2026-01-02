from time import time, sleep
from threading import Thread

from sat1_control.tas2780 import Tas2780
from sat1_control.buttons import Buttons
from sat1_control.utils.utils import Utils
from sat1_control.led_controller import LedController

def volume_to_leds(volume: float, total_leds: int = 24) -> int:
    volume = max(0.0, min(1.0, volume))  # clamp
    return int(round(volume * total_leds))


class SpeakerController:
    def __init__(self, amp_level=20, 
                       power_mode=2,
                       volume_step=0.05, 
                       volume=None):

        self.button_control_running = False

        self.volume_step = volume_step
        self.tas = Tas2780()

        if volume is None:
            volume = Utils.get_volume_state() 
        
        self.tas.setup()
        self.tas.activate()            
        
        self.tas.amp_level = amp_level
        self.tas.power_mode = power_mode

        self.set_volume(volume)

        self.btn = Buttons()
        if self.btn.mute.pressed:
            self.mute_on()

        self.led = None
        self.led_start_time = None
        self.led_timeout = 3

    def button_control(self, blocked=False, show_leds=True):
        if show_leds:
            self.led = LedController()
            self.led.start()

        if blocked:
            self._button_control()
        else:
            if not self.button_control_running:
                Thread(target=self._button_control, daemon=True).start()

    def increase_volume(self):
        current_vol = Utils.get_volume_state()
        if current_vol < 1:
            self.set_volume(current_vol + self.volume_step)
    
    def decrease_volume(self):
        current_vol = Utils.get_volume_state()
        if current_vol > 0:
            self.set_volume(current_vol - self.volume_step)

    def disable(self):
        self.tas.deactivate()
    
    def set_volume(self, volume):
        Utils.save_volume_state(volume)

        self.tas.volume = volume
        self.tas.write_volume()

    def mute_on(self):
        self.tas.mute_on()

    def mute_off(self):
        self.tas.mute_off()

    def _run_led(self, animation):
        if not self.led:
            return 

        if animation == "show_volume":
            num_on_leds = volume_to_leds(self.volume)
            self.led.on_volume_change(num_leds=num_on_leds,
                                      clear_leds=False)
        
        elif animation == "on_mute":
            self.led.on_mute()
        
        self.led_start_time = time()
    
    def _check_led_timeout(self):
        if not self.led or self.led_start_time is None:
            return 

        if (time() - self.led_start_time) >= self.led_timeout:
            self.led.off()
            self.led_start_time = None

    def _button_control(self):
        self.button_control_running = True
        try:
            while self.button_control_running:

                if self.btn.mute.pressed:
                    if not self.is_muted:
                        self._run_led("on_mute")
                        self.mute_on()
                else:
                    if self.is_muted:
                        self._run_led("show_volume")
                        self.mute_off()

                if not self.is_muted:
                    if self.btn.up.pressed_edge:
                        self.increase_volume()
                        self._run_led("show_volume")
                    
                    if self.btn.down.pressed_edge:
                        self.decrease_volume()
                        self._run_led("show_volume")

                else:
                    if self.btn.up.pressed_edge or self.btn.down.pressed_edge:
                        self._run_led("on_mute")

                self._check_led_timeout()
                sleep(0.1)
        
        except Exception as e:
            raise e

        self.button_control_running = False

    @property
    def volume(self):
        return Utils.get_volume_state()

    @property
    def is_active(self):
        return self.tas.is_active

    @property
    def is_muted(self):
        return self.tas.is_muted
