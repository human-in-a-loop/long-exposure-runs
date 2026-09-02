# Verify pass 1 of 23 — VP-A #1..#3 (invalidated first-class negatives)

Stage 2 of 48. Slice: three invalidated milestones from the run's six-item first-class negative-findings set. Verify that the on-disk evidence supports the invalidation narrative and that the record is honest (not glossed).

## 1. M-TEX-1/panel/embedding c11 — CLAP fetchability fail, VGGish ladder rung landed

**Ledger:** validated/medium at c4 → reopened/high at c11 → in-progress/medium c11 → invalidated/medium c11.

**Evidence on disk:**
- `data/tex/panel_rung_log.jsonl`: single row records attempted_top_rung=`clap`, landed_rung=`vggish`, with URLs pinned.
- `data/tex/clap_upgrade_smoke.json`: VGGish rung self-distance = 7.387e-08 (tolerance ≤ 1e-4 → PASS); cross (original vs bare-MIDI) cosine = 0.1234 (matches cycle-9 stage-by-stage row per the log's `cross_distance_reproduces_cycle9_row: true`).
- Fetchability ladder in `panel_rung_log.jsonl` documents 5 rungs (1.0 laion_clap import, 1.1 with `torch.library.register_fake` no-op patch, 1.2 CLAP_Module init, 1.3 weights fetch, 2 VGGish, 3 none_available). Rungs 1.0..1.2 blocked with concrete reasons: torchvision::nms op missing on cpu-only torch 2.13.0; HuggingFace roberta-base config fetch fails on SSL CERTIFICATE_VERIFY_FAILED (workspace egress cert block). No local roberta-base cache. Rung 1.3 not_attempted (upstream block). Rung 2 landed.

**Verdict:** CONFIRMED. The "invalidated/medium" ledger status reflects the CLAP top-rung falling out of the ladder; the panel's embedding family still resolves at the VGGish rung with a documented rung log, and the panel numeric contracts (self ≤ 1e-4, cross reproduces c9 anchor) hold. Narrative is honest — the invalidation names the rung that failed, not the panel itself.

## 2. M-TRANS-1/basic-pitch/octave-suppression c8 — +0.15 aggregate uplift below +0.3 success bar

**Ledger:** in-progress/medium → invalidated/high at c8.

**Evidence on disk:**
- `data/transcribe/octave_suppression/grid_search.tsv`: 3×3 grid over T_min ∈ {50, 100, 200} ms × overlap_min ∈ {0.3, 0.5, 0.7} × 3 mixes (synth_030s/060s/090s) + baseline row per mix (10 cells × 3 mixes = 30 rows).
- Best-cell aggregate bass F1 uplift = mean over 3 mixes of (0.1476, 0.1455, 0.1607) = **+0.1513**. Every non-baseline cell produces the same per-mix uplift → the grid degenerates because the octave-pair detection under this rule only fires on a stable set of confidence-tie pairs regardless of the tightness of T_min / overlap_min inside the tested range.
- `passes_harmless=True` on every cell: drums_F1_delta = 0.0 (drums have no ground-truth notes on these synth mixes — F1 is 0.0 baseline); other_F1_delta = 0.0 uniformly.
- Success bar (from plan-of-record milestone row): "bass F1 aggregate uplift ≥ +0.3 evaluated honestly — falsifiability escape hatch invoked if unmet." +0.1513 < +0.3 → falsifiability escape hatch invoked; milestone marked invalidated/high. That IS the pre-registered outcome for shortfall.

**Verdict:** CONFIRMED. Grid degeneracy is real: only ~14/29/44 notes suppressed per mix (identical across all 9 grid cells for a given mix), so no cell can beat +0.15 without a different suppression rule (e.g., non-tied confidence resolution, wider velocity-based tiebreak, or a different octave-detection window). Invalidation narrative is honest.

## 3. M-EAR-1/synthetic-label-stability-audit c22 — CORN chassis C1/C2 FAIL

**Ledger:** in-progress/medium (twice) → invalidated/high at c22.

**Evidence on disk:**
- `data/ear/stability_audit/stability_report.json` fields:
  - C1 "MAE reproducibility": cycle6_mae=0.8909 vs envelope [p05=1.0318, p95=2.0818] → **FAIL** (cycle-6 result is more optimistic than the entire 5th percentile of the 10-recipe synthetic-label envelope; the chassis's cycle-6 MAE was recipe-specific, not chassis-stable).
  - C2 "Rank stability": mean pairwise Kendall τ-b = **0.0588** across 45 pairs (10-choose-2); threshold ≥ 0.7 → **FAIL** (τ range [-0.346, 0.496]; median 0.079).
  - C3 "Byte-determinism × 2": marked **PENDING** in report body.
- Byte-determinism spot-check: `sha256(stability_report.json) == sha256(stability_report.run1.json)` → both `36615ad7…6889c9aa`. C3 verifiable PASS on disk; the report's `PENDING` verdict was never updated.

**Verdict:** CONFIRMED for chassis-invalidation. C1 + C2 FAILs alone force the chassis-instability finding regardless of C3. But — see MINOR finding below on C3.

## MINOR (logged only, not acted on)

- **C3 verdict stale in stability_report.json.** The report body says `PENDING` for C3 while the two run outputs are byte-identical on disk. Report was written from run1 alone; the byte-determinism check was performed externally (evidenced by the `.run1.json` sidecar) but never re-materialized back into `stability_report.json`. Impact on the invalidation verdict: none — C1 + C2 already FAIL. Logged.

## Cross-check against downstream

The three invalidations trigger real downstream commitments in the ledger:
- The c11 CLAP failure crystallizes the c14 `M-TEX-1/panel/embedding/content-flip-analysis` sub-sub-milestone (systematic sweep to bound the family disagreement) — validated/medium at c14.
- The c8 octave-suppression failure crystallizes the falsifiability escape hatch policy for future extractor-metric interventions.
- The c22 chassis failure crystallizes the c23 head-regularization audit, c25 feature-representation audit, and ultimately the c26 `_manager/M-EAR-1-path-B-commit` durable commitment (validated/high at c26) — the "Path B" that defers all ear calibration to real labels. This is the audit's most consequential downstream chain: the c22 invalidation is load-bearing for the entire real-label ear-model campaign (v0/v1/v2/v2.1) that follows.

All three first-class negatives are integrated into the plan of record as intended.

## Findings appended

3 findings appended to `audits/final/findings.jsonl` (severity MINOR for the C3 stale verdict; no CRITICAL or MODERATE findings this pass — all three invalidations are honest, well-evidenced, and load-bearing for downstream work).

## Slice progress

Cumulative verified milestones this pass: 3 (VP-A #1, #2, #3).
Remaining verify slices: 22.
Next slice (S3): VP-A #4..#6 — c23 head-regularization, c25 feature-representation, c35 palette-schema-v2-hydration-render RENDER_FAILS.
