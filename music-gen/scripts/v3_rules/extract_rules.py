#!/usr/bin/env /usr/bin/python3
"""V3 deterministic rules extractor (M-V3-RULES-1, cycle 23, clone 2).

Reads the four operator-approved v3 merged.mid corpora READ-ONLY and emits
a byte-deterministic rules artifact under a caller-supplied out-dir. See
docs/v3_rules_deterministic_extractor_spec_c23.md for the contract.

No PRNG. No sidecar_nonfactor. No VST3 state APIs. Interpreter guard on.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import mido

# --- Fixed constants (no clock, no PRNG) ---
EXTRACT_TS_ISO = "2026-09-02T00:00:00Z"
EXTRACTOR_VERSION = "v3-rules-c23-1"
STEM_ORDER = ("bass", "drums", "guitar", "piano", "vocals", "other")
RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")

CORPUS = (
    ("31a164f845f8e27e", "data/v3_spine/31a164f845f8e27e/merged.mid"),
    ("252eb21ce7df7328", "data/v3/deliveries/252eb21ce7df7328/merged.mid"),
    ("51e433ade2a845e1", "data/v3/deliveries/51e433ade2a845e1/merged.mid"),
    ("cdd2717e52820ff6", "data/v3/deliveries/cdd2717e52820ff6/merged.mid"),
)

FETCHABILITY_CANDIDATES = ("music21", "mingus", "jsonschema", "sklearn")


def _assert_env():
    assert sys.executable == "/usr/bin/python3", (
        "interpreter guard: expected /usr/bin/python3, got " + sys.executable
    )
    assert os.environ.get("PYTHONHASHSEED") == "0", "PYTHONHASHSEED must be 0"
    assert os.environ.get("TZ") == "UTC", "TZ must be UTC"
    assert os.environ.get("LC_ALL") == "C.UTF-8", "LC_ALL must be C.UTF-8"
    assert os.environ.get("SOURCE_DATE_EPOCH"), "SOURCE_DATE_EPOCH must be set"


def _canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)


def _rule_id(params):
    h = hashlib.sha256(_canonical_json(params).encode("ascii")).hexdigest()
    return "rule_" + h[:16]


def _event_id(rule_id, song_sha16, stem):
    payload = (rule_id + "|" + song_sha16 + "|" + stem).encode("ascii")
    return hashlib.sha256(payload).hexdigest()[:32]


def _stem_notes(track, tpb):
    """Return sorted list of (start_tick, end_tick, pitch, velocity) tuples."""
    t = 0
    active = {}
    notes = []
    for msg in track:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            active.setdefault(msg.note, []).append((t, msg.velocity))
        elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
            key = active.get(msg.note)
            if key:
                start, vel = key.pop(0)
                notes.append((start, t, msg.note, vel))
    notes.sort()
    return notes


def _harmonic_rule(song_sha16, stem, notes, tpb, track_index):
    if not notes:
        return None
    pc_hist = [0] * 12
    for _, _, p, _ in notes:
        pc_hist[p % 12] += 1
    total = sum(pc_hist)
    pc_dist = [round(c / total, 6) for c in pc_hist]
    key_idx = max(range(12), key=lambda i: pc_hist[i])
    params = {
        "pitch_class_distribution": pc_dist,
        "dominant_pitch_class": key_idx,
        "window_beats": 4,
    }
    rid = _rule_id(params)
    end_tick = notes[-1][1]
    return {
        "schema_v": 1,
        "event_type": "rule",
        "rule_type": "harmonic",
        "rule_id": rid,
        "event_id": _event_id(rid, song_sha16, stem),
        "extractor": "extract.harmonic",
        "extractor_version": EXTRACTOR_VERSION,
        "parameters": params,
        "provenance_pointers": [{
            "song_sha16": song_sha16,
            "stem": stem,
            "measure_range": [0, max(1, end_tick // (tpb * 4))],
            "midi_track_index": track_index,
            "midi_ticks_per_beat": tpb,
        }],
        "scope": {"level": "song", "start_s": 0.0, "end_s": 0.0},
        "confidence": 0.75,
        "parameters_random_state": 0,
        "ts": EXTRACT_TS_ISO,
    }


def _rhythmic_rule(song_sha16, stem, notes, tpb, track_index):
    if not notes:
        return None
    onsets = [n[0] for n in notes]
    beat_ticks = tpb
    on_beat = sum(1 for o in onsets if (o % beat_ticks) == 0)
    off_beat = len(onsets) - on_beat
    duration_ticks = max(onsets[-1], 1)
    n_bars = max(1, duration_ticks // (tpb * 4))
    density_per_bar = round(len(onsets) / n_bars, 4)
    grid = 8
    for g in (16, 8, 4):
        if all((o * g) % tpb == 0 for o in onsets[:64]):
            grid = g
            break
    params = {
        "onset_density_per_bar": density_per_bar,
        "on_beat_fraction": round(on_beat / max(1, len(onsets)), 4),
        "quantization_grid_subdivisions_per_beat": grid,
    }
    rid = _rule_id(params)
    return {
        "schema_v": 1,
        "event_type": "rule",
        "rule_type": "rhythmic",
        "rule_id": rid,
        "event_id": _event_id(rid, song_sha16, stem),
        "extractor": "extract.rhythmic",
        "extractor_version": EXTRACTOR_VERSION,
        "parameters": params,
        "provenance_pointers": [{
            "song_sha16": song_sha16,
            "stem": stem,
            "measure_range": [0, int(n_bars)],
            "midi_track_index": track_index,
            "midi_ticks_per_beat": tpb,
        }],
        "scope": {"level": "song", "start_s": 0.0, "end_s": 0.0},
        "confidence": 0.7,
        "parameters_random_state": 0,
        "ts": EXTRACT_TS_ISO,
    }


def _melodic_rule(song_sha16, stem, notes, tpb, track_index):
    if len(notes) < 2:
        return None
    pitches = [n[2] for n in notes]
    intervals = [pitches[i + 1] - pitches[i] for i in range(len(pitches) - 1)]
    ihist = {}
    for iv in intervals:
        ihist[str(iv)] = ihist.get(str(iv), 0) + 1
    ihist_sorted = dict(sorted(ihist.items()))
    params = {
        "interval_histogram": ihist_sorted,
        "range_semitones": max(pitches) - min(pitches),
        "n_notes": len(pitches),
    }
    rid = _rule_id(params)
    end_tick = notes[-1][1]
    return {
        "schema_v": 1,
        "event_type": "rule",
        "rule_type": "melodic",
        "rule_id": rid,
        "event_id": _event_id(rid, song_sha16, stem),
        "extractor": "extract.melodic",
        "extractor_version": EXTRACTOR_VERSION,
        "parameters": params,
        "provenance_pointers": [{
            "song_sha16": song_sha16,
            "stem": stem,
            "measure_range": [0, max(1, end_tick // (tpb * 4))],
            "midi_track_index": track_index,
            "midi_ticks_per_beat": tpb,
        }],
        "scope": {"level": "song", "start_s": 0.0, "end_s": 0.0},
        "confidence": 0.7,
        "parameters_random_state": 0,
        "ts": EXTRACT_TS_ISO,
    }


def _form_rule(song_sha16, stem, notes, tpb, track_index):
    if not notes:
        return None
    bar_ticks = tpb * 4
    end_tick = notes[-1][1]
    n_bars = max(1, end_tick // bar_ticks)
    active_bars = set()
    for s, e, _, _ in notes:
        b0 = s // bar_ticks
        b1 = max(b0, (e - 1) // bar_ticks)
        for b in range(b0, b1 + 1):
            active_bars.add(int(b))
    boundaries = []
    prev_active = False
    for b in range(int(n_bars) + 1):
        is_active = b in active_bars
        if is_active != prev_active:
            boundaries.append(int(b))
        prev_active = is_active
    params = {
        "n_bars": int(n_bars),
        "section_boundaries_bars": boundaries,
        "n_active_bars": len(active_bars),
    }
    rid = _rule_id(params)
    return {
        "schema_v": 1,
        "event_type": "rule",
        "rule_type": "form",
        "rule_id": rid,
        "event_id": _event_id(rid, song_sha16, stem),
        "extractor": "extract.form",
        "extractor_version": EXTRACTOR_VERSION,
        "parameters": params,
        "provenance_pointers": [{
            "song_sha16": song_sha16,
            "stem": stem,
            "measure_range": [0, int(n_bars)],
            "midi_track_index": track_index,
            "midi_ticks_per_beat": tpb,
        }],
        "scope": {"level": "song", "start_s": 0.0, "end_s": 0.0},
        "confidence": 0.6,
        "parameters_random_state": 0,
        "ts": EXTRACT_TS_ISO,
    }


def _arrangement_rule(song_sha16, per_stem_notes, tpb):
    bar_ticks = tpb * 4
    end_tick = 0
    for notes in per_stem_notes.values():
        if notes:
            end_tick = max(end_tick, notes[-1][1])
    n_bars = max(1, end_tick // bar_ticks)
    windows = []
    win_bars = 4
    for w in range(0, int(n_bars), win_bars):
        active = []
        w_lo = w * bar_ticks
        w_hi = (w + win_bars) * bar_ticks
        for stem in STEM_ORDER:
            notes = per_stem_notes.get(stem, [])
            if any(s < w_hi and e > w_lo for s, e, _, _ in notes):
                active.append(stem)
        windows.append({"window_bar_start": w, "active_stems": active})
    params = {
        "window_bars": win_bars,
        "windows": windows,
        "n_windows": len(windows),
    }
    rid = _rule_id(params)
    return {
        "schema_v": 1,
        "event_type": "rule",
        "rule_type": "arrangement",
        "rule_id": rid,
        "event_id": _event_id(rid, song_sha16, "full_mix"),
        "extractor": "extract.arrangement",
        "extractor_version": EXTRACTOR_VERSION,
        "parameters": params,
        "provenance_pointers": [{
            "song_sha16": song_sha16,
            "stem": "full_mix",
            "measure_range": [0, int(n_bars)],
            "midi_track_index": -1,
            "midi_ticks_per_beat": tpb,
        }],
        "scope": {"level": "song", "start_s": 0.0, "end_s": 0.0},
        "confidence": 0.65,
        "parameters_random_state": 0,
        "ts": EXTRACT_TS_ISO,
    }


def _emit_fetchability(out_dir):
    rows = []
    for name in FETCHABILITY_CANDIDATES:
        try:
            __import__(name)
            on_disk = True
            note = "importable"
        except Exception as e:
            on_disk = False
            note = type(e).__name__
        rows.append({
            "candidate": name,
            "on_disk": on_disk,
            "note": note,
            "no_fetch_attempts": True,
            "probe_ts": EXTRACT_TS_ISO,
        })
    rows.sort(key=lambda r: r["candidate"])
    path = out_dir / "fetchability_ladder.jsonl"
    with path.open("w", encoding="ascii") as f:
        for r in rows:
            f.write(_canonical_json(r) + "\n")
    return path


def extract(repo_root: Path, out_dir: Path):
    _assert_env()
    out_dir.mkdir(parents=True, exist_ok=True)
    _emit_fetchability(out_dir)

    all_rules = []
    for song_sha16, rel in CORPUS:
        mid_path = repo_root / rel
        mf = mido.MidiFile(str(mid_path))
        tpb = mf.ticks_per_beat
        by_name = {}
        by_index = {}
        for i, tr in enumerate(mf.tracks):
            nm = (tr.name or "").strip().lower()
            if nm in STEM_ORDER:
                by_name[nm] = tr
                by_index[nm] = i
        per_stem_notes = {}
        for stem in STEM_ORDER:
            tr = by_name.get(stem)
            if tr is None:
                per_stem_notes[stem] = []
                continue
            notes = _stem_notes(tr, tpb)
            per_stem_notes[stem] = notes
            ti = by_index[stem]
            for fn in (_harmonic_rule, _rhythmic_rule, _melodic_rule,
                       _form_rule):
                r = fn(song_sha16, stem, notes, tpb, ti)
                if r is not None:
                    all_rules.append(r)
        arr = _arrangement_rule(song_sha16, per_stem_notes, tpb)
        if arr is not None:
            all_rules.append(arr)

    all_rules.sort(key=lambda r: (r["rule_type"], r["rule_id"], r["event_id"]))

    art_path = out_dir / "rules_artifact.jsonl"
    with art_path.open("w", encoding="ascii") as f:
        for r in all_rules:
            f.write(_canonical_json(r) + "\n")

    sha = hashlib.sha256(art_path.read_bytes()).hexdigest()
    (out_dir / "rules_artifact.sha256").write_text(sha + "\n")

    return {
        "rules_artifact_sha256": sha,
        "n_rules": len(all_rules),
        "n_rules_by_type": {t: sum(1 for r in all_rules if r["rule_type"] == t)
                            for t in RULE_TYPES},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args()
    result = extract(args.repo_root.resolve(), args.out_dir.resolve())
    sys.stdout.write(_canonical_json(result) + "\n")


if __name__ == "__main__":
    main()
