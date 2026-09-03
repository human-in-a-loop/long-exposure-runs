---
created: 2026-08-29T18:30:00Z
cycle: 48
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _manager/corpus-expansion-plan
fork: e651a0d7b0c8
clone: 1
---

# `_manager/corpus-expansion-plan` — c48 Branch B report

**Verdict:** `CORPUS_EXPANSION_TICKET_LANDS` (per frozen 2-verdict rubric —
`docs/corpus_expansion_plan_rubric.md`, SHA-256
`c1503cfa44300a3d0cf80e167c5a93066721419e398389531bf40638cd912fe6`).

3 axes × 3 concrete action items × 3 falsifiable trigger conditions each;
zero live-network probes (AST-grep clean); three-way `rubric_hash`
byte-equality verified; 16/16 anchors byte-identical pre/post; 20/20 tests
green; §65 integration extension +10 checks green.

## §1 — c26 Path B §5 quoted verbatim + corpus state

`docs/ear_path_b_commitment.md` §5.2 stub (verbatim, per read-only anchor
SHA-256 `2c81d80a6933…`):

> To be instantiated by any cycle that receives a bootstrap-τ FAIL on 80
> rated songs. Values in `<>` are placeholders.
>
> ```yaml
> milestone_id: _manager/M-EAR-1-corpus-expansion-request
> cycle: <N>
> …
> narrative: |
>   Path B SB2 evaluation invalidated on N=80.
>   Current: N=80 songs, band distribution H=30 (rating 6), M=30 (rating 5),
>     L=20 (rating 4). Observed mean pairwise τ = <VALUE>.
>   Target: N such that a bootstrap-power calculation projects
>     mean_tau ≥ 0.4 at the observed per-clip band-variance level with
>     probability ≥ 0.80.
>   Rated-song acquisition cost estimate: <yt-dlp minutes> +
>     <human-rating minutes / song>.
>   Timeline: <estimated cycles to acquire + re-rate the delta>.
> ```

**c48 note.** The c26 §5.2 template presumes N=80 has already been
delivered and Path B SB2 has FAILED on it. c48 reality is different — only
43/80 songs are on disk (10 band-4 + 10 band-5 + 13 band-6 + 10 band-7
per c36/c45/c47 corpus). The 37-song gap is the operative constraint. This
report fills the template placeholder with the feasibility landscape that
must be traversed to close the gap — three orthogonal axes with concrete
action items, cost estimates, and falsifiable trigger conditions.

**Corpus state (verified at commit time via `corpus/ratings/ratings_manifest.tsv`
SHA-256 `bc436ac1abba…`):**

| item                          | value                             |
|-------------------------------|-----------------------------------|
| rated songs on disk           | 43                                |
| rated songs targeted          | 80                                |
| gap                           | 37                                |
| band distribution on disk     | 10 (band-4) / 10 (band-5) / 13 (band-6) / 10 (band-7) |
| egress status                 | HTTP 429 + `tv_embedded` player-client closure (stable c45→c47) |

## §2 — Axis (i): egress unblock path

Owner mixed (researcher for analytical probes; worker for policy doc).
Confidence: **low**. Total analytical hours: **2.0**. Operator-dependent
hours: **unbounded** (workspace policy review is out-of-band). Expected
corpus delta range: **[0, 37]**.

| id  | name                                    | trigger (falsifiable)                                                         | Δcorpus | analytical h |
|-----|-----------------------------------------|-------------------------------------------------------------------------------|---------|--------------|
| i.1 | yt-dlp version probe (analytical)       | on-disk yt-dlp version < upstream release with commit-message match `tv_embedded\|player_client\|429` | 0–37    | 0.5          |
| i.2 | alternative CDN characterization        | `data/ingestion/egress_status.jsonl` shows ≥ 3 consecutive failures on same CDN sub-shard | 0–15    | 0.5          |
| i.3 | workspace policy documentation draft    | `policy_change_present = absent` after ≥ 5 cycles of periodic probing         | 0–37    | 1.0          |

**Non-obviousness.** All three items are strictly documentation-only in
this workspace; none of them attempts a live network call. i.1 reads the
on-disk yt-dlp version and compares to release-note text a researcher has
fetched out-of-band. i.2 reads `egress_status.jsonl` and characterizes the
failure sub-shard distribution. i.3 drafts a request document a human
operator would carry to workspace-policy review.

## §3 — Axis (ii): alternative source paths

Owner mixed (operator for handoff, researcher for alt-corpus fetchability,
worker for cadence probe). Confidence: **medium**. Total analytical hours:
**3.0**. Operator-dependent hours: **1–4** (bounded — operator handoff
protocol is documented from c36 precedent). Expected corpus delta range:
**[0, 40]** (upper bound higher than gap because a rating-band-equivalent
alternative may overshoot slightly).

| id   | name                                                                | trigger (falsifiable)                                                                       | Δcorpus | analytical h |
|------|---------------------------------------------------------------------|---------------------------------------------------------------------------------------------|---------|--------------|
| ii.1 | manual seed alternative (operator handoff protocol)                 | `operator_confirms_seeds_available = confirmed` AND `count >= 37`                            | 0–37    | 1.0          |
| ii.2 | friend-of-workspace tunnel (rating-band-equivalent alt corpus)      | `alt_corpus_band_dist_within_2 = present` AND `fetchable = available`                        | 0–40    | 1.0          |
| ii.3 | upstream operator delivery-cadence probe                            | `operator_delivers_new_rated_song >= 1` since c47 close                                       | 0–37    | 1.0          |

**Non-obviousness.** Item ii.2 is the substitutability escape hatch — the
ear-model chassis does not care which specific 80 songs constitute the
corpus, only that the ordinal rating band distribution is preserved. A
Freesound.org or Free Music Archive slice with band-distribution within
±2 songs per band would be a scientifically-valid substitute. This is the
axis with the highest chance of shipping without an operator handoff.

## §4 — Axis (iii): partial-corpus interpolation (analytical projection under c26 fix-lock)

Owner: **worker**. Confidence: **high** (analytical). Total analytical
hours: **3.0**. Operator-dependent hours: **0**. Expected corpus delta
range: **[0, 0]** — this axis produces N-required projections, not corpus
growth.

| id    | name                                                     | trigger (falsifiable)                                                                                          | analytical h |
|-------|----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|--------------|
| iii.1 | SB1 margin projection under c26-frozen chassis           | `kappa_sb1_derivable_from_c36_c38_c45 = present` AND `monotonic_in_N = confirmed`                              | 1.0          |
| iii.2 | SB2 τ projection under c26-frozen chassis                | `sb2_trajectory_monotonic_in_N = confirmed` OR `INSUFFICIENT_CONVERGENCE_ANALYSIS = present`                    | 1.0          |
| iii.3 | SB3 detection + FPR projection under c26-frozen chassis  | `sb3_denominator_widened_to_50 = present` AND `fpr_boundary_documented = confirmed`                             | 1.0          |

**Result (per `data/corpus_expansion_plan/partial_corpus_projection.json`):**
Both SB1 and SB2 return **`INSUFFICIENT_CONVERGENCE_ANALYSIS`** — the c36
v0, c38 v1, c45 v2 verdict trajectory all sits at N=43, so the per-song
sensitivity coefficient κ is under-identified from a single-N observation
series. A meaningful two-point κ estimate requires re-running the c26
chassis at N > 43 (naturally paired with axis (ii) operator delivery).
SB3 returns **`PROJECTED_ALREADY_AT_BOUNDARY_PASS`** — c47 v2.1 confirmed
detection = 1.000 with FPR = 0.100 at the 50-control boundary; SB3 is
corpus-invariant at chassis level per the c22/c23/c25 anti-pattern
lockouts, so N-growth is expected to widen the FPR margin qualitatively.

**Honest sensitivity.** This axis' scientific product is not a specific
N; it is the rigorous statement *"under c26 fix-lock and current
single-N observations, the analytical N-required question is
under-identified until at least one additional N observation lands."*
That is the correct answer, not a fabricated number.

## §5 — Per-axis cost table + expected corpus delta range

Per `data/corpus_expansion_plan/cost_estimator_output.json`:

| axis                                       | analytical h | operator-dep h | Δcorpus | confidence |
|--------------------------------------------|--------------|----------------|---------|------------|
| i — egress unblock                         | 2.0          | unbounded      | [0, 37] | low        |
| ii — alternative sources                   | 3.0          | 1–4            | [0, 40] | medium     |
| iii — partial-corpus interpolation         | 3.0          | 0              | [0, 0]  | high       |

**Total analytical hours across all three axes: 8.0.** This is the
worker-side cost of executing the entire feasibility landscape in a
single dedicated cycle. If parallelizable, three worker clones could ship
one axis each in ≈ 1 cycle.

## §6 — N-required-per-SB projection under c26-frozen chassis

Per `data/corpus_expansion_plan/partial_corpus_projection.json`:

- **SB1 (margin > 0.5909):** `INSUFFICIENT_CONVERGENCE_ANALYSIS`. All three
  observations (c36, c38, c45) sit at N=43; κ is under-identified.
  Recommended probe: re-run v2 chassis at N=80 post corpus-expansion
  delivery to enable a two-point κ estimate.
- **SB2 (mean τ ≥ 0.4):** `INSUFFICIENT_CONVERGENCE_ANALYSIS`. Same
  under-identification. The observed c45 v2 mean_tau_delta_vs_v1 = −0.0314
  is far from the 0.4 threshold; a naive linear extrapolation would demand
  a large N delta but has no data support.
- **SB3 (detection ≥ 0.90 at α=1.0 AND FPR ≤ 0.10):**
  `PROJECTED_ALREADY_AT_BOUNDARY_PASS` under c47 v2.1 stability
  (detection = 1.000, FPR = 0.100 exactly, denominator = 50). SB3 is
  corpus-invariant at chassis level; N-growth widens FPR margin.

## §7 — No-live-network probe surface (AST-grep evidence)

AST-parse of every `scripts/corpus_expansion_plan/*.py` module walks
`ast.Import` and `ast.ImportFrom` nodes; zero occurrences of any name in
the blocklist `{urllib, urllib.request, urllib.parse, requests, socket,
httpx, yt_dlp, aiohttp, urllib3}`. Verified by:

- `tests/test_corpus_expansion_plan.py` test 07 — PASS (0 hits).
- `tests/test_integration_cross_branch.py` §65g — PASS (0 hits under
  `scripts/corpus_expansion_plan/`).

## §8 — Anchor preservation manifest (16 SHAs)

Per `data/corpus_expansion_plan/anchor_preservation.json`
(`all_sha_byte_identical_pre_post = true`, `diffs = []`):

| # | path                                                        | pre==post SHA-256 (12-char prefix) |
|---|-------------------------------------------------------------|------------------------------------|
| 1 | `corpus/ratings/ratings_manifest.tsv`                       | `bc436ac1abba…`                    |
| 2 | `docs/ear_path_b_commitment.md`                             | `2c81d80a6933…`                    |
| 3 | `data/ingestion/egress_status.jsonl` (pre-append snapshot)  | `61c5886921ca…`                    |
| 4 | `docs/anchor_manifest_v1.md`                                | `8d5fd0e81b63…`                    |
| 5 | `data/anchor_manifest_v1.json`                              | `138f37a02530…`                    |
| 6 | `docs/ear_real_label_training_v2_rubric.md`                 | `01948b6efe6c…`                    |
| 7 | `data/ear_v2/rubric_hash.txt`                               | `008c3a2202c3…`                    |
| 8 | `data/ear_v2/verdict.json`                                  | `fed3a4605c70…`                    |
| 9 | `docs/ear_real_label_training_v2p1_rubric.md`               | `2920875671ea…`                    |
| 10| `data/ear_v2p1/rubric_hash.txt`                             | `9857e51fee30…`                    |
| 11| `data/ear_v2p1/verdict.json`                                | `9662a7371b2e…`                    |
| 12| `docs/pre_registration_gate_policy.md`                      | `3aad99d0e1e6…`                    |
| 13| `scripts/ear/synthetic_labels.py`                           | `b71f194ef97e…`                    |
| 14| `scripts/ear/stability_metrics.py`                          | `6a5cb5183fdc…`                    |
| 15| `scripts/ear/stability_audit.py`                            | `b1ce5137b665…`                    |
| 16| `data/ear/stability_audit/stability_report.json`            | `36615ad78907…`                    |

16 anchors ≥ 15 target. All byte-identical pre==post.

## §9 — Egress failure-mode registry cite

Per `data/ingestion/egress_status.jsonl` (last two rows before c48
probe): HTTP 429 + `tv_embedded` player-client closure, stable since c45
(cycle-46, cycle-47 both re-observed same mode). Registered under
`_infra/egress-failure-mode-registry` (c46 lemma). This cycle's Branch B
appends one bookkeeping row (`M-INGEST-1/egress-probe-cycle48-clone-1`)
recording the same failure mode; not the two-consecutive
`media_ok=true` unblock signal.

## §10 — c49 handoff seeds

For the next cycle's researcher / auditor:

1. **Operator inquiry status (axis ii.1)** — has any new rated song been
   delivered since c47 close? If so, the axis (iii) SB1/SB2 κ estimate
   becomes identifiable and the natural next probe is re-running the c26
   chassis at the new N.
2. **Alternative CDN characterization (axis i.2)** — c48 did not
   consume `egress_status.jsonl` beyond snapshot; a c49 axis-i.2 sweep
   over the failure-mode registry would produce a concrete CDN sub-shard
   distribution table.
3. **Workspace policy request review cadence (axis i.3)** — this branch
   did NOT ship `docs/workspace_egress_policy_request.md` (that is item
   i.3's expected outcome); c49 has the option to instantiate it if the
   trigger fires (5+ cycles of periodic probing with no policy change).
4. **Corpus-substitutability probe (axis ii.2)** — a c49 researcher
   could score Freesound.org / FMA subsets for rating-band-distribution
   equivalence; this is the highest-leverage axis that does not depend on
   external actors.
5. **Auditor read for c48 post-merge** — the auditor's job is to verify:
   (a) three-way rubric_hash byte-equality, (b) axes.tsv structure
   conformance to the rubric's "concrete action item" definition,
   (c) verdict.json enum member correctness, (d) c22/c26/c45/c47 anchor
   preservation, (e) zero live-network probes under `scripts/corpus_expansion_plan/`.
6. **Do NOT re-open** c22 chassis, c23 head, c25 feature, or the c26 SB
   thresholds themselves — c48 respects the fix-lock verbatim.

## Reproducibility (Appendix)

- Rubric doc SHA: `c1503cfa44300a3d0cf80e167c5a93066721419e398389531bf40638cd912fe6`.
- Test invocation: `PYTHONPATH=. /usr/bin/python3 tests/test_corpus_expansion_plan.py` → 20/20 PASS.
- Cross-branch integration §65: `PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py` → all 10 new §65 checks PASS.
- Regenerate artifacts under env pins: `bash tools/_c48_run_scripts.sh` (BLAS+PYTHONHASHSEED=0+SOURCE_DATE_EPOCH=1756463424+TZ=UTC+LC_ALL=C.UTF-8).

Cycle 48, fork e651a0d7b0c8, clone 1 (Branch B). `run_id = run-2026-08-28T040704Z`.
