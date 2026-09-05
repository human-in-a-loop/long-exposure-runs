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

## Invariant (d) — on-disk-vs-brief divergence disclosure norm

If actual on-disk truth (anchor SHAs, leaderboard ranks, script contents, grid contents, etc.) diverges from brief text, the divergence MUST be explicitly disclosed in work_output §Issues, with the on-disk value pinned by SHA and the worker's rationale for choosing on-disk over brief. Precedents:

- c12 audit: brief drums-anchor transcription error `dadafcfc…269e00…` vs on-disk `dadafcfc…651c23…` — worker disclosed in `_replay_regression_c12.json.brief_anchor_discrepancy_note`, cited on-disk canonical per FD-1. Auditor: exemplary hygiene.
- c14 Track 3 guitar stage-2 grid: brief-specified `{24, 27, 31, 26, 25}` vs on-disk c13 top-5 `{24, 25, 26, 27, 28}` — worker followed on-disk but did NOT disclose in work_output. c15 retroactive disclosure closes this class.
- c14 Track 4 test debt: brief-hardcoded c12 builder SHA `eaa8fb6c…` vs on-disk canonical `295e5501…` — worker pinned on-disk in test regression, disclosed correctly in work_output §Issues. Correct pattern.

FD-1 makes on-disk truth authoritative; invariant (d) makes silent-honoring an anti-pattern.

## Invariant (e) — cross-cycle pinned-profile shape stability

Delivery-manifest artifacts (e.g., `cg_<instrument>_pinned_profile.json`)
commit to their key structure on first campaign use. Subsequent same-family
pinnings replicate the shape verbatim, or the drift is disclosed under
invariant (d).

Campaign-canonical `acceptance_fork` shape (from c14 drums anchor):

```
acceptance_fork:
  chosen: {id, verbatim, rationale_points}
  rejected: [{id, verbatim, reason}, ...]
  authority: str
  invariants_doc: str (path to docs/agent_picks_selection_invariants.md)
```

`supersedes_path` remains top-level (per c14 lemma; `str`, not `list`; not
nested under `acceptance_fork`).

Precedents:

- c9 bass_v2 acceptance (pre-formalization; predates invariant framework —
  grandfathered).
- c14 drums acceptance (4 nested + top-level `supersedes_path` — CANONICAL).
- c15 guitar acceptance (3 nested + top-level `supersedes_path`;
  `invariants_doc` folded into `authority` string — DRIFT, disclosed
  retroactively at c16 per invariant (d)).

Enforcement: new pinned-profile emissions test-assert this shape via
`tests/test_pinned_profile_shape.py` (c16 addition). The c15 guitar
drift is grandfathered as a documented DRIFT precedent — the test
records it as such rather than failing on it.

## Operational invariant OP-1 — fine-fit-driver serial-launch lock

Numbered separately from the (a)–(e) selection invariants; this is an
operational discipline invariant, not a candidate-selection rule.

Fine-fit drivers that load VGGish embeddings (via the composite objective)
MUST run serial — no concurrent driver launch. Empirical trigger: c31 guitar
fine-fit was SIGSTOP-killed (exit 147 = 128+19) at cell 163/180 due to
parallel VGGish memory contention with a concurrent bass fine-fit sweep on
the same machine. A serial-solo retry succeeded 180/180.

Enforcement:

- Every fine-fit driver (`fine_fit_sf2_v2.py`, `fine_fit_sf2_drums.py`,
  `fine_fit_sf2_guitar.py`) checks-and-refuses at entry against a sentinel
  file `data/v4/_run/fine_fit_serial_lock` — if present, driver exits
  non-zero with a clear error message identifying the incumbent lock owner
  (pid, driver name, start timestamp) and hands off to operator.
- On accepted entry, the driver creates the sentinel via `os.open(...,
  O_CREAT | O_EXCL | O_WRONLY)` with `{pid, driver, cycle, started_at}` as
  a canonical JSON payload — the `O_EXCL` guarantees mutual exclusion at
  the syscall boundary even under race.
- The sentinel is removed in a `finally` block that covers normal exit,
  exceptions, and (best-effort) signal handling.
- Regression coverage: `tests/test_fine_fit_serial_lock_c32.py` asserts
  (i) sentinel creation on entry, (ii) second driver refusal-with-clear-
  error while sentinel present, (iii) sentinel removal on normal exit,
  (iv) sentinel removal on halt/exception exit.
- Extended in `tests/test_c30_legacy_mode_regression.py` (in-place, per
  c18 additive pattern) with OP-1 sentinel behaviour cases so the OP-1
  contract stays visible in the campaign-wide regression suite.

Scope: OP-1 applies to any driver that instantiates a VGGish model on the
same host. Non-VGGish drivers (e.g. `coarse_sweep_sf2*.py` before hygiene
integration) are exempt; they may run concurrently. If a future driver
adds VGGish, it MUST adopt OP-1 sentinel behaviour before its first
detached launch.

## Version

- c14 (2026-09-04): initial codification (invariants a/b/c).
- c15 (2026-09-04): extended with invariant (d) — on-disk-vs-brief disclosure norm.
- c16 (2026-09-04): extended with invariant (e) — cross-cycle pinned-profile shape stability.
- c32 (2026-09-05): extended with operational invariant OP-1 — fine-fit-driver serial-launch lock.

