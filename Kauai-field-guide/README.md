# Kauai-field-guide

A long-exposure run developing a comprehensive, locally accessible, HTML-based
field guide to the plants of the unpopulated coast of Kauai, Hawaii — the
roadless Nā Pali Coast and other remote, uninhabited coastal stretches —
covering common, notable, and rare & exotic (including invasive) species.

## Run setup

- Harness: [long-exposure](https://github.com/human-in-a-loop/long-exposure)
  (researcher → worker → auditor loop with end-of-run final auditor →
  final reporter → curator pipeline).
- Provider/model: Claude CLI, `model: claude-opus-4-7` (full model id, set
  globally and per agent role in `agent_models`).
- Live workspace during the run: `/home/user/workspaces/kauai-field-guide`
  on the cloud sandbox that executed the run; artifacts were synced into
  this folder afterwards.
- Loop: `max_cycles: 6`, `cycle_cooldown_seconds: 30`, reporter every
  3 cycles.

## Files

- `kauai_field_guide_long_exposure_prompt.md` — the directive injected via
  `long-exposure launch "<directive>"`.
- `long-exposure.config.yaml` — the exact harness config used for the run.
- `site/` — the deliverable: self-contained offline HTML field guide
  (open `site/index.html` in a browser; no network needed).
- `reports/`, `audits/` — cycle reports, final report, and final audit from
  the run pipeline.
- Remaining files (plan of record, promise ledger, REFERENCES.md, scripts,
  etc.) follow the standard long-exposure workspace conventions.
