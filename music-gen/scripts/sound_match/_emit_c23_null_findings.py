#!/usr/bin/env -S /usr/bin/python3
"""Emit c23 NULL findings for empty-MIDI + inaudible non-CG stem cells.

Per c14 CG piano+other precedent: empty MIDI reference + inaudible stem
(rms_dbfs < -60 dB silence floor) = first-class NULL finding.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for k, v in _PINS.items():
    os.environ.setdefault(k, v)

if sys.executable != "/usr/bin/python3":
    raise RuntimeError("requires /usr/bin/python3")


def sha16(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


CELLS = [
    # (song_sha16, song_name, stem, stem_wav_path, midi_probe_note_on)
    ("252eb21ce7df7328", "What If I Go", "guitar",
     "data/v3_spine/252eb21ce7df7328/operator_section/rc9_6stem/guitar.wav", 0),
    ("51e433ade2a845e1", "Rome", "piano",
     "data/v3_spine/51e433ade2a845e1/operator_section/rc9_6stem/piano.wav", 0),
    ("51e433ade2a845e1", "Rome", "other",
     "data/v3_spine/51e433ade2a845e1/operator_section/rc9_6stem/other.wav", 0),
    ("88d247468cb6d49f", "Peach Dream", "guitar",
     "data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/rc9_6stem/guitar.wav", 0),
    # Disco A vocals is empty-MIDI + inaudible, but vocals is hybrid-overlay per campaign policy (L59-60);
    # emit informational finding not NULL_no_profile_possible.
]


def emit_null_finding(sha, name, stem, wav_path, n_note_on):
    wav = Path(wav_path)
    audib_path = Path(f"data/v4/profiles/{sha}/audibility_{stem}.json")
    audib = json.load(open(audib_path))
    verdict = f"{stem.upper()}_NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE"
    doc = {
        "manifest_kind": "stem_null_finding_c23",
        "milestone_id": f"M-V4-PROFILES-1/{sha}-{stem}-null-finding-c23",
        "cycle": 23,
        "created": "2026-09-05T00:00:00Z",
        "run_id": "run-2026-09-05T000000Z",
        "song_sha16": sha,
        "song_name": name,
        "instrument": stem,
        "verdict": verdict,
        "verdict_enum_frozen": [
            f"{stem.upper()}_NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE",
            f"{stem.upper()}_MIDI_EMPTY_REFERENCE_AUDIBLE_FIRST_CLASS_FINDING",
            f"{stem.upper()}_MIDI_NONEMPTY_SWEEP_ELIGIBLE",
        ],
        "midi_probe": {
            "path": f"data/v4/profiles/{sha}/stem_midi_probe.json",
            "n_note_on": n_note_on,
            "is_empty": True,
        },
        "reference_stem": {
            "path": str(wav),
            "sha256_16": sha16(wav),
            "rms_dbfs": audib["rms_dbfs"],
            "peak_dbfs": audib["peak_dbfs"],
            "lufs_i": audib.get("lufs_i"),
            "method": audib["method"],
            "silence_floor_db": audib["silence_floor_db"],
            "verdict_audible": audib["verdict_audible"],
        },
        "downstream_policy": (
            f"Showcase mix uses original htdemucs {stem} stem verbatim (empty MIDI = silent per-track, "
            f"already what v3-spine default emits). No sf2 sweep launched. No family-2 needed."
        ),
        "c14_precedent": "data/v4/profiles/31a164f845f8e27e/piano_null_finding.json (CG piano NULL under same audibility-grounded shape)",
        "sweep_deferred": False,
        "sweep_reason_deferred": None,
        "sweep_not_needed": True,
        "sweep_not_needed_rationale": "empty MIDI + inaudible stem = no sound to match",
        "supersedes_path": None,
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    out = Path(f"data/v4/profiles/{sha}/{stem}_null_finding.json")
    with open(out, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
    print(f"wrote {out}: verdict={verdict}")


def main():
    for cell in CELLS:
        emit_null_finding(*cell)
    # Disco A vocals separate: hybrid-overlay policy applies regardless
    sha = "cdd2717e52820ff6"
    audib = json.load(open(f"data/v4/profiles/{sha}/audibility_vocals.json"))
    doc = {
        "manifest_kind": "vocals_hybrid_overlay_note_c23",
        "milestone_id": f"M-V4-PROFILES-1/{sha}-vocals-hybrid-overlay-note-c23",
        "cycle": 23,
        "created": "2026-09-05T00:00:00Z",
        "run_id": "run-2026-09-05T000000Z",
        "song_sha16": sha,
        "song_name": "Disco A",
        "instrument": "vocals",
        "verdict": "VOCALS_HYBRID_OVERLAY_POLICY_APPLIES",
        "policy_source": "music_gen_v4_prompt.md L59-60 (Vocals: hybrid overlay (original vocal stem over instrumental render); generated songs are INSTRUMENTAL.)",
        "midi_empty_note": "vocals track has 0 note_on and reference stem inaudible (rms_dbfs=%.2f); hybrid-overlay uses original vocals stem verbatim so profiling has no meaning here." % audib["rms_dbfs"],
        "reference_stem_audibility": audib,
        "sweep_not_needed": True,
        "supersedes_path": None,
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    out = Path(f"data/v4/profiles/{sha}/vocals_hybrid_overlay_note.json")
    with open(out, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
    print(f"wrote {out}: verdict={doc['verdict']}")


if __name__ == "__main__":
    main()
