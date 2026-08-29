import inspect
from long_exposure import workspace_bootstrap as wb
src = inspect.getsource(wb)
lines = src.splitlines()
for i, l in enumerate(lines):
    if 'event_id' in l or 'uuid5' in l or 'content_hash' in l:
        print(i, l)
