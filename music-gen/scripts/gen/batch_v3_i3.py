#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:35:00Z
# cycle: 15
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-2, fork 392503ab7d47)
# milestone: M-GEN-1/batch-v3-i3
# ---
"""Batch-v3-I3 orchestrator: 8 songs on the D_minor-augmented rules pool.

Verbatim reuse of cycle-13 batch-v2's render pipeline. Only the input
ledger and the batch root differ:

  ledger      : data/rules/ledger_i3_dminor.jsonl  (76 source + 10 D_minor
                harmonic variants; harmonic K 10 -> 20)
  batch root  : data/gen/batch_v3_i3/

The augmented ledger is (re)built at runtime by
scripts.rules.sampling.i3_dminor.build_augmented_ledger so this script
is self-contained and byte-deterministic from a clean tree.

All render stages (sample_ruleset, enforce_coherence, assemble_score,
render, score) are imported unchanged from scripts.gen.batch_v2's
dependency graph — cycle-9 DawDreamer chain SHA anchor and cycle-13
batch-v2 rendering contract preserved.

After the batch, runs collision_analysis over the batch_v3_i3 root and
writes an i3-specific summary comparing observed pairs to the analytic
prediction (H=10 sweep row: 8.24; task-brief prediction: 7.75; PASS
band: 6-9).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

# Pins BEFORE downstream imports (mirror batch_v2.py).
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.gen.batch_v2 import run_batch  # noqa: E402 -- verbatim render pipeline
from scripts.gen.collision_analysis import analyze, write_tsv  # noqa: E402
from scripts.rules.sampling.i3_dminor import build_augmented_ledger  # noqa: E402


I3_LEDGER = _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl"
I3_MANIFEST = _REPO / "data" / "rules" / "i3_dminor_manifest.json"
I3_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v3_i3"


# PASS band per assignment brief:
#   PASS   if 6 <= observed <= 9
#   PARTIAL if observed in {5, 10}
#   FAIL   otherwise
def _classify(observed_pairs: int) -> str:
    if 6 <= observed_pairs <= 9:
        return "PASS"
    if observed_pairs in (5, 10):
        return "PARTIAL"
    return "FAIL"


def run(batch_root: Path = I3_BATCH_ROOT) -> dict:
    # Step 1: (re)build augmented ledger.
    m_aug = build_augmented_ledger(_REPO / "data" / "rules" / "ledger.jsonl", I3_LEDGER)
    I3_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    I3_MANIFEST.write_text(json.dumps(m_aug, indent=2, sort_keys=True))

    # Step 2: render the batch (verbatim batch_v2 pipeline; different ledger + root).
    batch_manifest = run_batch(ledger=I3_LEDGER, batch_root=batch_root)
    (batch_root / "batch_manifest.json").write_text(
        json.dumps(batch_manifest, indent=2, sort_keys=True))

    # Step 3: collision analysis on this batch.
    coll = analyze(batch_root)
    (batch_root / "collision_analysis.json").write_text(
        json.dumps(coll, indent=2, sort_keys=True))
    write_tsv(coll, batch_root / "collision_matrix.tsv")

    observed_coerced = int(coll["coerced"]["total_pairwise_collisions"])
    observed_raw = int(coll["raw"]["total_pairwise_collisions"])

    # Analytic BP prediction on augmented pool (per-type K):
    #   harmonic:20, rhythmic:18, melodic:18, form:15, arrangement:15
    #   C(8,2)=28; expected pairs per type = 28/K; sum:
    bp_per_type = {"harmonic": 28/20, "rhythmic": 28/18, "melodic": 28/18,
                   "form": 28/15, "arrangement": 28/15}
    bp_total = sum(bp_per_type.values())

    i3_summary = {
        "milestone": "M-GEN-1/batch-v3-i3",
        "intervention": "I3_dminor",
        "ledger_augmentation": {
            "source_ledger_sha256": m_aug["source_ledger_sha256"],
            "augmented_ledger_sha256": m_aug["augmented_ledger_sha256"],
            "harmonic_K_before": m_aug["harmonic_K_before"],
            "harmonic_K_after": m_aug["harmonic_K_after"],
            "n_dminor_variants_added": m_aug["n_dminor_variants_added"],
        },
        "analytic_predictions": {
            "birthday_paradox_per_type": bp_per_type,
            "birthday_paradox_total_at_N8": bp_total,
            "report_I3_sweep_H10_prediction": 8.244444444444444,
            "task_brief_prediction": 7.75,
        },
        "observed": {
            "coerced_pairs": observed_coerced,
            "raw_pairs": observed_raw,
            "per_rule_type_pairs": {
                rt: len(coll["coerced"]["per_rule_type_pairs"][rt])
                for rt in coll["rule_types"]
            },
            "raw_per_rule_type_pairs": {
                rt: len(coll["raw"]["per_rule_type_pairs"][rt])
                for rt in coll["rule_types"]
            },
        },
        "verdict": {
            "pass_band": [6, 9],
            "partial_band": [5, 10],
            "coerced_verdict": _classify(observed_coerced),
            "raw_verdict": _classify(observed_raw),
        },
        "trend": {
            "cycle_13_batch_v2_N8_76rules_pairs": 11,
            "cycle_15_batch_v3_i3_N8_86rules_pairs": observed_coerced,
            "delta_from_v2": observed_coerced - 11,
        },
    }
    (batch_root / "i3_summary.json").write_text(
        json.dumps(i3_summary, indent=2, sort_keys=True))

    return i3_summary


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path, default=I3_BATCH_ROOT)
    args = ap.parse_args(argv)
    s = run(args.batch_root)
    print(f"[batch_v3_i3] observed coerced pairs = {s['observed']['coerced_pairs']} "
          f"(prediction 7.75, PASS band 6-9) -> {s['verdict']['coerced_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
