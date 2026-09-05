import json
import pathlib

p = pathlib.Path("/home/user/long-exposure-runs/music-gen/audits/final/lessons.jsonl")
row = {
    "slug": "recursive-delta-audit-over-unchanged-surface-is-a-first-class-outcome",
    "content": (
        "# Recursive delta audit over an unchanged surface is a first-class outcome\n\n"
        "**Pattern observed.** A second delta-audit pass ran with the same delta boundary "
        "artifact set as the immediately-prior committed audit. Both validators returned "
        "clean; both prior findings re-confirmed on their own evidence; no new findings "
        "surfaced during Verify or Test; no reconciliation events were warranted; the "
        "campaign surface (promise_ledger.jsonl, referenced on-disk artifacts, closure "
        "report) was byte-identical to the prior audit's baseline snapshot.\n\n"
        "**What works.**\n"
        "1. Treat empty-delta as a first-class terminal outcome, not a bug. The correct "
        "response is a short document that (a) declares the delta empty, (b) re-confirms "
        "carried findings by re-running their own evidence checks (never by trusting the "
        "prior audit's conclusion), (c) proposes zero reconciliation events, and (d) names "
        "the prior committed audit as the canonical record.\n"
        "2. Re-run the primary evidence (grep counts, SHA checks, validator invocations) "
        "even when the surface is unchanged. The cost is small and it catches a rare "
        "silent-supersession class where a file's mtime changed but its SHA did not, or "
        "vice versa.\n"
        "3. Keep the lesson budget honest: at most max(1, ceil(delta_cycles/3)) = 1 for a "
        "single-report delta; if nothing new was learned, emit zero.\n\n"
        "**What doesn't work (anti-patterns to avoid).**\n"
        "1. Manufacturing findings to justify the pass. If the prior audit surfaced "
        "everything, the second pass adds nothing by restating the same substance in new "
        "words. Report the empty delta; do not pad.\n"
        "2. Forging reconciliation events on the audit's own authority. F1 (the "
        "ledger-vs-disk parity gap) is real, but the audit is not the party responsible for "
        "appending the missing completion events - the campaign is. Auditor-authored "
        "reconciliation would either duplicate the report's own bookkeeping disclosure or "
        "forge a completion event whose evidence line is the very report being audited.\n"
        "3. Rewriting the prior committed report in place. Under the framework's "
        "expected-file contract the delta pass writes to the same canonical path, but the "
        "correct semantics are 'supplement' not 'supersede'. The document should say so "
        "explicitly.\n\n"
        "**Cross-references.**\n"
        "- Prior committed delta audit (this same file, timestamp 2026-09-05T00:11:46Z) - "
        "canonical record of F1 and F2.\n"
        "- Framework rule: reconciliation is the campaign's responsibility once the audit "
        "has surfaced the invariant break; the auditor's job ends at severity "
        "classification and future-work anchoring.\n"
        "- Related lesson por-narrative-transcription-drift-is-the-dominant-audit-trail-"
        "defect-class (prior commit): explains the F1 class in general terms; this lesson "
        "complements it with the recursive-pass dynamics."
    ),
    "keywords": [
        "delta-audit",
        "empty-delta",
        "recursive-audit",
        "carried-findings",
        "reconciliation-responsibility",
    ],
    "subtopic": "audit-cadence",
    "tools": ["promise_check", "org_check", "findings.jsonl"],
}
with p.open("a") as f:
    f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("lessons.jsonl lines:", sum(1 for _ in p.open()))
