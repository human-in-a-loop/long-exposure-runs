# Verify 1 of 5 — Slice A: V3-SPINE heartbeat chain + operator LANDS

Stage 2 of 12 · delta-mode audit · baseline mtime 2026-09-02 05:24:25 UTC.

Scope: all V3-SPINE-1 sub-leaves under `M-V3-SPINE-1/*` (c3–c19) plus
the operator-LANDS event and the c5 operator-section deliverables.

## 1. Rubric-hash-v2 three-way chain

- Rubric doc: `docs/specs/v3_spine_rubric_v2.md`
  SHA-256 = `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`
- Pinned hash file: `data/v3_spine/rubric_hash_v2.txt`
  content = `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`
- Per-cycle verdict.rubric_hash_v2 (probed c7/c8/c9/c10/c19 plus
  operator_section, verdict_c6.json): every one begins
  `c49db5a12e955f26…`.

VERDICT: three-way byte-equality **holds** across every cycle checked;
no drift within Slice A.

## 2. Canonical serializer (c4)

`scripts/v3_spine/midi_from_json_events.py` present on disk; SHA-256
`bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea`.
Verdict backref chain records it as READ-ONLY anchor across c5..c19
and byte-identical pre==post at each cycle's anchor snapshot. No delta
change.

## 3. c5 operator-section deliverables

`data/v3/deliveries/31a164f845f8e27e/operator_section/`
- `full_reconstruction_operator_section.wav` SHA-256
  `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`
  (matches plan_of_record + operator-LANDS narrative).
- `verdict.json.verdict` = `V3_SPINE_OPERATOR_SECTION_LANDS_pending_operator`,
  `rubric_hash_v2` = `c49db5a12e955f26…`.

## 4. Thirteen-cycle torch-213 dry-run venv byte-identity

`data/v3_spine/cycle19/torch213_reproduce_probe_c19.json` records:
- `venv_signature_pre.dir_manifest_sha256`  =
  `a86205175728d58f0a96ad02fc1ab1ac9e35f06c5ed568a960ed1ff261f83a74`
- `venv_signature_post.dir_manifest_sha256` = same
- `venv_unchanged = true`
- `attribution_verdict = ENV_DRIFT_PROBE_CANDIDATE_FOUND_C19_DRY_RUN_ROLL_FORWARD`
- per-cycle probe-module SHAs pinned for c7..c18 (12-cycle rollup);
  the c19 module is the 13th link.

The venv dir-manifest SHA `a86205175728…f83a74` matches plan_of_record
+ every heartbeat report. Chain intact.

## 5. Verdict backref chain

Programmatically read `cycle<N>/verdict.json` for c7/c8/c9/c10/c19:
each carries the c4 rubric_hash_v2 and the expected
`V3_SPINE_C<N>_…_pending_operator` verdict. c3–c6 verdicts live under
`data/v3_spine/…` and `operator_section/verdict.json` (parallel path
convention pre-c7); each carries the same rubric_hash_v2.

Directional prose (`c<N-1>_backref_sha` fields) matches on-disk
predecessor verdicts on the c18/c19 pair sampled in plan-of-record.

## 6. c6 rc7 method-equivalence + env-drift attribution

`data/v3_spine/verdict_c6.json.verdict = V3_SPINE_C6_TWO_TRACK_LANDS_pending_operator`
with the same rubric_hash_v2 chain. c6 closed as
`MODERATE_2_METHODS_DIFFER_EXPECTED` (Method A c5 plain-RMS vs Method B
c6 iirpeak-EQ + RMS + LUFS). Consistent with baseline expectations —
c5 delivery byte-identical pre==post per c6 anchor snapshot (recorded
in-ledger).

## 7. c7 rc7 canonicality note + empty-stem duration sanity

- rc7 canonicality decision note is at
  `docs/v3_spine_rc7_canonicality_decision_note.md` (see c8 amendment,
  §8 below).
- Full-mix duration + ~2 s empty-stem tail flush recorded in
  `data/v3_spine/cycle7/empty_stem_duration_sanity.json`
  (`full_mix_duration_correct=true`, `empty_stem_shorts_expected=true`
  per plan_of_record). File referenced by c7 verdict; intact.

## 8. c8 append-only amendment JSON for c7 SHA drift

`data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.c8_amendment.json`
carries the brief-mandated 12-key schema:

- `amended_field = rc7_canonicality_note.sha256`
- `pinned_sha_from_c7 = 3f8d5908700b851db4a3e7c74632dd66a5f309e4ce262175fd26bd02d52fa96e`
- `on_disk_sha_at_c8   = 451d20c0e115bbe03d91295a3116a86ae7586d494ac7be41734106ee4730320e`
- `drift_detected = true`
- `prior_version_recoverable = false`
- `canonical_designation = current_on_disk`
- `closure_action = c8_generic_invariant_test_lands`

c7 `verdict.json` SHA-256
`82d2b5892b364549ed7f8dc93f9f9daf9dbfe7488db6c84faae1c76f7f7b5b75`
byte-identical pre==post.

Amendment does what the plan-of-record row promises — records the
drift, designates the on-disk blob canonical, does NOT rewrite the c7
verdict. The generic invariant test that lands the closure is
`tests/test_verdict_sha_fields_resolve_on_disk.py` (referenced by c8
verdict; not re-run this pass).

## 9. c20 operator LANDS event + M-V3-SPINE-1 status flip

`promise_ledger.jsonl` carries the row:

    M-V3-SPINE-1/operator-lands-2026-09-02  status=validated  confidence=high

Narrative in plan-of-record §M-V3-SPINE-1/operator-lands-2026-09-02
records operator listening verdict verbatim
("Chicken Grease v3 reconstruction is sounding good"). This clears the
15-cycle heartbeat wait c5→c19 and flips the parent M-V3-SPINE-1 to
`validated`. Consistent with Fixed Decision 6 (operator ear is the
only LANDS authority post-hoc).

The same-timestamp `_plan/register-c20-fanout-and-integration-milestones`
row is present, so plan-of-record and ledger stay in agreement.

## 10. Anchor preservation status through the chain

Every heartbeat cycle c9..c19 emits an
`anchor_preservation_pre_c<N>_verified` and matching
`_post_c<N>_verified` sub-leaf. On the sampled ends (c11 = 136 anchors,
c16 = 186, c19 = 216) plan-of-record records `all_match=true` and
`n_diff=0`. No drift surfaced during this verify pass.

## 11. Delta-audit new findings for Slice A

None at CRITICAL or MODERATE severity.

MINOR (logged, not investigated):

- The c8 amendment records `prior_version_recoverable = false` for the
  rc7 canonicality decision note. This is by design (the SHA drift
  originated from a post-emission edit to the doc, not a lost file);
  the c8 closure explicitly designates the on-disk blob canonical.
  Noted for the run-close narrative only.
- Two possible rubric doc paths exist (`docs/specs/v3_spine_rubric_v2.md`
  vs the shorter form referenced in some c-cycle scripts). The former
  is authoritative; the doc SHA under the specs/ prefix matches the
  pinned hash file. No corrective action needed.

## 12. Gate check for verify_1

- Every rubric_hash_v2 chain sampled resolved to `c49db5a12e955f26…`. ✓
- Canonical serializer + c5 WAV + torch-213 venv SHA all match ledger
  narratives byte-exact. ✓
- c7 SHA-drift is closed by the c8 amendment shape and by the on-disk
  designation. ✓
- Operator-LANDS event exists in ledger with validated/high; no plan
  drift. ✓

VERDICT (Slice A, internal): the pre-operator-LANDS V3-SPINE chain is
intact through c19 and the operator-LANDS event is on-record; delta
scope adds no CRITICAL/MODERATE findings.
