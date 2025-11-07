from sat1_control.utils.spi_interface import SpiInterface
from dataclasses import dataclass


@dataclass
class UpButton:
    is_pressed: bool

@dataclass
class DownButton:
    is_pressed: bool

@dataclass
class RightButton:
    is_pressed: bool 

@dataclass
class LeftButton:
    is_active: bool 


class Buttons:
    @classmethod
    def __init__(self):
        self.spi = SpiInterface()

    @property
    def up(self):
        state = self.get_state([[0, 3, 0, 0], 
                                [0, 7, 0, 0]])

        return UpButton(is_pressed=state)

    @property
    def down(self):
        state = self.get_state([[0, 1, 128, 0], 
                                [0, 5, 128, 0]])
        
        return DownButton(is_pressed=state)

    @property
    def right(self):
        state = self.get_state([[0, 2, 128, 0], 
                                [0, 6, 128, 0]])
        
        return RightButton(is_pressed=state)

    @property
    def left(self):
        state = self.get_state([[0, 5, 128, 0], 
                                [0, 6, 128, 0], 
                                [0, 7, 0, 0], 
                                [0, 7, 128, 0]])
        return LeftButton(is_active=state)

    def get_state(self, states):
        res = self.spi.request_status_register_update()
        if res and res in states:
            return True
        return False