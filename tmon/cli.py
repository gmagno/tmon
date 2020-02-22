# -*- coding: utf-8 -*-

"""CLI script for tmon.
"""

import argparse
import platform
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
    description = textwrap.dedent("""
        Temperature Monitor (tmon v0.3.8) -- executes a program while
        monitoring CPU temperature, reporting the min, max and mean
        temperatures and plotting an ascii chart at the end to stderr.
        All signals are redirected to the program.
        If no program is passed, %(prog)s runs as expected returning on
        SIGINT (Ctrl-C).
        For full documentation check the repo: https://github.com/gmagno/tmon
    """)

    epilog = r"""
           /##
          | ##
         /######   /######/####   /######  /#######
        |_  ##_/  | ##_  ##_  ## /##__  ##| ##__  ##
          | ##    | ## \ ## \ ##| ##  \ ##| ##  \ ##
          | ## /##| ## | ## | ##| ##  | ##| ##  | ##
          |  ####/| ## | ## | ##|  ######/| ##  | ##
           \___/  |__/ |__/ |__/ \______/ |__/  |__/
    """

    epilog += textwrap.dedent("""
        return:
            %(prog)s returns when the child program exits, stops, or is
            terminated by a signal. The return value of %(prog)s is the return
            value of the program it executed.

        examples:
            $ %(prog)s echo How can a clam cram in a clean cream can
            How can a clam cram in a clean cream can

            ===================
            Temp Monitor Report

                min: 51.0 °C
                avg: 51.0 °C
                max: 51.0 °C

                raw: /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
            ===================

            $ %(prog)s bash -c 'sleep 6; stress -c 4 -t 3; sleep 6'
            stress: info: [30357] dispatching hogs: 4 cpu, 0 io, 0 vm, 0 hdd
            stress: info: [30357] successful run completed in 3s

            ===================
            Temp Monitor Report

                temp (°C) for a period of 0:00:15
                53.00  ┤
                52.67  ┤
                52.33  ┤
                52.00  ┤
                51.67  ┤      ╭─╮
                51.33  ┤      │ │
                51.00  ┤      │ │
                50.67  ┤      │ ╰╮
                50.33  ┤      │  │
                50.00  ┤     ╭╯  │
                49.67  ┤     │   │
                49.33  ┤     │   │
                49.00  ┼╮  ╭╮│   ╰─╮
                48.67  ┤│  │││     │
                48.33  ┤│  │││     │
                48.00  ┤╰──╯╰╯     ╰───

                min: 48.0 °C
                avg: 49.1 °C
                max: 52.0 °C

                raw: /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
            ===================

            $ %(prog)s -f -y 5 -x 5 bash -c 'sleep 6;stress -c 4 -t 3;sleep 6'
            stress: info: [31055] dispatching hogs: 4 cpu, 0 io, 0 vm, 0 hdd
            stress: info: [31055] successful run completed in 3s

            ===================
            Temp Monitor Report

                temp (°F) for a period of 0:00:15
                126.00  ┤
                124.50  ┤  ╭╮
                123.00  ┤ ╭╯│
                121.50  ┤ │ ╰╮
                120.00  ┼─╯  ╰

                min: 120.2 °F
                avg: 122.2 °F
                max: 127.4 °F

                raw: /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
            ===================

            $ %(prog)s -l 40 70 -x 10 -y 10 bash -c 'stress -c 4 -t 3; sleep 6'
            stress: info: [853] dispatching hogs: 4 cpu, 0 io, 0 vm, 0 hdd
            stress: info: [853] successful run completed in 3s

            ===================
            Temp Monitor Report

                temp (°C) for a period of 0:00:09
                70.00  ┤
                66.67  ┤
                63.33  ┤
                60.00  ┤
                56.67  ┤
                53.33  ┤
                50.00  ┼────╮   ╭
                46.67  ┤    ╰───╯
                43.33  ┤
                40.00  ┤

                min: 49.0 °C
                avg: 50.6 °C
                max: 53.0 °C

                raw: /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
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
        help="shows %(prog)s version"
    )
    parser.add_argument(
        "-f", "--fahrenheit", required=False, action='store_true',
        help="shows temperatures in °F instead of °C (the default)"
    )
    parser.add_argument(
        "-c", "--chart-only", required=False, action='store_true',
        help=(
            "only shows the temperature chart. Ignored if there is only one "
            "data point"
        )
    )
    parser.add_argument(
        "-s", "--stats-only", required=False, action='store_true',
        help="Only shows temperature stats"
    )
    parser.add_argument(
        "-p", "--path-only", required=False, action='store_true',
        help="only shows the path to raw data"
    )

    parser.add_argument(
        "command", metavar='CMD', nargs=argparse.REMAINDER,
        help="Command args to run."
    )
    parser.add_argument(
        "-y", "--ysize", required=False, default=15, type=int,
        help="y-axis size in number terminal characters", action=AxisSizeAction
    )
    parser.add_argument(
        "-x", "--xsize", required=False, default=70, type=int,
        help="x-axis size in number terminal characters", action=AxisSizeAction
    )
    parser.add_argument(
        "-l", "--ylim", nargs=2, required=False, metavar=('MIN', 'MAX'),
        type=float, help=(
            "y-axis view limits with min and max values. It is ignored if the "
            "measured temperatures fall outside the specified range."
        )
    )
    args = vars(parser.parse_args())
    return args


def main():
    kwargs = parse_args()
    if kwargs['version']:
        print("Temperature Monitor -- tmon v0.3.8")
        return 0

    if platform.system() != 'Linux':
        print(textwrap.dedent("""
            You seem to be running a non linux operating system. tmon is a
            proud-to-be-linux-only tool, {} is not supported and will
            probably never be. Please take the next step for a better tech
            life and download a real operating system :)
                https://mirrors.kernel.org/
        """.format(platform.system())))
        return 1

    return tmon.run(
        cmd=kwargs['command'],
        xsize=kwargs['xsize'], ysize=kwargs['ysize'], ylim=kwargs['ylim'],
        fahrenheit=kwargs['fahrenheit'], stats_only=kwargs['stats_only'],
        chart_only=kwargs['chart_only'], path_only=kwargs['path_only']
    )


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
