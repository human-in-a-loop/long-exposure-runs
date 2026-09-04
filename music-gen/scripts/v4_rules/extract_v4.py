#!/usr/bin/python3
# ---
# cycle: 21
# milestone: M-V4-RULES-1/substantive
# purpose: Substantive M-V4-RULES-1 extractor. Two models over the 5
#          operator-approved focus songs:
#          * Model A - statistical style model (tempo/key/mode,
#            chord-transition matrices, per-instrument groove templates
#            on the 16th grid, note-density and register profiles,
#            bar-length statistics; plus per-song audio descriptor arcs
#            derived from section.wav).
#          * Model B - lightweight learned sequence model: cellular
#            automaton bar-transition model fitted per instrument on
#            binary onset vectors, with a variable-order Markov
#            comparison point. Per operator direction 2026-09-03 the
#            CA is retained unless it clearly fails (degenerate output
#            or gross Model-A non-conformance) - both models remain
#            available to the generator.
#          Also emits a v3-shape rules_artifact.jsonl (harmonic +
#          rhythmic + melodic + form + arrangement) so downstream
#          consumers of the v3 rules artifact keep working.
# ---
"""M-V4-RULES-1 substantive extractor.

Deterministic given the 7-key env-pin. Reads the five focus songs'
merged.mid + section.wav READ-ONLY. Emits under `data/v4/rules/`:
    statistical_model.json     - Model A (per-song + aggregated)
    sequence_model.json        - Model B (CA per instrument + VOMM)
    audio_descriptors.jsonl    - per-song energy/spectral/LUFS arcs
    rules_artifact.jsonl       - v3-shape rule rows (76+ rows)
    rules_artifact.sha256      - hex of the JSONL
    manifest.json              - inventory + shas + env_pin

Contracts:
    * No PRNG, no `sidecar_nonfactor` import, no VST3 state APIs.
    * `/usr/bin/python3` interpreter guard.
    * Canonical JSON with sort_keys=True; ASCII writes.
    * Rule rows preserve the c23 shape so v3 consumers keep working.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import wave
from pathlib import Path
from typing import Any

import mido

# --- Canonical constants (no PRNG, no clock) ---
EXTRACT_TS_ISO = "2026-09-04T07:00:00Z"
EXTRACTOR_VERSION = "v4-rules-c21-1"

STEM_ORDER = ("bass", "drums", "guitar", "piano", "vocals", "other")
RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")

CANONICAL_ENV_PIN_SHA = (
    "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
)

# Focus set (band 6/7, all operator-approved). Names are for humans;
# provenance is by song_sha16 + on-disk paths.
CORPUS = (
    ("31a164f845f8e27e", "Chicken Grease", "6",
     "data/v3_spine/31a164f845f8e27e/merged.mid",
     "data/v3_spine/31a164f845f8e27e/operator_section_c26_checkpointed/section.wav"),
    ("252eb21ce7df7328", "What If I Go", "7",
     "data/v3/deliveries/252eb21ce7df7328/merged.mid",
     "data/v3_spine/252eb21ce7df7328/operator_section/section.wav"),
    ("51e433ade2a845e1", "Rome", "6",
     "data/v3/deliveries/51e433ade2a845e1/merged.mid",
     "data/v3_spine/51e433ade2a845e1/operator_section/section.wav"),
    ("cdd2717e52820ff6", "Disco A", "6",
     "data/v3/deliveries/cdd2717e52820ff6/merged.mid",
     "data/v3_spine/cdd2717e52820ff6/operator_section/section.wav"),
    ("88d247468cb6d49f", "Peach Dream", "7",
     "data/v3/deliveries/88d247468cb6d49f/cycle25/merged.mid",
     "data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/section.wav"),
)

__all__ = (
    "extract",
    "list_corpus_songs",
    "compute_rule_id",
    "extract_rules_v4",
)


# ----- discipline guards -----

def _assert_env() -> None:
    if sys.executable != "/usr/bin/python3":
        raise RuntimeError(
            f"interpreter guard: expected /usr/bin/python3, got {sys.executable}"
        )
    for k, v in (("PYTHONHASHSEED", "0"), ("TZ", "UTC"), ("LC_ALL", "C.UTF-8")):
        if os.environ.get(k) != v:
            raise RuntimeError(f"env-pin: {k} must be {v!r}, got {os.environ.get(k)!r}")
    if not os.environ.get("SOURCE_DATE_EPOCH"):
        raise RuntimeError("env-pin: SOURCE_DATE_EPOCH must be set")


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_rule_id(params: dict) -> str:
    h = hashlib.sha256(_canonical_json(params).encode("ascii")).hexdigest()
    return "rule_" + h[:16]


def _event_id(rule_id: str, song_sha16: str, stem: str) -> str:
    payload = (rule_id + "|" + song_sha16 + "|" + stem).encode("ascii")
    return hashlib.sha256(payload).hexdigest()[:32]


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def list_corpus_songs() -> tuple:
    return tuple(row[0] for row in CORPUS)


# ----- MIDI plumbing (deterministic) -----

def _stem_notes(track, tpb):
    """Return sorted list of (start_tick, end_tick, pitch, velocity)."""
    t = 0
    active: dict[int, list] = {}
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


def _mid_tempo_bpm(mf) -> float:
    """Return first-track set_tempo as bpm; default 120.0."""
    for tr in mf.tracks:
        for msg in tr:
            if msg.type == "set_tempo":
                return round(60_000_000.0 / float(msg.tempo), 3)
    return 120.0


def _load_song_notes(mid_path: Path):
    mf = mido.MidiFile(str(mid_path))
    tpb = mf.ticks_per_beat
    per_stem = {s: [] for s in STEM_ORDER}
    per_stem_track_index = {s: -1 for s in STEM_ORDER}
    for i, tr in enumerate(mf.tracks):
        nm = (tr.name or "").strip().lower()
        if nm in STEM_ORDER:
            per_stem[nm] = _stem_notes(tr, tpb)
            per_stem_track_index[nm] = i
    bpm = _mid_tempo_bpm(mf)
    return tpb, bpm, per_stem, per_stem_track_index


# ----- Model A rule rows (v3-shape + audio-arc extension) -----

def _harmonic_rule(song_sha16, stem, notes, tpb, track_index):
    if not notes:
        return None
    pc_hist = [0] * 12
    for _, _, p, _ in notes:
        pc_hist[p % 12] += 1
    total = sum(pc_hist)
    pc_dist = [round(c / total, 6) for c in pc_hist]
    dominant = max(range(12), key=lambda i: pc_hist[i])
    params = {
        "pitch_class_distribution": pc_dist,
        "dominant_pitch_class": dominant,
        "window_beats": 4,
    }
    rid = compute_rule_id(params)
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
            "song_sha16": song_sha16, "stem": stem,
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
    on_beat = sum(1 for o in onsets if (o % tpb) == 0)
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
    rid = compute_rule_id(params)
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
            "song_sha16": song_sha16, "stem": stem,
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
    ihist: dict[str, int] = {}
    for iv in intervals:
        ihist[str(iv)] = ihist.get(str(iv), 0) + 1
    ihist_sorted = dict(sorted(ihist.items()))
    params = {
        "interval_histogram": ihist_sorted,
        "range_semitones": max(pitches) - min(pitches),
        "n_notes": len(pitches),
    }
    rid = compute_rule_id(params)
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
            "song_sha16": song_sha16, "stem": stem,
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
    active_bars: set[int] = set()
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
    rid = compute_rule_id(params)
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
            "song_sha16": song_sha16, "stem": stem,
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
    win_bars = 4
    windows = []
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
    rid = compute_rule_id(params)
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
            "song_sha16": song_sha16, "stem": "full_mix",
            "measure_range": [0, int(n_bars)],
            "midi_track_index": -1,
            "midi_ticks_per_beat": tpb,
        }],
        "scope": {"level": "song", "start_s": 0.0, "end_s": 0.0},
        "confidence": 0.65,
        "parameters_random_state": 0,
        "ts": EXTRACT_TS_ISO,
    }


# ----- Model A structured summary (statistical_model.json) -----

def _groove_template_16th(notes, tpb):
    """16th-grid onset histogram + velocity means per position (16 slots).

    Deterministic pure function of MIDI notes and tpb.
    """
    slots_per_bar = 16
    slot_ticks = (tpb * 4) / slots_per_bar
    onset_hist = [0] * slots_per_bar
    vel_sum = [0] * slots_per_bar
    for s, _, _, v in notes:
        # nearest-slot rounding (deterministic tie-break via round())
        pos = int((s % (tpb * 4)) / slot_ticks + 0.5) % slots_per_bar
        onset_hist[pos] += 1
        vel_sum[pos] += int(v)
    vel_mean = [round(vel_sum[i] / onset_hist[i], 3) if onset_hist[i] else 0.0
                for i in range(slots_per_bar)]
    total = sum(onset_hist)
    onset_prob = [round(c / total, 6) if total else 0.0 for c in onset_hist]
    return {
        "slots_per_bar": slots_per_bar,
        "onset_hist": onset_hist,
        "onset_prob_per_slot": onset_prob,
        "velocity_mean_per_slot": vel_mean,
        "n_notes": total,
    }


def _register_profile(notes):
    if not notes:
        return {"n_notes": 0}
    pitches = sorted(n[2] for n in notes)
    m = pitches[len(pitches) // 2]
    return {
        "n_notes": len(pitches),
        "pitch_min": pitches[0],
        "pitch_max": pitches[-1],
        "pitch_median": m,
        "pitch_mean_x100": int(round(100 * sum(pitches) / len(pitches))),
    }


def _key_estimate(all_pc_hist):
    """Krumhansl-style major/minor best-fit key on a 12-bin pc histogram.

    Deterministic pure function.
    """
    major = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    minor = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    total = sum(all_pc_hist) or 1.0
    norm = [c / total for c in all_pc_hist]
    best = None
    for root in range(12):
        for mode_name, profile in (("major", major), ("minor", minor)):
            rotated = profile[-root:] + profile[:-root]
            score = sum(norm[i] * rotated[i] for i in range(12))
            if (best is None) or (score > best[0]):
                best = (score, root, mode_name)
    return {
        "root_pc": best[1],
        "mode": best[2],
        "krumhansl_score": round(float(best[0]), 6),
    }


def _chord_transition_matrix(all_notes, tpb):
    """Beat-level pitch-class-set transitions across the pitched stems.

    Returns a nested dict {from_pcset: {to_pcset: count}} keyed by
    sorted comma-joined pc strings, plus the sorted state vocabulary.
    """
    beat_ticks = tpb  # one PC slice per beat
    by_beat: dict[int, set[int]] = {}
    for s, e, p, _ in all_notes:
        b0 = s // beat_ticks
        b1 = max(b0, (e - 1) // beat_ticks)
        for b in range(int(b0), int(b1) + 1):
            by_beat.setdefault(int(b), set()).add(int(p) % 12)
    if not by_beat:
        return {"states": [], "transitions": {}, "n_transitions": 0}
    max_beat = max(by_beat)
    states_seq = []
    for b in range(max_beat + 1):
        pcset = by_beat.get(b)
        if pcset:
            states_seq.append(",".join(str(x) for x in sorted(pcset)))
    if len(states_seq) < 2:
        return {"states": sorted(set(states_seq)), "transitions": {},
                "n_transitions": 0}
    transitions: dict[str, dict[str, int]] = {}
    for i in range(len(states_seq) - 1):
        a, b = states_seq[i], states_seq[i + 1]
        transitions.setdefault(a, {})[b] = transitions.get(a, {}).get(b, 0) + 1
    # canonical ordering
    canon = {k: dict(sorted(v.items())) for k, v in sorted(transitions.items())}
    vocab = sorted({k for k in canon} | {t for v in canon.values() for t in v})
    return {
        "states": vocab,
        "transitions": canon,
        "n_transitions": len(states_seq) - 1,
    }


# ----- Model B: cellular-automaton bar-transition model -----

def _binary_bar_grid(notes, tpb, slots_per_bar=16):
    """Return list of int-bar-vectors (each 16 bits) of note onsets.

    Each bar is 16 slots; bit set if any onset falls on that slot.
    """
    if not notes:
        return []
    bar_ticks = tpb * 4
    slot_ticks = bar_ticks / slots_per_bar
    end_tick = notes[-1][1]
    n_bars = int(max(1, end_tick // bar_ticks))
    bars = [[0] * slots_per_bar for _ in range(n_bars + 1)]
    for s, _, _, _ in notes:
        b = int(s // bar_ticks)
        pos = int((s % bar_ticks) / slot_ticks + 0.5) % slots_per_bar
        if 0 <= b < len(bars):
            bars[b][pos] = 1
    # trim trailing all-zero bars
    while bars and sum(bars[-1]) == 0:
        bars.pop()
    return bars


def _fit_ca_rules_1d(bars, radius=1):
    """Fit a 1D radius-r CA rule per instrument on binary bar vectors.

    Rule = for each position i in bar t+1, predict bit from the (2r+1)
    neighborhood in bar t centered at position i (wrapping). Returns
    the majority-vote decision table + per-neighborhood entropy stats.

    Deterministic pure function.
    """
    if len(bars) < 2:
        return {"n_bars": len(bars), "insufficient_data": True}
    slots_per_bar = len(bars[0])
    n_states = 1 << (2 * radius + 1)
    counts_one = [0] * n_states
    counts_total = [0] * n_states
    for t in range(len(bars) - 1):
        cur = bars[t]
        nxt = bars[t + 1]
        for i in range(slots_per_bar):
            neigh_bits = 0
            for k in range(-radius, radius + 1):
                idx = (i + k) % slots_per_bar
                neigh_bits = (neigh_bits << 1) | (cur[idx] & 1)
            counts_total[neigh_bits] += 1
            counts_one[neigh_bits] += nxt[i]
    table = []
    for s in range(n_states):
        if counts_total[s] == 0:
            table.append({"state": s, "p_one": None, "count": 0, "decision": None})
            continue
        p = counts_one[s] / counts_total[s]
        decision = 1 if p >= 0.5 else 0
        table.append({
            "state": s,
            "p_one": round(p, 6),
            "count": counts_total[s],
            "decision": decision,
        })
    # accuracy on training set (self-consistency)
    correct = 0
    total = 0
    for t in range(len(bars) - 1):
        cur = bars[t]
        nxt = bars[t + 1]
        for i in range(slots_per_bar):
            neigh_bits = 0
            for k in range(-radius, radius + 1):
                idx = (i + k) % slots_per_bar
                neigh_bits = (neigh_bits << 1) | (cur[idx] & 1)
            pred = table[neigh_bits]["decision"]
            if pred is not None:
                total += 1
                if pred == nxt[i]:
                    correct += 1
    acc = round(correct / total, 6) if total else 0.0
    return {
        "radius": radius,
        "n_bars": len(bars),
        "slots_per_bar": slots_per_bar,
        "rule_table": table,
        "training_accuracy": acc,
    }


def _generate_ca(seed_bar, ca_fit, n_steps=8, slots_per_bar=16, radius=1):
    """Deterministic CA generation from a fixed seed bar.

    Used to detect degenerate output (all-off or all-on across steps).
    """
    if ca_fit.get("insufficient_data") or not ca_fit.get("rule_table"):
        return {"insufficient_data": True}
    table = ca_fit["rule_table"]
    cur = list(seed_bar)
    trajectory = [list(cur)]
    for _ in range(n_steps):
        nxt = [0] * slots_per_bar
        for i in range(slots_per_bar):
            neigh_bits = 0
            for k in range(-radius, radius + 1):
                idx = (i + k) % slots_per_bar
                neigh_bits = (neigh_bits << 1) | (cur[idx] & 1)
            dec = table[neigh_bits]["decision"]
            nxt[i] = 0 if dec is None else int(dec)
        cur = nxt
        trajectory.append(list(cur))
    ones = [sum(row) for row in trajectory]
    return {
        "n_steps": n_steps,
        "ones_per_step": ones,
        "degenerate_all_off": all(o == 0 for o in ones[1:]),
        "degenerate_all_on": all(o == slots_per_bar for o in ones[1:]),
    }


def _fit_vomm(bars, order=2):
    """Fit a variable-order Markov (VOMM) on token sequence.

    Tokens = int representation of each bar's 16-bit vector. Returns
    per-order transition tables (dicts keyed by string prefix), plus
    training accuracy for one-step-ahead prediction at each order.
    """
    if len(bars) < order + 1:
        return {"insufficient_data": True, "n_bars": len(bars), "order": order}
    tokens = []
    for row in bars:
        t = 0
        for bit in row:
            t = (t << 1) | (bit & 1)
        tokens.append(int(t))
    accs = {}
    tables = {}
    for k in range(1, order + 1):
        counts: dict[str, dict[str, int]] = {}
        for i in range(len(tokens) - k):
            prefix = ",".join(str(x) for x in tokens[i:i + k])
            nxt = str(tokens[i + k])
            counts.setdefault(prefix, {})[nxt] = counts.get(prefix, {}).get(nxt, 0) + 1
        # canonical
        canon = {p: dict(sorted(v.items())) for p, v in sorted(counts.items())}
        tables[str(k)] = canon
        # predict via argmax of counts (stable tie-break: smallest token first)
        correct, total = 0, 0
        for i in range(len(tokens) - k):
            prefix = ",".join(str(x) for x in tokens[i:i + k])
            row = canon.get(prefix, {})
            if not row:
                continue
            best_key = None
            best_val = -1
            for kk, vv in row.items():
                if vv > best_val or (vv == best_val and (best_key is None or int(kk) < int(best_key))):
                    best_val = vv
                    best_key = kk
            total += 1
            if int(best_key) == tokens[i + k]:
                correct += 1
        accs[str(k)] = round(correct / total, 6) if total else 0.0
    return {
        "n_bars": len(bars),
        "order": order,
        "token_alphabet_size": len(set(tokens)),
        "accuracy_by_order": accs,
        "transition_tables": tables,
    }


# ----- audio descriptors (energy arc + spectral balance + LUFS) -----

def _read_wav_mono_int16(p: Path):
    with wave.open(str(p), "rb") as w:
        sr = w.getframerate()
        nch = w.getnchannels()
        sampw = w.getsampwidth()
        nf = w.getnframes()
        raw = w.readframes(nf)
    if sampw != 2:
        raise RuntimeError(f"unsupported sampwidth={sampw} for {p}")
    import struct
    fmt = "<" + "h" * (len(raw) // 2)
    ints = struct.unpack(fmt, raw)
    if nch == 1:
        mono = list(ints)
    else:
        mono = [sum(ints[i * nch:(i + 1) * nch]) // nch for i in range(nf)]
    return sr, mono


def _energy_arc(mono, sr, hop_s=0.5):
    hop = max(1, int(round(sr * hop_s)))
    out = []
    for i in range(0, len(mono), hop):
        block = mono[i:i + hop]
        if not block:
            continue
        acc = 0
        for x in block:
            acc += x * x
        rms = (acc / len(block)) ** 0.5
        db = 20.0 * (0.0 if rms == 0 else (__import__("math").log10(rms / 32768.0)))
        out.append(round(db, 3))
    return {"hop_s": hop_s, "n_frames": len(out), "rms_dbfs_per_hop": out}


def _spectral_balance(mono, sr, band_edges_hz=(0, 200, 800, 3200, 12800, 22050),
                      hop_s=1.0):
    """Very light band-energy trajectory via FFT of hop-sized windows.

    Uses a rectangular window (no PRNG); returns per-hop per-band dBFS.
    """
    import math
    hop = max(256, int(round(sr * hop_s)))
    # nearest power of two >= hop
    n_fft = 1
    while n_fft < hop:
        n_fft <<= 1
    edges = tuple(band_edges_hz)
    n_bands = len(edges) - 1
    def _fft_mag(block):
        # numpy is available (v3 stack); use it deterministically.
        import numpy as np
        x = np.array(block, dtype=np.float64)
        if len(x) < n_fft:
            x = np.concatenate([x, np.zeros(n_fft - len(x))])
        else:
            x = x[:n_fft]
        X = np.fft.rfft(x)
        mag = np.abs(X) / max(1, len(x))
        return mag
    freqs = None
    frames = []
    for i in range(0, len(mono), hop):
        block = mono[i:i + hop]
        if len(block) < hop:
            break
        mag = _fft_mag(block)
        if freqs is None:
            import numpy as np
            freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
        band_energy = [0.0] * n_bands
        for bi in range(n_bands):
            lo, hi = edges[bi], edges[bi + 1]
            mask = (freqs >= lo) & (freqs < hi)
            e = float((mag[mask] ** 2).sum())
            band_energy[bi] = e
        # normalized dB
        total = sum(band_energy) or 1e-12
        row = [round(10.0 * math.log10(max(1e-12, e / total)), 3) for e in band_energy]
        frames.append(row)
    return {
        "hop_s": hop_s,
        "band_edges_hz": list(edges),
        "n_frames": len(frames),
        "band_db_normalized_per_hop": frames,
    }


def _section_lufs_i(mono, sr):
    """Compute LUFS-I via pyloudnorm if present; else RMS-dBFS fallback."""
    try:
        import numpy as np
        import pyloudnorm as pyln  # noqa: F401
        arr = np.array(mono, dtype=np.float32) / 32768.0
        meter = pyln.Meter(sr)
        return {"lufs_i": round(float(meter.integrated_loudness(arr)), 3),
                "measurement": "pyloudnorm"}
    except Exception:
        import math
        acc = 0
        for x in mono:
            acc += x * x
        rms = (acc / max(1, len(mono))) ** 0.5
        db = 20.0 * (0.0 if rms == 0 else math.log10(rms / 32768.0))
        return {"lufs_i": None, "rms_dbfs": round(db, 3),
                "measurement": "rms_fallback"}


def _audio_descriptors_for_song(song_sha16, section_wav_path: Path):
    sr, mono = _read_wav_mono_int16(section_wav_path)
    arc = _energy_arc(mono, sr, hop_s=0.5)
    sb = _spectral_balance(mono, sr, hop_s=1.0)
    lufs = _section_lufs_i(mono, sr)
    return {
        "song_sha16": song_sha16,
        "section_wav_sha256": _sha256_file(section_wav_path),
        "sample_rate": sr,
        "duration_s": round(len(mono) / sr, 3),
        "energy_arc": arc,
        "spectral_balance": sb,
        "section_lufs_i": lufs,
    }


# ----- driver -----

def extract(repo_root: Path, out_dir: Path) -> dict:
    _assert_env()
    out_dir.mkdir(parents=True, exist_ok=True)

    all_rule_rows: list[dict] = []
    per_song_stat: dict[str, dict] = {}
    per_song_seq: dict[str, dict] = {}
    audio_rows: list[dict] = []
    corpus_index: list[dict] = []

    for song_sha16, name, band, mid_rel, wav_rel in CORPUS:
        mid_path = repo_root / mid_rel
        wav_path = repo_root / wav_rel
        tpb, bpm, per_stem, per_stem_ti = _load_song_notes(mid_path)
        corpus_index.append({
            "song_sha16": song_sha16,
            "name_hint": name,
            "rating_band": band,
            "midi_path": str(mid_rel),
            "midi_sha256": _sha256_file(mid_path),
            "section_wav_path": str(wav_rel),
            "section_wav_sha256": _sha256_file(wav_path),
            "tpb": tpb,
            "midi_bpm": bpm,
        })

        # v3-shape rule rows
        for stem in STEM_ORDER:
            notes = per_stem[stem]
            ti = per_stem_ti[stem]
            for fn in (_harmonic_rule, _rhythmic_rule, _melodic_rule, _form_rule):
                r = fn(song_sha16, stem, notes, tpb, ti)
                if r is not None:
                    all_rule_rows.append(r)
        arr = _arrangement_rule(song_sha16, per_stem, tpb)
        if arr is not None:
            all_rule_rows.append(arr)

        # Model A structured summary
        pc_all = [0] * 12
        all_notes = []
        for stem in ("bass", "guitar", "piano", "other"):
            for _, _, p, _ in per_stem[stem]:
                pc_all[p % 12] += 1
            all_notes.extend(per_stem[stem])
        all_notes.sort()
        key = _key_estimate(pc_all)
        chord_trans = _chord_transition_matrix(all_notes, tpb)
        grooves = {stem: _groove_template_16th(per_stem[stem], tpb)
                   for stem in STEM_ORDER}
        registers = {stem: _register_profile(per_stem[stem])
                     for stem in STEM_ORDER}
        end_tick = 0
        for stem in STEM_ORDER:
            if per_stem[stem]:
                end_tick = max(end_tick, per_stem[stem][-1][1])
        n_bars = int(max(1, end_tick // (tpb * 4)))
        per_song_stat[song_sha16] = {
            "song_sha16": song_sha16,
            "name_hint": name,
            "rating_band": band,
            "midi_bpm": bpm,
            "key_estimate": key,
            "chord_transition_matrix": chord_trans,
            "grooves_16th": grooves,
            "register_profile": registers,
            "n_bars": n_bars,
            "note_counts_by_stem": {s: len(per_stem[s]) for s in STEM_ORDER},
        }

        # Model B: per instrument CA + VOMM
        per_inst_seq = {}
        for stem in STEM_ORDER:
            bars = _binary_bar_grid(per_stem[stem], tpb)
            if not bars:
                per_inst_seq[stem] = {"n_bars": 0, "insufficient_data": True}
                continue
            ca = _fit_ca_rules_1d(bars, radius=1)
            # seed bar = the first bar of the corpus for this instrument
            seed = bars[0]
            gen = _generate_ca(seed, ca, n_steps=8, radius=1)
            vomm = _fit_vomm(bars, order=2)
            # sanity: CA retained unless clearly failing (degenerate output)
            ca_retained = not (
                gen.get("degenerate_all_off", False)
                or gen.get("degenerate_all_on", False)
                or (isinstance(ca.get("training_accuracy"), float)
                    and ca["training_accuracy"] < 0.5)
            )
            per_inst_seq[stem] = {
                "n_bars": len(bars),
                "ca_fit": ca,
                "ca_generation_smoke_8_steps": gen,
                "vomm_fit": vomm,
                "ca_retained": ca_retained,
                "retention_rationale": (
                    "not-degenerate + train-acc>=0.5" if ca_retained
                    else "degenerate output OR train-acc<0.5"
                ),
            }
        per_song_seq[song_sha16] = {
            "song_sha16": song_sha16,
            "per_instrument": per_inst_seq,
        }

        # audio descriptors
        audio_rows.append(_audio_descriptors_for_song(song_sha16, wav_path))

    # canonical ordering of rule rows
    all_rule_rows.sort(key=lambda r: (r["rule_type"], r["rule_id"], r["event_id"]))

    # aggregate per-band statistics for Model A
    band_agg: dict[str, dict] = {}
    for row in per_song_stat.values():
        b = row["rating_band"]
        band_agg.setdefault(b, {"songs": [], "midi_bpm_values": [],
                                "note_counts_by_stem": {s: [] for s in STEM_ORDER}})
        band_agg[b]["songs"].append(row["song_sha16"])
        band_agg[b]["midi_bpm_values"].append(row["midi_bpm"])
        for s in STEM_ORDER:
            band_agg[b]["note_counts_by_stem"][s].append(row["note_counts_by_stem"][s])
    for b, agg in band_agg.items():
        agg["songs"].sort()
        bpms = agg["midi_bpm_values"]
        agg["midi_bpm_mean"] = round(sum(bpms) / len(bpms), 3)
        for s in STEM_ORDER:
            nc = agg["note_counts_by_stem"][s]
            agg["note_counts_by_stem"][s + "_mean"] = round(sum(nc) / len(nc), 3)

    # emit rules_artifact.jsonl
    art_path = out_dir / "rules_artifact.jsonl"
    with art_path.open("w", encoding="ascii") as f:
        for r in all_rule_rows:
            f.write(_canonical_json(r) + "\n")
    art_sha = _sha256_file(art_path)
    (out_dir / "rules_artifact.sha256").write_text(art_sha + "\n")

    # emit statistical_model.json (Model A)
    stat_model = {
        "schema_v": 1,
        "extractor_version": EXTRACTOR_VERSION,
        "env_pin_sha256": CANONICAL_ENV_PIN_SHA,
        "per_song": {k: per_song_stat[k] for k in sorted(per_song_stat)},
        "per_band_aggregate": {b: band_agg[b] for b in sorted(band_agg)},
        "ts": EXTRACT_TS_ISO,
    }
    stat_path = out_dir / "statistical_model.json"
    stat_path.write_text(_canonical_json(stat_model), encoding="ascii")
    stat_sha = _sha256_file(stat_path)

    # emit sequence_model.json (Model B)
    seq_model = {
        "schema_v": 1,
        "extractor_version": EXTRACTOR_VERSION,
        "env_pin_sha256": CANONICAL_ENV_PIN_SHA,
        "model_b_notes": (
            "CA-first per operator direction 2026-09-03; VOMM order-2 "
            "included as sanity/comparison. Retention rule: CA retained "
            "unless CA clearly fails (degenerate output or train-acc<0.5). "
            "Both models remain available to the generator."
        ),
        "per_song": {k: per_song_seq[k] for k in sorted(per_song_seq)},
        "ts": EXTRACT_TS_ISO,
    }
    seq_path = out_dir / "sequence_model.json"
    seq_path.write_text(_canonical_json(seq_model), encoding="ascii")
    seq_sha = _sha256_file(seq_path)

    # emit audio_descriptors.jsonl
    audio_rows.sort(key=lambda r: r["song_sha16"])
    audio_path = out_dir / "audio_descriptors.jsonl"
    with audio_path.open("w", encoding="ascii") as f:
        for r in audio_rows:
            f.write(_canonical_json(r) + "\n")
    audio_sha = _sha256_file(audio_path)

    # emit env_pin
    env_pin = {
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "SOURCE_DATE_EPOCH": os.environ.get("SOURCE_DATE_EPOCH"),
        "TZ": os.environ.get("TZ"),
        "LC_ALL": os.environ.get("LC_ALL"),
        "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", "1"),
        "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS", "1"),
        "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS", "1"),
    }
    env_json = _canonical_json(env_pin)
    env_sha = hashlib.sha256(env_json.encode("ascii")).hexdigest()
    (out_dir / "env_pin.json").write_text(env_json, encoding="ascii")

    n_rules_by_type = {
        t: sum(1 for r in all_rule_rows if r["rule_type"] == t)
        for t in RULE_TYPES
    }

    # write ca_retention summary honestly (Model B sanity)
    retention_summary = {}
    for song_sha16, s in per_song_seq.items():
        for stem, inst in s["per_instrument"].items():
            key = f"{song_sha16}:{stem}"
            retention_summary[key] = {
                "ca_retained": inst.get("ca_retained"),
                "n_bars": inst.get("n_bars"),
                "training_accuracy": (inst.get("ca_fit") or {}).get("training_accuracy"),
                "vomm_order2_accuracy": (
                    (inst.get("vomm_fit") or {}).get("accuracy_by_order", {}) or {}
                ).get("2"),
            }
    retention_path = out_dir / "ca_retention_summary.json"
    retention_path.write_text(_canonical_json(retention_summary), encoding="ascii")

    # manifest
    manifest = {
        "schema_v": 1,
        "milestone_id": "M-V4-RULES-1",
        "extractor_version": EXTRACTOR_VERSION,
        "env_pin_sha256_from_extractor": env_sha,
        "canonical_env_pin_sha256_expected": CANONICAL_ENV_PIN_SHA,
        "env_pin_matches_canonical": env_sha == CANONICAL_ENV_PIN_SHA,
        "corpus": corpus_index,
        "artifacts": {
            "rules_artifact.jsonl": {"sha256": art_sha,
                                     "n_rules": len(all_rule_rows),
                                     "n_rules_by_type": n_rules_by_type},
            "statistical_model.json": {"sha256": stat_sha},
            "sequence_model.json": {"sha256": seq_sha},
            "audio_descriptors.jsonl": {"sha256": audio_sha},
            "ca_retention_summary.json": {"sha256": _sha256_file(retention_path)},
            "env_pin.json": {"sha256": env_sha},
        },
        "ts": EXTRACT_TS_ISO,
    }
    manifest_json = _canonical_json(manifest)
    (out_dir / "manifest.json").write_text(manifest_json, encoding="ascii")
    manifest_sha = hashlib.sha256(manifest_json.encode("ascii")).hexdigest()

    return {
        "rules_artifact_sha256": art_sha,
        "statistical_model_sha256": stat_sha,
        "sequence_model_sha256": seq_sha,
        "audio_descriptors_sha256": audio_sha,
        "manifest_sha256": manifest_sha,
        "env_pin_sha256": env_sha,
        "env_pin_matches_canonical": env_sha == CANONICAL_ENV_PIN_SHA,
        "n_rules": len(all_rule_rows),
        "n_rules_by_type": n_rules_by_type,
        "n_songs": len(CORPUS),
    }


def extract_rules_v4(corpus_manifest=None, out_dir=None, *,
                     env_pin_sha256=CANONICAL_ENV_PIN_SHA):
    """Legacy scaffold entry retained for backward compatibility."""
    if out_dir is None:
        raise ValueError("out_dir required")
    return extract(Path("."), Path(out_dir))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args()
    result = extract(args.repo_root.resolve(), args.out_dir.resolve())
    sys.stdout.write(_canonical_json(result) + "\n")


if __name__ == "__main__":
    _assert_env()
    main()
