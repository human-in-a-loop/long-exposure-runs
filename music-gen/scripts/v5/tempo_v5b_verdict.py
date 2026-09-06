#!/usr/bin/python3
"""c80 P1 — frozen falsification verdict for tempo v5b (harmonic-sum).

created: 2026-09-06T16:12:00Z
cycle: 80
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo_v5b-verdict-c80

Reads data/v5/corpus/tempo_v5b_preregistration.json (targets FIXED before the
run) and every <sha16>/tempo_v5b.json, evaluates the targets VERBATIM, and
writes data/v5/corpus/tempo_v5b_falsification.json with one of:
  SUPPORTED_ON_FIVE_ANCHORS | RULES_OUT_HARMONIC_SUM |
  SUPPORTED_ON_ANCHORS_UNSTABLE_ELSEWHERE (secondary downgrade: >50 % of the
  21 non-anchor songs flip).
Also records the pre-registration mtime gate (prereg mtime < every output mtime).
No retune, no second criterion (FD-1).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
CORPUS = Path("data/v5/corpus")


def main() -> int:
    prereg_p = CORPUS / "tempo_v5b_preregistration.json"
    prereg = json.loads(prereg_p.read_text())
    man = json.loads((CORPUS / "corpus_manifest.json").read_text())
    songs = [s["sha16"] for s in man["songs"] if s.get("in_v5_corpus")]
    targets = prereg["falsification_targets_fixed_before_run"]

    per_song, missed, mtimes = {}, [], []
    for s in songs:
        p = CORPUS / s / "tempo_v5b.json"
        r = json.loads(p.read_text())
        mtimes.append(p.stat().st_mtime)
        entry = {"bpm_v5": r["bpm_v5"], "bpm_v5b": r["bpm_v5b"], "flipped_vs_v5": r["flipped_vs_v5"],
                 "s_scores_top3": r["s_scores_top3"], "winner": r["winner"]}
        if s in targets:
            t = targets[s]
            b = r["bpm_v5b"]
            hit = b is not None and t["window"][0] <= b <= t["window"][1]
            if "must_not_be_in" in t and b is not None and t["must_not_be_in"][0] <= b <= t["must_not_be_in"][1]:
                hit = False
            entry.update({"target": t, "hit": bool(hit),
                          "delta_vs_anchor_bpm": (round(b - t["within_2_of"], 6) if b is not None else None)})
            if not hit:
                missed.append(s)
        per_song[s] = entry

    non_anchor = [s for s in songs if s not in targets]
    n_flip = sum(1 for s in non_anchor if per_song[s]["flipped_vs_v5"])
    flip_frac = n_flip / len(non_anchor) if non_anchor else 0.0
    if missed:
        verdict = "RULES_OUT_HARMONIC_SUM"
    elif flip_frac > 0.5:
        verdict = "SUPPORTED_ON_ANCHORS_UNSTABLE_ELSEWHERE"
    else:
        verdict = "SUPPORTED_ON_FIVE_ANCHORS"

    prereg_mtime = prereg_p.stat().st_mtime
    out = {
        "schema_version": 1, "cycle": 80, "criterion": "harmonic_sum_v5b",
        "verdict": verdict,
        "verdict_enum": prereg["verdict_enum"],
        "anchored_songs": list(targets.keys()),
        "missed_targets": missed,
        "non_anchor_songs": len(non_anchor), "non_anchor_flips": n_flip, "non_anchor_flip_fraction": round(flip_frac, 4),
        "total_flips_vs_v5": sum(1 for s in songs if per_song[s]["flipped_vs_v5"]),
        "per_song": per_song,
        "preregistration_gate": {"prereg_mtime": prereg_mtime, "min_output_mtime": min(mtimes),
                                 "prereg_precedes_all_outputs": bool(prereg_mtime < min(mtimes))},
        "fd1": "targets evaluated verbatim from the pre-registration; no retune; no second criterion this cycle",
    }
    (CORPUS / "tempo_v5b_falsification.json").write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(f"VERDICT {verdict}; missed={missed}; non-anchor flips {n_flip}/{len(non_anchor)}; "
          f"prereg precedes outputs: {out['preregistration_gate']['prereg_precedes_all_outputs']}")
    for s in targets:
        e = per_song[s]
        print(f"  {targets[s]['name']:14s} v5={e['bpm_v5']:>9} v5b={e['bpm_v5b']:>9} hit={e['hit']} delta={e['delta_vs_anchor_bpm']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
