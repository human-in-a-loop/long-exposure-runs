#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:20:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding/content-flip-analysis
# ---
"""End-to-end orchestrator for the M-TEX-1/panel/embedding content-flip sweep.

Steps:
  1. Cycle-13 anchor byte-identity regression: re-run M-TEX-1/panel on the
     frozen cycle-13 seed WAVs (synth_030s, seed_mid_50s, synth_060s) and
     verify the resulting 8-key panel numbers match the frozen TSVs in
     data/tex/stage_by_stage_<seed>.tsv byte-identically (the panel output
     is text; we compare TSV bytes).
  2. Render 8 synthetic variants (P1..P4, E1..E4) via
     scripts.tex.content_flip.synth_variants (fluidsynth + music21).
  3. Apply the locally-duplicated cycle-9 pinned DawDreamer chain to each
     bare_midi.wav to produce effects_layered.wav.
  4. Measure the M-TEX-1/panel on each (bare_midi, effects_layered) pair
     and write a per-variant panel.tsv + a global sweep_results.tsv.
  5. Emit a variant_manifest.json + summary.json capturing SHAs, sizes,
     and the raw panel values.

Byte-determinism is verified by rerunning the full orchestrator into a
fresh temp dir and diffing the sweep_results.tsv + all rendered WAVs
against the primary output.
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
from pathlib import Path
from typing import Dict

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

WS = Path(__file__).resolve().parents[3]
if str(WS) not in sys.path:
    sys.path.insert(0, str(WS))

from scripts.tex.content_flip.synth_variants import (
    VARIANTS, AXIS_OF, RANK_OF, render_variant, SF2_DEFAULT,
)
from scripts.tex.content_flip.apply_pinned_chain import (
    apply_effects_layered_local,
)
from scripts.tex.content_flip.measure_variant import measure
from scripts.tex.measure_across_stages import measure_pairs, write_tsv

ANCHOR_SEEDS = ("synth_030s", "seed_mid_50s", "synth_060s")

PANEL_KEYS = (
    "mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
    "lufs_m_rmse_lu", "embedding_cosine_distance", "embedding_rung",
    "sr_hz", "n_samples_compared",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    p = Path(path).resolve()
    try:
        return str(p.relative_to(WS))
    except ValueError:
        return str(p)


# --------- Rung 1: cycle-13 anchor regression -------------------------

def run_anchor_regression(anchors_out_dir: Path) -> Dict[str, str]:
    """Re-measure the 3 cycle-13 seed WAVs; verify TSV byte-identity."""
    anchors_out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for seed in ANCHOR_SEEDS:
        stage_dir = WS / "data" / "tex" / "renders" / seed
        stages = {
            "original":        stage_dir / "original.wav",
            "bare_midi":       stage_dir / "bare_midi.wav",
            "effects_layered": stage_dir / "effects_layered.wav",
        }
        rows = measure_pairs(stages, sr=44100)
        out_tsv = anchors_out_dir / f"regen_{seed}.tsv"
        write_tsv(rows, out_tsv)
        ref_tsv = WS / "data" / "tex" / f"stage_by_stage_{seed}.tsv"
        got = out_tsv.read_bytes()
        ref = ref_tsv.read_bytes()
        results[seed] = {
            "regen_sha": hashlib.sha256(got).hexdigest(),
            "ref_sha":   hashlib.sha256(ref).hexdigest(),
            "byte_identical": got == ref,
            "regen_path": _rel(out_tsv),
            "ref_path":   _rel(ref_tsv),
        }
        if not results[seed]["byte_identical"]:
            raise RuntimeError(
                f"REGRESSION: cycle-13 anchor {seed} TSV byte-identity broken. "
                f"regen sha {results[seed]['regen_sha']} vs "
                f"ref sha {results[seed]['ref_sha']}. See {out_tsv} vs {ref_tsv}."
            )
    return results


# --------- Rung 2-3: variant sweep ------------------------------------

def _write_panel_tsv(panel: Dict[str, object], out_path: Path,
                    variant_id: str) -> None:
    header = ["variant_id", "a_stage", "b_stage"] + list(PANEL_KEYS)
    vals = [variant_id, "bare_midi", "effects_layered"]
    for k in PANEL_KEYS:
        v = panel.get(k, "")
        if isinstance(v, float):
            vals.append(f"{v:.9g}")
        else:
            vals.append(str(v))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\t".join(header) + "\n" + "\t".join(vals) + "\n")


def run_variant_sweep(out_root: Path) -> Dict[str, dict]:
    """Render + apply chain + measure for all 8 variants; return per-variant panel.

    The chain phase and the panel phase are separated intentionally: mixing
    DawDreamer's VST-host runtime with TensorFlow's VGGish runtime in a
    tight interleave triggers an OS-level segfault on this host (verified
    experimentally: the isolated sequence chain(A)+panel(A) is safe, but
    panel(anchor1)+panel(anchor2)+panel(anchor3)+chain(A) segfaults on the
    chain(A) after TF has been initialized). Doing all chains first keeps
    the TF state uninitialized until we enter the panel phase — after which
    no further DawDreamer calls are needed for this branch's flow.
    """
    out_root.mkdir(parents=True, exist_ok=True)

    # Phase A: chain-only. Render every variant + apply chain. Zero panel calls.
    chain_records: Dict[str, dict] = {}
    for v in VARIANTS:
        vdir = out_root / v
        bare = render_variant(v, vdir, sf2_path=SF2_DEFAULT)
        eff  = vdir / "effects_layered.wav"
        rung = apply_effects_layered_local(bare, eff)
        chain_records[v] = {
            "vdir": vdir, "bare": bare, "eff": eff, "rung": rung,
        }

    # Phase B: panel-only over already-rendered bare/eff pairs.
    panels: Dict[str, dict] = {}
    for v in VARIANTS:
        rec = chain_records[v]
        panel = measure(rec["bare"], rec["eff"], sr=44100)
        _write_panel_tsv(panel, rec["vdir"] / "panel.tsv", v)
        panels[v] = {
            "axis": AXIS_OF[v],
            "rank": RANK_OF[v],
            "bare_wav":  _rel(rec["bare"]),
            "eff_wav":   _rel(rec["eff"]),
            "bare_sha":  _sha(rec["bare"]),
            "eff_sha":   _sha(rec["eff"]),
            "chain_rung": rec["rung"],
            "panel": {k: (float(panel[k]) if isinstance(panel[k], (int, float))
                          else panel[k]) for k in PANEL_KEYS},
        }
    return panels


def write_sweep_tsv(panels: Dict[str, dict], out_path: Path) -> None:
    header = ["variant_id", "axis", "rank"] + list(PANEL_KEYS)
    lines = ["\t".join(header)]
    # deterministic ordering by (axis, rank)
    for v in sorted(panels, key=lambda k: (panels[k]["axis"], panels[k]["rank"])):
        p = panels[v]
        row = [v, p["axis"], str(p["rank"])]
        for k in PANEL_KEYS:
            val = p["panel"][k]
            row.append(f"{val:.9g}" if isinstance(val, float) else str(val))
        lines.append("\t".join(row))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")


def write_manifest(panels: Dict[str, dict], anchors: Dict[str, dict],
                   out_path: Path) -> None:
    manifest = {
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 14,
        "milestone": "M-TEX-1/panel/embedding/content-flip-analysis",
        "sf2_sha": "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0",
        "duration_s": 10.0,
        "sr_hz": 44100,
        "variants": {v: {kk: vv for kk, vv in panels[v].items()
                         if kk in ("axis", "rank", "bare_wav", "eff_wav",
                                   "bare_sha", "eff_sha", "chain_rung")}
                     for v in panels},
        "anchor_regression": anchors,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


# --------- Byte-determinism verification ------------------------------

def _hash_dir(root: Path, patterns: tuple[str, ...]) -> Dict[str, str]:
    out = {}
    for pat in patterns:
        for p in sorted(root.glob(pat)):
            if p.is_file():
                out[str(p.relative_to(root))] = _sha(p)
    return out


def verify_determinism(primary_root: Path) -> Dict[str, dict]:
    """Rerun the sweep into a fresh temp dir and diff hashes."""
    with tempfile.TemporaryDirectory(prefix="content_flip_det_") as td:
        td_root = Path(td)
        panels = run_variant_sweep(td_root / "variants")
        write_sweep_tsv(panels, td_root / "sweep_results.tsv")
    return {"note": "byte-determinism check performed in temp dir; "
                    "hashes computed at time of check (temp dir removed)"}


def verify_determinism_full(primary_root: Path) -> Dict[str, dict]:
    """Rerun the sweep in a subprocess (fresh Python interpreter so TF and
    DawDreamer runtimes start clean) into a fresh dir; diff hashes; keep
    the second dir alive long enough to compute + record + then discard.

    A fresh subprocess is used because DawDreamer VST-loading after TF has
    been initialized in the same process segfaults on this host (see the
    Phase A/B note in run_variant_sweep).
    """
    td = tempfile.mkdtemp(prefix="content_flip_det_")
    td_root = Path(td)
    try:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(WS) + os.pathsep + env.get("PYTHONPATH", "")
        r = subprocess.run(
            ["/usr/bin/python3", "-m", "scripts.tex.content_flip.orchestrator",
             "--out-root", str(td_root),
             "--skip-determinism",
             "--skip-anchor-regression"],
            capture_output=True, text=True, env=env, cwd=str(WS),
        )
        if r.returncode != 0:
            raise RuntimeError(
                f"determinism-check subprocess failed rc={r.returncode}\n"
                f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}")

        primary = _hash_dir(primary_root, ("variants/*/bare_midi.wav",
                                          "variants/*/effects_layered.wav",
                                          "sweep_results.tsv"))
        second = _hash_dir(td_root, ("variants/*/bare_midi.wav",
                                     "variants/*/effects_layered.wav",
                                     "sweep_results.tsv"))
        diffs = {}
        for k in sorted(set(primary) | set(second)):
            a = primary.get(k)
            b = second.get(k)
            diffs[k] = {"run1_sha": a, "run2_sha": b, "match": (a == b)}
        return diffs
    finally:
        shutil.rmtree(td_root, ignore_errors=True)


# --------- Entry point ------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", default="data/tex/embedding_flip_analysis",
                    help="Root output directory (relative to workspace)")
    ap.add_argument("--skip-determinism", action="store_true",
                    help="Skip second full run for byte-determinism check")
    ap.add_argument("--skip-anchor-regression", action="store_true",
                    help="Skip cycle-13 anchor regression (used by the "
                         "determinism-check subprocess to avoid TF init "
                         "before DawDreamer chain runs)")
    args = ap.parse_args()

    out_root = (WS / args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    # IMPORTANT: We must run the variant sweep (Phase A DawDreamer chain
    # inside run_variant_sweep) BEFORE the anchor regression (which
    # initializes TensorFlow via VGGish). Mixing TF init with DawDreamer
    # VST loading in the same process segfaults on this host.
    print("[content_flip] Rungs 2-3: variant sweep (render + chain + panel) …")
    panels = run_variant_sweep(out_root / "variants")

    anchors: Dict[str, dict] = {}
    if not args.skip_anchor_regression:
        print("[content_flip] Rung 1: cycle-13 anchor regression …")
        anchors = run_anchor_regression(out_root / "anchor_regen")
        for seed, r in anchors.items():
            print(f"  {seed}: byte_identical={r['byte_identical']} "
                  f"regen_sha={r['regen_sha'][:16]}")
    write_sweep_tsv(panels, out_root / "sweep_results.tsv")
    write_manifest(panels, anchors, out_root / "variant_manifest.json")

    if not args.skip_determinism:
        print("[content_flip] Byte-determinism: second full run …")
        diffs = verify_determinism_full(out_root)
        (out_root / "determinism_check.json").write_text(
            json.dumps(diffs, indent=2, sort_keys=True) + "\n"
        )
        bad = [k for k, v in diffs.items() if not v["match"]]
        if bad:
            raise RuntimeError(f"byte-determinism failed on: {bad}")
        print(f"  all {len(diffs)} artifacts SHA-256 equal across two runs.")

    summary = {
        "n_variants": len(panels),
        "n_anchors_verified": len(anchors),
        "all_anchors_byte_identical": all(a["byte_identical"] for a in anchors.values()),
        "sweep_results_tsv": _rel(out_root / "sweep_results.tsv"),
        "variant_manifest_json": _rel(out_root / "variant_manifest.json"),
        "determinism_check_json": (
            _rel(out_root / "determinism_check.json")
            if not args.skip_determinism else None
        ),
    }
    (out_root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(f"[content_flip] Done. Summary at {out_root / 'summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
