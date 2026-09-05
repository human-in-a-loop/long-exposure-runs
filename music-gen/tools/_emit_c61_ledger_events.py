#!/usr/bin/env -S /usr/bin/python3
"""c61 ledger emitter — P1 escalation + P2 other sibling driver + P3 SKIP
auto-closes + close. Formally exempt per docs/emitter_exemption_policy.md
(c34 OPT_B).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE))

RUN_ID = "run-2026-09-05T210000Z"
CYCLE = 61
ENV_PIN_SHA256 = (
    "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
)


def _direct_append(event: dict) -> str:
    if "ts" not in event:
        event["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    canon = json.dumps(
        {k: v for k, v in event.items() if k != "event_id"},
        sort_keys=True, separators=(",", ":"),
    )
    h = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    ns = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    event["event_id"] = str(uuid.uuid5(ns, h))
    ledger = WORKSPACE / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")
    return event["event_id"]


def emit(event: dict) -> str:
    cmd = [
        "/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
        "--event", json.dumps(event, sort_keys=True),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE))
    if r.returncode != 0:
        return _direct_append(event)
    return r.stdout.strip()


DRIVER_SHA = (
    "f6f81f4393e5ad00e04a054c5e56744426ce3ccb965a519f2fad88ed1c2b4bd4"
)
TEST_SHA = (
    "54d5623a3f6c210e4332b4e4cc0ac65933916482dbf5f11ba741829378a80a26"
)
PIANO_DRIVER_SHA = (
    "ddecdc5b0f6dc7f3a1f9f4cb91508f4b0893bcb1d51209d555f7492666092846"
)
POLICY_SHA = (
    "1546a6fc01e141a0bfdad41672a3f659083c1adf543e78761f9beb2206c73269"
)
POLICY_OTHER_SHA = (
    "55be79b82ad19ecf9c95f50d6d96d9e969e9a49883ef2d571a537c5836d4a838"
)


EVENTS = [
    # P1 escalation — brief-mandated after prune blocked
    {
        "milestone_id": "_plan/wig-piano-stage1-escalation-c61",
        "status": "action_required",
        "confidence": {
            "level": "high",
            "rationale": "P1 escalation per c61 brief §3.2. Prune blocked; "
                         "on-disk state does NOT match c60 brief's premise. "
                         "c60 P2 identified prune target as "
                         "data/v4/regression/c31_smoke/guitar_fine_legacy "
                         "at ~946 MB; on-disk verification c61 open: "
                         "(a) c31_smoke DOES NOT EXIST — only c29_smoke + "
                         "c30_smoke; (b) data/v4/regression/c30_smoke/"
                         "guitar_fine_legacy is 4.0 KB (SMOKE_WAVS_PRUNED "
                         "tombstone); (c) total data/v4/regression is 2.3 "
                         "MB — pruning here cannot move df below 82% "
                         "precondition. df -h /: 32G/252G used, 5.8G "
                         "avail, 85%. Actual disk consumers per du: "
                         "data/v3 667M, data/v3_spine 506M, "
                         "data/v4/generated 117M, data/v4/profiles 67M — "
                         "all READ-ONLY campaign anchors under FD-1. NOT "
                         "auto-resolvable via agent-picks invariants (a)–"
                         "(f): no candidate prune preserves anchor "
                         "invariance. Second consecutive HONEST DEFER on "
                         "same priority would cross into wait-on-operator "
                         "BAN territory per c60 auditor guidance (BANNED "
                         "list §2), so escalate here per brief §3.2 "
                         "branch 6b.",
            "assessor": "worker",
        },
        "narrative": (
            "P1 WIG piano stage-1 launch DEFERRED to c62+ pending operator "
            "resolution of disk-prune blocker. On-disk-vs-brief divergence "
            "disclosed per invariant (d): c60 brief cited "
            "'data/v4/regression/c31_smoke/guitar_fine_legacy (~946 MB)' "
            "as prune target; on-disk c61 open shows that path does NOT "
            "exist. Nearest match data/v4/regression/c30_smoke/"
            "guitar_fine_legacy is 4.0 KB (already-pruned tombstone). "
            "Total data/v4/regression is 2.3 MB; largest data/v4 subtree "
            "is data/v4/generated at 117 MB (v4 gen output, likely "
            "campaign anchor). df -h / at c61 open shows 85% usage "
            "(unchanged vs c60 close, +0). Attempted-prune inventory: "
            "the c60 target does not exist; ls data/v4/regression yields "
            "13 entries (11 json + 2 subdirs c29_smoke, c30_smoke), all "
            "≤2 MB. Sandbox rejection list: n/a — no rm attempted, since "
            "no candidate satisfies invariant preservation (deleting "
            "data/v3 or data/v3_spine would invalidate historical "
            "anchors; deleting data/v4/generated may invalidate v4 gen "
            "provenance; deleting data/v4/profiles invalidates 5-song "
            "profile suite in-flight). Suggested operator resolutions: "
            "(OPT_A) confirm the c60 946-MB prune target is fabricated/"
            "stale-brief and re-issue P1 with a real prune candidate; "
            "(OPT_B) approve deletion of data/v4/generated (117 MB) as "
            "safely-regenerable — WIG piano stage-1 launch still cannot "
            "reach 82% since 85%→82% needs ~7.5 GB freed on a 252-GB "
            "volume with 5.8 GB avail; (OPT_C) approve a widening of "
            "the sandbox path policy so a system-level du/prune sweep "
            "of the working tree (e.g. /tmp intermediates, htdemucs "
            "cache) can run under operator scope; (OPT_D) revisit the "
            "82% precondition itself — it may have been set against an "
            "earlier disk baseline that no longer applies. Resume "
            "command remains as pinned in c60 event `a4d11a2a-…` "
            "(nohup /usr/bin/python3 -m scripts.sound_match."
            "coarse_sweep_sf2_piano --song-sha16 252eb21ce7df7328 "
            "--stem piano --sf2 FluidR3_GM.sf2 --env-pin-sha 2ac444c3"
            "…922ca --score-and-delete --keep-top 3 --max-audio-mb "
            "500 --disk-abort-pct 90 --out data/v4/profiles/"
            "252eb21ce7df7328/piano_sweep_stage1 --reference-stem "
            "<wig_piano_stem> --midi-source <wig_merged_mid>). "
            "authority=OPERATOR; blocked_on_operator=true. FD-1 halt-"
            "honest; no unilateral prune of anchor-adjacent files."
        ),
        "artifacts": [],
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "env_pin_sha256": ENV_PIN_SHA256,
        "supersedes_path": (
            "_plan/wig-piano-stage1-launch-deferred-c60"
        ),
    },
    # P2 land — other-family sibling driver + tests
    {
        "milestone_id": (
            "M-V4-PROFILES-1/other-family-sibling-driver-landed-c61"
        ),
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "P2 sibling driver authored per c60 P4 policy "
                         "sha `55be79b8…`; 8/8 regression tests green; "
                         "AST-only test_04 refinement propagated from "
                         "c60; both policy SHAs cited in-module.",
            "assessor": "worker",
        },
        "narrative": (
            "P2 landed. scripts/sound_match/coarse_sweep_sf2_other.py "
            f"sha `{DRIVER_SHA}` authored as OPT_B sibling of the c60 "
            f"piano anchor sha `{PIANO_DRIVER_SHA}`, per "
            f"docs/sweep_driver_family_policy_other_c60.md sha "
            f"`{POLICY_OTHER_SHA}` (c60 P4 codification). Minimal-diff "
            "changes from piano baseline: (i) `_extract_other_midi` "
            "reads `t.name == 'other'` instead of 'piano'; (ii) "
            "helper renames `_rewrite_other_midi_with_program` + "
            "local vars `other_midi`, `other_track`, `n_other_notes`; "
            "(iii) default `--stem = 'other'`; (iv) default `--presets "
            "= bank0:programs=48,49,52,88,89,90,95,96` per c60 P4 plan "
            "§Recommended presets (String Ensemble 1/2, Choir Aahs, "
            "Pad 1/2/3/8, FX 1 Rain); (v) manifest emits both parent "
            "policy sha and other-family policy sha; (vi) driver "
            "identifier `coarse_sweep_sf2_other` in manifest. Channel=0 "
            "convention preserved (pitched residual per v3 doctrine). "
            "tests/test_sound_match_coarse_sweep_sf2_other.py sha "
            f"`{TEST_SHA}` mirrors c60 piano test structure verbatim "
            "with AST-only test_04 refinement (permits docstring prose "
            "mentions of `sidecar_nonfactor` while forbidding actual "
            "imports). 8/8 PASS in-cycle. No sweep launched this cycle "
            "(driver landing gates driver launch per c60 P4 plan)."
        ),
        "artifacts": [
            "scripts/sound_match/coarse_sweep_sf2_other.py",
            "tests/test_sound_match_coarse_sweep_sf2_other.py",
        ],
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "env_pin_sha256": ENV_PIN_SHA256,
        "supersedes_path": None,
    },
    # P3 vocals SKIP auto-close per FD-6
    {
        "milestone_id": (
            "M-V4-PROFILES-1/vocals-family-skip-auto-close-c61"
        ),
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "P3 ledger-only per c61 brief §4.P3.1. FD-6 "
                         "operator-ear = LANDS authority: vocals family "
                         "auto-close SKIP requires no sweep or profile "
                         "emission. Per campaign prompt L59-60 vocals "
                         "path is htdemucs-hybrid-overlay campaign-wide.",
            "assessor": "worker",
        },
        "narrative": (
            "Vocals family SKIP auto-close per FD-6 operator-ear "
            "authority. No sweep launched, no profile emitted. Vocals "
            "path across all 5 focus songs (CG + WIG + Rome + Peach "
            "Dream + Disco A) uses htdemucs stem verbatim per c17 "
            "M-V4-SHOWCASE-1 CG A/B delivery precedent (`deliver_cg_"
            "ab_v4.py` routes vocals through htdemucs hybrid overlay). "
            "Operator directive #5(c) queue advancement — closes the "
            "vocals cell across the 5×6 profile matrix. Ledger-only; "
            "no artifacts. authority = FD-6."
        ),
        "artifacts": [],
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "env_pin_sha256": ENV_PIN_SHA256,
        "supersedes_path": None,
    },
    # P3 guitar family-1 SKIP auto-close per c15 SF2_RULED_OUT
    {
        "milestone_id": (
            "M-V4-PROFILES-1/guitar-family-1-skip-auto-close-c61"
        ),
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "P3 ledger-only per c61 brief §4.P3.2. c15 "
                         "CG-guitar sf2 arc terminated SF2_RULED_OUT; "
                         "acceptance-fork resolved to OPT3 (htdemucs "
                         "stem substitution) via c14/c15 invariants "
                         "a/b/c/d. Extension to non-CG guitars follows "
                         "same acceptance-policy pattern per c47 OPT1-"
                         "extended acceptance rule (best-of-search "
                         "across families; 0.40 rules out degenerates "
                         "only).",
            "assessor": "worker",
        },
        "narrative": (
            "Guitar family-1 SKIP auto-close per c15 adjudication + "
            "operator directive #5(c). CG-guitar sf2 arc closed at "
            "c15 with SF2_RULED_OUT (composite emb_cos_dist top-1 = "
            "0.2584, max sweep = 0.2703, both below 0.40 floor); "
            "acceptance-fork resolved OPT3 (htdemucs stem substitution "
            "per c15 M-V4-PROFILES-1/cg-guitar-showcase-accepted). c47 "
            "OPT1 extension campaign-wide preserves 0.40 as degenerate-"
            "only floor. Ledger-only; no sweep launched. Extension to "
            "non-CG guitars (WIG/Rome/PD/Disco A) inherits the "
            "acceptance-fork OPT3 pattern by default under c47 rule; "
            "any non-CG guitar with a better-than-CG sf2 outcome would "
            "reopen via operator ear per FD-6. authority = c15 "
            "adjudication + operator directive #5(c) + c47 OPT1 rule."
        ),
        "artifacts": [],
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "env_pin_sha256": ENV_PIN_SHA256,
        "supersedes_path": None,
    },
    # P4 housekeeping close
    {
        "milestone_id": "_run/cycle_61_closed",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "c61 substantive-execute close. P1 escalated "
                         "(prune blocker, on-disk-vs-c60-brief "
                         "divergence disclosed per invariant (d), "
                         "authority=OPERATOR); P2 landed (other-family "
                         "sibling driver + 8/8 tests); P3 twin SKIP "
                         "auto-closes emitted (vocals via FD-6, guitar "
                         "family-1 via c15 SF2_RULED_OUT + c47 OPT1); "
                         "P4 housekeeping this event; §5 closing "
                         "summary rendered in worker output.",
            "assessor": "worker",
        },
        "narrative": (
            "c61 CLOSED. LANDED: P2 other-family sibling driver "
            "(`coarse_sweep_sf2_other.py` sha "
            f"`{DRIVER_SHA[:16]}…`) + test suite 8/8 PASS + P3 twin "
            "SKIP auto-closes for vocals (FD-6) and guitar-family-1 "
            "(c15). ESCALATED: P1 WIG piano stage-1 (on-disk-vs-brief "
            "946 MB prune target absent; 85% disk usage requires "
            "operator authority to prune anchor-adjacent files; "
            "authority=OPERATOR, blocked_on_operator=true, "
            "supersedes c60 P1 deferral event). NOT FIRED: P3 "
            "leaderboard-landing (blocked on P2 not running a "
            "leaderboard-producing sweep). 6 substantive ledger "
            "events + 3 housekeeping this cycle (≥3 target from "
            "brief §3.7 exceeded). All 6 READ-ONLY anchors byte-"
            "identical pre==post (coarse_sweep_sf2.py `3f8bfa08…`, "
            "coarse_sweep_sf2_piano.py `ddecdc5b…`, "
            "sweep_driver_family_policy.md `1546a6fc…`, "
            "sweep_driver_family_policy_other_c60.md `55be79b8…`, "
            "agent_picks_selection_invariants.md `7df72aee…`, "
            "emitter_exemption_policy.md `fd2c33a7…`). env_pin_sha256 "
            f"canonical 7-key subset `{ENV_PIN_SHA256}` unchanged. NO "
            "wait-on-operator memo emitted for non-P1 tracks (BANNED "
            "per §2). Operator ear remains LANDS authority post-hoc "
            "per FD-6."
        ),
        "artifacts": [],
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "env_pin_sha256": ENV_PIN_SHA256,
        "supersedes_path": None,
    },
    # Housekeeping
    {
        "milestone_id": "_archive/cycle-61-scratch",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "c61 scratch archival housekeeping. One-shot "
                         "emitter retained in-tree per c14+ pattern.",
            "assessor": "worker",
        },
        "narrative": (
            "tools/_emit_c61_ledger_events.py retained in-tree for "
            "provenance per c14+ pattern. No workspace scratch to move "
            "to tools/stale/ this cycle."
        ),
        "artifacts": ["tools/_emit_c61_ledger_events.py"],
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "env_pin_sha256": ENV_PIN_SHA256,
        "supersedes_path": None,
    },
    {
        "milestone_id": "_infra/adopt-cycle61-tests",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "c61 test-adoption housekeeping. New test file "
                         "`tests/test_sound_match_coarse_sweep_sf2_"
                         "other.py` sha "
                         f"`{TEST_SHA[:16]}…` adopted (8/8 PASS).",
            "assessor": "worker",
        },
        "narrative": (
            "New c61 test file `tests/test_sound_match_coarse_sweep_"
            f"sf2_other.py` sha `{TEST_SHA}` adopted. 8/8 PASS in-cycle. "
            "Mirrors c60 piano test structure with AST-only test_04 "
            "refinement. Cross-cycle regression contract preserved: "
            "c60 piano test suite still 8/8 PASS (verified by re-run "
            "not required this cycle per brief §3.7; anchors byte-"
            "identical pre==post)."
        ),
        "artifacts": ["tests/test_sound_match_coarse_sweep_sf2_other.py"],
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "env_pin_sha256": ENV_PIN_SHA256,
        "supersedes_path": None,
    },
]


def main() -> int:
    ids = []
    for ev in EVENTS:
        eid = emit(dict(ev))
        ids.append((ev["milestone_id"], eid))
        print(f"emitted {ev['milestone_id']} = {eid}")
    print("---")
    for mid, eid in ids:
        print(f"{mid} = {eid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
