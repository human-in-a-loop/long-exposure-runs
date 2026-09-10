#!/usr/bin/python3
"""c87 (= harness c131, offset 44) EARLY ledger trio — emitted at turn start, as the work lands (MODERATE-8), before the
iteration-3 render completes:

  (a) _plan/adopt-operator-guidance-2026-09-09-c131   — the binding guidance quoted VERBATIM from the on-disk file
  (b) M-V5-GEN-1/F2-route-decided-c86                 — decided_at = mtime of data/v5/gen/f2_route_gate_c86.json (c86), ledgered_at = now (c87)
  (c) M-V5-GEN-1/F4-tempo-fix                          — validated/high CLOSED; supersedes data/v5/corpus/tempo_f4_verdict_c85.json

created: 2026-09-10T01:43:00Z
cycle: 87
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _archive/cycle-87-scratch

Every event carries `agent`; event_id = UUID5(NAMESPACE_URL, canonical JSON minus event_id/ts); idempotent on
(milestone_id, cycle == 87); supersedes_path is str|None (c14 lemma). df via `df -P` (driver semantics), NOT os.statvfs.
Retained in-tree per docs/emitter_exemption_policy.md.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 87
HARNESS_CYCLE = 131
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
G_131 = "docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt"
G_F2 = "docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt"
GATE = "data/v5/gen/f2_route_gate_c86.json"
RES = "data/v5/corpus/tempo_f4_operator_resolution_c86.json"
BLOCKED = "data/v5/corpus/recanonicalization_blocked.json"
STALE = "data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json"
PRE_SHA = "2fbabc07849dbe238545b9e629f91cd81746c6216e5db3027e88f4e9313f8a8e"
POST_SHA_EXPECTED = "eb78cfc0ce57dc9f50c68e2c683378cd0fe32a6feb4ab55276002ce64e6aa972"


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(p):
    return json.loads(Path(p).read_text())


def _iso(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def _df_pct() -> int:
    """`df -P .` Use% — the driver/df_check semantics (os.statvfs over-reports by the reserved blocks)."""
    out = subprocess.run(["df", "-P", "."], capture_output=True, text=True, check=True).stdout.splitlines()[-1].split()
    return int(out[4].rstrip("%"))


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _ev(milestone_id, status, level, rationale, narrative, artifacts, supersedes_path=None):
    body = {"agent": "worker", "artifacts": artifacts, "confidence": {"assessor": "worker", "level": level, "rationale": rationale},
            "cycle": CYCLE, "env_pin_sha256": ENV_PIN, "milestone_id": milestone_id, "narrative": narrative,
            "run_id": RUN_ID, "status": status, "supersedes_path": supersedes_path, "ts": TS}
    body["event_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, _canonical({k: v for k, v in body.items() if k not in ("event_id", "ts")})))
    return body


def main() -> int:
    g_text = Path(G_131).read_text()
    g_sha = _sha(G_131)
    gate = _j(GATE)
    decided_at = _iso(Path(GATE).stat().st_mtime)
    res = _j(RES)
    post_sha = _sha(BLOCKED)
    assert _sha(STALE) == PRE_SHA, "stale blocked copy drifted"
    assert post_sha == POST_SHA_EXPECTED, f"live blocked file drifted: {post_sha}"
    h23 = _j("data/v5/rules/harmony_markov_v5_full_c86.json")
    g23 = _j("data/v5/rules/groove_v5_v2_full_c86.json")
    df = _df_pct()
    events = []

    events.append(_ev("_plan/adopt-operator-guidance-2026-09-09-c131", "validated", "high",
        "operator guidance quoted verbatim from the on-disk file; sha256 pinned; adopted as the binding order of work for this cycle.",
        f"c87 (harness c131; offset 44 disclosed, not reconciled) adoption of OPERATOR GUIDANCE 2026-09-09 (c131) `{G_131}` (sha256 {g_sha}, sha16 {g_sha[:16]}, "
        f"{Path(G_131).stat().st_size} B). VERBATIM: <<<{g_text}>>> Consequences: (1) the five landed `velocities.json` are consumed AS-IS (all 5 present at turn start; "
        f"`velocity_profiles_v5.json` sha {_sha('data/v5/rules/velocity_profiles_v5.json')[:16]}… present on disk — on-disk authoritative, no re-extraction); iteration 3 launched DETACHED at turn start "
        f"(`data/v5/logs/gen_iter03_c87.launch.json`) after the P0 non-logic edits so the recorded script SHAs are final (generate_v5 {_sha('scripts/v5/generate_v5.py')[:16]}…, "
        f"midi_from_json_events_v5 {_sha('scripts/v5/midi_from_json_events_v5.py')[:16]}…; `velocity_v5.py` {_sha('scripts/v5/velocity_v5.py')[:16]}… NOT edited — pinned inside every velocities.json). "
        f"(2) Cross-cycle htdemucs stem SHA mismatch vs the c79 cache ACCEPTED — one ledger line, no memo, no regression bar. (3) F3 comping statistics + `--f3` default-off only after F2 lands. "
        f"No redesign, no route re-derivation, no retune (FD-1). df at emit {df} % (driver semantics).",
        [G_131, G_F2, "data/v5/logs/gen_iter03_c87.launch.json"]))

    events.append(_ev("M-V5-GEN-1/F2-route-decided-c86", "validated", "high",
        "decision timestamp is the route-gate file's own mtime (c86); this line is the c87 ledger record of a decision already taken — nothing re-derived.",
        f"ROUTE DECIDED = {gate['route']} — decided_at={decided_at} (mtime of `{GATE}`, gate ts field {gate['ts']}), ledgered_at={TS} (c87). Guidance `{G_F2}` sha16 {gate['guidance']['sha16']} "
        f"(on-disk sha {_sha(G_F2)[:16]}…). Gate readings: df {gate['df_used_pct_driver_semantics']} % ≤ 85 (driver semantics) ✓; htdemucs importable under /usr/bin/python3 + sub_env (torch {gate['torch_version']}) ✓; "
        f"full-song WIG separation {gate['separation_wall_s']} s ≤ 300 ✓ (decode {gate['decode_wall_s']} s; full.wav sha {gate['full_wav_sha256'][:12]}… == c79). Fresh stems did NOT match the c79 stage-cache SHAs "
        f"(separation_x2_holds={gate['separation_x2_holds']}) → the pre-registered in-cycle ×2 fallback applied and held on WIG; the cross-cycle mismatch is ACCEPTED per the c131 guidance (one line, no memo). "
        f"Not re-derived in c87 per the guidance.",
        [GATE, "scripts/v5/f2_route_gate_c86.py", "data/v5/logs/f2_route_gate_c86.log", G_F2]))

    events.append(_ev("M-V5-GEN-1/F4-tempo-fix", "validated", "high",
        "F4 CLOSED: operator adjudication recorded verbatim in c86; unblock recorded IN the blocked file (pre/post SHAs pinned); v5c recanonicalization ×2; n=23 chain consumed by the rules layer.",
        f"F4 TEMPO FIX CLOSED (ledgered c87 for the c86 landing): both tempo-blocked focus songs unblocked under operator authority (guidance sha16 8677bb0cd3f240a0 addendum) at "
        f"PD 88d247468cb6d49f = {res['adopted_bpm']['88d247468cb6d49f']} BPM and Disco A cdd2717e52820ff6 = {res['adopted_bpm']['cdd2717e52820ff6']} BPM (`{RES}` sha {_sha(RES)[:16]}…). "
        f"`{BLOCKED}` amended IN PLACE additively: pre-amend sha {PRE_SHA} preserved byte-identical as `{STALE}`; post-amend sha {post_sha}. `canonical_v5c_reindexed/` written for both songs at the adopted BPM "
        f"via the READ-ONLY c80 reindex + c4 serializer, byte-det ×2 (`data/v5/corpus/byte_determinism_c86.json`); `canonical_v5_reindexed/` untouched. Rules layer re-run at n=23: harmony {h23['degeneracy_verdict']}, "
        f"groove {g23['verdict']} (consumed from iteration 4; iteration 3 consumes n=21 by design). generate_v5.donor_tempo untouched so the flag-off replay of iteration 2 stays byte-identical. "
        f"Supersedes the c85 F4_HALF_DOUBLE_AMBIGUOUS verdict `data/v5/corpus/tempo_f4_verdict_c85.json` (sha {_sha('data/v5/corpus/tempo_f4_verdict_c85.json')[:16]}…, kept on disk). Tempo axis remains STOPPED (no criterion, no v5e).",
        [RES, BLOCKED, STALE, "data/v5/corpus/tempo_overrides_c86.json", "data/v5/corpus/byte_determinism_c86.json", "data/v5/rules/harmony_markov_v5_full_c86.json",
         "data/v5/rules/groove_v5_v2_full_c86.json", "data/v5/corpus/f4_close_report_c86.md", "tests/test_c86_f4_close.py"],
        supersedes_path="data/v5/corpus/tempo_f4_verdict_c85.json"))

    _le = os.environ.get("LONG_EXPOSURE_PKG_PATH", "/home/user/human-in-a-loop/long-exposure")
    if _le not in sys.path:
        sys.path.append(_le)
    try:
        from long_exposure.tools._ledger_schema import validate_event, REQUIRED_EVENT_FIELDS
        for e in events:
            miss = [k for k in REQUIRED_EVENT_FIELDS if k not in e]
            assert not miss, (e["milestone_id"], miss)
            errs = validate_event(e)
            assert not errs, (e["milestone_id"], errs)
    except ImportError:
        print("WARN: long_exposure schema not importable; field check only")
    for e in events:
        assert e["agent"] == "worker" and isinstance(e["supersedes_path"], (str, type(None)))
        for a in e["artifacts"]:
            assert Path(a).exists(), (e["milestone_id"], a)
    existing = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("cycle") == CYCLE:
                existing.add(row.get("milestone_id"))
    to_append = [e for e in events if e["milestone_id"] not in existing]
    if "--dry-run" in sys.argv:
        print(f"DRY RUN: {len(events)} events validated; would append {[e['milestone_id'] for e in to_append]}")
        return 0
    if not to_append:
        print("IDEMPOTENT: all c87 early milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c87 early events")
    for e in to_append:
        print(f"  {e['status']:12s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
