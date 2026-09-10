#!/usr/bin/python3
"""c87 P3 — F3 comping-rhythm statistics from corpus guitar + piano + other stems (data-existence only).

created: 2026-09-10T01:49:00Z
cycle: 87
harness_cycle: 131
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F3-comping-statistics-c87

Inputs (READ-ONLY): the n=23 `gate.used` list of data/v5/rules/eligible_c86.json; per song
data/v5/corpus/<sha16>/{canonical_v5c_reindexed|canonical_v5_reindexed}/{guitar,piano,other}.reindexed.json
(same lossless preference tuple as harmony_v5.py / groove_v5_v2.py: a dir is eligible iff it carries reindex_manifest.json).
`--tempo-overrides` exactly as harmony_v5.load_tempo_overrides: an overridden song MUST have been served from
canonical_v5c_reindexed/ (TempoOverrideDirError otherwise) and its bpm is the override.

Grid (copied, not invented): seconds -> ticks as scripts/v3_spine/midi_from_json_events._seconds_to_ticks
(tick = max(0, int(round(sec * bpm / 60 * 480)))); 16th = 120 ticks; slot = int(round(tick / 120)); bar = slot // 16;
pos = slot % 16 (groove_v5_v2.py). No drum phase alignment (offset 0 = groove_v5_v2 `stats_unaligned_offset0`): the
comping stems carry no kick/snare to align on.

Statistics per stem class (guitar / piano / other) and pooled: onset density per bar (note starts per bar and onset
groups per bar over bars with >= 1 onset), 16-slot onset histogram (normalised), inter-onset-interval histogram in
16ths (1..16, clipped), mean chord size per onset group (starts within 30 ms of the group's first start), sustain ratio
(mean paired note duration in beats), n_songs / n_bars contributing. Per-song n_bars_with_onsets per stem + pooled.

Pre-registered verdict (data/v5/rules/comping_prereg_c87.json, written BEFORE this script ran; NOT retuned):
  COMPING_NON_DEGENERATE iff >= 8 songs contribute >= 16 bars with onsets to the pooled guitar+piano+other set
                         AND the pooled 16-slot histogram's max slot mass < 0.5;
  COMPING_DEGENERATE otherwise.
After writing the output the script asserts prereg mtime < output mtime and records prereg_sha256.

Discipline: /usr/bin/python3 guard; no PRNG; no wall-clock in the output; sort_keys JSON; floats rounded to 6 dp;
READ-ONLY inputs; nothing here feeds a generator this cycle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
         "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
         "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
CYCLE = 87
AGENT = "worker"
RUN_ID = "run-2026-09-06T000000Z"
PPQ = 480
TICKS_16TH = PPQ // 4
SLOTS = 16
IOI_MAX = 16
CHORD_WINDOW_S = 0.030
COMPING_STEMS = ("guitar", "piano", "other")
MIDI_DIR_PREFERENCE = ("canonical_v5c_reindexed", "canonical_v5_reindexed")
TEMPO_OVERRIDE_DIR = MIDI_DIR_PREFERENCE[0]
THRESHOLDS = {"min_songs": 8, "min_bars_with_onsets_per_song": 16, "pooled_max_slot_mass_lt": 0.5, "chord_window_ms": 30}
ENUM = ("COMPING_NON_DEGENERATE", "COMPING_DEGENERATE")


class MissingReindexError(RuntimeError):
    """Raised when an eligible song has no lossless re-indexed canonical dir (c81 rule)."""


class TempoOverrideDirError(RuntimeError):
    """Raised when a --tempo-overrides song was not served from canonical_v5c_reindexed/ (c86 rule)."""


class PreregMtimeError(RuntimeError):
    """Raised when the prereg file's mtime is not strictly earlier than the output's mtime."""


def sha_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_tempo_overrides(path) -> dict:
    """c86: sha16 -> bpm; None/absent -> {} (identical to harmony_v5.load_tempo_overrides)."""
    if not path:
        return {}
    return {str(k): float(v) for k, v in json.loads(Path(path).read_text()).items()}


def seconds_to_ticks(t_seconds: float, bpm: float) -> int:
    """scripts/v3_spine/midi_from_json_events._seconds_to_ticks (c4 serializer), copied verbatim."""
    beats = float(t_seconds) * float(bpm) / 60.0
    return max(0, int(round(beats * PPQ)))


def slot_of(t_seconds: float, bpm: float) -> int:
    """groove_v5_v2.onsets_slots convention: slot = round(tick / 120)."""
    return int(round(seconds_to_ticks(t_seconds, bpm) / TICKS_16TH))


def r6(x):
    return None if x is None else round(float(x), 6)


def read_stem_events(path: Path) -> list[dict]:
    """(start_time, pitch, index, end_time|None) from a *.reindexed.json (end linked by start_event_index)."""
    if not path.exists():
        return []
    ev = json.loads(path.read_text())
    starts = [e for e in ev if e.get("type") == "start"]
    end_by_sei: dict[int, float] = {}
    for e in ev:
        if e.get("type") == "end":
            sei = int(e["start_event_index"])
            et = float(e["end_time"])
            if sei not in end_by_sei or et < end_by_sei[sei]:  # reindexed guarantees <= 1 end per start; keep earliest if not
                end_by_sei[sei] = et
    out = []
    for s in starts:
        out.append({"start": float(s["start_time"]), "pitch": int(s["pitch"]), "index": int(s["index"]),
                    "end": end_by_sei.get(int(s["index"]))})
    out.sort(key=lambda n: (n["start"], n["pitch"], n["index"]))
    return out


def onset_groups(notes: list[dict]) -> list[dict]:
    """Collapse starts within CHORD_WINDOW_S of the group's FIRST start into one onset group (sorted input)."""
    groups: list[dict] = []
    for n in notes:
        if groups and n["start"] - groups[-1]["start"] <= CHORD_WINDOW_S:
            groups[-1]["size"] += 1
        else:
            groups.append({"start": n["start"], "size": 1})
    return groups


def analyse_stem(notes: list[dict], bpm: float) -> dict:
    groups = onset_groups(notes)
    slot_counts = [0] * SLOTS
    ioi_counts = [0] * IOI_MAX  # index k-1 = IOI k (clipped 1..16)
    bars: dict[int, dict[str, int]] = {}
    prev_slot = None
    chord_sizes = []
    for g in groups:
        slot = slot_of(g["start"], bpm)
        b = bars.setdefault(slot // SLOTS, {"onsets": 0, "notes": 0})
        b["onsets"] += 1
        b["notes"] += g["size"]
        slot_counts[slot % SLOTS] += 1
        chord_sizes.append(g["size"])
        if prev_slot is not None:
            ioi = min(IOI_MAX, max(1, slot - prev_slot))
            ioi_counts[ioi - 1] += 1
        prev_slot = slot
    durs = [(n["end"] - n["start"]) * bpm / 60.0 for n in notes if n["end"] is not None and n["end"] > n["start"]]
    return {"n_starts": len(notes), "n_onset_groups": len(groups), "n_unpaired_starts": sum(1 for n in notes if n["end"] is None),
            "n_bars_with_onsets": len(bars), "bars": sorted(bars),
            "slot_counts": slot_counts, "ioi_counts": ioi_counts, "chord_size_sum": int(sum(chord_sizes)),
            "duration_beats_sum": float(sum(durs)), "n_paired_durations": len(durs),
            "onsets_per_bar": r6(len(groups) / len(bars)) if bars else None,
            "notes_per_bar": r6(len(notes) / len(bars)) if bars else None,
            "chord_size_mean": r6(sum(chord_sizes) / len(groups)) if groups else None,
            "sustain_ratio": r6(sum(durs) / len(durs)) if durs else None}


def analyse_song(sha16: str, corpus: Path, tempo_overrides: dict) -> dict:
    d = corpus / sha16
    mid_dir = None
    for sub in MIDI_DIR_PREFERENCE:
        if (d / sub / "reindex_manifest.json").exists():
            mid_dir = d / sub
            break
    if mid_dir is None:
        raise MissingReindexError(f"MISSING_REINDEX: {sha16} has no {'/'.join(MIDI_DIR_PREFERENCE)} directory")
    tm = json.loads((d / "transcription_manifest.json").read_text())
    bpm = float(tm["bpm_v5"])
    override = None
    if sha16 in tempo_overrides:
        if mid_dir.name != TEMPO_OVERRIDE_DIR:
            raise TempoOverrideDirError(f"TEMPO_OVERRIDE_DIR: {sha16} has a --tempo-overrides entry but events came from {mid_dir} "
                                        f"(expected {d / TEMPO_OVERRIDE_DIR}); run scripts/v5/recanonicalize_tempo_v5.py")
        override = {"bpm_v5_manifest": bpm, "bpm_override": float(tempo_overrides[sha16]), "midi_dir_asserted": TEMPO_OVERRIDE_DIR}
        bpm = float(tempo_overrides[sha16])
    per_stem = {}
    pooled_bars: set[int] = set()
    for stem in COMPING_STEMS:
        st = analyse_stem(read_stem_events(mid_dir / f"{stem}.reindexed.json"), bpm)
        pooled_bars |= set(st["bars"])
        per_stem[stem] = st
    rec = {"sha16": sha16, "title": tm.get("title"), "bpm_used": r6(bpm), "midi_dir": str(mid_dir),
           "per_stem": per_stem, "n_bars_with_onsets_pooled": len(pooled_bars)}
    if override is not None:
        rec["tempo_override_c86"] = override
    return rec


def _hist(counts: list[int]) -> tuple[list[float], int]:
    n = sum(counts)
    return ([r6(c / n) for c in counts] if n else [0.0] * len(counts)), n


def pool(per_song: dict, stems: tuple) -> dict:
    slot = [0] * SLOTS
    ioi = [0] * IOI_MAX
    n_starts = n_groups = n_bars = chord_sum = n_durs = 0
    dur_sum = 0.0
    n_songs = 0
    bars_by_song = []
    for sha16 in sorted(per_song):
        song_bars: set[int] = set()
        contributed = False
        for stem in stems:
            st = per_song[sha16]["per_stem"][stem]
            if st["n_onset_groups"] == 0:
                continue
            contributed = True
            song_bars |= set(st["bars"])
            slot = [a + b for a, b in zip(slot, st["slot_counts"])]
            ioi = [a + b for a, b in zip(ioi, st["ioi_counts"])]
            n_starts += st["n_starts"]
            n_groups += st["n_onset_groups"]
            chord_sum += st["chord_size_sum"]
            dur_sum += st["duration_beats_sum"]
            n_durs += st["n_paired_durations"]
        if contributed:
            n_songs += 1
            n_bars += len(song_bars)
            bars_by_song.append(len(song_bars))
    slot_p, _ = _hist(slot)
    ioi_p, n_ioi = _hist(ioi)
    max_mass = max(slot_p) if n_groups else None
    return {"stems": list(stems), "n_songs": n_songs, "n_bars": n_bars, "n_starts": n_starts, "n_onset_groups": n_groups,
            "onset_density_notes_per_bar": r6(n_starts / n_bars) if n_bars else None,
            "onset_density_onsets_per_bar": r6(n_groups / n_bars) if n_bars else None,
            "slot16_counts": slot, "slot16_histogram": slot_p, "slot16_max_mass": max_mass,
            "slot16_argmax": int(max(range(SLOTS), key=lambda i: (slot[i], -i))) if n_groups else None,
            "ioi16_counts": ioi, "ioi16_histogram": ioi_p, "n_ioi": n_ioi,
            "chord_size_mean": r6(chord_sum / n_groups) if n_groups else None,
            "sustain_ratio": r6(dur_sum / n_durs) if n_durs else None, "n_paired_durations": n_durs,
            "bars_with_onsets_by_contributing_song": bars_by_song}


def main() -> int:
    ap = argparse.ArgumentParser(description="c87 F3 comping-rhythm statistics (guitar + piano + other)")
    ap.add_argument("--eligible-from", default="data/v5/rules/eligible_c86.json")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--tempo-overrides", default=None, help="JSON {sha16: bpm} (data/v5/corpus/tempo_overrides_c86.json)")
    ap.add_argument("--out", default="data/v5/rules/comping_v5.json")
    ap.add_argument("--prereg", default="data/v5/rules/comping_prereg_c87.json")
    ap.add_argument("--cycle", type=int, default=CYCLE)
    args = ap.parse_args()
    os.chdir(_WS)
    corpus = Path(args.corpus_dir)
    prereg_p = Path(args.prereg)
    if not prereg_p.exists():
        raise SystemExit(f"PREREG_MISSING: {prereg_p} must be written before this script runs")
    prereg = json.loads(prereg_p.read_text())
    if prereg.get("thresholds") != THRESHOLDS or sorted(prereg.get("enum", {})) != sorted(ENUM):
        raise SystemExit(f"PREREG_MISMATCH: thresholds/enum in {prereg_p} differ from the script's constants")
    tempo_overrides = load_tempo_overrides(args.tempo_overrides)
    elig = json.loads(Path(args.eligible_from).read_text())
    used = list(elig["gate"]["used"])
    per_song = {}
    for s in used:
        r = analyse_song(s, corpus, tempo_overrides)
        per_song[s] = r
        print(f"{s} {str(r['title'])[:24]:24s} bpm={r['bpm_used']} dir={Path(r['midi_dir']).name:24s} "
              + " ".join(f"{st}={r['per_stem'][st]['n_onset_groups']}/{r['per_stem'][st]['n_bars_with_onsets']}b" for st in COMPING_STEMS)
              + f" pooled_bars={r['n_bars_with_onsets_pooled']}")
    stats = {stem: pool(per_song, (stem,)) for stem in COMPING_STEMS}
    stats["pooled"] = pool(per_song, COMPING_STEMS)
    pooled = stats["pooled"]
    songs_ge = sorted(s for s in per_song if per_song[s]["n_bars_with_onsets_pooled"] >= THRESHOLDS["min_bars_with_onsets_per_song"])
    max_mass = pooled["slot16_max_mass"]
    non_deg = (len(songs_ge) >= THRESHOLDS["min_songs"] and max_mass is not None and max_mass < THRESHOLDS["pooled_max_slot_mass_lt"])
    verdict = {"enum": ENUM[0] if non_deg else ENUM[1], "enum_values": list(ENUM), "thresholds": THRESHOLDS,
               "n_songs_with_ge_16_pooled_bars": len(songs_ge), "songs_with_ge_16_pooled_bars": songs_ge,
               "songs_ok": len(songs_ge) >= THRESHOLDS["min_songs"],
               "pooled_max_slot_mass": max_mass, "pooled_argmax_slot": pooled["slot16_argmax"],
               "slot_mass_ok": bool(max_mass is not None and max_mass < THRESHOLDS["pooled_max_slot_mass_lt"]),
               "rule": "COMPING_NON_DEGENERATE iff n_songs_with_ge_16_pooled_bars >= 8 AND pooled_max_slot_mass < 0.5"}
    out = {"schema_version": 1, "cycle": args.cycle, "agent": AGENT, "run_id": RUN_ID, "env_pin_sha256": ENV_PIN_SHA256,
           "script_sha256": sha_file(Path(__file__)), "prereg_path": str(prereg_p), "prereg_sha256": sha_file(prereg_p),
           "eligible": {"path": args.eligible_from, "sha256": sha_file(Path(args.eligible_from)), "n_used": len(used), "used": used,
                        "late_landed_deferred": list(elig["gate"].get("late_landed_deferred", []))},
           "corpus_dir": args.corpus_dir, "stems": list(COMPING_STEMS),
           "grid": {"ppq": PPQ, "ticks_per_16th": TICKS_16TH, "slots_per_bar": SLOTS, "phase_offset": 0,
                    "seconds_to_ticks": "max(0, int(round(sec * bpm / 60 * 480))) (scripts/v3_spine/midi_from_json_events._seconds_to_ticks)",
                    "slot": "int(round(tick / 120)); bar = slot // 16; pos = slot % 16 (groove_v5_v2.py)",
                    "chord_window_s": CHORD_WINDOW_S, "ioi_clip": [1, IOI_MAX], "onset_group": "starts within 30 ms of the group's first start",
                    "sustain_ratio": "mean paired note duration in beats (unpaired starts excluded)",
                    "bars_with_onsets": "bar indices holding >= 1 onset group; pooled per song = union over stems",
                    "midi_dir_preference": list(MIDI_DIR_PREFERENCE)},
           "per_song": {s: {k: (v if k != "per_stem" else {st: {kk: vv for kk, vv in sv.items() if kk != "bars"} for st, sv in v.items()})
                            for k, v in r.items()} for s, r in per_song.items()},
           "stats": stats, "verdict": verdict,
           "notes": ["data-existence only; NOT fed to any generator this cycle",
                     "no drum phase alignment (offset 0); comping stems carry no kick/snare",
                     "instrument field ignored: every start event in the stem file counts"]}
    if args.tempo_overrides:
        out["tempo_overrides_c86"] = {"path": args.tempo_overrides, "sha256": sha_file(Path(args.tempo_overrides)),
                                      "overrides": {k: r6(v) for k, v in sorted(tempo_overrides.items())},
                                      "applied_to": [s for s in used if s in tempo_overrides], "midi_dir_asserted": TEMPO_OVERRIDE_DIR}
    out_p = Path(args.out)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    if not prereg_p.stat().st_mtime < out_p.stat().st_mtime:
        raise PreregMtimeError(f"PREREG_AFTER_OUTPUT: {prereg_p} mtime {prereg_p.stat().st_mtime} >= {out_p} mtime {out_p.stat().st_mtime}")
    print(f"VERDICT {verdict['enum']}: songs>=16 pooled bars {len(songs_ge)}/{len(used)} (min {THRESHOLDS['min_songs']}); "
          f"pooled max slot mass {max_mass} at slot {pooled['slot16_argmax']} (< {THRESHOLDS['pooled_max_slot_mass_lt']})")
    for k in COMPING_STEMS + ("pooled",):
        st = stats[k]
        print(f"  {k:7s} songs={st['n_songs']} bars={st['n_bars']} onsets={st['n_onset_groups']} notes/bar={st['onset_density_notes_per_bar']} "
              f"onsets/bar={st['onset_density_onsets_per_bar']} chord={st['chord_size_mean']} sustain={st['sustain_ratio']} maxslot={st['slot16_max_mass']}")
    print(f"wrote {out_p} sha256={sha_file(out_p)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
