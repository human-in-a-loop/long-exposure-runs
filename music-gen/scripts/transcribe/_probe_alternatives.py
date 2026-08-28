"""One-shot fetchability probe for alternative-transcriber candidates."""
import json
import os
import subprocess
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3"

TARGETS = [
    ("crepe==0.0.15", "Crepe (pitch)"),
    ("magenta==2.1.4", "Magenta (onsets-frames)"),
    ("note-seq==0.0.5", "note-seq (magenta core)"),
]
OUT = Path("data/transcribe/alternative_selection.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)


def probe(spec):
    tmp = Path("/tmp") / f"{spec.replace('==','_').replace('.','_')}_probe"
    tmp.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "pip", "download",
         "--dest", str(tmp), "--no-deps", spec],
        capture_output=True, text=True, timeout=90,
    )
    return {"target": spec, "exit": r.returncode,
            "stderr_tail": r.stderr[-400:].strip(),
            "files": sorted(os.listdir(tmp))}


rows = []
for spec, desc in TARGETS:
    entry = {"desc": desc, **probe(spec)}
    rows.append(entry)
    print(f"[probe] {spec}: exit={entry['exit']} files={len(entry['files'])}", flush=True)

# Librosa fallback is always available (installed at top-level).
import librosa  # noqa
rows.append({
    "desc": "librosa-family fallback (pyin + onset + CQT peak-picking)",
    "target": "librosa (already installed)",
    "exit": 0,
    "stderr_tail": "",
    "files": [f"librosa=={librosa.__version__}"],
})

OUT.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")
print(json.dumps(rows, indent=2))
