#!/usr/bin/env -S /usr/bin/python3
# c35 Branch A clone-0: one-shot egress probe emit. Archived to tools/stale/ after use.
import json, time, pathlib, sys
assert sys.executable == "/usr/bin/python3"
row = {
  "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "resource": "youtu.be/googlevideo",
  "source": "cycle35_branch_a_topofcycle",
  "status": "blocked",
  "http_code": 403,
  "media_ok": False,
  "metadata_ok": True,
  "notes": "egress remains blocked; c35 Branch A proceeds on non-audio path per music_gen_long_exposure_prompt.md Fixed Decisions."
}
p = pathlib.Path("data/ingestion/egress_status.jsonl")
p.parent.mkdir(parents=True, exist_ok=True)
with open(p, "a") as f:
    f.write(json.dumps(row, sort_keys=True) + "\n")
print("emitted egress probe row")
