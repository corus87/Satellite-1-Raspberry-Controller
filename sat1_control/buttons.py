from __future__ import annotations

from dataclasses import dataclass
from sat1_control._xmos import _XMOSTransport

_PORT_A = 1


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
    """
    Reads the four hardware buttons on the Satellite1 HAT via XMOS SPI.

    Example::

        buttons = Buttons()

        while True:
            if buttons.up.pressed_edge:
                ...
            if buttons.mute.pressed:
                ...
            sleep(0.1)
    """

    def __init__(self, transport: _XMOSTransport | None = None):
        self._xmos = transport or _XMOSTransport()
        self._prev: dict[str, bool] = {k: False for k in ("up", "down", "mute", "action")}

    def _bit(self, bit: int, inverted: bool) -> bool:
        self._xmos.request_status_update()
        raw = bool((self._xmos.get_status(_PORT_A) >> bit) & 1)
        return raw ^ inverted

    def _read(self, name: str) -> tuple[bool, bool, bool]:
        if name == "up":
            value = self._bit(0, inverted=True)
        elif name == "down":
            value = self._bit(2, inverted=True)
        elif name == "mute":
            value = self._bit(3, inverted=False)
        elif name == "action":
            value = self._bit(1, inverted=True)
        else:
            value = False

        prev = self._prev[name]
        self._prev[name] = value
        return value, value and not prev, not value and prev

    @property
    def up(self) -> ButtonState:
        pressed, on, off = self._read("up")
        return ButtonState(pressed, on, off)

    @property
    def down(self) -> ButtonState:
        pressed, on, off = self._read("down")
        return ButtonState(pressed, on, off)

    @property
    def mute(self) -> StateButtonState:
        pressed, on, off = self._read("mute")
        return StateButtonState(pressed, on, off)

    @property
    def action(self) -> ButtonState:
        pressed, on, off = self._read("action")
        return ButtonState(pressed, on, off)
