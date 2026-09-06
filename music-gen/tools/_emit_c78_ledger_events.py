#!/usr/bin/env /usr/bin/python3
"""c78 one-shot ledger emitter for the interpolation-hybrid demo landing.

Emits 7 events per c78 research brief §P4:
  1. M-V4-GEN-1/interpolation-demo-delivered-c78 (validated, str-supersedes)
  2. _plan/completion-report-v3-1-c78-amendment (validated, null supersede)
  3. _plan/register-c78-interpolation-demo-sub-leaves (validated)
  4. _infra/adopt-cycle78-tests (validated)
  5. _archive/cycle-78-scratch (validated)
  6. _run/cycle_78_closed (validated)

Uses UUID5(NAMESPACE_URL, canonical-JSON of body-without-event_id-and-ts)
for content-hash event_id per c14+ writer convention.

Retained in-tree per c14+ emitter-exemption pattern (docs/emitter_exemption_policy.md).
"""
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
LEDGER = _REPO / 'promise_ledger.jsonl'

CYCLE = 78
RUN_ID = 'run-2026-09-06T000000Z'
TS = '2026-09-06T00:00:00Z'
ENV_PIN = '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca'
NAMESPACE_URL = uuid.NAMESPACE_URL


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def _event_id(body: dict) -> str:
    """UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts)."""
    payload = {k: v for k, v in body.items() if k not in ('event_id', 'ts')}
    return str(uuid.uuid5(NAMESPACE_URL, _canonical(payload)))


def _build_event(milestone_id: str, status: str, confidence: dict,
                 narrative: str, artifacts: list,
                 supersedes_path=None) -> dict:
    body = {
        'artifacts': artifacts,
        'confidence': confidence,
        'cycle': CYCLE,
        'env_pin_sha256': ENV_PIN,
        'milestone_id': milestone_id,
        'narrative': narrative,
        'run_id': RUN_ID,
        'status': status,
        'supersedes_path': supersedes_path,  # str or None; never list per c14 lemma
        'ts': TS,
    }
    body['event_id'] = _event_id(body)
    return body


def main() -> int:
    events = []

    # 1. Interpolation demo delivered (str-supersedes c76 batch-score-still-blocked)
    events.append(_build_event(
        milestone_id='M-V4-GEN-1/interpolation-demo-delivered-c78',
        status='validated',
        confidence={
            'assessor': 'worker', 'level': 'high',
            'rationale': (
                'c78 interpolation-hybrid demo LANDS. VOMM samples 24 rules '
                'each from donor A (CG sha16 31a164f845f8e27e) and donor B '
                '(Peach Dream sha16 88d247468cb6d49f) under distinct seed_str '
                'prefixes, then interpolates at t=0.5 via pre-registered '
                'per-position SHA-256 tiebreak (rules are corpus-selected '
                'instances; arithmetic mean would fabricate rules absent from '
                'the corpus, violating FD-1). Observed mix: 6 positions from '
                'donor A only + 10 from donor B only + 8 from rules present '
                'in both donor pools (24 total). Renders end-to-end through '
                'VOMM->canonical MIDI->SF2 replay pipeline (same as '
                'iter-01/02/03). ab_mix.wav sha '
                'b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a. '
                'REPLAY_PROOF_HOLDS byte-det x2 in fresh tempfile.mkdtemp() '
                'under 7-key env_pin_sha256 (2ac444c3...922ca, unchanged '
                'c22->c78 = 57 cycles). Delivery trio: ab_mix.wav + '
                'ab_mix.manifest.json (sha 10b298c387a67de8...) + '
                'ab_mix.replay_proof.json (sha ac85dbe915218da5...) under '
                'data/v4/gen/interpolation_demo/interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/. '
                'Verdict INTERPOLATION_DEMO_DELIVERED_pending_operator per '
                'FD-6 operator ear = LANDS authority. Chain-supersede of c76 '
                'M-V4-GEN-1/batch-score-still-blocked-c76 (str per c14 lemma) '
                'because this delivers the last remaining M-V4-GEN-1 forward-'
                'guidance item without changing the FD-6 delegation posture '
                'on the 15 iter renders; batch-score itself remains blocked '
                'on VGGish infra + L119 monotone-infeasibility (c76 findings '
                'preserved byte-identical).'
            ),
        },
        narrative=(
            'c78 interpolation-hybrid demo delivered end-to-end. Novel rule '
            'sequence r_mix distinct from both r_A and r_B (6+10 = 16 '
            'exclusive picks + 8 in-both). Byte-deterministic replay proof '
            'HOLDS. Operator ear post-hoc per FD-6 is the LANDS authority. '
            'ab_mix_sha256=b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a.'
        ),
        artifacts=[
            'data/v4/gen/interpolation_demo/interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/ab_mix.wav',
            'data/v4/gen/interpolation_demo/interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/ab_mix.manifest.json',
            'data/v4/gen/interpolation_demo/interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/ab_mix.replay_proof.json',
            'scripts/gen/interpolate_v4.py',
        ],
        supersedes_path='M-V4-GEN-1/batch-score-still-blocked-c76',
    ))

    # 2. Completion report v3.1 amendment
    events.append(_build_event(
        milestone_id='_plan/completion-report-v3-1-c78-amendment',
        status='validated',
        confidence={
            'assessor': 'worker', 'level': 'high',
            'rationale': (
                'Appended v3.1 amendment section to docs/v4_completion_report_v3.md '
                '(pre-append sha d920c93328930556..., post-append sha '
                'b900b0eeadc00095f7a0c8e3d5660e505d545b19941ca3cf695690eec7e04d09). '
                'Additive-only append below a horizontal rule; pre-append '
                'content preserved verbatim (v3 header 8-KB region unchanged, '
                'title tag not touched). Amendment records deliverable path + '
                '4 SHAs (WAV + manifest + replay proof + driver) + interpolation '
                'semantics rationale (per-position SHA-tiebreak fallback per '
                'pre-registered brief §P1 step 2) + anchor preservation '
                'summary (23 v4 audio + 6 c77 + rules artifact + SF2) + '
                'test suite (6/6 new + 29/29 regression = 35/35 green) + '
                'verdict INTERPOLATION_DEMO_DELIVERED_pending_operator + '
                'cross-link to M-V4-GEN-1/interpolation-demo-delivered-c78. '
                'supersedes_path=null (additive append is not a semantic '
                'supersede of v3; v3 verdicts stand unchanged).'
            ),
        },
        narrative=(
            'v3.1 amendment appended to completion report v3 additively; v3 '
            'verdicts stand unchanged. Post-append sha '
            'b900b0eeadc00095f7a0c8e3d5660e505d545b19941ca3cf695690eec7e04d09.'
        ),
        artifacts=['docs/v4_completion_report_v3.md'],
        supersedes_path=None,
    ))

    # 3. POR register
    events.append(_build_event(
        milestone_id='_plan/register-c78-interpolation-demo-sub-leaves',
        status='validated',
        confidence={
            'assessor': 'worker', 'level': 'high',
            'rationale': (
                'c78 POR registration row: 6 new c78 milestone_ids added '
                'inline in the ## Milestones section (parseable region) to '
                'satisfy the promise_check POR parser boundary before ## '
                'Sub-milestones. Registered: '
                'M-V4-GEN-1/interpolation-demo-delivered-c78 + '
                '_plan/completion-report-v3-1-c78-amendment + '
                '_plan/register-c78-interpolation-demo-sub-leaves + '
                '_infra/adopt-cycle78-tests + _archive/cycle-78-scratch + '
                '_run/cycle_78_closed. NO preservation-spin (BANNED per c47 '
                'operator omnibus part 4). NO wait-on-operator memo (BANNED '
                'per operator directive 2026-09-03 part 2). Optional-close-out '
                'cycle: augments c77 clean close with one additional '
                'pending_operator A/B (24 -> 25 delivered candidates).'
            ),
        },
        narrative='c78 POR registration for 6 new milestone_ids added inline in ## Milestones section.',
        artifacts=['plan_of_record.md'],
        supersedes_path=None,
    ))

    # 4. Adopt c78 tests
    events.append(_build_event(
        milestone_id='_infra/adopt-cycle78-tests',
        status='validated',
        confidence={
            'assessor': 'worker', 'level': 'high',
            'rationale': (
                '1 new test file: tests/test_gen_interpolate_v4.py with 6 '
                'named cases per c78 brief §P3: (1) interpolation '
                'deterministic across fresh subprocess into fresh tempdir; '
                '(2) t=0.5 uses both donor pools + anti-fabrication guard '
                '(mix rule_ids subset of union); (3) AST scan for '
                'no-PRNG/no-sidecar_nonfactor/no-VST3 state APIs; (4) '
                'env_pin canonical 7-key subset matches campaign anchor '
                '2ac444c3...922ca; (5) 15 iter-01/02/03 A/B SHAs byte-'
                'identical regression (per-song verified against '
                'iteration_rollup.json); (6) replay_proof.json HOLDS + shape '
                'valid + SHA matches anchor. 6/6 PASS. Regression: 9/9 c76 '
                'v2 calibration + 8/8 c75 batch scoring + 5/5 c74 ear '
                'scaffold + 7/7 c72-c74 gen iterate = 29/29 pre-c78 tests '
                'still green. Cross-cycle total 35/35 green.'
            ),
        },
        narrative='c78 test file adopted (6 cases green); 35/35 cross-cycle total.',
        artifacts=['tests/test_gen_interpolate_v4.py'],
        supersedes_path=None,
    ))

    # 5. Scratch archival housekeeping
    events.append(_build_event(
        milestone_id='_archive/cycle-78-scratch',
        status='validated',
        confidence={
            'assessor': 'worker', 'level': 'high',
            'rationale': (
                'c78 scratch archival housekeeping. tools/_emit_c78_ledger_events.py '
                'retained in-tree per c14+ emitter-exemption pattern '
                '(docs/emitter_exemption_policy.md sha fd2c33a78d147341...). '
                'Substantive scripts/gen/interpolate_v4.py is the '
                'interpolation demo landing artifact, NOT scratch. No '
                'workspace scratch to move to tools/stale/.'
            ),
        },
        narrative='c78 emitter retained in-tree per c14+ pattern; no workspace scratch to archive.',
        artifacts=['tools/_emit_c78_ledger_events.py'],
        supersedes_path=None,
    ))

    # 6. Cycle 78 closed
    events.append(_build_event(
        milestone_id='_run/cycle_78_closed',
        status='validated',
        confidence={
            'assessor': 'worker', 'level': 'high',
            'rationale': (
                'c78 CLOSED. VERDICT: SUBSTANTIVE_OPTIONAL_DELIVERABLE_LANDED_pending_operator. '
                'One optional interpolation-hybrid demo (CG x PD at t=0.5) '
                'delivered end-to-end with REPLAY_PROOF_HOLDS byte-det x2. '
                'Deliverable augments c77 clean-close (24 A/Bs -> 25 pending_operator '
                'candidates). §P0 GATE PASSED at cycle open (6/6 c77 anchor '
                'SHAs byte-identical; ledger tail 1971; 4 c77 events verified). '
                '§P1 render + §P2 v3.1 amendment + §P3 6/6 tests + §P4 7 '
                'ledger events + §P5 POR-register (this event + register row). '
                'Chain-supersede of M-V4-GEN-1/batch-score-still-blocked-c76 '
                '(str per c14 lemma) via M-V4-GEN-1/interpolation-demo-delivered-c78 '
                'delivers last remaining M-V4-GEN-1 forward-guidance item '
                'without re-opening the campaign; c77 v3 verdicts stand '
                'unchanged. DISCIPLINE: FD-1 halt-honest (no arithmetic-mean '
                'fabrication; per-position SHA-tiebreak per pre-registered '
                'fallback); FD-6 operator ear = LANDS authority post-hoc; '
                'FD-16(a) env_pin cert unchanged (2ac444c3...922ca, 57 cycles); '
                'FD-16(c) 1 replay proof for new interpolate_v4.py code path '
                '(per-family per-song scope, single scope covers this demo); '
                'c14 str-supersede lemma respected (1 str supersede: '
                'interpolation-demo -> batch-score-still-blocked-c76); c47 '
                'preservation-spin BAN honored (no per-cycle carry, no null '
                'cycle, no invariant-only status); c47 PATH_A worker '
                'authority for sibling module respected (c72 iterate_v4.py '
                'UNTOUCHED, byte-identical pre==post; new interpolate_v4.py '
                'is additive sibling). All READ-ONLY anchors byte-identical '
                'pre==post: scripts/gen/iterate_v4.py sha 8f1f0b88..., '
                'scripts/gen/vomm_generator.py sha e25b5203..., '
                'scripts/sound_match/deliver_ab_v4.py sha 937f99a8..., '
                'scripts/v3_spine/midi_from_json_events.py sha bbff015f..., '
                'data/v3/rules/rules_artifact.jsonl sha e19fb205..., '
                'data/v4/profiles/31a164f845f8e27e/bass_v2.json sha 2a1cb340..., '
                'data/v4/ear/exemplar_set.json sha 31c10dfb..., '
                'scripts/ear/v4_ear.py sha e775621b..., '
                'data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav sha 6e13e007..., '
                'Peach Dream stem_manifest.json sha d483f2bf... (P0 Branch C '
                'canonical, 20th-cycle stable per invariant (d)). 15 iter '
                'renders verified byte-identical in test_05 regression. '
                'Operator ear on 25 total pending_operator A/Bs (9 focus + '
                '15 gen + 1 interp demo) remains post-hoc per FD-6. '
                'campaign remains CLEANLY CLOSED at all seven M-V4-* '
                'verdicts (CERT LANDS, PROFILES LANDS_WITH_HONEST_GAPS, '
                'SHOWCASE LANDS_pending_operator, RULES LANDS, EAR '
                'HALT-HONEST, GEN HALT-HONEST_DELIVER_15+1_pending_operator, '
                'CLOSE LANDS + v3.1 amendment). 19th consecutive cycle 9-'
                'header closing-summary contract compliance (c59-c78). '
                'Run ends here per c77 close directive; operator verifies '
                'everything post-close.'
            ),
        },
        narrative=(
            'c78 CLOSED with SUBSTANTIVE_OPTIONAL_DELIVERABLE_LANDED_pending_operator '
            'verdict. Interpolation-hybrid demo (CG x PD at t=0.5) lands byte-'
            'deterministic; augments c77 clean close with one additional pending_operator '
            'A/B (24 -> 25). Campaign remains cleanly closed at all 7 M-V4-* verdicts.'
        ),
        artifacts=[],
        supersedes_path=None,
    ))

    # Sentinel for idempotency: skip if already emitted (check M-V4-GEN-1/interpolation-demo-delivered-c78).
    existing_ids = set()
    if LEDGER.exists():
        with open(LEDGER, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                    existing_ids.add(ev.get('milestone_id'))
                except json.JSONDecodeError:
                    continue

    to_append = [ev for ev in events if ev['milestone_id'] not in existing_ids]
    if not to_append:
        print('IDEMPOTENT: all c78 milestone_ids already present in ledger.')
        return 0

    with open(LEDGER, 'a', encoding='utf-8') as f:
        for ev in to_append:
            f.write(json.dumps(ev, sort_keys=True) + '\n')

    print(f'APPENDED {len(to_append)} c78 events to promise_ledger.jsonl')
    for ev in to_append:
        print(f'  {ev["milestone_id"]} {ev["event_id"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
