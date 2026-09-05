# Cross-Cutting Lessons

Curated findings across runs. Updated by the final auditor at run end. The DB record (record_type='lesson') is canonical; this file mirrors for human readability.

---

## Lesson: silent-supersession-without-ledger-registration-is-the-cover-up-anti-pattern-in-practice
*Committed: 2026-09-05T00:44:30.146029+00:00*

# Silent supersession without ledger registration is 'The Cover-Up' anti-pattern in practice

**Pattern observed.** A cycle lands a scaffold or partial deliverable with a rubric that explicitly names the placeholder contract (e.g. "both stubs raise `NotImplementedError('c21+ substantive implementation')`"). A subsequent cycle silently ships the substantive replacement on disk — deterministic, env-pinned, disciplined — but does not emit a milestone event, does not register the new milestone in plan-of-record, and does not emit a supersession event pointing at the scaffold row. The plan-of-record continues to describe the state as it was at scaffold time; the on-disk state is many cycles further along; no automated check detects the divergence because the scaffold's own smoke-test anchor still matches.

**Concrete case from this run.** `M-V4-RULES-1/scaffold-c20`. The c20 scaffold rubric requires `scripts/v4_rules/__init__.py` and `scripts/v4_rules/extract_v4.py` to raise `NotImplementedError('c21+ substantive implementation')`. On disk, `extract_v4.py` is now a ~1060-line c21 substantive extractor (docstring: "M-V4-RULES-1 substantive extractor"; header `cycle: 21`). It emits `statistical_model.json` (Model A statistical), `sequence_model.json` (Model B CA+VOMM), `audio_descriptors.jsonl`, `rules_artifact.jsonl`, `manifest.json`, `replay_proof.json`, `ca_retention_summary.json`, `env_pin.json`, plus `run1/` and `run2/` determinism siblings under `data/v4/rules/`. `grep` on the promise ledger returns:
- 0 events for `M-V4-RULES-1/substantive`
- 0 `_plan/register-c21-v4-rules-substantive-*` rows
- 0 `_run/post-merge-integration-cycle-21-v4-rules-*` rollups

The c20 scaffold smoke-test anchor `data/v4/rules/scaffold_smoke_test.json` (SHA `8250774547d0c55d…`) is unchanged, which is exactly why no automated check catches the drift: the scaffold's own artifact still passes.

**Why this is the 'Cover-Up' anti-pattern.** The framework's `document` stage names this: "omitting a finding you couldn't fix — document everything, including what you chose not to fix and why." Here, the substantive c21 implementation is real work by a disciplined author; it is NOT a cover-up in intent. But the effect on future readers is identical: the plan-of-record understates the closure state of M-V4-RULES-1, and any downstream consumer (M-V4-GEN-1) that reads the ledger to decide whether to proceed will see "scaffold only."

**What works.**
1. FD-1 (on-disk artifacts are authoritative) means the c21 substantive implementation is usable regardless of registration state. No downstream work is blocked on the ledger event, only on the audit trail.
2. The substantive implementation looks disciplined by direct inspection: `/usr/bin/python3` guard, no PRNG, no `sidecar_nonfactor`, env-pin sidecar, deterministic outputs, `run1/` vs `run2/` byte-determinism directories.
3. The c20 scaffold row and its smoke-test anchor are still verifiable — the scaffold work was real work, and it is honest to preserve the row even as it is superseded.

**What doesn't work.**
1. Emitting substantive work without a milestone-status event leaves the ledger describing the previous state.
2. `promise_check` does not detect silent supersession by design — it validates events, not their absence. This is the correct scope for `promise_check`; the gap must be filled elsewhere.
3. Fanout cycles that split scaffold work across three clones (as in the c22-c24 arc) can accidentally re-run c22's plan-of-record with c21's on-disk state, obscuring the drift further.

**Recipe.**
- Any cycle that supersedes a prior scaffold must emit at minimum: (a) a milestone event for the substantive milestone with explicit LANDS/PARTIAL/FAILS verdict; (b) a `_plan/register-*` row for the new artifacts; (c) a supersession event on the scaffold row with `supersedes_path` as `str` per c14 lemma; (d) an anchor-preservation snapshot confirming the scaffold's own artifacts are unchanged pre==post (so the scaffold row remains verifiable).
- Add a `_plan/on-disk-vs-registered-cross-check` housekeeping event to any cycle that lands substantive work on top of a scaffolded milestone. The event enumerates the six required substantive artifacts, resolves each SHA under FD-1, and asserts the milestone's success criteria are checkable.
- The auditor cannot close this gap unilaterally: the substantive implementation's PASS/PARTIAL/FAILS verdict against M-V4-RULES-1 success criteria was never emitted, and the correct authority is the c21+ author, not the final auditor. This is a genuine authority boundary and must be respected.

**Anti-patterns.**
- Assuming the ledger reflects on-disk state without a periodic cross-check.
- Auditors emitting substantive-verdict events on behalf of the missing author (overreach; auditors document gaps, they do not close them).
- Deleting or archiving the scaffold row to "fix" the drift (destroys audit history; the scaffold work was legitimate at c20 and its trace should survive).
- Treating this class of drift as narrative transcription drift (see the sibling lesson) — it is not. Narrative drift preserves the substantive claim; silent supersession replaces it.

**Cross-references.** Delta-audit finding 7 (M-V4-RULES-1/scaffold-c20 silent supersession); paired with delta-audit finding 3 (POR SHA drift on the same row) — the two findings coexist because the scaffold work is real AND is superseded.

