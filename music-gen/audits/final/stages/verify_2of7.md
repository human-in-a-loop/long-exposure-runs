# Final Audit — Stage 3 (verify 2/7)

Delta window: c32–c78. Mode: DELTA-AUDIT (baseline `final_audit_report.md`
committed 2026-09-05 covers c1–c31).

## Slice for this pass

Item 2 from explore.md §3: **SHOWCASE-1 delivery byte-integrity** — 9 A/B
mixes across 5 song delivery directories under `data/v4/deliveries/`:
Chicken Grease c17 CG showcase mix + 4 c69 v1 A/Bs (WIG, Rome, PD,
Disco A) + 4 c71 v2 audibility-gated re-renders. Each must have:

- `ab_mix.wav` (or `cg_ab_mix.wav` for CG) on disk at the pinned SHA-256
- paired `ab_mix.replay_proof.json` (or `cg_ab_mix.replay_proof.json`)
- `REPLAY_PROOF_HOLDS` with `run1_sha256 == run2_sha256`
- `env_pin_sha256` = canonical 7-key subset
  `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`

## Method

1. Enumerated all 5 song delivery dirs; located every `*ab_mix*.wav` +
   paired `*ab_mix*.replay_proof.json`.
2. Computed SHA-256 on each WAV; asserted the first-16-hex byte-match
   against the ledger-pinned anchor.
3. Parsed each replay-proof JSON; asserted `verdict == REPLAY_PROOF_HOLDS`,
   `run1_sha256 == run2_sha256`, `env_pin_sha256` == canonical subset.

## Results

### WAV SHA-256 vs ledger pin (9/9 OK)

| Mix              | Path                                              | SHA (16 hex)       | Size B       | vs ledger pin |
|------------------|---------------------------------------------------|--------------------|--------------|---------------|
| CG c17           | 31a164f845f8e27e/cg_ab_mix.wav                    | `6e13e0075c5d8116` | 5,292,044    | OK (30.000 s) |
| WIG c69 v1       | 252eb21ce7df7328/ab_mix.wav                       | `6feca5d1fb41ee14` | 1,984,300    | OK (11.249 s HONEST partial) |
| Rome c69 v1      | 51e433ade2a845e1/ab_mix.wav                       | `81e2ef1525ed4485` | 5,292,044    | OK (30.000 s) |
| PD c69 v1        | 88d247468cb6d49f/ab_mix.wav                       | `a300cf4ca12f132e` | 5,292,044    | OK (30.000 s) |
| Disco A c69 v1   | cdd2717e52820ff6/ab_mix.wav                       | `1b673106aae19b9c` | 5,292,044    | OK (30.000 s) |
| WIG c71 v2       | 252eb21ce7df7328/ab_mix_v2.wav                    | `29de5ee222f2d848` | 5,292,044    | OK (30.000 s audibility-gated fix) |
| Rome c71 v2      | 51e433ade2a845e1/ab_mix_v2.wav                    | `9ea1fe324677b01e` | 5,769,516    | OK (~32.71 s max-trunc + SF2 tail) |
| PD c71 v2        | 88d247468cb6d49f/ab_mix_v2.wav                    | `e164c42bc192de78` | 5,767,468    | OK (~32.70 s max-trunc + SF2 tail) |
| Disco A c71 v2   | cdd2717e52820ff6/ab_mix_v2.wav                    | `77cd593a48dbbb27` | 6,434,348    | OK (~36.48 s all-3-audible + SF2 tail) |

9/9 first-16-hex WAV SHAs match the ledger pins (M-V4-SHOWCASE-1 CG
c17 delivery; the four `M-V4-SHOWCASE-1/<song>-ab-full-render` c69
sub-leaves; the four `M-V4-SHOWCASE-1/<song>-ab-full-render-v2` c71
sub-leaves). Sizes reconcile against per-song narratives (WIG c69
partial 11.249 s is honestly disclosed at
`M-V4-SHOWCASE-1/wig-duration-diagnostic-honest` c70; Rome/PD c71 v2
~32.7 s and Disco A c71 v2 ~36.5 s are the c71 max-truncation
policy + SF2-release-tail extensions disclosed in the
`_infra/deliver-ab-v4-render-defect-fix-c71` narrative).

### Replay proofs (9/9 REPLAY_PROOF_HOLDS)

Every proof JSON parses with:

- `verdict == "REPLAY_PROOF_HOLDS"`
- `run1_sha256 == run2_sha256` (and equal to the on-disk WAV SHA)
- `env_pin_sha256 == 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`

FD-16(c) per-family per-song replay-proof scoping satisfied across
both the c69 sf2-only render family (5 proofs: CG + 4 c69 v1) and the
c71 audibility-gated substitution + max-truncation render family
(4 proofs: 4 c71 v2). The c71 new code path warrants one ×2 proof
per per-family per-song scope per operator relaxation 2026-09-03;
4/4 emitted.

### Env-pin cert continuity

Canonical 7-key subset `2ac444c3…922ca` held byte-identical across all
9 delivery proofs. This is the same subset held from c22 M-V4-CERT-1
E2E_DETERMINISM_HOLDS through c77 clean close (verified byte-identical
in prior baseline audit). No cert re-issue trigger (FD-16(a)) fires.

## Findings this slice

**0 new findings.**

Item 2 (SHOWCASE-1 delivery byte-integrity) is substantively backed on
disk: 9/9 mix WAVs at pinned SHAs, 9/9 REPLAY_PROOF_HOLDS with matching
env_pin, all sizes reconcile against the ledger's honest-partial and
max-truncation narratives.

## Baseline carry-forward status

- F1 (ledger-vs-disk parity gap for substantive v4 milestones): the
  9 SHOWCASE deliveries all resolve on disk to their ledger-pinned
  SHAs — this slice closes the SHOWCASE-1 portion of the F1 concern.
- F2 (c31 audit-findings artifact absent on disk): orthogonal; not
  reopened by any SHOWCASE artifact.

## Next stage

Stage 4 = verify 3/7. Natural pick: item 3 (c47 escalation closures —
6 memos claim `closed_by_operator` via `c47_omnibus_closure` block).
Verify each `data/v4/_manager/*.json` sidecar carries the block, cross-
check that no `_manager/M-V4-CERT-*-halt` or
`_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` or
`_manager/M-V4-METRIC-SEMANTICS-c16` post-c47 event re-opens it.
