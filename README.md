# long-exposure-runs

Public artifacts from selected long-exposure research runs.

## Runs

- `Memory_Centric_Agentic_Inference/` - A long-exposure run exploring memory-centric architecture for agentic LLM inference, including reports, datasets, scripts, figures, audits, and final synthesized outputs.
- `Physicalized_Model_Weights/` - A long-exposure run exploring whether portions of model inference can be physicalized into hardware, including reports, generated evidence, scripts, figures, audits, and final synthesized outputs.
- `Alignment_Test_Factory/` - A long-exposure run exploring an open alignment test factory for agentic AI systems, including a runnable prototype, schemas, deterministic scorers, Inspect AI integrations, tests, cycle reports, and final audit/report artifacts.
- `Residual_Minimization_ML_Reliability/` - A long-exposure run exploring when residual minimization objectives in scientific machine learning do or do not certify reliability, including theorem sketches, toy simulations, figures, tests, audits, and final synthesized outputs.
- `Rogers_Ramanujan_Derivation/` - A long-exposure run exploring a derivation-first proof trail for the Rogers-Ramanujan identities, including proof notes, symbolic probes, validation artifacts, audits, and final reports.
- `Random_Hyperbolic_Surface_Spectral_Rigidity/` - A long-exposure run reconstructing and extending a random hyperbolic surface spectral-rigidity paper, including proof ledgers, finite Schreier benchmarks, obstruction maps, datasets, scripts, audits, and final reports.
- `Kauai-field-guide/` - A long-exposure run producing a self-contained offline HTML field guide to the plants of Kauai's unpopulated coast (46 species across common / notable / rare & exotic tiers, 113 openly licensed photos plus SVG identification diagrams); open `Kauai-field-guide/site/index.html`.

Active runs:

- `music-gen/` - A long-exposure campaign (launched 2026-08-28) for a transcription-first music pipeline: audio harvesting/curation, source separation, transcription, score/MIDI generation, DAW control, quality heuristics, a trainable 1-7 "ear", and deterministic new-song generation from extracted rules.

The checked-in artifacts are intended as inspectable research outputs rather than a reusable software package. Some paths in generated logs were sanitized from local machine paths before publication.

## Trading research topics (tier-2) — `trading-research/`

Standing per-topic deep-research runs that feed the automated trading platform
**advisory-only** — research never touches the deterministic trade core (it is
surfaced to the human reviewer in the daily report, never fed to portfolio
construction, the risk veto, or execution). They live under `trading-research/`;
each directory is its own long-exposure `working_directory`, and the trader
ingests `trading-research/<topic>/reports/final/final_report.md`.

- `trading-research/geopolitics/`
- `trading-research/macro-rates/`
- `trading-research/energy-commodities/`
- `trading-research/tech-ai/`
- `trading-research/healthcare-biotech/`
- `trading-research/financials/`
- `trading-research/consumer/`

Cadence: monthly fresh runs + weekly follow-up guidance (human-prompted for now).

## Branching policy — `main` is the single source of truth

This repository keeps exactly one long-lived branch: `main`. Everything that
belongs to a run — scaffolding, cycle sweeps, artifacts, final reports — is
tracked there, so `main` alone reflects the complete, current state.

- Work happens on short-lived PR branches, which are merged into `main` and
  then deleted. Nothing is left parked on a branch.
- `.github/workflows/delete-merged-branch.yml` deletes a PR's head branch
  automatically when the PR closes. Enable **Settings → General →
  Automatically delete head branches** as well, so the cleanup holds even if
  Actions are disabled.
- Long-running runs land their periodic sweeps on `main` rather than
  accumulating on a run branch, so a reader never has to hunt across branches
  to find the newest artifacts.
