#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T06:00:00Z
# cycle: 20
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-V4-RULES-1/scaffold-c20
# purpose: One-shot emitter for data/v4/rules/scaffold_smoke_test.json.
#          Retained in-tree per c14/c15/c16/c17/c18/c19 pattern.
# ---
"""Generate the M-V4-RULES-1 scaffold smoke-test JSON.

Records: fetchability outcomes for music21/mingus/jsonschema/sklearn
(no fetch attempted); scaffold stub verification (every entry point
raises NotImplementedError('c21+ substantive implementation')); env_pin
canonical 7-key subset with SHA anchor.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

CANDIDATES = ("music21", "mingus", "jsonschema", "sklearn")
CANONICAL_ENV_PIN = (
    "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
)


def probe_libraries() -> dict:
    out = {}
    for name in CANDIDATES:
        try:
            m = importlib.import_module(name)
            v = getattr(m, "__version__", None)
            loc = getattr(m, "__file__", None) or "<builtin>"
            out[name] = {
                "candidate": name,
                "no_fetch_attempts": True,
                "on_disk": True,
                "note": "importable",
                "version": v,
                "location": loc,
            }
        except Exception as exc:
            out[name] = {
                "candidate": name,
                "no_fetch_attempts": True,
                "on_disk": False,
                "note": type(exc).__name__,
            }
    return out


def probe_scaffold_stubs() -> dict:
    from scripts.v4_rules import extract_rules_v4 as pkg_stub
    from scripts.v4_rules.extract_v4 import (
        extract_rules_v4,
        list_corpus_songs,
        compute_rule_id,
    )
    entries = (
        ("scripts.v4_rules:extract_rules_v4", pkg_stub),
        ("scripts.v4_rules.extract_v4:extract_rules_v4", extract_rules_v4),
        ("scripts.v4_rules.extract_v4:list_corpus_songs", list_corpus_songs),
        ("scripts.v4_rules.extract_v4:compute_rule_id", compute_rule_id),
    )
    out = {}
    for name, fn in entries:
        try:
            fn()
            raised = None
            msg = None
        except NotImplementedError as e:
            raised = "NotImplementedError"
            msg = str(e)
        except Exception as e:
            raised = type(e).__name__
            msg = str(e)
        out[name] = {
            "raised": raised,
            "raised_message": msg,
            "contract_ok": (
                raised == "NotImplementedError"
                and msg == "c21+ substantive implementation"
            ),
        }
    return out


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    init_sha = sha256_of(ROOT / "scripts/v4_rules/__init__.py")
    extract_sha = sha256_of(ROOT / "scripts/v4_rules/extract_v4.py")

    stubs = probe_scaffold_stubs()
    libs = probe_libraries()

    smoke = {
        "kind": "m_v4_rules_1_scaffold_smoke_test",
        "cycle": 20,
        "run_id": "run-2026-08-28T040704Z",
        "created": "2026-09-04T06:00:00Z",
        "milestone_id": "M-V4-RULES-1/scaffold-c20",
        "scaffold_only": True,
        "substantive_implementation_deferred_to": "c21+",
        "env_pin_sha256": CANONICAL_ENV_PIN,
        "env_pin_keys": [
            "PYTHONHASHSEED",
            "SOURCE_DATE_EPOCH",
            "TZ",
            "LC_ALL",
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
        ],
        "scaffold_scripts": {
            "scripts/v4_rules/__init__.py": init_sha,
            "scripts/v4_rules/extract_v4.py": extract_sha,
        },
        "scaffold_stub_probes": stubs,
        "all_stubs_raise_c21_plus_notimplemented": all(
            v["contract_ok"] for v in stubs.values()
        ),
        "fetchability_probe": {
            "no_fetch_attempts": True,
            "note": (
                "Per c23 M-V3-RULES-1 pattern: on-disk-vs-blocked status "
                "recorded without any fetch attempted. Extractor at c21+ "
                "uses only pure stdlib + mido==1.3.3 (matches c23 "
                "predecessor)."
            ),
            "candidates": libs,
        },
        "readonly_v3_rules_anchors": {
            "scripts/v3_rules/extract_rules.py": (
                "9af3e37cfbe3338fd2ce693098398e08143753527970e852be822515bc5c89d2"
            ),
            "data/v3/rules/rules_artifact.jsonl": (
                "e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186"
            ),
        },
        "notes": [
            (
                "c20 scaffold contract per brief Track 1: stubs raise "
                "NotImplementedError with the exact message "
                "'c21+ substantive implementation'; smoke-test JSON "
                "documents fetchability + env_pin; no substantive "
                "extraction attempted."
            ),
            (
                "Track 2 escalation _manager/M-V4-METRIC-SEMANTICS-c16 "
                "remains blocked_on_operator=true; c20 does not "
                "adjudicate it."
            ),
            (
                "Invariant (d) on-disk-vs-brief divergence disclosure "
                "norm: no divergences to disclose this cycle."
            ),
        ],
    }

    out_path = ROOT / "data/v4/rules/scaffold_smoke_test.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(smoke, sort_keys=True, indent=2) + "\n")
    smoke_sha = sha256_of(out_path)

    print(f"WROTE {out_path}")
    print(f"scaffold_smoke_test.json sha256 = {smoke_sha}")
    print(f"scripts/v4_rules/__init__.py sha256 = {init_sha}")
    print(f"scripts/v4_rules/extract_v4.py sha256 = {extract_sha}")
    ok = smoke["all_stubs_raise_c21_plus_notimplemented"]
    print(f"all_stubs_raise_c21_plus_notimplemented = {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
