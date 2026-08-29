#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:18:50Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
# ---
"""c36 Branch C — top-level entry: run probes, compute pairwise metrics,
emit verdict per the frozen rubric, conditionally emit
tolerance_gate_rubric_candidate.json.

Strictly serial. No PRNG. Interpreter guard forces /usr/bin/python3.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from scripts.vst3_nondeterminism import _shared as sh  # noqa: E402
from scripts.vst3_nondeterminism import rms_pairwise_distribution as rms_mod  # noqa: E402
from scripts.vst3_nondeterminism import envelope_correlation_pairwise as env_mod  # noqa: E402
from scripts.vst3_nondeterminism import characterization_fit as fit_mod  # noqa: E402

assert sys.executable == "/usr/bin/python3", sys.executable


def classify(per_plugin: dict) -> str:
    """Apply the frozen rubric to per-plugin aggregate metrics.

    Per-plugin classification:
      SMALL      = mrms < 1e-4 AND mmel < 0.5 AND mecc > 0.99
      STRUCTURAL = mrms >= 1e-2 OR mmel >= 3.0 OR mecc < 0.9

    Aggregate verdict (rubric §MIXED example: 'Surge XT small but
    Dexed structural, or single-metric borderline'):
      SMALL_PERTURBATION_TOLERABLE = all plugins SMALL
      STRUCTURAL_DRIFT            = all plugins STRUCTURAL
      MIXED                        = anything between (incl. one plugin
                                     STRUCTURAL + other SMALL, or any
                                     single-metric borderline sitting
                                     in (1e-4, 1e-2), (0.5, 3.0), or
                                     (0.9, 0.99)).
    """
    per = {}
    for plugin, s in per_plugin.items():
        mrms = s["rms"]["max"]
        mmel = s["mel_l1_db"]["max"]
        mecc = s["env_corr"]["min"]
        plugin_small = (mrms < 1e-4) and (mmel < 0.5) and (mecc > 0.99)
        plugin_struct = (mrms >= 1e-2) or (mmel >= 3.0) or (mecc < 0.9)
        per[plugin] = ("SMALL" if plugin_small
                       else "STRUCTURAL" if plugin_struct
                       else "BORDERLINE")
    labels = set(per.values())
    if labels == {"SMALL"}:
        return "SMALL_PERTURBATION_TOLERABLE"
    if labels == {"STRUCTURAL"}:
        return "STRUCTURAL_DRIFT"
    return "MIXED"


def build_tolerance_candidate(per_plugin: dict, rubric_hash: str) -> dict:
    """Given SMALL_PERTURBATION_TOLERABLE, propose per-plugin thresholds
    slightly outside the observed distribution (1.5× / 0.98×)."""
    obs_max_rms = max(s["rms"]["max"] for s in per_plugin.values())
    obs_max_mel = max(s["mel_l1_db"]["max"] for s in per_plugin.values())
    obs_min_ecc = min(s["env_corr"]["min"] for s in per_plugin.values())
    return {
        "candidate_status": "PROPOSED_NOT_ADOPTED",
        "adopts": None,
        "adopted_by_cycle": None,
        "source_rubric_hash": rubric_hash,
        "observed_max_pairwise_rms": obs_max_rms,
        "observed_max_pairwise_mel_l1_db": obs_max_mel,
        "observed_min_pairwise_env_correlation": obs_min_ecc,
        "tolerance_rms_max": obs_max_rms * 1.5,
        "tolerance_mel_l1_db_max": obs_max_mel * 1.5,
        "tolerance_env_corr_min": obs_min_ecc * 0.98,
        "notes": (
            "1.5× / 0.98× per rubric §SMALL_PERTURBATION_TOLERABLE. "
            "Candidate only; c37 owns adoption for a future "
            "M-DAW-SPIKE-1/palette-v3-VST3-tolerance-activation "
            "peer sub-milestone."
        ),
    }


def anchor_snapshot_post() -> None:
    """Write the 'post' half of the anchor preservation snapshot; assert
    byte-equality against 'pre'."""
    import hashlib
    ap_path = REPO / "data" / "vst3_nondeterminism" / "anchor_preservation.json"
    ap = json.loads(ap_path.read_text())
    pre = ap["pre"]
    post = {}
    for relpath in pre:
        p = REPO / relpath
        post[relpath] = hashlib.sha256(p.read_bytes()).hexdigest()
    ap["post"] = post
    ap["preserved"] = post == pre
    if not ap["preserved"]:
        diffs = [rp for rp in pre if pre[rp] != post.get(rp)]
        ap["drift"] = diffs
    ap_path.write_text(json.dumps(ap, sort_keys=True, indent=2) + "\n")


def main() -> int:
    # Step 1: probes (call as subprocess for fresh interpreter isolation
    # per plugin — mirrors c31's per-probe process discipline).
    for probe in ("probe_surge_xt.py", "probe_dexed.py"):
        script = REPO / "scripts" / "vst3_nondeterminism" / probe
        r = subprocess.run(
            ["/usr/bin/python3", str(script)],
            cwd=str(REPO), check=False
        )
        if r.returncode != 0:
            print(f"probe failed: {probe}", file=sys.stderr)
            return r.returncode

    # Step 2: pairwise metrics
    rms_mod.main()
    env_mod.main()

    # Step 3: mel + per-plugin summaries
    per_plugin = {}
    for plugin in sh.PLUGINS:
        per_plugin[plugin] = fit_mod.compute_for(plugin)

    # Step 4: verdict per rubric
    rubric_hash = (REPO / "data/vst3_nondeterminism/rubric_hash.txt").read_text().strip()
    verdict = classify(per_plugin)
    v = {
        "verdict": verdict,
        "rubric_hash": rubric_hash,
        "per_plugin": {
            plugin: {
                "label": (
                    "SMALL" if (s["rms"]["max"] < 1e-4
                                and s["mel_l1_db"]["max"] < 0.5
                                and s["env_corr"]["min"] > 0.99)
                    else "STRUCTURAL" if (s["rms"]["max"] >= 1e-2
                                          or s["mel_l1_db"]["max"] >= 3.0
                                          or s["env_corr"]["min"] < 0.9)
                    else "BORDERLINE"
                ),
                "max_pairwise_rms": s["rms"]["max"],
                "max_pairwise_mel_l1_db": s["mel_l1_db"]["max"],
                "min_pairwise_env_correlation": s["env_corr"]["min"],
                "max_abs_sample": s["max_abs_sample"]["max"],
                "median_pairwise_rms": s["rms"]["median"],
                "median_pairwise_mel_l1_db": s["mel_l1_db"]["median"],
                "median_pairwise_env_correlation": s["env_corr"]["median"],
                "run_shas": s["run_shas"],
                "all_shas_distinct": s["all_shas_distinct"],
                "all_shas_equal": s["all_shas_equal"],
            }
            for plugin, s in per_plugin.items()
        },
    }
    out_v = REPO / "data" / "vst3_nondeterminism" / "characterization_verdict.json"
    out_v.write_text(json.dumps(v, sort_keys=True, indent=2) + "\n")
    print(f"verdict: {verdict}")

    # Step 5: tolerance-gate candidate if SMALL_PERTURBATION_TOLERABLE
    tol_path = REPO / "data" / "vst3_nondeterminism" / "tolerance_gate_rubric_candidate.json"
    if verdict == "SMALL_PERTURBATION_TOLERABLE":
        c = build_tolerance_candidate(per_plugin, rubric_hash)
        tol_path.write_text(json.dumps(c, sort_keys=True, indent=2) + "\n")
        print(f"wrote {tol_path.relative_to(REPO)}")

    # Step 6: anchor snapshot post
    anchor_snapshot_post()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
