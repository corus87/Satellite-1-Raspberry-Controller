from pathlib import Path

VOLUME_STATE_FILE = "volume.state"

class Utils:

    @classmethod
    def save_volume_state(cls, volume):
        try:
            volume = float(volume)
        except Exception as e:
            raise e

        if volume > 1.0:
            volume = 1.0

        if volume < 0:
            volume = 0

        path = Path(__file__).parent.resolve()
        with open(path / VOLUME_STATE_FILE, "w") as f:
            f.write(str(volume))

    @classmethod
    def get_volume_state(cls):
        path = Path(__file__).parent.resolve()
        try:
            with open(path / VOLUME_STATE_FILE) as f:
                return float(f.read())
        except Exception as e:
            cls.save_volume_state("0.8")
        return 0.8