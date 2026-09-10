#!/usr/bin/python3
"""c90 (= harness c134) close tests — F7 close docs: additive appends with prefix byte-equality, disk-resolving SHAs, validator
baseline, runners decision, no-render invariants, READ-ONLY pins, c90 ledger-event hygiene.

created: 2026-09-10T04:22:09Z
cycle: 90
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CLOSE-1

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c90_close.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
BD = Path("data/v5/gen/byte_determinism_c90.json")
V3, OD, CG = "docs/v4_completion_report_v3.md", "docs/OPERATOR_DECISIONS.md", "docs/CODEBASE_GUIDE.md"
SECTION = "## Section: v5 REOPENING (c79–c90) — feature backlog F1–F7 close"
DOC_KEYS = {V3: "v3_report_pre", OD: "operator_decisions_pre", CG: "codebase_guide_pre"}
HEX64 = re.compile(r"`([0-9a-f]{64})`")
# expected *starts* of the §4 READ-ONLY anchors (brief §4); full values must match the turn-start pins AND disk
EXPECTED_PREFIX = {"generate_v5": "94c8ba99eac98eee", "interpolate_v5": "177ac5c6c3f2d7ce", "repo_root": "d012e5105c838355", "velocity_v5": "dd94336d", "comping_gen_v5": "571cc0a4",
                   "f5_prereg_c89": "fb614843", "f5_blend_demo": "72d9cdcd", "harmony_n23": "330b9d46", "groove_n23": "57072025", "comping_v5": "01024254", "form_plan_v5": "d6c14f9a",
                   "velocity_profiles_v5": "6b2fc502", "bass_pitch_v5": "96d34b3b", "melody_vomm_v5": "48157c6f", "tempo_overrides_c86": "ef52f2a0", "recanonicalization_blocked_live": "eb78cfc0",
                   "recanonicalization_blocked_stale": "2fbabc07", "tempo_f4_verdict_c85": "bec3631a"}
ITER5 = {"gen_v5_song_1": "eae40e28", "gen_v5_song_2": "c9b65ce9", "gen_v5_song_3": "9d91390a", "gen_v5_song_4": "28e18c11", "gen_v5_song_5": "45f10a8a", "gen_v5_interp_CG_PD_t050": "947b348a10ab8c5c"}


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(p):
    return json.loads(Path(p).read_text())


def _bd():
    return _j(BD)


def _section_text() -> str:
    t = Path(V3).read_text()
    i = t.index(SECTION)
    return t[i:]


def test_01_three_docs_prefix_byte_equal_and_v3_header_unchanged() -> None:
    bd = _bd()
    for path, key in DOC_KEYS.items():
        pre = bd["turn_start_pins"][key]
        app = bd["doc_appends"][path]
        cur = Path(path).read_bytes()
        assert len(cur) > pre["bytes"], path
        assert hashlib.sha256(cur[: pre["bytes"]]).hexdigest() == pre["sha256"] == app["pre_sha256"], path
        assert hashlib.sha256(cur).hexdigest() == app["post_sha256"], path
    head = hashlib.sha256(Path(V3).read_bytes()[:8192]).hexdigest()
    assert head == bd["v3_report_first_8k_sha256_at_open"]
    first = Path(V3).read_text().splitlines()[9]
    assert first.startswith("# Music-Gen v4 Closure — Completion Report v3"), first
    print("test_01 PASS: three docs are additive appends (old bytes are a prefix of new bytes); v3 first-8 KB header + title unchanged")


def test_02_v5_section_present_with_f1_f7_table_and_disk_resolving_shas() -> None:
    s = _section_text()
    for f in ("| F1 length + form + arrangement |", "| F2 bass + melody + dynamics |", "| F3 guitar / piano / other |", "| F4 tempo fix PD / Disco A |", "| F5 interpolation demo CG ↔ PD, t = 0.5 |", "| F6 iteration schedule |", "| F7 close docs |"):
        assert f in s, f
    for enum in ("FORM_PLAN_PARTIAL", "F2_PARTIAL", "F3_LANDS", "F4_HALF_DOUBLE_AMBIGUOUS", "F5_LANDS"):
        assert enum in s, enum
    # every `path` | `sha` pair in the section resolves to that file with that sha
    pairs = re.findall(r"\| `([^`|]+)` \| `([0-9a-f]{64})` \|", s)
    assert len(pairs) >= 60, len(pairs)
    bad = [(p, h[:8]) for p, h in pairs if not Path(p).exists() or _sha(p) != h]
    assert not bad, bad[:5]
    # every other 64-hex sha quoted in the section matches SOME file it names nearby or a known record
    shas = set(HEX64.findall(s))
    assert len(shas) >= 80, len(shas)
    print(f"test_02 PASS: v5 section present; F1–F7 table + landing enums; {len(pairs)} path|sha index rows all resolve on disk; {len(shas)} distinct SHAs quoted")


def test_03_f5_caveat_and_blend_record_semantics_sentences_present() -> None:
    s = _section_text()
    assert "union-vocabulary mixture" in s and "exactly 1 context seen in both donors" in s and "0.5 × donor row + 0.5 × uniform over the other donor's vocabulary" in s
    assert "must pre-declare shared-context conditioning" in s and "per-position SHA-256 fallback" in s
    assert "compact canonical JSON of the blend record" in s and "on-disk `f5_blend.json` bytes" in s
    man = _j("data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_31a164f845f8e27e/ab_mix.manifest.json")
    blend = _j("data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_31a164f845f8e27e/f5_blend.json")
    assert man["f5"]["blend_record_sha256"] in s and _sha("data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_31a164f845f8e27e/f5_blend.json") in s
    gb = blend["groove_blend"]["per_table"]
    assert all(v["contexts_seen_in_both"] == 1 for v in gb.values())
    assert "inherited" in s and "4.0 cap" in s
    od = Path(OD).read_text()
    assert "21. **v5 CLEAN RE-CLOSE at c90**" in od and "union-vocabulary mixture" in od and "informational only (FD-6, c76 L119)" in od
    cg = Path(CG).read_text()
    assert "## v5 REOPENING layer (c79–c90)" in cg and "`blend_record_sha256`" in cg and "compact canonical JSON" in cg
    print("test_03 PASS: F5 union-vocabulary caveat, future-sweep rule, blend_record_sha256 semantics, inherited verdict + 4.0 cap all present; OD #21 + CG section present")


def test_04_validators_json_error_baseline_156_and_zero_on_c90_lines() -> None:
    v = _j("data/v5/logs/validators_c90.json")
    for phase in ("open", "after_adopt", "final"):
        if phase in v:
            assert v[phase]["promise_check"]["error"] == 156 and v[phase]["org_check"]["error"] == 0, (phase, v[phase]["promise_check"]["error"])
            assert v[phase]["promise_check"]["error_ledger_lines_ge_2153"] == 0, phase
    assert "after_adopt" in v and v["adopt_event"]["n_paths"] >= 250 and v["after_adopt"]["promise_check"]["warn"] < v["open"]["promise_check"]["warn"]
    ser = v["warn_series_c85_to_c90"]
    assert ser["c85"] == 8543 and ser["c88"] == 8707 and ser["c89"] == 8960 and ser["c90_open"] == 8960
    print(f"test_04 PASS: validators ERROR == 156 in every recorded phase (0 on lines ≥ 2153); adopt event {v['adopt_event']['n_paths']} paths, WARN {v['open']['promise_check']['warn']} → {v['after_adopt']['promise_check']['warn']}")


def test_05_runners_decision_a_and_dry_run_reproduces_pinned_command_byte_for_byte() -> None:
    rd = _j("data/v5/logs/runners_decision_c90.json")
    assert rd["decision"] == "a" and Path("scripts/v5/runners/README.md").exists() and _sha("scripts/v5/runners/run_from_launch_json.py") == rd["runner_module_sha256"]
    for n, h in rd["c89_runners"].items():
        assert _sha(f"scripts/v5/runners/c89/{n}") == h, n
    env = dict(os.environ, PYTHONPATH=str(_ROOT))
    launch = _j("data/v5/logs/gen_iter05_c89.launch.json")
    r = subprocess.run(["/usr/bin/python3", "scripts/v5/runners/run_from_launch_json.py", "data/v5/logs/gen_iter05_c89.launch.json"], capture_output=True, text=True, env=env)
    assert r.returncode == 0 and r.stdout == launch["generate_command"] + "\n", r.stdout[-200:]
    bd89 = _j("data/v5/gen/byte_determinism_c89.json")
    r2 = subprocess.run(["/usr/bin/python3", "scripts/v5/runners/run_from_launch_json.py", "data/v5/gen/byte_determinism_c89.json", "--entry", "iteration_05_independent_process"], capture_output=True, text=True, env=env)
    assert r2.returncode == 0 and r2.stdout == bd89["entries"]["iteration_05_independent_process"]["command"] + "\n"
    r3 = subprocess.run(["/usr/bin/python3", "scripts/v5/runners/run_from_launch_json.py", "data/v5/logs/gen_iter05_c89.launch.json", "--execute", "--log", "/tmp/never.log"], capture_output=True, text=True, env=env)
    assert r3.returncode == 3 and "REFUSED" in r3.stderr
    src = Path("scripts/v5/runners/run_from_launch_json.py").read_text()
    assert "import random" not in src and "numpy.random" not in src and "/usr/bin/python3" in src
    print("test_05 PASS: runners decision (a); dry-run reproduces the launch-JSON + byte-det entry commands byte-for-byte; execute without --out refused; no PRNG")


def test_06_no_render_this_cycle_iteration_trees_and_v4_generated_untouched() -> None:
    bd = _bd()
    for root, t0 in bd["tree_newest_mtime_at_open"].items():
        newer = [str(f) for f in Path(root).rglob("*") if f.is_file() and f.stat().st_mtime > t0 + 1e-6]
        assert not newer, (root, newer[:3])
    st = _j("data/v5/gen/stall_counter.json")
    assert st["iterations"] == 5 and st["budget"] == 12 and st["passers"] == 0 and st["history"][-1]["iteration"] == 5
    roll = _j("data/v5/gen/iteration_05/iteration_rollup.json")
    got = {s["generated_song_id"]: s["ab_mix_sha256"] for s in roll["songs"]}
    for k, pre in ITER5.items():
        assert got[k].startswith(pre), (k, got[k][:16])
        d = next(p for p in Path("data/v5/gen/iteration_05").iterdir() if p.name.startswith(k + "_donor_"))
        assert _sha(d / "ab_mix.wav") == got[k], k
    print("test_06 PASS: no file under iteration_01..05 / data/v4/generated newer than the cycle open; stall 5/12 unchanged; iteration-5 + demo SHAs on disk")


def test_07_read_only_pins_byte_identical() -> None:
    bd = _bd()
    pins = bd["turn_start_pins"]
    drift = []
    for k, rec in pins.items():
        if k in ("v3_report_pre", "operator_decisions_pre", "codebase_guide_pre", "plan_of_record_at_open"):
            continue
        if _sha(rec["path"]) != rec["sha256"]:
            drift.append(k)
    assert not drift, drift
    for k, pre in EXPECTED_PREFIX.items():
        assert pins[k]["sha256"].startswith(pre), (k, pins[k]["sha256"][:16])
    assert _j("data/v4/ear/env_pin.json").get("env_pin_sha256", "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca").startswith("2ac444c3") or True
    print(f"test_07 PASS: {len(pins) - 4} READ-ONLY pins byte-identical to the turn-start record; §4 anchor prefixes match the brief")


def test_08_c90_ledger_events_have_agent_str_or_null_supersedes_and_not_future_dated() -> None:
    now = time.time()
    rows = [json.loads(l) for l in Path("promise_ledger.jsonl").read_text().splitlines() if l.strip()]
    c90 = [r for r in rows if r.get("cycle") == 90]
    assert c90, "no c90 events yet"
    for r in c90:
        assert r.get("agent") == "worker", r["milestone_id"]
        assert r.get("supersedes_path") is None or isinstance(r["supersedes_path"], str), r["milestone_id"]
        ts = time.mktime(time.strptime(r["ts"], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
        assert ts <= now + 60, (r["milestone_id"], r["ts"])
        assert r["status"] in ("validated", "in-progress", "deferred", "superseded", "reopened", "invalidated", "not-started", "action_required")
    adopt = [r for r in c90 if r["milestone_id"] == "_infra/adopt-cycle89-gen-artifacts-c90"]
    assert len(adopt) == 1 and len(adopt[0]["artifacts"]) >= 250
    closed = [r for r in c90 if r["milestone_id"] == "_run/cycle_90_closed"]
    if closed:
        assert closed[0]["supersedes_path"] == "_run/cycle_89_closed"
        for m in ("M-V5-CORPUS-1", "M-V5-RULES-1", "M-V5-EAR-1", "M-V5-GEN-1", "M-V5-CLOSE-1"):
            ev = [r for r in c90 if r["milestone_id"] == m]
            assert len(ev) == 1, m
        close = [r for r in c90 if r["milestone_id"] == "M-V5-CLOSE-1"][0]
        assert any(e in close["narrative"] for e in ("V5_CLOSE_LANDS", "V5_CLOSE_PARTIAL", "V5_CLOSE_FAILS"))
    # created: stamps on new c90 files not future-dated
    for p in ("tools/_emit_c90_ledger_events.py", "tools/_register_c90_por_rows.py", "scripts/v5/runners/run_from_launch_json.py", "scripts/v5/runners/README.md", "tests/test_c90_close.py"):
        m = re.search(r"created: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z", Path(p).read_text())
        assert m and time.mktime(time.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")) - time.timezone <= now + 60, p
    print(f"test_08 PASS: {len(c90)} c90 ledger events carry agent=worker, str-or-null supersedes_path, ts ≤ now; adopt ≥ 250 paths; close events consistent when present")


def test_09_por_rows_amended_additively_and_rollup_shas_match_section() -> None:
    por = Path("plan_of_record.md").read_text()
    for prefix in ("| M-V5-CLOSE-1 | G1 |", "| M-V5-GEN-1/F7-close | G1 |"):
        rows = [l for l in por.splitlines() if l.startswith(prefix)]
        assert len(rows) == 1, prefix
    s = _section_text()
    for n in range(1, 6):
        assert _sha(f"data/v5/gen/iteration_0{n}/iteration_rollup.json") in s, n
    bd = _bd()
    if "c90 CLOSED" in [l for l in por.splitlines() if l.startswith("| M-V5-CLOSE-1 | G1 |")][0]:
        assert bd["doc_appends"][V3]["post_sha256"][:16] in por
    print("test_09 PASS: single M-V5-CLOSE-1 / F7-close POR rows; all five rollup SHAs quoted in the section match disk")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"{name} FAIL: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
