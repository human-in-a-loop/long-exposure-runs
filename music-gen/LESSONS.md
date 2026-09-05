# Cross-Cutting Lessons

Curated findings across runs. Updated by the final auditor at run end. The DB record (record_type='lesson') is canonical; this file mirrors for human readability.

---

## Lesson: por-narrative-transcription-drift-is-the-dominant-audit-trail-defect-class
*Committed: 2026-09-05T00:11:27.999449+00:00*

# POR-narrative transcription drift is the dominant audit-trail defect class

**Pattern observed.** Four of five MINOR delta-audit findings and part of one MODERATE finding are the same class: a milestone lands on disk with a byte-deterministic artifact, then the plan-of-record narrative that describes that artifact pins a slightly different SHA (or path). The drift never invalidates the substantive claim, but it silently degrades the ledger's authority as the primary reference.

**Concrete cases from this run.**
- `M-V3-RULES-1/first-activation/rubric-committed`: POR pins `docs/v3_rules_deterministic_extractor_spec_c23.md`; on-disk canonical path is `docs/specs/v3_rules_deterministic_extractor_spec_c23.md` (same SHA `e81ff589200f6d6b…`).
- `M-V4-PROFILES-1/cg-bass-sf2-replay-proof-v2`: POR pins `bass_v2.replay_proof.json` SHA `86948709746b966a…`; on-disk is `4b9eea98052d6b2f…` (full divergence, no prefix collision).
- `M-V4-PROFILES-1/cg-bass-sf2-replay-proof`: POR pins `run1_sha256 == run2_sha256 == 832868d0ea8a81ca…`; on-disk holds `c69775040c325b86…`. File mtime consistent with a legitimate regeneration after the c11 `_infra/replay-channel-aware-fix-c11`.
- `M-V4-PROFILES-1/cg-drums-profile-v1-emitted`: POR pins `drums.json` SHA `f48b7d7fb1bf28d3ff6b9c9e17e64f1ee…`; on-disk `f48b7d7fb1bf28d3fb65c5827c47a917…` — same 16-hex prefix, tail divergence. Also a 62-hex-character MIDI SHA (malformed).
- `M-V4-RULES-1/scaffold-c20`: POR pins scaffold stub SHAs `c8603851d54c56c4…` and `1e0ad1131f090003…`; on-disk `3189da3df7cfb49f…` and `2b1764e3fa9b4c75…`. In this case the drift class escalated: the divergence is not narrative slippage, it is silent supersession (see the sibling lesson).

**What works.**
1. FD-1 (on-disk artifacts are authoritative) is the correct backstop. Every substantive claim in the delta window remains verifiable against the on-disk SHA.
2. Three-way `rubric_hash*` byte-equality chains catch drift on the rubric itself. Every landed milestone in the delta window kept its chain intact.
3. The `_infra/adopt-cycle<N>-tests` + `_archive/cycle-<N>-scratch` housekeeping event pattern from cycle 3+ is the correct habit; the drift is entirely in POR-body narratives, not in event bodies.

**What doesn't work.**
1. Freely hand-transcribing SHAs into the plan-of-record narrative (paragraph text) invites typos: 62-hex characters (missing hex), first-16-collision-then-divergence, and full-SHA divergence all appear in the delta window.
2. Refreshing POR narrative text after a legitimate regeneration (e.g. after `_infra/replay-channel-aware-fix-c11`) is not a codified housekeeping obligation. The regeneration event lands cleanly; the narrative that named the pre-regeneration SHA is left behind.
3. There is no automated `promise_check`-style validator for POR-body SHAs (it validates event bodies, not paragraph text).

**Recipe.**
- When emitting a milestone-row narrative that mentions an artifact SHA, write it as `<sha16>…` (first-16-hex only) unless the row's own success criteria require the full SHA. This matches on-disk artifact naming conventions (`focus_set_v2.json` under `<sha16>/`) and removes the failure mode of writing a truncated or off-by-one 62-hex value.
- When a regeneration event lands (`_infra/*-fix-c<N>`) that changes an artifact's SHA, the same cycle's `_plan/register-*` row should refresh the affected narratives. The pattern is analogous to `_infra/adopt-cycle<N>-tests` — bookkeeping, not policy.
- Add a housekeeping validator: `python3 -m long_exposure.tools.por_check` that walks Milestones-table narratives for `[0-9a-f]{16,}` runs, resolves them against on-disk artifacts under FD-1, and flags stale or malformed entries. Non-blocking (WARN, not ERROR) so it does not gate cycles.

**Anti-patterns.**
- Pinning a full 64-hex SHA in prose without an automated round-trip check.
- Treating a stale SHA in the narrative as "just narrative drift" without checking whether the artifact was regenerated for a substantive reason (e.g. the c11 channel-aware fix).
- Using different SHA conventions in the same POR row: full for one artifact, first-16-hex for its sibling.

**Cross-references.** Delta-audit findings 1 (M-V3-RULES-1 path drift), 2 (bass_v2 replay-proof), 3 (v4_rules scaffold SHA drift), 4 (bass replay-proof), 5 (drums profile + 62-hex MIDI SHA).

