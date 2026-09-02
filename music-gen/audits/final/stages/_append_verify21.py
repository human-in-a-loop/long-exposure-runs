#!/usr/bin/env python3
"""Append 3 closure notes for verify_21of23 to findings.jsonl."""
import json
import pathlib
from datetime import datetime, timezone

FF = pathlib.Path("/home/user/long-exposure-runs/music-gen/audits/final/findings.jsonl")
ts = datetime.now(timezone.utc).isoformat()

rows = [
    {
        "ts": ts,
        "milestone_id": "M-INGEST-1/egress-ready-automation",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "narrative": (
            "Slice 21 verify pass: validated/high, cycle 8. 5 scripts under scripts/egress_ready/ "
            "(776 LOC total), 6 named fixture JSONLs under tests/fixtures/egress_status/ matching "
            "the plan-of-record scenarios exactly (all-false, single-true-then-back, two-consecutive-triggers, "
            "already-triggered-then-false, interleaved-then-true-true, stale-row-does-not-count). "
            "test_egress_ready_state.py enforces zero real subprocess.run at import time via _SubprocessRunForbidden. "
            "Grep-verified zero live network imports (urllib/requests/socket/httpx). "
            "No PRNG. Consumed downstream by M-EAR-1/armed-harness (c11) and the periodic egress-probe cycles c17-c54."
        ),
        "verdict": "CONFIRMED",
    },
    {
        "ts": ts,
        "milestone_id": "M-DAW-SPIKE-1/palette-assignment-schema",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "narrative": (
            "Slice 21 verify pass: validated, cycle 31 Branch B. JSON Schema draft 2020-12 (palette_v1.json) "
            "+ YAML mirror + two-layer validator + provenance module + 21 valid synthetic instances "
            "(7 drums + 7 bass + 7 other; exceeds >=20 spec) + 11 planted-invalid instances covering "
            "10 distinct rejection classes (exceeds >=8 spec, including duplicate_assignment_id as a class-10 pair). "
            "Content-derived UUID5 assignment_ids visible in filenames. rubric_hash.txt pinned at "
            "1493818cb276344e817a965c6d8b9d3cbfe02607e7cd741fdc46a1b3560ebce9. Follows M-RULES-1/schema pattern verbatim. "
            "Consumed downstream by M-TEX-1/palette-driven-bare-render (c33) and M-GEN-1/palette-driven-batch-v{1..4} (c34-c36)."
        ),
        "verdict": "CONFIRMED",
    },
    {
        "ts": ts,
        "milestone_id": "_manager/M-EAR-1-path-B-commit",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "narrative": (
            "Slice 21 verify pass: validated/high, cycle 26. 444-line commitment doc formalizes deferral of ear calibration "
            "to post-egress real labels after three-cycle Path A exhaustion (c22, c23, c25 all invalidated on 55-clip synthetic valset). "
            "Three frozen success bars with numeric thresholds derived from prior empirical results (SB1 IQR=0.5909090909 from c22 "
            "per_recipe_mae.tsv Q3-Q1; SB2 mean tau>=0.4 from c23 chassis-relaxed rubric; SB3 detection>=0.90 at alpha=1.0 per c6 protocol). "
            "Non-factor leak protocol explicit: artist parsed from title, genre honestly deferred (playlist_id aliased with rating band), "
            "era honestly deferred (no metadata pre-egress). 43/80 corpus-proximity caveat surfaced with expansion-ticket template. "
            "671-line synthetic-trigger fixture test exceeds the >=6 case bar substantially. Anchors the c36 v0, c37 v1, c45 v2, "
            "c46 SB3 widening, and c47 v2.1 Path B chain."
        ),
        "verdict": "CONFIRMED",
    },
]

with FF.open("a", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=True) + "\n")

print(f"appended {len(rows)} rows to {FF}")
print(f"findings.jsonl now has {sum(1 for _ in FF.open())} rows")
