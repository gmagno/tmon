"""CLI script for tmon.
"""

import argparse
import textwrap
import sys

from tmon import tmon


class AxisSizeAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if values < 3:
            parser.error(
                "Minimum axis size for {0} is 3".format(option_string)
            )
        setattr(namespace, self.dest, values)


def parse_args():
    description = (
        "Temperature Monitor (tmon v0.3.6) -- executes a program while\n"
        "monitoring CPU temperature, reporting the min, max and mean\n"
        "temperatures and plotting an ascii chart at the end to stderr.\n"
        "All signals are redirected to the program.\n"
        "If no program is passed, %(prog)s runs as expected returning on\n"
        "SIGINT (Ctrl-C).\n"
        "For full documentation check the repo: https://github.com/gmagno/tmon"
    )
    epilog = textwrap.dedent("""
        return:
            %(prog)s returns when the child program exits, stops, or is
            terminated by a signal. The return value of %(prog)s is the return
            value of the program it executed.

        examples:
            $ %(prog)s echo How can a clam cram in a clean cream can
            How can a clam cram in a clean cream can


            ===================
            Temp Monitor Report:

            Temp (°C) for a period of 0:00:00
            >> 53.0 °C <<

            /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
            ===================

            $ %(prog)s bash -c 'sleep 6; stress -c 4 -t 3; sleep 6'
            stress: info: [17832] dispatching hogs: 4 cpu, 0 io, 0 vm, 0 hdd
            stress: info: [17832] successful run completed in 3s


            ===================
            Temp Monitor Report:

            Temp (°C) for a period of 0:00:15
            59.00  ┤
            58.67  ┤
            58.33  ┤
            58.00  ┤
            57.67  ┤      ╭─╮
            57.33  ┤      │ │
            57.00  ┤      │ │
            56.67  ┤     ╭╯ ╰╮
            56.33  ┤     │   │
            56.00  ┤     │   │
            55.67  ┼─╮   │   │
            55.33  ┤ │   │   │
            55.00  ┤ ╰───╯   ╰────╮
            54.67  ┤              │
            54.33  ┤              │
            54.00  ┤              ╰

            /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
            ===================

            $ %(prog)s -y 5 -x 5 bash -c 'sleep 6; stress -c 4 -t 3; sleep 6'
            stress: info: [17181] dispatching hogs: 4 cpu, 0 io, 0 vm, 0 hdd
            stress: info: [17181] successful run completed in 3s


            ===================
            Temp Monitor Report:

            Temp (°C) for a period of 0:00:15
            60.00  ┤
            59.00  ┤  ╭╮
            58.00  ┼╮╭╯│
            57.00  ┤╰╯ │
            56.00  ┤   ╰─

            /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
            ===================

            $ %(prog)s -l 40 70 -x 10 -y 10 bash -c 'stress -c 4 -t 3; sleep 6'
            stress: info: [19677] dispatching hogs: 4 cpu, 0 io, 0 vm, 0 hdd
            stress: info: [19677] successful run completed in 3s


            ===================
            Temp Monitor Report:

            Temp (°C) for a period of 0:00:09
            70.00  ┤
            66.67  ┤
            63.33  ┤
            60.00  ┤
            56.67  ┼───╮
            53.33  ┤   ╰─────
            50.00  ┤
            46.67  ┤
            43.33  ┤
            40.00  ┤

            /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
            ===================

        copyright:
            Copyright © 2020 Gonçalo Magno <goncalo@gmagno.dev>
            This software is licensed under the MIT License.
    """)
    parser = argparse.ArgumentParser(
        prog="tmon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description,
        epilog=epilog
    )
    parser.add_argument(
        "-v", "--version", required=False, action='store_true',
        help="Shows %(prog)s version."
    )
    parser.add_argument(
        "command", metavar='CMD', nargs=argparse.REMAINDER,
        help="Command args to run."
    )
    parser.add_argument(
        "-y", "--ysize", required=False, default=15, type=int,
        help="Y-axis size in number terminal characters", action=AxisSizeAction
    )
    parser.add_argument(
        "-x", "--xsize", required=False, default=70, type=int,
        help="X-axis size in number terminal characters", action=AxisSizeAction
    )
    parser.add_argument(
        "-l", "--ylim", nargs=2, required=False, metavar=('MIN', 'MAX'),
        type=float, help=(
            "Y-axis view limits with min and max values. It is ignored if the "
            "measured temperatures fall outside the specified range."
        )
    )
    args = vars(parser.parse_args())
    return args


def main():
    args = parse_args()
    if args['version']:
        print("Temperature Monitor -- tmon v0.3.6")
        return 0
    t = tmon.TMon(
        config={k: args[k] for k in args if k in ['ysize', 'xsize', 'ylim']}
    )
    ret = t.run(args['command'])
    return ret


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
