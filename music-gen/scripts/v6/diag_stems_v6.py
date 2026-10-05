#!/usr/bin/python3
"""v6 Phase 5 (iteration 05) — gap localisation by INSTRUMENT GROUP and the MIX-CHAIN ORACLE (docs/v6_iteration_05_diagnostics.md).

created: 2026-10-05
milestone: M-V6-ITER-05/localize

  diag_stems_v6.py render-stems --iteration-dir data/v6/gen/iteration_04_corpus --out <scratch>/it04_stems
      re-renders every song of an iteration with render_song(keep_stems=True) into <out>/<song>/stems/{drums,bass,other}.wav
      (mix.STEM_GROUP; the mix is re-rendered too and its sha256 is asserted equal to the iteration's render_manifest, then
      deleted — a replay check for free). Resumable.
  diag_stems_v6.py score-stems --stems-dir <scratch>/it04_stems [--backbones clap] [--splits 10]
      PER-STEM DISTRIBUTION SCORING: candidate group stems, FORMAT-MATCHED to the corpus Demucs stems (22.05 kHz mono), vs the real
      stems data/v6/stems/<donor>/<kind>.wav of all donors; plus the real stems' own split-half floor per kind. Pre-registered
      ranking rule: gap ratio = kid_song(cand vs real) / p97.5(split-half kid_song of the real stems); the group with the largest
      ratio is the farthest from real. c2st, coverage and kNN-real are reported next to their floor means.
  diag_stems_v6.py oracle --out <scratch>/oracle [--backbones clap,mert] [--splits 10]
      MIX-CHAIN ORACLE (upper bound): the REAL corpus stems (drums, bass, other -> role keys) re-mixed through OUR chain
      (render_v6/mix.py mix_song, 44.1 kHz stereo), format-matched back to 22.05 kHz mono and scored against corpus_accomp with the
      split protocol: oracle(half A) vs real(half B) over the same deterministic splits as real(A) vs real(B). Pre-registered
      verdict: the chain is a gap (FLAG) when the oracle's mean kid_song exceeds the real-vs-real p97.5 of the same splits AND its
      mean c2st exceeds the corpus_accomp gate threshold (gates_v6.json references.corpus_accomp); otherwise the chain is not the
      problem. Novelty is not applicable (the oracle IS the reference music; halves are disjoint by song).

Discipline: /usr/bin/python3 guard (through the imported modules); sorted-key atomic JSON; seeds explicit; writes audio only
under the given scratch --out (never under data/); embeddings sha-cached under data/v6/embeddings.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402

from scripts.v6 import diag_common as dc  # noqa: E402
from scripts.v6 import scorecard as sc  # noqa: E402
from scripts.v6 import scorecard_format as scf  # noqa: E402
from scripts.v6.v6_common import env_record, read_json, sha16_of, sha256_file, write_json_atomic  # noqa: E402

KINDS = ("drums", "bass", "other")
ORACLE_ROLE = {"drums": "drums", "bass": "bass", "other": "keys"}
DEFAULT_STEMS_ROOT = _WS / "data" / "v6" / "stems"
DEFAULT_ACCOMP_MANIFEST = _WS / "data" / "v6" / "public" / "corpus_accomp" / "manifest.json"
DEFAULT_GATES = _WS / "data" / "v6" / "scorecard" / "gates_v6.json"
DEFAULT_EMB_DIR = _WS / "data" / "v6" / "embeddings"
DEFAULT_FMT_CACHE = _WS / "data" / "v6" / "scorecard" / "format_cache"
SR = 44100


def _log(msg):
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


# ============================================================================= render-stems
def render_stems(iteration_dir: Path, out: Path, log=_log) -> dict:
    from scripts.v6.gen.render_v6 import render_song, select
    pool = select.load_pool()
    out.mkdir(parents=True, exist_ok=True)
    man_path = out / "render_stems_manifest.json"
    man = read_json(man_path) if man_path.exists() else {"schema_version": dc.SCHEMA_VERSION, "iteration_dir": str(iteration_dir), "songs": {}}
    dirs = sorted([d for d in iteration_dir.iterdir() if d.is_dir() and (d / "render_manifest.json").exists()], key=lambda d: int(d.name.split("_")[3]))
    for sd in dirs:
        rm = read_json(sd / "render_manifest.json")
        so = out / sd.name
        if sd.name in man["songs"] and all((so / "stems" / f"{k}.wav").exists() for k in man["songs"][sd.name]["stems"]):
            log(f"[render-stems] {sd.name} resumed")
            continue
        t0 = time.time()
        m = render_song.render_song(sd, rm["donor"], iteration=int(rm["iteration"]), seed=int(rm["seed"]), out_dir=so, band=rm.get("band"), pool=pool, keep_stems=True, log=lambda *a: None)
        same = m["ab_mix_sha256"] == rm["ab_mix_sha256"]
        for junk in ("ab_mix.wav",):
            (so / junk).unlink(missing_ok=True)
        for p in (so / "render_midi").glob("*"):
            p.unlink()
        man["songs"][sd.name] = {"donor": rm["donor"], "song_id": rm["song_id"], "replay_mix_equal": same, "stems": {k: dict(v, path=str(so / v["path"])) for k, v in m["stems_kept"].items()},
                                 "ensemble": m["ensemble"], "wall_s": round(time.time() - t0, 1)}
        log(f"[render-stems] {sd.name} groups={sorted(m['stems_kept'])} mix_replay_equal={same} {time.time() - t0:.0f}s")
        write_json_atomic(man_path, man)
    man["n_songs"] = len(man["songs"])
    man["all_replay_equal"] = all(v["replay_mix_equal"] for v in man["songs"].values())
    write_json_atomic(man_path, man)
    return man


# ============================================================================= score-stems
def real_stem_items(stems_root: Path, kind: str) -> list:
    man = read_json(stems_root / "manifest.json")
    items = []
    for sha, s in sorted(man["songs"].items()):
        p = stems_root / sha / f"{kind}.wav"
        if p.exists():
            items.append({"path": str(p), "sha16": sha16_of(sha256_file(p)), "label": f"{s.get('title') or sha}|{kind}", "source_sha16": sha})
    return items


def score_stems(stems_dir: Path, stems_root: Path, backbones: list, emb_dir: Path, fmt_cache: Path, out: Path, splits: int, seed: int, k: int, log=_log) -> dict:
    rep = {"schema_version": dc.SCHEMA_VERSION, "stems_dir": str(stems_dir), "stems_root": str(stems_root), "backbones": backbones, "splits": splits, "seed": seed, "k": k,
           "rule": "gap ratio = kid_song(candidate group vs real group) / p97.5(split-half kid_song of the real group); ranked descending; "
                   "c2st / coverage / kNN-real shown next to the floor means. Pre-registered before measurement (iteration 05).",
           "kinds": {}, "env": env_record()}
    for kind in KINDS:
        cand_src = sorted(stems_dir.glob(f"*/stems/{kind}.wav"))
        if not cand_src:
            rep["kinds"][kind] = {"error": "no candidate stems"}
            continue
        ref_items = real_stem_items(stems_root, kind)
        fmt = scf.reference_format(ref_items)
        cand_items, fmt_block = scf.match_items([{"path": str(p), "sha16": sha16_of(sha256_file(p)), "label": f"{p.parent.parent.name}|{kind}"} for p in cand_src], fmt, fmt_cache, log)
        block = {"n_candidates": len(cand_items), "n_reference": len(ref_items), "format": fmt, "n_transformed": fmt_block["n_transformed"], "backbones": {}}
        for bb in backbones:
            tag = f"stem={kind}"
            cands = dc.embed_set([c["path"] for c in cand_items], bb, emb_dir, log, tag=tag, labels={c["sha16"]: c["label"] for c in cand_items})
            refs = dc.embed_set([r["path"] for r in ref_items], bb, emb_dir, log, tag=tag, labels={r["sha16"]: r["label"] for r in ref_items})
            flat = dc.score(cands, refs, seed=seed, k=k, backbone=bb)
            floor = dc.split_half_floor(refs, splits, seed, k, bb)
            fa = floor["aggregate"]
            block["backbones"][bb] = {"candidate_vs_real": flat, "floor": floor,
                                      "gap_ratio_kid": dc.ratio_to_floor(flat["kid_song"], fa["kid_song"], "p97_5"),
                                      "c2st_minus_floor_mean": flat["c2st_balanced_accuracy"] - fa["c2st_balanced_accuracy"]["mean"],
                                      "coverage_over_floor_mean": dc.ratio_to_floor(flat["coverage"], fa["coverage"], "mean"),
                                      "knn_real_over_floor_mean": dc.ratio_to_floor(flat["knn_real_fraction"], fa["knn_real_fraction"], "mean")}
            log(f"[score-stems:{bb}] {kind}: kid {flat['kid_song']:.3g} (floor p97.5 {fa['kid_song'].get('p97_5', float('nan')):.3g}) ratio {block['backbones'][bb]['gap_ratio_kid']} "
                f"c2st {flat['c2st_balanced_accuracy']:.3f} cov {flat['coverage']:.3f} knn {flat['knn_real_fraction']:.3f}")
        rep["kinds"][kind] = block
    rep["ranking"] = {bb: sorted([(kind, rep["kinds"][kind]["backbones"][bb]["gap_ratio_kid"]) for kind in rep["kinds"] if "backbones" in rep["kinds"][kind] and bb in rep["kinds"][kind]["backbones"]],
                               key=lambda t: -(t[1] if t[1] is not None else -1)) for bb in backbones}
    out.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out / "stems_diagnostic.json", rep)
    (out / "STEMS.md").write_text(stems_markdown(rep), encoding="utf-8")
    return rep


def stems_markdown(rep: dict) -> str:
    L = [f"# Per-stem distribution scoring ({', '.join(rep['backbones'])}; real-stem floor from {rep['splits']} split halves)", "", rep["rule"], ""]
    for bb in rep["backbones"]:
        rows = []
        for kind, _ in rep["ranking"][bb]:
            b = rep["kinds"][kind]["backbones"][bb]
            f, fa = b["candidate_vs_real"], b["floor"]["aggregate"]
            rows.append([kind, f["kid_song"], fa["kid_song"].get("p97_5"), b["gap_ratio_kid"], f["c2st_balanced_accuracy"], fa["c2st_balanced_accuracy"].get("mean"),
                         f["coverage"], fa["coverage"].get("mean"), f["knn_real_fraction"], f["knn_real_fraction_null"], fa["knn_real_fraction"].get("mean"), f"{f['n_windows_a']}/{f['n_windows_b']}"])
        L += [f"## {bb}", "", dc.md_table(["group", "kid_song", "floor p97.5", "gap ratio", "c2st", "floor c2st", "coverage", "floor cov", "kNN-real", "null", "floor kNN", "windows c/r"], rows)]
    return "\n".join(L)


# ============================================================================= oracle
def _load_mono(path: Path):
    import soundfile as sf
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    return x.mean(axis=1), sr


def oracle_mix_one(stems_root: Path, donor: str, band: int, bpm: float, out_wav: Path) -> dict:
    """Real stems (22.05 kHz mono) -> 44.1 kHz, duplicated to stereo -> mix.mix_song as drums / bass / keys(other) -> 16-bit master."""
    from scripts.v6.gen.render import write_wav_int16
    from scripts.v6.gen.render_v6 import mix
    stems = {}
    for kind in KINDS:
        x, sr = _load_mono(stems_root / donor / f"{kind}.wav")
        y = scf.transform_audio(x, sr, SR, 2)
        stems[ORACLE_ROLE[kind]] = y
    master, mman = mix.mix_song(stems, SR, int(band), False, float(bpm), 0.1)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    write_wav_int16(out_wav, master, SR)
    return {"donor": donor, "band": int(band), "bpm": float(bpm), "roles": {k: ORACLE_ROLE[k] for k in KINDS}, "path": str(out_wav), "sha256": sha256_file(out_wav),
            "master": {k: mman["master"][k] for k in ("lufs_final", "true_peak_dbtp_final", "crest_factor_db_final", "spectral_tilt_db_final", "tilt_shelf_gain_db")},
            "per_stem_gain_db": {r: mman["per_stem"][r]["gain_db"] for r in mman["per_stem"]}}


def oracle(stems_root: Path, accomp_manifest: Path, out: Path, diag_out: Path, backbones: list, emb_dir: Path, fmt_cache: Path, gates_path: Path, splits: int, seed: int, k: int,
           log=_log, mix_only: bool = False) -> dict:
    from scripts.v6.gen.compose_v6 import donor_bpm
    acc = read_json(accomp_manifest)
    out.mkdir(parents=True, exist_ok=True)
    mix_man_path = out / "oracle_mixes.json"
    mixes = read_json(mix_man_path) if mix_man_path.exists() else {"schema_version": dc.SCHEMA_VERSION, "songs": {}}
    for donor, s in sorted(acc["songs"].items()):
        wav = out / f"{donor}.wav"
        if donor in mixes["songs"] and wav.exists() and sha256_file(wav) == mixes["songs"][donor]["sha256"]:
            continue
        bpm, src = donor_bpm(donor, 0, [], _WS / "data" / "v5" / "corpus")
        t0 = time.time()
        mixes["songs"][donor] = dict(oracle_mix_one(stems_root, donor, int(s.get("band") or 5), bpm, wav), bpm_source=src, wall_s=round(time.time() - t0, 1))
        log(f"[oracle] mixed {donor} band={s.get('band')} bpm={bpm:.1f} LUFS={mixes['songs'][donor]['master']['lufs_final']} {time.time() - t0:.0f}s")
        write_json_atomic(mix_man_path, mixes)
    donors = sorted(acc["songs"])
    if mix_only:
        return mixes
    ref_items = [{"path": str(_WS / acc["songs"][d]["path"]) if not Path(acc["songs"][d]["path"]).is_absolute() else acc["songs"][d]["path"], "sha16": acc["songs"][d]["sha16"], "label": d} for d in donors]
    fmt = scf.reference_format(ref_items)
    ora_items, fmt_block = scf.match_items([{"path": mixes["songs"][d]["path"], "sha16": sha16_of(mixes["songs"][d]["sha256"]), "label": d} for d in donors], fmt, fmt_cache, log)
    gates = sc.load_gates(gates_path)
    gbb, gkey = sc.gates_for_reference(gates, "corpus_accomp")
    rep = {"schema_version": dc.SCHEMA_VERSION, "n_songs": len(donors), "splits": splits, "seed": seed, "k": k, "format": fmt, "gates_key": gkey, "mixes": str(mix_man_path),
           "rule": "oracle(half A) vs real(half B) over the same deterministic splits as real(A) vs real(B); FLAG (chain is a gap) when mean oracle kid_song > p97.5 of the "
                   "real-vs-real kid_song over these splits AND mean oracle c2st > the corpus_accomp c2st gate; otherwise the mix chain is not the problem.", "backbones": {}, "env": env_record()}
    for bb in backbones:
        ora = dc.embed_set([o["path"] for o in ora_items], bb, emb_dir, log, labels={o["sha16"]: o["label"] for o in ora_items})
        real = dc.embed_set([r["path"] for r in ref_items], bb, emb_dir, log, labels={r["sha16"]: r["label"] for r in ref_items})
        by_label_o, by_label_r = {s.song_id: s for s in ora}, {s.song_id: s for s in real}
        common = [d for d in donors if d in by_label_o and d in by_label_r]
        per_split = []
        for i, (ia, ib) in enumerate(dc.deterministic_halves(len(common), splits, seed)):
            A_real, B_real = [by_label_r[common[j]] for j in ia], [by_label_r[common[j]] for j in ib]
            A_ora = [by_label_o[common[j]] for j in ia]
            fo = dc.score(A_ora, B_real, seed=seed + i, k=k, n_boot=0, subsets=20, backbone=bb)
            fr = dc.score(A_real, B_real, seed=seed + i, k=k, n_boot=0, subsets=20, backbone=bb)
            per_split.append({"split": i, "oracle_vs_real": fo, "real_vs_real": fr})
        agg_o = {m: dc.agg([p["oracle_vs_real"].get(m) for p in per_split]) for m in dc.FLOOR_METRICS}
        agg_r = {m: dc.agg([p["real_vs_real"].get(m) for p in per_split]) for m in dc.FLOOR_METRICS}
        c2_thr = gbb[bb]["c2st_balanced_accuracy"]["threshold"]
        kid_flag = agg_o["kid_song"]["mean"] > agg_r["kid_song"]["p97_5"]
        c2_flag = agg_o["c2st_balanced_accuracy"]["mean"] > c2_thr
        rep["backbones"][bb] = {"n_common_songs": len(common), "per_split": per_split, "oracle": agg_o, "real_vs_real": agg_r, "c2st_gate": c2_thr,
                                "kid_above_floor_p97_5": bool(kid_flag), "c2st_above_gate": bool(c2_flag), "verdict": "FLAG" if (kid_flag and c2_flag) else "PASS",
                                "kid_ratio_to_floor_p97_5": dc.ratio_to_floor(agg_o["kid_song"]["mean"], agg_r["kid_song"], "p97_5"),
                                "coverage_ratio_to_floor_mean": dc.ratio_to_floor(agg_o["coverage"]["mean"], agg_r["coverage"], "mean")}
        log(f"[oracle:{bb}] kid {agg_o['kid_song']['mean']:.3g} vs floor p97.5 {agg_r['kid_song']['p97_5']:.3g}; c2st {agg_o['c2st_balanced_accuracy']['mean']:.3f} (gate {c2_thr}, floor "
            f"{agg_r['c2st_balanced_accuracy']['mean']:.3f}); coverage {agg_o['coverage']['mean']:.3f} vs {agg_r['coverage']['mean']:.3f} -> {rep['backbones'][bb]['verdict']}")
    diag_out.mkdir(parents=True, exist_ok=True)
    write_json_atomic(diag_out / "oracle_diagnostic.json", rep)
    (diag_out / "ORACLE.md").write_text(oracle_markdown(rep), encoding="utf-8")
    return rep


def oracle_markdown(rep: dict) -> str:
    L = [f"# Mix-chain oracle: real corpus stems through render_v6/mix.py vs corpus_accomp ({rep['n_songs']} songs, {rep['splits']} splits)", "", rep["rule"], ""]
    rows = []
    for bb, b in rep["backbones"].items():
        o, r = b["oracle"], b["real_vs_real"]
        rows.append([bb, o["kid_song"]["mean"], r["kid_song"]["mean"], r["kid_song"]["p97_5"], b["kid_ratio_to_floor_p97_5"], o["c2st_balanced_accuracy"]["mean"], r["c2st_balanced_accuracy"]["mean"],
                     b["c2st_gate"], o["coverage"]["mean"], r["coverage"]["mean"], o["knn_real_fraction"]["mean"], r["knn_real_fraction"]["mean"], b["verdict"]])
    L.append(dc.md_table(["backbone", "oracle kid", "real kid mean", "real kid p97.5", "kid ratio", "oracle c2st", "real c2st", "c2st gate", "oracle cov", "real cov", "oracle kNN", "real kNN", "verdict"], rows))
    return "\n".join(L)


# ============================================================================= CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render-stems")
    r.add_argument("--iteration-dir", required=True)
    r.add_argument("--out", required=True)
    s = sub.add_parser("score-stems")
    s.add_argument("--stems-dir", required=True)
    s.add_argument("--out", default=str(dc.DIAG_DIR / "iteration_05" / "stems"))
    o = sub.add_parser("oracle")
    o.add_argument("--out", required=True, help="scratch dir for the oracle mixes (audio; never under data/)")
    o.add_argument("--diag-out", default=str(dc.DIAG_DIR / "iteration_05" / "oracle"))
    o.add_argument("--accomp-manifest", default=str(DEFAULT_ACCOMP_MANIFEST))
    o.add_argument("--gates", default=str(DEFAULT_GATES))
    o.add_argument("--mix-only", action="store_true", help="only (re)build the oracle mixes (no embedding / scoring)")
    for p in (s, o):
        p.add_argument("--stems-root", default=str(DEFAULT_STEMS_ROOT))
        p.add_argument("--backbones", default="clap")
        p.add_argument("--emb-dir", default=str(DEFAULT_EMB_DIR))
        p.add_argument("--format-cache", default=str(DEFAULT_FMT_CACHE))
        p.add_argument("--splits", type=int, default=10)
        p.add_argument("--seed", type=int, default=0)
        p.add_argument("--k", type=int, default=5)
    a = ap.parse_args(argv)
    if a.cmd == "render-stems":
        man = render_stems(Path(a.iteration_dir), Path(a.out))
        _log(f"render-stems: {man['n_songs']} songs, all_replay_equal={man['all_replay_equal']}")
        return 0 if man["all_replay_equal"] else 3
    bbs = [b.strip() for b in a.backbones.split(",") if b.strip()]
    if a.cmd == "score-stems":
        score_stems(Path(a.stems_dir), Path(a.stems_root), bbs, Path(a.emb_dir), Path(a.format_cache), Path(a.out), a.splits, a.seed, a.k)
        return 0
    oracle(Path(a.stems_root), Path(a.accomp_manifest), Path(a.out), Path(a.diag_out), bbs, Path(a.emb_dir), Path(a.format_cache), Path(a.gates), a.splits, a.seed, a.k, mix_only=a.mix_only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
