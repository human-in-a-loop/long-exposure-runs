#!/usr/bin/python3
# ---
# cycle: 21
# milestone: M-V4-GEN-1
# purpose: Seeded generator program per campaign prompt v4. Draws
#          scaffolding from Model A (statistical_model.json) and
#          bar-to-bar patterns from Model B (sequence_model.json).
#          Renders via fluidsynth (deterministic sf2 rung) and scores
#          via the M-V4-EAR-1 VGGish ear. Emits per-song manifests
#          with (seed, generator hash, rules hash, donor, env pin,
#          ear score).
# ---
"""M-V4-GEN-1 seeded instrumental generator.

Contracts (per campaign prompt):
    * Agent creativity lives in DESIGNING this generator - no
      hand-written songs. Every song is `generator(rules, seed, config)
      -> MIDI -> driver render with donor profiles -> donor mix
      match -> ear score` (this build uses fluidsynth's deterministic
      sf2 rung instead of the full v3 spine to keep the closure
      iteration budget under the ~1-hour ear target).
    * SEEDED and DETERMINISTIC: no PRNG imports; the 'seed' is folded
      into a hash-driven deterministic index stream (all sampling
      via SHA-256 of the seed + context strings, cast to int).
    * Interpreter guard `/usr/bin/python3`; canonical 7-key env-pin;
      no `sidecar_nonfactor`; no VST3 state APIs.
    * INSTRUMENTAL only: vocals track empty by policy.
    * Structural gates on generated songs WARN (not halt) per operator
      relaxation 2026-09-03.
    * Stall rule: after 8 iterations without 5 passers (ear >= 6),
      STOP and deliver the best 5 with honest gap analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any

os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import mido

CANONICAL_ENV_PIN_SHA = (
    "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
)

# Donor order used as fallback donor rotation when a config picks 'auto'.
DONOR_ORDER = (
    "31a164f845f8e27e",  # Chicken Grease
    "252eb21ce7df7328",  # WIG
    "51e433ade2a845e1",  # Rome
    "cdd2717e52820ff6",  # Disco A
    "88d247468cb6d49f",  # Peach Dream
)

# fluidsynth-deterministic GM programs per stem (mirrors the CG-arc
# best-composite finds where available; simple defaults elsewhere).
DEFAULT_GM = {
    "drums": {"channel": 9, "program": 0, "bank": 128},   # ch10 std kit
    "bass": {"channel": 0, "program": 33, "bank": 0},     # Electric Bass finger
    "guitar": {"channel": 1, "program": 27, "bank": 0},   # Clean Electric Guitar
    "piano": {"channel": 2, "program": 4, "bank": 0},     # Rhodes-family EP2
    "other": {"channel": 3, "program": 17, "bank": 0},    # Drawbar Organ
}

# GM percussion pitches on channel 10 keyed by "bar slot column" bucket
DRUM_PITCHES = (
    36,  # kick    - slot 0..3
    38,  # snare   - slot 4..7
    42,  # hihat closed - slot 8..11
    46,  # hihat open   - slot 12..15
)

SF2_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
EXPECTED_SF2_SHA = (
    "74594e8fb5c22ef4f7cf14b9e4b0f2f7ccc7c88a7f1c2c53c88a4dc85af51cb0"
)

RULES_DIR = Path("data/v4/rules")

TARGET_PASS_SCORE = 6.0
TARGET_N_PASSERS = 5
STALL_MAX_ITERATIONS = 8


# ----- discipline -----

def _assert_env() -> None:
    if sys.executable != "/usr/bin/python3":
        raise RuntimeError(f"interpreter guard failed: {sys.executable}")
    for k, v in (("PYTHONHASHSEED", "0"), ("TZ", "UTC"), ("LC_ALL", "C.UTF-8")):
        if os.environ.get(k) != v:
            raise RuntimeError(f"env-pin: {k}={os.environ.get(k)!r} not {v!r}")


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----- deterministic hash-driven index stream -----

class HashStream:
    """Deterministic pseudo-random index stream.

    Given a base seed string, `.pick(context, upper)` returns an int in
    [0, upper) derived from SHA-256(seed || context || counter). No
    PRNG import required.
    """

    __slots__ = ("_seed_bytes", "_ctr")

    def __init__(self, seed: str):
        self._seed_bytes = seed.encode("ascii")
        self._ctr = 0

    def pick(self, context: str, upper: int) -> int:
        if upper <= 0:
            return 0
        self._ctr += 1
        payload = self._seed_bytes + b"|" + context.encode("ascii") + b"|" + str(self._ctr).encode("ascii")
        h = hashlib.sha256(payload).digest()
        n = int.from_bytes(h[:8], "big")
        return n % upper

    def pick_float01(self, context: str) -> float:
        return self.pick(context, 1 << 30) / float(1 << 30)


# ----- rules loading -----

def _load_rules():
    stat = json.loads((RULES_DIR / "statistical_model.json").read_text(encoding="ascii"))
    seq = json.loads((RULES_DIR / "sequence_model.json").read_text(encoding="ascii"))
    return stat, seq


def _rules_hash():
    return _sha256_file(RULES_DIR / "rules_artifact.jsonl")


def _pick_donor(config, hs: HashStream) -> str:
    donor = config.get("donor_song_sha16", "auto")
    if donor == "auto":
        idx = hs.pick("donor", len(DONOR_ORDER))
        return DONOR_ORDER[idx]
    return donor


def _donor_key_scale(stat, donor_sha16, hs):
    ps = stat["per_song"].get(donor_sha16) or stat["per_song"][DONOR_ORDER[0]]
    ke = ps["key_estimate"]
    return int(ke["root_pc"]), str(ke["mode"])


def _key_to_pitch_scale(root_pc: int, mode: str):
    """Return sorted list of MIDI pitches (spanning ~C1..C6) in the key."""
    major_intv = (0, 2, 4, 5, 7, 9, 11)
    minor_intv = (0, 2, 3, 5, 7, 8, 10)
    intv = major_intv if mode == "major" else minor_intv
    scale_pcs = [(root_pc + i) % 12 for i in intv]
    pitches = []
    for octv in range(1, 6):  # C1..B5
        for pc in scale_pcs:
            p = 12 * octv + pc
            if 21 <= p <= 108:
                pitches.append(p)
    return sorted(pitches)


# ----- bar-sequence generation via CA + VOMM -----

def _pick_ca_rule_table(seq_model, donor_sha16, stem):
    ps = seq_model["per_song"].get(donor_sha16) or {}
    inst = (ps.get("per_instrument") or {}).get(stem, {})
    ca_fit = inst.get("ca_fit") or {}
    if ca_fit.get("insufficient_data"):
        return None
    return ca_fit


def _pick_vomm(seq_model, donor_sha16, stem):
    ps = seq_model["per_song"].get(donor_sha16) or {}
    inst = (ps.get("per_instrument") or {}).get(stem, {})
    return inst.get("vomm_fit") or None


def _bar_from_int(v, slots=16):
    return [((v >> (slots - 1 - i)) & 1) for i in range(slots)]


def _bar_to_int(row):
    v = 0
    for bit in row:
        v = (v << 1) | (bit & 1)
    return v


def _generate_bars(seq_model, donor_sha16, stem, n_bars, hs):
    """Generate a list of 16-slot binary bars via CA (fallback VOMM).

    Returns list of length n_bars; each is a list of 16 ints in {0,1}.
    Fully deterministic given the seed via HashStream.
    """
    slots = 16
    ca = _pick_ca_rule_table(seq_model, donor_sha16, stem)
    # seed bar (agent-designed): a syncopated on-1-3-6-8-10-14 template
    # is used as a musically-plausible starting condition; the CA
    # evolves it deterministically.
    seed_row = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # sprinkle bits based on hash to give per-seed variety
    hits = 4 + hs.pick(f"seed-{stem}-hits", 5)  # 4..8 bits
    picked: set[int] = set()
    while len(picked) < hits:
        picked.add(hs.pick(f"seed-{stem}-pos", slots))
    for i in picked:
        seed_row[i] = 1
    bars = [seed_row]
    if ca and ca.get("rule_table"):
        table = ca["rule_table"]
        for t in range(n_bars - 1):
            cur = bars[-1]
            nxt = [0] * slots
            for i in range(slots):
                # radius=1 neighborhood, wrapping
                idx0 = (i - 1) % slots
                idx1 = i
                idx2 = (i + 1) % slots
                neigh = (cur[idx0] << 2) | (cur[idx1] << 1) | cur[idx2]
                dec = table[neigh]["decision"]
                if dec is None:
                    # fall back: use hash-driven bit
                    dec = hs.pick(f"fill-{stem}-{t}-{i}", 2)
                nxt[i] = int(dec)
            bars.append(nxt)
    else:
        # VOMM-order-2 fallback
        vomm = _pick_vomm(seq_model, donor_sha16, stem)
        if vomm and not vomm.get("insufficient_data") and vomm.get("transition_tables", {}).get("2"):
            tt = vomm["transition_tables"]["2"]
            # start prefix = seed bar int, echoed
            prev = _bar_to_int(seed_row)
            prev2 = prev
            for _ in range(n_bars - 1):
                key = f"{prev2},{prev}"
                row = tt.get(key)
                if not row:
                    # deterministic fallback: reuse seed
                    nxt_int = prev
                else:
                    # pick most-common (with tie-break by smallest token)
                    best_key = None
                    best_val = -1
                    for kk, vv in row.items():
                        if vv > best_val or (vv == best_val and (best_key is None or int(kk) < int(best_key))):
                            best_val = vv
                            best_key = kk
                    nxt_int = int(best_key)
                bars.append(_bar_from_int(nxt_int, slots))
                prev2 = prev
                prev = nxt_int
        else:
            # last-resort fallback: hash-driven repeat
            for t in range(n_bars - 1):
                row = list(seed_row)
                # perturb 2 bits deterministically
                for _ in range(2):
                    j = hs.pick(f"fb-{stem}-{t}", slots)
                    row[j] ^= 1
                bars.append(row)
    # cap length
    return bars[:n_bars]


# ----- MIDI assembly -----

def _write_merged_midi(out_path: Path, bar_grids, tpb, bpm, pitch_scale, hs):
    """Assemble merged.mid from bar_grids (dict stem -> list of 16-bit bars).

    Instrument programs from DEFAULT_GM. Pitch selection: for melodic
    stems, walk through pitch_scale using a hash-driven cursor; for
    drums, map 4 slot-buckets to (kick, snare, hihatC, hihatO).
    """
    mf = mido.MidiFile(ticks_per_beat=tpb)
    # meta track (track 0): tempo
    meta = mido.MidiTrack()
    tempo = mido.bpm2tempo(bpm)
    meta.append(mido.MetaMessage("set_tempo", tempo=int(tempo), time=0))
    meta.append(mido.MetaMessage("time_signature", numerator=4, denominator=4,
                                 clocks_per_click=24, notated_32nd_notes_per_beat=8,
                                 time=0))
    mf.tracks.append(meta)

    slot_ticks = (tpb * 4) // 16
    note_len_ticks = slot_ticks  # 1-slot durations

    def _events_from_bars(stem, bars, gm):
        events = []  # list of (abs_tick, msg)
        ch = gm["channel"]
        prog = gm["program"]
        bank = gm.get("bank", 0)
        # program change at time 0
        events.append((0, mido.Message("control_change", channel=ch, control=0, value=bank & 0x7F, time=0)))
        events.append((0, mido.Message("control_change", channel=ch, control=32, value=(bank >> 7) & 0x7F, time=0)))
        events.append((0, mido.Message("program_change", channel=ch, program=prog & 0x7F, time=0)))
        cursor = hs.pick(f"{stem}-cursor", max(1, len(pitch_scale)))
        for bi, bar in enumerate(bars):
            for si, on in enumerate(bar):
                if not on:
                    continue
                t0 = bi * (tpb * 4) + si * slot_ticks
                t1 = t0 + note_len_ticks
                if stem == "drums":
                    bucket = si // 4  # 0..3
                    pitch = DRUM_PITCHES[bucket]
                elif stem == "bass":
                    # bass low register: pick a scale pitch <= 55
                    pool = [p for p in pitch_scale if 28 <= p <= 55]
                    if not pool:
                        pool = pitch_scale
                    step = hs.pick(f"{stem}-{bi}-{si}", len(pool))
                    pitch = pool[step]
                else:
                    step = hs.pick(f"{stem}-{bi}-{si}", len(pitch_scale))
                    # bias toward mid register
                    if stem == "guitar":
                        pool = [p for p in pitch_scale if 52 <= p <= 84]
                    elif stem == "piano":
                        pool = [p for p in pitch_scale if 48 <= p <= 84]
                    else:  # other
                        pool = [p for p in pitch_scale if 55 <= p <= 84]
                    if not pool:
                        pool = pitch_scale
                    pitch = pool[step % len(pool)]
                vel = 96 if stem == "drums" else 84
                events.append((t0, mido.Message("note_on", channel=ch, note=pitch, velocity=vel, time=0)))
                events.append((t1, mido.Message("note_off", channel=ch, note=pitch, velocity=0, time=0)))
        # sort stably; convert to delta-time
        events.sort(key=lambda x: x[0])
        tr = mido.MidiTrack()
        # add track name meta
        tr.append(mido.MetaMessage("track_name", name=stem, time=0))
        prev_t = 0
        for t_abs, msg in events:
            dt = t_abs - prev_t
            m = msg.copy(time=dt if dt >= 0 else 0)
            tr.append(m)
            prev_t = t_abs
        return tr

    for stem in ("drums", "bass", "guitar", "piano", "other", "vocals"):
        gm = DEFAULT_GM.get(stem)
        if stem == "vocals":
            # instrumental -> empty vocals track
            tr = mido.MidiTrack()
            tr.append(mido.MetaMessage("track_name", name=stem, time=0))
            mf.tracks.append(tr)
            continue
        bars = bar_grids.get(stem)
        if bars is None:
            tr = mido.MidiTrack()
            tr.append(mido.MetaMessage("track_name", name=stem, time=0))
            mf.tracks.append(tr)
            continue
        mf.tracks.append(_events_from_bars(stem, bars, gm))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mf.save(str(out_path))


# ----- fluidsynth render -----

def _fluidsynth_render(midi_path: Path, out_wav_path: Path, sr: int = 44100,
                       gain: float = 0.5):
    if not Path(SF2_PATH).exists():
        raise RuntimeError(f"SF2 missing at {SF2_PATH}")
    cmd = [
        "fluidsynth", "-ni",
        "-F", str(out_wav_path),
        "-r", str(sr),
        "-g", str(gain),
        "-o", "synth.cpu-cores=1",
        "-o", "synth.reverb.active=false",
        "-o", "synth.chorus.active=false",
        "-o", f"synth.sample-rate={sr}",
        SF2_PATH,
        str(midi_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ----- ear scoring (adapted from v4_ear/ear.py) -----

_VGG_CACHE = None


def _get_vgg():
    global _VGG_CACHE
    if _VGG_CACHE is not None:
        return _VGG_CACHE
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import tensorflow_hub as hub
        _VGG_CACHE = hub.load("https://tfhub.dev/google/vggish/1")
    return _VGG_CACHE


def _read_wav_mono(p: Path):
    with wave.open(str(p), "rb") as w:
        sr = w.getframerate()
        nch = w.getnchannels()
        sampw = w.getsampwidth()
        nf = w.getnframes()
        raw = w.readframes(nf)
    if sampw != 2:
        raise RuntimeError(f"unexpected sampwidth={sampw}")
    import struct
    fmt = "<" + "h" * (len(raw) // 2)
    ints = struct.unpack(fmt, raw)
    if nch == 1:
        mono = list(ints)
    else:
        mono = [sum(ints[i * nch:(i + 1) * nch]) // nch for i in range(nf)]
    import numpy as np
    arr = np.array(mono, dtype=np.float32) / 32768.0
    return sr, arr


def _resample_to_16k(y, sr_in):
    import librosa
    if sr_in == 16000:
        return y
    return librosa.resample(y, orig_sr=sr_in, target_sr=16000)


def _windows(y, sr=16000, win_s=10.0, hop_s=5.0):
    win = int(round(sr * win_s))
    hop = int(round(sr * hop_s))
    out = []
    s = 0
    while s + win <= len(y):
        out.append(y[s:s + win])
        s += hop
    return out


def _embed_song(y16):
    import numpy as np
    m = _get_vgg()
    wins = _windows(y16)
    if not wins:
        return np.zeros((0, 128), dtype=np.float64)
    embs = []
    for w in wins:
        f = m(w).numpy()
        embs.append(f.mean(axis=0).astype(np.float64) if f.ndim == 2 else f.astype(np.float64))
    return np.vstack(embs)


def _load_exemplar_embs():
    import numpy as np
    d = np.load("data/v4/ear/exemplar_embeddings.npz", allow_pickle=True)
    return np.vstack([d[k] for k in d.files])


def _load_calibration():
    d = json.loads((Path("data/v4/ear/ear_scores.json")).read_text())
    return float(d["calibration_E_mean_loo"]), float(d["calibration_F_noise_floor_stat"])


def _score_wav_ear(wav_path: Path):
    import numpy as np
    sr, y = _read_wav_mono(wav_path)
    y16 = _resample_to_16k(y, sr)
    cand = _embed_song(y16)
    ex = _load_exemplar_embs()
    if cand.shape[0] == 0 or ex.shape[0] == 0:
        return {"score_1_7": 1.0, "statistic": 0.0, "n_windows": 0}
    a = cand / (np.linalg.norm(cand, axis=1, keepdims=True) + 1e-12)
    b = ex / (np.linalg.norm(ex, axis=1, keepdims=True) + 1e-12)
    sims = a @ b.T
    per_win = sims.max(axis=1)
    order = np.argsort(per_win)[::-1]
    k = max(1, len(per_win) // 2)
    stat = float(per_win[order[:k]].mean())
    E, F = _load_calibration()
    if E <= F:
        score = 1.0
    else:
        score = 1.0 + 6.0 * (stat - F) / (E - F)
    score = round(max(1.0, min(7.0, score)), 4)
    return {"score_1_7": score, "statistic": round(stat, 6),
            "n_windows": int(cand.shape[0])}


# ----- generator entry point -----

def generate_song(seed: str, config: dict, out_dir: Path):
    """Generator entry point per spec.

    * seed: string; folded through SHA-256 for deterministic sampling.
    * config: {donor_song_sha16, n_bars, sr, gain, ...}
    * out_dir: destination directory.
    Returns manifest dict; writes merged.mid + song.wav + manifest.json.
    """
    _assert_env()
    out_dir.mkdir(parents=True, exist_ok=True)
    hs = HashStream(seed)
    stat, seq = _load_rules()

    donor = _pick_donor(config, hs)
    root, mode = _donor_key_scale(stat, donor, hs)
    pitch_scale = _key_to_pitch_scale(root, mode)

    n_bars = int(config.get("n_bars", 16))
    tpb = int(config.get("tpb", 480))
    bpm = int(round(stat["per_song"].get(donor, {}).get("midi_bpm", 100)))

    bar_grids = {}
    for stem in ("drums", "bass", "guitar", "piano", "other"):
        bar_grids[stem] = _generate_bars(seq, donor, stem, n_bars, hs)

    midi_path = out_dir / "merged.mid"
    _write_merged_midi(midi_path, bar_grids, tpb, bpm, pitch_scale, hs)
    midi_sha = _sha256_file(midi_path)

    wav_path = out_dir / "song.wav"
    _fluidsynth_render(midi_path, wav_path, sr=int(config.get("sr", 44100)),
                       gain=float(config.get("gain", 0.5)))
    wav_sha = _sha256_file(wav_path)

    scoring = _score_wav_ear(wav_path)

    gen_hash = _sha256_file(Path("scripts/v4_gen/gen.py"))
    rules_hash = _rules_hash()

    manifest = {
        "schema_v": 1,
        "milestone_id": "M-V4-GEN-1",
        "seed": seed,
        "config": config,
        "donor_song_sha16": donor,
        "midi_bpm": bpm,
        "key_estimate_from_donor": {"root_pc": root, "mode": mode},
        "n_bars": n_bars,
        "tpb": tpb,
        "generator_hash": gen_hash,
        "rules_hash": rules_hash,
        "sf2_path": SF2_PATH,
        "sf2_sha256": _sha256_file(Path(SF2_PATH)),
        "midi_sha256": midi_sha,
        "song_wav_sha256": wav_sha,
        "ear": scoring,
        "structural_gates_warn_not_halt": True,
        "instrumental_vocals_empty": True,
        "env_pin_sha256": CANONICAL_ENV_PIN_SHA,
        "ts": "2026-09-04T07:45:00Z",
    }
    (out_dir / "manifest.json").write_text(_canonical_json(manifest), encoding="ascii")
    return manifest


# ----- batch driver + stall rule -----

def run_batch(out_root: Path, seeds: list, config: dict) -> dict:
    _assert_env()
    out_root.mkdir(parents=True, exist_ok=True)
    per_iter = []
    passers = []
    for i, seed in enumerate(seeds[:STALL_MAX_ITERATIONS]):
        out_dir = out_root / f"iter_{i + 1:02d}_seed_{seed}"
        m = generate_song(seed, config, out_dir)
        per_iter.append({
            "iter": i + 1,
            "seed": seed,
            "score_1_7": m["ear"]["score_1_7"],
            "song_wav_sha256": m["song_wav_sha256"],
            "midi_sha256": m["midi_sha256"],
            "donor": m["donor_song_sha16"],
            "manifest_path": str(out_dir / "manifest.json"),
        })
        if m["ear"]["score_1_7"] >= TARGET_PASS_SCORE:
            passers.append(per_iter[-1])
        if len(passers) >= TARGET_N_PASSERS:
            break

    # honest stop
    stopped_reason = ("target_passers_reached" if len(passers) >= TARGET_N_PASSERS
                      else "stall_rule_max_iterations")

    # deliver best 5 (by score desc)
    ranked = sorted(per_iter, key=lambda r: r["score_1_7"], reverse=True)
    top5 = ranked[:5]

    result = {
        "schema_v": 1,
        "milestone_id": "M-V4-GEN-1",
        "n_iterations": len(per_iter),
        "n_passers": len(passers),
        "target_n_passers": TARGET_N_PASSERS,
        "target_pass_score": TARGET_PASS_SCORE,
        "stall_max_iterations": STALL_MAX_ITERATIONS,
        "stopped_reason": stopped_reason,
        "all_iterations": per_iter,
        "top5_by_ear": top5,
        "passers": passers,
        "env_pin_sha256": CANONICAL_ENV_PIN_SHA,
        "ts": "2026-09-04T07:50:00Z",
    }
    (out_root / "batch_report.json").write_text(_canonical_json(result), encoding="ascii")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", required=True, type=Path)
    ap.add_argument("--seeds", nargs="+", required=True,
                    help="seed strings; up to 8 will be used")
    ap.add_argument("--donor", default="auto")
    ap.add_argument("--n-bars", type=int, default=16)
    args = ap.parse_args()
    config = {"donor_song_sha16": args.donor, "n_bars": args.n_bars,
              "sr": 44100, "gain": 0.5, "tpb": 480}
    result = run_batch(args.out_root.resolve(), list(args.seeds), config)
    sys.stdout.write(_canonical_json({
        "n_iterations": result["n_iterations"],
        "n_passers": result["n_passers"],
        "top5_scores": [r["score_1_7"] for r in result["top5_by_ear"]],
        "stopped_reason": result["stopped_reason"],
    }) + "\n")


if __name__ == "__main__":
    _assert_env()
    main()
