from time import sleep
from threading import Thread

from sat1_control.tas2780 import Tas2780
from sat1_control.buttons import Buttons
from sat1_control.utils.utils import Utils

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

    def button_control(self, blocked=False):
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

        #if self.is_muted:
        #    self.mute_off()

        self.tas.volume = volume
        self.tas.write_volume()

    def mute_on(self):
        self.tas.mute_on()

    def mute_off(self):
        self.tas.mute_off()

    def _button_control(self):
        self.button_control_running = True
        btn = Buttons()
        try:
            while self.button_control_running:
                if btn.left.is_active:
                    if not self.is_muted:
                        self.mute_on()
                else: 
                    if self.is_muted:
                        self.mute_off()

                if not self.is_muted:
                    if btn.up.is_pressed:
                        self.increase_volume()
                    
                    if btn.down.is_pressed:
                        self.decrease_volume()

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
