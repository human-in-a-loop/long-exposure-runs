---
created: 2026-09-05T04:00:00Z
cycle: 29
run_id: run-2026-09-05T040000Z
agent: worker
milestone: M-V4-CLOSE-1/completion-report-v2-emitted-c29
supersedes_path: docs/v4_closure_completion_report.md
---

# Music-Gen v4 Closure — Completion Report v2 (c29)

This is the c22-c28 amendments consolidation report per c29 Track E BOOKKEEPING.
**State at c29 close only; no forward-looking claims per brief.** All SHAs
freshly disk-read at cycle open (c29 anchor drift check: PASS, zero drift
vs c28 records).

---

## §1 Env-Pin Certificate Lineage (c22 baseline → c28)

- **c22**: canonical 7-key subset established. `env_pin_sha256 =
  2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` (keys:
  `PYTHONHASHSEED`, `SOURCE_DATE_EPOCH`, `TZ`, `LC_ALL`, `OMP_NUM_THREADS`,
  `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`). Sweep-time 9-key superset
  documented as diagnostic superset (same variables, extended surface for
  BLAS+torch).
- **c22 → c28**: no re-issue. Env pin has held byte-identical across every
  cycle since c22.
- **c29**: env_pin_sha256 = `2ac444c3…922ca` (verified fresh at cycle open;
  unchanged).
- Cert doc: `docs/v3_determinism_certificate.md` §2, verdict
  `E2E_DETERMINISM_HOLDS` (2026-09-03). Re-issue trigger is env_pin change
  per FD-16(a); no trigger fired.

---

## §2 Sweep-Hygiene Procedure Evolution

- **PROC 2026-09-03** (SWEEP-STORAGE HYGIENE): score-and-delete per
  candidate; ≤500 MB working audio per instrument; df check before each
  stage; disk ≤90%. Landed c9.
- **PROC 2026-09-05** (SWEEP-HYGIENE FIX): render→score→delete per
  candidate; running top-5 audio only; delete all remaining sweep audio
  after each pin; df ≥85% → prune first; batch-render-full-grid BANNED.
  Landed c27 per operator directive after c26 accumulated 432+254
  unscored WAVs on non-CG stage-2 sweeps.
- **c27**: canonical module `scripts/sound_match/_sweep_hygiene_c27.py`
  (sha `771ff42b768d9c44dd96bc9066666bcaa3d6b81ebdc6930fea07f452a3fa51c4`)
  exports `RunningTopK`, `df_guard_before_stage(prune@85%, abort@90%)`,
  `_prune_stale_sweep_audio(age gate=60s)`, `prune_after_pin`. Test suite
  `tests/test_sweep_hygiene_c27.py` 10/10 PASS.
- **c28**: driver integration per
  `docs/sweep_hygiene_c27_driver_adoption_plan.md` (sha
  `37203b8d60594fd09aa4555ffc8f77c1a6402003457c0f7fb5dbfefabbdd053a`).
  Six sweep drivers integrated additively (import block + 3 flags + df
  guard call + per-cell topk push + post-pin cleanup). Legacy behavior
  preserved under `--legacy-batch-render`. Test suite extended 10 → 18
  cases (all green). Per-driver SHA drift table:

  | Driver | pre (c27) | post (c28) |
  |---|---|---|
  | coarse_sweep_sf2.py | `c74c35bc61264c88…` | `3f8bfa0822b62cc9…` |
  | coarse_sweep_sf2_drums.py | `b894f2b322b4e5af…` | `26aa754c4a3052d7…` |
  | coarse_sweep_sf2_guitar.py | `9ddf692f0a903875…` | `d6c54f214be894f5…` |
  | fine_fit_sf2_v2.py | `dc03007365aa29be…` | `4602e5b143acaa7c…` |
  | fine_fit_sf2_drums.py | `54fb4d489088a437…` | `789e63e276c810c7…` |
  | fine_fit_sf2_guitar.py | `96368445891c21f8…` | `91e982b15fdd540e…` |

- **c29**: Track A CG-anchor legacy-mode regression PARTIAL. One driver
  (`coarse_sweep_sf2.py`) proven byte-identical to c1 anchor on 3-preset
  subset {32, 33, 34}: composites (821.942, 821.612, 827.153) and
  render_shas (`652986f7…`, `c1abdad6…`, `c071cae8…`) match c1 anchor
  byte-identically. Remaining 5 drivers × full-preset legacy-mode matrix
  HONESTLY DEFERRED to c30.

---

## §3 Per-Song Stem Landing Table (5 focus songs)

Freshly disk-read at c29 open. `render_family` column: family1 =
real-fluidsynth (sf2), family2 = stem-sampled, htdemucs = htdemucs-6s
stem substitution (OPT3 acceptance).

### Chicken Grease (sha16 `31a164f845f8e27e`) — showcase LANDS_pending_operator

| Stem | Stage | Family | Floor Status | Replay Proof SHA (canonical) |
|---|---|---|---|---|
| bass | v2 pinned (c9 OPT1+OPT3) | family1 sf2 | STILL_INDETERMINATE (0.4946 vs 0.60 aspirational; ≥0.40 floor) | `832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5` |
| drums | c14 revised OPT3 htdemucs substitution | htdemucs | NO_WINNER (sf2 RULED_OUT c11; family2 RULED_OUT c12) | stem SHA `34492c03f301b6ea…` |
| guitar | c15 OPT3 htdemucs substitution | htdemucs | NO_WINNER (sf2 RULED_OUT c14; family2 RULED_OUT c15) | stem SHA `e4ff08ea10f9bbcb…` |
| piano | c13 NULL, c14 grounded INAUDIBLE | none | PIANO_NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE | rms_dbfs=-81.53 |
| other | c14 NULL grounded INAUDIBLE | none | OTHER_NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE | rms_dbfs=-81.73 |
| vocals | htdemucs hybrid overlay (D2 policy) | htdemucs | N/A (policy) | verbatim htdemucs copy |
| **mix** | c17 A/B full render | (per-cell above) | LANDS_pending_operator | `6e13e0075c5d8116784109067cf2c73acd65e47d67398b88aa08e0f752f9484b` |

### What If I Go / WIG (sha16 `252eb21ce7df7328`) — bass profile emitted c28

| Stem | Stage | Family | Floor Status | Replay Proof SHA (canonical) |
|---|---|---|---|---|
| bass | stage-2 emitted c28 from c26 leaderboard | family1 sf2 | STILL_INDETERMINATE (emb_cos_dist=0.187 ≤ 0.40 floor; SF2_CONFIRMED FORBIDDEN pending operator) | `f4118fc72fd393e3…` (per c28 record; ledger event `M-V4-PROFILES-1/what_if_i_go-bass-replay-proof-verified`) |
| drums | stage-1 deferred (Track D c29→c30) | — | — | — |
| guitar | not yet opened | — | — | — |
| piano | not yet opened | — | — | — |
| other | not yet opened | — | — | — |
| vocals | not yet opened | — | — | — |

### Rome (sha16 `51e433ade2a845e1`) — stem_manifest opened c18

| Stem | Stage | Family | Floor Status | Replay Proof SHA (canonical) |
|---|---|---|---|---|
| bass | c23 stage-1 → stage-2 deferred (Track C c28→c29→c30) | — | c23 stage-1 emb_cos_dist=0.5145 predicts SF2_RULED_OUT | — |
| others | not opened; blocked_on `_manager/M-V4-METRIC-SEMANTICS-c16` | — | — | — |

### Peach Dream (sha16 `88d247468cb6d49f`) — stem_manifest opened c19

| Stem | Stage | Family | Floor Status | Replay Proof SHA (canonical) |
|---|---|---|---|---|
| bass | c23 stage-1 → stage-2 deferred (Track C c28→c29→c30) | — | c23 stage-1 emb_cos_dist=0.4437 predicts SF2_RULED_OUT | — |
| others | not opened; blocked_on `_manager/M-V4-METRIC-SEMANTICS-c16` | — | — | — |

### Disco A (sha16 `cdd2717e52820ff6`) — stem_manifest opened c19

| Stem | Stage | Family | Floor Status | Replay Proof SHA (canonical) |
|---|---|---|---|---|
| bass | c26 stage-2 sweep INTERRUPTED mid-run (per c27 Track B verification); c28/c29 re-run deferred to c30 with integrated driver | — | — | — |
| drums | stage-1 deferred (Track D c29→c30) | — | — | — |
| others | not opened; blocked_on `_manager/M-V4-METRIC-SEMANTICS-c16` | — | — | — |

---

## §4 Escalations Open at c29 Close (verbatim IDs)

- `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` — SF2_CONFIRMED
  policy on non-CG bass. `blocked_on_operator=true`. Preserved unchanged
  since c27. c28 canonical narrative: "Do NOT self-resolve. Do NOT re-open
  for auto-resolution under invariants (a)-(e); this one is genuinely
  operator-scoped."
- `_manager/M-V4-METRIC-SEMANTICS-c16` — embedding_cos_vggish
  distance-vs-similarity operator escalation. `blocked_on_operator=true`.
  Preserved unchanged since c16. Two named paths: Path A (distance-as-named;
  thresholds inverted in interpretation), Path B (intended similarity
  semantics; one-line panel/objective correction). Neither auto-resolvable
  under invariants (a)-(d); true operator-scope.

Both escalations `carried_from_cycle=28` (unchanged this cycle).

---

## §5 Discipline-Invariant Audit (AST scan per driver, c29)

All six sweep drivers scanned via `tests/test_sweep_hygiene_c27.py` test_18
(`test_no_forbidden_ast_patterns_in_edited_drivers`). 18/18 test suite
PASS at c29 open. No PRNG imports (`random.*`, `np.random.*`), no
`sidecar_nonfactor` imports, no VST3 state APIs (`get_state`/`save_state`/
`save_preset`/`load_state`/`set_state`), no `--verify-det` flag,
`/usr/bin/python3` interpreter guard at head of each driver.

| Driver | AST audit | Interpreter guard | Hygiene import |
|---|---|---|---|
| coarse_sweep_sf2.py | PASS | PASS | PASS |
| coarse_sweep_sf2_drums.py | PASS | PASS | PASS |
| coarse_sweep_sf2_guitar.py | PASS | PASS | PASS |
| fine_fit_sf2_v2.py | PASS | PASS | PASS |
| fine_fit_sf2_drums.py | PASS | PASS | PASS |
| fine_fit_sf2_guitar.py | PASS | PASS | PASS |

Additional cross-cycle invariants (READ-ONLY anchors, verified byte-identical
pre==post at c29):

- `scripts/sound_match/objective.py` sha
  `8087ce809de9561bff14d2da00a21e4df55dd391b616d136cfc8859263706f11` (composite formula frozen)
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` sha
  `6e13e0075c5d8116784109067cf2c73acd65e47d67398b88aa08e0f752f9484b` (c17 CG A/B anchor)
- `scripts/sound_match/_sweep_hygiene_c27.py` sha `771ff42b768d9c44…` (c27 canonical)
- `docs/agent_picks_selection_invariants.md` sha `c185718424bd5d93…` (invariants (a)-(e))
- `docs/sweep_hygiene_c27_driver_adoption_plan.md` sha `37203b8d60594fd0…` (c28 plan)

---

## Report scope

State at c29 close only. c29 Track A landed a representative one-driver
byte-identity regression against c1 CG-bass anchor + honestly deferred the
full 6-driver × legacy matrix. c29 Tracks B/C/D honestly deferred with
concrete resume commands. This report supersedes
`docs/v4_closure_completion_report.md` (per c14 lemma `supersedes_path` is
`str`, not list).
