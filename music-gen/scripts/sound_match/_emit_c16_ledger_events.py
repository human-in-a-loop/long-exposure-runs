#!/usr/bin/python3
"""Emit cycle-16 ledger events (append to promise_ledger.jsonl).

Mirror of c15 emitter shape.
"""
from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "promise_ledger.jsonl"
NS_LEDGER = uuid.uuid5(uuid.NAMESPACE_DNS, "music-gen.v4.ledger")


def _event_id(body: dict) -> str:
    payload = {k: v for k, v in body.items() if k not in ("event_id", "ts")}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(NS_LEDGER, canonical))


def emit(events: list[dict]) -> None:
    with open(LEDGER, "a") as f:
        for ev in events:
            ev.setdefault(
                "ts",
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            body = {k: ev[k] for k in ev if k != "event_id"}
            ev["event_id"] = _event_id(body)
            ordered = {k: ev[k] for k in sorted(ev.keys())}
            f.write(json.dumps(ordered, sort_keys=True) + "\n")


def main() -> int:
    run_id = "run-2026-09-04T110000Z"
    cy = 16
    common = {
        "agent": "worker",
        "cycle": cy,
        "run_id": run_id,
        "status": "validated",
        "confidence": {
            "assessor": "worker",
            "level": "high",
            "rationale": "on-disk artifacts sha-pinned in narrative",
        },
    }

    events: list[dict] = []

    # Track 1: diagnostic
    events.append({
        **common,
        "milestone_id": "_infra/embedding-metric-semantics-diagnosed-c16",
        "narrative": (
            "c16 Track 1 CRITICAL diagnostic: authored "
            "scripts/sound_match/probe_embedding_metric_semantics.py "
            "(SHA d6464d02f2d201d8...); imports scripts.texture."
            "embedding_panel READ-ONLY. Three-pair probe (A identity, "
            "B near-identity numerical, C bass vs drums real-content) "
            "returns Pair A=0.0, Pair B=0.0, Pair C=0.20050325552349146. "
            "Verdict metric_is=distance: an identical-input value of 0.0 "
            "decisively rules out similarity semantics (a similarity "
            "would return ~1.0 on identity). Diagnostic JSON at "
            "data/v4/diagnostics/embedding_metric_semantics.json (SHA "
            "2884dd3203f4e561...). Byte-det x2 REPLAY_PROOF_HOLDS at "
            "data/v4/diagnostics/embedding_metric_semantics.replay_proof."
            "json (SHA b3d74f5913bc0b05...). env_pin_sha256="
            "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842"
            "a922ca (7-key). Track 2 owns operator escalation; no "
            "prior verdict rewritten in this cycle per c15 auditor DO "
            "NOT. Pair C tightened during exploration from pure sines "
            "(0.19 — VGGish embeds sines too tightly) to real bass vs "
            "drums stems (0.20 clean above-identity ordering) — "
            "documented in probe module description."
        ),
        "artifacts": [
            "scripts/sound_match/probe_embedding_metric_semantics.py",
            "data/v4/diagnostics/embedding_metric_semantics.json",
            "data/v4/diagnostics/embedding_metric_semantics.replay_proof.json",
        ],
    })

    # Track 2: operator escalation
    events.append({
        **common,
        "status": "action_required",
        "confidence": {
            "assessor": "worker",
            "level": "high",
            "rationale": (
                "on-disk artifacts sha-pinned; agent-picks invariants "
                "do not disambiguate the two named paths; operator "
                "authority required per FD-16(a)"
            ),
        },
        "milestone_id": "_manager/M-V4-METRIC-SEMANTICS-c16",
        "narrative": (
            "c16 Track 2 CRITICAL operator escalation authored: "
            "data/v4/_manager/M-V4-METRIC-SEMANTICS-c16.json (SHA "
            "011a708e94989e6abb60d04dcea6d33c0b4a968b47e450a8896ddc"
            "9703473f59). status=action_required, authority=OPERATOR, "
            "blocked_on_operator=true, supersedes_path=null (new class). "
            "Two named paths: Path A (field is distance as named — "
            "thresholds inverted in interpretation; every prior CG "
            "verdict may re-read as strong-match on corrected sign); "
            "Path B (intended semantics is similarity — needs one-line "
            "panel or objective `1 - distance` correction; FD-16(a) "
            "cert re-issue trigger). Neither auto-resolvable via "
            "agent-picks invariants (a)/(b)/(c)/(d). Honest disclosure: "
            "systematic 5-arc pattern may reduce to threshold bug under "
            "Path A; M-V4-SHOWCASE-1 still shippable via OPT3 stems; "
            "operator ear remains LANDS authority per FD-6. NO prior "
            "verdict rewritten; NO acceptance-fork re-opened. DO NOT "
            "list per c15/c16 auditor guidance strictly honored."
        ),
        "artifacts": [
            "data/v4/_manager/M-V4-METRIC-SEMANTICS-c16.json",
        ],
    })

    events.append({
        **common,
        "milestone_id": (
            "_plan/embedding-metric-semantics-operator-escalation-c16"
        ),
        "narrative": (
            "c16 fork registration recording the two named paths + "
            "authority + diagnostic evidence anchor: Path A distance-"
            "as-named (thresholds inverted), Path B similarity-as-"
            "worded (numeric-contract fix). authority = FD-16(a) "
            "env_pin change → cert re-issue trigger + FD-6 operator "
            "ear = LANDS authority. supersedes_path=null (str-or-null "
            "per c14 lemma; here null because new escalation class). "
            "Diagnostic evidence anchor: data/v4/diagnostics/"
            "embedding_metric_semantics.json SHA 2884dd3203f4e561... "
            "metric_is=distance."
        ),
    })

    # Track 3: invariant (e) + test
    events.append({
        **common,
        "milestone_id": "_infra/pinned-profile-shape-invariant-e-c16",
        "narrative": (
            "c16 Track 3 MODERATE closure of c15 auditor MODERATE #2. "
            "Extended docs/agent_picks_selection_invariants.md (SHA "
            "c185718424bd5d93...) with invariant (e): cross-cycle "
            "pinned-profile shape stability. Canonical acceptance_fork "
            "shape codified as c14 drums anchor (4 nested keys chosen/"
            "rejected/authority/invariants_doc + top-level "
            "supersedes_path as str). c15 guitar drift (3 nested keys, "
            "invariants_doc folded into authority string) disclosed "
            "retroactively per invariant (d) as documented DRIFT "
            "precedent. c9 bass_v2 grandfathered. tests/test_pinned_"
            "profile_shape.py (SHA 0c1f5667117c4755..., 6/6 PASS) "
            "enforces the invariant: c14 drums canonical shape, c15 "
            "guitar drift, c9 grandfathered SHA-only, invariants doc "
            "carries (e), no PRNG/sidecar, supersedes_path never list. "
            "Recursion note: invariant (d) applied to the invariants "
            "framework itself."
        ),
        "artifacts": [
            "docs/agent_picks_selection_invariants.md",
            "tests/test_pinned_profile_shape.py",
        ],
    })

    # Track 4: adoption + tests
    events.append({
        **common,
        "milestone_id": "_infra/adopt-cycle15-scripts-c16-fillin",
        "narrative": (
            "c16 Track 4 adopts c15 new scripts under their milestone "
            "parents. c15 family-2 spike + builder + emit scripts + "
            "additive deliver_cg_ab_v4.py edit already landed at c15 "
            "with SHAs preserved: family2_stem_sampled_guitar_spike.py "
            "SHA 8adb676a5d7fde94..., family2_stem_sampled_guitar_"
            "builder.py SHA 8741a973af698f81.... Adoption row closes "
            "c15 auditor RECOMMENDED item #5 (WARN drift on c15 new "
            "scripts). One-shot emitters retained in tree per c14 "
            "pattern for provenance."
        ),
        "artifacts": [
            "scripts/sound_match/family2_stem_sampled_guitar_spike.py",
            "scripts/sound_match/family2_stem_sampled_guitar_builder.py",
            "scripts/sound_match/_c15_family2_guitar_emit.py",
            "scripts/sound_match/_emit_c15_ledger_events.py",
        ],
    })

    events.append({
        **common,
        "milestone_id": (
            "_infra/adopt-cycle14-guitar-stage2-tests-c16-fillin"
        ),
        "narrative": (
            "c16 Track 4 closes c15 auditor RECOMMENDED item #6 for "
            "c14 test debt. tests/test_sound_match_fine_fit_sf2_"
            "guitar.py (SHA d7ae0918feb61428..., 8/8 PASS): regression "
            "pins c14 leaderboard SHA b9335a639e63be00, run_manifest "
            "SHA 8e494c9b22d4d799, guitar.json SHA 5e6220ad9971e8fe, "
            "guitar.replay_proof.json SHA cc22105f2ff41509, guitar_"
            "family_verdict.json SHA cff0e3fbd4c2dd79. Asserts 180 "
            "distinct render SHAs, top-1 prog 28 composite 129.65 "
            "emb_cos 0.2584 (agnostic to Track 1 sign-convention "
            "diagnosis). Grid-deviation note (c15 Track 1 disclosure) "
            "documented in test docstring. tests/test_sound_match_"
            "audibility_measurement.py (SHA 5fde3b2cb27a1012..., 6/6 "
            "PASS): regression pins c14 piano_stem_audibility.json "
            "SHA af5bb2c03547ca0b + other_stem_audibility.json SHA "
            "5cc28e7f83c2d7ec; both verdict_audible=False; env_pin_"
            "sha256 recorded; orthogonal to Track 1 sign-convention "
            "outcome."
        ),
        "artifacts": [
            "tests/test_sound_match_fine_fit_sf2_guitar.py",
            "tests/test_sound_match_audibility_measurement.py",
        ],
    })

    events.append({
        **common,
        "milestone_id": (
            "_infra/adopt-cycle15-family2-guitar-tests-c16-fillin"
        ),
        "narrative": (
            "c16 Track 4 closes c15 test debt for family-2 stem-"
            "sampled guitar arc. tests/test_sound_match_family2_"
            "guitar.py (SHA eaace55b7da44a2b..., 8/8 PASS): regression "
            "pins c15 render.wav SHA f41560714a68415c, spike + builder "
            "script anchors byte-identical (READ-ONLY), profile + "
            "replay-proof + verdict SHAs pinned. Asserts 5 unique "
            "pitches / 37 voiced slices / 147 onsets bank shape, "
            "REPLAY_PROOF_HOLDS byte-det x2, FAMILY2_RULED_OUT verdict "
            "enum as-recorded. Enum interpretation under Track 1 "
            "diagnostic outcome is Track 2 operator scope, not the "
            "test's business — the test asserts the on-disk enum "
            "value only."
        ),
        "artifacts": [
            "tests/test_sound_match_family2_guitar.py",
        ],
    })

    # Track 5: POR + housekeeping
    events.append({
        **common,
        "milestone_id": (
            "_plan/register-c16-embedding-metric-semantics-diagnostic-"
            "and-invariant-e-sub-leaves"
        ),
        "narrative": (
            "c16 plan-of-record registration for all c16 sub-leaves. "
            "Adds rows for _infra/embedding-metric-semantics-diagnosed-"
            "c16, _manager/M-V4-METRIC-SEMANTICS-c16, _plan/embedding-"
            "metric-semantics-operator-escalation-c16, _infra/pinned-"
            "profile-shape-invariant-e-c16, _infra/adopt-cycle15-"
            "scripts-c16-fillin, _infra/adopt-cycle14-guitar-stage2-"
            "tests-c16-fillin, _infra/adopt-cycle15-family2-guitar-"
            "tests-c16-fillin, _archive/cycle-16-scratch, _infra/adopt-"
            "cycle16-tests, _run/cycle_16_closed. Closes promise_check "
            "drift on the newly emitted milestone_ids."
        ),
    })

    events.append({
        **common,
        "milestone_id": "_archive/cycle-16-scratch",
        "narrative": (
            "c16 scratch archival. Session-scoped scratchpad preserved "
            "under harness-managed dir (byte-det probe wrapper at "
            "/tmp/.../scratchpad/_byte_det_probe.sh). One-shot c16 "
            "ledger emitter scripts/sound_match/_emit_c16_ledger_"
            "events.py retained in tree for provenance per c14/c15 "
            "pattern. No workspace scratch to archive."
        ),
    })

    events.append({
        **common,
        "milestone_id": "_infra/adopt-cycle16-tests",
        "narrative": (
            "c16 test-adoption housekeeping. Carries three new c16 "
            "test files: tests/test_pinned_profile_shape.py (Track 3, "
            "6/6 PASS), tests/test_sound_match_fine_fit_sf2_guitar.py "
            "(Track 4 c14 fillin, 8/8 PASS), tests/test_sound_match_"
            "audibility_measurement.py (Track 4 c14 fillin, 6/6 PASS), "
            "tests/test_sound_match_family2_guitar.py (Track 4 c15 "
            "fillin, 8/8 PASS). Total 28 cases green (exceeds ≥22 "
            "brief target). Closes accumulated test-debt bookkeeping "
            "for c14 + c15."
        ),
        "artifacts": [
            "tests/test_pinned_profile_shape.py",
            "tests/test_sound_match_fine_fit_sf2_guitar.py",
            "tests/test_sound_match_audibility_measurement.py",
            "tests/test_sound_match_family2_guitar.py",
        ],
    })

    # Cycle closed rollup
    events.append({
        **common,
        "milestone_id": "_run/cycle_16_closed",
        "narrative": (
            "c16 CLOSED. Five tracks landed: (1) Track 1 CRITICAL "
            "diagnostic — probe empirically settles metric_is=distance "
            "via Pair A identity=0.0 decisive; byte-det x2 HOLDS. (2) "
            "Track 2 CRITICAL operator escalation authored with two "
            "named paths (A distance-inverted-thresholds, B "
            "similarity-numeric-fix); neither auto-resolvable via "
            "agent-picks; blocked_on_operator=true; NO prior verdict "
            "rewritten. (3) Track 3 MODERATE — invariant (e) cross-"
            "cycle pinned-profile shape stability codified; test 6/6 "
            "PASS. (4) Track 4 test debt cleanup — three new test "
            "files 22/22 PASS (c14 guitar stage-2 8, c14 audibility "
            "6, c15 family-2 guitar 8) plus c16 Track 3 shape test "
            "6/6. (5) Track 5 POR + housekeeping. M-V4-SHOWCASE-1 "
            "status unchanged: all 5 CG cells terminal; renderable_"
            "now=true; blocked on operator authority for Track 2 "
            "escalation, NOT on technical work. Operator ear remains "
            "LANDS authority post-hoc per FD-6."
        ),
    })

    emit(events)
    print(f"emitted {len(events)} events to {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
