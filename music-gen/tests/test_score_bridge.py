#!/usr/bin/env python3
# M-SCORE-1 test suite. Plain assertions, no pytest.
#
# Invocation:
#   PYTHONPATH=. OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
#     /usr/bin/python3 tests/test_score_bridge.py
#
# Sections:
#   1. Seed round-trip determinism (byte-identity on two runs).
#   2. Seed round-trip note preservation (multi-set equality vs authored seed).
#   3. Merged-full-song F1 (dual: vs GT and vs BP input).
#   4. Merged pipeline determinism on real data.
#   5. Failure-mode surfacing (bad XML / missing input / timeout).
#   6. Isolation invariant (no imports of sidecar_nonfactor).
#
# Non-factor isolation: this test MUST NOT import scripts.classifier.sidecar_nonfactor.

import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

# Deterministic single-thread environment for mir_eval; propagates to
# child mscore3 subprocesses too.
for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[k] = "1"

import mido
import numpy as np
import mir_eval

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.score.bridge import (
    xml_to_midi, midi_to_xml, merge_stems_to_score, ScoreBridgeError,
)
from scripts.score.seed_score import (
    build_seed_score, write_seed_xml, seed_note_multiset, SEED_EVENTS,
)
from scripts.score.jsonl_to_midi import convert_all_stems


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.parent
SCORE_DIR = ROOT / "data" / "score"
BP_JSONL_DIR = ROOT / "data" / "transcribe" / "basic_pitch" / "synth_030s"
REF_JSONL_DIR = ROOT / "data" / "transcribe" / "reference" / "synth_030s"

SCORE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _extract_notes_per_track(mid_path: Path):
    """Return list of (track_index, notes) with notes as (onset_s, offset_s, pitch)."""
    m = mido.MidiFile(str(mid_path))
    tpb = m.ticks_per_beat
    tempo = 500000
    for tr in m.tracks:
        for msg in tr:
            if msg.type == "set_tempo":
                tempo = msg.tempo
                break
    sec_per_tick = (tempo / 1e6) / tpb
    out = []
    for i, tr in enumerate(m.tracks):
        active = {}; abs_t = 0; notes = []
        for msg in tr:
            abs_t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[(msg.channel, msg.note)] = abs_t
            elif msg.type == "note_off" or (
                msg.type == "note_on" and msg.velocity == 0
            ):
                k = (msg.channel, msg.note)
                if k in active:
                    onset_ticks = active.pop(k)
                    notes.append((
                        onset_ticks * sec_per_tick,
                        abs_t * sec_per_tick,
                        int(msg.note),
                    ))
        out.append((i, notes))
    return out


def _load_ref_jsonl(path: Path):
    notes = []
    with open(path) as f:
        for ln in f:
            r = json.loads(ln)
            notes.append((float(r["onset_s"]), float(r["offset_s"]), int(r["pitch"])))
    return notes


def _f1(ref_notes, est_notes):
    if not ref_notes and not est_notes:
        return 1.0, 1.0, 1.0
    if not ref_notes:
        return 0.0, 1.0, 0.0
    if not est_notes:
        return 1.0, 0.0, 0.0
    ref = np.array(ref_notes, dtype=float)
    est = np.array(est_notes, dtype=float)
    p, r, fv, _ = mir_eval.transcription.precision_recall_f1_overlap(
        ref[:, :2], ref[:, 2], est[:, :2], est[:, 2],
        onset_tolerance=0.05, pitch_tolerance=0.5, offset_ratio=None,
    )
    return p, r, fv


PASS = 0
FAIL = 0
FAILURES = []


def _check(cond, name):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS §{name}")
    else:
        FAIL += 1
        FAILURES.append(name)
        print(f"FAIL §{name}")


# ---------------------------------------------------------------------------
# §1  Seed round-trip determinism (byte-identity)
# ---------------------------------------------------------------------------

def test_seed_roundtrip_determinism():
    seed_xml = SCORE_DIR / "seed_8bar.musicxml"
    write_seed_xml(seed_xml)

    m1 = xml_to_midi(seed_xml, SCORE_DIR / "test_seed_m1.mid")
    x1 = midi_to_xml(m1, SCORE_DIR / "test_seed_x1.musicxml")
    m2 = xml_to_midi(x1, SCORE_DIR / "test_seed_m2.mid")
    x2 = midi_to_xml(m2, SCORE_DIR / "test_seed_x2.musicxml")

    _check(m1.read_bytes() == m2.read_bytes(),
           "1a seed MIDI byte-identical across two round-trips")
    _check(x1.read_bytes() == x2.read_bytes(),
           "1b seed scrubbed MusicXML byte-identical across two round-trips")


# ---------------------------------------------------------------------------
# §2  Seed round-trip note preservation
# ---------------------------------------------------------------------------

def test_seed_note_preservation():
    seed_xml = SCORE_DIR / "seed_8bar.musicxml"
    write_seed_xml(seed_xml)
    m1 = xml_to_midi(seed_xml, SCORE_DIR / "test_seed_m1.mid")

    exported = []
    for _, notes in _extract_notes_per_track(m1):
        exported.extend(notes)

    expected = seed_note_multiset()  # list of (part, onset_s, dur_s, pitch)
    exp_pitches = sorted([e[3] for e in expected])
    got_pitches = sorted([n[2] for n in exported])

    _check(len(exported) == len(SEED_EVENTS),
           f"2a note count exact ({len(exported)} == {len(SEED_EVENTS)})")
    _check(got_pitches == exp_pitches,
           "2b pitch multi-set exact (allowing legitimate PPQ quantization on timing)")

    # Onset preservation within 1 tick @ PPQ=480, tempo=120 BPM => ~2 ms.
    exp_onsets = sorted([e[1] for e in expected])
    got_onsets = sorted([round(n[0], 3) for n in exported])
    max_shift = max(abs(a - b) for a, b in zip(exp_onsets, got_onsets))
    _check(max_shift <= 0.003,
           f"2c onset drift <= 3 ms ({max_shift * 1000:.2f} ms observed)")


# ---------------------------------------------------------------------------
# §3  Merged-full-song F1 (dual: vs GT and vs BP input)
# ---------------------------------------------------------------------------

# Sufficiency thresholds per the research brief:
# - vs BP input (identity-merge metric, the bridge's actual invariant):
#     >= 0.98 per stem.
# - vs GT (upper-bounded by cycle-6 basic-pitch quality; brief explicitly
#     allows lower F1 here provided the diagnosis is documented):
#     record for the report, do NOT gate on 0.98.
F1_BP_MIN = 0.98

def test_merged_f1():
    stem_out_dir = SCORE_DIR / "stems_from_bp"
    stem_midis = convert_all_stems(BP_JSONL_DIR, stem_out_dir)

    out_xml = SCORE_DIR / "test_merged.musicxml"
    out_mid = SCORE_DIR / "test_merged.mid"
    merge_stems_to_score(stem_midis, out_xml, tempo_bpm=120.0,
                          time_signature=(4, 4))
    xml_to_midi(out_xml, out_mid)

    sidecar_path = out_xml.with_name(out_xml.stem + ".parts_mapping.json")
    _check(sidecar_path.exists(),
           "3a merge sidecar (parts_mapping.json) written")
    sidecar = json.loads(sidecar_path.read_text())
    parts_by_stem = sidecar["parts_by_stem"]

    all_tracks = _extract_notes_per_track(out_mid)
    non_meta = all_tracks[1:]

    merged_by_stem = {}
    cursor = 0
    for stem in sorted(parts_by_stem.keys()):
        n_parts = len(parts_by_stem[stem])
        agg = []
        for _ in range(n_parts):
            if cursor < len(non_meta):
                agg.extend(non_meta[cursor][1])
            cursor += 1
        merged_by_stem[stem] = agg

    bp_by_stem = {}
    for stem, path in stem_midis.items():
        agg = []
        for _, ns in _extract_notes_per_track(path):
            agg.extend(ns)
        bp_by_stem[stem] = agg

    # Bridge identity-merge: F1 vs BP input must be >= 0.98 per stem.
    for stem in sorted(bp_by_stem):
        p, r, fv = _f1(bp_by_stem[stem], merged_by_stem[stem])
        print(f"    §3 vs-BP {stem}: P={p:.4f} R={r:.4f} F1={fv:.4f} "
              f"ref={len(bp_by_stem[stem])} est={len(merged_by_stem[stem])}")
        _check(fv >= F1_BP_MIN,
               f"3b vs-BP {stem} F1 {fv:.4f} >= {F1_BP_MIN}")

    # vs GT: recorded for the report (upper-bounded by BP upstream noise).
    for stem, ref_name in (("drums", "drums"),
                             ("bass", "bass"),
                             ("other", "other")):
        ref = _load_ref_jsonl(REF_JSONL_DIR / f"{ref_name}.reference.jsonl")
        p, r, fv = _f1(ref, merged_by_stem[stem])
        print(f"    §3 vs-GT {stem}: P={p:.4f} R={r:.4f} F1={fv:.4f} "
              f"ref={len(ref)} est={len(merged_by_stem[stem])}")

    # Structural: the merged export must recover ALL input notes across the
    # per-stem track group (post-tie-collapse).
    for stem in sorted(bp_by_stem):
        _check(
            len(merged_by_stem[stem]) == len(bp_by_stem[stem]),
            f"3c stem {stem} note count preserved "
            f"(got {len(merged_by_stem[stem])} == {len(bp_by_stem[stem])})",
        )


# ---------------------------------------------------------------------------
# §4  Merged pipeline determinism
# ---------------------------------------------------------------------------

def test_merged_determinism():
    stem_out_dir = SCORE_DIR / "stems_from_bp"
    stem_midis = convert_all_stems(BP_JSONL_DIR, stem_out_dir)

    x1 = SCORE_DIR / "test_det_r1.musicxml"
    x2 = SCORE_DIR / "test_det_r2.musicxml"
    m1 = SCORE_DIR / "test_det_r1.mid"
    m2 = SCORE_DIR / "test_det_r2.mid"
    merge_stems_to_score(stem_midis, x1, tempo_bpm=120.0, time_signature=(4, 4))
    xml_to_midi(x1, m1)
    merge_stems_to_score(stem_midis, x2, tempo_bpm=120.0, time_signature=(4, 4))
    xml_to_midi(x2, m2)
    _check(x1.read_bytes() == x2.read_bytes(),
           "4a merged XML byte-identical across two full runs (after scrub)")
    _check(m1.read_bytes() == m2.read_bytes(),
           "4b merged MIDI byte-identical across two full runs")


# ---------------------------------------------------------------------------
# §5  Failure-mode surfacing
# ---------------------------------------------------------------------------

def test_failure_modes():
    # 5a: syntactically invalid XML.
    bad = SCORE_DIR / "test_bad.xml"
    bad.write_text("<not-actually-musicxml>oops")
    raised = None
    try:
        xml_to_midi(bad, SCORE_DIR / "test_bad_out.mid", timeout_s=10)
    except ScoreBridgeError as e:
        raised = str(e)
    _check(raised is not None and len(raised) > 0,
           "5a invalid XML raises ScoreBridgeError with non-empty message")

    # 5b: missing input file.
    raised = None
    try:
        xml_to_midi(SCORE_DIR / "does_not_exist_xyz.xml",
                     SCORE_DIR / "test_missing_out.mid", timeout_s=10)
    except ScoreBridgeError as e:
        raised = str(e)
    _check(raised is not None and "not found" in raised.lower(),
           "5b missing input raises ScoreBridgeError with 'not found' diagnostic")

    # 5c: timeout on a real input.
    seed_xml = SCORE_DIR / "seed_8bar.musicxml"
    if not seed_xml.exists():
        write_seed_xml(seed_xml)
    raised = None
    try:
        xml_to_midi(seed_xml, SCORE_DIR / "test_timeout_out.mid", timeout_s=1)
        # mscore3 3.2.3 on a small seed usually finishes < 1s; wire a
        # more aggressive timeout via _run_mscore's timeout arg
    except ScoreBridgeError as e:
        raised = str(e)
    # If the small seed finishes under 1s, force the timeout path via
    # an extremely low value (0.001s).
    if raised is None:
        try:
            xml_to_midi(seed_xml, SCORE_DIR / "test_timeout_out.mid", timeout_s=0)
        except ScoreBridgeError as e:
            raised = str(e)
    _check(raised is not None and "timed out" in raised.lower(),
           "5c timeout raises ScoreBridgeError with 'timed out' diagnostic")

    # 5d: merge_stems_to_score with a missing stem file.
    raised = None
    try:
        merge_stems_to_score(
            {"bass": SCORE_DIR / "no_such_bass.mid"},
            SCORE_DIR / "test_bad_merge.musicxml",
        )
    except ScoreBridgeError as e:
        raised = str(e)
    _check(raised is not None and "stem MIDI not found" in raised,
           "5d missing stem MIDI raises ScoreBridgeError with 'stem MIDI not found'")


# ---------------------------------------------------------------------------
# §6  Isolation invariant
# ---------------------------------------------------------------------------

def test_isolation():
    # Grep every .py under scripts/score/ + this test file. No import of
    # sidecar_nonfactor allowed.
    targets = list((ROOT / "scripts" / "score").rglob("*.py"))
    targets.append(Path(__file__))
    hits = []
    pat = re.compile(r"^\s*(from|import)\s+scripts\.classifier\.sidecar_nonfactor",
                     re.MULTILINE)
    for p in targets:
        text = p.read_text()
        if pat.search(text):
            hits.append(str(p))
    _check(len(hits) == 0,
           f"6a no sidecar_nonfactor imports in scripts/score/ or test "
           f"({len(hits)} hits)")

    # Also assert the module actually exposes the promised API.
    from scripts.score import bridge
    for name in ("xml_to_midi", "midi_to_xml", "merge_stems_to_score",
                 "ScoreBridgeError"):
        _check(hasattr(bridge, name),
               f"6b bridge module exposes {name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_seed_roundtrip_determinism()
    test_seed_note_preservation()
    test_merged_f1()
    test_merged_determinism()
    test_failure_modes()
    test_isolation()

    print()
    print(f"result: {'PASS' if FAIL == 0 else 'FAIL'} "
          f"({PASS} pass, {FAIL} fail)")
    if FAIL:
        for name in FAILURES:
            print(f"  FAILED §{name}")
        sys.exit(1)
