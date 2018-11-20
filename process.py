import signal
from threading import Thread
from subprocess import Popen, PIPE, STDOUT

import logging

from helper import *

class Process:
    def fpipe(self):
        try:
            for line in self.proc.stdout:
                self.logger.info(line.decode("utf-8").rstrip())
                self.logfile.write(line)
        except ValueError:
            pass

    def __init__(self, name, log, proc_args, stdout_print=False, proc_kwargs={}, must_kill=False):
        self.name = name
        self.log = log
        self.proc_args = proc_args
        self.proc_kwargs = proc_kwargs
        self.must_kill = must_kill

        self.logfile = None
        self.proc = None
        self.tpipe = None

        self.logger = create_logger(
            self.name, 
            file=False,
            level=logging.INFO if stdout_print else logging.ERROR,
            print_level=False,
        )

    def __enter__(self):
        self.logfile = open(self.log, "wb")
        self.proc = Popen(
            self.proc_args,
            **self.proc_kwargs,
            stdout=PIPE,
            stderr=STDOUT,
        )
        self.tpipe = Thread(target=self.fpipe)
        self.tpipe.start()

    def kill(self):
        self.proc.kill()

    def __exit__(self, *args):
        if self.must_kill:
            self.kill()
        else:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=1.0)
            except TimeoutExpired:
                self.kill()
        self.logfile.close()
        #self.tpipe.join()
