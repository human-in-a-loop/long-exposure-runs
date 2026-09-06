#!/usr/bin/python3
"""c82 P1.6 — c76 v2 wider-linear LOO sanity gate on FRESH embeddings (from the isolated ear venv), not the cache.

created: 2026-09-06T18:30:00Z
cycle: 82
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-EAR-1/ear-gate-v5-c82

Input: the run-1 npz persisted by scripts/v5/ear_probe_v5.py (EAR_PROBE_SAVE_NPZ), rows keyed by the FROZEN
exemplar / band-4 short ids of scripts/v4_ear/ear.py. The gate itself is the READ-ONLY c76 code:
scripts/ear/v4_ear_v2.leave_one_out_v2 (wider-linear calibration) + scripts/ear/v4_ear.sanity_gate (campaign
L115-117: >= 4 of 5 exemplars >= 6, none < 5.5). Band-4 spot check via score_audio_v2 with the shared raw ceiling
(campaign L119 informational; c76 proved it infeasible under VGGish). Cached-embedding LOO reported alongside.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; FROZEN inputs read-only.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_WS))
import numpy as np  # noqa: E402
from scripts.ear import v4_ear as V1  # noqa: E402  READ-ONLY (c74)
from scripts.ear import v4_ear_v2 as V2  # noqa: E402  READ-ONLY (c76)
from scripts.v4_ear import ear as E  # noqa: E402  READ-ONLY (short ids)

FRESH = _WS / "data/v5/ear/ear_probe_c82_fresh_embeddings.npz"
OUT = _WS / "data/v5/ear/ear_gate_v5_c82.json"


def main() -> int:
    if not FRESH.exists():
        rec = {"schema_version": 1, "cycle": 82, "agent": "worker", "status": "EAR_GATE_NOT_RUN", "reason": f"{FRESH} absent (probe did not persist fresh embeddings)"}
        OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
        print(rec["status"]); return 3
    z = np.load(FRESH)
    ex_ids = [x[0] for x in E.EXEMPLARS]
    b4_ids = [x[0] for x in E.BAND_4_SPOT_CHECK]
    fresh_sig = {k: z[k].astype("float64").tolist() for k in ex_ids}
    exemplar_set = V1.load_exemplar_set()
    cached_sig = V1.build_exemplar_signatures(exemplar_set)
    loo_fresh = V2.leave_one_out_v2(exemplar_set, exemplar_signatures=fresh_sig)
    loo_cached = V2.leave_one_out_v2(exemplar_set, exemplar_signatures=cached_sig)
    gate_fresh = V1.sanity_gate(loo_fresh)
    gate_cached = V1.sanity_gate(loo_cached)
    raw = {}
    for held in fresh_sig:
        rest = {k: v for k, v in fresh_sig.items() if k != held}
        raw[held] = V1._max_over_exemplar_windows(fresh_sig[held], rest)
    raw_max = max(raw.values())
    band4 = {k: round(V2.score_audio_v2(z[k].astype("float64").tolist(), fresh_sig, raw_max), 4) for k in b4_ids if k in z.files}
    loo_min = min(loo_fresh.values())
    l119 = {"band4_max": max(band4.values()) if band4 else None, "loo_min": round(loo_min, 4), "threshold_loo_min_minus_0_5": round(loo_min - 0.5, 4),
            "passes": (max(band4.values()) < loo_min - 0.5) if band4 else None, "note": "informational; c76 proved L119 infeasible under the VGGish backbone (l119_infeasibility_proof_c76.json)"}
    rec = {"schema_version": 1, "cycle": 82, "agent": "worker", "milestone": "M-V5-EAR-1/ear-gate-v5-c82", "status": "EAR_GATE_RUN",
           "fresh_npz": str(FRESH.relative_to(_WS)), "fresh_npz_sha256": hashlib.sha256(FRESH.read_bytes()).hexdigest(),
           "calibration": V2.module_env_manifest_v2(), "loo_fresh_v2": {k: round(v, 4) for k, v in loo_fresh.items()},
           "loo_cached_v2": {k: round(v, 4) for k, v in loo_cached.items()}, "raw_stats_fresh": {k: round(v, 6) for k, v in raw.items()},
           "sanity_gate_fresh": gate_fresh, "sanity_gate_cached": gate_cached, "band4_spot_check_fresh_v2": band4, "l119_check": l119,
           "gate_rule": "campaign L115-117: >= 4 of 5 exemplar LOO scores >= 6 and none < 5.5 (scripts/ear/v4_ear.sanity_gate READ-ONLY)",
           "restores_ge6_gate": bool(gate_fresh.get("pass", gate_fresh.get("passes", False)))}
    OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in ("loo_fresh_v2", "loo_cached_v2", "sanity_gate_fresh", "band4_spot_check_fresh_v2", "l119_check")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
