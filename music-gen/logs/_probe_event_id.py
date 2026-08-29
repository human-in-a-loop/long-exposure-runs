import inspect, re
from long_exposure import workspace_bootstrap as wb
src = inspect.getsource(wb)
for m in re.finditer(r"def [^\(]*event_id[^\n]*", src):
    print(m.group(0))
# Also look for uuid5 usages
for m in re.finditer(r"uuid5[^\n]*", src):
    print(m.group(0))
