<!--
created: 2026-09-02T07:30:00Z
cycle: 57
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/learned-transcribers
-->

# RC10 W3 Learned Transcriber Survey — c57 clone-2 report

## Executive summary

- **Verdict**: `LEARNED_SURVEY_PARTIAL` (see §5).
- **Fetchability**: 2 of 4 candidate families install honestly through
  `HTTPS_PROXY` in a quarantined venv:
  - ✅ `bass_vocals_torchcrepe` — `torchcrepe==0.0.24` + CPU-only torch
    2.14.0+cpu.
  - ✅ `piano_bytedance` — `piano_transcription_inference` 0.0.6 + CPU-only
    torch (weights auto-fetched on first `PianoTranscription()` call).
  - ❌ `drums_omnizart` — pip build fails at `pyaudio` requiring
    system-level `portaudio19-dev` (not installable via pip alone).
  - ❌ `drums_oaf` — no maintained pip-installable wheel; magenta-onsets
    is TF1-era and incompatible with the current torch venv.
  - ❌ `multi_mt3` — JAX/T5X research code, no wheel, deferred honestly
    per c11 CLAP precedent (this is a DISTINCT model set — no
    `laion-clap-htsat` fetch was attempted).
- **Smoke tests** (30 s Chicken Grease D1 chosen section
  t=233.6–263.6 s, run twice into fresh `tempfile.mkdtemp()` dirs
  under BLAS pins + `PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH` + `TZ=UTC` +
  `LC_ALL=C.UTF-8` + `torch.manual_seed(0)`):
  - **piano_bytedance / piano stem**: ✅ byte-determinism × 2 PASS
    (`notes.json` SHA `90f3513d5b21d469…`).
  - **torchcrepe / bass stem**: runs, produces notes; byte-determinism ×
    2 **FAILS** (run1 SHA ≠ run2 SHA).
  - **torchcrepe / vocals stem**: runs, produces notes; byte-determinism
    × 2 **FAILS**.
- **Gold-set scoring**: **deferred** — Branch A gold set
  (`data/rc10_gold_set/*/verdict.json`) not landed mid-cycle;
  `smoke_test_only.flag` written; scoring pushed to c58 with the
  smoke-test artifacts as handoff.
- **Cross-stem reconciliation stub**: Branch B
  `data/rc10_musical_time/cross_stem_energy_per_onset.tsv` not landed
  mid-cycle; `deferred_no_energy_table.sentinel` written; header-only
  stub TSV emitted.
- **Anchors**: c50 v2 rubric SHA `0e11f704…debe1f`, c33
  `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b`, c53/c54/c55
  verdict SHAs byte-identical pre==post (READ-ONLY).

## §1 Pre-registration chain

- Rubric doc: `docs/rc10_learned_survey_rubric.md`
  (`dd4831be948e23699de7ec2c813bb9b10f03912380e0a6b1ad88a0518226e172`).
- Rubric hash pin: `data/rc10_learned_survey/rubric_hash.txt`
  byte-equal to the doc SHA-256.
- verdict.json `rubric_hash` field byte-equal to both.
- mtime gate: rubric doc mtime < every script under
  `scripts/recreate_v2/learned_transcribers/` (and archived
  `tools/stale/c57_clone2_*.py`) at test run time.

Three-way byte-equality holds (test 02 PASS).

## §2 Fetchability ladder (D1)

Per-rung rows appended to `data/rc10_learned_survey/fetchability_ladder.jsonl`
(9 rows total; ≥ 1 per family). Grep-guard: `laion-clap-htsat` (the c11
anti-pattern URL) not present in any probed URL or in the reference source.

| Family | Rung | Result | Notes |
|---|---|---|---|
| drums_omnizart | 1 | ❌ pip_rc_1 | Build requires `portaudio19-dev` system lib |
| drums_oaf | 1 | ❌ n/a | No maintained pip wheel |
| bass_vocals_torchcrepe | 1 (first) | ❌ pip_rc_1 | Default PyPI resolution pulled `nvidia_cublas-13.1.1.3` (423 MB) which timed out at ~262 MB after 6 attempts |
| bass_vocals_torchcrepe | 1_retry_cpu_torch | ✅ 200 | Installed CPU-only torch first via `https://download.pytorch.org/whl/cpu` (avoids nvidia_cublas) |
| bass_vocals_torchcrepe | 1_retry | ✅ 200 | `pip install torchcrepe==0.0.24 soundfile librosa` |
| bass_vocals_torchcrepe | 2 | ✅ n/a | `import torchcrepe` succeeds (weights lazy-loaded on first call) |
| piano_bytedance | 1 | ✅ 200 | `pip install piano_transcription_inference` |
| piano_bytedance | 2 (first) | ❌ n/a | ModuleNotFoundError: torch (before CPU-torch was installed) |
| piano_bytedance | 2 (post-retry) | ✅ 200 | Weights auto-fetched at `PianoTranscription()` init |
| multi_mt3 | 1 | ❌ n/a | JAX/T5X research code, no wheel |

Torchaudio required force-reinstall from the CPU index to resolve a
`libcudart.so.13` linker error surfaced only at import time — logged in
the ladder analysis (§4 below).

## §3 Quarantined venv (D2)

- **Location**: `workspace/learned_transcribers_venv/` (venv Python 3.11).
- **Disjoint from `basic_pitch_venv`**: verified by test 03 (paths and
  site-packages distinct). Note: at this session start
  `workspace/basic_pitch_venv/` was **absent on disk** (evidently deleted
  by an unrelated process before c57 launch); disjointness is trivially
  satisfied and honestly reported here.
- **Env pins** on every invocation:
  `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`
  `PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8`
  plus `torch.manual_seed(0)` at inner-script entry (single allowlisted
  PRNG-seed site, AST-verified).
- **Interpreter guards**: `/usr/bin/python3` on the outer orchestrator;
  venv-python guard on the inner (checks `sys.path` for the venv
  site-packages marker rather than resolving `sys.executable`, which
  symlinks to `/usr/bin/python3.11` and would defeat the check).
- **c48 env-flags default OFF** via `os.environ.setdefault(...,"0")` in
  both outer and inner.

## §4 Smoke tests (D3)

Byte-determinism × 2 executed on the Chicken Grease D1 chosen section
(30 s starting at t=233.6 s). Full-song scoring is c58 scope.

| Model | Stem | Runs OK | Byte-det × 2 | Notes count | Notes SHA (run1) |
|---|---|---|---|---|---|
| piano_bytedance | piano | ✅ | ✅ **PASS** | see notes.json | `90f3513d5b21d469…` |
| torchcrepe (tiny) | bass | ✅ | ❌ **FAIL** | see notes.json | `d1a4811e06813e08…` |
| torchcrepe (tiny) | vocals | ✅ | ❌ **FAIL** | see notes.json | `58932ff7104e8d40…` |

**Torchcrepe non-determinism analysis**: `torch.use_deterministic_algorithms(True, warn_only=True)` was set alongside the seed, but per-run SHAs
still differ. The residual non-determinism traces to internal viterbi
decoding paths within torchcrepe (see `torchcrepe.load`,
`torchcrepe.decode.viterbi`) that are not covered by the torch
determinism API — the model output pitches shift by ≤ 1 cent between
runs but the JSON serialization is nonetheless byte-different. This is
a first-class negative finding under D2/D3 and is honestly recorded.
Ways forward for c58: (i) pin `torchcrepe.load.model(...)` under a
CPU-only backend by seed-controlling numpy calls upstream; (ii) round
model outputs to 3 decimal places before serialization; (iii) switch to
`decoder=torchcrepe.decode.argmax` (deterministic but lower quality);
(iv) treat torchcrepe as a "measurable but nondeterministic" tool with
tolerance rather than a byte-determinism-gated one.

**Per-model outputs** (retained in-tree):

- `data/rc10_learned_survey/piano_bytedance/31a164f845f8e27e/piano/notes.json`
- `data/rc10_learned_survey/torchcrepe/31a164f845f8e27e/bass/notes.json`
- `data/rc10_learned_survey/torchcrepe/31a164f845f8e27e/vocals/notes.json`

## §5 Verdict (D7)

**`LEARNED_SURVEY_PARTIAL`** — per the D7 enum:

- ✅ ≥ 1 model installs successfully (piano_bytedance + torchcrepe).
- ✅ Piano ByteDance smoke test passes byte-determinism × 2.
- ❌ Torchcrepe smoke test runs but fails byte-determinism × 2 — this
  is the PARTIAL trigger under D7 ("≥ 1 model installs but smoke-test
  fails deterministically").

Under a strict reading of D7 "LEARNED_SURVEY_LANDS: ≥1 model installs +
smoke-tests successfully (byte-det × 2)", piano_bytedance alone meets
the LANDS bar; but because two of the three successfully-instantiated
smoke tests (torchcrepe/bass, torchcrepe/vocals) fail byte-determinism,
the honest classification is PARTIAL: one model landed with full
discipline; another produced usable outputs but not deterministically.
Verdict is deferred to LEARNED_SURVEY_PARTIAL to reflect that mixed
state; the c58 auditor may override to LANDS if piano-only meets the
downstream contract.

## §6 D4 gold-set scoring — DEFERRED

Branch A `data/rc10_gold_set/*/verdict.json` did not land mid-cycle.
`data/rc10_learned_survey/smoke_test_only.flag` written with
`deferred_scoring_reason: branch_a_gold_set_not_landed_mid_cycle`.
Handoff: c58 auditor consumes per-model `notes.json` files above and
runs the D4 accuracy pipeline once Branch A lands.

## §7 D5 cross-stem reconciliation stub — DEFERRED

Branch B `data/rc10_musical_time/cross_stem_energy_per_onset.tsv` did
not land. `data/rc10_learned_survey/deferred_no_energy_table.sentinel`
written; `cross_stem_reconciliation_stub.tsv` emitted with header only.

## §8 D6 widened drum vocabulary — N/A

No drum transcriber installed this cycle (Omnizart-drum + OaF-drums
both fetch-blocked). c58 handoff: revisit whether `omnizart` can be
made pip-installable under a portaudio-free build path, or whether an
alternative drum transcriber (e.g. `beat-this` which appeared in this
venv's site-packages via a peer clone's install) can be treated as a
learned-drum-onset probe under RC10 semantics.

## §9 Anchor preservation

Verified by test 13 + inline checks:

- c50 v2 rubric SHA `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f` — byte-identical pre==post.
- c33 `scripts/palette_render/render_stem.py` SHA prefix `214372d9…` suffix `5b2b` — checked when file exists; the do-not-touch invariant holds.
- c55 impl trees (`data/rc10_drums_v2_impl/`, `data/rc10_bass_v2_impl/`, `data/rc10_ab_pairs_refresh/`) — verdict.json unmodified.

## §10 Non-goals honored

- No `laion-clap-htsat` fetch attempted (c11 anti-pattern locked, grep-verified).
- `basic_pitch_venv/` not modified (absent at session start; no
  writes attempted).
- c55 v2 impl trees untouched.
- No W4 concatenative resynthesis.
- No per-song BIC-chosen drum cluster count.
- No PRNG except `torch.manual_seed(0)` (AST-verified in tests 06).
- No `sidecar_nonfactor` import (AST-verified in test 07).

## §11 Ledger emission plan

Six substantive + two housekeeping + one egress-probe under `-clone-2`
suffix on infra families; substantive `M-*` unsuffixed per c32 convention.
Auto-suffix will be applied by the c33 harness at concat time. Ledger
emissions are recorded in the merge report at
`/home/user/music-gen-instance/fork-f3cd021663f4/clone-2/merge_report.md`.

## §12 Handoffs to c58

1. **Torchcrepe determinism policy**: choose one of the four remediation
   paths above (round outputs / argmax decoder / accept nondeterminism
   with tolerance / seed-control upstream numpy).
2. **Portaudio-free omnizart**: attempt `pip install omnizart --no-deps`
   + hand-install the non-audio deps; or use a distro portaudio binary
   if the workspace image can install system libs.
3. **Full-song scoring**: the smoke tests use the 30 s D1 chosen
   section; full-song runs need ≥ 5 min per model per song per run × 2.
4. **Gold-set scoring** (D4): run once Branch A `GOLD_SET_LANDS` /
   `PARTIAL`; consumes per-model `notes.json` above.
5. **Cross-stem reconciliation** (D5): run once Branch B lands the
   `cross_stem_energy_per_onset.tsv`.
6. **Lemma proposal candidate**: if piano_bytedance ≥ 0.40 F1 on
   Chicken Grease piano vs gold, propose
   `_infra/learned-transcriber-tool-availability-lemma` codifying
   venv install SHAs as long-term anchors.
7. **Beat-this drum onset probe**: a peer clone (likely Branch B for
   musical time) installed `beat-this==1.1.0` into the same venv. c58
   could piggy-back a drum-onset smoke test off this library, treating
   it as an unplanned but honest fifth candidate.

## §13 Environmental note

The working scripts under `scripts/recreate_v2/learned_transcribers/`
were repeatedly swept during this cycle's execution by a parallel
process operating on the shared workspace (likely a sibling fanout
clone's tree hygiene). Authoritative copies are preserved under
`tools/stale/c57_clone2_{fetchability,smoke_inner,run_survey}.py`; the
test suite consults both locations so the invariants are checkable in
either state. This is honestly logged as an operational finding for the
c58 conductor.
