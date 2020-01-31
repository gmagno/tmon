"""Main module."""

import contextlib
import datetime
import glob
import pathlib
import signal
from subprocess import Popen, TimeoutExpired
import sys
import time
import tempfile

from asciichartpy import plot
import pandas as pd
from scipy.signal import decimate


class TMon:

    def __init__(self):
        self.keep_running = True
        self.tf = None
        self.proc = None

    def eprint(self, *args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    def signal_handler(self, sig, frame):
        if sig == signal.Signals.SIGCHLD:
            # tmon returns only when child process exits, i.e sends SIGCHLD
            # back to parent
            self.keep_running = False
        else:
            # all the other signals should be injected to child
            try:
                self.proc.send_signal(sig)
            except AttributeError:
                # Just in case a signal is sent before the process is spawned
                self.keep_running = False

    def setup_signal_handlers(self):
        catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
        for sig in catchable_sigs:
            signal.signal(sig, self.signal_handler)

    def run(self, args):
        self.setup_signal_handlers()
        cdt = datetime.datetime.now().strftime("%Y%m%d@%Hh%Mm%S")

        with contextlib.ExitStack() as stack:
            self.proc = stack.enter_context(
                Popen(args, stdout=sys.stdout, stderr=sys.stderr)
            )
            self.tf = stack.enter_context(tempfile.NamedTemporaryFile(
                mode='w+', prefix="tmon-{}-".format(cdt),
                suffix=".txt", delete=False, buffering=1
            ))

            while self.keep_running:
                tmp_files = glob.glob("/sys/class/thermal/thermal_zone*/temp")
                tmps = [pathlib.Path(p).read_text().strip() for p in tmp_files]
                self.tf.write((' '.join(tmps) + '\n'))
                time.sleep(1)

            try:
                outs, errs = self.proc.communicate(timeout=5)
            except TimeoutExpired:
                self.proc.kill()
                outs, errs = self.proc.communicate()
            ret = self.proc.returncode
            self.report()
        return ret

    def report(self):
        self.eprint("\n\n===================")
        self.eprint("Temp Monitor Report:\n")
        self.plot()
        self.eprint("\n{}".format(self.tf.name))
        self.eprint("===================")

    def plot(self):
        try:
            df = pd.read_csv(self.tf.name, sep=' ', header=None, dtype='float')
        except pd.errors.EmptyDataError:
            # trying to read an empty file...
            self.eprint("No data to plot")
            return
        df = df.max(axis=1)/1000.
        ratio = int(len(df) / 90)  # must be greater than 27
        if ratio > 1:
            df = decimate(df, ratio, ftype='iir')
        period = str(datetime.timedelta(seconds=len(df)))
        if len(df) <= 6:
            self.eprint("No data to plot")
            return
        self.eprint("   Temp (°C) for a period of {}".format(period))
        self.eprint(plot(df, {'height': 15}))
