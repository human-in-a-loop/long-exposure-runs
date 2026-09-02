import json
import re
targets = [
    "M-EAR-1/real-label-training-v2.1",
    "M-EAR-1/real-label-training-v2.1/anchor-preservation-verified",
    "M-EAR-1/real-label-training-v2.1/features-loaded",
    "M-EAR-1/real-label-training-v2.1/head-trained",
    "M-EAR-1/real-label-training-v2.1/rubric-committed",
    "M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-1",
    "M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-2",
    "M-EAR-1/real-label-training-v2.1/verdict-emitted",
    "M-RECREATE-2/accurate-small-set-v2",
    "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey",
    "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano",
    "M-RECREATE-2/accurate-small-set/rc8-peak-section-selection",
    "_archive/deprecate-c45-determinism-check-clone-2",
    "_infra/anchor-manifest-v1",
    "_infra/harness-and-writer-hardening-v3",
    "_infra/harness-clone-namespace-guard",
    "_infra/pin-source-date-epoch-anchor-clone-2",
    "_infra/pre-registration-gate-policy-scope-verification-clone-1",
    "_manager/M-EAR-1-v2-c45-deprecation-and-source-date-epoch-anchor-pin-clone-2",
]

# Load all milestone_ids from ledger
mids = []
with open('promise_ledger.jsonl') as f:
    for line in f:
        try:
            mids.append(json.loads(line).get('milestone_id', ''))
        except Exception:
            pass
from collections import Counter
c = Counter(mids)

print(f"{'TARGET':<80} exact  clone*")
for t in targets:
    exact = c.get(t, 0)
    prefix = t + '-clone-'
    prefix2 = t + '/'
    clone_ct = sum(v for k, v in c.items() if k.startswith(prefix))
    child_ct = sum(v for k, v in c.items() if k.startswith(prefix2))
    print(f"{t:<80} {exact:>5}  {clone_ct:>5}  children:{child_ct}")
