<!--
created: 2026-08-29T17:45:00Z
cycle: 47
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/pre-registration-gate-policy-scope-verification-clone-1
-->

# Pre-registration gate policy — scope verification report (c47 Branch B)

## §1 Verdict + one-line justification

**Verdict: MIXED.** The c46 harness-constraint claim holds for the
currently-observed harness session (all cycles 45+ commits land at
the periodic-sweep boundary), but the git-log history also contains
9 commits classified as `worker-turn` (all from cycles 38–39 under
`M-SCORE-1/bridge-api-real-audio-quantization/*`) whose landing
pattern indicates the harness of those sessions DID permit
`git commit` inside a single worker turn. Both patterns are present
in evidence; the amendment scope is therefore session-context
dependent.

Decision rule applied: `worker_in_turn_count=9 > 0 AND sweep_count=141 > 0`.

## §2 Rubric doc quote (verbatim) + SHA-256

Rubric SHA-256: `1be2bac55ce595b47b6f369f472c3dadff31024d0447c133fd75bdf0132511cb`.
Pinned to `data/pre_reg_policy_verify/rubric_hash.txt` (single-line
hex + newline). Embedded in `data/pre_reg_policy_verify/verdict.json`
`rubric_hash` field. Three-way byte-equality asserted in test 03.

Verbatim frozen verdict clauses from
`docs/pre_registration_gate_policy_scope_verification_rubric.md` §Frozen verdict set:

> **HARNESS_CONSTRAINT_CONFIRMED** — every commit classified as
> worker-authored in the git-log history occurred at periodic-sweep
> boundaries (author-email match with periodic-sweep bot OR
> commit-message marker match with `(periodic sweep)` /
> `(post-merge cycle N)` / `(cycle N merge...)`). Zero commits are
> classified as worker-inside-turn.
>
> **HARNESS_CONSTRAINT_LIFTED** — at least one commit is classified
> as worker-authored **and** carries evidence of landing inside a
> single worker turn (commit-message marker names a specific
> substantive milestone with no periodic-sweep envelope and no
> post-merge envelope), and that class is not empty across the
> entire history.
>
> **MIXED** — evidence supports both patterns partitioned by session
> context class. Some session contexts produce only periodic-sweep
> commits; other contexts produce worker-inside-turn commits.

## §3 Methodology

1. `scripts/pre_reg_policy_verify/grep_git_log.py`: subprocess-drives
   `git log --all --format=%H %ae %aI %s` from the workspace root
   into `data/pre_reg_policy_verify/git_log_raw.tsv`. Interpreter
   guard on `/usr/bin/python3`; startup banner to stdout.

2. `scripts/pre_reg_policy_verify/classify_commits.py`: two-signal
   classifier.
   - Signal (a): author-email pattern → `bot` (matches
     `noreply@anthropic.com`) or `human` (none observed).
   - Signal (b): first-match regex over the commit subject, ordered
     `merge-integration` → `periodic-sweep` → `auditor-turn` →
     `researcher-turn` → `worker-turn` → `harness-auto-write`.
   - `session_context = marker_class`. Confidence = `high` when
     bot-authored with a non-unknown marker; `medium` on unknown
     marker; `low` reserved for future human authors.
   - Emits `commit_classification.tsv`.

3. `scripts/pre_reg_policy_verify/session_context_matrix.py`: reduce
   the classified table to a 7-class × counts matrix + `TOTAL` row.
   Deterministic ordering (canonical class list).

4. `scripts/pre_reg_policy_verify/verdict.py`: apply the rubric per
   the decision-precedence rule. Emits `verdict.json` with the
   `rubric_hash` chain, `counts_by_context`, `sweep_total`,
   `in_turn_total`, per-class evidence sample (first 3 rows per
   class in insertion order), and `decision_rule_applied`.

Determinism envelope: `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424
TZ=UTC LC_ALL=C.UTF-8`.

## §4 Empirical evidence table

Full `session_context_matrix.tsv`:

| session_context | commit_count | confidence_high | confidence_medium | confidence_low |
|---|---:|---:|---:|---:|
| periodic-sweep | 105 | 105 | 0 | 0 |
| merge-integration | 36 | 36 | 0 | 0 |
| worker-turn | 9 | 9 | 0 | 0 |
| auditor-turn | 0 | 0 | 0 | 0 |
| researcher-turn | 0 | 0 | 0 | 0 |
| harness-auto-write | 0 | 0 | 0 | 0 |
| unknown | 94 | 0 | 94 | 0 |
| **TOTAL** | **244** | **150** | **94** | **0** |

Derived aggregates (from `verdict.json`):

- `sweep_total = 141` (periodic-sweep + merge-integration + harness-auto-write).
- `in_turn_total = 9` (worker-turn + auditor-turn + researcher-turn).
- `unknown = 94` (conservatively bucketed OUT of `in_turn_total`; the
  subject strings are variants of `Add music-gen run artifacts …`
  without a `(periodic sweep)` or `(cycle N merge …)` envelope — a
  harness-authored intermediate class).

Worker-turn evidence rows (all 9 fall in cycles 38–39):

- `47423e522007e5acd093d57de7a23fd93899cef5` 2026-08-29T09:36:31 —
  `M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2: archive c39 scratch (c39 clone-1)`
- `8f516b37d970fb579f2340721abf85492fa1b552` 2026-08-29T09:35:56 —
  `M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2: scripts + tests + report + data (c39 clone-1)`
- `904df26eeafa0ca1bba3a718132f63794914caac` 2026-08-29T09:24:20 —
  `M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2: rubric first (c39)`
- 6 additional M-SCORE-1/bridge-api-real-audio-quantization commits
  from c38 clone-1 (rubric, scripts, report, probe refinements,
  archive, plus two `commit ear v1 rubric{,hash}` hand-authored
  commits).

## §5 Reconciliation action executed

**Reconciliation C fired (MIXED)**: added a new §3 to
`docs/pre_registration_gate_policy.md` listing the session-context
partition. Prior §1 + §2 preserved verbatim (SHA-256 of the first
3488 bytes of the post-edit doc equals the pre-edit doc SHA-256
`d432523ec2bdc9a628e02eba2542545e7dc2de4781ac628284fc1157b67f230f`;
prefix preservation asserted in `anchor_preservation.json` and
test 08).

Partition:

- Harness-boundary bucket (mtime-only gate is correct):
  `periodic-sweep` (105), `merge-integration` (36),
  `harness-auto-write` (0), `unknown` (94).
- In-turn-capable bucket (path (i) git-log gate remained
  satisfiable): `worker-turn` (9), `auditor-turn` (0),
  `researcher-turn` (0).

No sunset ticket emitted — MIXED does not trigger path (i)
reinstatement globally; future cycles falling into the
in-turn-capable bucket may restore the git-log gate scope-locally.

## §6 Anchor preservation manifest summary

`data/pre_reg_policy_verify/anchor_preservation.json` carries 18
SHA-256 entries (target ≥15):

- `docs/pre_registration_gate_policy.md`: pre-SHA + post-SHA + prefix
  SHA-of-first-3488-bytes (asserted equal to pre-SHA).
- c22 stability harness: 7 scripts under `scripts/ear/` +
  `stability_audit/*.tsv|*.json` files.
- c46 canonical: `scripts/ear_v2/adjudication/determinism_check_c46.py`.
- Branch A / Branch C: existence checks — no pre-existing files
  under `scripts/ear_v2p1/`, `data/ear_v2p1/`,
  `scripts/deprecation_and_anchor_pin/`,
  `data/deprecation_and_anchor_pin/`, or `data/anchor_manifest_v1.json`
  at snapshot time (peer clones may have added these concurrently;
  see §9).

All c22 stability harness + c46 canonical module SHAs verified
byte-identical pre==post in tests 12 + 13.

## §7 Byte-determinism × 2 SHA table

Recorded in `data/pre_reg_policy_verify/determinism_check.json`:

| artifact | run_1 SHA-256 | run_2 SHA-256 | equal |
|---|---|---|:-:|
| commit_classification.tsv | `119d41d4afc850700bd586ad0c87107b8f0fd36c6d2aee6d4531f48afad45a68` | `119d41d4afc850700bd586ad0c87107b8f0fd36c6d2aee6d4531f48afad45a68` | ✓ |
| session_context_matrix.tsv | `81bbf452f4d376a6f9a6e5f04079947f2d1e2de09cbf91044feec11d77b59aa9` | `81bbf452f4d376a6f9a6e5f04079947f2d1e2de09cbf91044feec11d77b59aa9` | ✓ |
| verdict.json | `53febe83b0d638d51064bb958a86074bddfcbd0e403d3a2cb5d0edf648d07de1` | `53febe83b0d638d51064bb958a86074bddfcbd0e403d3a2cb5d0edf648d07de1` | ✓ |

Two independent fresh `tempfile.mkdtemp()` runs under the pinned
env envelope produce byte-identical outputs.

## §8 Discipline invariants asserted

- Interpreter guard `/usr/bin/python3` present in every non-`__init__`
  script (test 07).
- Zero PRNG imports/references (`random`, `numpy.random`, `np.random`,
  `secrets`) under `scripts/pre_reg_policy_verify/` (test 05).
- Zero `sidecar_nonfactor` references (test 06).
- Zero `i4_stratified` references (test 15).
- Startup banner emitted by every module (test 14).
- Foreground execution: all pipeline runs completed synchronously
  in-process (no `run_in_background`).
- Rubric doc mtime < script mtimes (test 01).
- Git-log gate: ADVISORY (test 02) — this cycle's writes land in a
  future periodic-sweep envelope.

## §9 Known limitations

- Git-log completeness depends on `--all`: history reachable only
  from unreferenced dangling commits is not included. In practice
  the workspace has no such refs at scope-verification time.
- The `unknown` bucket (94 commits) contains bare `Add music-gen run
  artifacts` variants that lack an explicit `(periodic sweep)` or
  `(cycle N merge …)` envelope but ARE harness-authored (subject
  matches the harness's canonical prefix). They are conservatively
  bucketed OUT of `in_turn_total`. Reclassifying them into
  `periodic-sweep` would strengthen the MIXED verdict toward
  CONFIRMED for the current-session context, but not overturn it —
  the 9 worker-turn c38/c39 commits remain regardless.
- Peer fanout clones (Branch A `ear_v2p1/`, Branch C
  `deprecation_and_anchor_pin/`, `data/anchor_manifest_v1.md`) may
  add files concurrently in the same workspace. `git status
  --porcelain` picks these up; test 11 was rewritten to positively
  verify THIS clone's scope rather than reject peer writes.
- The classifier's marker-signal regex is anchored to this campaign's
  observed prefixes. A different campaign or session with different
  commit-message conventions would need the ordered regex table in
  `classify_commits.py` re-tuned.

## §10 c48 handoff seeds

1. **Auditor-reads-rubric-docs lemma** (from c46 handoff): the c47
   auditor should verify the rubric doc's PARTIAL/CONFIRMED/LIFTED/
   MIXED clauses against the actual observed decision-rule inputs,
   not paraphrase — c46 audit conflated PASS with IMPROVEMENT axes.
2. **Periodic-sweep failure surface**: if any c48 cycle finds a
   misclassified commit (e.g. a `worker-turn` commit envelope-wrapped
   by `(periodic sweep)`), it will change the MIXED verdict count
   materially; re-run the classifier deterministically to catch
   drift.
3. **MIXED reconciliation follow-up**: path (i) git-log gate can be
   restored scope-locally for `worker-turn`/`auditor-turn`/
   `researcher-turn` contexts if a c48+ harness update permits
   in-turn commits. A follow-up amendment would name the class and
   flip test 02 from SOFT to HARD for that scope only.
4. **c46 `_plan/git-log-gate-policy-amendment` status**: this cycle's
   MIXED verdict LEAVES the amendment in place (not retired) — the
   claim holds for the current harness. If a future cycle produces
   LIFTED, retire that ticket under state-machine `superseded` per
   the c29 lemma.
5. **Egress retry cadence**: `M-INGEST-1/egress-probe-cycle47-clone-1`
   recorded HTTP 429 + `tv_embedded` (unchanged since c45/c46). Two
   consecutive `media_ok=true` rows remain the ingestion-unblock
   signal; no such row observed this cycle.
