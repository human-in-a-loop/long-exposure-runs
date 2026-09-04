# Agent-Picks Selection Invariants (c14 codification)

**Authority**: campaign prompt `music_gen_v4_prompt.md` BINDING anti-stall rule + operator directive 2026-09-03 part (2) + c13 auditor recommendation.

**Scope**: whenever the agent must select one of N pre-registered options in a manager-escalation fork under the anti-stall rule (no wait on operator), it MUST apply these invariants in order. Retroactively applicable to c9 CG-bass acceptance-fork (compliant) and c13 CG-drums acceptance-fork (non-compliant on all three; formal reason for the c14 revise to OPT3).

## Invariant (a) — prefer no operator-scope extension

When option X extends an operator directive's scope (e.g. from CG-bass-ONLY to CG-bass-AND-drums) and option Y stays within the directive's stated scope, prefer option Y unless Y is impossible.

*Applied to c14 CG-drums fork*: OPT1 requires extending c9 composite-relative WINNER rule (currently CG-bass ONLY) to CG-drums. OPT3 stays within stated scope. Prefer OPT3 over OPT1 under (a).

## Invariant (b) — prefer above-floor over below-floor

When option X selects a candidate below a retained absolute floor (e.g. 0.40 emb_cos RULED_OUT floor) and option Y selects an above-floor candidate OR takes a non-candidate policy path (refuse showcase; use reference stem), prefer Y over X.

*Applied to c14 CG-drums fork*: OPT1's 0.2374 is below the retained 0.40 floor. OPT3 does not select any candidate. Prefer OPT3 over OPT1 under (b).

## Invariant (c) — do not reject an option based on misreading its own definition

Before rejecting option X, quote its definition verbatim from the pre-registered escalation JSON. If the rejection rationale relies on a paraphrase that contradicts the verbatim text (example: rejecting OPT3 = "Refuse drums showcase, use original htdemucs drums track directly" because "hybrid overlay is spec'd for VOCALS ONLY" — OPT3 is not a hybrid overlay, it is a refuse-and-substitute), the rejection is invalid and MUST be reconsidered.

*Applied to c14 CG-drums fork*: c13's rejection of OPT3 misread "refuse drums showcase, use htdemucs drums track as-is in the mix" as "extending hybrid-overlay from vocals to drums". OPT3 is not a hybrid overlay; it is a policy consequence of the arc being exhausted. Re-reading OPT3 verbatim admits it as a valid pick.

## Interaction with binding specs

These invariants sit under (never above) FD-1 (no tuning/retry/fallback), FD-6 (operator ear = LANDS authority post-hoc), FD-16 (env_pin drives cert re-issue; never `--verify-det`; replay proofs per RENDER FAMILY per SONG), and the operator directive 2026-09-03 parts (1)-(3). They also sit under the campaign prompt's binding anti-stall rule. They constrain the agent's judgment call, not the operator's.

## Reference in future acceptance-fork events

Future acceptance-fork ledger events under `_manager/*acceptance-fork*` or `_manager/*acceptance-policy*` SHOULD cite this document by path (`docs/agent_picks_selection_invariants.md`) in their `authority` block, and their per-option `reason_rejected` fields SHOULD explicitly note which invariants (a)/(b)/(c) apply.

## Version

- c14 (2026-09-04): initial codification.
