import os

with open("./epicsTestApp/configure/RELEASE.pre", 'r') as file :
        data = file.read()

reps = {"%{EPICS_BASE}": os.environ["EPICS_BASE"]}
for k, v in reps.items():
    data = data.replace(k, v)
    print("  %s -> %s" % (k, v))

with open("./epicsTestApp/configure/RELEASE", 'w') as file:
    file.write(data)
