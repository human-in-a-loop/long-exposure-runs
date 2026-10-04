#!/usr/bin/python3
"""v6 Phase 5 — sweep_seeds: compose the 3 fixture songs for many seeds, with and without --humanize, run the validators and
tabulate per rule how many (song, seed, mode) cases violate a cap, the max / total count, BEFORE (repair_pass=False: the
constructive layers alone) and AFTER the counterpoint repair pass (repair.py), and every FORCED violation (a rule the composer
could not satisfy by construction; recorded with its reason in plan.json["repairs"]["forced"] / chord_slots[*]["forced"]).

created: 2026-10-04
milestone: M-V6-GEN-5/hardening

  /usr/bin/python3 scripts/v6/gen/sweep_seeds.py [--seeds 0-11] [--bars 32] [--bpm 100,120,152] [--out-dir data/v6/gen/sweeps]
      [--stamp 20261004T120000Z] [--modes plain,humanize] [--no-before] [--quiet]

Writes <out-dir>/seed_sweep_<stamp>.json (+ .md table). In-process (compose_song, no rendering, no files per song): ~0.3 s a
compose, two composes a case (before / after) unless --no-before. No PRNG anywhere; the sweep is a pure function of (seeds, bars, bpm, code).
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


def run_case(models: dict, seed: int, bpm: float, donor: str, song_id: str, n_bars: int, humanize: bool, before: bool = True) -> dict:
    """One (song, seed, mode): the repaired song's validators (+ the un-repaired song's as metrics_before / cap_pass_before when `before`)."""
    hz = {"mt": None, "path": None, "sha256": None} if humanize else None
    t0 = time.time()
    res = compose_song(models, song_id, donor, seed, bpm, n_bars, hz, repair_pass=True)
    val, plan = res["validators"], res["plan"]
    pre = compose_song(models, song_id, donor, seed, bpm, n_bars, hz, repair_pass=False)["validators"] if before else None
    rep = plan.get("repairs") or {}
    forced_keys = plan.get("voicing_forced", [])
    realized = plan.get("realized_keys_violations", [])
    return {"song_id": song_id, "donor": donor, "seed": seed, "bpm": bpm, "humanize": humanize, "wall_s": round(time.time() - t0, 3),
            "metrics": val["metrics"], "cap_pass": val["cap_pass"], "all_caps_pass": val["all_caps_pass"], "parallels": val["detail"]["parallels"],
            "metrics_before": pre["metrics"] if pre else None, "cap_pass_before": pre["cap_pass"] if pre else None, "all_caps_pass_before": pre["all_caps_pass"] if pre else None,
            "leading_tone": val["detail"]["leading_tone"], "n_repairs": rep.get("n_repairs", 0), "repairs_by_rule": rep.get("by_rule", {}),
            "forced": (rep.get("forced") or []) + [dict(f, rule="keys_voicing:" + "+".join(f["rules"]), realized=any(r["to"][:2] == [f["bar"], f["beat"]] or r["from"][:2] == [f["bar"], f["beat"]] for r in realized)) for f in forced_keys],
            "realized_keys_violations": realized, "harmony_junction": plan.get("harmony_junction", {})}


def _rule_stats(cases: list, r: str, mkey: str, ckey: str) -> dict:
    cs = [c for c in cases if c.get(mkey) is not None]
    viol = [c for c in cs if not c[ckey].get(r, True)]
    vals = [c[mkey][r] for c in cs if isinstance(c[mkey].get(r), (int, float)) and not isinstance(c[mkey].get(r), bool)]
    counted = validators.CAPS[r]["per"] in ("per_64_bars", "song") and all(isinstance(v, int) for v in vals)
    return {"n_cases_violating": len(viol), "max_count": max(vals) if vals else None, "total_count": sum(vals) if counted and vals else None,
            "violating_cases": [f"{c['song_id']}|seed={c['seed']}|{'humanize' if c['humanize'] else 'plain'}={c[mkey][r]}" for c in viol]}


def summarize(cases: list) -> dict:
    rules = list(validators.CAPS) + [r for r in validators.HUMANIZE_CAPS if any(r in c["metrics"] for c in cases)]
    per_rule = {}
    for r in rules:
        after = _rule_stats(cases, r, "metrics", "cap_pass")
        before = _rule_stats(cases, r, "metrics_before", "cap_pass_before") if r in validators.CAPS and any(c.get("metrics_before") for c in cases) else None
        per_rule[r] = dict(after, before=before)
    forced = []
    for c in cases:
        for f in c["forced"]:
            forced.append(dict(f, song_id=c["song_id"], seed=c["seed"], humanize=c["humanize"]))
    rep_rules: dict = {}
    for c in cases:
        for k, v in c["repairs_by_rule"].items():
            rep_rules[k] = rep_rules.get(k, 0) + v
    unforced_fail = [c for c in cases if not c["all_caps_pass"] and not c["forced"]]
    return {"n_cases": len(cases), "n_cases_all_caps_pass": sum(1 for c in cases if c["all_caps_pass"]),
            "n_cases_all_caps_pass_before": sum(1 for c in cases if c.get("all_caps_pass_before")) if any(c.get("metrics_before") for c in cases) else None, "per_rule": per_rule,
            "n_forced": len(forced), "forced": forced, "n_forced_realized": sum(1 for f in forced if f.get("realized", True)),
            "n_realized_keys_violations": sum(len(c["realized_keys_violations"]) for c in cases),
            "n_harmony_junction_retries": sum(v["retries"] for c in cases for v in c["harmony_junction"].values()), "n_repairs_total": sum(c["n_repairs"] for c in cases), "repairs_by_rule": rep_rules,
            "n_cases_failing_without_forced": len(unforced_fail),
            "cases_failing_without_forced": [f"{c['song_id']}|seed={c['seed']}|{'humanize' if c['humanize'] else 'plain'}" for c in unforced_fail]}


def markdown(summary: dict, meta: dict) -> str:
    nb = summary.get("n_cases_all_caps_pass_before")
    L = [f"# Seed sweep {meta['stamp']}", "", f"seeds {meta['seeds'][0]}..{meta['seeds'][-1]} x 3 fixtures x modes {meta['modes']} = {summary['n_cases']} cases; "
         f"bars {meta['n_bars']}; all caps pass in {summary['n_cases_all_caps_pass']}/{summary['n_cases']} cases after the repair pass"
         + (f" ({nb}/{summary['n_cases']} before it)" if nb is not None else "") + f"; repairs applied {summary['n_repairs_total']} ({summary['repairs_by_rule']}); "
         f"forced violations {summary['n_forced']} ({summary['n_forced_realized']} realised on the song's chord pairs; {summary['n_realized_keys_violations']} realised keys-rule "
         f"violations in all); harmony junction re-samples {summary['n_harmony_junction_retries']}.", "",
         "`before` = the same seed composed with repair_pass=False (constructive layers only); `after` = with repair.py. Counts are the validators' raw metrics "
         "(total = summed over cases where the metric is a count). A forced keys_voicing flag sits on a LABEL slot and so appears at every recurrence; "
         "`realized` says whether that recurrence's actual neighbour violates.", "",
         "| rule | cap | cases violating before | after | max count before | after | total count before | after |", "|---|---|---|---|---|---|---|---|"]
    for r, s in summary["per_rule"].items():
        cap = validators.ALL_CAPS[r]
        b = s.get("before") or {}
        L.append(f"| {r} | {cap['op']} {cap['cap']} ({cap['per']}) | {b.get('n_cases_violating', '-')} | {s['n_cases_violating']} | {b.get('max_count', '-')} | {s['max_count']} | "
                 f"{b.get('total_count', '-')} | {s['total_count']} |")
    L += ["", "## Forced violations (logged with reason)", ""]
    if not summary["forced"]:
        L.append("none")
    for f in summary["forced"]:
        L.append(f"- {f['song_id']} seed={f['seed']} {'humanize' if f['humanize'] else 'plain'} bar {f.get('bar')} slot {f.get('slot', f.get('beat'))}: {f['rule']}"
                 f"{'' if f.get('realized', True) else ' (not realised at this recurrence)'} — {f.get('reason')}")
    L += ["", "## Cases failing a cap without a forced violation", ""]
    L += [f"- {c}" for c in summary["cases_failing_without_forced"]] or ["none"]
    return "\n".join(L) + "\n"


def sweep(seeds: list, n_bars: int, bpms: list, modes: list, before: bool = True, log=print, models: dict | None = None) -> tuple[list, dict]:
    models = models or load_models(None, fixtures=True)
    donors = sorted(FIXTURE_DONORS)
    cases = []
    for seed in seeds:
        for hum in modes:
            for i, donor in enumerate(donors):
                c = run_case(models, seed, float(bpms[i % len(bpms)]), donor, f"gen_v6_song_{i + 1}", n_bars, hum, before)
                cases.append(c)
                bad = [k for k, v in c["cap_pass"].items() if not v]
                bad_b = [k for k, v in (c["cap_pass_before"] or {}).items() if not v]
                log(f"seed {seed:2d} {'humanize' if hum else 'plain   '} {c['song_id']} {c['wall_s']:.2f}s repairs={c['n_repairs']} forced={len(c['forced'])} "
                    f"before={'PASS' if not bad_b else 'FAIL ' + ','.join(bad_b)} after={'PASS' if c['all_caps_pass'] else 'FAIL ' + ','.join(bad)}")
    return cases, summarize(cases)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 multi-seed validator sweep over the fixture songs")
    ap.add_argument("--seeds", default="0-11")
    ap.add_argument("--bars", type=int, default=32)
    ap.add_argument("--bpm", default=",".join(str(int(b)) for b in DEFAULT_BPM))
    ap.add_argument("--modes", default="plain,humanize")
    ap.add_argument("--out-dir", default="data/v6/gen/sweeps")
    ap.add_argument("--stamp", default=None, help="file stamp (default: UTC now, %%Y%%m%%dT%%H%%M%%SZ)")
    ap.add_argument("--no-before", action="store_true", help="skip the second (repair_pass=False) compose per case: no 'before' columns")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    seeds = parse_seeds(args.seeds)
    modes = [m.strip() == "humanize" for m in args.modes.split(",") if m.strip()]
    stamp = args.stamp or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_dir = Path(args.out_dir) if Path(args.out_dir).is_absolute() else WS / args.out_dir
    cases, summary = sweep(seeds, args.bars, [float(x) for x in args.bpm.split(",")], modes, not args.no_before, (lambda *a: None) if args.quiet else print)
    meta = {"stamp": stamp, "seeds": seeds, "n_bars": args.bars, "bpm": args.bpm, "modes": args.modes, "before": not args.no_before}
    doc = {"schema_version": 1, "meta": meta, "summary": summary, "cases": cases, "caps": validators.CAPS}
    write_json_atomic(out_dir / f"seed_sweep_{stamp}.json", doc)
    md = markdown(summary, meta)
    (out_dir / f"seed_sweep_{stamp}.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {out_dir / f'seed_sweep_{stamp}.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
