import os
from subprocess import run

def git_clone(url, path, branch):
    if not os.path.exists(path):
        res = run(["git", "clone", url, path, "--branch", branch])
        if res.returncode != 0:
            raise Exception("git clone %s error" % url)

if __name__ == "__main__":
    git_clone(
        "https://github.com/epics-base/epics-base.git",
        "epics-base",
        "R7.0.2",
    )
    git_clone(
        "https://github.com/eclipse/mosquitto.git",
        "mosquitto",
        "v1.5.8",
    )
