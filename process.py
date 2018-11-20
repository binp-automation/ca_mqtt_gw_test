from threading import Thread
from subprocess import Popen, PIPE, STDOUT

from helper import *

class Process:
    def fpipe(self):
        for line in self.proc.stdout:
            self.logger.info(line.decode("utf-8").rstrip())
            self.logfile.write(line)

    def __init__(self, name, log, proc_args, stdout=False, **proc_kwargs):
        self.name = name
        self.log = log
        self.proc_args = proc_args
        self.proc_kwargs = proc_kwargs
        self.stdout = stdout

        self.logfile = None
        self.proc = None
        self.tpipe = None

        self.logger = create_logger(
            self.name, 
            file=False, 
            stdout=stdout,
            level=False,
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

    def __exit__(self, *args):
        self.proc.terminate()
        self.proc.wait()
        self.tpipe.join()
        self.logfile.close()
