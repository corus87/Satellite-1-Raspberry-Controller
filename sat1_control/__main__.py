#!/usr/bin/env python3

import argparse
from time import sleep

from sat1_control import LedController, SpeakerController


def main():
    parser = argparse.ArgumentParser(prog="sat1_control")
    sub = parser.add_subparsers(dest="action", required=True)

    led = sub.add_parser("led")
    led.add_argument("--animation", "-a", required=True,
                     choices=["on_start", "on_error", "listen", "think", "speak", "off"])
    led.add_argument("--timeout", "-t", type=int, default=10)
    led.add_argument("--pattern", "-p", choices=["default"], default="default")

    spk = sub.add_parser("speaker")
    spk.add_argument("--set-volume", "-v", type=float, metavar="0.0-1.0")
    spk.add_argument("--increase", "-i", action="store_true")
    spk.add_argument("--decrease", "-d", action="store_true")
    spk.add_argument("--mute-on", "-m", action="store_true", dest="mute_on")
    spk.add_argument("--mute-off", "-u", action="store_true", dest="mute_off")
    spk.add_argument("--get-volume", "-g", action="store_true", dest="get_volume")

    args = parser.parse_args()

    if args.action == "led":
        ctl = LedController(pattern=args.pattern, timeout=args.timeout)
        dispatch = {
            "on_start": ctl.on_start,
            "on_error": ctl.on_error,
            "listen":   ctl.listen,
            "think":    ctl.think,
            "speak":    ctl.speak,
        }
        if args.animation == "off":
            ctl.off()
        else:
            dispatch[args.animation]()
            try:
                while ctl.animator.is_running:
                    sleep(0.1)
            except KeyboardInterrupt:
                pass
            finally:
                ctl.stop()

    elif args.action == "speaker":
        ctl = SpeakerController()
        if args.set_volume is not None:
            ctl.set_volume(args.set_volume)
        elif args.increase:
            ctl.increase_volume()
        elif args.decrease:
            ctl.decrease_volume()
        elif args.mute_on:
            ctl.mute_on()
        elif args.mute_off:
            ctl.mute_off()
        elif args.get_volume:
            print(ctl.volume)
        else:
            print(f"volume={ctl.volume:.2f}  muted={ctl.is_muted}")


if __name__ == "__main__":
    main()
