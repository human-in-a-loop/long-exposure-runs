#!/usr/bin/env python3
"""Stage 33 (test 9/23) probes for final audit.

Probes:
1. Ratings manifest vs on-disk files: for each rating band {4,5,6,7},
   parse manifest rows, enumerate on-disk mp3s under corpus/ratings/<band>/,
   assert (a) file count matches manifest count per band OR docs the gap,
   (b) each on-disk mp3 filename encodes video_id or LOCAL sentinel,
   (c) count LOCAL vs YouTube video_id.
2. Egress-probe cycle coverage: enumerate ledger events matching
   ^M-INGEST-1/egress-probe.* per c49 policy A/B; assert every cycle
   in c46..c54 has >=1 probe row.
3. Test-file count and c51+ suite spot-check for pre-registered SHA anchors.
4. Full ledger validation via long_exposure.tools._ledger_schema.validate_event
   on every row.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

WD = Path("/home/user/long-exposure-runs/music-gen")
OUT_DIR = WD / "audits/final"
OUT = {}


def probe1_ratings_manifest():
    manifest = WD / "corpus/ratings/ratings_manifest.tsv"
    per_band = defaultdict(list)
    total_rows = 0
    with manifest.open(newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            total_rows += 1
            per_band[row["rating"]].append({
                "video_id": row["video_id"],
                "title": row["title"],
                "playlist_id": row["playlist_id"],
                "duration_s": row["duration_s"],
                "url": row["url"],
            })

    result = {"total_manifest_rows": total_rows, "per_band": {}}
    for band in ("4", "5", "6", "7"):
        band_dir = WD / f"corpus/ratings/{band}"
        if not band_dir.exists():
            result["per_band"][band] = {"error": "band_dir_missing"}
            continue
        files = sorted(p.name for p in band_dir.iterdir() if p.suffix == ".mp3")
        # Filename regex: NNN__VIDEOID__title.mp3 or NNN__LOCAL__pattern.mp3
        pat = re.compile(r"^(\d{3})__([A-Za-z0-9_-]+)__.*\.mp3$")
        parsed = []
        unparsed = []
        for fn in files:
            m = pat.match(fn)
            if m:
                parsed.append({"seq": m.group(1), "token": m.group(2), "fn": fn})
            else:
                unparsed.append(fn)
        local_count = sum(1 for p in parsed if p["token"] == "LOCAL")
        yt_count = sum(1 for p in parsed if p["token"] != "LOCAL")
        # Cross-check: how many YT tokens appear in manifest for this band?
        band_ytids = {r["video_id"] for r in per_band[band]}
        yt_in_manifest = sum(
            1 for p in parsed
            if p["token"] != "LOCAL" and p["token"] in band_ytids
        )
        yt_not_in_manifest = sum(
            1 for p in parsed
            if p["token"] != "LOCAL" and p["token"] not in band_ytids
        )
        result["per_band"][band] = {
            "manifest_rows": len(per_band[band]),
            "on_disk_mp3s": len(files),
            "parseable_filenames": len(parsed),
            "unparseable_filenames": unparsed,
            "local_files": local_count,
            "yt_files": yt_count,
            "yt_ids_matching_manifest": yt_in_manifest,
            "yt_ids_not_in_manifest": yt_not_in_manifest,
        }
    OUT["probe1_ratings_manifest"] = result


def probe2_egress_probe_coverage():
    ledger = WD / "promise_ledger.jsonl"
    per_cycle = defaultdict(list)
    total_probes = 0
    with ledger.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            mid = ev.get("milestone_id", "")
            if mid.startswith("M-INGEST-1/egress-probe"):
                total_probes += 1
                cycle = ev.get("cycle")
                per_cycle[cycle].append({
                    "milestone_id": mid,
                    "status": ev.get("status"),
                    "agent": ev.get("agent"),
                })
    result = {
        "total_probe_events": total_probes,
        "unique_cycles": sorted(per_cycle.keys()),
        "per_cycle_counts": {c: len(v) for c, v in sorted(per_cycle.items())},
    }
    # Coverage check c46..c54
    missing = [c for c in range(46, 55) if c not in per_cycle]
    result["missing_cycles_c46_c54"] = missing
    result["coverage_verdict"] = "PASS" if not missing else "GAP"
    OUT["probe2_egress_probe_coverage"] = result


def probe3_test_suites():
    tests_dir = WD / "tests"
    test_files = sorted(p.name for p in tests_dir.glob("test_*.py"))
    # spot-check for c51+ suites (rc7, rc10, harness-and-writer-v3, etc.)
    c51_plus_patterns = [
        "test_rc7_v2_rerun.py",
        "test_rc10_guitar_piano.py",
        "test_rc10_drums_bass.py",
        "test_c48_shadow_ledger_reconciliation.py",
        "test_harness_and_writer_hardening_v3.py",
        "test_pre_reg_policy_verify.py",
    ]
    presence = {name: (tests_dir / name).exists() for name in c51_plus_patterns}
    # For each present suite, quick sanity: does file contain sha256 references?
    sha_refs = {}
    for name, present in presence.items():
        if present:
            try:
                content = (tests_dir / name).read_text()
                sha_refs[name] = {
                    "line_count": content.count("\n"),
                    "mentions_sha256": "sha256" in content.lower() or "sha_256" in content.lower(),
                    "mentions_rubric_hash": "rubric_hash" in content,
                }
            except Exception as e:
                sha_refs[name] = {"error": str(e)}
    OUT["probe3_test_suites"] = {
        "total_test_files": len(test_files),
        "c51_plus_expected": presence,
        "c51_plus_sha_refs": sha_refs,
    }


def probe4_full_ledger_validation():
    # Import validate_event
    sys.path.insert(0, str(WD))
    try:
        from long_exposure.tools._ledger_schema import validate_event
    except Exception as e:
        OUT["probe4_full_ledger_validation"] = {"error": f"import failed: {e}"}
        return

    ledger = WD / "promise_ledger.jsonl"
    total = 0
    valid = 0
    invalid = []
    with ledger.open() as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as e:
                invalid.append({"line": lineno, "error": f"json: {e}"})
                continue
            try:
                validate_event(ev)
                valid += 1
            except Exception as e:
                invalid.append({
                    "line": lineno,
                    "milestone_id": ev.get("milestone_id"),
                    "error": str(e)[:300],
                })
    OUT["probe4_full_ledger_validation"] = {
        "total_events": total,
        "valid": valid,
        "invalid_count": len(invalid),
        "invalid_first_20": invalid[:20],
        "verdict": "PASS" if not invalid else "FAIL",
    }


if __name__ == "__main__":
    probe1_ratings_manifest()
    probe2_egress_probe_coverage()
    probe3_test_suites()
    probe4_full_ledger_validation()
    out_path = OUT_DIR / "_stage33_results.json"
    out_path.write_text(json.dumps(OUT, indent=2, sort_keys=True))
    print(f"Wrote {out_path}")
    # print short summary
    for k, v in OUT.items():
        print(f"\n=== {k} ===")
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, (dict, list)) and len(str(vv)) > 200:
                    print(f"  {kk}: <{type(vv).__name__} of len {len(vv)}>")
                else:
                    print(f"  {kk}: {vv}")
