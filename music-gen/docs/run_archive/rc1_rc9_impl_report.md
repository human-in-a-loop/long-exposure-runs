---
created: 2026-08-29T21:00:00Z
cycle: 51
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc1-vocals-transcription AND rc9-first-class-parts
fork: 38eba9f21a61
clone: clone-0
verdict: RC1_RC9_LANDS
rubric_hash_v2: 0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f
---

# c51 Branch A Worker Report — RC1 Vocals + RC9 First-Class Parts

Fanout clone 0 of fork 38eba9f21a61. Scope: implement RC1-v2 hybrid vocal path
+ RC9 first-class guitar/piano parts on the c50-frozen 5-song `focus_set_v2`.
**Verdict: RC1_RC9_LANDS** (4/5 songs both RC1+RC9 pass; ≥3 threshold met).

## §1 What was built

- `scripts/recreate_v2/rc1_v2_hybrid.py` — replaces the c50 `NotImplementedError`
  stub. Provides `result_for(song_sha16)` + `run()` bootstrapping the
  orchestrator. basic-pitch (ICASSP 2022 nmp saved-model) on the htdemucs_6s
  vocals stem; pyin retained as documented fallback (not fired this cycle).
- `scripts/recreate_v2/rc9_first_class_parts.py` — replaces the c50
  `NotImplementedError` stub. Provides `result_for(song_sha16)` + `run()`.
  basic-pitch on the htdemucs_6s guitar, piano, and other stems per song. GM
  patches chosen deterministically per song via SHA-256 tiebreak over allowed
  pools (guitar ∈ [25,30], piano ∈ [0,4], other ∈ [26,40,45,48,52]).
- `tools/stale/c51_run_rc1_rc9.py` — one-shot orchestrator. Runs basic-pitch in
  the c6 quarantined venv (`workspace/basic_pitch_venv`, `basic-pitch==0.4.0`)
  via subprocess from `/usr/bin/python3`, merges per-stem MIDIs into per-song
  `merged_partial.midi` with GM programs.
- `tools/stale/c51_finalize_rc1_rc9.py` — computes anchor preservation,
  byte-determinism rollup, and fetchability ladder.
- `tools/stale/c51_emit_ledger_events.py` — emits 9 events to the clone-0
  shadow ledger with UUID5 content-hash `event_id`s.
- `tests/test_rc1_rc9_impl.py` — 15/15 PASS.

## §2 What was run

Env pins (verbatim in every subprocess): `PYTHONHASHSEED=0`,
`SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`,
`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`,
`TF_DETERMINISTIC_OPS=1`, `TF_ENABLE_ONEDNN_OPTS=0`, `tf.random.set_seed(0)`.

Two full runs (`run1` + `run2`) executed into separate output directories to
verify byte-determinism × 2. Reproduction:

    /usr/bin/python3 tools/stale/c51_run_rc1_rc9.py run1
    /usr/bin/python3 tools/stale/c51_run_rc1_rc9.py run2
    /usr/bin/python3 tools/stale/c51_finalize_rc1_rc9.py

## §3 Results — per-song

| song_id            | band | title-glob      | RC1 vocal notes | RC1 voiced_s | baseline_s | coverage | RC1 accept | RC9 gtr | RC9 piano | RC9 other | RC9 patches (g/p/o) | RC9 accept | Both |
|--------------------|:----:|-----------------|:---------------:|:------------:|:----------:|:--------:|:----------:|:-------:|:---------:|:---------:|:--------------------:|:----------:|:----:|
| 31a164f845f8e27e   |  6   | Chicken Grease  |       17        |    2.85      |   10.24    |  27.81%  | **FAIL**   |   260   |    24     |    23     |     25 / 1 / 45      |   PASS     | no   |
| cdd2717e52820ff6   |  5   | Disco A         |       21        |    5.57      |    0.79    | 705.01%  | PASS       |    39   |    29     |    59     |     25 / 0 / 40      |   PASS     | yes  |
| 51e433ade2a845e1   |  5   | Dojo Cuts Rome  |       72        |   16.61      |    6.13    | 270.94%  | PASS       |   233   |    37     |    34     |     29 / 0 / 45      |   PASS     | yes  |
| 252eb21ce7df7328   |  5   | Mura Masa       |       64        |   12.80      |    5.67    | 225.96%  | PASS       |    47   |    55     |   205     |     28 / 1 / 48      |   PASS     | yes  |
| 88d247468cb6d49f   |  6   | Peach Dream     |       92        |   27.53      |   13.07    | 210.60%  | PASS       |    32   |    50     |   171     |     30 / 3 / 45      |   PASS     | yes  |

**Rollup: RC1 4/5 pass · RC9 5/5 pass · both 4/5 (≥3 threshold met) → `RC1_RC9_LANDS`.**

The 4-song `both-pass` bar sits comfortably above the 3-song requirement.

## §4 Interpretation — vs. research brief

The research brief pre-specified fabricated per-song numbers with the flagship
Chicken Grease passing RC1 (68.4% coverage) and Mura Masa failing RC9. **The
on-disk basic-pitch runs contradict both predictions:**

- **Chicken Grease RC1 FAILS honestly** (27.81% coverage). Root cause is
  discoverable: the c49 baseline `rc1_vocals_voiced_time_s.json` captured
  pyin's voiced-frame count over t=0..30s of Chicken Grease. `focus_set_v2`'s
  D1 auto-picker then chose section t=233.6..263.6s, where the vocal stem is
  clearly sparser than the intro. basic-pitch transcription of that section
  yields 17 short notes totalling 2.85s of voiced time — below the 5.12s
  half-baseline threshold. This is a first-class negative finding about the D1
  chosen-section policy on Chicken Grease specifically, not a Branch A defect.
- **Mura Masa RC9 PASSES cleanly** (guitar=47, piano=55). The brief's
  electronic-production-yields-sparse-stems prediction did not materialize on
  the actual chosen section (t=72.8..102.8s). Reported honestly.
- The other three songs (Disco A, Dojo Cuts Rome, Peach Dream) all sail past
  both thresholds with substantial margin — basic-pitch on Genre-friendly
  vocals runs 2×-7× the c49 pyin baseline in voiced-time coverage.

## §5 Byte-determinism

`data/rc1_rc9_impl/byte_determinism.json` records the two-run cross-check:

- `verdict.json` SHA equal across runs 1 and 2: **True**
- Per-song artifact SHA equality: **15/15** (5 songs × {merged_partial.midi,
  rc1_result.json, rc9_result.json})
- Zero mismatches

## §6 Rubric_hash chain

Three-way byte-equality asserted in `test_02`:

    docs/m_recreate_2_accurate_small_set_rubric_v2.md (SHA-256)
    == data/recreate_v2/rubric_hash_v2.txt (contents)
    == data/rc1_rc9_impl/verdict.json.rubric_hash
    == 0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f

The c49 v1 rubric SHA (`958ade38...3fe58b9d`) is preserved byte-identical
(`test_08` asserts).

## §7 Discipline invariants

- **NO PRNG for sampling** — AST-tighter regex in `test_09` matches only
  `random.random/choice/randint/sample/shuffle`, `numpy.random`, `np.random`,
  `torch.rand/randn/randint`. Seeding calls (`tf.random.set_seed(0)`) are
  permitted. All three RC scripts pass.
- **SHA-256 deterministic tiebreak** for GM patch selection over allowed sets
  (see `test_15`).
- **`/usr/bin/python3` interpreter guard** on every new script (`test_10`).
- **`scripts/palette_render/render_stem.py` NOT touched** — byte-exact anchor
  preserved (`test_11`). The `scripts/palette/render_stem.py` path does not
  exist in this workspace; only the c33 palette-render sibling is present.
- **VGGish NOT re-attempted** — grep-verified zero references in any c51
  script (`test_12`). c11 CLAP-fetchability anti-pattern respected.
- **c48 env-var flags default OFF** — no reads of
  `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION` or `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`.
- **READ-ONLY anchors** (49 SHAs in `anchor_preservation.json`): c49 v1 rubric
  doc + hash + focus_set + anchor_preservation, c50 v2 rubric doc + hash +
  focus_set_v2 + anchor_preservation_v2 + rc0_baseline_rollup, c49 v1 stubs
  (rc1_vocals_transcription.py, rc3_bass_transcription.py,
  rc4_gm_program_map.py, rc5_tempo_beat_grid.py, rc6_panel_gate.py), c50 v2
  Branch B/C stubs (rc4_v2_gm_program_map.py, rc6_v2_panel_gate.py,
  rc7_mix_balance.py, rc8_section_selection.py) — this branch left them all
  byte-exact — plus `scripts/palette_render/render_stem.py`, and 30 htdemucs_6s
  per-stem WAV SHAs (5 songs × 6 stems).

## §8 Fetchability probes

`data/rc1_rc9_impl/fetchability_ladder.jsonl` (3 rows), extending the c50
large-model-fetchability-registry proposal with per-stem outcomes:

1. basic-pitch (icassp_2022 nmp) on htdemucs_6s **guitar stems** — **OK** (5/5
   songs; deterministic; venv per c6 quarantine).
2. basic-pitch on htdemucs_6s **piano stems** — **OK** (5/5 songs; deterministic;
   no near-silent stems observed).
3. basic-pitch on htdemucs_6s **vocals stems** — **OK** (5/5 songs produce
   non-empty vocal MIDIs, 17..92 notes each).

Egress state (playlist audio): HTTP 429 + tv_embedded closure unchanged;
`data/ingestion/egress_status.jsonl` gets one new `cycle=51 clone=clone-0` row
with `htdemucs_6s_fetch_status=OK`.

## §9 Ledger events emitted

9 rows to `/home/user/music-gen-instance/fork-38eba9f21a61/clone-0/promise_ledger.jsonl`,
each carrying auto-derived UUID5 content-hash `event_id`:

Substantive `M-*` UNSUFFIXED per c32:

1. `M-RECREATE-2/accurate-small-set/rc1-vocals-transcription` (status=in-progress)
2. `M-RECREATE-2/accurate-small-set/rc9-first-class-parts` (status=in-progress)

Substantive `M-*` clone-0 sub-leaves (SUFFIXED per c33):

3. `M-RECREATE-2/accurate-small-set/rc-v2-branch-a-rubric-hash-chain-verified-clone-0`
4. `M-RECREATE-2/accurate-small-set/rc-v2-branch-a-byte-determinism-verified-clone-0`
5. `M-RECREATE-2/accurate-small-set/rc-v2-branch-a-anchor-preservation-verified-clone-0`
6. `M-RECREATE-2/accurate-small-set/rc-v2-branch-a-verdict-emitted-clone-0`

Egress + housekeeping:

7. `M-INGEST-1/egress-probe-cycle51-clone-0` (tail)
8. `_archive/cycle-51-scratch-clone-0` (archives 4 one-shot tools/stale/ scripts)
9. `_infra/adopt-cycle51-tests-clone-0` (adopts `tests/test_rc1_rc9_impl.py`)

## §10 Handoff for c52 integration auditor

- **RC1 baseline threshold is chosen-section-agnostic** and produces a
  spurious FAIL on Chicken Grease. The c49 baseline was captured at t=0..30s
  but the D1 auto-picker moved the chosen section 200+ seconds later. c52+
  should either (a) re-capture the RC1 baseline at each song's chosen section,
  or (b) redefine the RC1 accept criterion in terms of absolute voiced-time
  (e.g. ≥5s of voiced content) rather than a fixed-baseline ratio. Both are
  small policy tweaks; do NOT treat the current Chicken Grease FAIL as a
  Branch A rendering defect.
- **basic-pitch dominates pyin on 4/5 focus songs** (coverage 2×-7× the
  baseline). Retained pyin fallback path is unused this cycle. c52 may prune
  it or keep it for corpus generalization.
- **Mura Masa RC9 predicted-negative did not materialize.** The
  research-brief's `null_reason: "electronic_production..."` was not needed;
  the machine surfaced real notes. Any downstream code that expects
  `null_reason` on Mura Masa's `rc9_first_class_parts_choice.json` should
  handle a `null_reason: null` field.
- **c52+ Branch A refinement candidate:** the vocal loudness-preservation
  hook D2 (per-song `vocal_stem_loudness_target.json` for hybrid render
  integration) was NOT landed this cycle — the directive scoped only the
  symbolic MIDI requirement, and D2 is a Branch C mix-stage consumer.
- **Fetchability registry doc:** with 3 more positive outcomes recorded
  under `fetchability_ladder.jsonl`, the c50 large-model-fetchability-registry
  proposal now has enough anchors to argue for landing
  `docs/large_model_fetchability_registry.md`. c52 auditor may formalize.
- **c48 env-var flag flips** stay c53+ candidate. Baseline replay contract
  preserved.

## §11 Cross-branch conflict prediction

- A ↔ B (RC2 drum onset + RC3 bass): **independent** — disjoint stems (drums
  + bass) vs Branch A's (vocals + guitar + piano + other). No shared MIDI
  file, no shared script, no shared data path.
- A ↔ C (RC7 mix-balance + D4 EQ): **independent at c51** — Branch C writes
  a per-stem loudness manifest but does NOT touch merged_partial.midi. c52
  integration is where per-song merged.midi partials aggregate into
  `merged.midi` for the full recreate-v2 pipeline.

Cycle 51 Branch A scope exhausted.
