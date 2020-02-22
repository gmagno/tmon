# -*- coding: utf-8 -*-

"""Main module."""

import contextlib
import datetime
import glob
import math
import pathlib
import signal
from subprocess import Popen, TimeoutExpired
import sys
import time
import tempfile
import textwrap

from tmon.asciichart import plot
from tmon.utils import eprint


class Monitor:

    def __init__(self):
        self.keep_running = True
        self.tf = None
        self.proc = None

    def _setup_signal_handlers(self):
        catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
        for sig in catchable_sigs:
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, sig, frame):
        if sig == signal.Signals.SIGCHLD:
            # tmon returns only when child process exits, i.e sends SIGCHLD
            # back to parent
            self.keep_running = False
        else:
            # all the other signals should be injected to the child process
            try:
                self.proc.send_signal(sig)
            except AttributeError:
                # Just in case a signal is sent before the process is spawned
                # or no child process was executed at all, i.e when tmon is run
                # with no arguments
                if sig == signal.Signals.SIGINT:
                    self.keep_running = False

    def _start_timer(self):
        self.start = datetime.datetime.now()
        self.cdt = self.start.strftime("%Y%m%d@%Hh%Mm%S")

    def _stop_timer(self):
        self.period = str(datetime.datetime.now() - self.start).split('.')[0]

    def start(self, args):
        self._setup_signal_handlers()
        self._start_timer()

        with contextlib.ExitStack() as stack:
            if args:
                self.proc = stack.enter_context(
                    Popen(args, stdout=sys.stdout, stderr=sys.stderr)
                )
            self.tf = stack.enter_context(tempfile.NamedTemporaryFile(
                mode='w+', prefix="tmon-{}-".format(self.cdt),
                suffix=".txt", delete=False, buffering=1
            ))

            while True:  # do-while() loop to ensure it runs at least once
                tmp_files = glob.glob("/sys/class/thermal/thermal_zone*/temp")
                tmps = [pathlib.Path(p).read_text().strip() for p in tmp_files]
                self.tf.write((' '.join(tmps) + '\n'))
                if not self.keep_running:
                    break
                time.sleep(1)
            ret = 0
            if args:
                try:
                    self.proc.communicate(timeout=5)
                except TimeoutExpired:
                    self.proc.kill()
                    self.proc.communicate()  # we don't care about stdout/err
                ret = self.proc.returncode
            self._stop_timer()

            lines = pathlib.Path(self.tf.name).read_text().splitlines()
            self.ds = [max([float(t)
                       for t in l.split(' ')])*0.001 for l in lines]
        return ret


class Report:
    """Temperature Reporter
    """

    def __init__(self, ds, tfname, period, fahrenheit=False):
        self.ds = ds if not fahrenheit else [t*1.8 + 32 for t in ds]
        self.tfname = tfname
        self.period = period
        self.unit = "°F" if fahrenheit else "°C"

    def header(self):
        return textwrap.dedent("""
            ===================
            Temp Monitor Report
        """)

    def footer(self):
        return textwrap.dedent("""
            ===================
        """)

    def chart(self, xsize, ysize, ylim):
        ds = self.ds
        ratio = int(len(ds) / xsize)
        if ratio > 1:
            ds = ds[::ratio]
        ret = "temp ({}) for a period of {}\n".format(self.unit, self.period)
        if len(ds) > 1:
            try:
                minimum, maximum = ylim
            except TypeError:
                minimum = math.floor(min(ds))
                maximum = math.ceil(max(ds) + 0.1)
            else:
                minimum = min(minimum, math.floor(min(ds)))
                maximum = max(maximum, math.ceil(max(ds) + 0.1))

            ret += plot(ds, {
                'height': ysize - 1,
                'minimum': minimum,
                'maximum': maximum,
            })
        else:
            ret = ""
        return ret

    def stats(self):
        mi = round(min(self.ds), 1)
        av = round(sum(self.ds) / len(self.ds), 1)
        ma = round(max(self.ds), 1)
        ret = "min: {0} {3}\navg: {1} {3}\nmax: {2} {3}".format(
            mi, av, ma, self.unit
        )
        return ret

    def report(self, xsize, ysize, ylim):
        ret = self.header() + "\n"
        chart = self.chart(xsize, ysize, ylim)
        if chart != "":
            ret += textwrap.indent(self.chart(xsize, ysize, ylim), '    ')
            ret += "\n\n"
        ret += textwrap.indent(self.stats(), '    ') + "\n\n"
        ret += textwrap.indent("raw: " + self.tfname, '    ')
        ret += self.footer()
        return ret


def run(
    cmd=None, xsize=70, ysize=15, ylim=None, fahrenheit=False,
    stats_only=False, chart_only=False, path_only=False
):
    monitor = Monitor()
    ret = monitor.start(cmd)
    ds, tfname, period = monitor.ds, monitor.tf.name, monitor.period
    report = Report(ds, tfname, period, fahrenheit=fahrenheit)
    if stats_only:
        eprint('\n' + report.stats())
    elif chart_only:
        eprint('\n' + report.chart(xsize, ysize, ylim))
    elif path_only:
        eprint('\n' + tfname)
    else:
        eprint(report.report(xsize, ysize, ylim))
    return ret
