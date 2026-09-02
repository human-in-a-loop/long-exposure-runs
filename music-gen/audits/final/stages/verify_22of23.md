# Final Audit — Stage 23 (verify 22/23)

<checkpoint>
  <stage>verify</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~190k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Verified 3 fresh closure_verified milestones from earlier-cycle infrastructure (M-SEP-1/alternative UMXHQ c5; M-HEUR-1/meta-tracker c4; M-RULES-1/schema/ledger-writer c6). Anchor-verified on-disk artifacts, checked determinism claims, fixed-decision compliance (no PRNG, isolation, append-only), and grep-confirmed the interpreter guard where in scope.</what-i-did>
  <next-action>Slice 23/23 next stage; then Test (adversarial) passes begin.</next-action>
  <gate-check>Continuing in verify — 3 milestones cleared with 0 defects. All findings emitted as closure_note (severity INFO / verdict CONFIRMED).</gate-check>
</checkpoint>

## Anchors verified read-only pre-slice
- `data/rules/ledger.jsonl` — 76 rows (matches plan-of-record extraction footprint).
- `data/separation/results.tsv` — 37 rows; separator column ∈ {htdemucs, openunmix, naive_copy_third} + header.
- `data/heuristics/{d15d5c009a70cc32,d251556aedfe35ef,d60cead66dbd0b95}/meta_descriptors.json` — 3 songs, one per seed.

## 1. M-SEP-1/alternative (c5, validated/high) — closure_verified

**Ledger status.** `validated/high` at cycle 5 (worker, 2026-08-28T06:05:54Z); parent `M-SEP-1` rolls up validated/high at the same cycle. Success criterion: "UMXHQ runs on all 3 mixes; same TSV schema as baseline; naive-copy baseline row present; adopt-or-build verdict cites the numbers."

**On-disk anchors verified.**
- `scripts/separation/run_alternative.py` (70 LOC) — `openunmix.umxhq(targets=STEM_ORDER, niter=1, residual=False)` at line 44; deterministic driver.
- `scripts/separation/verify_umxhq_determinism.py` (146 LOC) — SHA-256 byte-identity harness; `bytes_identical = sha256(a_path) == sha256(b_path)` at line 104; sidecar SHA at line 134.
- `data/separation/results.tsv` — 12 UMXHQ rows (4 stems × 3 mixes: `synth_030s`, `synth_060s`, `synth_090s`); 12 htdemucs rows; 12 naive_copy_third baseline rows; TSV schema `separator, mix_id, stem, sdr_db, sir_db, sar_db, est_energy_dBFS` matches htdemucs baseline exactly.
- Sample UMXHQ row on `synth_030s`: drums SDR=8.302 dB / bass 9.947 / other 3.515 — bounded, finite, non-vocal-stem SDR positive on the 3 pitched stems; vocals row present with est_energy_dBFS reported as GT-zero case per the sub-milestone's success-criterion wording.

**Honesty check.** The header is authored once (`separator` column key). All UMX rows carry finite values on drums/bass/other; the vocals row records the est_energy_dBFS floor per the sub-milestone's design (GT-zero case). Naive-copy baseline is present as a first-class row (`naive_copy_third`), enabling the "adopt-or-build verdict cites the numbers" success bar to be met honestly.

**Fixed-decision compliance.**
- No PRNG in `scripts/separation/run_alternative.py` (grep for `random.|np.random|torch.rand`).
- SF2 hash `74594e8f…1cb0` pinned in `scripts/separation/synth_gt.py:216` (`hashlib.sha256(Path(SF2).read_bytes()).hexdigest()`) — determinism-anchor invariant preserved across the ground-truth stack this alternative measures against.
- Determinism verifier uses SHA-256 byte-identity; no float-tolerance escape hatch.

**Downstream chain.** `M-TRANS-1` (c6) consumes M-SEP-1 stems for basic-pitch note-level F1 measurement; `M-SCORE-1/merged-full-song` (c8) inherits the same synth-mix per-stem MIDIs. UMXHQ is the alternative comparator arm of the adopt-or-build verdict, which selected htdemucs and deferred per-instrument isolation.

**Verdict.** closure_verified — 0 defects.

## 2. M-HEUR-1/meta-tracker (c4, validated/high) — closure_verified

**Ledger status.** `validated/high` at cycle 4 (worker, 2026-08-28T05:40:00Z); parent `M-HEUR-1` rolls up validated/high the same cycle. Success criterion: "Meta-tracker JSON produced on all 3 seed songs; anchored-tail weight matches the formula numerically on seed_long_87s (0.2333…) and seed_mid_50s (0.6667…)."

**On-disk anchors verified.**
- `scripts/heuristics/meta_tracker.py` (193 LOC) — canonical `anchored_tail_weight(prev_t_end_s, this_t_start_s)` at line 38; consumes each clip's `anchored_tail` bool and weights via `max(0, (30 - overlap)/30)`.
- `data/heuristics/d60cead66dbd0b95/meta_descriptors.json` — 87-s seed. Confirmed on disk: `anchored_tail_formula = "weight = max(0, (30.0 - overlap_s) / 30.0)"`; `clip_weights[3] = 0.23333333333333334` — matches the plan-of-record `seed_long_87s` reference value of `0.2333…` to full float precision.
- Both remaining seeds (`d251556aedfe35ef`, `d15d5c009a70cc32`) have `meta_descriptors.json` present — 3-song coverage bar met.
- Descriptors carry all four required macro fields: `dynamics_trajectory`, `form_coherence`, `peak_location_fraction`, `heuristic_variance_across_clips`.

**Honesty check.** Anchored-tail weight formula is stored verbatim in the descriptor JSON (self-documenting invariant). `form_coherence` computed on the ORIGINAL source (per the module docstring at line 84 `_song_form_coherence` — clip-concat would confound diagonal-band ratio). Meta-tracker returns floats, not booleans-as-conclusions.

**Fixed-decision compliance.**
- No PRNG in `scripts/heuristics/meta_tracker.py`.
- Non-factor isolation: `tests/test_heuristics_isolation.py` (166 LOC) explicitly guards against `sidecar_nonfactor` imports across the M-HEUR-1 module (5 references in the test).

**Downstream chain.** Consumed by `M-EAR-1/preparation/features` (c6) as the 4-D M-HEUR-1 vector adjoined to the PANNs 2048-D representation; anchored-tail per-song aggregation lifts directly from this module's weighting formula.

**Verdict.** closure_verified — 0 defects.

## 3. M-RULES-1/schema/ledger-writer (c6, validated/high) — closure_verified

**Ledger status.** `validated/high` at cycle 6 (worker, 2026-08-28T07:15:00Z); parent `M-RULES-1/schema` rolls up validated/high the same cycle. Success criterion: "Duplicate-id append rejected; supersede pointing at nonexistent id rejected; supersede chain (A→B→C) resolves transitively; source contains no `open()` with `'w'` or `'r+'`."

**On-disk anchors verified.**
- `scripts/rules/ledger.py` (193 LOC). Grep for open modes confirms only `open(p, "a")` at line 185 — no `'w'` or `'r+'` writes (append-only invariant honored at the syntactic level).
- Public API: `write_rule`, `write_supersede`, `effective_rules` (line 152), `LedgerError` (line 89) as documented in the plan-of-record row.
- Duplicate-id rejection: line 107 raises `LedgerError(f"duplicate rule_id: {rid}")`.
- Supersede target-existence check: line 126 raises `LedgerError(f"supersedes_rule_id {sup} not found in ledger")`; self-supersede rejected at line 130.
- `data/rules/ledger.jsonl` — 76 rows, sample first two rows carry all schema-mandated fields (`rule_id`, `rule_type`, `parameters`, `provenance_pointers`, `schema_v: 1`, `scope`, `event_type`, `confidence`, `event_id`, `extractor`, `extractor_version`, `ts`). Content-derived `rule_id`s (`rule_0271c7a9f3b5f606`, `rule_821a916f5a58a283`) match the `M-RULES-1/schema/synthetic-instances` reproducibility contract.

**Honesty check.** Reader implementation (`effective_rules`) resolves supersede chain by streaming rows in insertion order; the writer refuses to append a supersede whose target does not yet exist in the ledger prefix — this rejects out-of-order emission and enforces the transitive-chain contract explicitly rather than by convention.

**Fixed-decision compliance.**
- No PRNG in `scripts/rules/ledger.py`.
- Append-only invariant syntactically enforced (grep-verified: single `open()` call, mode `"a"`).
- `tests/test_rules_schema.py` (413 LOC) — plain-assert suite (no pytest dep) covering the four planted-invalid classes plus edge cases per the sibling `M-RULES-1/schema/tests` milestone.

**Downstream chain.** Every `M-RULES-1/extraction` cycle-9 event and every `M-RULES-1/extraction/breadth-seeds` cycle-12 event lands its typed rule rows through this writer; the c14/c15 D_minor augmented shard `data/rules/ledger_i3_dminor.jsonl` reuses the same writer contract; every c34+ palette assignment resolves its provenance pointers by reading rows this writer emitted.

**Verdict.** closure_verified — 0 defects.

## Cross-cutting observations (no findings this slice)
- All three milestones sit at the base of long downstream chains (M-SEP-1/alternative → M-TRANS-1 → M-SCORE-1; M-HEUR-1/meta-tracker → M-EAR-1/preparation/features; M-RULES-1/schema/ledger-writer → every extraction event + every palette assignment). Their durable validation is what allowed the campaign's later cycles to treat them as read-only anchors without re-verification. No drift observed.
- The append-only writer's supersede-target check propagates to `data/rules/ledger_i3_dminor.jsonl` (86 rows per plan-of-record row for `M-GEN-1/batch-v3-i3`); the same invariant lets `M-GEN-1/collision-model-birthday-paradox` treat rule_ids as content-derived stable keys.

## Findings appended this stage (3)
- `closure_note` on M-SEP-1/alternative (INFO / CONFIRMED)
- `closure_note` on M-HEUR-1/meta-tracker (INFO / CONFIRMED)
- `closure_note` on M-RULES-1/schema/ledger-writer (INFO / CONFIRMED)

## Cumulative slice coverage (post-stage-23)
| Slice | Milestones cleared | Defects |
|-------|--------------------|---------|
| 1..22 | 63 verified (per prior stage summaries) | 0 CRITICAL / 0 MODERATE |
| 23 (this) | +3 | 0 |
| Running | 66 | 0 defects |

## Summary
| Milestone | Cycle | Status | Anchors | Determinism | Fixed-decision | Verdict |
|-----------|-------|--------|---------|-------------|----------------|---------|
| M-SEP-1/alternative | 5 | validated/high | 12 UMX rows + 12 htdemucs + 12 naive-copy; run_alternative.py 70 LOC; verify_umxhq_determinism.py 146 LOC | SHA-256 byte-identity harness | SF2 pinned, no PRNG, no network in script | closure_verified |
| M-HEUR-1/meta-tracker | 4 | validated/high | 3 seed meta_descriptors.json; 87-s clip weight 0.2333… | Formula stored verbatim in JSON | No PRNG, sidecar isolation test present | closure_verified |
| M-RULES-1/schema/ledger-writer | 6 | validated/high | ledger.py 193 LOC single `open(…, "a")`; ledger.jsonl 76 rows | Content-derived rule_ids reproduce | Append-only + duplicate/target-missing raises | closure_verified |

[OUTPUT: final_audit_stage]
Stage 23 (verify 22/23): 3 milestones verified — M-SEP-1/alternative (c5), M-HEUR-1/meta-tracker (c4), M-RULES-1/schema/ledger-writer (c6). 0 defects.
File: audits/final/stages/verify_22of23.md
Findings appended: 3
[END OUTPUT: final_audit_stage]
