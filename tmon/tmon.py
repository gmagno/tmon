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

from tmon.asciichart import plot


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
        start = datetime.datetime.now()
        cdt = start.strftime("%Y%m%d@%Hh%Mm%S")

        with contextlib.ExitStack() as stack:
            self.proc = stack.enter_context(
                Popen(args, stdout=sys.stdout, stderr=sys.stderr)
            )
            self.tf = stack.enter_context(tempfile.NamedTemporaryFile(
                mode='w+', prefix="tmon-{}-".format(cdt),
                suffix=".txt", delete=False, buffering=1
            ))

            while True:  # do-while() loop to ensure it runs at least once
                tmp_files = glob.glob("/sys/class/thermal/thermal_zone*/temp")
                tmps = [pathlib.Path(p).read_text().strip() for p in tmp_files]
                self.tf.write((' '.join(tmps) + '\n'))
                if not self.keep_running:
                    break
                time.sleep(1)
            try:
                outs, errs = self.proc.communicate(timeout=5)
            except TimeoutExpired:
                self.proc.kill()
                outs, errs = self.proc.communicate()
            ret = self.proc.returncode

            self.period = str(datetime.datetime.now() - start).split('.')[0]

            self.report()
        return ret

    def report(self):
        self.eprint("\n\n===================")
        self.eprint("Temp Monitor Report:\n")
        self.plot()
        self.eprint("\n{}".format(self.tf.name))
        self.eprint("===================")

    def plot(self):
        lines = pathlib.Path(self.tf.name).read_text().splitlines()
        ds = [max([float(t) for t in l.split(' ')]) / 1000 for l in lines]
        ratio = int(len(ds) / 90)
        if ratio > 1:
            ds = ds[::ratio]
        # period = str(datetime.timedelta(seconds=len(ds)))
        self.eprint("   Temp (°C) for a period of {}".format(self.period))
        if len(ds) > 1:
            self.eprint(plot(ds, {
                'height': 15,
                'minimum': math.floor(min(ds)),
                'maximum': math.ceil(max(ds) + 0.1),
            }))
        else:
            self.eprint("   >> {} °C <<".format(ds[0]))
