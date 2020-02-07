=====
Usage
=====

To use Temp Monitor in a project::

    tmon -h
    usage: tmon [-h] [-v] [-y YSIZE] [-x XSIZE] [-l MIN MAX] ...

    Temperature Monitor (tmon v0.3.6) -- executes a program while
    monitoring CPU temperature, reporting the min, max and mean
    temperatures and plotting an ascii chart at the end to stderr.
    All signals are redirected to the program.
    If no program is passed, tmon runs as expected returning on
    SIGINT (Ctrl-C).
    For full documentation check the repo: https://github.com/gmagno/tmon

    positional arguments:
    CMD                   Command args to run.

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         Shows tmon version.
    -y YSIZE, --ysize YSIZE
                            Y-axis size in number terminal characters
    -x XSIZE, --xsize XSIZE
                            X-axis size in number terminal characters
    -l MIN MAX, --ylim MIN MAX
                            Y-axis view limits with min and max values. It is
                            ignored if the measured temperatures fall outside the
                            specified range.

    return:
        tmon returns when the child program exits, stops, or is
        terminated by a signal. The return value of tmon is the return
        value of the program it executed.

    examples:
        $ tmon echo How can a clam cram in a clean cream can
        How can a clam cram in a clean cream can

        ===================
        Temp Monitor Report:

        Temp (°C) for a period of 0:00:00
        >> 53.0 °C <<

        /tmp/tmon-YYYYMMDD@HHhMMmSS-XXXXXXXX.txt
        ===================

        $ tmon bash -c 'sleep 6; stress -c 4 -t 3; sleep 6'
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

        $ tmon -y 5 -x 5 bash -c 'sleep 6; stress -c 4 -t 3; sleep 6'
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

        $ tmon -l 40 70 -x 10 -y 10 bash -c 'stress -c 4 -t 3; sleep 6'
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
