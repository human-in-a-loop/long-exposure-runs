#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:25:00Z
# cycle: 34
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render/cross-seed
# ---
"""Cross-seed orchestrator.

Sequence:
  1. Snapshot mtime + SHA of every c33 palette_render + c31 palette
     + c31 palette_probe + c33 dawdreamer_state anchor file.
  2. For each seed in [seed_mid_50s, synth_060s], call process_seed().
  3. Resolve per-seed verdict against the frozen rubric.
  4. Combine per-seed verdicts into cross-seed cumulative verdict.
  5. Re-take the anchor snapshot; assert unchanged.
  6. Write verdict.json (with rubric_hash byte-equal to rubric_hash.txt
     in both per-seed keys) + cross_seed_summary.tsv + anchor_preservation.json.

NO PRNG. /usr/bin/python3 guarded. No sidecar_nonfactor. Read-only c33/c31 imports.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette_render_cross_seed import (  # noqa: E402
    NUMERIC_FAMILY_KEYS, PALETTE_DELTA_PCT, SEEDS,
)
from scripts.palette_render_cross_seed.run_seed import process_seed  # noqa: E402
# READ-ONLY imports of c33 anchors (parity witnesses only).
from scripts.palette_render import build_assignments as _c33_build  # noqa: E402
from scripts.palette_render import render_stem as _c33_render_stem  # noqa: E402
from scripts.texture.panel import PUBLIC_KEYS  # noqa: E402

OUT_DIR = _REPO / "data" / "palette_render_cross_seed"
ANCHOR_DIRS = (
    _REPO / "scripts" / "palette_render",
    _REPO / "data" / "palette_render",
    _REPO / "scripts" / "palette",
    _REPO / "scripts" / "palette_probe",
    _REPO / "scripts" / "dawdreamer_state",
)


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_anchors() -> dict:
    """Return {rel_path: {mtime, sha}} for every regular file under ANCHOR_DIRS."""
    snap = {}
    for d in ANCHOR_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.rglob("*")):
            if not p.is_file():
                continue
            if "__pycache__" in p.parts:
                continue
            rel = str(p.relative_to(_REPO))
            snap[rel] = {
                "mtime_ns": p.stat().st_mtime_ns,
                "sha256": _sha256_file(p),
            }
    return snap


def _delta_pct(baseline: float, current: float) -> float:
    if baseline is None or current is None:
        return math.nan
    denom = max(1e-9, abs(baseline))
    return abs(current - baseline) / denom * 100.0


def resolve_per_seed_verdict(seed_result: dict) -> tuple[str, dict]:
    """Apply per-seed 3-verdict rubric."""
    # RENDER_FAILS gates
    if not seed_result["combined_sha_equal"]:
        return "RENDER_FAILS", {"reason": "bare_combined SHA mismatch across runs"}
    for stem, ok in seed_result["per_stem_sha_equal"].items():
        if not ok:
            return "RENDER_FAILS", {"reason": f"per-stem SHA mismatch on {stem}"}

    for tag, panel in (("orig_vs_palette", seed_result["panel_original_vs_palette"]),
                       ("fluid_vs_palette", seed_result["panel_fluidsynth_vs_palette"])):
        if set(panel.keys()) != set(PUBLIC_KEYS):
            return "RENDER_FAILS", {"reason": f"panel key contract violation on {tag}",
                                    "keys": sorted(panel.keys())}
        for k in NUMERIC_FAMILY_KEYS:
            v = panel.get(k)
            if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
                return "RENDER_FAILS", {"reason": f"non-finite {k} on {tag}", "value": v}

    # Numeric family activation: compare fluid_vs_palette panel to this-seed's
    # c13 fluidsynth-only self-panel (which is the numeric floor).
    deltas = {}
    for k in NUMERIC_FAMILY_KEYS:
        baseline = seed_result["panel_fluidsynth_self"].get(k)
        current = seed_result["panel_fluidsynth_vs_palette"].get(k)
        deltas[k] = {
            "baseline": baseline,
            "current": current,
            "delta_pct": _delta_pct(baseline, current),
        }

    any_moves = any((not math.isnan(d["delta_pct"])) and d["delta_pct"] >= PALETTE_DELTA_PCT
                    for d in deltas.values())
    if any_moves:
        return "PALETTE_MOVES_PANEL", {"deltas": deltas}
    return "PALETTE_NEUTRAL", {"deltas": deltas}


def resolve_cross_seed(per_seed: dict[str, str]) -> str:
    labels = list(per_seed.values())
    if "RENDER_FAILS" in labels:
        return "RENDER_FAILS"
    n_moves = sum(1 for x in labels if x == "PALETTE_MOVES_PANEL")
    if n_moves == 2:
        return "CROSS_SEED_CONSISTENT"
    if n_moves == 1:
        return "CROSS_SEED_PARTIAL"
    return "CROSS_SEED_INCONSISTENT"


def _write_cross_seed_summary(results: dict, verdicts: dict, out_path: Path) -> None:
    """Rows: one per seed; columns: seed, verdict, per-key baseline/current/delta%."""
    header = ["seed", "verdict"]
    for k in NUMERIC_FAMILY_KEYS:
        header += [f"{k}_baseline", f"{k}_palette", f"{k}_delta_pct"]
    lines = ["\t".join(header)]
    for seed in SEEDS:
        r = results[seed]
        v = verdicts[seed]
        row = [seed, v]
        for k in NUMERIC_FAMILY_KEYS:
            b = r["panel_fluidsynth_self"].get(k)
            c = r["panel_fluidsynth_vs_palette"].get(k)
            row += [f"{b}", f"{c}", f"{_delta_pct(b, c):.6f}"]
        lines.append("\t".join(row))
    out_path.write_text("\n".join(lines) + "\n")


def _panel_json_safe(panel: dict) -> dict:
    out = {}
    for k, v in panel.items():
        if v is None:
            out[k] = None
        elif isinstance(v, (int, float, bool)):
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                out[k] = str(v)
            else:
                out[k] = float(v) if isinstance(v, (int, float)) else v
        else:
            out[k] = str(v)
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    anchor_pre = snapshot_anchors()

    results = {}
    for seed in SEEDS:
        results[seed] = process_seed(seed)

    per_seed_verdicts = {}
    per_seed_justifications = {}
    for seed, r in results.items():
        v, j = resolve_per_seed_verdict(r)
        per_seed_verdicts[seed] = v
        per_seed_justifications[seed] = j

    cumulative = resolve_cross_seed(per_seed_verdicts)

    anchor_post = snapshot_anchors()
    anchor_unchanged = anchor_pre == anchor_post

    if not anchor_unchanged:
        # Best-effort: identify divergent paths.
        diff = []
        for k in set(anchor_pre) | set(anchor_post):
            if anchor_pre.get(k) != anchor_post.get(k):
                diff.append(k)
        raise RuntimeError(f"anchor divergence: {diff[:20]}")

    rubric_hash = (OUT_DIR / "rubric_hash.txt").read_text().strip()

    verdict_json = {
        "cross_seed_cumulative_verdict": cumulative,
        "rubric_hash": rubric_hash,
        "palette_delta_pct_threshold": PALETTE_DELTA_PCT,
    }
    for seed in SEEDS:
        r = results[seed]
        v = per_seed_verdicts[seed]
        j = per_seed_justifications[seed]
        verdict_json[seed] = {
            "rubric_hash": rubric_hash,
            "verdict": v,
            "combined_sha_run1": r["combined_sha_run1"],
            "combined_sha_run2": r["combined_sha_run2"],
            "combined_sha_equal": r["combined_sha_equal"],
            "per_stem_sha_equal": r["per_stem_sha_equal"],
            "sample_count": r["sample_count"],
            "assignments": [{"stem": a["stem"], "instrument": a["instrument"],
                             "assignment_id": a["assignment_id"],
                             "provenance_pointers": a["provenance_pointers"]}
                            for a in r["assignments"]],
            "panel_original_vs_palette": _panel_json_safe(r["panel_original_vs_palette"]),
            "panel_fluidsynth_vs_palette": _panel_json_safe(r["panel_fluidsynth_vs_palette"]),
            "panel_fluidsynth_self_baseline": _panel_json_safe(r["panel_fluidsynth_self"]),
            "panel_delta_percent_per_key": {
                k: _delta_pct(r["panel_fluidsynth_self"].get(k),
                              r["panel_fluidsynth_vs_palette"].get(k))
                for k in NUMERIC_FAMILY_KEYS
            },
            "justification": j,
        }
    verdict_json["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict_json, sort_keys=True, indent=2) + "\n")

    _write_cross_seed_summary(results, per_seed_verdicts,
                              OUT_DIR / "cross_seed_summary.tsv")

    (OUT_DIR / "anchor_preservation.json").write_text(
        json.dumps({"pre": anchor_pre, "post": anchor_post,
                    "unchanged": anchor_unchanged},
                   sort_keys=True, indent=2) + "\n")

    print(json.dumps({"cross_seed_cumulative_verdict": cumulative,
                      "per_seed": per_seed_verdicts,
                      "rubric_hash": rubric_hash,
                      "anchor_unchanged": anchor_unchanged},
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
