from dataclasses import dataclass
from sat1_control.utils.spi_interface import SpiInterface

GPIO_PORT_IN_A = 1
GPIO_PORT_IN_B = 2


@dataclass
class ButtonState:
    pressed: bool = False
    pressed_edge: bool = False
    released_edge: bool = False


@dataclass
class StateButtonState:
    pressed: bool = False
    toggled_on: bool = False
    toggled_off: bool = False


class Buttons:
    def __init__(self, spi: SpiInterface | None = None):
        self.spi = spi or SpiInterface()

        # per-button cached state
        self._state = {
            "action": False,
            "down": False,
            "up": False,
            "mute": False,
        }

    def _read_cached(self, port: int, pin: int, inverted: bool) -> bool:
        self.spi.request_status_register_update()
        value = self.spi.get_status_register(port)
        bit = (value >> pin) & 1
        return bool(bit) ^ inverted

    def _read_button(self, name: str, value: bool) -> ButtonState:
        prev = self._state[name]
        self._state[name] = value

        return ButtonState(
            pressed=value,
            pressed_edge=value and not prev,
            released_edge=not value and prev,
        )

    def _read_state_button(self, name: str, value: bool) -> StateButtonState:
        prev = self._state[name]
        self._state[name] = value

        return StateButtonState(
            pressed=value,
            toggled_on=value and not prev,
            toggled_off=not value and prev,
        )

    @property
    def action(self) -> ButtonState:        
        value = self._read_cached(GPIO_PORT_IN_A, 0, True)
        return self._read_button("action", value)

    @property
    def down(self) -> ButtonState:
        value = self._read_cached(GPIO_PORT_IN_A, 1, True)
        return self._read_button("down", value)

    @property
    def up(self) -> ButtonState:
        value = self._read_cached(GPIO_PORT_IN_B, 7, True)
        return self._read_button("up", value)

    @property
    def mute(self) -> StateButtonState:
        value = self._read_cached(GPIO_PORT_IN_A, 2, False)
        return self._read_state_button("mute", value)