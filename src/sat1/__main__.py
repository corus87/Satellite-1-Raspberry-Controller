#!/bin/env python3

import argparse
from time import sleep

from sat1 import LedController
from sat1 import SpeakerController

def main():

    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(dest="action", 
                                            required=True, 
                                            help="Choose action."
                                            )

    led_parser = subparsers.add_parser("led")
    speaker_parser = subparsers.add_parser("speaker")    

    main_parser.add_argument("--led", 
                             help="Run LED Pattern", 
                             action="store_true")
    
    main_parser.add_argument("--speaker", 
                             help="Control Speaker", 
                             action="store_true")

    led_parser.add_argument("--animation", "-a",
                            help="Choose animation",
                            required=True,
                            choices=["on_start", "on_error", "listen", "think", "speak", "off"])

    led_parser.add_argument("--timeout", "-t",
                            help="Timeout when animation ends",
                            default=10,
                            type=int)

    led_parser.add_argument("--pattern", "-p",
                            help="Pattern to use",
                            choices=["default"],
                            default="default")
    
    speaker_parser.add_argument("--set-volume", "-v",
                                help="Set volume between 0-1",
                                type=float)

    speaker_parser.add_argument("--increase", "-i",
                                help="Increase Volume",
                                action="store_true")

    speaker_parser.add_argument("--decrease", "-d",
                                help="Decrease Volume",
                                action="store_true")

    speaker_parser.add_argument("--mute_on", "-m",
                                help="Mute on.",
                                action="store_true")

    speaker_parser.add_argument("--mute_off", "-u",
                                help="Mute off.",
                                action="store_true")

    speaker_parser.add_argument("--button_control", "-b",
                                help="Control volume with HW buttons (Left: Mute/Unmute, Up: Increase, Down: Decrease volume)",
                                action="store_true")

    speaker_parser.add_argument("--get_volume", "-g",
                                help="Get volume",
                                action="store_true")


    args = main_parser.parse_args()
    action = args.action.lower()

    if action == "led":
        ctl = LedController(pattern=args.pattern,
                            timeout=args.timeout)

        if args.animation == "on_start":
            ctl.animator.run(ctl.pattern.on_start)
        elif args.animation == "on_error":
            ctl.animator.run(ctl.pattern.on_error)
        elif args.animation == "listen":
            ctl.animator.run(ctl.pattern.listen)
        elif args.animation == "think":
            ctl.animator.run(ctl.pattern.think)
        elif args.animation == "speak":
            ctl.animator.run(ctl.pattern.speak)
        elif args.animation == "off":
            ctl.off()

        try:
            while ctl.animator.is_running:
                sleep(0.1)
        except KeyboardInterrupt:
            pass
        ctl.stop()

    elif action == "speaker":
        ctl = SpeakerController()

        if args.set_volume:
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
        elif args.button_control:
            try:
                print("Volume control enabled.\nPress strg + c to cancel.")
                ctl.button_control()
            except KeyboardInterrupt:
                pass
        else:
            print("Speaker enabled")

if __name__ == "__main__":
    main()