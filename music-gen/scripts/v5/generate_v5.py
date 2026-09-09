#!/usr/bin/python3
"""c84 P3 — groove-first v5 generator, iteration 1 (OPERATOR #6: drums+bass from the joint groove model -> chords from the
harmony chain on a fixed form plan -> keys/melody as chord tones on the grid; donor profiles + mix as v4).
c85 P1 (F1 LENGTH + FORM + ARRANGEMENT): additive `--form-plan <json>` (DEFAULT OFF — the iteration-1 path is byte-identical
in audio), `--cycle`, M4 (no groove-model copy into the iteration dir), F6 stall-history schema.
c86 (F2 BASS + MELODY + DYNAMICS, 2026-09-09T23:30:00Z, pre-registered in data/v5/gen/f2_prereg_c86.json): additive `--f2`
(DEFAULT OFF — the --form-plan path stays byte-identical to iteration 2) + `--velocity-mode {uniform,f2}` + `--rms-variance-test`.
With --f2: bass pitches from data/v5/rules/bass_pitch_v5.json (chord-conditioned interval classes, donor register), melody from
data/v5/rules/melody_vomm_v5.json (order-3 VOMM over scale-degree|IOI tokens, per section run so literal repeats reproduce, muted
per the F1 arrangement), velocities for ALL stems (drums per GM class x 16th slot, bass by kick-coincidence x slot, keys by slot,
melody by phrase position) drawn by SHA-256 inverse-CDF from data/v5/rules/velocity_profiles_v5.json (Route 1 stem-audio
profiles); MIDI via the sibling serializer scripts/v5/midi_from_json_events_v5.py (velocity field). `--velocity-mode uniform`
renders the same notes at velocity 100 everywhere (the exact null); `--rms-variance-test` renders that twin into a tempdir and
records the per-stem 50 ms frame-RMS variance ratio (>= 1.5 on every stem with notes = operator clause (c)). F2 enum in the
rollup: F2_LANDS iff velocities present 5/5 AND RMS test 5/5 AND replay x2 5/5; else F2_PARTIAL.

created: 2026-09-09T21:30:00Z
cycle: 84 (c85 additive extension 2026-09-09T22:10:00Z)
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/iteration-01-c84 (c85: M-V5-GEN-1/F1-form-arrangement)

Inputs (READ-ONLY): data/v5/rules/groove_v5_v2_full.json (c84 P2 model: kick8 marginal + snare16|kick8 + hat16|kick8,snare16 +
bass16|kick8, alpha-smoothed), data/v5/rules/harmony_markov_v5_full.json (c84 P1 chain: functional states "rel_root:quality",
segment-level change matrix + stationary distribution), data/v4/gen/donor_profile_map.json (5 donors, pinned sf2 profiles),
tempo: donor bpm_v5 (tempo-blocked donors use their frozen anchor_bpm from recanonicalization_blocked.json).
Per song (seed_str = f"gen_v5_song_{N}|donor={sha16}|seed={seed}"), all draws by SHA-256 inverse-CDF (no PRNG):
  1. form plan A A B A, 4 bars per section (16 bars); section A generated ONCE and repeated literally (forced repetition).
     c85 --form-plan: n_sections drawn from the corpus length distribution (8 bars each, 32..64 bars); labels from the
     corpus label Markov chain if R1 passed, else the pre-declared fixed template A A B A B C A A truncated to n_sections
     (data/v5/gen/form_prereg_c85.json); every label generated once and repeated literally; non-A labels obey the
     contrast rule (first chord root != A's dominant root, restricted to states with >= 8 segments; drum-density tercile
     != A's realized tercile via an 8-candidate deterministic filter); arrangement = intro (keys+melody muted; drums
     too when intro_density_quantile < 0.33), outro (melody muted, final bar held), breakdown (first non-A section in
     the middle half: drums muted for 4 bars), fills (last bar of every section: snare16+hat16 from the corpus boundary
     pool by SHA-256 inverse-CDF). Per-section CORE MIDI is serialized for the literal-repeat byte-equality claim.
  2. groove: per bar sample kick8 -> snare16|kick8 -> hat16|kick8,snare16 -> bass16|kick8 (scripts.v5.groove_v5_v2 row_for/draw).
  3. chords: one functional state per bar; first from the stationary distribution, then the segment-level (change-only) matrix
     (unseen rows -> uniform); 'N' = no chord (keys/melody rest; bass plays the tonic). Tonic = donor's KK key when the donor is
     in the chain, else SHA-256-derived (tempo-blocked donors PD / Disco A are not in the chain).
  4. bass: root (fifth on every 4th onset) at bass16 onsets, legato to the next onset; drums: kick 36 / snare 38 / hat 42;
     keys: chord tones sustained per bar (electric_piano, ch 2); melody: chord tones on the 8th grid with hash-gated rests.
  5. canonical MIDI via the READ-ONLY c4 serializer at the donor tempo; sf2 replay (READ-ONLY scripts.sound_match.replay):
     bass/drums via the donor's pinned profiles (CG drums: GM Standard Kit shim per c72), keys/melody via GM shims
     (program 4 Electric Piano 1 / program 11 Vibraphone — disclosed, not profiled); RMS-normalize (-18 dBFS bass/drums,
     -22 dBFS keys/melody, gain in [0.05, 4]); sum + 0.99 peak-limit; 16-bit PCM via stdlib wave (c72 writer).
  6. ab_mix.wav + ab_mix.manifest.json (+ ab_mix.replay_proof.json with --prove-replay: second full render into mkdtemp);
     per-track WAVs deleted after the mix (score-and-delete hygiene) unless --keep-per-track.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; nothing under data/v4/** written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile
import time
import wave
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scripts.v5 import groove_v5_v2 as G  # noqa: E402  READ-ONLY (row_for / draw / hash_uniform / bits)
from scripts.v5.harmony_v5 import QUALITIES  # noqa: E402  READ-ONLY template intervals
from scripts.v3_spine.midi_from_json_events import serialize as canonical_midi_serialize  # noqa: E402  READ-ONLY c4 serializer
from scripts.sound_match.replay import replay as sf2_replay  # noqa: E402  READ-ONLY
from scripts.v5.midi_from_json_events_v5 import serialize as serialize_v5  # noqa: E402  c86 F2 sibling serializer (velocity field)
from scripts.v5.velocity_v5 import sample_velocity, DRUM_CLASSES as VEL_DRUM_CLASSES  # noqa: E402  c86 F2 (ladder sampler)

ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
FORM_PLAN = ("A", "A", "B", "A")
BARS_PER_SECTION = 4
SLOTS = 16
KICK_PITCH, SNARE_PITCH, HAT_PITCH = 36, 38, 42
DRUM_HIT_S = 0.1
TARGET_RMS_DB = {"bass": -18.0, "drums": -18.0, "keys": -22.0, "melody": -22.0}
SHIMS = {"keys": {"program": 4, "name": "GM Electric Piano 1 (shim, not profiled)"},
         "melody": {"program": 11, "name": "GM Vibraphone (shim, not profiled)"},
         "drums_cg": {"program": 0, "name": "GM Standard Kit (c72 CG shim; CG drums are htdemucs OPT3, no pinned profile)"}}
MELODY_PLAY_P = 0.6
# c85 F1 constants (pre-registered in data/v5/gen/form_prereg_c85.json)
F1_BARS_PER_SECTION = 8
F1_MIN_SEGMENTS = 8
F1_N_CANDIDATES = 8
F1_INTRO_BASS_ONLY_Q = 0.33
F1_MIN_DURATION_S = 90.0
F1_MIN_BARS = 32
F1_MIN_LABELS = 3
F1_ENUM = ("FORM_PLAN_LANDS", "FORM_PLAN_PARTIAL", "FORM_PLAN_FAILS")
# c86 F2 constants (pre-registered in data/v5/gen/f2_prereg_c86.json)
F2_ENUM = ("F2_LANDS", "F2_PARTIAL", "F2_FAILS")
F2_MELODY_REGISTER = (67, 84)
F2_VOMM_ORDER = 3
F2_PHRASE_GAP_BEATS = 2.0
F2_RMS_FRAME_S = 0.050
F2_RMS_ACTIVE_DB = -60.0
F2_RMS_RATIO_MIN = 1.5
F2_IOI_BUCKETS = (1, 2, 3, 4, 6, 8, 12)


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def u(tag: str) -> float:
    return G.hash_uniform(tag)


def draw_row(row: dict, tag: str) -> int:
    return G.draw(row, u(tag))


def draw_from(weights: dict, tag: str) -> str:
    """Inverse-CDF over a {state: prob} dict in sorted-key order (no PRNG)."""
    keys = sorted(weights)
    tot = sum(weights[k] for k in keys) or 1.0
    x = u(tag)
    acc = 0.0
    for k in keys:
        acc += weights[k] / tot
        if x < acc:
            return k
    return keys[-1]


def seg_matrix(chain: dict) -> tuple[list, dict]:
    states = chain["states"]
    C = chain["segment_level_counts"]
    P = {}
    for i, s in enumerate(states):
        row = C[i]
        tot = sum(row)
        P[s] = {states[j]: (row[j] / tot if tot else 1.0 / len(states)) for j in range(len(states))}
    return states, P


def sample_bar(model: dict, tag: str, i: int, cand: str = "") -> dict:
    k = draw_row(G.row_for(model["kick_marginal"], "*"), f"{tag}|bar{i}{cand}|kick|*")
    s = draw_row(G.row_for(model["snare_given_kick"], str(k)), f"{tag}|bar{i}{cand}|snare|{k}")
    h = draw_row(G.row_for(model["hat_given_kick_snare"], f"{k}|{s}"), f"{tag}|bar{i}{cand}|hat|{k}|{s}")
    b = draw_row(G.row_for(model["bass_given_kick"], str(k)), f"{tag}|bar{i}{cand}|bass|{k}")
    return {"kick": k, "snare": s, "hat": h, "bass": b}


def sample_groove_bars(model: dict, tag: str, n: int) -> list:
    return [sample_bar(model, tag, i) for i in range(n)]


def sample_chords(chain: dict, tag: str, n: int, first_weights: dict | None = None) -> list:
    states, P = seg_matrix(chain)
    first = draw_from(first_weights if first_weights is not None else chain["stationary_distribution"], f"{tag}|chord0|stationary")
    seq = [first]
    for i in range(1, n):
        seq.append(draw_from(P[seq[-1]], f"{tag}|chord{i}|from={seq[-1]}"))
    return seq


def state_pcs(state: str, tonic: int) -> list | None:
    if state == "N" or ":" not in state:
        return None
    r, q = state.split(":")
    root = (tonic + int(r)) % 12
    return [(root + iv) % 12 for iv in QUALITIES[q]]


def popcount(x: int) -> int:
    return bin(int(x)).count("1")


def bar_density(g: dict) -> int:
    return popcount(g["kick"]) + popcount(g["snare"]) + popcount(g["hat"])


def state_root(state: str) -> int | None:
    return int(state.split(":")[0]) if state != "N" and ":" in state else None


def _f2_velocity(f2: dict, ladder: dict, tag: str) -> int:
    """F2 velocity draw (SHA-256 inverse-CDF on the empirical quantile ladder); uniform mode = the exact null (100)."""
    if f2["velocity_mode"] == "uniform":
        return 100
    return sample_velocity(ladder, u(tag))


def _f2_bass_register(model: dict, donor: str) -> dict:
    """Donor register {median, iqr_lo, iqr_hi} from bass_pitch_v5.json per_song; PD / Disco A (not in the n=21 corpus) use the
    corpus register (disclosed in the manifest via register['source'])."""
    ps = model.get("per_song", {}).get(donor, {}).get("register")
    if ps:
        return {"median": ps["median"], "iqr_lo": ps["iqr_lo"], "iqr_hi": ps["iqr_hi"], "source": f"per_song[{donor}]"}
    c = model["register"]["corpus"]
    return {"median": c["median"], "iqr_lo": c["iqr_lo"], "iqr_hi": c["iqr_hi"], "source": "corpus (donor not in the n=21 bass corpus)"}


def _f2_melody_run(f2: dict, label: str, n_bars: int, tonic: int, mode: str) -> list:
    """VOMM melody for one contiguous run of `n_bars` bars of section `label` (tags key on label + step so literal repeats
    of a section reproduce the same melody). Returns [(pos16, pitch, ioi16, phrase_pos)]."""
    M = f2["melody_model"]
    sample_next, token_pitch = f2["melody_fns"]
    lo, hi = F2_MELODY_REGISTER
    out, ctx, pos, prev, k = [], (), 0, None, 0
    total = n_bars * 16
    while pos < total:
        tag = f"{f2['tag']}|F2|melody|{label}|{k}"
        tok = sample_next(M, ctx, u(tag))
        deg, ioi = tok.split("|")
        ioi = int(ioi)
        pitch = int(token_pitch(tok, tonic, mode, lo, hi, prev))
        out.append([pos, pitch, ioi])
        prev = pitch
        ctx = (ctx + (tok,))[-F2_VOMM_ORDER:]
        pos += max(1, ioi)
        k += 1
    # phrase position: gap >= 2 beats (8 sixteenths) opens a new phrase; peak = highest pitch inside the phrase
    phrases, cur = [], []
    for i, (p, pitch, ioi) in enumerate(out):
        if cur and p - out[cur[-1]][0] >= int(F2_PHRASE_GAP_BEATS * 4):
            phrases.append(cur)
            cur = []
        cur.append(i)
    if cur:
        phrases.append(cur)
    posn = {}
    for ph in phrases:
        peak = max(ph, key=lambda i: (out[i][1], -i))
        for j, i in enumerate(ph):
            posn[i] = "first" if j == 0 else ("last" if j == len(ph) - 1 else ("peak" if i == peak else "other"))
    return [(p, pitch, ioi, posn[i]) for i, (p, pitch, ioi) in enumerate(out)]


def build_events(bars: list, chords: list, tonic: int, bpm: float, arr: list | None = None, f2: dict | None = None) -> dict:
    """arr (c85, optional): per-bar dicts {"mute": [stems], "fill": {"snare","hat"} | None, "hold": bool}; None = c84 behaviour.
    f2 (c86, optional): {"tag", "velocity_mode", "profiles", "bass_model", "bass_fns", "melody_model", "melody_fns", "register",
    "mode", "sections": [(label, bar_in_section)] parallel to bars}; None = c84/c85 behaviour byte-for-byte."""
    beat = 60.0 / bpm
    bar_len = 4 * beat
    s16 = beat / 4
    ev = {"drums": [], "bass": [], "keys": [], "melody": []}
    idx = {k: 0 for k in ev}

    def note(stem: str, inst: str, pitch: int, t0: float, t1: float, vel: int | None = None) -> None:
        i = idx[stem]
        s = {"index": i, "instrument": inst, "pitch": int(pitch), "start_time": round(t0, 6), "type": "start"}
        if vel is not None:
            s["velocity"] = int(vel)
        ev[stem].append(s)
        ev[stem].append({"start_event_index": i, "end_time": round(max(t1, t0 + 0.02), 6), "type": "end"})
        idx[stem] = i + 1

    P = f2["profiles"]["profiles"] if f2 else None
    sec = f2["sections"] if f2 else None
    for b, (g0, st) in enumerate(zip(bars, chords)):
        a = arr[b] if arr is not None else None
        g = dict(g0)
        mute = set(a["mute"]) if a else set()
        hold = bool(a and a.get("hold"))
        if a and a.get("fill"):
            g["snare"], g["hat"] = int(a["fill"]["snare"]), int(a["fill"]["hat"])
        t_bar = b * bar_len
        vt = f"{f2['tag']}|F2|{sec[b][0]}|{sec[b][1]}" if f2 else ""
        kick_slots = {2 * j for j in G.bits(g["kick"], 8)}
        if "drums" not in mute:
            if hold:
                note("drums", "drums", KICK_PITCH, t_bar, t_bar + DRUM_HIT_S, _f2_velocity(f2, P["drums"]["kick"]["0"], f"{vt}|drums|kick|0") if f2 else None)
            else:
                for j in G.bits(g["kick"], 8):
                    note("drums", "drums", KICK_PITCH, t_bar + 2 * j * s16, t_bar + 2 * j * s16 + DRUM_HIT_S,
                         _f2_velocity(f2, P["drums"]["kick"][str(2 * j)], f"{vt}|drums|kick|{2 * j}") if f2 else None)
                for p in G.bits(g["snare"]):
                    note("drums", "drums", SNARE_PITCH, t_bar + p * s16, t_bar + p * s16 + DRUM_HIT_S,
                         _f2_velocity(f2, P["drums"]["snare"][str(p)], f"{vt}|drums|snare|{p}") if f2 else None)
                for p in G.bits(g["hat"]):
                    note("drums", "drums", HAT_PITCH, t_bar + p * s16, t_bar + p * s16 + DRUM_HIT_S,
                         _f2_velocity(f2, P["drums"]["hat"][str(p)], f"{vt}|drums|hat|{p}") if f2 else None)
        pcs = state_pcs(st, tonic)
        root_pc = pcs[0] if pcs else tonic
        fifth_pc = pcs[2] if pcs and len(pcs) > 2 else (root_pc + 7) % 12
        nxt = state_pcs(chords[b + 1], tonic) if b + 1 < len(chords) else None
        next_root_pc = nxt[0] if nxt else None
        if "bass" not in mute:
            if hold:
                note("bass", "electric_bass", 40 + ((root_pc - 4) % 12), t_bar, t_bar + 4 * beat,
                     _f2_velocity(f2, P["bass"]["coincident"]["0"], f"{vt}|bass|hold") if f2 else None)
            else:
                bpos = G.bits(g["bass"])
                for k, p in enumerate(bpos):
                    t0 = t_bar + p * s16
                    t1 = t_bar + (bpos[k + 1] * s16 if k + 1 < len(bpos) else 4 * beat)
                    if f2:
                        sample_cls, to_pitch = f2["bass_fns"]
                        chg = bool(next_root_pc is not None and next_root_pc != root_pc and p >= 12)
                        cls = sample_cls(f2["bass_model"], p % 4, chg, u(f"{vt}|bass|cls|{p}"))
                        pitch = int(to_pitch(cls, root_pc, next_root_pc, f2["register"], u(f"{vt}|bass|pitch|{p}")))
                        lad = P["bass"]["coincident" if p in kick_slots else "other"][str(p)]
                        note("bass", "electric_bass", pitch, t0, t1, _f2_velocity(f2, lad, f"{vt}|bass|vel|{p}"))
                    else:
                        pc = fifth_pc if k % 4 == 3 else root_pc
                        pitch = 40 + ((pc - 4) % 12)  # E2..D#3
                        note("bass", "electric_bass", pitch, t0, t1)
        if pcs and "keys" not in mute:
            kv = _f2_velocity(f2, P["keys"]["0"], f"{vt}|keys") if f2 else None
            for n, pc in enumerate(pcs):
                pitch = 60 + ((pc - 0) % 12) + (12 if n and pc < pcs[0] else 0)
                note("keys", "electric_piano", pitch, t_bar, t_bar + 4 * beat - 0.02, kv)
        if pcs and not f2 and "melody" not in mute:
            for e8 in range(8):
                tag = f"melody|bar{b}|e{e8}|{st}"
                if u(tag) < MELODY_PLAY_P:
                    pc = pcs[int(u(tag + "|tone") * len(pcs)) % len(pcs)]
                    note("melody", "synth_lead", 72 + (pc % 12), t_bar + e8 * 2 * s16, t_bar + (e8 + 1) * 2 * s16 - 0.01)
    if f2:  # F2 melody: VOMM per contiguous section run (literal repeats reproduce), muted bars dropped, velocity by phrase position
        b = 0
        while b < len(bars):
            label = sec[b][0]
            e = b
            while e + 1 < len(bars) and sec[e + 1][0] == label and sec[e + 1][1] == sec[e][1] + 1:
                e += 1
            run = _f2_melody_run(f2, label, e - b + 1, tonic, f2["mode"])
            for pos, pitch, ioi, ppos in run:
                bb = b + pos // 16
                if arr is not None and "melody" in set(arr[bb]["mute"]):
                    continue
                t0 = b * bar_len + pos * s16
                vel = _f2_velocity(f2, P["melody"][ppos], f"{f2['tag']}|F2|melody|{label}|vel|{pos}")
                note("melody", "synth_lead", pitch, t0, t0 + max(1, ioi) * s16 - 0.01, vel)
            b = e + 1
    return ev


def write_wav_int16(path: Path, data: np.ndarray, sr: int) -> None:
    a = np.asarray(data, dtype=np.float32)
    if a.ndim == 1:
        a = np.stack([a, a], axis=-1)
    a = np.clip(a, -1.0, 1.0)
    ai = np.round(a * 32767.0).astype(np.int16)
    raw = struct.pack("<" + "h" * ai.size, *ai.reshape(-1).tolist())
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(raw)


def rms_norm(wav: Path, target_db: float) -> tuple[np.ndarray, int, float]:
    data, sr = sf.read(str(wav), dtype="float32", always_2d=True)
    cur = float(np.sqrt((data.astype(np.float64) ** 2).mean())) if data.size else 0.0
    gain = (10 ** (target_db / 20.0)) / cur if cur > 1e-9 else 1.0
    gain = max(0.05, min(4.0, gain))
    return data * gain, sr, gain


def donor_tempo(donor: str, corpus: Path) -> tuple[float, str]:
    blocked = json.loads((corpus / "recanonicalization_blocked.json").read_text())["blocked_songs"]
    if donor in blocked:
        return float(blocked[donor]["anchor_bpm"]), "tempo_blocked_anchor_bpm"
    return float(json.loads((corpus / donor / "tempo_v5.json").read_text())["bpm_v5"]), "tempo_v5.bpm_v5"


# ---------------------------------------------------------------- c85 F1: form plan + contrast rule + arrangement ----
def combine_events(ev: dict) -> list:
    """One event array over the four stems (drums, bass, keys, melody) with globally re-indexed start/end pairs."""
    out, off = [], 0
    for stem in ("drums", "bass", "keys", "melody"):
        n = 0
        for e in ev[stem]:
            e2 = dict(e)
            if e2["type"] == "start":
                e2["index"] = int(e2["index"]) + off
                n += 1
            else:
                e2["start_event_index"] = int(e2["start_event_index"]) + off
            out.append(e2)
        off += n
    return out


def canonicalize_labels(seq: list) -> list:
    seen: dict[str, str] = {}
    out = []
    for lab in seq:
        if lab not in seen:
            seen[lab] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[len(seen)]
        out.append(seen[lab])
    return out


def plan_form(fp: dict, tag: str) -> dict:
    n_sec = int(draw_from({k: float(v) for k, v in fp["length_distribution"].items()}, f"{tag}|form|n_sections"))
    if fp["R1"]["pass"]:
        labs = [draw_from(fp["start_distribution"], f"{tag}|form|label0")]
        for i in range(1, n_sec):
            labs.append(draw_from(fp["transition_probs"][labs[-1]], f"{tag}|form|label{i}|from={labs[-1]}"))
        raw, source = labs, "corpus_label_markov"
    else:
        raw, source = list(fp["R1"]["fallback_template"][:n_sec]), "R1_FAILED_fixed_template_AABABCAA"
    return {"n_sections": n_sec, "labels_raw": raw, "labels": canonicalize_labels(raw), "label_source": source}


def tercile_of(x: float, bounds: list) -> int:
    return 0 if x < bounds[0] else (1 if x < bounds[1] else 2)


def dominant_root(chords: list) -> int | None:
    cnt: dict[int, int] = {}
    for st in chords:
        r = state_root(st)
        if r is not None:
            cnt[r] = cnt.get(r, 0) + 1
    return min(cnt, key=lambda r: (-cnt[r], r)) if cnt else None


def contrast_section(groove: dict, chain: dict, fp: dict, tag: str, label: str, a_root: int | None, a_terc: int) -> dict:
    """Non-A section under the pre-registered contrast rule."""
    states = chain["states"]
    rows = [sum(r) for r in chain["segment_level_counts"]]
    allowed = {s: p for s, p in chain["stationary_distribution"].items()
               if state_root(s) is not None and state_root(s) != a_root and rows[states.index(s)] >= F1_MIN_SEGMENTS}
    if allowed:
        chords = sample_chords(chain, f"{tag}|section={label}", F1_BARS_PER_SECTION, first_weights=allowed)
        harmony_ok = state_root(chords[0]) != a_root
    else:
        chords = sample_chords(chain, f"{tag}|section={label}", F1_BARS_PER_SECTION)
        harmony_ok = False
    probs = fp["per_label"].get(label, {}).get("density_tercile_probs", [1 / 3, 1 / 3, 1 / 3])
    cands = [t for t in range(3) if t != a_terc]
    target = min(cands, key=lambda t: (-probs[t], t))
    b = fp["density_tercile_bounds"]
    mid = {0: b[0] / 2.0, 1: (b[0] + b[1]) / 2.0, 2: b[1] + (b[1] - b[0]) / 2.0}[target]
    bars, cand_used = [], []
    for i in range(F1_BARS_PER_SECTION):
        cs = [sample_bar(groove["model"], f"{tag}|section={label}", i, f"|cand{c}") for c in range(F1_N_CANDIDATES)]
        pick = next((c for c, g in enumerate(cs) if tercile_of(bar_density(g), b) == target), None)
        if pick is None:
            pick = min(range(F1_N_CANDIDATES), key=lambda c: (abs(bar_density(cs[c]) - mid), c))
        bars.append(cs[pick])
        cand_used.append(pick)
    dens = float(np.mean([bar_density(g) for g in bars]))
    terc = tercile_of(dens, b)
    return {"chords": chords, "bars": bars, "first_chord_root": state_root(chords[0]), "a_dominant_root": a_root,
            "harmony_contrast_ok": harmony_ok, "n_allowed_start_states": len(allowed), "target_tercile": target,
            "realized_density": round(dens, 6), "realized_tercile": terc, "a_realized_tercile": a_terc,
            "density_contrast_ok": terc != a_terc, "candidate_index_per_bar": cand_used,
            "contrast_rule_true": bool(harmony_ok and terc != a_terc)}


def arrangement(plan: dict, fp: dict, tag: str) -> tuple[list, dict]:
    labels, n = plan["labels"], plan["n_sections"]
    nb = F1_BARS_PER_SECTION
    arr = [{"mute": [], "fill": None, "hold": False} for _ in range(n * nb)]
    intro_bass_only = fp["intro_density_quantile"] is not None and fp["intro_density_quantile"] < F1_INTRO_BASS_ONLY_Q
    for k in range(nb):
        arr[k]["mute"] = ["keys", "melody"] + (["drums"] if intro_bass_only else [])
    for k in range((n - 1) * nb, n * nb):
        arr[k]["mute"] = sorted(set(arr[k]["mute"]) | {"melody"})
    arr[n * nb - 1]["hold"] = True
    lo, hi = n // 4, -(-3 * n // 4)
    breakdown = next((i for i in range(n) if lo <= i < hi and labels[i] != "A"), None)
    if breakdown is not None:
        for k in range(breakdown * nb, breakdown * nb + 4):
            arr[k]["mute"] = sorted(set(arr[k]["mute"]) | {"drums"})
    pool = fp["boundary_fill_pool"]
    fills = []
    for i in range(n):
        w = {str(j): float(e["count"]) for j, e in enumerate(pool)}
        e = pool[int(draw_from(w, f"{tag}|fill|section{i}"))]
        arr[i * nb + nb - 1]["fill"] = {"snare": e["snare"], "hat": e["hat"]}
        fills.append({"section": i, "snare": e["snare"], "hat": e["hat"]})
    return arr, {"intro": {"section": 0, "mode": "bass_only" if intro_bass_only else "drums_and_bass", "intro_density_quantile": fp["intro_density_quantile"]},
                 "outro": {"section": n - 1, "melody_muted": True, "final_bar_held": True},
                 "breakdown": {"section": breakdown, "drums_muted_bars": 4 if breakdown is not None else 0, "middle_half": [lo, hi]},
                 "fills": fills, "fill_pool_size": len(pool)}


def render_song(spec: dict, seed: int, out_dir: Path, groove: dict, chain: dict, corpus: Path, keep_per_track: bool,
                rules_sha: dict, cycle: int = 84, form_plan: dict | None = None, form_plan_sha: str | None = None,
                f2_cfg: dict | None = None) -> dict:
    donor = spec["donor_song_sha16"]
    gen_id = spec["generated_song_id"].replace("gen_v4_", "gen_v5_")
    tag = f"{gen_id}|donor={donor}|seed={seed}"
    f2 = None
    if f2_cfg is not None:  # c86 F2: per-song config (models are shared; register + key mode are donor-specific)
        key = chain["per_song"].get(donor, {}).get("key", {})
        f2 = {"tag": tag, "velocity_mode": f2_cfg["velocity_mode"], "profiles": f2_cfg["profiles"], "bass_model": f2_cfg["bass_model"],
              "bass_fns": f2_cfg["bass_fns"], "melody_model": f2_cfg["melody_model"], "melody_fns": f2_cfg["melody_fns"],
              "register": _f2_bass_register(f2_cfg["bass_model"], donor), "mode": str(key.get("mode", "major")),
              "mode_source": "donor_kk_key_from_chain" if key else "major_default_(donor not in chain)"}
    ser = serialize_v5 if f2 is not None else canonical_midi_serialize
    song_dir = out_dir / f"{gen_id}_donor_{donor}"
    song_dir.mkdir(parents=True, exist_ok=True)
    bpm, tempo_src = donor_tempo(donor, corpus)
    if donor in chain["per_song"]:
        tonic, tonic_src = int(chain["per_song"][donor]["key"]["tonic"]), "donor_kk_key_from_chain"
    else:
        tonic, tonic_src = int(u(f"{tag}|tonic") * 12) % 12, "sha256_derived_(donor not in chain)"
    jd, md, rd = song_dir / "generated_json", song_dir / "generated_midi", song_dir / "per_track"
    for d in (jd, md, rd):
        d.mkdir(exist_ok=True)
    f1 = None
    if form_plan is None:
        form_seq, bars_per_section = list(FORM_PLAN), BARS_PER_SECTION
        sec_bars = {s: sample_groove_bars(groove["model"], f"{tag}|section={s}", bars_per_section) for s in sorted(set(form_seq))}
        sec_chords = {s: sample_chords(chain, f"{tag}|section={s}", bars_per_section) for s in sorted(set(form_seq))}
        arr = None
    else:
        plan = plan_form(form_plan, tag)
        form_seq, bars_per_section = plan["labels"], F1_BARS_PER_SECTION
        sec_bars = {"A": sample_groove_bars(groove["model"], f"{tag}|section=A", bars_per_section)}
        sec_chords = {"A": sample_chords(chain, f"{tag}|section=A", bars_per_section)}
        a_root = dominant_root(sec_chords["A"])
        a_dens = float(np.mean([bar_density(g) for g in sec_bars["A"]]))
        a_terc = tercile_of(a_dens, form_plan["density_tercile_bounds"])
        contrast = {}
        for lab in sorted(set(form_seq) - {"A"}):
            c = contrast_section(groove, chain, form_plan, tag, lab, a_root, a_terc)
            sec_bars[lab], sec_chords[lab] = c["bars"], c["chords"]
            contrast[lab] = {k: v for k, v in c.items() if k not in ("bars", "chords")}
        arr, arr_info = arrangement(plan, form_plan, tag)
        (md / "sections").mkdir(exist_ok=True)
        core_sha = {}
        for i, lab in enumerate(form_seq):  # literal-repeat measure: core (pre-arrangement) section MIDI
            f2s = dict(f2, sections=[(lab, k) for k in range(bars_per_section)]) if f2 else None
            ev = build_events(sec_bars[lab], sec_chords[lab], tonic, bpm, None, f2s)
            cj = jd / f"section_{i}_{lab}.json"
            cj.write_text(json.dumps(combine_events(ev), sort_keys=True, separators=(",", ":")))
            cm = md / "sections" / f"section_{i}_{lab}.mid"
            ser(str(cj), str(cm), float(bpm), (4, 4))
            core_sha[f"{i}_{lab}"] = _sha(cm)
        a_shas = {v for k, v in core_sha.items() if k.endswith("_A")}
        f1 = {"plan": plan, "a_dominant_root": a_root, "a_realized_density": round(a_dens, 6), "a_realized_tercile": a_terc,
              "contrast": contrast, "arrangement": arr_info, "section_core_midi_sha256": core_sha, "a_repeats_byte_equal": len(a_shas) == 1,
              "n_a_sections": sum(1 for s in form_seq if s == "A")}
    bars = [b for s in form_seq for b in sec_bars[s]]
    chords = [c for s in form_seq for c in sec_chords[s]]
    f2f = dict(f2, sections=[(s, k) for s in form_seq for k in range(bars_per_section)]) if f2 else None
    events = build_events(bars, chords, tonic, bpm, arr, f2f)
    midi_sha, wav_sha, gains, profiles_used = {}, {}, {}, {}
    bass_profile = json.loads((_WS / spec["donor_bass_profile_relpath"]).read_text())
    sf2_path, sf2_sha = bass_profile["identity"]["sf2_path"], bass_profile["identity"].get("sf2_sha256", "")

    def shim(program: int, note_: str) -> dict:
        return {"family": "sf2", "identity": {"sf2_path": sf2_path, "sf2_sha256": sf2_sha, "bank": 0, "program": program},
                "params": {"sample_rate": 44100, "gain": 1.0}, "note": note_}

    tracks = []
    for stem in ("drums", "bass", "keys", "melody"):
        (jd / f"{stem}.json").write_text(json.dumps(events[stem], sort_keys=True, separators=(",", ":")))
        ser(str(jd / f"{stem}.json"), str(md / f"{stem}.mid"), float(bpm), (4, 4))
        midi_sha[stem] = _sha(md / f"{stem}.mid")
        if stem == "bass":
            prof, profiles_used[stem] = bass_profile, spec["donor_bass_profile_relpath"]
        elif stem == "drums":
            rel = spec.get("donor_drums_profile_relpath")
            if rel:
                prof, profiles_used[stem] = json.loads((_WS / rel).read_text()), rel
            else:
                prof, profiles_used[stem] = shim(SHIMS["drums_cg"]["program"], SHIMS["drums_cg"]["name"]), "shim:" + SHIMS["drums_cg"]["name"]
        else:
            prof, profiles_used[stem] = shim(SHIMS[stem]["program"], SHIMS[stem]["name"]), "shim:" + SHIMS[stem]["name"]
        wav = rd / f"{stem}.wav"
        if not events[stem]:  # empty stem (e.g. all-N chords): silent song length, no render
            sr0 = 44100
            write_wav_int16(wav, np.zeros((int(sr0 * len(bars) * 4 * 60.0 / bpm), 2), dtype=np.float32), sr0)
        else:
            sf2_replay(prof, str(md / f"{stem}.mid"), str(wav))
        wav_sha[stem] = _sha(wav)
        data, sr, g = rms_norm(wav, TARGET_RMS_DB[stem])
        gains[stem] = round(g, 6)
        tracks.append(data)
    max_len = max(t.shape[0] for t in tracks)
    acc = np.zeros((max_len, 2), dtype=np.float64)
    for t in tracks:
        acc[: t.shape[0], :] += t.astype(np.float64)
    peak = float(np.abs(acc).max())
    if peak > 0.99:
        acc *= 0.99 / peak
    mix = acc.astype(np.float32)
    out_wav = song_dir / "ab_mix.wav"
    write_wav_int16(out_wav, mix, sr)
    deleted = []
    if not keep_per_track:
        for p in sorted(rd.glob("*.wav")):
            deleted.append(p.name)
            p.unlink()
    duration = round(len(mix) / sr, 4)
    man = {"schema_version": 1, "cycle": cycle, "run_id": "run-2026-09-06T000000Z", "agent": "worker",
           "milestone": "M-V5-GEN-1/iteration-01-c84" if form_plan is None else "M-V5-GEN-1/F1-form-arrangement",
           "generated_song_id": gen_id, "donor_song_sha16": donor, "donor_song_name": spec.get("donor_song_name"), "seed": seed, "seed_str": tag,
           "generator": "groove_first_v5", "generator_hash": _sha(Path(__file__)), "rules_sha256": rules_sha,
           "tempo_bpm": bpm, "tempo_source": tempo_src, "tonic": tonic, "tonic_source": tonic_src,
           "form_plan": list(form_seq), "bars_per_section": bars_per_section, "n_bars": len(bars),
           "section_chords": sec_chords, "chord_sequence": chords, "section_grooves": sec_bars,
           "midi_sha256": midi_sha, "per_track_wav_sha256": wav_sha, "per_track_deleted_after_mix": deleted, "gains": gains,
           "target_rms_dbfs": TARGET_RMS_DB, "profiles_used": profiles_used, "shims_disclosed": SHIMS,
           "donor_bass_profile_relpath": spec["donor_bass_profile_relpath"], "donor_drums_profile_relpath": spec.get("donor_drums_profile_relpath"),
           "ab_mix_sha256": _sha(out_wav), "ab_mix_duration_s": duration, "sample_rate": sr,
           "sum_method": "float_accumulate_peaklimit_099_max_len_zero_pad", "env_pin_sha256": ENV_PIN_SHA256, "env_pins": dict(_PINS),
           "ear_score": None, "ear_score_reason": "scored separately by scripts/v5/score_gen_batch_v5.py (informational, FD-6)",
           "sampling": "SHA-256 inverse-CDF on seed_str-derived tags (no PRNG)",
           "form_repetition": "section A generated once, repeated literally at positions 1, 2, 4" if form_plan is None
           else "every label generated once and repeated literally wherever it recurs (core MIDI byte-equality per section under section_core_midi_sha256)"}
    if f1 is not None:
        f1["clauses"] = {"n_bars_ge_32": len(bars) >= F1_MIN_BARS, "duration_ge_90s": duration >= F1_MIN_DURATION_S,
                         "distinct_labels_ge_3": len(set(form_seq)) >= F1_MIN_LABELS,
                         "contrast_rule_all_non_a": all(c["contrast_rule_true"] for c in f1["contrast"].values()) and bool(f1["contrast"]),
                         "a_repeats_byte_equal": f1["a_repeats_byte_equal"]}
        f1["all_clauses"] = all(f1["clauses"].values())
        man["form_plan_sha256"] = form_plan_sha
        man["form_prereg_sha256"] = _sha(Path("data/v5/gen/form_prereg_c85.json"))
        man["f1"] = f1
    if f2 is not None:
        per_stem = {}
        for stem in ("drums", "bass", "keys", "melody"):
            vels = [int(e["velocity"]) for e in events[stem] if e["type"] == "start"]
            pitches = [int(e["pitch"]) for e in events[stem] if e["type"] == "start"]
            per_stem[stem] = {"n_notes": len(vels), "n_distinct_velocities": len(set(vels)), "velocity_min": min(vels) if vels else None,
                              "velocity_max": max(vels) if vels else None, "velocity_mean": round(sum(vels) / len(vels), 3) if vels else None,
                              "velocities_present": bool(vels) and (len(set(vels)) >= 2 or len(vels) == 1),
                              "pitch_min": min(pitches) if pitches else None, "pitch_max": max(pitches) if pitches else None}
        man["milestone"] = "M-V5-GEN-1/F2-bass-melody-dynamics"
        man["f2"] = {"route": f2_cfg["route"], "velocity_mode": f2["velocity_mode"], "serializer": "scripts/v5/midi_from_json_events_v5.py (velocity field; byte-equal to c4 without velocities)",
                     "models_sha256": f2_cfg["models_sha256"], "prereg_sha256": f2_cfg["prereg_sha256"], "bass_register": f2["register"],
                     "melody_key_mode": f2["mode"], "melody_key_mode_source": f2["mode_source"], "melody_register": list(F2_MELODY_REGISTER),
                     "per_stem": per_stem, "velocities_present_all_stems_with_notes": all(v["velocities_present"] for v in per_stem.values() if v["n_notes"])}
        man["f2_prereg_sha256"] = f2_cfg["prereg_sha256"]
    (song_dir / "ab_mix.manifest.json").write_text(json.dumps(man, sort_keys=True, indent=2) + "\n")
    return man


def frame_rms_variance(wav: Path) -> dict:
    """c86 F2 clause (c): variance of the 50 ms frame-RMS (dB) over ACTIVE frames (> -60 dBFS); gain-invariant."""
    data, sr = sf.read(str(wav), dtype="float32", always_2d=True)
    y = data.astype(np.float64).mean(axis=1)
    n = int(round(F2_RMS_FRAME_S * sr))
    nf = len(y) // n
    if nf == 0:
        return {"n_frames": 0, "n_active": 0, "variance_db2": None}
    fr = y[: nf * n].reshape(nf, n)
    rms = 20.0 * np.log10(np.sqrt((fr * fr).mean(axis=1)) + 1e-9)
    act = rms[rms > F2_RMS_ACTIVE_DB]
    return {"n_frames": int(nf), "n_active": int(act.size), "variance_db2": round(float(act.var()), 6) if act.size > 1 else None,
            "mean_db": round(float(act.mean()), 4) if act.size else None}


def onset_rms_variance(wav: Path, events_json: Path) -> dict:
    """INFORMATIONAL diagnostic (not the pre-registered clause): variance of the 50 ms RMS (dB) measured at every note onset of the
    stem — the quantity the F2 velocities modulate directly (mirrors the Route-1 extraction window)."""
    data, sr = sf.read(str(wav), dtype="float32", always_2d=True)
    y = data.astype(np.float64).mean(axis=1)
    n = int(round(F2_RMS_FRAME_S * sr))
    vals = []
    for e in json.loads(events_json.read_text()):
        if e.get("type") != "start":
            continue
        c = int(round(float(e["start_time"]) * sr))
        seg = y[max(0, c): min(len(y), c + n)]
        if seg.size:
            vals.append(20.0 * np.log10(np.sqrt((seg * seg).mean()) + 1e-9))
    a = np.asarray(vals)
    return {"n_onsets": int(a.size), "variance_db2": round(float(a.var()), 6) if a.size > 1 else None, "mean_db": round(float(a.mean()), 4) if a.size else None}


def f2_rms_variance_test(f2_dir: Path, uni_dir: Path, per_stem: dict) -> dict:
    out, all_ok = {}, True
    for stem, st in per_stem.items():
        if not st["n_notes"]:
            out[stem] = {"skipped": "no notes"}
            continue
        a, b = frame_rms_variance(f2_dir / f"{stem}.wav"), frame_rms_variance(uni_dir / f"{stem}.wav")
        ratio = (a["variance_db2"] / b["variance_db2"]) if a["variance_db2"] and b["variance_db2"] else None
        ok = ratio is not None and ratio >= F2_RMS_RATIO_MIN
        all_ok = all_ok and ok
        out[stem] = {"f2": a, "uniform": b, "ratio_f2_over_uniform": round(ratio, 4) if ratio is not None else None, "ge_1p5": ok}
        ej = f2_dir.parent / "generated_json" / f"{stem}.json"
        if ej.exists():  # informational onset-window diagnostic
            oa, ob = onset_rms_variance(f2_dir / f"{stem}.wav", ej), onset_rms_variance(uni_dir / f"{stem}.wav", ej)
            out[stem]["onset_rms_informational"] = {"f2": oa, "uniform": ob,
                                                    "ratio_f2_over_uniform": round(oa["variance_db2"] / ob["variance_db2"], 4) if oa["variance_db2"] and ob["variance_db2"] else None}
    return {"frame_s": F2_RMS_FRAME_S, "active_floor_dbfs": F2_RMS_ACTIVE_DB, "ratio_min": F2_RMS_RATIO_MIN, "per_stem": out, "passes_all_stems_with_notes": all_ok,
            "clause": "pre-registered: variance of the 50 ms frame-RMS (dB) over active frames, F2 / uniform >= 1.5 on every stem with notes; the onset-window ratio is informational only"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v5 groove-first generator")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--songs", type=int, default=5)
    ap.add_argument("--donor-map", default="data/v4/gen/donor_profile_map.json")
    ap.add_argument("--groove", default="data/v5/rules/groove_v5_v2_full.json")
    ap.add_argument("--harmony", default="data/v5/rules/harmony_markov_v5_full.json")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--out", default=None, help="default data/v5/gen/iteration_NN")
    ap.add_argument("--prove-replay", action="store_true")
    ap.add_argument("--keep-per-track", action="store_true")
    ap.add_argument("--no-stall-update", action="store_true")
    ap.add_argument("--form-plan", default=None, help="c85 F1: data/v5/rules/form_plan_v5.json (default OFF = c84 iteration-1 path)")
    ap.add_argument("--cycle", type=int, default=84)
    ap.add_argument("--feature", default=None, help="c85 F6: feature label recorded in the stall history (default: F1 when --form-plan, else none)")
    # c86 F2 (default OFF: the --form-plan path stays byte-identical to iteration 2)
    ap.add_argument("--f2", action="store_true", help="c86 F2: bass pitches from bass_pitch_v5, melody from melody_vomm_v5, velocities from velocity_profiles_v5")
    ap.add_argument("--velocity-mode", choices=("uniform", "f2"), default="uniform", help="c86 F2: 'uniform' = velocity 100 everywhere (the exact null)")
    ap.add_argument("--velocity-profiles", default="data/v5/rules/velocity_profiles_v5.json")
    ap.add_argument("--bass-model", default="data/v5/rules/bass_pitch_v5.json")
    ap.add_argument("--melody-model", default="data/v5/rules/melody_vomm_v5.json")
    ap.add_argument("--rms-variance-test", action="store_true", help="c86 F2 clause (c): also render the uniform-velocity twin into a tempdir and compare per-stem frame-RMS variance")
    args = ap.parse_args(argv)
    f2_cfg = None
    if args.f2:
        from scripts.v5.bass_pitch_v5 import sample_interval_class, interval_to_pitch  # noqa: E402  c86 T2 models (READ-ONLY use)
        from scripts.v5.melody_vomm_v5 import sample_next, token_pitch  # noqa: E402
        f2_cfg = {"velocity_mode": args.velocity_mode, "profiles": json.loads(Path(args.velocity_profiles).read_text()),
                  "bass_model": json.loads(Path(args.bass_model).read_text()), "bass_fns": (sample_interval_class, interval_to_pitch),
                  "melody_model": json.loads(Path(args.melody_model).read_text()), "melody_fns": (sample_next, token_pitch),
                  "prereg_sha256": _sha(Path("data/v5/gen/f2_prereg_c86.json")),
                  "models_sha256": {"velocity_profiles": _sha(Path(args.velocity_profiles)), "bass_pitch": _sha(Path(args.bass_model)),
                                    "melody_vomm": _sha(Path(args.melody_model)), "velocity_v5_script": _sha(Path("scripts/v5/velocity_v5.py")),
                                    "bass_pitch_script": _sha(Path("scripts/v5/bass_pitch_v5.py")), "melody_vomm_script": _sha(Path("scripts/v5/melody_vomm_v5.py")),
                                    "serializer_v5_script": _sha(Path("scripts/v5/midi_from_json_events_v5.py"))}}
        f2_cfg["route"] = f2_cfg["profiles"].get("route", "ROUTE_1_STEM_AUDIO")
    out = Path(args.out or f"data/v5/gen/iteration_{args.iteration:02d}")
    out.mkdir(parents=True, exist_ok=True)
    groove = json.loads(Path(args.groove).read_text())
    chain = json.loads(Path(args.harmony).read_text())
    assert chain["degeneracy_verdict"] == "NON_DEGENERATE", "harmony chain must be NON_DEGENERATE (brief P3 gate)"
    assert groove["verdict"] != "GROOVE_V2_DEGENERATE", "groove model must not be DEGENERATE (brief P3 gate)"
    rules_sha = {"harmony_chain": _sha(Path(args.harmony)), "groove_model": _sha(Path(args.groove)),
                 "harmony_prereg": _sha(Path("data/v5/rules/harmony_prereg_c84.json")), "groove_prereg": _sha(Path("data/v5/rules/groove_prereg_c84.json")),
                 "donor_map": _sha(Path(args.donor_map))}
    form_plan, fp_sha = None, None
    if args.form_plan:
        form_plan = json.loads(Path(args.form_plan).read_text())
        fp_sha = _sha(Path(args.form_plan))
        rules_sha["form_plan"] = fp_sha
    specs = json.loads(Path(args.donor_map).read_text())["songs"][: args.songs]
    corpus = Path(args.corpus_dir)
    rollup = {"schema_version": 1, "cycle": args.cycle, "agent": "worker", "run_id": "run-2026-09-06T000000Z", "iteration": args.iteration, "seed": args.seed,
              "generator": "groove_first_v5", "generator_hash": _sha(Path(__file__)), "rules_sha256": rules_sha, "env_pin_sha256": ENV_PIN_SHA256,
              "harmony_verdict": chain["degeneracy_verdict"], "groove_verdict": groove["verdict"],
              "groove_overfits_disclosed": groove["verdict"] == "GROOVE_V2_OVERFITS", "songs": []}
    if form_plan is not None:
        rollup["form_plan"] = {"path": args.form_plan, "sha256": fp_sha, "R1_pass": form_plan["R1"]["pass"],
                               "label_source": "corpus_label_markov" if form_plan["R1"]["pass"] else "R1_FAILED_fixed_template_AABABCAA"}
    if f2_cfg is not None:
        rules_sha.update({"velocity_profiles": f2_cfg["models_sha256"]["velocity_profiles"], "bass_pitch": f2_cfg["models_sha256"]["bass_pitch"],
                          "melody_vomm": f2_cfg["models_sha256"]["melody_vomm"]})
        rollup["f2"] = {"route": f2_cfg["route"], "velocity_mode": args.velocity_mode, "models_sha256": f2_cfg["models_sha256"],
                        "prereg_sha256": f2_cfg["prereg_sha256"], "rms_variance_test_requested": bool(args.rms_variance_test)}
    for spec in specs:
        keep = args.keep_per_track or bool(f2_cfg is not None and args.rms_variance_test)
        man = render_song(spec, args.seed, out, groove, chain, corpus, keep, rules_sha, args.cycle, form_plan, fp_sha, f2_cfg)
        entry = {"generated_song_id": man["generated_song_id"], "donor": man["donor_song_sha16"], "ab_mix_sha256": man["ab_mix_sha256"],
                 "duration_s": man["ab_mix_duration_s"], "chords": man["chord_sequence"]}
        song_dir = out / f"{man['generated_song_id']}_donor_{man['donor_song_sha16']}"
        if f2_cfg is not None:
            entry["f2_per_stem"] = {k: {kk: v[kk] for kk in ("n_notes", "n_distinct_velocities", "velocity_min", "velocity_max")} for k, v in man["f2"]["per_stem"].items()}
            entry["velocities_present"] = man["f2"]["velocities_present_all_stems_with_notes"]
            if args.rms_variance_test:
                uni_cfg = dict(f2_cfg, velocity_mode="uniform")
                with tempfile.TemporaryDirectory(prefix="gen_v5_uniform_") as td:
                    man_u = render_song(spec, args.seed, Path(td), groove, chain, corpus, True, rules_sha, args.cycle, form_plan, fp_sha, uni_cfg)
                    uni_dir = Path(td) / f"{man_u['generated_song_id']}_donor_{man_u['donor_song_sha16']}" / "per_track"
                    test = f2_rms_variance_test(song_dir / "per_track", uni_dir, man["f2"]["per_stem"])
                    test["uniform_twin"] = {"ab_mix_sha256": man_u["ab_mix_sha256"], "midi_sha256": man_u["midi_sha256"], "tempdir": td,
                                            "per_stem_velocities": {k: (v["velocity_min"], v["velocity_max"]) for k, v in man_u["f2"]["per_stem"].items()},
                                            "same_pitches_as_f2": all(man_u["f2"]["per_stem"][k]["pitch_min"] == man["f2"]["per_stem"][k]["pitch_min"]
                                                                      and man_u["f2"]["per_stem"][k]["pitch_max"] == man["f2"]["per_stem"][k]["pitch_max"] for k in man["f2"]["per_stem"])}
                if not args.keep_per_track:  # score-and-delete: the per-track WAVs were kept only for the test
                    deleted = []
                    for p in sorted((song_dir / "per_track").glob("*.wav")):
                        deleted.append(p.name)
                        p.unlink()
                    man["per_track_deleted_after_mix"] = deleted
                man["f2"]["rms_variance_test"] = test
                (song_dir / "ab_mix.manifest.json").write_text(json.dumps(man, sort_keys=True, indent=2) + "\n")
                entry["rms_variance_test"] = {k: v.get("ratio_f2_over_uniform") for k, v in test["per_stem"].items()}
                entry["rms_variance_passes"] = test["passes_all_stems_with_notes"]
                print(f"  RMS-variance ratios {entry['rms_variance_test']} -> {'PASS' if test['passes_all_stems_with_notes'] else 'FAIL'}")
        if "f1" in man:
            entry.update({"form": man["form_plan"], "n_bars": man["n_bars"], "clauses": man["f1"]["clauses"], "all_clauses": man["f1"]["all_clauses"],
                          "contrast": {k: {kk: v[kk] for kk in ("harmony_contrast_ok", "density_contrast_ok", "contrast_rule_true", "n_allowed_start_states")} for k, v in man["f1"]["contrast"].items()},
                          "breakdown_section": man["f1"]["arrangement"]["breakdown"]["section"], "intro_mode": man["f1"]["arrangement"]["intro"]["mode"]})
        print(f"{man['generated_song_id']} donor={man['donor_song_sha16']} bpm={man['tempo_bpm']:.2f} tonic={man['tonic']} sha={man['ab_mix_sha256'][:12]} dur={man['ab_mix_duration_s']}s"
              + (f" form={''.join(man['form_plan'])} bars={man['n_bars']} clauses={man['f1']['clauses']}" if "f1" in man else ""))
        if args.prove_replay:
            with tempfile.TemporaryDirectory(prefix="gen_v5_replay_") as td:
                man2 = render_song(spec, args.seed, Path(td), groove, chain, corpus, False, rules_sha, args.cycle, form_plan, fp_sha, f2_cfg)
                td_used = td
            proof = {"verdict": "REPLAY_PROOF_HOLDS" if man2["ab_mix_sha256"] == man["ab_mix_sha256"] else "REPLAY_PROOF_FAILS",
                     "run1_sha256": man["ab_mix_sha256"], "run2_sha256": man2["ab_mix_sha256"], "run2_midi_equal": man2["midi_sha256"] == man["midi_sha256"],
                     "run2_per_track_equal": man2["per_track_wav_sha256"] == man["per_track_wav_sha256"], "run2_tempdir": td_used,
                     "env_pin_sha256": ENV_PIN_SHA256, "cycle": args.cycle, "agent": "worker"}
            (out / f"{man['generated_song_id']}_donor_{man['donor_song_sha16']}" / "ab_mix.replay_proof.json").write_text(json.dumps(proof, sort_keys=True, indent=2) + "\n")
            entry["replay_proof"] = proof["verdict"]
            print(f"  {proof['verdict']}")
        rollup["songs"].append(entry)
    if form_plan is not None:
        n_ok = sum(1 for s in rollup["songs"] if s.get("all_clauses"))
        rollup["f1_enum"] = "FORM_PLAN_LANDS" if n_ok == len(rollup["songs"]) == 5 else ("FORM_PLAN_PARTIAL" if n_ok >= 3 else "FORM_PLAN_FAILS")
        rollup["f1_songs_all_clauses"] = n_ok
        print(f"F1 enum {rollup['f1_enum']} ({n_ok}/5 songs satisfy all clauses)")
    if f2_cfg is not None:  # c86 F2 enum (pre-registered): LANDS iff velocities on every stem with notes 5/5 AND RMS test 5/5 AND replay x2 holds
        songs_ = rollup["songs"]
        vel_ok = sum(1 for s in songs_ if s.get("velocities_present"))
        rms_ok = sum(1 for s in songs_ if s.get("rms_variance_passes")) if args.rms_variance_test else None
        rep_ok = sum(1 for s in songs_ if s.get("replay_proof") == "REPLAY_PROOF_HOLDS") if args.prove_replay else None
        clauses = {"velocities_present_5_of_5": vel_ok == len(songs_) == 5, "rms_variance_5_of_5": rms_ok == len(songs_) == 5 if rms_ok is not None else None,
                   "replay_x2_5_of_5": rep_ok == len(songs_) == 5 if rep_ok is not None else None}
        rollup["f2"].update({"clauses": clauses, "n_velocities_present": vel_ok, "n_rms_variance_pass": rms_ok, "n_replay_holds": rep_ok,
                             "f2_enum": "F2_LANDS" if all(v is True for v in clauses.values()) else ("F2_PARTIAL" if args.velocity_mode == "f2" else "F2_PARTIAL(velocity_mode=uniform)")})
        print(f"F2 enum {rollup['f2']['f2_enum']} clauses {clauses}")
    (out / "iteration_rollup.json").write_text(json.dumps(rollup, sort_keys=True, indent=2) + "\n")
    if not args.no_stall_update:
        sc_p = Path("data/v5/gen/stall_counter.json")
        sc = json.loads(sc_p.read_text())
        sc["iterations"] = max(int(sc.get("iterations", 0)), args.iteration)
        sc["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())  # c85 F6
        feature = args.feature or ("F2 bass+melody+dynamics" if f2_cfg is not None else ("F1 length+form+arrangement" if form_plan is not None else "none (seed only)"))
        hist = {"iteration": args.iteration, "cycle": args.cycle, "seed": args.seed, "n_songs": len(specs),
                "passers_declared": 0, "feature": feature, "donor_map_sha256": rules_sha["donor_map"],
                "form_plan_sha256": fp_sha, "rules_sha256": {k: rules_sha[k] for k in ("harmony_chain", "groove_model")},
                "note": "ear scores informational under FD-6 (c76 L119 proof); no passer declared"}
        if f2_cfg is not None:
            hist["f2"] = {"route": f2_cfg["route"], "velocity_mode": args.velocity_mode, "models_sha256": f2_cfg["models_sha256"], "f2_enum": rollup["f2"].get("f2_enum")}
        sc.setdefault("history", []).append(hist)
        sc_p.write_text(json.dumps(sc, indent=2) + "\n")
        print(f"stall counter {sc['iterations']}/{sc['budget']}")
    # c85 M4: the groove model is NOT copied into the iteration dir any more (rules_sha256.groove_model pins it).
    return 0


if __name__ == "__main__":
    sys.exit(main())
