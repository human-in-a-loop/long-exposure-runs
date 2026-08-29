import inspect, sys
from long_exposure import workspace_bootstrap as wb
src = inspect.getsource(wb)
sys.stdout.write("has STATE: " + str("_STATE_TRANSITIONS" in src) + "\n")
i = src.find("STATE_TRANSITIONS")
sys.stdout.write("index: " + str(i) + "\n")
sys.stdout.write(src[i:i+900] + "\n")
sys.stdout.flush()
