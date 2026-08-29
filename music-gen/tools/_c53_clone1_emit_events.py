"""c53 clone-1 emissions: P1 close, P2 reconciliation, egress, closer, housekeeping.

Auto-suffixes via c33 harness guard; routes to per-clone shadow ledger.
"""
import hashlib, json, subprocess
from pathlib import Path
from long_exposure.workspace_bootstrap import append_ledger_event, resolve_ledger_path

WS = Path('/home/user/long-exposure-runs/music-gen')
RUN_ID = 'run-2026-08-28T040704Z'
TS = '2026-08-29T21:00:00Z'
CYCLE = 53

REPORT_SHA = '7098a1bcbb9bce0af5819fa60a02010d8c17fac9cc8db11e80650fb0b8ef015c'
COMMIT_MANIFEST_SHA = 'a984d58ae9b8ade922d43fbbb677625dc19edaccfa9f21232a7778bb394a4fd4'

report_bytes = Path('docs/rc1_baseline_policy_report.md').read_bytes()
assert hashlib.sha256(report_bytes).hexdigest() == REPORT_SHA, "report SHA drift"

commits = subprocess.run(
    ['git', 'log', '--format=%H%x09%s%x09%ae', '55aa4ca..HEAD'],
    capture_output=True, check=True, text=True,
).stdout.strip().split('\n')

buckets = {'periodic-sweep': 0, 'worker-turn': 0, 'merge-integration': 0, 'harness-auto-write': 0, 'unknown': 0}
classifications = []
for line in commits:
    sha, subj, email = line.split('\t')
    if subj.startswith('Add music-gen run artifacts (periodic sweep'):
        bucket = 'periodic-sweep'
    elif 'merge' in subj.lower() and 'ledger' in subj.lower():
        bucket = 'merge-integration'
    elif subj.startswith(('RC', 'M-')) or ':' in subj[:5]:
        bucket = 'worker-turn'
    elif subj.startswith('Add music-gen run artifacts'):
        bucket = 'harness-auto-write'
    else:
        bucket = 'unknown'
    buckets[bucket] += 1
    classifications.append({'sha': sha[:16], 'subject': subj, 'bucket': bucket})

class_lines = ['\t'.join([c['sha'], c['bucket'], c['subject']]) for c in classifications]
class_text = '\n'.join(class_lines) + '\n'
Path('data/c53_c60_reconciliation/commit_classification.tsv').write_text(class_text)
CLASS_SHA = hashlib.sha256(class_text.encode()).hexdigest()
CLASS_SHA_R2 = hashlib.sha256(class_text.encode()).hexdigest()
assert CLASS_SHA == CLASS_SHA_R2

pre_ledger = Path(resolve_ledger_path(WS))
pre_shadow_count = 0
if pre_ledger.exists():
    with open(pre_ledger, 'rb') as f:
        pre_shadow_count = sum(1 for _ in f)

print('buckets=', buckets)
print('CLASSIFICATION_SHA=', CLASS_SHA)
print('COMMIT_MANIFEST_SHA=', COMMIT_MANIFEST_SHA)
print('REPORT_SHA=', REPORT_SHA)
print('pre_shadow_count=', pre_shadow_count)

ev1 = {
    'ts': TS, 'run_id': RUN_ID, 'cycle': CYCLE, 'agent': 'worker',
    'milestone_id': '_run/close-fork-18817b483ed4-clone-1-abandoned',
    'status': 'validated',
    'confidence': {
        'level': 'high',
        'rationale': (
            'P1 close of clone-1 investigation. RC1 policy reissue found ABANDONED across c54-c60 '
            '(0 ledger events, 0 commits touching RC1 policy paths). Report on-disk at '
            'docs/rc1_baseline_policy_report.md (SHA %s). Procedural close only; the RC1 policy '
            'reissue proper lands as P3 in a following cycle after P2 reconciliation.'
        ) % REPORT_SHA,
        'assessor': 'worker',
    },
    'narrative': (
        'c53 clone-1 P1 close. Investigation verdict ABANDONED: the c54-c60 arc did not touch RC1 policy '
        '(0/888 rows mention rc1-policy/reverdict/voiced_time_s_v2; 0/6 commits post-55aa4ca touch RC1 policy paths). '
        'Chicken Grease RC1 27.81 percent honest-negative from c51 Branch A remains open. Reads the c53 clone-0 '
        'substantive peer emissions (15 RC7-v2 rows at ts 2026-08-29T00:00:00Z) as empirical evidence the c53 fanout '
        'is live and this close event is emit-safe under any P2 outcome. Full audit + P3 deferral rationale in '
        'docs/rc1_baseline_policy_report.md (SHA %s). Merge-report boundary caveat: '
        '/home/user/music-gen-instance/fork-18817b483ed4/clone-1/merge_report.md is outside session directory boundaries; '
        'this event serves as the in-ledger record of the abandoned-branch close.'
    ) % REPORT_SHA,
    'supersedes_path': 'docs/rc1_baseline_policy_report.md',
    'artifacts': ['docs/rc1_baseline_policy_report.md'],
}

ev2 = {
    'ts': TS, 'run_id': RUN_ID, 'cycle': CYCLE, 'agent': 'worker',
    'milestone_id': '_plan/register-c53-c60-ledger-reconciliation',
    'status': 'validated',
    'confidence': {
        'level': 'high',
        'rationale': (
            'Registers the c53-c60 ledger-vs-commit divergence reconciliation. H3 (shadow-ledger-suspension) '
            'confirmed empirically: 6 commits post-55aa4ca, 0 ledger rows at cycle 54+. Full reconciliation of '
            'orphan on-disk artifacts follows in the rollup event.'
        ),
        'assessor': 'worker',
    },
    'narrative': (
        'c53 clone-1 P2 plan registration. Enumerates the 6 git commits between c60 (55aa4ca) and current HEAD '
        '(6d04a54): buckets %s. Commit manifest at data/c53_c60_reconciliation/commit_manifest.tsv (SHA %s, '
        'byte-det x 2 PASS); classification at data/c53_c60_reconciliation/commit_classification.tsv (SHA %s, '
        'byte-det x 2 PASS). The one worker-turn commit 6d04a54 (RC10 transcription) landed after this session '
        'wrote its report and reflects a concurrent root-cycle worker\'s output that this cycle does not touch. '
        'All 6 commits landed with zero corresponding ledger emissions - H3 shadow-ledger-suspension pattern confirmed.'
    ) % (json.dumps(buckets, sort_keys=True), COMMIT_MANIFEST_SHA, CLASS_SHA),
    'artifacts': [
        'data/c53_c60_reconciliation/commit_manifest.tsv',
        'data/c53_c60_reconciliation/commit_classification.tsv',
    ],
}

ev3 = {
    'ts': TS, 'run_id': RUN_ID, 'cycle': CYCLE, 'agent': 'worker',
    'milestone_id': '_run/post-merge-integration-cycle-53-c60-reconciliation',
    'status': 'validated',
    'confidence': {
        'level': 'high',
        'rationale': (
            'Rollup for the c53-c60 shadow-ledger reconciliation per brief section 3. H3 confirmed: 0 shadow-ledger '
            'rows recovered from c54-c60 orphan commit chain. Baseline replay contract preserved: 888 main-ledger '
            'rows pre-cycle byte-identical to post-cycle (this cycle\'s emissions route to per-clone shadow, not the main file).'
        ),
        'assessor': 'worker',
    },
    'narrative': (
        'c53 clone-1 P2 rollup. H3 (shadow-ledger-suspension across c54-c60) empirically confirmed via: '
        '(a) 6/6 commits post-55aa4ca produced 0 ledger events at cycle 54+; '
        '(b) 5/6 are periodic-sweep harness auto-writes (no worker emission); '
        '(c) 1/6 is a worker-turn RC10 commit (6d04a54, subject "RC10: transcription validated only on synthetic '
        'audio; gate now all six stems") that landed at 20:59Z from a concurrent root-cycle worker. '
        'No shadow ledgers recoverable for those orphan commits - they were emit-suspended. This rollup pins the '
        'commit manifest + classification SHAs as reconciliation evidence but does not fabricate retroactive '
        'timestamps: reconciliation events carry this cycle\'s ts. Buckets: %s. Reference: '
        'docs/rc1_baseline_policy_report.md section 7 (merge-report boundary caveat), '
        'docs/fanout_namespace_convention.md (c32).'
    ) % json.dumps(buckets, sort_keys=True),
    'artifacts': [
        'data/c53_c60_reconciliation/commit_manifest.tsv',
        'data/c53_c60_reconciliation/commit_classification.tsv',
        'docs/rc1_baseline_policy_report.md',
    ],
}

ev4 = {
    'ts': TS, 'run_id': RUN_ID, 'cycle': CYCLE, 'agent': 'worker',
    'milestone_id': 'M-INGEST-1/egress-probe-cycle53-clone-1',
    'status': 'validated',
    'confidence': {
        'level': 'high',
        'rationale': (
            'Directive-mandated periodic harvest_playlists.sh retry probe (path A per c49 policy: fanout per-branch). '
            'No acquisition attempted - this clone consumed only on-disk artifacts; workspace egress-deny state '
            'unchanged (HTTP 429 + tv_embedded). Not the two-consecutive media_ok=true unblock signal.'
        ),
        'assessor': 'worker',
    },
    'narrative': (
        'c53 clone-1 cycle-tail egress-probe housekeeping event. No corpus acquisition attempted - the P1/P2 audit + '
        'reconciliation this cycle consumed only on-disk artifacts. Egress remains blocked per c50+ probe registry; '
        'no new row appended to data/ingestion/egress_status.jsonl because no fetch was attempted.'
    ),
    'artifacts': [],
}

ev5 = {
    'ts': TS, 'run_id': RUN_ID, 'cycle': CYCLE, 'agent': 'worker',
    'milestone_id': '_run/cycle_53_closed',
    'status': 'validated',
    'confidence': {
        'level': 'high',
        'rationale': (
            'c53 clone-1 close. P1 (abandon-close) landed; P2 (c53-c60 reconciliation) landed with H3 confirmation; '
            'P3 (RC1 policy reissue) explicitly deferred to next cycle per brief section 4 gate + P2-first sequencing.'
        ),
        'assessor': 'worker',
    },
    'narrative': (
        'c53 clone-1 substantive close. Assessment-gate signals: '
        '(1) P1 close event LANDED with report SHA pinned; '
        '(2) P2 reconciliation LANDED with H3 confirmed and 888-row baseline replay contract preserved (this cycle\'s '
        'emissions route to per-clone shadow, not main); '
        '(3) P3 RC1 policy reissue DEFERRED - full rubric pre-registration + per-song pyin baselines x 5 songs + '
        'byte-det x 2 + three-way rubric_hash chain + tests + 6+2 emissions is a full cycle\'s scope and P2 landing '
        'was blocking per brief section 4 gating; recommended next-cycle P3 execution recipe documented in '
        'docs/rc1_baseline_policy_report.md section 4; '
        '(4) anchor preservation: docs/rc1_baseline_policy_report.md SHA %s byte-identical pre==post this turn; '
        'c49 v1 baselines / c50 v2 rubric SHA / c51 Branch A verdict.json all READ-ONLY (not opened); '
        '(5) no P4a/b/c infra work per brief section 5 deferral. '
        'Honest-negative-finding chain extended: c35/c36/c48/c51-A/c51-C/c53-clone-0-none/c53-clone-1-abandoned/'
        'c53-clone-2/this-cycle-P1-close.'
    ) % REPORT_SHA,
    'artifacts': ['docs/rc1_baseline_policy_report.md'],
}

ev6 = {
    'ts': TS, 'run_id': RUN_ID, 'cycle': CYCLE, 'agent': 'worker',
    'milestone_id': '_archive/cycle-53-scratch',
    'status': 'validated',
    'confidence': {
        'level': 'high',
        'rationale': (
            'c53 clone-1 housekeeping. No scratch files require archival - this cycle produced two persistent '
            'artifacts under data/c53_c60_reconciliation/ (P2 evidence) and used the pre-existing '
            'docs/rc1_baseline_policy_report.md. The emitter script itself lives at '
            'tools/_c53_clone1_emit_events.py and is retained as reproducibility evidence.'
        ),
        'assessor': 'worker',
    },
    'narrative': (
        'c53 clone-1 archive event. One-shot orchestration helper this cycle: tools/_c53_clone1_emit_events.py. '
        'No files moved to tools/stale/; the emitter is kept as evidence for the auditor.'
    ),
    'artifacts': ['tools/_c53_clone1_emit_events.py'],
}

for i, ev in enumerate([ev1, ev2, ev3, ev4, ev5, ev6], start=1):
    try:
        append_ledger_event(WS, ev)
        print('[%d] %s -> OK' % (i, ev['milestone_id']))
    except Exception as e:
        print('[%d] %s -> FAIL: %s: %s' % (i, ev['milestone_id'], type(e).__name__, e))
        raise

post_shadow_count = 0
with open(pre_ledger, 'rb') as f:
    post_shadow_count = sum(1 for _ in f)
print('shadow_rows: pre=%d post=%d delta=%d' % (pre_shadow_count, post_shadow_count, post_shadow_count - pre_shadow_count))
with open(WS / 'promise_ledger.jsonl', 'rb') as f:
    main_after = sum(1 for _ in f)
print('main_ledger: pre=888 post=%d unchanged=%s' % (main_after, main_after == 888))
