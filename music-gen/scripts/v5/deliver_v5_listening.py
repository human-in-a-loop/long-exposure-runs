#!/usr/bin/python3
"""c84 P3 — copy an iteration's best samples to the operator listening dir data/v4/generated/v5_iter_NN/ (OPERATOR #7).

created: 2026-09-09T21:45:00Z
cycle: 84
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/iteration-01-c84

Ranks the iteration's ab_mix.wav by the informational ear score (data/v5/gen/gen_v5_iterNN_ear_scores_c84.json; FD-6: not a
passer declaration), copies the running top-K (default 5) WAV + manifest + ear_score sibling, and writes a listening manifest.
Everything outside the top-K audio is score-and-delete territory (the generator already deleted per-track WAVs). Nothing else
under data/v4/** is written. Discipline: /usr/bin/python3 guard; no PRNG.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)
_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--scores", default=None)
    ap.add_argument("--keep-top", type=int, default=5)
    args = ap.parse_args(argv)
    it = f"iteration_{args.iteration:02d}"
    scores_p = Path(args.scores or f"data/v5/gen/gen_v5_iter{args.iteration:02d}_ear_scores_c84.json")
    scores = json.loads(scores_p.read_text())["scores"]
    dst = Path(f"data/v4/generated/v5_iter_{args.iteration:02d}")
    dst.mkdir(parents=True, exist_ok=True)
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1]["ear_score_v2"], kv[0]))[: args.keep_top]
    rows = []
    for key, sc in ranked:
        src = Path("data/v5/gen") / key
        d = dst / key.split("/", 1)[1]
        d.mkdir(parents=True, exist_ok=True)
        copied = {}
        for name in ("ab_mix.wav", "ab_mix.manifest.json", "ab_mix.replay_proof.json", "ear_score_v5.json"):
            if (src / name).exists():
                shutil.copyfile(src / name, d / name)
                copied[name] = _sha(d / name)
        rows.append({"key": key, "ear_score_v2_informational": sc["ear_score_v2"], "ge_6_informational": sc["ge_6"], "dest": str(d), "copied_sha256": copied})
    man = {"schema_version": 1, "cycle": 84, "agent": "worker", "run_id": "run-2026-09-06T000000Z", "milestone": "M-V5-GEN-1/iteration-01-c84",
           "iteration": args.iteration, "source_dir": f"data/v5/gen/{it}", "scores_table": str(scores_p), "scores_table_sha256": _sha(scores_p),
           "keep_top": args.keep_top, "ranking": "informational ear score (c76 v2 wider-linear via the isolated venv); FD-6 operator ear is the LANDS authority; not a passer declaration",
           "samples": rows}
    (dst / "listening_manifest.json").write_text(json.dumps(man, sort_keys=True, indent=2) + "\n")
    print(json.dumps([(r["key"], r["ear_score_v2_informational"]) for r in rows]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
