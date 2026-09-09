#!/usr/bin/python3
"""c86 F2 Route 1 — per-note velocity from stem audio (score-and-delete) + corpus velocity profiles.

created: 2026-09-09T23:10:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F2-bass-melody-dynamics

Pre-registered in data/v5/gen/f2_prereg_c86.json (blocks velocity_extraction_route_1 + velocity_profiles). Per focus song:
  1. df guard (READ-ONLY _sweep_hygiene_c27._disk_used_pct_user < 90 %) -> ffmpeg decode of the corpus mp3 into a tempdir;
  2. htdemucs_6s separation in a SUBPROCESS started under the driver's pinned env (recreate_v3.sub_env; /usr/bin/python3) so
     torch/BLAS see the pins at load time; the READ-ONLY recreate_v3._run_htdemucs_once is the only separation code path;
     fresh stem SHAs are compared to the c79 stage-cache SHAs (cross-cycle x2) and, for --x2-song, the separation is run a
     second time in-cycle (fresh tempdir) and compared (in-cycle x2);
  3. per stem (drums, bass, guitar, other, piano, vocals): 50 ms RMS (dB) centred on every MuScriptor start_time
     (data/v5/corpus/<sha16>/muscriptor_full/<stem>.json), truncated at the file ends; per-(song, stem) midrank
     normalization p5 -> 40 / p95 -> 110 (linear in rank fraction, int, clipped [1,127]); degenerate guard (p95-p5 < 1e-6 dB
     -> constant 80 + flag); R1 spread diagnostic;
  4. data/v5/corpus/<sha16>/velocity_v5/velocities.json + sibling canonical_v5_velocity/<stem>.mid (the reindexed events
     of canonical_v5_reindexed/<stem>.reindexed.json with velocities, serialized by scripts/v5/midi_from_json_events_v5.py
     at the song's grid tempo). canonical_v5_reindexed/*.mid are NEVER written (tested sidecar anchors) — disclosed reading
     of the operator's "write velocities into canonical_v5_reindexed";
  5. tempdir deleted (stems never persist).
Then data/v5/rules/velocity_profiles_v5.json: per-stem x GM-class x 16th-slot quantile ladders (drums), bass split by
kick-coincidence, melody by phrase position, keys by slot; R1/R2 diagnostics; Route-2 ladders for any stem failing R1.
Grid tempo: bpm_v5 from the transcription manifest, except the operator-adopted F4 tempos for PD / Disco A
(122.197271 / 120.272335; data/v5/corpus/tempo_overrides_c86.json when present, else the built-in constants — same numbers).
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; nothing under data/v4/** written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)
_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scripts.v3_spine import recreate_v3 as _v3  # noqa: E402  READ-ONLY (sub_env, sha)
from scripts.sound_match._sweep_hygiene_c27 import _disk_used_pct_user  # noqa: E402  READ-ONLY
from scripts.v5.midi_from_json_events_v5 import serialize as serialize_v5  # noqa: E402

ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
FOCUS = ["252eb21ce7df7328", "31a164f845f8e27e", "51e433ade2a845e1", "88d247468cb6d49f", "cdd2717e52820ff6"]
STEMS = ["drums", "bass", "guitar", "other", "piano", "vocals"]
ADOPTED_F4 = {"88d247468cb6d49f": 122.197271, "cdd2717e52820ff6": 120.272335}
WINDOW_S = 0.050
V_LO, V_HI, P_LO, P_HI = 40.0, 110.0, 0.05, 0.95
DEGENERATE_DB = 1e-6
R1_MIN_SPREAD_DB = 6.0
QUANTS = [0, 10, 25, 50, 75, 90, 100]
DRUM_CLASSES = {"kick": (35, 36), "snare": (37, 38, 39, 40), "hat": (42, 44, 46)}
KICK_COINCIDENT_S = 0.030
PHRASE_GAP_BEATS = 2.0
DF_ABORT = 90.0
ROUTE2 = {"drums": {"kick": {"on": 110, "off": 85}, "snare": {"on": 110, "off": 85}, "hat": {"even": 90, "odd": 55}},
          "bass": {"coincident": 100, "other": 80}, "melody": {"peak": 105, "other": 85}, "keys": {"all": 90}}

_SEP_WORKER = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from scripts.v3_spine import recreate_v3 as v3
shas = v3._run_htdemucs_once(Path(sys.argv[2]), Path(sys.argv[3]))
Path(sys.argv[4]).write_text(json.dumps(shas, sort_keys=True))
"""


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def rms_db_at(y: np.ndarray, sr: int, t: float) -> float:
    n = int(round(WINDOW_S * sr))
    c = int(round(t * sr))
    i0, i1 = max(0, c - n // 2), min(len(y), c - n // 2 + n)
    if i1 <= i0:
        return -180.0
    seg = y[i0:i1].astype(np.float64)
    return float(20.0 * np.log10(np.sqrt(np.mean(seg * seg)) + 1e-9))


def midrank_velocities(vals: list) -> tuple[list, dict]:
    """p5 -> 40, p95 -> 110, linear in midrank fraction; ties (identical windows) share a velocity."""
    n = len(vals)
    a = np.asarray(vals, dtype=np.float64)
    if n == 0:
        return [], {"n": 0, "p5_db": None, "p95_db": None, "spread_db": None, "degenerate": None}
    p5, p95 = float(np.percentile(a, 5)), float(np.percentile(a, 95))
    spread = p95 - p5
    if spread < DEGENERATE_DB:
        return [80] * n, {"n": n, "p5_db": round(p5, 6), "p95_db": round(p95, 6), "spread_db": round(spread, 6), "degenerate": True}
    order = np.argsort(a, kind="stable")
    ranks = np.empty(n, dtype=np.float64)
    s = a[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and s[j + 1] == s[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 0.5  # midrank, 0.5-based
        i = j + 1
    rf = ranks / n
    v = V_LO + (V_HI - V_LO) * (rf - P_LO) / (P_HI - P_LO)
    v = np.clip(np.round(v), 1, 127).astype(int)
    return [int(x) for x in v], {"n": n, "p5_db": round(p5, 6), "p95_db": round(p95, 6), "spread_db": round(spread, 6), "degenerate": False}


def grid_tempo(sha16: str, corpus: Path) -> tuple[float, str]:
    ov = corpus / "tempo_overrides_c86.json"
    if ov.exists():
        d = json.loads(ov.read_text())
        if sha16 in d:
            return float(d[sha16]), "tempo_overrides_c86.json (operator-adopted F4)"
    if sha16 in ADOPTED_F4:
        return ADOPTED_F4[sha16], "built-in operator-adopted F4 constant (same value as tempo_overrides_c86.json)"
    tm = json.loads((corpus / sha16 / "transcription_manifest.json").read_text())
    return float(tm["bpm_v5"]), "transcription_manifest.bpm_v5"


def separate(full_wav: Path, out_dir: Path) -> tuple[dict, float]:
    t0 = time.time()
    res = out_dir.parent / f"{out_dir.name}.shas.json"
    subprocess.run(["/usr/bin/python3", "-c", _SEP_WORKER, str(_WS), str(full_wav), str(out_dir), str(res)],
                   check=True, env=_v3.sub_env(), cwd=str(_WS))
    return json.loads(res.read_text()), round(time.time() - t0, 1)


def cached_stem_shas(sha16: str, corpus: Path) -> dict:
    ms = sorted((corpus / sha16 / "stage_cache/v5_htdemucs_6s").glob("*/stage_manifest.json"))
    return json.loads(ms[0].read_text())["result"]["stems"] if ms else {}


def process_song(sha16: str, song: dict, corpus: Path, x2: bool) -> dict:
    df0 = _disk_used_pct_user(str(_WS))
    if df0 >= DF_ABORT:
        raise SystemExit(f"DF_ABORT {df0:.2f} % >= {DF_ABORT}")
    bpm, bpm_src = grid_tempo(sha16, corpus)
    rec = {"sha16": sha16, "title": song["title"], "audio_path": song["audio_path"], "df_pct_at_entry": round(df0, 2),
           "grid_bpm": bpm, "grid_bpm_source": bpm_src, "stems": {}}
    with tempfile.TemporaryDirectory(prefix=f"vel_v5_{sha16[:8]}_") as td:
        td = Path(td)
        full = td / "full.wav"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", song["audio_path"], "-ac", "2", "-ar", "44100", str(full)],
                       check=True, env=_v3.sub_env())
        rec["full_wav_sha256"] = _sha(full)
        shas, wall = separate(full, td / "stems")
        rec["separation"] = {"wall_s": wall, "fresh_stem_sha256": shas, "c79_cached_stem_sha256": cached_stem_shas(sha16, corpus)}
        rec["separation"]["cross_cycle_equal"] = {k: shas.get(k) == rec["separation"]["c79_cached_stem_sha256"].get(k) for k in STEMS}
        rec["separation"]["cross_cycle_x2_holds"] = all(rec["separation"]["cross_cycle_equal"].values())
        if x2:
            shas2, wall2 = separate(full, td / "stems2")
            rec["separation"]["in_cycle_run2"] = {"wall_s": wall2, "stem_sha256": shas2, "equal": {k: shas.get(k) == shas2.get(k) for k in STEMS}}
            rec["separation"]["in_cycle_x2_holds"] = all(rec["separation"]["in_cycle_run2"]["equal"].values())
            shutil.rmtree(td / "stems2", ignore_errors=True)
        rec["df_pct_peak"] = round(_disk_used_pct_user(str(_WS)), 2)
        vel_dir = corpus / sha16 / "velocity_v5"
        vel_dir.mkdir(exist_ok=True)
        out = {}
        for stem in STEMS:
            y, sr = sf.read(str(td / "stems" / f"{stem}.wav"), dtype="float32", always_2d=True)
            y = y.mean(axis=1)
            ev = json.loads((corpus / sha16 / "muscriptor_full" / f"{stem}.json").read_text())
            starts = [e for e in ev if e.get("type") == "start"]
            rms = [rms_db_at(y, sr, float(e["start_time"])) for e in starts]
            vels, st = midrank_velocities(rms)
            st["r1_spread_ge_6db"] = (st["spread_db"] is not None) and st["spread_db"] >= R1_MIN_SPREAD_DB
            st["sr"] = int(sr)
            st["stem_duration_s"] = round(len(y) / sr, 3)
            out[stem] = [[int(e["index"]), float(e["start_time"]), round(r, 4), int(v)] for e, r, v in zip(starts, rms, vels)]
            rec["stems"][stem] = st
        # --- sibling MIDI with velocities (canonical_v5_reindexed/ NEVER written) ---
        vmid_dir = corpus / sha16 / "canonical_v5_velocity"
        vmid_dir.mkdir(exist_ok=True)
        midi_sha = {}
        for stem in STEMS:
            vmap = {(row[0], round(row[1], 6)): row[3] for row in out[stem]}
            rj = corpus / sha16 / "canonical_v5_reindexed" / f"{stem}.reindexed.json"
            events = json.loads(rj.read_text())
            n_hit = 0
            for e in events:
                if e.get("type") == "start":
                    k = (int(e.get("original_index", e["index"])), round(float(e["start_time"]), 6))
                    if k in vmap:
                        e["velocity"] = int(vmap[k])
                        n_hit += 1
            vj = vmid_dir / f"{stem}.velocity.json"
            vj.write_text(json.dumps(events, sort_keys=True, separators=(",", ":")))
            serialize_v5(str(vj), str(vmid_dir / f"{stem}.mid"), bpm, (4, 4))
            midi_sha[stem] = {"mid": _sha(vmid_dir / f"{stem}.mid"), "json": _sha(vj), "n_starts": sum(1 for e in events if e.get("type") == "start"), "n_velocity_assigned": n_hit}
        payload = {"schema_version": 1, "cycle": 86, "agent": "worker", "run_id": "run-2026-09-06T000000Z",
                   "milestone": "M-V5-GEN-1/F2-bass-melody-dynamics", "route": "ROUTE_1_STEM_AUDIO", "sha16": sha16, "title": song["title"],
                   "grid_bpm": bpm, "grid_bpm_source": bpm_src, "window_s": WINDOW_S, "mapping": "midrank fraction: p5->40, p95->110, int, clip [1,127]; ties share a velocity",
                   "degenerate_guard_db": DEGENERATE_DB, "columns": ["index(chunk-local MuScriptor)", "start_time_s", "rms_db", "velocity"],
                   "env_pin_sha256": ENV_PIN_SHA256, "separation": rec["separation"], "full_wav_sha256": rec["full_wav_sha256"],
                   "stem_stats": rec["stems"], "sibling_midi": {"dir": os.path.relpath(str(vmid_dir.resolve()), str(_WS)), "tempo_bpm": bpm, "sha256": midi_sha,
                                                                  "note": "canonical_v5_reindexed/*.mid untouched (tested anchors); velocities live in this sibling dir"},
                   "stems_deleted_after_measuring": True, "velocities": out}
        (vel_dir / "velocities.json").write_text(json.dumps(payload, sort_keys=True, indent=1) + "\n")
        rec["velocities_json_sha256"] = _sha(vel_dir / "velocities.json")
        rec["sibling_midi_sha256"] = midi_sha
    rec["stems_deleted"] = True
    return rec


# ------------------------------------------------------------------------------------------------------- profiles ----
def ladder(vals: list) -> dict:
    a = np.asarray(vals, dtype=np.float64)
    if a.size == 0:
        return {"n": 0, "mean": None, "std": None, "quantiles": None}
    return {"n": int(a.size), "mean": round(float(a.mean()), 4), "std": round(float(a.std()), 4),
            "quantiles": [round(float(np.percentile(a, q)), 2) for q in QUANTS]}


def sample_velocity(lad: dict, u: float) -> int:
    """SHA-256 inverse-CDF at generation time: linear interpolation of the empirical quantile ladder at u*100."""
    q = lad.get("quantiles") if lad else None
    if not q:
        return 100
    return int(max(1, min(127, round(float(np.interp(u * 100.0, QUANTS, q))))))


def slot_of(t: float, bpm: float, offset: int) -> int:
    return (int(round(t * bpm / 60.0 * 4.0)) - offset) % 16


def build_profiles(recs: dict, corpus: Path, groove: dict) -> dict:
    pooled = {"drums": {c: {s: [] for s in range(16)} for c in DRUM_CLASSES}, "bass": {"coincident": {s: [] for s in range(16)}, "other": {s: [] for s in range(16)}},
              "melody": {"first": [], "peak": [], "last": [], "other": []}, "keys": {s: [] for s in range(16)}}
    per_song_fig = {}
    r1 = {}
    for sha16 in FOCUS:
        v = json.loads((corpus / sha16 / "velocity_v5/velocities.json").read_text())
        bpm = float(v["grid_bpm"])
        offset = int(groove.get("per_song", {}).get(sha16, {}).get("phase", {}).get("offset", 0))
        drums = json.loads((corpus / sha16 / "muscriptor_full/drums.json").read_text())
        pitch_of = {(int(e["index"]), round(float(e["start_time"]), 6)): int(e["pitch"]) for e in drums if e.get("type") == "start"}
        kick_times = sorted(float(r[1]) for r in v["velocities"]["drums"] if pitch_of.get((r[0], round(r[1], 6))) in DRUM_CLASSES["kick"])
        kt = np.asarray(kick_times) if kick_times else np.zeros(0)
        fig = {"drums": {c: {s: [] for s in range(16)} for c in DRUM_CLASSES}, "bass": {s: [] for s in range(16)}, "keys": {s: [] for s in range(16)}, "melody": {s: [] for s in range(16)}, "offset": offset, "bpm": bpm}
        for r in v["velocities"]["drums"]:
            p = pitch_of.get((r[0], round(r[1], 6)))
            for c, ps in DRUM_CLASSES.items():
                if p in ps:
                    s = slot_of(r[1], bpm, offset)
                    pooled["drums"][c][s].append(r[3]); fig["drums"][c][s].append(r[3])
        for r in v["velocities"]["bass"]:
            s = slot_of(r[1], bpm, offset)
            coin = bool(kt.size) and bool(np.min(np.abs(kt - r[1])) <= KICK_COINCIDENT_S)
            pooled["bass"]["coincident" if coin else "other"][s].append(r[3]); fig["bass"][s].append(r[3])
        # melody = vocals + other synth_lead; keys = guitar + piano + other synth_pad
        other = json.loads((corpus / sha16 / "muscriptor_full/other.json").read_text())
        inst_of = {(int(e["index"]), round(float(e["start_time"]), 6)): e.get("instrument") for e in other if e.get("type") == "start"}
        voc = json.loads((corpus / sha16 / "muscriptor_full/vocals.json").read_text())
        vpitch = {(int(e["index"]), round(float(e["start_time"]), 6)): int(e["pitch"]) for e in voc if e.get("type") == "start"}
        opitch = {(int(e["index"]), round(float(e["start_time"]), 6)): int(e["pitch"]) for e in other if e.get("type") == "start"}
        mel = [(r[1], vpitch.get((r[0], round(r[1], 6)), 60), r[3]) for r in v["velocities"]["vocals"]]
        mel += [(r[1], opitch.get((r[0], round(r[1], 6)), 60), r[3]) for r in v["velocities"]["other"] if inst_of.get((r[0], round(r[1], 6))) == "synth_lead"]
        mel.sort()
        beat = 60.0 / bpm
        phrases, cur = [], []
        for t, p, vel in mel:
            if cur and t - cur[-1][0] >= PHRASE_GAP_BEATS * beat:
                phrases.append(cur); cur = []
            cur.append((t, p, vel))
        if cur:
            phrases.append(cur)
        for ph in phrases:
            peak_i = max(range(len(ph)), key=lambda i: (ph[i][1], -i))
            for i, (t, p, vel) in enumerate(ph):
                pos = "first" if i == 0 else ("last" if i == len(ph) - 1 else ("peak" if i == peak_i else "other"))
                pooled["melody"][pos].append(vel); fig["melody"][slot_of(t, bpm, offset)].append(vel)
        for stem in ("guitar", "piano"):
            for r in v["velocities"][stem]:
                s = slot_of(r[1], bpm, offset); pooled["keys"][s].append(r[3]); fig["keys"][s].append(r[3])
        for r in v["velocities"]["other"]:
            if inst_of.get((r[0], round(r[1], 6))) == "synth_pad":
                s = slot_of(r[1], bpm, offset); pooled["keys"][s].append(r[3]); fig["keys"][s].append(r[3])
        per_song_fig[sha16] = {k: ({c: {str(s): (round(float(np.mean(x)), 2) if x else None) for s, x in d.items()} for c, d in val.items()} if k == "drums"
                                   else ({str(s): (round(float(np.mean(x)), 2) if x else None) for s, x in val.items()} if isinstance(val, dict) else val))
                               for k, val in fig.items()}
        r1[sha16] = {stem: v["stem_stats"][stem] for stem in STEMS}
    prof = {"drums": {c: {str(s): ladder(pooled["drums"][c][s]) for s in range(16)} for c in DRUM_CLASSES},
            "bass": {k: {str(s): ladder(pooled["bass"][k][s]) for s in range(16)} for k in ("coincident", "other")},
            "melody": {k: ladder(pooled["melody"][k]) for k in ("first", "peak", "last", "other")},
            "keys": {str(s): ladder(pooled["keys"][s]) for s in range(16)}}
    # R1: drums + bass spread >= 6 dB on >= 4/5 songs
    r1_pass = {stem: sum(1 for s in FOCUS if r1[s][stem]["r1_spread_ge_6db"]) for stem in STEMS}
    r1_verdict = {stem: r1_pass[stem] >= 4 for stem in ("drums", "bass")}
    route2_stems = [stem for stem in ("drums", "bass") if not r1_verdict[stem]]
    # R2 structure diagnostics (pooled drums)
    slot_mean = {}
    for s in range(16):
        xs = [x for c in DRUM_CLASSES for x in pooled["drums"][c][s]]
        slot_mean[s] = float(np.mean(xs)) if xs else None
    back = [slot_mean[s] for s in (4, 12) if slot_mean[s] is not None]
    odd = [slot_mean[s] for s in range(1, 16, 2) if slot_mean[s] is not None]
    hat_even = [x for s in range(0, 16, 2) for x in pooled["drums"]["hat"][s]]
    hat_odd = [x for s in range(1, 16, 2) for x in pooled["drums"]["hat"][s]]
    bass_c = [x for s in range(16) for x in pooled["bass"]["coincident"][s]]
    bass_o = [x for s in range(16) for x in pooled["bass"]["other"][s]]
    means = [m for m in slot_mean.values() if m is not None]
    r2 = {"drums_backbeat_mean_slots_4_12": round(float(np.mean(back)), 3) if back else None,
          "drums_odd_slot_mean": round(float(np.mean(odd)), 3) if odd else None,
          "backbeat_minus_odd": round(float(np.mean(back) - np.mean(odd)), 3) if back and odd else None,
          "backbeat_ge_plus_10": bool(back and odd and (np.mean(back) - np.mean(odd)) >= 10.0),
          "hat_even_mean": round(float(np.mean(hat_even)), 3) if hat_even else None, "hat_odd_mean": round(float(np.mean(hat_odd)), 3) if hat_odd else None,
          "hat_odd_lower_than_even": bool(hat_even and hat_odd and np.mean(hat_odd) < np.mean(hat_even)),
          "bass_kick_coincident_mean": round(float(np.mean(bass_c)), 3) if bass_c else None, "bass_non_coincident_mean": round(float(np.mean(bass_o)), 3) if bass_o else None,
          "bass_coincident_gt_non": bool(bass_c and bass_o and np.mean(bass_c) > np.mean(bass_o)),
          "drums_slot_profile_std": round(float(np.std(means)), 3) if means else None,
          "structureless_std_lt_5": bool(means and np.std(means) < 5.0)}
    return {"schema_version": 1, "cycle": 86, "agent": "worker", "run_id": "run-2026-09-06T000000Z", "milestone": "M-V5-GEN-1/F2-bass-melody-dynamics",
            "route": "ROUTE_1_STEM_AUDIO", "prereg_path": "data/v5/gen/f2_prereg_c86.json", "prereg_sha256": _sha(_WS / "data/v5/gen/f2_prereg_c86.json"),
            "env_pin_sha256": ENV_PIN_SHA256, "songs": FOCUS, "grid": {"slots_per_bar": 16, "slot": "round(t*bpm/60*4) - phase_offset mod 16",
            "phase_offset_source": "groove_v5_v2_full.json per_song.phase.offset (0 when the song is absent: PD/Disco A)"},
            "quantile_levels": QUANTS, "sampling": "sample_velocity(ladder, u): np.interp(u*100, levels, quantiles), u = SHA-256 uniform",
            "drum_classes": {k: list(v) for k, v in DRUM_CLASSES.items()}, "kick_coincident_s": KICK_COINCIDENT_S, "phrase_gap_beats": PHRASE_GAP_BEATS,
            "profiles": prof, "per_song_slot_means": per_song_fig, "per_song_stem_stats": r1,
            "R1": {"min_spread_db": R1_MIN_SPREAD_DB, "songs_passing_per_stem": r1_pass, "drums_bass_pass_ge_4_of_5": r1_verdict, "route_2_fallback_stems": route2_stems},
            "R2": r2, "route_2_ladders_if_needed": ROUTE2, "per_song_separation": {s: json.loads((corpus / s / "velocity_v5/velocities.json").read_text())["separation"] for s in FOCUS}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="c86 F2 Route-1 velocity extraction + profiles")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--songs", nargs="*", default=None)
    ap.add_argument("--x2-song", default="252eb21ce7df7328", help="song whose separation is run twice in-cycle (fresh tempdir)")
    ap.add_argument("--profiles-out", default="data/v5/rules/velocity_profiles_v5.json")
    ap.add_argument("--profiles-only", action="store_true", help="skip extraction; rebuild the profiles from the on-disk velocities.json files")
    ap.add_argument("--groove", default="data/v5/rules/groove_v5_v2_full.json")
    args = ap.parse_args(argv)
    os.chdir(_WS)
    corpus = Path(args.corpus_dir)
    man = json.loads(Path("data/v5/corpus/corpus_manifest.json").read_text())
    songs = {s["sha16"]: s for s in man["songs"]}
    log = {"schema_version": 1, "cycle": 86, "agent": "worker", "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "per_song": {}}
    if not args.profiles_only:
        for s in (args.songs or FOCUS):
            rec = process_song(s, songs[s], corpus, x2=(s == args.x2_song))
            log["per_song"][s] = rec
            sep = rec["separation"]
            print(f"{s} {rec['title'][:24]:24s} sep {sep['wall_s']}s cross-cycle x2 {sep['cross_cycle_x2_holds']}"
                  + (f" in-cycle x2 {sep['in_cycle_x2_holds']}" if "in_cycle_x2_holds" in sep else "") + f" df peak {rec['df_pct_peak']}%; "
                  + "; ".join(f"{st} n={v['n']} spread={v['spread_db']}dB" for st, v in rec["stems"].items()))
            Path("data/v5/logs/velocity_v5_c86.progress.json").write_text(json.dumps(log, sort_keys=True, indent=1) + "\n")
    groove = json.loads(Path(args.groove).read_text())
    prof = build_profiles(log["per_song"], corpus, groove)
    Path(args.profiles_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.profiles_out).write_text(json.dumps(prof, sort_keys=True, indent=1) + "\n")
    print(f"profiles -> {args.profiles_out}; R1 {prof['R1']}; R2 {prof['R2']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
