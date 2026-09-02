#!/usr/bin/env python3
"""RC5 tempo/beat-grid implementation (c53 Branch C, clone-2).

Parent milestone: M-RECREATE-2/accurate-small-set/rc5-tempo-beat-grid.
Rubric: docs/rc5_tempo_beat_grid_rubric.md.

Per song, on the ORIGINAL MIX:
  1. Load (native sr, mono).
  2. librosa.beat.beat_track(hop_length=512, start_bpm=120.0, tightness=100).
  3. Tempo-octave-correction against c49 baseline BPM (argmin variant).
  4. Write rc5_tempo_estimate.json.
  5. Read the more-complete partial MIDI (Branch A first, else Branch B),
     retempo via music21, write merged_retempo.midi + merged_retempo.musicxml.
  6. Per-song PASS iff |corrected - baseline| <= 2 BPM.

NO PRNG. /usr/bin/python3 guard. music21 imported READ-ONLY.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import sys
import tempfile

# c48 env-var flags default OFF
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(k, "1")

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

RC5_ID = "M-RECREATE-2/accurate-small-set/rc5-tempo-beat-grid"
RUBRIC_HASH_PATH = REPO_ROOT / "data/rc5_impl/rubric_hash.txt"
RUBRIC_DOC_PATH = REPO_ROOT / "docs/rc5_tempo_beat_grid_rubric.md"
FOCUS_SET_PATH = REPO_ROOT / "data/recreate_v2/focus_set_v2.json"
BASELINE_ROOT = REPO_ROOT / "data/recreate_v2/baseline"
BRANCH_A_ROOT = REPO_ROOT / "data/rc1_rc9_impl/per_song"
BRANCH_B_ROOT = REPO_ROOT / "data/rc2_rc3_impl"
OUT_ROOT = REPO_ROOT / "data/rc5_impl"

HOP_LENGTH = 512
START_BPM = 120.0
TIGHTNESS = 100
PASS_THRESHOLD_BPM = 2.0


def _interpreter_guard() -> None:
    if sys.executable != "/usr/bin/python3" and not sys.executable.endswith("/python3"):
        raise RuntimeError(f"expected /usr/bin/python3, got {sys.executable}")


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_focus_set() -> list[dict]:
    d = json.loads(FOCUS_SET_PATH.read_text())
    return d["songs"]


def load_baseline_bpm(sha16: str) -> float:
    p = BASELINE_ROOT / sha16 / "rc5_tempo_bpm.json"
    return float(json.loads(p.read_text())["estimated_bpm"])


def pick_partial_midi(sha16: str) -> tuple[pathlib.Path, str]:
    """Prefer Branch A merged_partial.midi (RC1+RC9); else Branch B."""
    a = BRANCH_A_ROOT / sha16 / "merged_partial.midi"
    if a.exists():
        return a, "branch_a_merged_partial"
    b = BRANCH_B_ROOT / sha16 / "merged.midi"
    if b.exists():
        return b, "branch_b_merged"
    raise FileNotFoundError(f"no partial MIDI for {sha16}")


def octave_correct(raw: float, baseline: float) -> tuple[float, str, int]:
    """Return (corrected, label, index). Deterministic tie-break to smallest index."""
    variants = [raw, raw * 2.0, raw / 2.0]
    diffs = [abs(v - baseline) for v in variants]
    idx = min(range(3), key=lambda i: diffs[i])
    labels = ["none", "double", "half"]
    return variants[idx], labels[idx], idx


def estimate_tempo(mix_path: pathlib.Path) -> tuple[float, int]:
    import librosa  # local import; keeps startup light for AST tests

    y, sr = librosa.load(str(mix_path), sr=None, mono=True)
    tempo, _beats = librosa.beat.beat_track(
        y=y,
        sr=sr,
        hop_length=HOP_LENGTH,
        start_bpm=START_BPM,
        tightness=TIGHTNESS,
    )
    # librosa may return ndarray shape (1,) or scalar; coerce deterministically
    if hasattr(tempo, "item"):
        try:
            raw = float(tempo.item())
        except ValueError:
            raw = float(tempo.flatten()[0])
    else:
        raw = float(tempo)
    return raw, int(sr)


def retempo_midi(
    src_midi: pathlib.Path,
    out_midi: pathlib.Path,
    out_musicxml: pathlib.Path,
    corrected_bpm: float,
) -> None:
    """Re-tempo the partial MIDI to corrected_bpm via music21 9.1.0.

    music21 is imported READ-ONLY (c37 lesson: never touch its cache).
    We (a) parse; (b) strip existing MetronomeMark objects; (c) insert
    a single MetronomeMark at offset 0; (d) write MIDI + MusicXML.
    """
    from music21 import converter, tempo as m21tempo, stream

    sc = converter.parse(str(src_midi))
    # Remove existing tempo indications for a clean single-tempo score.
    for elt in list(sc.recurse().getElementsByClass(m21tempo.MetronomeMark)):
        try:
            elt.activeSite.remove(elt)
        except Exception:
            pass
    mm = m21tempo.MetronomeMark(number=float(corrected_bpm))
    sc.insert(0, mm)
    # Write MIDI + MusicXML.
    out_midi.parent.mkdir(parents=True, exist_ok=True)
    sc.write("midi", fp=str(out_midi))
    sc.write("musicxml", fp=str(out_musicxml))


def per_song(song: dict, out_root: pathlib.Path) -> dict:
    sha16 = song["audio_sha16"]
    mix_path = REPO_ROOT / song["audio_path"]
    baseline_bpm = load_baseline_bpm(sha16)

    raw, sr = estimate_tempo(mix_path)
    corrected, label, idx = octave_correct(raw, baseline_bpm)
    abs_diff = abs(corrected - baseline_bpm)

    song_dir = out_root / sha16
    song_dir.mkdir(parents=True, exist_ok=True)

    src_midi, src_label = pick_partial_midi(sha16)
    out_midi = song_dir / "merged_retempo.midi"
    out_musicxml = song_dir / "merged_retempo.musicxml"
    retempo_midi(src_midi, out_midi, out_musicxml, corrected)

    est = {
        "song_id": sha16,
        "raw_estimate": raw,
        "corrected_estimate": corrected,
        "octave_correction_applied": label,
        "octave_variant_index": idx,
        "baseline_bpm": baseline_bpm,
        "abs_diff_vs_baseline": abs_diff,
        "sample_rate": sr,
        "hop_length": HOP_LENGTH,
        "start_bpm": START_BPM,
        "tightness": TIGHTNESS,
        "partial_midi_source": src_label,
        "partial_midi_sha256": sha256_file(src_midi),
    }
    est_path = song_dir / "rc5_tempo_estimate.json"
    est_path.write_text(json.dumps(est, sort_keys=True, indent=2) + "\n")

    passed = abs_diff <= PASS_THRESHOLD_BPM
    return {
        "song_id": sha16,
        "raw_estimate": raw,
        "corrected_estimate": corrected,
        "baseline_bpm": baseline_bpm,
        "octave_correction_applied": label,
        "abs_diff_vs_baseline": abs_diff,
        "verdict": "PASS" if passed else "FAIL",
        "artifacts": {
            "rc5_tempo_estimate.json": sha256_file(est_path),
            "merged_retempo.midi": sha256_file(out_midi),
            "merged_retempo.musicxml": sha256_file(out_musicxml),
        },
    }


def aggregate_verdict(per_song_rows: list[dict]) -> str:
    passes = sum(1 for r in per_song_rows if r["verdict"] == "PASS")
    if passes >= 3:
        return "RC5_LANDS"
    if passes >= 1:
        return "RC5_PARTIAL"
    return "RC5_FAILS"


def run(out_root: pathlib.Path | None = None) -> dict:
    _interpreter_guard()
    if out_root is None:
        out_root = OUT_ROOT
    out_root.mkdir(parents=True, exist_ok=True)

    songs = load_focus_set()
    per_song_rows = [per_song(s, out_root) for s in songs]
    verdict = aggregate_verdict(per_song_rows)

    rubric_hash = RUBRIC_HASH_PATH.read_text().strip()
    doc_hash = sha256_file(RUBRIC_DOC_PATH)
    assert rubric_hash == doc_hash, (
        f"rubric hash chain broken: doc={doc_hash} pin={rubric_hash}"
    )

    v = {
        "milestone": RC5_ID,
        "cycle": 53,
        "clone": "clone-2",
        "verdict": verdict,
        "n_pass": sum(1 for r in per_song_rows if r["verdict"] == "PASS"),
        "n_total": len(per_song_rows),
        "pass_threshold_bpm": PASS_THRESHOLD_BPM,
        "per_song": per_song_rows,
        "rubric_hash": rubric_hash,
    }
    (out_root / "verdict.json").write_text(json.dumps(v, sort_keys=True, indent=2) + "\n")
    return v


if __name__ == "__main__":
    v = run()
    print(json.dumps({"verdict": v["verdict"], "n_pass": v["n_pass"], "n_total": v["n_total"]}, indent=2))
