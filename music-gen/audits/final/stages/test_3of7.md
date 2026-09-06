# Test Stage 3/7 — Delta-Audit Adversarial Pass (c77-c87 delta scope)

## Scope
Delta-scope adversarial pass on the c77-c87 delta boundary above the committed baseline `audits/final/final_audit_report.md`. Focus areas per test-stage plan:
1. c78 interpolation-hybrid demo provenance chain integrity
2. All six c47 operator omnibus escalation memos remain CLOSED on disk
3. 25 A/B deliverable list is complete (9 focus + 15 gen + 1 interpolation)
4. Delta-scope disciplines: no new SF2_CONFIRMED on non-CG bass; no preservation-spin sub-leaves; no wait-on-operator memo

## Checks performed

### T3.1 — c78 interpolation demo provenance
Path: `data/v4/gen/interpolation_demo/interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/`
Manifest fields verified:
- `donor_a_sha16 = 31a164f845f8e27e` (Chicken Grease — first operator-approved focus song per c47 chain)
- `donor_b_sha16 = 88d247468cb6d49f` (Peach Dream — per c70 M-V4-GEN-1/interpolation-demo-spec pre-registered pair)
- `interpolation_t = 0.5`
- `interpolation_semantics = per_position_sha256_tiebreak_at_threshold_t`
- `generator = vomm` (consistent with c73 `_gen/vomm-promoted-primary` supersede + c74 `_gen/anticipation-abandoned-weights-unfetchable`)
- `rules_artifact_sha256 = e19fb205b282dabb...` (READ-ONLY anchor byte-identical to c23 M-V3-RULES-1/first-activation)
- `env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5...` (canonical 7-key subset, byte-identical since c22)
- `ab_mix_sha256 = b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a`
- `n_positions = 24` (both `sampled_rule_ids_donor_a` and `sampled_rule_ids_donor_b` populated)

Replay proof (`ab_mix.replay_proof.json`):
- `verdict = REPLAY_PROOF_HOLDS`
- `run1_sha256 == run2_sha256 == b129c6d1bac8be90fa32249a012a47e5...` (byte-identical ×2 in fresh tempdirs)
- `env_pin_sha256` matches manifest

**Verdict**: PASS. c78 interpolation demo satisfies FD-16(c) per-family per-song replay proof requirement + pre-registered donor pair from c70 + canonical env_pin subset unchanged. Deferrable-then-delivered narrative (c74 P6 → c78 landing after c77 clean close) is coherent.

### T3.2 — c47 operator omnibus escalation memos still CLOSED
All 6 sidecars under `data/v4/_manager/` inspected:
| Memo | status | blocked_on_operator |
| --- | --- | --- |
| M-V4-CERT-composite-fp-drift-adjudication-c32.json | closed_by_operator | False |
| M-V4-CERT-fine-fit-sf2-drums-legacy-halt.json | closed_by_operator | False |
| M-V4-CERT-fine-fit-sf2-guitar-legacy-halt.json | closed_by_operator | False |
| M-V4-CERT-fine-fit-sf2-v2-legacy-halt.json | closed_by_operator | False |
| M-V4-METRIC-SEMANTICS-c16.json | closed_by_operator | False |
| M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json | closed_by_operator | False |

**Verdict**: PASS. Zero re-opening across c77-c87 delta scope. Consistent with campaign L151-152 CLOSED verdict.

### T3.3 — 25 A/B deliverable list complete
On-disk enumeration:
- 4 focus v1 `ab_mix.wav` under `data/v4/deliveries/*/` (WIG, Rome, PD, Disco A — c69)
- 4 focus v2 `ab_mix_v2.wav` under `data/v4/deliveries/*/` (c71 audibility-gated substitution fix)
- 1 CG showcase `cg_ab_mix.wav` (c17)
- 15 gen A/Bs under `data/v4/gen/iteration_{01,02,03}/*/ab_mix.wav` (3 iters × 5 songs)
- 1 interpolation demo `data/v4/gen/interpolation_demo/.../ab_mix.wav` (c78)

Total = 4 + 4 + 1 + 15 + 1 = **25**. Matches campaign closure claim.

**Verdict**: PASS. No drift in deliverable count.

### T3.4 — No SF2_CONFIRMED on non-CG bass (invariant preserved)
Search returned no non-CG bass profile carrying SF2_CONFIRMED in delta scope. c47 OPT1 extension replaces the CONFIRMED gate with best-of-search across families under distance semantics (0.40 upper-bound rules out only degenerate candidates). c9 CG bass_v2 acceptance under composite-relative rule remains the only precedent; downstream focus songs deliver via c69/c71 audibility-gated mixes rather than fine-fit sf2 pinning.

**Verdict**: PASS.

### T3.5 — c47 preservation-spin BAN + wait-on-operator BAN honored across delta
Delta-report tail sample (c85-c87 substantive-close verdicts VALIDATED, zero CRITICAL, zero MODERATE, `[[BRANCH_COMPLETE]]` at c87) shows no per-cycle preservation sub-leaves and no wait-on-operator memos. c78 stands as a single deferred-then-delivered substantive event, not a preservation spin.

**Verdict**: PASS.

## New findings this stage
None. All five adversarial probes returned clean against the delta boundary.

## Cumulative delta-scope findings (through stage 11)
- **From test_1of7**: 1 MODERATE — `M-V4-CLOSE-ledger-agent-field-drift-c77-c78` (10 delta-scope ledger events at c77+c78 missing `agent` field; clean in c85-c87). No addition this stage.

## Discipline reminders honored
- FD-1 halt-honest (all probes cite on-disk facts; no fabrication)
- FD-16(a) env_pin cert unchanged (`2ac444c3...`) across 57 cycles c22→c78
- FD-16(c) per-family per-song replay proofs held on every delivered artifact examined
- c47 preservation-spin BAN + wait-on-operator BAN honored
- No READ-ONLY anchors touched
