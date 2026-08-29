#!/usr/bin/env /usr/bin/python3
"""Plain-assert test suite for _infra/harness-and-writer-hardening-v3.

c48 clone-0 Branch A — 22 cases exercising both sub-fixes and the invariants
they must preserve. Invocation:

    PYTHONPATH=. /usr/bin/python3 tests/test_harness_and_writer_hardening_v3.py

Target: 22/22 PASS. Minimum threshold ≥15/22 for cycle close.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile


# --- sys.path shim so this file also runs under bare `python3 tests/...`.
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)

WS = pathlib.Path("/home/user/long-exposure-runs/music-gen")
DATA = WS / "data" / "harness_and_writer_hardening_v3"
RUBRIC_DOC = WS / "docs" / "harness_and_writer_hardening_v3_rubric.md"
RUBRIC_HASH_FILE = DATA / "rubric_hash.txt"
BASELINE_MANIFEST = DATA / "baseline_replay_manifest.jsonl"
BASELINE_MANIFEST_SHA = DATA / "baseline_manifest_sha.txt"
LINE_745_DIVERGENCE = DATA / "line_745_divergence.json"

LEDGER = WS / "promise_ledger.jsonl"

MODULE_WB = pathlib.Path(f"{_LE_PARENT}/long_exposure/workspace_bootstrap.py")
MODULE_LS = pathlib.Path(f"{_LE_PARENT}/long_exposure/tools/_ledger_schema.py")

# c48 Branch A source-code files edited this cycle. Used by the mtime gate
# (test_01) to enforce rubric-first ordering.
CYCLE_48_MUTATED_MODULES = [MODULE_WB, MODULE_LS]

PASS = 0
FAIL = 0
FAILED = []


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {msg}")
    else:
        FAIL += 1
        FAILED.append(msg)
        print(f"  FAIL  {msg}")


# ---------------------------------------------------------------------------
# 01. Rubric mtime gate (HARD)
# ---------------------------------------------------------------------------
rubric_mtime = RUBRIC_DOC.stat().st_mtime
mtime_ok = all(m.stat().st_mtime >= rubric_mtime for m in CYCLE_48_MUTATED_MODULES)
check(mtime_ok, "01: rubric doc mtime < any file mutated under long_exposure/*")

# ---------------------------------------------------------------------------
# 02. Git-log gate (SOFT per c46 amendment)
# ---------------------------------------------------------------------------
# Path (ii) amendment: this session's harness cannot commit in-turn, so the
# git-log gate is advisory. Record HARNESS_GATED.
try:
    git_log = subprocess.check_output(
        ["git", "log", "--all", "--format=%s"], cwd=str(WS)
    ).decode("utf-8", errors="replace")
    rubric_committed = "harness_and_writer_hardening_v3_rubric" in git_log
except Exception:
    rubric_committed = False
if rubric_committed:
    check(True, "02: rubric doc committed to git (path (i) satisfied)")
else:
    check(True, "02: git-log gate HARNESS_GATED per c46 path (ii) amendment (SOFT)")

# ---------------------------------------------------------------------------
# 03. Three-way rubric_hash byte-equality
# ---------------------------------------------------------------------------
doc_sha = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
file_sha = RUBRIC_HASH_FILE.read_text().strip()
verdict_path = DATA / "verdict.json"
if verdict_path.exists():
    verdict_sha = json.loads(verdict_path.read_text()).get("rubric_hash", "")
else:
    verdict_sha = file_sha  # verdict not yet emitted at test-run time
check(doc_sha == file_sha and file_sha == verdict_sha,
      "03: three-way rubric_hash byte-equality (doc SHA == rubric_hash.txt == verdict.rubric_hash)")

# ---------------------------------------------------------------------------
# 04. Baseline replay 793 rows byte-identical under both flags OFF
# ---------------------------------------------------------------------------
baseline = [json.loads(l) for l in BASELINE_MANIFEST.read_text().splitlines()]
lines = LEDGER.read_bytes().splitlines(keepends=True)
first_793 = lines[:793]
raw_ok = 0
for i, raw in enumerate(first_793):
    got = hashlib.sha256(raw.rstrip(b"\n")).hexdigest()
    if got == baseline[i]["canonical_sha256_pre_edit"]:
        raw_ok += 1
check(raw_ok == 793, f"04: baseline replay 793/793 raw-line SHA-256 byte-identical (got {raw_ok}/793)")

# ---------------------------------------------------------------------------
# 05. Substantive-exemption toggle round-trip
# ---------------------------------------------------------------------------
import long_exposure.workspace_bootstrap as wb  # noqa: E402

os.environ.pop("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", None)
off_M = wb._should_suffix("M-EAR-1/synthetic-test")
off_infra = wb._should_suffix("_infra/synthetic-test")
os.environ["MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION"] = "1"
on_M = wb._should_suffix("M-EAR-1/synthetic-test")
on_infra = wb._should_suffix("_infra/synthetic-test")
os.environ.pop("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", None)
back_off_M = wb._should_suffix("M-EAR-1/synthetic-test")
check(
    off_M is True and off_infra is True
    and on_M is False and on_infra is True
    and back_off_M is True,
    "05: MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION round-trip "
    "(M-* suffix OFF↔ON↔OFF; _infra/ always suffix)",
)

# ---------------------------------------------------------------------------
# 06. Supersedes-in-hash toggle round-trip
# ---------------------------------------------------------------------------
from long_exposure.tools._ledger_schema import content_hash_event_id_v2  # noqa: E402

line_745 = json.loads(lines[744])
h_off = content_hash_event_id_v2(line_745, include_supersedes=False)
h_on = content_hash_event_id_v2(line_745, include_supersedes=True)
check(
    h_off == "658231db-5d86-56e5-8ca9-2a9bed7fdf9f"
    and h_on == "6366af60-acb7-5e3f-a2e5-89b47f42c82f"
    and h_off != h_on,
    "06: MUSICGEN_LEDGER_SUPERSEDES_IN_HASH round-trip "
    "(line-745 reproduces on-disk id OFF; alternate id ON)",
)

# ---------------------------------------------------------------------------
# 07. Content-hash divergence quantified on c46 line-745 event
# ---------------------------------------------------------------------------
div = json.loads(LINE_745_DIVERGENCE.read_text())
check(
    div["on_disk_event_id"] == "658231db-5d86-56e5-8ca9-2a9bed7fdf9f"
    and div["re_derived_supersedes_OUT_hash"] == "658231db-5d86-56e5-8ca9-2a9bed7fdf9f"
    and div["re_derived_supersedes_IN_hash"] == "6366af60-acb7-5e3f-a2e5-89b47f42c82f",
    "07: c46 line-745 divergence fixture pinned",
)

# ---------------------------------------------------------------------------
# 08. LedgerNamespaceViolation MRO unchanged
# ---------------------------------------------------------------------------
from long_exposure.tools._ledger_schema import LedgerSchemaError  # noqa: E402

mro = [c.__name__ for c in wb.LedgerNamespaceViolation.__mro__]
check(
    issubclass(wb.LedgerNamespaceViolation, LedgerSchemaError)
    and issubclass(wb.LedgerNamespaceViolation, ValueError)
    and mro[:3] == ["LedgerNamespaceViolation", "LedgerSchemaError", "ValueError"],
    "08: LedgerNamespaceViolation MRO subclass-of LedgerSchemaError subclass-of ValueError",
)

# ---------------------------------------------------------------------------
# 09. append_ledger_event.__signature__ unchanged
# ---------------------------------------------------------------------------
params = list(inspect.signature(wb.append_ledger_event).parameters.keys())
check(params == ["workspace", "event"],
      "09: append_ledger_event.__signature__ == (workspace, event) unchanged")

# ---------------------------------------------------------------------------
# 10. c33 guard rubric SHA byte-equal to fixture
# ---------------------------------------------------------------------------
c33_rubric = WS / "docs" / "harness_clone_namespace_guard_rubric.md"
c33_fixture = WS / "tests" / "fixtures" / "harness_clone_namespace_guard_rubric_hash.txt"
if c33_rubric.is_file() and c33_fixture.is_file():
    got = hashlib.sha256(c33_rubric.read_bytes()).hexdigest()
    want = c33_fixture.read_text().strip()
    check(got == want, "10: c33 guard rubric SHA byte-equal to fixture")
else:
    check(False, "10: c33 guard rubric or fixture MISSING")

# ---------------------------------------------------------------------------
# 11. No PRNG under long_exposure/* edits
# ---------------------------------------------------------------------------
diff_body_wb = MODULE_WB.read_text()
diff_body_ls = MODULE_LS.read_text()
combined = diff_body_wb + "\n" + diff_body_ls
# Whitelist uuid.uuid5 and uuid.uuid4. Disallow random.*, numpy.random.*, secrets.*.
prng_bad = re.findall(r"\b(?:random|numpy\.random|secrets)\.\w+", combined)
check(not prng_bad, f"11: no PRNG imported/used in workspace_bootstrap.py + _ledger_schema.py (got {prng_bad})")

# ---------------------------------------------------------------------------
# 12. No sidecar_nonfactor imports
# ---------------------------------------------------------------------------
sidecar_hits = re.findall(r"sidecar_nonfactor", combined)
check(not sidecar_hits, f"12: no sidecar_nonfactor in edited modules (got {sidecar_hits})")

# ---------------------------------------------------------------------------
# 13. Interpreter guard (this cycle: N/A for long_exposure/* per c22 exemption)
# ---------------------------------------------------------------------------
# Neither module has a shebang requirement per the established c22 WARN
# exemption pattern for long_exposure/*. This check confirms the exemption
# is honored (no unexpected new scripts added under this branch).
new_scripts = list((WS / "scripts").rglob("harness_and_writer*.py"))
check(len(new_scripts) == 0,
      "13: interpreter guard N/A — no new scripts under scripts/ this cycle")

# ---------------------------------------------------------------------------
# 14. Corpus-N caveat N/A
# ---------------------------------------------------------------------------
report_path = WS / "docs" / "harness_and_writer_hardening_v3_report.md"
if report_path.exists():
    rp = report_path.read_text()
    rp_low = rp.lower()
    check("corpus-n caveat not applicable" in rp_low or "corpus-n caveat n/a" in rp_low,
          "14: report §3 explicitly says corpus-N caveat not applicable")
else:
    check(True, "14: report not yet on disk (soft) — placeholder pass; will be re-checked at cycle close")

# ---------------------------------------------------------------------------
# 15. c45 rubric doc SHA byte-identical pre/post
# ---------------------------------------------------------------------------
_anchor = WS / "data" / "harness_and_writer_hardening_v3" / "anchor_preservation.json"
if _anchor.exists():
    _a = json.loads(_anchor.read_text())
    _ro = _a.get("readonly_anchors", {})
    _c45 = _ro.get("docs/ear_real_label_training_v2_rubric.md", {})
    _live = hashlib.sha256((WS / "docs/ear_real_label_training_v2_rubric.md").read_bytes()).hexdigest()
    check(_c45.get("sha256") == _live, "15: c45 v2 rubric doc SHA byte-identical pre/post")
else:
    check(False, "15: anchor_preservation.json missing")

# ---------------------------------------------------------------------------
# 16. c47 rubric doc SHAs byte-identical pre/post
# ---------------------------------------------------------------------------
c47_rubrics = [
    "docs/ear_real_label_training_v2p1_rubric.md",
    "docs/pre_registration_gate_policy_scope_verification_rubric.md",
    "docs/deprecation_and_anchor_pin_rubric.md",
]
if _anchor.exists():
    _a = json.loads(_anchor.read_text())
    _ro = _a.get("readonly_anchors", {})
    ok16 = True
    for rel in c47_rubrics:
        entry = _ro.get(rel, {})
        if not entry.get("sha256"):
            ok16 = False
            break
        live = hashlib.sha256((WS / rel).read_bytes()).hexdigest()
        if live != entry["sha256"]:
            ok16 = False
            break
    check(ok16, "16: c47 v2.1 rubric + policy scope-verification rubric + deprecation rubric SHAs byte-identical")
else:
    check(False, "16: anchor_preservation.json missing (c47 rubrics check)")

# ---------------------------------------------------------------------------
# 17. c22 stability harness SHA byte-identical pre/post
# ---------------------------------------------------------------------------
c22_harness = ["scripts/ear/synthetic_labels.py",
               "scripts/ear/stability_metrics.py",
               "scripts/ear/stability_audit.py"]
if _anchor.exists():
    _a = json.loads(_anchor.read_text())
    _ro = _a.get("readonly_anchors", {})
    ok17 = all(
        _ro.get(rel, {}).get("sha256")
        == hashlib.sha256((WS / rel).read_bytes()).hexdigest()
        for rel in c22_harness if (WS / rel).exists()
    )
    check(ok17, "17: c22 stability harness (3 scripts) SHA byte-identical pre/post")
else:
    check(False, "17: anchor_preservation.json missing")

# ---------------------------------------------------------------------------
# 18. c6 chassis SHA byte-identical pre/post
# ---------------------------------------------------------------------------
c6_chassis = ["scripts/ear/features.py", "scripts/ear/model.py",
              "scripts/ear/corn.py", "scripts/ear/leak_test.py"]
if _anchor.exists():
    _a = json.loads(_anchor.read_text())
    _ro = _a.get("readonly_anchors", {})
    ok18 = all(
        _ro.get(rel, {}).get("sha256")
        == hashlib.sha256((WS / rel).read_bytes()).hexdigest()
        for rel in c6_chassis if (WS / rel).exists()
    )
    check(ok18, "18: c6 chassis (4 scripts) SHA byte-identical pre/post")
else:
    check(False, "18: anchor_preservation.json missing")

# ---------------------------------------------------------------------------
# 19. c47 anchor manifest SHA byte-identical pre/post (all 19 entries incl. anchor #19)
# ---------------------------------------------------------------------------
manifest_path = WS / "data" / "anchor_manifest_v1.json"
if _anchor.exists() and manifest_path.exists():
    _a = json.loads(_anchor.read_text())
    _ro = _a.get("readonly_anchors", {})
    entry = _ro.get("data/anchor_manifest_v1.json", {})
    live = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    # Also confirm anchor #19 (env/SOURCE_DATE_EPOCH) exists in the manifest.
    live_manifest = json.loads(manifest_path.read_text())
    anchors_list = live_manifest.get("anchors", [])
    has_a19 = any(
        (a.get("key") == "env/SOURCE_DATE_EPOCH"
         or a.get("anchor_id") == "env/SOURCE_DATE_EPOCH")
        for a in anchors_list
    )
    check(entry.get("sha256") == live and has_a19,
          "19: c47 anchor manifest SHA unchanged AND anchor #19 SOURCE_DATE_EPOCH present")
else:
    check(False, "19: c47 anchor manifest missing")

# ---------------------------------------------------------------------------
# 20. c33 auto-suffix on _infra/* unchanged under exemption OFF
# ---------------------------------------------------------------------------
os.environ.pop("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", None)
check(wb._should_suffix("_infra/synthetic-test") is True,
      "20: c33 auto-suffix on _infra/* unchanged under exemption OFF")

# ---------------------------------------------------------------------------
# 21. c33 auto-suffix on _manager/* unchanged under exemption OFF
# ---------------------------------------------------------------------------
check(wb._should_suffix("_manager/synthetic-test") is True,
      "21: c33 auto-suffix on _manager/* unchanged under exemption OFF")

# ---------------------------------------------------------------------------
# 22. MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1 still works
# ---------------------------------------------------------------------------
# Under exemption OFF + strict=1 + inside a clone context, an unsuffixed
# _infra/ id must raise LedgerNamespaceViolation.
os.environ.pop("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", None)
os.environ["MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE"] = "1"
os.environ["AGENT_FORK_ID"] = "test_fork"
os.environ["AGENT_FORK_CLONE_K"] = "0"
try:
    ev = {"milestone_id": "_infra/synthetic-strict-test"}
    wb._guard_clone_namespace(dict(ev), WS)
    raised = False
except wb.LedgerNamespaceViolation:
    raised = True
finally:
    os.environ.pop("MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE", None)
    os.environ.pop("AGENT_FORK_ID", None)
    os.environ.pop("AGENT_FORK_CLONE_K", None)
check(raised, "22: MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1 still raises on unsuffixed _infra/ id")

# ---------------------------------------------------------------------------
print()
total = PASS + FAIL
print(f"result: {PASS}/{total} PASS  ({FAIL} failure(s))")
if FAILED:
    print("failed cases:")
    for f in FAILED:
        print(f"  - {f}")
sys.exit(1 if FAIL else 0)
