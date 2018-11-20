import traceback
import logging

def hook(logger):
    def realhook(func):
        def deco(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except:
                logger.error(traceback.format_exc())
        return deco
    return realhook

def create_logger(name, stdout=True, file=True, path=None, level=True):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if level:
        ln = "%(levelname)s: "
    else:
        ln = ""

    if stdout:
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(logging.Formatter("[%(name)s] " + ln + "%(message)s"))
        logger.addHandler(sh)

    if file:
        if path is None:
            path = "logs/%s.log" % name
        fh = logging.FileHandler(path, mode="w")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(ln + "%(message)s"))
        logger.addHandler(fh)

    return logger