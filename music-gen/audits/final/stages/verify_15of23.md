# Verify stage 15 of 23 (framework stage 16 of 48)

Slices verified this stage:

- Slice A — **M-DAW-SPIKE-1/palette-schema-v2** (c34 fork 43802db1a81c Branch A clone-0)
- Slice B — **M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround** (c33 Branch B clone-1)
- Slice C — **M-TEX-1/panel/embedding/content-flip-analysis** (c14 clone-2)

Verification protocol (5-step): 1) locate rubric doc + verdict JSON on
disk; 2) hash chain (doc SHA == rubric_hash.txt content ==
verdict.rubric_hash) where the milestone uses one; 3) enumerate the
claimed artifacts and check presence + integrity; 4) cross-check with
downstream cycles; 5) log legibility/drift observations as findings.

## Slice A — M-DAW-SPIKE-1/palette-schema-v2 (c34 Branch A, SCHEMA_V2_LANDS)

**Rubric chain PASS.** All three tokens byte-equal:

- `docs/palette_schema_v2_rubric.md` SHA-256 = `ed737733c79848c9…c452ec2`
- `data/palette_v2/rubric_hash.txt` content = `ed737733c79848c9…c452ec2`
- `data/palette_v2/schema/verdict.json` `.rubric_hash` = `ed737733c79848c9…c452ec2`

**Verdict.** `SCHEMA_V2_LANDS`. 15/15 criteria (a..o) marked PASS,
including 16 valid instances, 8 planted-invalid rejection classes,
determinism × 2, v1 backwards-compat (3 c31 rows revalidate under
`format=v1_flat`), and both c31 palette-v1 anchors + c33 dawdreamer_state
P1 anchors unchanged.

**Companion artifacts present on disk:** rubric doc, report doc,
`scripts/palette_v2/{schema/palette_v2.json,schema/palette_v2.yaml,validate.py,provenance.py}`,
`data/palette_v2/schema/{verdict.json, assignment_ids_v2_expected.tsv, validation_report.tsv, skip_manifest.json}`,
`data/palette_v2/anchor_preservation_before.json`. No legibility gap.

Verdict category: **closure_verified**. No finding.

## Slice B — M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround (c33 Branch B, WORKAROUND_FOUND)

**Rubric chain PASS.** All three tokens byte-equal:

- `docs/dawdreamer_state_extraction_rubric.md` SHA-256 = `611e0b768036d448…4a69f27c`
- `data/dawdreamer_state/rubric_hash.txt` content = `611e0b768036d448…4a69f27c`
- `data/dawdreamer_state/verdict.json` `.rubric_hash` = `611e0b768036d448…4a69f27c`

**Verdict.** `WORKAROUND_FOUND` with `winning_path = "P1"` (iterate
`get_parameter(i)` + `get_parameter_name(i)`). Per-plugin evidence
present under `data/dawdreamer_state/per_plugin/{surge_xt,dexed}/`
with `p1_state_v2.json`, `p1_state_sha`, `p2_preset_hex`, `p2_state_sha`,
`p3_metadata.json`, `p3_state_sha`.

**Observed but expected:** `per_plugin.dexed.P2.equal=false` (SHAs
`1fcb9f23…` vs `d199a849…`) and top-level `per_path.P2.both_deterministic_nonempty=false`.
This is not a defect — the whole point of Branch B was to characterize
which of P1/P2/P3 delivers deterministic non-empty state; P1 wins, P2 on
Dexed is documented in `per_plugin` as non-deterministic, and the winner
selection is P1.

Verdict category: **closure_verified**. No finding.

## Slice C — M-TEX-1/panel/embedding/content-flip-analysis (c14 clone-2, validated/medium)

**Ledger claim.** `validated/medium` event id `d2dc6f2d-54e4-5464-b917-99814895ef80`
pins 13 artifacts, including the report + figure and the
data outputs under `data/tex/embedding_flip_analysis/`:

- `sweep_results.tsv`, `variant_manifest.json`,
  `threshold_characterization.json`, `summary.json`,
  `determinism_check.json` — 5 top-level JSON/TSV
- (also referenced by later `_infra/adopt-content-flip-artifacts` event)
  `variants/{P1..P4,E1..E4}/{variant.mid, bare_midi.wav, effects_layered.wav, panel.tsv}`
  + `anchor_regen/regen_{synth_030s,seed_mid_50s,synth_060s}.tsv`

**On-disk reality (this stage).** `data/tex/embedding_flip_analysis/`
does **not exist** on disk. Every one of the 13 (+ orphan-adoption)
data artifacts pinned by the closure event is missing. Only the
narrative deliverables survive:

- `docs/tex_embedding_content_flip_report.md` — present
- `docs/figures/tex_embedding_flip_analysis.png` — present (assumed;
  ledger cites it and no drift reported)
- `scripts/tex/content_flip/{orchestrator.py, analyze_flip.py}` — present
- `tools/stale/content_flip.log` — archived run log confirms the sweep
  DID run at c14 (rung-1 byte-identity for the 3 anchor seeds PASS;
  byte-determinism × 2 across 17 artifacts PASS; log's own final line
  points at the now-missing `summary.json`)

**Classification.** The substantive knowledge (VGGish content-caveat
verdict, rank-1 sign-disagreement finding, option-(i) promotion path)
survives in the report; the scripts are intact; the archived log
corroborates the numbers. But the byte-determinism × 2 anchor cannot be
re-verified without regenerating the data, the `validated/medium`
closure's evidence pointer chain is broken, and no ledger event
supersedes/invalidates/re-archives the missing files. This is a
**MODERATE** evidence-drift defect.

Verdict category: **closure_partial_evidence_drift**.

## Findings appended this stage

Two rows appended to `audits/final/findings.jsonl`
(one MODERATE + one MINOR) and mirrored to
`audits/final/stages/_verify15_findings.jsonl`.

Cumulative slice coverage after this stage: 15/23 verify passes
complete; 8 remaining (16..23).
