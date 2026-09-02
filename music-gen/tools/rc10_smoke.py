"""Smoke test one song through RC10 pipeline for quick error surfacing."""
import sys, json
from pathlib import Path

sys.path.insert(0, "scripts/recreate_v2/rc10_other_vocals")
import run_rc10  # noqa: E402

songs = run_rc10._load_focus()
result = run_rc10._process_song(songs[0], Path("/tmp/rc10_smoke/out"), Path("/tmp/rc10_smoke/ab"))
print(json.dumps(result, indent=2, sort_keys=True))
