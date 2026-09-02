#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: canonicalize Peach Dream MuScriptor JSON → MIDI x2.

Per-song sibling of scripts/v3_spine/canonicalize_operator_section_probes.py (READ-ONLY).
"""
from __future__ import annotations
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.v3_spine.midi_from_json_events import serialize  # noqa: E402

SEC = Path("data/v3_spine/88d247468cb6d49f/chosen_section")
JSON_DIR = SEC / "muscriptor"
OUT_DIR = SEC / "canonical_midi"
OUT_DIR.mkdir(parents=True, exist_ok=True)
STEMS = ["drums", "bass", "guitar", "other", "piano", "vocals", "full_mix"]


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    tempo = json.loads((SEC / "tempo_choice.json").read_text())
    bpm = float(tempo["detected_bpm"])
    meter = tuple(tempo["meter"])

    results = {}
    for stem in STEMS:
        jp = JSON_DIR / f"{stem}.json"
        if not jp.exists():
            results[stem] = {"status": "missing_input"}
            continue
        with tempfile.TemporaryDirectory(prefix=f"pdcanon_{stem}_r1_") as d1:
            o1 = Path(d1) / f"{stem}.mid"
            serialize(str(jp), str(o1), bpm, meter)
            s1 = sha(o1)
            shutil.copy2(o1, OUT_DIR / f"{stem}.mid")
        with tempfile.TemporaryDirectory(prefix=f"pdcanon_{stem}_r2_") as d2:
            o2 = Path(d2) / f"{stem}.mid"
            serialize(str(jp), str(o2), bpm, meter)
            s2 = sha(o2)
        equal = s1 == s2 == sha(OUT_DIR / f"{stem}.mid")
        results[stem] = {
            "input_json": str(jp), "input_json_sha256": sha(jp),
            "run1_sha256": s1, "run2_sha256": s2,
            "final_out_sha256": sha(OUT_DIR / f"{stem}.mid"),
            "byte_deterministic_x2": equal,
        }
        print(f"{stem:10s} run1={s1[:16]} run2={s2[:16]} equal={equal}")

    payload = {
        "schema_version": 1, "cycle": 20, "clone": "clone-2",
        "song_sha16": "88d247468cb6d49f", "section": "chosen_section",
        "tempo_bpm": bpm, "meter": list(meter),
        "serializer_path": "scripts/v3_spine/midi_from_json_events.py",
        "serializer_sha256": sha("scripts/v3_spine/midi_from_json_events.py"),
        "results": results,
    }
    out = SEC / "canonical_midi_determinism.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    fails = [s for s, r in results.items() if not r.get("byte_deterministic_x2", False)]
    if fails:
        print(f"STOP: canonical non-det on {fails}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
