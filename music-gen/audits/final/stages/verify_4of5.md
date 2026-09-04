# Verify Slice D — CG-bass / CG-drums / CG-guitar profile arcs (c1–c15)

Stage 5 of 12 · scope: v4 M-V4-PROFILES-1 CG-instrument sound-matching arcs (c1 → c15) + related infra (c11 channel-aware replay fix, c13/c14/c15 acceptance forks, agent-picks invariants a–e).

Delta-audit mode: prior baseline `final_audit_report.md` treated canonical for pre-c22 work overall; slice D re-verifies only against POR narrative pins for the c1–c15 CG-profile chain to surface new drifts introduced by that arc.

---

## 1. Anchors verified byte-exact vs POR narrative (24-hex prefix on full SHA-256)

| Milestone / artifact | POR pin (24hex) | On-disk (24hex) | Match |
|---|---|---|---|
| c2 `bass.json` profile v1                                    | `11747a42cb1a8f7f693f27c3` | `11747a42cb1a8f7f693f27c3` | ✅ |
| c4 `bass_v2.json` profile v2                                 | `2a1cb340bffd11016c566467` | `2a1cb340bffd11016c566467` | ✅ |
| c3 `profile_writer.py` (additive `render_sha256_canonical_replay`) | `b36dc448c395a62192aba32d` | `b36dc448c395a62192aba32d` | ✅ |
| c1 `coarse_sweep_sf2.py`                                     | `c74c35bc61264c8846ed716d` | `c74c35bc61264c8846ed716d` | ✅ |
| c15 `cg_guitar_pinned_profile.json`                          | `14d0707898b557df…`        | `14d0707898b557dfa3edaf8f` | ✅ |
| FluidR3_GM.sf2 (READ-ONLY invariant)                         | `74594e8f…1cb0`            | `74594e8f…1cb0`           | ✅ |

## 2. Anchors substantively coherent, POR narrative sha drift (MINOR class)

| POR pin (full) | On-disk (full) | Substantive check | Class |
|---|---|---|---|
| `drums.json` — POR c11 `f48b7d7f…f1595315` <br/>brief-narrative pin `f48b7d7fb1bf28d3ff6b9c9e…` | `f48b7d7fb1bf28d3fb65c582…` | first-16-hex collision; c12 audit already disclosed this class as `drums_anchor_sha256_brief_transcription_error` under `_infra/replay-channel-aware-independent-reverify-c12` | **Not new** (already disclosed c12) |
| `drums.replay_proof.json` — POR c11 `a7877f2ec1dd67b4a4d1cf9b…` | `a7877f2ec1dd67b4d0e21607…` | first-16-hex collision; substantive: `run1==run2==dadafcfc…d64b8d7c` per c12 reverify (READ from on-disk drums replay proof); REPLAY_PROOF_HOLDS TRUE | **Not new** (already disclosed c12) |
| `bass_v2.replay_proof.json` — POR c4 `86948709746b966a766f731a…` | `4b9eea98052d6b2f54dcc7b8…` | full divergence (no prefix collision); substantive: `run1_sha256 == run2_sha256 == 832868d0ea8a81ca…bdb3aeac5` (byte-identical to c2 bass replay proof render SHA per c4 narrative), verdict=`REPLAY_PROOF_HOLDS`, env_pin canonical `2ac444c3…922ca` | **NEW MINOR** — filed |

## 3. Delivery-manifest coherence (c9 / c14 / c15 acceptance-fork chain)

| Manifest | Cycle | acceptance shape | supersedes_path | Verified |
|---|---|---|---|---|
| `cg_bass_pinned_profile.json`   | c9  | 4-key `acceptance_fork.{chosen, operator_authority, rationale, rejected}` (grandfathered per invariant e) | n/a | ✅ |
| `cg_drums_pinned_profile.json`  | c14 | canonical 4-key `acceptance_fork.{chosen, rejected, authority, invariants_doc}`; `acceptance_option=OPT3`; drums_source = htdemucs stem substitution | `str` → `stale/cg_drums_pinned_profile.c13_opt1_below_floor.json` (preserved on disk) | ✅ |
| `cg_guitar_pinned_profile.json` | c15 | 3-key `acceptance_fork.{chosen, rejected, authority}` (c15 drift, invariant (d) disclosed retroactively c16); `acceptance_option=OPT3` | `str` → `_manager/M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json` | ✅ |

Preservation invariant: c14 stale c13 OPT1 sibling exists on disk byte-preserved per invariant (d) + FD-1.
`supersedes_path` uniformly `str` (never list) per c14 lemma.

## 4. Family-verdict / arc-closeout cross-cycle coherence (spot-checked, not exhaustively re-hashed)

- **CG-bass arc** (c1–c7): sf2 STILL_INDETERMINATE (c3 stage-2b emb_cos 0.4946 < aspirational 0.6, above floor 0.4) + family-2 FAMILY2_RULED_OUT (c6, emb_cos 0.0896 < 0.4) → CG_BASS_ARC_EXHAUSTED_NO_CONFIRMED at c7. Resolved c9 via OPT1+OPT3 hybrid on operator directive (composite-relative winner extension for CG-bass ONLY; 0.6 kill-gate retired for CG-bass; 0.4 floor retained).
- **CG-drums arc** (c9→c11→c12→c13→c14): sf2 SF2_RULED_OUT (c11 emb_cos 0.2374 < 0.4) + family-2 FAMILY2_RULED_OUT (c12 emb_cos 0.0372 < 0.4) → CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED (c12). c13 chose OPT1 (below-floor composite-relative), invalidated by c14 audit CRITICAL, revised c14 to OPT3 (htdemucs stem substitution). Retroactively drove agent-picks invariants a/b/c/d formalization at c14.
- **CG-guitar arc** (c13→c14→c15): sf2 SF2_RULED_OUT (c14 emb_cos 0.2584 < 0.4) + family-2 FAMILY2_RULED_OUT (c15 emb_cos 0.03543 < 0.4) → CG_GUITAR_ARC_EXHAUSTED_NO_CONFIRMED (c15). Auto-resolved c15 to OPT3 via invariants a/b/c/d under FAMILY2_RULED_OUT outcome — validates that c14-formalized invariants prevent c13 mis-selection recurrence.

Systematic finding across four CG-instrument arcs (bass, drums, guitar, drums-family2): frozen composite objective ranks non-source-of-truth GM presets ahead of source-of-truth. First-class characterization per FD-1; not a defect. Documented cross-arc at c11–c15 report chain.

## 5. Infra fixes verified in-place

- **c6 replay-program-invariance fix** (`replay.py`): closes CRITICAL blocker on CG-bass family-2 arc. Byte-identical regression on c2 bass replay proof anchor `832868d0…bdb3aeac5` re-verified via file-inspection (bass_v2.replay_proof `run1_sha256==run2_sha256==832868d0…`).
- **c11 channel-aware replay fix** (`replay.py`, on-disk 24hex `1f43027039c45f5e066cf9f3`): drums channel-10 correctness. Independent from-fresh-subprocess re-verify at c12 via `_infra/replay-channel-aware-independent-reverify-c12` (bass_v2 anchor `832868d0…` + drums anchor byte-identical per POR c12 row). REPLAY_REGRESSION_HOLDS.
- **c3 `render_sha256_canonical_replay`** (additive `profile_writer.py` kwarg): backward-compat regression PASS (c2 `bass.json` `11747a42…` byte-identical pre==post). UUID5 `profile_id` invariance under new field held.

## 6. Discipline invariants (spot-checked)

- Interpreter guard `/usr/bin/python3` present on new c1–c15 `scripts/sound_match/*.py` modules (spot-checked coarse_sweep_sf2, profile_writer, replay).
- No PRNG (`random`, `numpy.random.*`, `torch.*` random) in profile-writer / replay / coarse-sweep / fine-fit paths per POR narrative and observed module structure.
- No `sidecar_nonfactor` imports in v4 sound_match layer.
- Env-pin canonical 7-key subset (`PYTHONHASHSEED`, `SOURCE_DATE_EPOCH`, `TZ`, `LC_ALL`, `OMP/MKL/OPENBLAS_NUM_THREADS`) with `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` recorded on every replay-proof / delivery manifest inspected.

## 7. Wall-of-operator-directive discipline

- Operator directive 2026-09-03 part (2) "wait-on-operator BANNED" — audited c9 onward: NO wait-on-operator memos emitted post-c9. Cycles c10–c15 proceed with fork-and-record pattern per binding spec.
- Operator directive part (1) sweep-storage hygiene (`--score-and-delete --keep-top 3 --max-audio-mb 500 --disk-abort-pct 90.0`) — audited c9 CG-drums-sweep-launched + c10/c11 completion: hygiene wired, disk-abort ceiling honored (c9 sweep launch DEFERRED to c10 per statvfs check — first-class honest deferral per FD-1).

## 8. Findings this stage

- **1 MINOR** appended to `findings.jsonl` — `M-V4-PROFILES-1/cg-bass-sf2-replay-proof-v2` POR c4 file-level SHA anchor drift (`86948709…` narrative vs `4b9eea98…` on-disk; substantive claims TRUE). Class: POR narrative anchor drift; no substantive REPLAY_PROOF invalidation. Not reconciled — cosmetic, POR-text-only.
- **0 CRITICAL, 0 MODERATE this stage.**

## 9. Not-yet-verified in Slice D (acknowledged deferrals for delta scope)

- CG-bass stage-1 + stage-2 + stage-2b leaderboard TSV content (only leaderboard SHA anchors in POR narrative sampled, per delta-audit anchor-verification scope).
- CG-drums stage-2 216-cell distinct-render-SHA claim (`216/216 distinct render SHAs`) — spot-check on top-1 render SHA `e8a8e5393…8bcb19de` deferred.
- Guitar stage-2 180-cell distinct-render-SHA claim — analogous.
- `_manager/M-V4-METRIC-SEMANTICS-c16` escalation (blocked_on_operator=true) — orthogonal to slice D verify scope; slice E will confirm carryover.

## 10. Anchors read-only preservation (partial cross-cycle spot check)

- c2 `bass.json` `11747a42…` byte-identical to POR c2 pin — READ-ONLY across c3/c4/c5/c6/c7/c9/c11/c12/c13/c14/c15 preserve claims consistent with on-disk state.
- `profile_writer.py` c3 additive extension backward-compat regression PASS via c2 profile SHA preservation.
- `coarse_sweep_sf2.py` c1 anchor byte-identical (v4 first-code module preserved across all c10–c15 sibling extensions).
- SF2 SHA `74594e8f…1cb0` byte-identical across every v4 render pipeline invocation in Slice D scope.

## 11. Aggregate slice-D verdict

**PASS** with 1 new MINOR (POR narrative anchor drift on bass_v2.replay_proof; substantive claims all TRUE). Slice-D chain of custody from c1 CG-bass first sweep through c15 CG-guitar auto-resolved OPT3 pinned profile holds byte-exact against all major named-code anchors; delivery manifests / acceptance-fork discipline / agent-picks invariants a–e formalization all coherent on disk.
