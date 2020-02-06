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

    def __init__(self, config):
        self.config = config
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
            # all the other signals should be injected to the child process
            try:
                self.proc.send_signal(sig)
            except AttributeError:
                # Just in case a signal is sent before the process is spawned
                # or no child process was executed at all
                if sig == signal.Signals.SIGINT:
                    self.keep_running = False

    def setup_signal_handlers(self):
        catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
        for sig in catchable_sigs:
            signal.signal(sig, self.signal_handler)

    def run(self, args):
        print(args)
        self.setup_signal_handlers()
        start = datetime.datetime.now()
        cdt = start.strftime("%Y%m%d@%Hh%Mm%S")

        with contextlib.ExitStack() as stack:
            if args:
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
            ret = 0
            if args:
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
        lines = pathlib.Path(self.tf.name).read_text().splitlines()
        self.ds = [max([float(t) for t in l.split(' ')]) / 1000 for l in lines]
        self.eprint("\n\n===================")
        self.eprint("Temp Monitor Report:\n")
        self.plot(self.ds)
        self.eprint("\n{}".format(self.tf.name))
        self.eprint("===================")

    def plot(self, ds):
        print(self.config['xsize'])
        print(self.config)
        ratio = int(len(ds) / self.config['xsize'])
        if ratio > 1:
            ds = ds[::ratio]
        self.eprint("   Temp (°C) for a period of {}".format(self.period))
        if len(ds) > 1:
            try:
                minimum, maximum = self.config['ylim']
            except TypeError:
                minimum = math.floor(min(ds))
                maximum = math.ceil(max(ds) + 0.1)
            else:
                minimum = min(minimum, math.floor(min(ds)))
                maximum = max(maximum, math.ceil(max(ds) + 0.1))

            self.eprint(plot(ds, {
                'height': self.config['ysize'] - 1,
                'minimum': minimum,
                'maximum': maximum,
            }))
        else:
            self.eprint("   >> {} °C <<".format(ds[0]))
