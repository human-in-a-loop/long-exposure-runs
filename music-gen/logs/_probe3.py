import inspect
from long_exposure import workspace_bootstrap as wb
src = inspect.getsource(wb)
i = src.find("_STATE_TRANSITIONS")
print(src[i:i+800])
