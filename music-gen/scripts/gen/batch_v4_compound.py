#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T17:15:00Z
# cycle: 16
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork cc548ca0c2e5)
# milestone: M-GEN-1/batch-v4-compound
# ---
"""Batch-v4 compound composition test: I3 corpus + I4 sampler stacked.

The compound is deliberately shallow: the I4 stratified rejection sampler
runs against the I3-augmented 86-row ledger, and everything downstream of
sampling (coherence gate, assemble, render, score) is the frozen
cycle-13 batch-v2 pipeline reused verbatim through
``scripts.gen.batch_v3_i4.run_batch``.

Reads (read-only):
    data/rules/ledger_i3_dminor.jsonl   -- I3-augmented 86-row source
    data/rules/i3_dminor_manifest.json  -- I3 augmentation manifest

Writes:
    data/gen/batch_v4/
        song_<s>/generated.musicxml
        song_<s>/generated.mid
        song_<s>/bare_midi.wav
        song_<s>/effects_layered.wav
        song_<s>/scoring.json
        song_<s>/coercions.json
        song_<s>/sampling_manifest.json
        song_<s>/rules.json           -- per-rule_type sampled rule ids
        summary.tsv                   -- via batch_v3_i4's writer
        provenance.jsonl              -- via batch_v3_i4's writer, augmented header
        batch_manifest.json           -- compound provenance chain

This driver does NOT modify the I4 sampler or any batch_v3_i4 code and
does NOT touch the source ledger, batch_v2, batch_v3_i3 or batch_v3_i4
directories.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Env pins BEFORE downstream imports pull numpy/torch.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)

# Frozen cycle-13/15 pieces, imported verbatim.
from scripts.gen.batch_v3_i4 import run_batch as _run_i4_batch  # noqa: E402
from scripts.gen.collision_analysis import analyze, write_tsv  # noqa: E402


I3_LEDGER = _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl"
I3_MANIFEST = _REPO / "data" / "rules" / "i3_dminor_manifest.json"
V4_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v4"
I4_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v3_i4"
I3_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v3_i3"
V2_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v2"
SOURCE_LEDGER = _REPO / "data" / "rules" / "ledger.jsonl"

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
SALTS = tuple(range(8))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_ledger_open_mode_assertion() -> None:
    """Prove that no code path in this driver opens the ledgers for write."""
    # Deliberate: raise if either ledger has been mutated relative to manifest.
    m = json.loads(I3_MANIFEST.read_text())
    live_i3 = _sha256(I3_LEDGER)
    if live_i3 != m["augmented_ledger_sha256"]:
        raise AssertionError(
            f"I3-augmented ledger content-hash drift: "
            f"live={live_i3} vs manifest={m['augmented_ledger_sha256']}"
        )
    live_src = _sha256(SOURCE_LEDGER)
    if live_src != m["source_ledger_sha256"]:
        raise AssertionError(
            f"Source ledger content-hash drift: "
            f"live={live_src} vs manifest={m['source_ledger_sha256']}"
        )


def _snapshot_dir_shas(root: Path) -> Dict[str, str]:
    """SHA-256 of every regular file under root, keyed by root-relative path."""
    out: Dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = _sha256(p)
    return out


def _write_rules_json(batch_root: Path) -> None:
    """Emit song_<s>/rules.json per brief §Deliverables."""
    for s in SALTS:
        sm = json.loads((batch_root / f"song_{s}" / "sampling_manifest.json").read_text())
        payload = {
            "salt": s,
            "raw_rule_ids": sm["raw_rule_ids"],
            "coerced_rule_ids": sm["chosen_rule_ids"],
        }
        (batch_root / f"song_{s}" / "rules.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True)
        )


def _load_batch_shas(batch_root: Path) -> Dict[int, Dict[str, str]]:
    """Return {salt: {musicxml, midi, bare_wav, effects_wav}} for a batch dir."""
    m = json.loads((batch_root / "batch_manifest.json").read_text())
    out: Dict[int, Dict[str, str]] = {}
    for row in m["per_song"]:
        s = int(row["salt"])
        out[s] = {
            "musicxml": row["sha"]["musicxml"],
            "midi": row["sha"]["midi"],
            "bare_wav": row["sha"]["bare_wav"],
            "effects_wav": row["sha"]["effects_wav"],
        }
    return out


def _anchor_cross_reference(v4_root: Path) -> Dict:
    """Compare batch-v4 per-song SHAs against I4-only and I3-only anchors."""
    v4 = _load_batch_shas(v4_root)
    i4 = _load_batch_shas(I4_BATCH_ROOT)
    i3 = _load_batch_shas(I3_BATCH_ROOT)

    per_cell: Dict[str, Dict[str, str]] = {}
    counts = {"matches_i4_only": 0, "matches_i3_only": 0,
              "matches_both": 0, "novel": 0}
    for s in SALTS:
        for fk in ("musicxml", "midi", "bare_wav", "effects_wav"):
            key = f"salt_{s}/{fk}"
            v = v4[s][fk]
            eq4 = (v == i4[s][fk])
            eq3 = (v == i3[s][fk])
            if eq4 and eq3:
                cat = "matches_both"
            elif eq4:
                cat = "matches_i4_only"
            elif eq3:
                cat = "matches_i3_only"
            else:
                cat = "novel"
            counts[cat] += 1
            per_cell[key] = {
                "batch_v4_sha256": v,
                "batch_v3_i4_sha256": i4[s][fk],
                "batch_v3_i3_sha256": i3[s][fk],
                "category": cat,
            }
    return {
        "salts": list(SALTS),
        "file_kinds": ["musicxml", "midi", "bare_wav", "effects_wav"],
        "counts": counts,
        "per_cell": per_cell,
    }


def _classify_verdict(collision_pairs_coerced: int, anchor_xref: Dict) -> Dict:
    """Apply the frozen 3-hypothesis rubric from the research brief.

    CONFIRMS_H1: 0 pairs
    CONFIRMS_H0_STRICT: 0 pairs AND ≥1 (salt, file_kind) cell matches_i4_only
                        or matches_both — evidence that stripping augmentation
                        left at least one full-song SHA reproducible
    CONFIRMS_H2: ≥1 pair (with an attribution note for the report to enrich)
    """
    if collision_pairs_coerced >= 1:
        return {
            "verdict": "CONFIRMS_H2",
            "observed_pairs": collision_pairs_coerced,
            "reasoning": (
                "Compound produced at least one pair. Interference between the "
                "corpus-side and algorithmic levers is directly observable. "
                "See §7 of the report for structural attribution."
            ),
        }
    matches_i4_or_both = (anchor_xref["counts"]["matches_i4_only"]
                          + anchor_xref["counts"]["matches_both"])
    if matches_i4_or_both >= 1:
        return {
            "verdict": "CONFIRMS_H0_STRICT",
            "observed_pairs": 0,
            "matches_i4_or_both_cells": matches_i4_or_both,
            "reasoning": (
                f"Zero pairs AND {matches_i4_or_both} of "
                f"{sum(anchor_xref['counts'].values())} (salt, file_kind) cells "
                "reproduce the I4-only anchor byte-identically. The two "
                "interventions are observably orthogonal at N=8: I3's harmonic "
                "expansion did not shift I4's rank-0 pick in any surviving cell."
            ),
        }
    return {
        "verdict": "CONFIRMS_H1",
        "observed_pairs": 0,
        "reasoning": (
            "Zero pairs; no I4-only cells reproduce byte-identically. I3's "
            "expansion changed at least one harmonic pick per salt, so "
            "downstream SHAs are novel — but the collision floor is still 0, "
            "confirming I4's dominance under N=8."
        ),
    }


def run(v4_root: Path = V4_BATCH_ROOT) -> Dict:
    v4_root = Path(v4_root)
    v4_root.mkdir(parents=True, exist_ok=True)

    # 1. Read-only preconditions: verify both ledgers content-hash to their
    #    frozen manifest, before spawning any subprocess.
    _read_ledger_open_mode_assertion()
    src_pre = _sha256(SOURCE_LEDGER)
    i3_pre = _sha256(I3_LEDGER)

    # 2. Snapshot anchor directories' file SHAs BEFORE the render, so the
    #    post-run comparison can prove non-modification.
    pre_shas = {
        "batch_v2":    _snapshot_dir_shas(V2_BATCH_ROOT),
        "batch_v3_i3": _snapshot_dir_shas(I3_BATCH_ROOT),
        "batch_v3_i4": _snapshot_dir_shas(I4_BATCH_ROOT),
    }

    # 3. Delegate to the frozen batch_v3_i4 driver — same I4 sampler, same
    #    coherence gate, same assemble/render/score — with the augmented
    #    ledger swapped in and a new batch root.
    inner_manifest = _run_i4_batch(ledger=I3_LEDGER, batch_root=v4_root)

    # 4. Emit per-song rules.json (compound-specific brief deliverable).
    _write_rules_json(v4_root)

    # 5. Collision analysis (frozen cycle-13 methodology).
    coll = analyze(v4_root)
    (v4_root / "collision_analysis.json").write_text(
        json.dumps(coll, indent=2, sort_keys=True)
    )
    write_tsv(coll, v4_root / "collision_matrix.tsv")

    # 6. Anchor cross-reference (§4 of the report).
    xref = _anchor_cross_reference(v4_root)
    (v4_root / "anchor_cross_reference.json").write_text(
        json.dumps(xref, indent=2, sort_keys=True)
    )

    # 7. Anchor-preservation SHAs POST-run.
    post_shas = {
        "batch_v2":    _snapshot_dir_shas(V2_BATCH_ROOT),
        "batch_v3_i3": _snapshot_dir_shas(I3_BATCH_ROOT),
        "batch_v3_i4": _snapshot_dir_shas(I4_BATCH_ROOT),
    }
    for name in ("batch_v2", "batch_v3_i3", "batch_v3_i4"):
        if pre_shas[name] != post_shas[name]:
            raise AssertionError(
                f"anchor-preservation FAILED for {name}: "
                f"pre-run and post-run SHAs differ"
            )
    src_post = _sha256(SOURCE_LEDGER)
    i3_post = _sha256(I3_LEDGER)
    if (src_pre, i3_pre) != (src_post, i3_post):
        raise AssertionError("ledger SHA drift across run")

    # 8. Hypothesis verdict.
    observed_pairs = int(coll["coerced"]["total_pairwise_collisions"])
    verdict = _classify_verdict(observed_pairs, xref)
    (v4_root / "hypothesis_verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True)
    )

    # 9. Compound batch manifest — chain-of-provenance overriding the
    #    inherited inner manifest with compound-specific fields.
    i3_m = json.loads(I3_MANIFEST.read_text())
    v4_manifest = dict(inner_manifest)
    v4_manifest.update({
        "milestone": "M-GEN-1/batch-v4-compound",
        "sampler": "i4_stratified_rejection_sha256",
        "source_ledger": "data/rules/ledger_i3_dminor.jsonl",
        "source_ledger_sha256": i3_pre,
        "source_row_count": i3_m["augmented_row_count"],
        "harmonic_K": i3_m["harmonic_K_after"],
        "provenance_chain": {
            "cycle_9_dawdreamer_chain": "scripts/tex/render_effects_layered.py",
            "cycle_13_render_pipeline": "scripts/gen/render_pipeline.py",
            "cycle_15_i4_sampler": "scripts/rules/sampling/i4_stratified.py",
            "cycle_15_i3_augmentation": "scripts/rules/sampling/i3_dminor.py",
            "i3_augmented_ledger_sha256": i3_m["augmented_ledger_sha256"],
            "i3_source_ledger_sha256": i3_m["source_ledger_sha256"],
        },
        "collision_pairs_at_N8": observed_pairs,
        "verdict": verdict["verdict"],
        "anchor_xref_counts": xref["counts"],
        "anchor_preservation": {
            "batch_v2_unchanged": True,
            "batch_v3_i3_unchanged": True,
            "batch_v3_i4_unchanged": True,
            "source_ledger_sha256_pre": src_pre,
            "source_ledger_sha256_post": src_post,
            "i3_ledger_sha256_pre": i3_pre,
            "i3_ledger_sha256_post": i3_post,
        },
    })
    (v4_root / "batch_manifest.json").write_text(
        json.dumps(v4_manifest, indent=2, sort_keys=True)
    )

    return v4_manifest


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path, default=V4_BATCH_ROOT)
    args = ap.parse_args(argv)
    m = run(args.batch_root)
    print(f"[batch_v4_compound] verdict = {m['verdict']}  pairs = "
          f"{m['collision_pairs_at_N8']}  ledger = "
          f"{m['source_ledger_sha256'][:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
