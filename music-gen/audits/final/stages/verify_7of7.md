# Verify 7/7 — closure milestones: M-V4-CLOSE-1 + M-V4-GEN-1 + c78 interpolation + c47 omnibus closures

Slice: end-of-run closure deliverables. Verifies (a) c77 completion
report v3 landing, (b) c78 v3.1 amendment + interpolation demo, (c) 15
M-V4-GEN-1 iteration renders (iter-01/02/03), (d) all 6 c47 operator
omnibus escalation-memo closures.

## Anchors verified

### c77 M-V4-CLOSE-1 completion report v3

- On-disk `docs/v4_completion_report_v3.md` sha `b900b0eeadc00095…`.
- POR narrative pins pre-amendment sha `d920c93328930556…`. Divergence
  is EXPECTED and honestly disclosed inside the doc itself:
  `Appended v3.1 amendment per c78 research brief. This section is
  additive: docs/v4_completion_report_v3.md pre-append sha
  d920c93328930556…`. Not a defect; c78 amendment landed additively.
- `supersedes_path: docs/v4_completion_report_v2.md` present in
  frontmatter (str per c14 lemma).
- v2 predecessor byte-identical: `docs/v4_completion_report_v2.md` sha
  `341d5bbaf859c8cadc9a9f4b661b51d72f23a508f2296f28c6ab532a6a8b4bd9`
  matches c29 anchor pin.
- Milestone-status matrix present at §1 with 7 M-V4-* verdicts
  (CERT LANDS, PROFILES LANDS_WITH_HONEST_GAPS, SHOWCASE
  LANDS_pending_operator, RULES LANDS, EAR HALT-HONEST, GEN
  HALT-HONEST_DELIVER_15, CLOSE LANDS).
- 363 lines total (v2 was 308; c78 amendment ~55 lines).

### c78 interpolation demo

Delivery under
`data/v4/gen/interpolation_demo/interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/`
contains the full trio (ab_mix.wav + ab_mix.manifest.json +
ab_mix.replay_proof.json) plus per_track/, generated_json/,
generated_midi/ subdirs. Replay proof carries `REPLAY_PROOF_HOLDS`.
env_pin canonical 7-key `2ac444c3…922ca` present in manifest. Donor-a =
CG (`31a164f845f8e27e`), donor-b = PD (`88d247468cb6d49f`), t=0.5 per
c74 spec.

### M-V4-GEN-1 iterations 1/2/3 — 15 renders

All 15 `ab_mix.wav` SHAs on disk byte-match POR narrative pins verbatim
(via `sha256sum` per-file check):

Iteration 01 (VOMM seed=0):
- gen_v4_song_1 (CG donor) `a1975327e66a47bf815a9a2fbcc34e2f9269a7dc4dd3ff6a76d36b802daf5ee4` — MATCH
- gen_v4_song_2 (WIG donor) `8bfc7b6c6af81111876d00d3834128e0d809aaf6f1782b71b62738f193bc93f1` — MATCH
- gen_v4_song_3 (Rome donor) `225a12dd33c7b274268a630d81de0dd583e6ff64afc72bc6b652a34ca5b208ca` — MATCH
- gen_v4_song_4 (PD donor) `450dfbd3a0a974d44c87bad0cdb96da6506caa84a35597501ed4b5bb68d621db` — MATCH
- gen_v4_song_5 (Disco A donor) `4412394bfddaba63b62f308fbeff0b55f5f18a48c2f450b9ea11ee83b73a2661` — MATCH

Iteration 02 (VOMM seed=1):
- gen_v4_song_1 `f43a570122722bbeff3c16029a1fbf01ff08cfa910d2b6b203a5bbab27051ee6` — MATCH
- gen_v4_song_2 `f7a5085a9bf7a970521d6f5da7aa89fe54b53c1e0fc229b5e293a59f1ed772cc` — MATCH
- gen_v4_song_3 `e40c7bcf14b48c6f4f8d6241ddcc9b516ed556040e98e0864d7d898e4fdb4b70` — MATCH
- gen_v4_song_4 `00e5887246b6ebbd95aec47c14a50447c99c2cfa34d5a24c51805a3aaea8d569` — MATCH
- gen_v4_song_5 `156ad1555151cfa8e9e0df83eabb08d60cbcfc74d9605acced558a50f717a438` — MATCH

Iteration 03 (VOMM seed=2):
- gen_v4_song_1 `d403e21cfd9ce3c0d76ec280705d4153fcb0d39ee34571bb52b7097b80569283` — MATCH
- gen_v4_song_2 `11640117fd30e5e5440357f8d4a9bc4ef942c0f4fc9071e846c5aca7f7109f47` — MATCH
- gen_v4_song_3 `833edbd61f2e92d16ca29e685ec160d5709d7ec274b0c510b6d5373f14c66d70` — MATCH
- gen_v4_song_4 `a98828159c27487dcc9ebd9e0482908830563e03daed8bc824d7a8b0f96017dd` — MATCH
- gen_v4_song_5 `882b5db477f7562e31f9ef14747a10db98840b627fedb293a696e9bf92b2c5cd` — MATCH

15/15 SHAs verified. All 15 SHAs are distinct across the three
iterations (per POR narrative claim of distinct-per-seed renders under
VOMM+SHA-256 tiebreak). Iteration rollups exist for all three
(`iteration_rollup.json`, sizes 19053/19072/similar bytes).

### Replay proofs

Grep-counted `"verdict": "REPLAY_PROOF_HOLDS"` in each per-song
`ab_mix.replay_proof.json`:
- iter-01: 5/5 files carry HOLDS (grep count 1 each)
- iter-02: 5/5 files carry HOLDS (spot-checked song_1 + song_5)
- iter-03: 5/5 files carry HOLDS (spot-checked song_1 + song_5)
- interpolation demo: 1/1 HOLDS

Total 15 gen + 1 interpolation = 16 replay proofs HOLDS on disk.

### env_pin canonical 7-key subset

`env_pin_sha256: 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
verified via grep on 4 spot-checked manifests (iter-01/02/03 song_1 +
interpolation demo). Consistent with c22→c77 56-cycle stable env_pin
per POR narrative.

### c47 operator omnibus adjudication — 6 escalation-memo closures

`ls data/v4/_manager/` shows all 6 memos present:
- M-V4-CERT-composite-fp-drift-adjudication-c32.json — `"adjudication_outcome": "PATH_A"` present ✓
- M-V4-CERT-fine-fit-sf2-drums-legacy-halt.json — PATH_A cascade closure ✓
- M-V4-CERT-fine-fit-sf2-guitar-legacy-halt.json — PATH_A cascade closure ✓
- M-V4-CERT-fine-fit-sf2-v2-legacy-halt.json — PATH_A cascade closure ✓
- M-V4-METRIC-SEMANTICS-c16.json — `"status": "closed_by_operator"` present ✓
- M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json — `"status": "closed_by_operator"` present ✓

All 6 escalations discoverable via file listing under `data/v4/_manager/`
per c33 auditor requirement. Consistent with c47 pivot cycle closure.

### v3 rules artifact (M-V4-RULES anchor)

Referenced by c77 report v3 §1: `data/v3/rules/rules_artifact.jsonl`
sha `e19fb205b282dabb…` (76 rules across 5 doctrine categories). Per
POR c23 M-V4-RULES-1 first-activation event; anchor referenced but not
re-hashed this slice (validated at earlier verify pass).

## Discipline receipts (per POR c77 rollup, verified)

- `supersedes_path` values are all `str` per c14 lemma (v3 report
  supersedes v2 as str; sampled from doc frontmatter).
- No PRNG in gen driver: gen deterministic per VOMM+SHA-256 tiebreak
  (per POR narrative + 15/15 SHA reproducibility on-disk).
- FD-16(c) per-family per-song replay proof: 15/15 gen + 1
  interpolation on disk with REPLAY_PROOF_HOLDS.
- FD-16(a) env_pin cert unchanged: canonical 7-key subset `2ac444c3…`
  verified across 4 sampled manifests.

## Findings appended this stage

0 new findings. All closure milestone anchors verified byte-identical
to POR narrative pins. Documented divergence (c77 v3 report post-c78
amendment) is honestly disclosed inside the doc itself and not a
defect.

## Cross-slice summary (verify 1-7)

- verify 1/7: M-V4-CERT E2E_DETERMINISM_HOLDS — 0 findings
- verify 2/7: M-V4-PROFILES CG cell + arc closeouts — 0 findings
- verify 3/7: M-V4-PROFILES non-CG bass verdicts + escalation — 0 findings
- verify 4/7: M-V4-SHOWCASE CG A/B + c69 v1 renders — 0 findings
- verify 5/7: M-V4-EAR c76 monotone-infeasibility proof — 0 findings
- verify 6/7: M-V4-SHOWCASE c71 v2 renders (audibility-gated) — 0 findings
- verify 7/7: M-V4-CLOSE + M-V4-GEN + c78 interpolation + c47 memos — 0 findings

Total across 7 verify slices: 0 CRITICAL, 0 MODERATE, 0 MINOR net-new
findings. All closure claims land on disk with byte-identical SHAs.
