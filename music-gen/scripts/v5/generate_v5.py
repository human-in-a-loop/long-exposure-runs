#!/usr/bin/python3
"""c84 P3 — groove-first v5 generator, iteration 1 (OPERATOR #6: drums+bass from the joint groove model -> chords from the
harmony chain on a fixed form plan -> keys/melody as chord tones on the grid; donor profiles + mix as v4).

created: 2026-09-09T21:30:00Z
cycle: 84
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/iteration-01-c84

Inputs (READ-ONLY): data/v5/rules/groove_v5_v2_full.json (c84 P2 model: kick8 marginal + snare16|kick8 + hat16|kick8,snare16 +
bass16|kick8, alpha-smoothed), data/v5/rules/harmony_markov_v5_full.json (c84 P1 chain: functional states "rel_root:quality",
segment-level change matrix + stationary distribution), data/v4/gen/donor_profile_map.json (5 donors, pinned sf2 profiles),
tempo: donor bpm_v5 (tempo-blocked donors use their frozen anchor_bpm from recanonicalization_blocked.json).
Per song (seed_str = f"gen_v5_song_{N}|donor={sha16}|seed={seed}"), all draws by SHA-256 inverse-CDF (no PRNG):
  1. form plan A A B A, 4 bars per section (16 bars); section A generated ONCE and repeated literally (forced repetition).
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
import shutil
import struct
import sys
import tempfile
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


def sample_groove_bars(model: dict, tag: str, n: int) -> list:
    out = []
    for i in range(n):
        k = draw_row(G.row_for(model["kick_marginal"], "*"), f"{tag}|bar{i}|kick|*")
        s = draw_row(G.row_for(model["snare_given_kick"], str(k)), f"{tag}|bar{i}|snare|{k}")
        h = draw_row(G.row_for(model["hat_given_kick_snare"], f"{k}|{s}"), f"{tag}|bar{i}|hat|{k}|{s}")
        b = draw_row(G.row_for(model["bass_given_kick"], str(k)), f"{tag}|bar{i}|bass|{k}")
        out.append({"kick": k, "snare": s, "hat": h, "bass": b})
    return out


def sample_chords(chain: dict, tag: str, n: int) -> list:
    states, P = seg_matrix(chain)
    first = draw_from(chain["stationary_distribution"], f"{tag}|chord0|stationary")
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


def build_events(bars: list, chords: list, tonic: int, bpm: float) -> dict:
    beat = 60.0 / bpm
    bar_len = 4 * beat
    s16 = beat / 4
    ev = {"drums": [], "bass": [], "keys": [], "melody": []}
    idx = {k: 0 for k in ev}

    def note(stem: str, inst: str, pitch: int, t0: float, t1: float) -> None:
        i = idx[stem]
        ev[stem].append({"index": i, "instrument": inst, "pitch": int(pitch), "start_time": round(t0, 6), "type": "start"})
        ev[stem].append({"start_event_index": i, "end_time": round(max(t1, t0 + 0.02), 6), "type": "end"})
        idx[stem] = i + 1

    for b, (g, st) in enumerate(zip(bars, chords)):
        t_bar = b * bar_len
        for j in G.bits(g["kick"], 8):
            note("drums", "drums", KICK_PITCH, t_bar + 2 * j * s16, t_bar + 2 * j * s16 + DRUM_HIT_S)
        for p in G.bits(g["snare"]):
            note("drums", "drums", SNARE_PITCH, t_bar + p * s16, t_bar + p * s16 + DRUM_HIT_S)
        for p in G.bits(g["hat"]):
            note("drums", "drums", HAT_PITCH, t_bar + p * s16, t_bar + p * s16 + DRUM_HIT_S)
        pcs = state_pcs(st, tonic)
        root_pc = pcs[0] if pcs else tonic
        fifth_pc = pcs[2] if pcs and len(pcs) > 2 else (root_pc + 7) % 12
        bpos = G.bits(g["bass"])
        for k, p in enumerate(bpos):
            pc = fifth_pc if k % 4 == 3 else root_pc
            pitch = 40 + ((pc - 4) % 12)  # E2..D#3
            t0 = t_bar + p * s16
            t1 = t_bar + (bpos[k + 1] * s16 if k + 1 < len(bpos) else 4 * beat)
            note("bass", "electric_bass", pitch, t0, t1)
        if pcs:
            for n, pc in enumerate(pcs):
                pitch = 60 + ((pc - 0) % 12) + (12 if n and pc < pcs[0] else 0)
                note("keys", "electric_piano", pitch, t_bar, t_bar + 4 * beat - 0.02)
            for e8 in range(8):
                tag = f"melody|bar{b}|e{e8}|{st}"
                if u(tag) < MELODY_PLAY_P:
                    pc = pcs[int(u(tag + "|tone") * len(pcs)) % len(pcs)]
                    note("melody", "synth_lead", 72 + (pc % 12), t_bar + e8 * 2 * s16, t_bar + (e8 + 1) * 2 * s16 - 0.01)
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


def render_song(spec: dict, seed: int, out_dir: Path, groove: dict, chain: dict, corpus: Path, keep_per_track: bool,
                rules_sha: dict) -> dict:
    donor = spec["donor_song_sha16"]
    gen_id = spec["generated_song_id"].replace("gen_v4_", "gen_v5_")
    tag = f"{gen_id}|donor={donor}|seed={seed}"
    song_dir = out_dir / f"{gen_id}_donor_{donor}"
    song_dir.mkdir(parents=True, exist_ok=True)
    bpm, tempo_src = donor_tempo(donor, corpus)
    if donor in chain["per_song"]:
        tonic, tonic_src = int(chain["per_song"][donor]["key"]["tonic"]), "donor_kk_key_from_chain"
    else:
        tonic, tonic_src = int(u(f"{tag}|tonic") * 12) % 12, "sha256_derived_(donor not in chain)"
    n_sec = len(FORM_PLAN)
    sec_bars = {s: sample_groove_bars(groove["model"], f"{tag}|section={s}", BARS_PER_SECTION) for s in sorted(set(FORM_PLAN))}
    sec_chords = {s: sample_chords(chain, f"{tag}|section={s}", BARS_PER_SECTION) for s in sorted(set(FORM_PLAN))}
    bars = [b for s in FORM_PLAN for b in sec_bars[s]]
    chords = [c for s in FORM_PLAN for c in sec_chords[s]]
    events = build_events(bars, chords, tonic, bpm)
    jd, md, rd = song_dir / "generated_json", song_dir / "generated_midi", song_dir / "per_track"
    for d in (jd, md, rd):
        d.mkdir(exist_ok=True)
    midi_sha, wav_sha, gains, profiles_used = {}, {}, {}, {}
    bass_profile = json.loads((_WS / spec["donor_bass_profile_relpath"]).read_text())
    sf2_path, sf2_sha = bass_profile["identity"]["sf2_path"], bass_profile["identity"].get("sf2_sha256", "")

    def shim(program: int, note_: str) -> dict:
        return {"family": "sf2", "identity": {"sf2_path": sf2_path, "sf2_sha256": sf2_sha, "bank": 0, "program": program},
                "params": {"sample_rate": 44100, "gain": 1.0}, "note": note_}

    tracks = []
    for stem in ("drums", "bass", "keys", "melody"):
        (jd / f"{stem}.json").write_text(json.dumps(events[stem], sort_keys=True, separators=(",", ":")))
        canonical_midi_serialize(str(jd / f"{stem}.json"), str(md / f"{stem}.mid"), float(bpm), (4, 4))
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
        if not events[stem]:  # empty stem (e.g. all-N chords): silent 16 bars, no render
            sr0 = 44100
            write_wav_int16(wav, np.zeros((int(sr0 * 16 * 4 * 60.0 / bpm), 2), dtype=np.float32), sr0)
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
    man = {"schema_version": 1, "cycle": 84, "run_id": "run-2026-09-06T000000Z", "agent": "worker", "milestone": "M-V5-GEN-1/iteration-01-c84",
           "generated_song_id": gen_id, "donor_song_sha16": donor, "donor_song_name": spec.get("donor_song_name"), "seed": seed, "seed_str": tag,
           "generator": "groove_first_v5", "generator_hash": _sha(Path(__file__)), "rules_sha256": rules_sha,
           "tempo_bpm": bpm, "tempo_source": tempo_src, "tonic": tonic, "tonic_source": tonic_src,
           "form_plan": list(FORM_PLAN), "bars_per_section": BARS_PER_SECTION, "n_bars": len(bars),
           "section_chords": sec_chords, "chord_sequence": chords, "section_grooves": sec_bars,
           "midi_sha256": midi_sha, "per_track_wav_sha256": wav_sha, "per_track_deleted_after_mix": deleted, "gains": gains,
           "target_rms_dbfs": TARGET_RMS_DB, "profiles_used": profiles_used, "shims_disclosed": SHIMS,
           "donor_bass_profile_relpath": spec["donor_bass_profile_relpath"], "donor_drums_profile_relpath": spec.get("donor_drums_profile_relpath"),
           "ab_mix_sha256": _sha(out_wav), "ab_mix_duration_s": round(len(mix) / sr, 4), "sample_rate": sr,
           "sum_method": "float_accumulate_peaklimit_099_max_len_zero_pad", "env_pin_sha256": ENV_PIN_SHA256, "env_pins": dict(_PINS),
           "ear_score": None, "ear_score_reason": "scored separately by scripts/v5/score_gen_batch_v5.py (informational, FD-6)",
           "sampling": "SHA-256 inverse-CDF on seed_str-derived tags (no PRNG)", "form_repetition": "section A generated once, repeated literally at positions 1, 2, 4"}
    (song_dir / "ab_mix.manifest.json").write_text(json.dumps(man, sort_keys=True, indent=2) + "\n")
    return man


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
    args = ap.parse_args(argv)
    out = Path(args.out or f"data/v5/gen/iteration_{args.iteration:02d}")
    out.mkdir(parents=True, exist_ok=True)
    groove = json.loads(Path(args.groove).read_text())
    chain = json.loads(Path(args.harmony).read_text())
    assert chain["degeneracy_verdict"] == "NON_DEGENERATE", "harmony chain must be NON_DEGENERATE (brief P3 gate)"
    assert groove["verdict"] != "GROOVE_V2_DEGENERATE", "groove model must not be DEGENERATE (brief P3 gate)"
    rules_sha = {"harmony_chain": _sha(Path(args.harmony)), "groove_model": _sha(Path(args.groove)),
                 "harmony_prereg": _sha(Path("data/v5/rules/harmony_prereg_c84.json")), "groove_prereg": _sha(Path("data/v5/rules/groove_prereg_c84.json")),
                 "donor_map": _sha(Path(args.donor_map))}
    specs = json.loads(Path(args.donor_map).read_text())["songs"][: args.songs]
    corpus = Path(args.corpus_dir)
    rollup = {"schema_version": 1, "cycle": 84, "agent": "worker", "run_id": "run-2026-09-06T000000Z", "iteration": args.iteration, "seed": args.seed,
              "generator": "groove_first_v5", "generator_hash": _sha(Path(__file__)), "rules_sha256": rules_sha, "env_pin_sha256": ENV_PIN_SHA256,
              "harmony_verdict": chain["degeneracy_verdict"], "groove_verdict": groove["verdict"],
              "groove_overfits_disclosed": groove["verdict"] == "GROOVE_V2_OVERFITS", "songs": []}
    for spec in specs:
        man = render_song(spec, args.seed, out, groove, chain, corpus, args.keep_per_track, rules_sha)
        entry = {"generated_song_id": man["generated_song_id"], "donor": man["donor_song_sha16"], "ab_mix_sha256": man["ab_mix_sha256"],
                 "duration_s": man["ab_mix_duration_s"], "chords": man["chord_sequence"]}
        print(f"{man['generated_song_id']} donor={man['donor_song_sha16']} bpm={man['tempo_bpm']:.2f} tonic={man['tonic']} sha={man['ab_mix_sha256'][:12]} dur={man['ab_mix_duration_s']}s")
        if args.prove_replay:
            with tempfile.TemporaryDirectory(prefix="gen_v5_replay_") as td:
                man2 = render_song(spec, args.seed, Path(td), groove, chain, corpus, False, rules_sha)
            proof = {"verdict": "REPLAY_PROOF_HOLDS" if man2["ab_mix_sha256"] == man["ab_mix_sha256"] else "REPLAY_PROOF_FAILS",
                     "run1_sha256": man["ab_mix_sha256"], "run2_sha256": man2["ab_mix_sha256"], "run2_midi_equal": man2["midi_sha256"] == man["midi_sha256"],
                     "run2_per_track_equal": man2["per_track_wav_sha256"] == man["per_track_wav_sha256"], "env_pin_sha256": ENV_PIN_SHA256, "cycle": 84, "agent": "worker"}
            (out / f"{man['generated_song_id']}_donor_{man['donor_song_sha16']}" / "ab_mix.replay_proof.json").write_text(json.dumps(proof, sort_keys=True, indent=2) + "\n")
            entry["replay_proof"] = proof["verdict"]
            print(f"  {proof['verdict']}")
        rollup["songs"].append(entry)
    (out / "iteration_rollup.json").write_text(json.dumps(rollup, sort_keys=True, indent=2) + "\n")
    if not args.no_stall_update:
        sc_p = Path("data/v5/gen/stall_counter.json")
        sc = json.loads(sc_p.read_text())
        sc["iterations"] = max(int(sc.get("iterations", 0)), args.iteration)
        sc.setdefault("history", []).append({"iteration": args.iteration, "cycle": 84, "seed": args.seed, "n_songs": len(specs),
                                             "passers_declared": 0, "note": "ear scores informational under FD-6 (c76 L119 proof); no passer declared"})
        sc_p.write_text(json.dumps(sc, indent=2) + "\n")
        print(f"stall counter {sc['iterations']}/{sc['budget']}")
    shutil.copy(Path(args.groove), out / "groove_model_used.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
