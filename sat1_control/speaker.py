from __future__ import annotations

import os
import logging
from pathlib import Path

from sat1_control._amp import _TAS2780

log = logging.getLogger(__name__)


class SpeakerController:
    """
    Controls the TAS2780 amplifier on the Satellite1 HAT.

    Volume is persisted to disk and restored on the next instantiation.

    Args:
        amp_level:   Amplifier output level 0–20. Default 10.
        power_mode:  0 = USB/5V power, 2 = 9V+ USB-PD. Default 0.
        volume_step: Step size for increase/decrease. Default 0.05.
        volume:      Initial volume 0.0–1.0. Loads from disk if not given.
        state_path:  Path for volume persistence. Defaults to ~/.cache/sat1/speaker/volume.

    Example::

        spk = SpeakerController()
        spk.set_volume(0.7)
        spk.increase_volume()
        spk.mute_on()
        spk.mute_off()
        print(spk.volume)
        spk.disable()
    """

    def __init__(
        self,
        amp_level: int = 10,
        power_mode: int = 0,
        volume_step: float = 0.05,
        volume: float | None = None,
        state_path: str | Path | None = None,
    ):
        self.volume_step = volume_step
        self._state_path = Path(state_path) if state_path else self._default_state_path()

        self._amp = _TAS2780(amp_level=amp_level, power_mode=power_mode)
        self._amp.setup()
        self._amp.activate()

        self.set_volume(volume if volume is not None else self._load_volume())

    def set_volume(self, volume: float) -> float:
        volume = max(0.0, min(1.0, volume))
        self._save_volume(volume)
        self._amp.set_volume(volume)
        return volume

    def increase_volume(self) -> float:
        return self.set_volume(self._load_volume() + self.volume_step)

    def decrease_volume(self) -> float:
        return self.set_volume(self._load_volume() - self.volume_step)

    def mute_on(self):
        self._amp.mute_on()

    def mute_off(self):
        self._amp.mute_off()

    def disable(self):
        self._amp.deactivate()

    @property
    def volume(self) -> float:
        return self._load_volume()

    @property
    def is_muted(self) -> bool:
        return self._amp.is_muted

    @property
    def is_active(self) -> bool:
        return self._amp.is_active

    def _default_state_path(self) -> Path:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        path = base / "sat1" / "speaker"
        path.mkdir(parents=True, exist_ok=True)
        return path / "volume"

    def _load_volume(self) -> float:
        try:
            return max(0.0, min(1.0, float(self._state_path.read_text())))
        except Exception:
            self._save_volume(0.8)
            return 0.8

    def _save_volume(self, volume: float):
        try:
            self._state_path.write_text(str(max(0.0, min(1.0, volume))))
        except OSError as e:
            log.error("Could not save volume: %s", e)
