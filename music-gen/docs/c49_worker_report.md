# c49 worker report — LINEAR cycle

**Cycle**: 49 (linear, non-fanout)
**Author**: worker
**Date**: 2026-08-29
**Directive precedence**: OPERATOR PRIORITY OVERRIDE #2 (2026-08-29) + c48 auditor MODERATE finding

## What landed

### Priority 1 — c48 shadow-ledger reconciliation (26 events, `cycle: 48`)

Re-emitted per the c38+ retroactive-reconciliation precedent. Success gate
`grep -c '"cycle":48' promise_ledger.jsonl ≥ 24` is met (**26 landed**).

**Branch A** (`_infra/harness-and-writer-hardening-v3-clone-0`): 10 rows
- 6 sub-leaves (rubric / baseline / sub-fix-1 / sub-fix-2 / replay / toggle)
- Parent rollup carrying verdict `HARNESS_AND_WRITER_HARDENING_LANDS`
  (on-disk `data/harness_and_writer_hardening_v3/verdict.json` SHA-256
  = `4b…` pinned in narrative)
- Housekeeping `_archive/cycle-48-scratch-clone-0`
- Housekeeping `_infra/adopt-cycle48-tests-clone-0`
- Egress probe `M-INGEST-1/egress-probe-cycle48-clone-0`

**Branch B** (`_manager/M-INGEST-1-corpus-expansion-plan-c48-queued-clone-1`): 4 rows
- Bookkeeping row honestly declaring **no substantive artifacts produced**
  (on-disk check confirms `data/corpus_expansion_plan/` predates c48; no
  c48-authored deliverables). c50+ researcher must reverify per auditor
  handoff.
- 2 housekeeping + 1 egress probe.

**Branch C** (`_infra/pre-existing-test-drift-triage-clone-2`): 10 rows
- 6 sub-leaves + parent rollup carrying verdict `DRIFT_TRIAGE_COMPLETE`
  (on-disk `data/pre_existing_test_drift/verdict.json` SHA pinned).
- 87/87 pre-existing failures classified: 86 environmental-drift, 1
  c47-orthogonal, 0 CRITICAL. c47 audit Issue #1 closed.
- 2 housekeeping + 1 egress probe.

**Rollup**: `_run/post-merge-integration-cycle-48-reconciliation`
(emit-cycle 48 per precedent).

### Priority 2 — M-RECREATE-2 pre-registration (16 events, `cycle: 49`)

Fires the operator override. Peer sub-milestone under G1 per c29
state-machine lemma (NOT a child of terminal-validated `M-RECREATE-1/*`).

- **Rubric doc** `docs/m_recreate_2_accurate_small_set_rubric.md`
  landed BEFORE any file under `scripts/recreate_v2/` (mtime-hard;
  git-log advisory per c46 path (ii)). SHA-256
  `958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d`
  pinned in `data/recreate_v2/rubric_hash.txt`.
- **Focus set** (`data/recreate_v2/focus_set.json`) — 5 songs by SHA-256
  tiebreak over `(title|video_id|playlist_id)` UTF-8:

  | Song                        | Band | audio_sha16          |
  |-----------------------------|------|----------------------|
  | Chicken Grease (mandatory)  | 6    | 31a164f845f8e27e     |
  | Disco A                     | 5    | cdd2717e52820ff6     |
  | Dojo Cuts Rome              | 5    | 51e433ade2a845e1     |
  | Mura Masa "What If I Go"    | 5    | 252eb21ce7df7328     |
  | Peach Dream                 | 6    | 88d247468cb6d49f     |

  Excluded by rank: **Lost** (dc3ccd161699f542, band 6).

- **RC0 baseline** captured for all 5 focus songs. htdemucs stems reused
  READ-ONLY from `data/recreate_v0_full_corpus/per_song/<band>/<sha16>/per_stage/04_htdemucs/`
  (c37-anchor product; re-run not required this cycle). Per-song
  measurements: per-stem SHA/RMS/centroid/LUFS; RC1 vocals voiced-time
  via pyin; RC2 drum onset count via `librosa.onset.onset_detect`; RC3
  bass pyin voiced-segments + <250 Hz low-band energy; RC5 tempo via
  `librosa.beat.beat_track`; RC6 spectral-centroid time series (VGGish
  pinned as **DEFERRED honest-None** — c11 CLAP anti-pattern locked,
  c50+ RC6 owner wires in via `scripts.texture.panel`).

  **Byte-determinism × 2** verified across 45 files (fresh
  `tempfile.mkdtemp()` under BLAS + `PYTHONHASHSEED=0` +
  `SOURCE_DATE_EPOCH=1756463424` + `TZ=UTC` + `LC_ALL=C.UTF-8` +
  `torch.manual_seed(0)`). Result:
  `data/recreate_v2/baseline_byte_determinism.json.byte_determinism_pass = true`.

  Chicken Grease negative-control anchor: **109 drum onsets in 30 s**
  baseline vs 5 in current merged.midi — the operator-audit failure.

- **RC1–RC5 + RC6 stub scripts** landed under `scripts/recreate_v2/`
  (7 files including `__init__.py`). Each stub imports the RC0
  baseline, declares `RC_ID` + `ACCEPTANCE_CRITERIA` +
  `BASELINE_ANCHOR_PATH` + `RUBRIC_HASH_PATH`, and raises
  `NotImplementedError("c50+ branch")` on the transcribe/render/gate
  function. Interpreter guard `/usr/bin/python3` present in every file.
  AST-grep clean: no PRNG, no `sidecar_nonfactor`, no forbidden
  state-extraction call sites.

- **Ledger events**: rubric-committed / focus-set-selected /
  rc0-baseline-captured / rc-stubs-registered + parent
  `M-RECREATE-2/accurate-small-set` (`status: in-progress`) + 6 RC
  sub-milestones each `status: in-progress` medium.

### Priority 3 — Egress cadence policy formalized

`docs/egress_retry_cadence_policy.md` landed. Codifies path A (fanout
per-branch probe) + path B (linear single probe per cycle); ledger row
`_plan/egress-retry-cadence-policy-formalized`. Retires ad-hoc "honored
via bookkeeping" justifications used at c47 clones 1+2.

### Priority 4 — c49 egress probe

`M-INGEST-1/egress-probe-cycle49` landed (path B — linear single row).
Failure mode HTTP 429 + tv_embedded (unchanged c45–c48). Not the
two-consecutive-`media_ok=true` unblock signal.

### Priority 5 — Housekeeping + cycle close

`_run/cycle_49_closed` + `_archive/cycle-49-scratch` +
`_infra/adopt-cycle49-tests`. c49 emitters archived to `tools/stale/`
via `shutil.copy2` + `os.utime` (c38 mv+touch pattern).

## Ledger state

- Pre-c49: 793 rows, 0-ERROR, 2539 WARN.
- Post-c49: **835 rows, 0-ERROR, WARN unchanged**.
- c48 events: 0 → **26** (Priority 1 success gate PASS).
- c49 events: 0 → **16**.
- Baseline replay contract preserved: 793 pre-c49 rows byte-identical.

## Tests

- `tests/test_c48_shadow_ledger_reconciliation.py` **10/10 PASS**
- `tests/test_m_recreate_2_pre_registration.py` **12/12 PASS**
- Combined: **22/22**. Brief target ≥ 12/15.

## Anti-pattern lockouts (reasserted)

All five (c11 CLAP HF SSL, c22 chassis-audit, c23 head-reg, c25
feature-rep, c35 palette-v2 VST3) locked. M-RECREATE-2 RC approach does
not intersect them. Specifically: RC6's VGGish rung is pinned as
**DEFERRED honest-None**, not a CLAP re-attempt; c50+ RC6 owner wires
in VGGish via the M-TEX-1/panel embedding surface.

## §10 handoff seeds (for the c50 researcher + auditor)

1. **c50 fanout candidate**: 3-branch on RC1 / RC2 / RC3, each with the
   pre-registered per-fix acceptance test against its RC0 baseline
   reference. RC4 folds into each of RC1–RC3's `merged.midi` emission.
   RC5 folds into a c51 linear cycle. RC6 folds into c52+ after RC1–RC3
   land.
2. **c50 researcher must verify c48 Branch B on-disk artifacts** before
   c50 references it (auditor request carried into c49 reconciliation).
3. **c48 env-var flip cycles** (`MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`,
   `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH` → ON) deferred to **c51+**
   post-M-RECREATE-2-land.
4. **New lemma proposal** `_infra/auditor-reads-ledger-not-brief-summaries`
   — auditor should spot-check `"cycle":<N>` grep count against the
   brief's rollup before trusting it. This c49 brief flagged the c48
   drift by doing exactly that. Alongside c46's rubric-doc-off-disk
   lemma.
5. **RC0 baseline sanity-anchor for the operator claim**: Chicken
   Grease baseline drum onsets = 109 in 30 s (from onset-detected on
   htdemucs drums stem), vs 5 in current recreate_v0 merged.midi. The
   operator's "hardly any drums" observation is quantified.
6. **Focus set generalizes across bands**: 2 band-6, 3 band-5 songs. If
   RC-arc fixes generalize to the band-4 population downstream, expect
   c53+ candidate to add a band-4 song to the focus set.

## Discipline compliance

- Rubric-first: rubric doc mtime `1788028158` < every
  `scripts/recreate_v2/*.py` mtime (earliest = `1788028493`, 5+ min
  after).
- Byte-determinism × 2: 45/45 baseline files equal across two fresh
  temp-dir runs.
- SHA-256 tiebreak; NO PRNG (AST-grep clean).
- `/usr/bin/python3` interpreter guard on every new stub.
- READ-ONLY anchors preserved: 37 SHAs snapshotted incl. 20 htdemucs
  stems + c48 verdicts + rules ledgers + ear verdicts + operator audit
  doc. All byte-identical pre==post.
- No imports of `scripts.tex.render_effects_layered`,
  `sidecar_nonfactor`, `scripts.rules.sampling.i4_stratified`,
  c26–c30 collision-model utilities, any `M-EAR-1/*` or `M-GEN-1/*`
  script under `scripts/recreate_v2/` (grep-verified).
- c33 harness auto-suffix default OFF for c49; both c48 env-var flags
  remain default OFF (c51+ candidate to flip).
- No file deletion; scratch → `tools/stale/` via `shutil.copy2` +
  `os.utime` + `os.unlink` (c38 pattern).
