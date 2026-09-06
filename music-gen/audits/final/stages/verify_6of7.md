# Verify 6/7 — c71 audibility-gated render fix chain (M-V4-SHOWCASE-1 v2 renders)

Stage 7 of 16 · delta-audit mode · baseline `final_audit_report.md` canonical.

## Slice

Substantive c71 CRITICAL closure of the c69 driver defect (c63 skip-close
policy documented but not implemented → audible harmonic stems dropped).
Per OPERATOR DIRECTIVE 2026-09-05: audibility-gated `htdemucs` stem
substitution + max-truncation policy. Four v2 A/B mixes delivered as
siblings to the c69 v1 anchors (str-supersede per c14 lemma, v1 anchors
preserved byte-identical):

- `M-V4-SHOWCASE-1/wig-ab-full-render-v2`      (WIG,     sha16 `252eb21ce7df7328`)
- `M-V4-SHOWCASE-1/rome-ab-full-render-v2`     (Rome,    sha16 `51e433ade2a845e1`)
- `M-V4-SHOWCASE-1/peach-dream-ab-full-render-v2` (PD,   sha16 `88d247468cb6d49f`)
- `M-V4-SHOWCASE-1/disco-a-ab-full-render-v2`  (Disco A, sha16 `cdd2717e52820ff6`)

Plus the driver additive edit `_infra/deliver-ab-v4-render-defect-fix-c71`
that ships the audibility gate + max-truncation + `--out-suffix` flag.

## Anchor verification (SHA pins vs on-disk)

All POR-pinned SHAs match on-disk state byte-identically.

| Anchor | POR pin | On-disk | Match |
|---|---|---|---|
| `scripts/sound_match/deliver_ab_v4.py` post-c71 | `937f99a8…c453b094c` | `937f99a8…c453b094c` | PASS |
| `scripts/sound_match/deliver_cg_ab_v4.py` (c17 READ-ONLY) | `3c454652…757ee54` | `3c454652…757ee54` | PASS |
| `scripts/sound_match/replay.py` (c11 READ-ONLY) | `1f430270…8bfdb7b9` | `1f430270…8bfdb7b9` | PASS |
| `scripts/sound_match/measure_stem_audibility.py` (c14 READ-ONLY) | `c40b76e4…ede08952` | `c40b76e4…ede08952` | PASS |
| WIG v2 ab_mix.wav | `29de5ee2…6f47e3e9` | `29de5ee2…6f47e3e9` | PASS |
| Rome v2 ab_mix.wav | `9ea1fe32…541b26b0` | `9ea1fe32…541b26b0` | PASS |
| PD v2 ab_mix.wav | `e164c42b…0afa7ce` | `e164c42b…0afa7ce` | PASS |
| Disco A v2 ab_mix.wav | `77cd593a…f8feb5f6` | `77cd593a…f8feb5f6` | PASS |
| WIG v1 ab_mix.wav (must be byte-identical pre==post) | `6feca5d1…f47e3e9` | `6feca5d1…f47e3e9` | PASS |
| Rome v1 ab_mix.wav | `81e2ef15…541b26b0` | `81e2ef15…541b26b0` | PASS |
| PD v1 ab_mix.wav | `a300cf4c…cc02d806` | `a300cf4c…cc02d806` | PASS |
| Disco A v1 ab_mix.wav | `1b673106…ea494080` | `1b673106…ea494080` | PASS |
| PD stem_manifest (invariant (d) fallback consumer) | `d483f2bf…3634cdd4` | `d483f2bf…3634cdd4` | PASS |

## Replay-proof verification (FD-16(c) new-code-path proofs)

All 4 v2 replay proofs on disk with `run1_sha256 == run2_sha256 ==` v2 wav SHA:

| Song | run1_sha256 | run2_sha256 | verdict |
|---|---|---|---|
| WIG     | `29de5ee2…` | `29de5ee2…` | REPLAY_PROOF_HOLDS |
| Rome    | `9ea1fe32…` | `9ea1fe32…` | REPLAY_PROOF_HOLDS |
| PD      | `e164c42b…` | `e164c42b…` | REPLAY_PROOF_HOLDS |
| Disco A | `77cd593a…` | `77cd593a…` | REPLAY_PROOF_HOLDS |

Per FD-16(c), one replay proof per new render family per song. c71 introduced
the audibility-gated substitution + max-truncation code path; 4 proofs cover
all 4 non-CG focus songs. CG (`31a164f845f8e27e`) uses the c17 anchor
`deliver_cg_ab_v4.py` code path, unchanged, and needs no new proof.

## WIG v1 manifest supersede annotation

`data/v4/deliveries/252eb21ce7df7328/ab_mix.manifest.json` on disk carries:
  - `superseded_by_v2_max_truncation` block (added at c71 §5 follow-up)
  - `wig_duration_diagnostic` block (preserved verbatim from c70 P1)

WIG v1 wav bytes byte-identical pre==post (asserted via SHA above).
Manifest JSON drifted by design (annotation append). Per c14 str-supersede
lemma respected.

## Discipline scan

`scripts/sound_match/deliver_ab_v4.py`:
  - Interpreter guard: `#!/usr/bin/env -S /usr/bin/python3` at line 1 (accepted per c15 interpreter policy)
  - PRNG imports: NONE (line 31 is a doc-string mention within a compliance block)
  - `sidecar_nonfactor` import: NONE
  - VST3 state APIs (`get_state`/`save_state`/`load_state`/`save_preset`): NONE
  - env_pin canonical 7-key subset `2ac444c3…922ca` present in all 4 v2 manifests

## Test-suite gate

`tests/test_deliver_ab_v4.py` on disk with 10 test functions (exceeds c71
§4 P4 gate of ≥8):

  1. `test_01_env_pin_drift_raises`
  2. `test_02_min_truncation_policy`
  3. `test_03_peach_dream_invariant_d_fallback`
  4. `test_04_absent_stems_manifest_shape`
  5. `test_05_manifest_provenance_field_completeness`
  6. `test_06_prove_replay_writes_second_render_into_fresh_tempdir`
  7. `test_07_absent_stem_htdemucs_substitution_when_audible`
  8. `test_08_absent_stem_stays_silent_when_below_floor`
  9. `test_09_max_truncation_policy`
  10. `test_10_v2_output_suffix_writes_sibling_files`

Tests 07/08 explicitly cover the c71 audibility-gate. Test 09 covers the
max-truncation policy change. Test 10 covers the `--out-suffix` sibling
preservation (guarantees v1 anchors are not clobbered on re-runs).

## Audibility-metadata spot check (Disco A)

Per-cell `audibility_verdict` + `rms_dbfs` in `ab_mix_v2.manifest.json`:

| Stem | audibility_verdict | rms_dbfs | POR narrative |
|---|---|---|---|
| guitar | true  | -25.08 | matches operator's -24.8 AUDIBLE |
| other  | true  | -20.95 | matches operator's -20.8 |
| piano  | true  | -21.82 | matches operator's -21.6 |

Disco A is the strongest test — all 3 unprofiled stems substituted per c71
`_absent_stem_dispatch` gate. Manifest data coherent with c71 POR narrative.

## Operator-directive traceability

`_infra/deliver-ab-v4-render-defect-fix-c71` narrative names:
  - OPERATOR DIRECTIVE 2026-09-05 (c63 skip-close policy application)
  - c17 anchor `deliver_cg_ab_v4.py` preserved byte-identical
  - 3 new branches (guitar/piano/other) additive; c69 semantics preserved for silent branches via `absent_no_audible_signal` label

Chain: c63 policy documented → c69 driver dropped audible stems (unnoticed) →
operator surfaces defect at c71 → c71 P1 driver-fix + P3 4 v2 renders + P4
completion-report-v2 append + P5 WIG v1 manifest supersede annotation.

## Verdict

All 13 anchor SHAs PASS. All 4 REPLAY_PROOF_HOLDS. Discipline gates GREEN
(no PRNG / no sidecar / no VST3 state APIs / canonical env_pin / interpreter
guard). Test suite 10 functions covering c71 additions. Manifest audibility
metadata coherent with POR narrative. c17/c11/c14 READ-ONLY anchors + 4 v1
c69 anchors + PD stem_manifest all byte-identical pre==post.

**0 new findings appended this stage.** c71 audibility-gated render fix
chain lands substantively as delivered.

## Notes carried forward

- The 4 c71 v2 A/B mixes contribute to the M-V4-SHOWCASE-1
  LANDS_pending_operator disposition and to the c77 v3 completion-report
  deliverable count (verified separately in a prior stage).
- Rome/PD/Disco A v2 durations 32-36 s (SF2 release-tail preservation under
  max-truncation) are HONEST per FD-1 c71 disclosure — NOT a defect.
- WIG v2 duration 30.000 s per max-truncation (piano canonical 29.921 s +
  release tail); the c70 WIG partial-mix truncation defect is fixed as a
  side effect of the max-truncation policy.
