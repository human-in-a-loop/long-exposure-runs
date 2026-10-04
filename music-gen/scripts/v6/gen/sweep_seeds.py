#!/usr/bin/python3
"""v6 Phase 5 — sweep_seeds: compose the 3 fixture songs for many seeds, with and without --humanize, run the validators and
tabulate per rule how many (song, seed, mode) cases violate a cap, the max count, and every FORCED violation (a rule the
composer could not satisfy by construction; recorded with its reason in plan.json["repairs"]["forced"] / chord_slots[*]["forced"]).

created: 2026-10-04
milestone: M-V6-GEN-5/hardening

  /usr/bin/python3 scripts/v6/gen/sweep_seeds.py [--seeds 0-11] [--bars 32] [--bpm 100,120,152] [--out-dir data/v6/gen/sweeps]
      [--stamp 20261004T120000Z] [--no-repair] [--modes plain,humanize] [--quiet]

Writes <out-dir>/seed_sweep_<stamp>.json (+ .md table). In-process (compose_song, no rendering, no files per song): ~0.3 s a case.
No PRNG anywhere; the sweep itself is a pure function of (seeds, bars, bpm, code).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.gen.common import WS, write_json_atomic  # noqa: E402
from scripts.v6.gen import validators  # noqa: E402
from scripts.v6.gen.compose_v6 import compose_song  # noqa: E402
from scripts.v6.gen.fixtures import FIXTURE_DONORS, load_models  # noqa: E402

DEFAULT_BPM = (100.0, 120.0, 152.0)


def parse_seeds(spec: str) -> list:
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def run_case(models: dict, seed: int, bpm: float, donor: str, song_id: str, n_bars: int, humanize: bool, repair: bool) -> dict:
    hz = {"mt": None, "path": None, "sha256": None} if humanize else None
    t0 = time.time()
    res = compose_song(models, song_id, donor, seed, bpm, n_bars, hz, repair_pass=repair)
    val, plan = res["validators"], res["plan"]
    rep = plan.get("repairs") or {}
    forced_keys = [{"bar": c["bar"], "beat": c["beat"], "state": c["state"], "rules": c["forced"], "reason": c.get("forced_reason")} for c in plan["chord_slots"] if c.get("forced")]
    return {"song_id": song_id, "donor": donor, "seed": seed, "bpm": bpm, "humanize": humanize, "wall_s": round(time.time() - t0, 3),
            "metrics": val["metrics"], "cap_pass": val["cap_pass"], "all_caps_pass": val["all_caps_pass"], "parallels": val["detail"]["parallels"],
            "leading_tone": val["detail"]["leading_tone"], "n_repairs": rep.get("n_repairs", 0), "repairs_by_rule": rep.get("by_rule", {}),
            "forced": (rep.get("forced") or []) + [dict(f, rule="keys_voicing:" + "+".join(f["rules"])) for f in forced_keys]}


def summarize(cases: list) -> dict:
    rules = list(validators.CAPS)
    per_rule = {}
    for r in rules:
        viol = [c for c in cases if not c["cap_pass"].get(r, True)]
        vals = [c["metrics"][r] for c in cases if isinstance(c["metrics"].get(r), (int, float)) and not isinstance(c["metrics"].get(r), bool)]
        per_rule[r] = {"n_cases_violating": len(viol), "max_count": max(vals) if vals else None,
                       "violating_cases": [f"{c['song_id']}|seed={c['seed']}|{'humanize' if c['humanize'] else 'plain'}={c['metrics'][r]}" for c in viol]}
    forced = []
    for c in cases:
        for f in c["forced"]:
            forced.append(dict(f, song_id=c["song_id"], seed=c["seed"], humanize=c["humanize"]))
    rep_rules: dict = {}
    for c in cases:
        for k, v in c["repairs_by_rule"].items():
            rep_rules[k] = rep_rules.get(k, 0) + v
    unforced_fail = [c for c in cases if not c["all_caps_pass"] and not c["forced"]]
    return {"n_cases": len(cases), "n_cases_all_caps_pass": sum(1 for c in cases if c["all_caps_pass"]), "per_rule": per_rule,
            "n_forced": len(forced), "forced": forced, "n_repairs_total": sum(c["n_repairs"] for c in cases), "repairs_by_rule": rep_rules,
            "n_cases_failing_without_forced": len(unforced_fail),
            "cases_failing_without_forced": [f"{c['song_id']}|seed={c['seed']}|{'humanize' if c['humanize'] else 'plain'}" for c in unforced_fail]}


def markdown(summary: dict, meta: dict) -> str:
    L = [f"# Seed sweep {meta['stamp']}", "", f"seeds {meta['seeds'][0]}..{meta['seeds'][-1]} x 3 fixtures x modes {meta['modes']} = {summary['n_cases']} cases; "
         f"bars {meta['n_bars']}; repair {'ON' if meta['repair'] else 'OFF'}; all caps pass in {summary['n_cases_all_caps_pass']}/{summary['n_cases']} cases; "
         f"repairs applied {summary['n_repairs_total']} ({summary['repairs_by_rule']}); forced violations {summary['n_forced']}.", "",
         "| rule | cap | cases violating | max count |", "|---|---|---|---|"]
    for r, s in summary["per_rule"].items():
        cap = validators.CAPS[r]
        L.append(f"| {r} | {cap['op']} {cap['cap']} ({cap['per']}) | {s['n_cases_violating']} | {s['max_count']} |")
    L += ["", "## Forced violations (logged with reason)", ""]
    if not summary["forced"]:
        L.append("none")
    for f in summary["forced"]:
        L.append(f"- {f['song_id']} seed={f['seed']} {'humanize' if f['humanize'] else 'plain'} bar {f.get('bar')} slot {f.get('slot', f.get('beat'))}: {f['rule']} — {f.get('reason')}")
    L += ["", "## Cases failing a cap without a forced violation", ""]
    L += [f"- {c}" for c in summary["cases_failing_without_forced"]] or ["none"]
    return "\n".join(L) + "\n"


def sweep(seeds: list, n_bars: int, bpms: list, modes: list, repair: bool, log=print) -> tuple[list, dict]:
    models = load_models(None, fixtures=True)
    donors = sorted(FIXTURE_DONORS)
    cases = []
    for seed in seeds:
        for hum in modes:
            for i, donor in enumerate(donors):
                c = run_case(models, seed, float(bpms[i % len(bpms)]), donor, f"gen_v6_song_{i + 1}", n_bars, hum, repair)
                cases.append(c)
                bad = [k for k, v in c["cap_pass"].items() if not v]
                log(f"seed {seed:2d} {'humanize' if hum else 'plain   '} {c['song_id']} {c['wall_s']:.2f}s repairs={c['n_repairs']} forced={len(c['forced'])} "
                    f"caps={'PASS' if c['all_caps_pass'] else 'FAIL ' + ','.join(bad)}")
    return cases, summarize(cases)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 multi-seed validator sweep over the fixture songs")
    ap.add_argument("--seeds", default="0-11")
    ap.add_argument("--bars", type=int, default=32)
    ap.add_argument("--bpm", default=",".join(str(int(b)) for b in DEFAULT_BPM))
    ap.add_argument("--modes", default="plain,humanize")
    ap.add_argument("--out-dir", default="data/v6/gen/sweeps")
    ap.add_argument("--stamp", default=None, help="file stamp (default: UTC now, %%Y%%m%%dT%%H%%M%%SZ)")
    ap.add_argument("--no-repair", action="store_true", help="compose without the counterpoint repair pass (the 'before' table)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    seeds = parse_seeds(args.seeds)
    modes = [m.strip() == "humanize" for m in args.modes.split(",") if m.strip()]
    stamp = args.stamp or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_dir = Path(args.out_dir) if Path(args.out_dir).is_absolute() else WS / args.out_dir
    cases, summary = sweep(seeds, args.bars, [float(x) for x in args.bpm.split(",")], modes, not args.no_repair, (lambda *a: None) if args.quiet else print)
    meta = {"stamp": stamp, "seeds": seeds, "n_bars": args.bars, "bpm": args.bpm, "modes": args.modes, "repair": not args.no_repair}
    doc = {"schema_version": 1, "meta": meta, "summary": summary, "cases": cases, "caps": validators.CAPS}
    write_json_atomic(out_dir / f"seed_sweep_{stamp}.json", doc)
    md = markdown(summary, meta)
    (out_dir / f"seed_sweep_{stamp}.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {out_dir / f'seed_sweep_{stamp}.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
