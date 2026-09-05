# test_4of5 — Delta-audit adversarial pass, slice c18–c25

**Stage:** 10 of 12 (test 4 of 5)
**Slice:** cycles c18–c25 new deliverables (delta-audit mode; baseline `audits/final/final_audit_report.md` canonical for pre-c18 material)
**Mode:** delta-audit adversarial re-verification of new-per-cycle artifacts; only new findings, new lessons, and reconciliation events surfaced

## Scope

Adversarial re-verification of six new deliverables from the c18–c25 window that were not covered by the committed audit baseline:

1. **M-V4-CERT-1** (c22-first-mentioned closure milestone) — double-run byte-determinism certificate on Chicken Grease v3 reference render
2. **M-V4-PROFILES-1/wig-opened** (c17) — What If I Go 6-stem htdemucs manifest
3. **M-V4-PROFILES-1/rome-opened** (c18) — Rome 6-stem htdemucs manifest
4. **M-V4-PROFILES-1/disco-a-opened** (c19) — Disco A 6-stem htdemucs manifest
5. **M-V4-PROFILES-1/peach-dream-opened** (c19) — Peach Dream 6-stem htdemucs manifest with c25 checkpointed-driver stem path
6. Cross-slice: env_pin_sha256 consistency + `_manager/M-V4-METRIC-SEMANTICS-c16` carryover into c18-c19 openings

## Positive verifications recorded this stage

### M-V4-CERT-1 double-run byte-determinism (operator's "check disk first" milestone)

- `data/v3/deliveries/31a164f845f8e27e/cert_run1/full_reconstruction.wav`
  SHA-256 = `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`
- `data/v3/deliveries/31a164f845f8e27e/cert_run2/full_reconstruction.wav`
  SHA-256 = `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`
- **run1 == run2 byte-equal, verdict `E2E_DETERMINISM_HOLDS` (per docs/v3_determinism_certificate.md §2)**
- `cert_run1/manifest.json.env_pins.env_pin_sha256` = `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d`
- `cert_run2/manifest.json.env_pins.env_pin_sha256` = `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d`
- **env_pin_sha256 identical across both runs — no drift**
- `docs/v3_determinism_certificate.md` carries 2 references to the `cc919559b4508b6b` prefix + 1 to the env_pin + 1 to `E2E_DETERMINISM_HOLDS` — narrative aligned with on-disk anchors

The M-V4-CERT-1 milestone lands cleanly and is defensible under FD-16(a) re-issue-on-env_pin-change semantics.

### Focus-song stem manifests (WIG / Rome / Disco A / Peach Dream)

| Song | sha16 | Manifest SHA-256 | Stems byte-match | blocked_on |
|---|---|---|---|---|
| WIG | 252eb21ce7df7328 | 13e21d69a8711b35c9bd4d2a0c603f6565b048c2fe1a2bc7bcdf6c4ff5ba1013 | 6/6 | c16 metric-semantics |
| Rome | 51e433ade2a845e1 | e00bd15d400b663777d2263614ac579ae5237420e36e7721240ab47433b96d22 | 6/6 | c16 metric-semantics |
| Disco A | cdd2717e52820ff6 | acadbf258cd95814ecff09bdff424d53ee6c97b5fefc0793e82c3a136b8ccc04 | 6/6 | c16 metric-semantics |
| Peach Dream | 88d247468cb6d49f | c4944ee80dfe446b118cf2584e29fa432cc33f21ecdcbe96cc2b63fe946a3b9e | 6/6 | c16 metric-semantics |

Per-song stem SHAs (bass/drums/guitar/other/piano/vocals) were re-hashed against the referenced htdemucs 6-stem WAV files: all 24 pairs match byte-for-byte with zero mismatches and zero missing files. env_pin_sha256 = `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` (canonical 7-key subset) identical across all four manifests.

### Peach Dream stem-path divergence — properly disclosed under invariant (d)

The manifest correctly carries an explicit `source_path_divergence_note` field disclosing that Peach Dream stems live under `data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/rc9_6stem/` rather than the canonical `operator_section/rc9_6stem/` path used by CG/WIG/Rome/Disco A. Filesystem confirms: `operator_section/` does not exist for this song (only `operator_section_c25_checkpointed/` and `operator_section_c27_checkpointed/`). All six stem WAVs at the c25 checkpointed path SHA-match the manifest byte-for-byte. Handling is textbook-invariant-(d)-compliant — brief specified the standard path, on-disk reality was documented honestly, and stems are shown byte-deterministic via the c25 checkpointed run.

### Cross-cycle `_manager/M-V4-METRIC-SEMANTICS-c16` carryover

All four c17/c18/c19 opened manifests carry a `blocked_on` field referencing `_manager/M-V4-METRIC-SEMANTICS-c16` and a `note_metric_semantics_carryover` acknowledging that candidate acceptance under each song's profile suite awaits the Path A vs Path B operator resolution. This is disciplined bookkeeping: opening a song's stem manifest is a scope decision, not a threshold commitment.

## Cross-manifest schema-shape variance (observed, already self-documented — no finding)

WIG's c17 manifest has a different top-level key set (`chosen_section`, `candidate_profiles`, `song_name`, `stems_source_root`, `milestone`) than the c18/c19 canonical shape used by Rome/Disco A/Peach Dream (`agent`, `audio_sha256`, `song_title`, `source`, `schema_shape_note`). The c18/c19 manifests carry a `schema_shape_note` key that explicitly acknowledges this divergence from WIG. No new finding — this is invariant-(d) disclosure already committed on-disk.

## Findings this stage

**None new** for this c18–c25 slice. Every substantive claim tested reproduces on disk with byte-identical SHAs. The largest single open decision — `_manager/M-V4-METRIC-SEMANTICS-c16` — is already surfaced as a MODERATE finding in test_3of5 stage and is carried forward through every c17–c19 opening manifest via the `blocked_on` field.

The three positive findings this stage reinforce:

1. **M-V4-CERT-1 lands cleanly** — full byte-identity + env_pin identity + narrative alignment across cert_run1/cert_run2/certificate doc.
2. **c18/c19 focus-song openings are structurally sound** — 24/24 stem SHAs verify + `blocked_on` carryover disciplined.
3. **Peach Dream divergence handled correctly** — invariant (d) disclosure norm applied verbatim.

## Findings file running total

`audits/final/findings.jsonl` remains at **6 lines** (no append this stage). Slice-D positive verifications recorded in `_stage34_results.json` (peer stage sidecar) and this stage doc.

## Next

Stage 11 (test 5/5): closure verification pass over remaining c19–c25+ closure infrastructure — `M-V4-RULES-1/scaffold-c20` stub contract verification, POR retirement decisions, and cross-check of `_infra/adopt-cycle*-tests` housekeeping. Stage 12 (document 1/1) writes `final_audit_report.md` + `final_audit_summary.json` and appends lesson candidates.
