#!/usr/bin/python3
"""v6 Phase 4 — render_song: composed song dir -> timbre-matched multi-patch stems -> mixed/mastered ab_mix.wav (+ manifests).

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

    /usr/bin/python3 scripts/v6/gen/render_v6/render_song.py --song-dir <dir with generated_json/ + plan.json> --donor <sha16>
        [--out <dir>] [--iteration 1] [--seed 0] [--band 5] [--temperature 0.05] [--keep-per-track] [--keep-stems] [--prove-replay] [--pool PATH]

Pipeline (all deterministic for sfz/sf2 patches): plan_patches (ensemble + patch per role, patch_plan.json) -> composer
events (generated_json/<stem>.json, humanized_json/<stem>.json preferred when present) paired into notes -> derived parts
(pad / comp_guitar / percussion, parts.py) -> expression (velocity curves, CC11/CC1 swells, CC64 pedal) -> 480-PPQ MIDI
per role (render_midi/<role>.mid) -> backends.render_stem (per_track/<role>.wav, deleted unless --keep-per-track) ->
mix.mix_song (per-stem HPF/comp/placement, reverb bus, bus comp, tilt steer, loudness to the corpus-derived target,
true-peak limit) -> ab_mix.wav (16-bit stereo) + mix_manifest.json + render_manifest.json. --prove-replay renders the whole
song a second time into a mkdtemp and asserts byte identity of every stem WAV and the mix (ab_mix.replay_proof.json).
compose_v6.py --renderer v6 calls render_song(); the GM renderer (scripts/v6/gen/render.py) is untouched.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

_WS = Path(__file__).resolve().parents[4]
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.gen.common import ENV_PIN_SHA256, WS, read_json, sha_file, write_json_atomic  # noqa: E402  (env pins + interpreter guard)
from scripts.v6.gen.render_v6 import backends, expression, midi_io, mix, parts, select  # noqa: E402

COMPOSED_ROLES = ("drums", "bass", "keys", "melody")
SR = 44100


def load_events(song_dir: Path, stem: str) -> list:
    for sub in ("humanized_json", "generated_json"):
        p = song_dir / sub / f"{stem}.json"
        if p.exists():
            return read_json(p)
    return []


def _read_stem(path: Path):
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    if sr != SR:
        import librosa
        x = librosa.resample(x.T, orig_sr=sr, target_sr=SR, res_type="soxr_hq").T.astype(np.float32)
    return x


def render_song(song_dir: Path, donor: str, iteration: int = 1, seed: int = 0, out_dir: Path | None = None, band: int | None = None, temperature: float = select.DEFAULT_TEMPERATURE,
                keep_per_track: bool = False, pool: dict | None = None, stems_root: Path = select.STEMS_ROOT, log=print, mix_name: str = "ab_mix.wav", keep_stems: bool = False) -> dict:
    """Returns the render manifest (also written as <out>/render_manifest.json). keep_stems (iteration 05 diagnostics): also write
    the mastered Demucs-style groups <out>/stems/{drums,bass,other}.wav (mix.STEM_GROUP; 16-bit stereo at SR) — the mix is unchanged."""
    from scripts.v6.gen.render import write_wav_int16
    t_all = time.time()
    song_dir = Path(song_dir)
    out = Path(out_dir) if out_dir else song_dir
    out.mkdir(parents=True, exist_ok=True)
    plan = read_json(song_dir / "plan.json")
    bpm, n_bars = float(plan["tempo_bpm"]), int(plan["form"]["n_bars"])
    song_len_s = n_bars * 4 * 60.0 / bpm
    song_id = plan.get("song_id", song_dir.name)
    pool = pool or select.load_pool()
    pp = select.plan_patches(song_id, donor, iteration, seed, pool, band, stems_root, temperature, log=log)
    write_json_atomic(out / "patch_plan.json", pp)
    tag = pp["tag"]
    notes_by_role = {r: midi_io.pair_events(load_events(song_dir, r)) for r in COMPOSED_ROLES}
    roles = pp["selection"]
    if "pad" in roles:
        notes_by_role["pad"] = parts.pad_part(plan, bpm)
    if "comp_guitar" in roles:
        notes_by_role["comp_guitar"] = parts.comp_guitar_part(notes_by_role["keys"], plan, bpm, tag)
    if "percussion" in roles:
        notes_by_role["percussion"] = parts.percussion_part(plan, bpm, pool["patches"][roles["percussion"]["patch_id"]], tag)
    midi_dir, pt_dir = out / "render_midi", out / "per_track"
    stems, per_role = {}, {}
    for role in sorted(roles):
        patch = pool["patches"][roles[role]["patch_id"]]
        notes = notes_by_role.get(role, [])
        if not notes:
            per_role[role] = {"patch_id": patch["id"], "n_notes": 0, "skipped": "no notes"}
            continue
        t0 = time.time()
        notes2, ccs, xinfo = expression.apply(notes, role, patch, tag, bpm, plan, song_len_s)
        mid = midi_dir / f"{role}.mid"
        minfo = midi_io.write_midi(notes2, mid, bpm, channel=backends.midi_channel_for(patch, role), program=patch.get("program") if patch["backend"] == "sf2" else None,
                                   bank=patch.get("bank") if patch["backend"] == "sf2" else None, ccs=ccs, song_len_s=song_len_s)
        wav = pt_dir / f"{role}.wav"
        rinfo = backends.render_stem(mid, patch, wav, SR)
        stems[role] = _read_stem(wav)
        per_role[role] = {"patch_id": patch["id"], "patch_name": patch["name"], "backend": patch["backend"], "midi": str(mid.relative_to(out)), "midi_sha256": sha_file(mid), "midi_info": minfo,
                          "expression": xinfo, "render": rinfo, "stem_wav_sha256": rinfo["wav_sha256"], "stem_duration_s": round(stems[role].shape[0] / SR, 4), "wall_s": round(time.time() - t0, 3)}
        log(f"[render_v6] {song_id} {role:12} {patch['id'][:48]:48} notes={len(notes2)} vel={xinfo['velocity']['realized_range']} cc={xinfo['cc']['n_cc']} {per_role[role]['wall_s']}s")
    t_mix = time.time()
    groups = {} if keep_stems else None
    master, mman = mix.mix_song(stems, SR, pp["band"], bool(plan.get("ballad")), bpm, pp["ensemble"]["melody_pan"], length_s=song_len_s + 1.5, groups=groups, tag=tag)
    mix_path = out / mix_name
    write_wav_int16(mix_path, master, SR)
    mman.update({"song_id": song_id, "donor": donor, "ab_mix": mix_path.name, "ab_mix_sha256": sha_file(mix_path), "wall_s": round(time.time() - t_mix, 3)})
    kept_stems = {}
    if keep_stems:
        (out / "stems").mkdir(parents=True, exist_ok=True)
        for g in sorted(groups):
            gp = out / "stems" / f"{g}.wav"
            write_wav_int16(gp, groups[g], SR)
            kept_stems[g] = {"path": str(gp.relative_to(out)), "sha256": sha_file(gp), "roles": sorted(r for r in stems if mix.STEM_GROUP.get(r, "other") == g)}
        mman["stems_kept"] = kept_stems
    write_json_atomic(out / "mix_manifest.json", mman)
    deleted = []
    if not keep_per_track:
        for p in sorted(pt_dir.glob("*.wav")):
            deleted.append(p.name)
            p.unlink()
        if pt_dir.exists() and not any(pt_dir.iterdir()):
            pt_dir.rmdir()
    man = {"schema_version": 1, "renderer": "render_v6", "song_id": song_id, "donor": donor, "iteration": iteration, "seed": seed, "band": pp["band"], "tempo_bpm": bpm, "n_bars": n_bars,
           "song_len_s": round(song_len_s, 4), "sample_rate": SR, "roles": per_role, "ensemble": pp["ensemble"]["roles"], "melody_family": pp["ensemble"]["melody_family"],
           "ab_mix": mix_path.name, "ab_mix_sha256": mman["ab_mix_sha256"], "ab_mix_duration_s": mman["duration_s"], "mix_master": mman["master"], "per_track_deleted_after_mix": deleted,
           "stems_kept": kept_stems, "iteration_05": {"comp_keep_p": parts.COMP_KEEP_P, "ensemble_p": dict(select.ENSEMBLE_P), "kit_family_first": select.KIT_FAMILY_FIRST,
                                                     "tilt_steer": dict(mix.TILT_STEER), "song_variation": dict(mix.SONG_VARIATION)},
           "pool_sha256": pool.get("_sha256"), "deterministic_backends_only": all(per_role[r].get("backend") in ("sfz", "sf2") for r in per_role if "backend" in per_role[r]),
           "env_pin_sha256": ENV_PIN_SHA256, "wall_s": round(time.time() - t_all, 3)}
    write_json_atomic(out / "render_manifest.json", man)
    return man


def prove_replay(song_dir: Path, donor: str, man: dict, out: Path, **kw) -> dict:
    with tempfile.TemporaryDirectory(prefix="render_v6_replay_") as td:
        man2 = render_song(song_dir, donor, out_dir=Path(td), keep_per_track=False, log=lambda *a: None, **kw)
    stems = {r: (man["roles"][r].get("stem_wav_sha256"), man2["roles"][r].get("stem_wav_sha256")) for r in man["roles"]}
    equal = {"stems": {r: a == b for r, (a, b) in stems.items()}, "mix": man["ab_mix_sha256"] == man2["ab_mix_sha256"],
             "midi": {r: man["roles"][r].get("midi_sha256") == man2["roles"][r].get("midi_sha256") for r in man["roles"]}}
    ok = equal["mix"] and all(equal["stems"].values()) and all(equal["midi"].values())
    proof = {"schema_version": 1, "verdict": "REPLAY_PROOF_HOLDS" if ok else "REPLAY_PROOF_FAILS", "equal": equal, "run1_ab_mix_sha256": man["ab_mix_sha256"], "run2_ab_mix_sha256": man2["ab_mix_sha256"],
             "deterministic_backends_only": man["deterministic_backends_only"], "env_pin_sha256": ENV_PIN_SHA256}
    write_json_atomic(out / "ab_mix.replay_proof.json", proof)
    return proof


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 realistic renderer: song dir -> ab_mix.wav")
    ap.add_argument("--song-dir", required=True)
    ap.add_argument("--donor", required=True, help="donor sha16 (or fixture id)")
    ap.add_argument("--out", default=None, help="output dir (default: the song dir)")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--band", type=int, default=None, help="override the donor's rating band (default: ingest receipts, else 5)")
    ap.add_argument("--temperature", type=float, default=select.DEFAULT_TEMPERATURE)
    ap.add_argument("--pool", default=str(select.POOL_PATH))
    ap.add_argument("--stems-root", default=str(select.STEMS_ROOT))
    ap.add_argument("--keep-per-track", action="store_true")
    ap.add_argument("--keep-stems", action="store_true", help="also write the mastered drums / bass / other groups to <out>/stems/ (diagnostics)")
    ap.add_argument("--prove-replay", action="store_true")
    args = ap.parse_args(argv)
    sd = Path(args.song_dir)
    sd = sd if sd.is_absolute() else WS / sd
    out = Path(args.out) if args.out else None
    out = (out if out.is_absolute() else WS / out) if out else None
    pool = select.load_pool(Path(args.pool))
    kw = dict(iteration=args.iteration, seed=args.seed, band=args.band, temperature=args.temperature, pool=pool, stems_root=Path(args.stems_root))
    man = render_song(sd, args.donor, out_dir=out, keep_per_track=args.keep_per_track, keep_stems=args.keep_stems, **kw)
    print(f"{man['song_id']} donor={args.donor} band={man['band']} roles={sorted(man['roles'])} mix={man['ab_mix_sha256'][:12]} LUFS={man['mix_master']['lufs_final']} "
          f"TP={man['mix_master']['true_peak_dbtp_final']} wall={man['wall_s']}s")
    if args.prove_replay:
        proof = prove_replay(sd, args.donor, man, out or sd, **kw)
        print(f"  {proof['verdict']} {proof['equal']}")
        return 0 if proof["verdict"] == "REPLAY_PROOF_HOLDS" else 3
    return 0


if __name__ == "__main__":
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    sys.exit(main())
