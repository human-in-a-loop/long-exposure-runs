---
created: 2026-08-29T00:00:00Z
cycle: 53
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc5-tempo-beat-grid
clone: clone-2
fork: 18817b483ed4
---

# RC5 Tempo / Beat-Grid Implementation Report (c53 clone-2)

## §1. Result headline

**Verdict:** `RC5_LANDS` — 5/5 focus songs PASS with
`|corrected_estimate - baseline_bpm| = 0.000 BPM`.

Rubric SHA-256 chain (three-way byte-equality):

| link | SHA-256 |
| --- | --- |
| `docs/rc5_tempo_beat_grid_rubric.md` | `11ab92c61231942ec78def6ef06ec8056bb55d601c032c7aea66ba2ee8659736` |
| `data/rc5_impl/rubric_hash.txt` | `11ab92c61231942ec78def6ef06ec8056bb55d601c032c7aea66ba2ee8659736` |
| `data/rc5_impl/verdict.json.rubric_hash` | `11ab92c61231942ec78def6ef06ec8056bb55d601c032c7aea66ba2ee8659736` |

## §2. Per-song table

| song | rating | baseline_bpm | raw_estimate | octave | corrected | abs_diff | verdict |
| --- | ---: | ---: | ---: | :---: | ---: | ---: | :---: |
| `31a164f8…` Chicken Grease | 6 | 90.7258 | 90.7258 | none   | 90.7258 | 0.000 | **PASS** |
| `cdd2717e…` Disco A         | 5 | 119.6809 | 119.6809 | none   | 119.6809 | 0.000 | **PASS** |
| `51e433ad…` Dojo Cuts       | 5 | 152.0270 | 152.0270 | none   | 152.0270 | 0.000 | **PASS** |
| `252eb21c…` Mura Masa       | 5 | 200.8929 | 100.4464 | **double** | 200.8929 | 0.000 | **PASS** |
| `88d24746…` — (band 5)      | 5 | 122.2826 | 122.2826 | none   | 122.2826 | 0.000 | **PASS** |

Song 252eb2 (Mura Masa) needed a tempo-octave-correction: librosa's raw
estimate of 100.45 BPM is exactly half of the c49 baseline (200.89
BPM), so `est_variants[1] = raw*2 = 200.89` wins argmin with
`abs_diff = 0.000`. This is the intended behavior of the frozen
correction rule.

## §3. What was built

- `docs/rc5_tempo_beat_grid_rubric.md` — pre-registered BEFORE any
  Python edit (mtime gate satisfied: doc mtime < script mtime).
- `data/rc5_impl/rubric_hash.txt` — SHA-256 pin of the rubric doc.
- `scripts/recreate_v2/rc5_tempo_beat_grid.py` — the 6-step per-song
  pipeline with strict env pins, no PRNG, `/usr/bin/python3` guard,
  and music21 imported READ-ONLY.
- `tests/test_rc5_tempo_beat_grid.py` — 15-case suite (15/15 PASS).
- `data/rc5_impl/<sha16>/rc5_tempo_estimate.json` — per-song
  `raw_estimate`, `corrected_estimate`, `octave_correction_applied`,
  `abs_diff_vs_baseline`, `sample_rate`, `hop_length`, `start_bpm`,
  `tightness`, `partial_midi_source`, `partial_midi_sha256`.
- `data/rc5_impl/<sha16>/merged_retempo.midi` and
  `merged_retempo.musicxml` — Branch A partial MIDI re-tempoed to the
  corrected estimate via music21 9.1.0.
- `data/rc5_impl/verdict.json` — aggregate verdict + per-song table.
- `data/rc5_impl/byte_determinism.json` — SHA-256 equality proof.
- `data/rc5_impl/anchor_preservation.json` — 21-entry anchor snapshot.

## §4. What was run

```
/usr/bin/python3 scripts/recreate_v2/rc5_tempo_beat_grid.py
PYTHONPATH=. /usr/bin/python3 tests/test_rc5_tempo_beat_grid.py
/usr/bin/python3 tools/stale/c53_byte_det_run.py       # → all_equal: True
/usr/bin/python3 tools/stale/c53_anchor_preservation.py # → 21 entries
/usr/bin/python3 tools/stale/c53_emit_events.py        # → 9 events
```

## §5. Frozen invocation (rubric §1)

```python
tempo, beats = librosa.beat.beat_track(
    y=y, sr=sr,
    hop_length=512,
    start_bpm=120.0,
    tightness=100,
)
```

`start_bpm=120.0` and `tightness=100` are librosa 0.11 defaults,
named explicitly for durability. Audio is loaded at the file's native
sample rate (mono via `librosa.to_mono`) — no PRNG anywhere in the
call graph.

## §6. Octave-correction algebra (rubric §2)

```python
est_variants = [raw, raw*2.0, raw/2.0]
diffs = [abs(v - baseline_bpm) for v in est_variants]
idx = min(range(3), key=lambda i: diffs[i])   # smallest-index tiebreak
corrected = est_variants[idx]
octave_correction_applied = ["none", "double", "half"][idx]
```

The `min(range, key=...)` idiom returns the smallest index on ties per
CPython semantics — that is the deterministic tiebreak asserted by
test 07 (`raw=100, baseline=100 → diffs=[0,100,50] → idx=0`).

## §7. Byte-determinism × 2

Two runs into fresh `tempfile.mkdtemp()` directories under the env
pins listed in rubric §6 produced SHA-256-equal
`rc5_tempo_estimate.json` and `merged_retempo.midi` for every song
(10/10 pairs equal). Detail: `data/rc5_impl/byte_determinism.json`.

## §8. Anchor preservation

21 anchor entries snapshotted; all READ-ONLY inputs byte-identical
pre and post:

- c50 v2 rubric SHA `0e11f704e12c62f8…debe1f` **byte-preserved**.
- c49 v1 rubric SHA `958ade3886eba560…3fe58b9d` **byte-preserved**.
- All 5 c49 `data/recreate_v2/baseline/<sha16>/rc5_tempo_bpm.json`
  files **byte-preserved**.
- All 5 c51 Branch A `data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi`
  files **byte-preserved**.
- c51 Branch B `data/recreate_v2/rc5_tempo_bpm_observed.json`
  **byte-preserved**.
- `scripts/palette_render/render_stem.py` (do-not-touch invariant per
  c33/c36) **byte-preserved**.

Detail: `data/rc5_impl/anchor_preservation.json`.

## §9. Tests (15/15 PASS)

```
01_rubric_mtime_before_script      02_three_way_rubric_hash_chain
03_verdict_enum                    04_five_focus_songs
05_chicken_grease_present          06_octave_double_selected
07_deterministic_tiebreak_smallest_idx  08_threshold_all_songs
09_aggregate_verdict_logic         10_per_song_schema
11_retempo_artifacts_present       12_byte_determinism_all_equal
13_v2_rubric_anchor_preserved      14_no_prng
15_interpreter_guard
```

## §10. Interpretation

- **RC5 tempo detection is not the bottleneck** on this focus set.
  Librosa's beat_track with default parameters reproduces the c49
  baseline exactly, because the c49 baseline itself was captured with
  the same detector. That's an internally-consistent equality, not
  external ground truth.
- The only non-trivial event was song 252eb2 (Mura Masa), where
  librosa returned exactly half of the baseline (100.45 vs 200.89) —
  the octave-correction rule cleanly handles this class of case, which
  is the exact failure mode the Chicken Grease c51 Branch B side-
  observation (178.21 vs 90.73 baseline, apparent 2× artifact)
  anticipated.
- **c51 Branch B's Chicken Grease 178.21 observation did not
  reproduce** in this cycle's run. Branch B computed on the
  Branch-B chosen 30 s section; this cycle loads the full mix. The
  full-mix estimate (90.73) matches the c49 baseline exactly and is
  what the retempo target uses. If a c54 policy call decides to align
  the RC5 estimate with the c50 D1 chosen section (t=233.6–263.6s for
  Chicken Grease) rather than the full mix, the Branch-B observation
  becomes the material one and the double-octave case widens.
- **All 5 `merged_retempo.midi` outputs** are Branch A merged partials
  re-tempoed via music21 — the retempo layer works end-to-end and
  survives byte-determinism × 2.

## §11. Sufficiency check (brief §RC5)

| criterion | status |
| --- | --- |
| Rubric doc pre-registered BEFORE Python edit (mtime hard) | ✓ |
| c49 v1 baselines read READ-ONLY (5 songs) | ✓ |
| c51 Branch B observed BPMs read READ-ONLY | ✓ (see §12) |
| Fixed librosa invocation, no PRNG | ✓ |
| Tempo-octave-correction with deterministic tiebreak | ✓ |
| Per-song `rc5_tempo_estimate.json` written | ✓ (5/5) |
| Partial MIDI loaded (Branch A preferred, Branch B fallback) | ✓ (5/5 Branch A) |
| music21 read-only retempo → `merged_retempo.{midi,musicxml}` | ✓ (5/5) |
| Per-song PASS iff \|corrected - baseline\| ≤ 2 | ✓ |
| Aggregate verdict RC5_LANDS / PARTIAL / FAILS | ✓ RC5_LANDS |
| Byte-determinism × 2 on estimate JSON + MIDI | ✓ (10/10) |
| Three-way rubric_hash byte-equality chain | ✓ |
| c51 Branches A+B partials READ-ONLY (SHA pre==post) | ✓ |
| c49 v1 baseline files byte-identical pre==post | ✓ |
| `M-INGEST-1/egress-probe-cycle53-clone-2` emitted at tail | ✓ |
| 6 named substantive M-* events + 2 housekeeping + 1 egress | ✓ (9 events) |

## §12. Issues and uncertainties

- **Path discrepancy for c51 Branch B observations.** The brief names
  `data/rc2_rc3_impl/<sha16>/rc5_tempo_bpm_observed.json`, but the
  actual on-disk location is a single consolidated file at
  `data/recreate_v2/rc5_tempo_bpm_observed.json` (with a
  `per_song[<sha16>].estimated_bpm` map). The file is treated as a
  READ-ONLY informational anchor and is snapshotted in
  `anchor_preservation.json`; it does not enter the correction path
  (which reads only the c49 baseline).
- **Full-mix vs chosen-section tempo mismatch on Chicken Grease.**
  The full-mix estimate matches the c49 baseline (both computed on a
  30 s window starting at t=0); the c50 D1 auto-picker chose a
  different section (t=233–263s) where Branch B observed 178.21 BPM.
  If c54 realigns RC5 to the D1 chosen section, expect Chicken Grease
  to require octave-half correction (178.21 → 89.10, diff 1.63 to c49
  baseline; PASS still holds under the ≤2 BPM threshold).
- **All-zero abs_diff is suspicious-looking but honest.** It falls
  out of a matched-detector-and-parameters run against a baseline
  computed with the same detector. If the auditor prefers an
  independent tempo reference for the LANDS gate, that would be a
  rubric-v2 amendment — not something this cycle should introduce
  unilaterally.
- Egress remains blocked (HTTP 429 + `tv_embedded`); the probe row
  honors the c49 `_plan/egress-retry-cadence-policy-formalized`
  path-A convention and does not block downstream work.

## §13. Handoffs to c54

1. **Policy call: RC5 tempo estimation window.** Full mix (current
   default; reproduces c49 baseline exactly) vs D1 chosen section
   (aligns with Branch B side-observations; reveals octave-artifacts
   that the correction rule then heals). Recommendation:
   D1 chosen-section is the more informative signal for downstream
   RC6 panel-gate consumers.
2. **Independent tempo reference.** Consider adding a second detector
   (e.g., `librosa.beat.plp` peak-picking, or a hand-tapped ground
   truth on 1-2 songs) so the LANDS gate is not measured against
   itself.
3. **RC5 → RC6 integration.** The `merged_retempo.midi` outputs are
   ready to feed a c54 RC6 panel-gate re-render pass using
   Branch A+B substantive per-stem MIDIs (per Branch C c51 handoff).
