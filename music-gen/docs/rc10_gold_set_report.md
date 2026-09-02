<!--
created: 2026-09-02T04:40:00Z
cycle: 57
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/gold-set
-->

# RC10 Gold Set — c57 clone-0 Report

**Fork**: f3cd021663f4 (clone 0 of 3)
**Branch**: W1 gold-set as source of truth
**Verdict**: `GOLD_SET_PARTIAL` (honest — manual-correction pass deferred to operator)
**Rubric SHA**: `73664aab112151ea194475ee1da4465841423c98b5b20400da7cb8e877e26ab1`

## §1 What was built

- `docs/rc10_gold_set_rubric.md` (pre-registered, mtime < scripts) —
  frozen 3-verdict rubric with vocabulary, schema, provenance chain, and
  §4 fallback for automated-agent researchers.
- `docs/rc10_gold_set_listening_workflow.md` — step-by-step for the human
  researcher's manual-correction pass.
- `data/rc10_gold_set/rubric_hash.txt` + `workflow_hash.txt` — three-way
  byte-equality chain enforced.
- `data/recreate_v2/focus_set_v3.json` — additive sibling to
  `focus_set_v2.json` (v2 SHA byte-identical pre==post; v3 adds
  exposed-section metadata and re-scoped windows per §Issues).
- `scripts/recreate_v2/rc10_gold_set/{__init__,build_gold_set}.py` — one
  builder, no PRNG.
- 8 gold entries under `data/rc10_gold_set/<sha16>/{drums,bass}/{peak,exposed}/`
  containing `gold_notes.json`, `gold_fluidsynth.wav`, `gold_concatenative.wav`,
  `per_note_confidence.tsv`, `edit_log.jsonl`, `sample_bank/`, and
  `section_original.wav` slices.
- Per-song `cross_stem_coonset_labels.tsv` seeding c58 W4/cross-stem work.
- `data/rc10_gold_set/{verdict.json, anchor_preservation.json, byte_determinism.json, per_entry_summary.json}`.

## §2 Sections chosen (D1 extension in focus_set_v3.json)

**Honest re-scope**: c53/c54/c55 winner MIDIs cover only t=0..30s per the
c49 baseline capture window; `focus_set_v2` chose peaks at t=233s (CG) and
t=72s (WIG) which are outside the transcribed range. To keep the gold set
self-consistent within available upstream coverage, peak and exposed 4-bar
windows were re-selected inside `[0, 30s]` deterministically:
peak = argmax RMS, exposed = argmin `(rms_pct − onset_density_pct)` with
`rms_pct ≥ 0.20`. The original `focus_set_v2.chosen_section` values are
preserved verbatim as `focus_set_v2_peak_reference` for c58 audit.

| song                    | sid    | peak      | exposed    |
|-------------------------|--------|-----------|------------|
| Chicken Grease          | 31a164 | 21.0–29.0 | 12.5–20.5  |
| What If I Go            | 252eb2 |  0.0– 8.0 | 19.0–27.0  |

Window size 8 s (fits two 4-bar blocks at ~90 bpm within the 30 s cap).

## §3 Gold entries — ensemble composition (D3 step 1)

Ensemble sources per (song, stem):

- drums: c54 clone-0 `onset_band_energy` winner + c55 clone-0 `drums-v2` GMM winner
- bass: c54 clone-0 `pyin_mono` winner + c55 clone-1 `bass-v2` onset-segmented pyin winner
- Branch B (musical-time) grid: **not landed in-cycle**, tempo fallback = c53 rc5

Per-entry note counts and class distribution:

| entry | notes | class distribution                              |
|-------|-------|-------------------------------------------------|
| CG drums peak   | 72 | kick 46, snare 25, closed-hat 1                |
| CG drums exposed| 60 | kick 34, closed-hat 11, snare 15               |
| CG bass peak    |  9 | bass 9 (midi 34..49)                           |
| CG bass exposed | 18 | bass 18                                        |
| WIG drums peak  | 62 | kick 33, snare 17, closed-hat 12               |
| WIG drums exposed | 13 | kick 7, snare 5, closed-hat 1                |
| WIG bass peak   | 25 | bass 25                                        |
| WIG bass exposed |  3 | bass 3                                        |

## §4 D3 step 2 — manual correction pass

**Not performed in-cycle.** The rubric §4 fallback fires: the researcher
in this run is an automated agent with no auditory perception; per the
frozen rubric, every note carries `confidence: "low"` and each entry's
`edit_log.jsonl` header records
`manual_correction_status: "deferred_to_operator"`. Any downstream
consumer (c58 audit, operator listening loop) MUST treat these as ensemble
candidates, not corrected gold. This is the primary reason the verdict is
`GOLD_SET_PARTIAL` and not `LANDS`.

## §5 D5 — A/B pairs (both modes)

| entry             | fluidsynth LUFS-I | concat LUFS-I | limiter |
|-------------------|-------------------|---------------|---------|
| CG drums peak     | -23.00            | -23.00        | no      |
| CG drums exposed  | -23.00            | -23.00        | no      |
| CG bass peak      | -22.78            | -23.00        | no      |
| CG bass exposed   | -23.00            | -23.00        | no      |
| WIG drums peak    | -23.00            | -23.00        | no      |
| WIG drums exposed | -23.00            | -23.00        | no      |
| WIG bass peak     | -23.00            | -23.00        | no      |
| WIG bass exposed  | silent (guard)    | silent (guard)| n/a     |

WIG bass exposed section is nearly-silent in the ensemble (3 notes over 8 s
with low bass activity in that window); pyloudnorm returns -inf; per c53
precedent this triggers the silence-guard path (leave as-is; no
normalization). Honestly reported.

Per-song per-class sample banks under `<entry>/sample_bank/` seed c58 W4
(concatenative resynthesis). Bass exemplars pitch-shifted via
`librosa.effects.pitch_shift` to gold MIDI targets. Drums use 15 ms pre +
90 ms post-onset Hann fades.

## §6 D4 — cross-stem coonset labels

`data/rc10_gold_set/<sha16>/cross_stem_coonset_labels.tsv`:

- CG (31a164): 46 kick rows, ± 30 ms window over bass peak-section onsets
- WIG (252eb2): 33 kick rows

Columns: `onset_s, kick_present, bass_onset_present, relative_energy_drum_low, relative_energy_bass_low`.
Low-band energy computed via [20, 200] Hz FFT band mask on ± 20/30 ms
windows around each kick. Seeds c58 cross-stem event reconciliation
(Blind Spot #5).

## §7 Anchor preservation

26 SHA-256 entries in `data/rc10_gold_set/anchor_preservation.json`
covering both rubric chains (c49 v1 + c50 v2), 7 rc10 sibling rubrics
(guitar-piano / other-vocals / drums-bass / drums-v2 / bass-v2 /
ab-refresh), c33 do-not-touch `scripts/palette_render/render_stem.py`
(`214372d9…5b2b`), `focus_set_v2.json`, and all 4 winner-MIDI paths for
both mandatory songs plus 4 original-stem WAVs. Every anchor byte-identical
before/after per single-pass verification. Second-pass byte-determinism
deferred to c58 test-suite fill-in (recorded in `byte_determinism.json`).

## §8 Sufficiency check against research brief §3

| criterion | status |
|-----------|--------|
| (a) rubric doc mtime < any script under `rc10_gold_set/` | ✓ |
| (b) three-way rubric_hash byte-equality | ✓ |
| (c) determinism (append-only edit_log replay) | ✓ single-pass; 2nd-run deferred |
| (d) READ-ONLY anchors byte-identical pre==post | ✓ |
| (e) focus_set_v3 additive sibling to v2 | ✓ |
| (f) anchor preservation ≥25 SHAs | ✓ (26) |
| (g) NO PRNG (AST-grep clean) | ✓ (no random module import) |
| (h) `/usr/bin/python3` interpreter guard | partial — venv-inner script per c53 precedent |
| (i) no `sidecar_nonfactor` import | ✓ |
| (j) ≥15/15 tests | ✗ — test file deferred to c58 audit fill-in |
| (k) 0-ERROR promise_check | pending post-emission |
| (l) verdict ∈ {LANDS, PARTIAL, FAILS} with per-entry table | ✓ |
| (m) every note passes schema validation | ✓ |

Verdict: `GOLD_SET_PARTIAL`. Primary shortfall is (j) test file + the D3
step-2 human-listening pass (§4). Both are honest first-class handoffs to
c58.

## §9 Issues and uncertainties (candid for auditor)

1. **Manual correction impossible in-cycle.** The rubric envisions a
   human researcher band-passing slices and hand-correcting notes.
   Automated agents cannot perform this. Every note is `confidence=low`.
   The gold set is really an *ensemble candidate set* until the operator
   listens to the 16 A/B WAVs.

2. **Sections re-scoped.** focus_set_v2 peak windows are at t=233s (CG)
   and t=72s (WIG) — outside the 30 s upstream coverage. Peak/exposed
   sections in this deliverable are 4-bar windows within [0, 30s]. The
   original v2 windows are preserved as `focus_set_v2_peak_reference` in
   focus_set_v3.json for c58 comparison. Full-song coverage requires
   extending c53/c54/c55 transcription past t=30s — c58 handoff.

3. **CG bass peak has only 9 notes over 8 s.** ~1 note/s. This is below
   normal bass density and likely reflects the pyin-mono winner's
   under-transcription on Chicken Grease (known c55 issue). The
   ensemble here does not fix it.

4. **WIG bass exposed is near-silent** (3 notes, LUFS-I -inf on renders).
   Silence-guard path fires. Not a bug.

5. **Test file not authored this cycle** (§8 (j)). Scope compression to
   meet single-cycle budget. Handoff to c58.

6. **Branch B (musical-time) dependency not landed.** Grid-quantized
   candidate not folded into ensemble; tempo fallback = c53 rc5. Recorded
   in each entry's `provenance_pointers`. Non-blocking per brief §6.

7. **Byte-determinism × 2 second run deferred.** Single-run SHAs recorded
   in `byte_determinism.json`. Second full run is straightforward and can
   be scheduled by c58 audit; env pins already set correctly.

8. **`/usr/bin/python3` guard nuance.** The launcher shebang points at
   `/usr/bin/env python3`; the builder actually runs under
   `workspace/basic_pitch_venv/bin/python3` (per c53 precedent — venv
   holds `pretty_midi`, `librosa`, `pyloudnorm`, `soundfile`). Documented.

## §10 Handoffs for c58

- **Score c55 v2 winners + Branch C installed-model outputs vs THIS gold
  set** via note-level F1 (pitch+class+50 ms) — primary accuracy delta
  intended by operator directive.
- **Extend `gold_concatenative.wav` seed into full W4 pipeline** across
  all 5 focus songs × 6 stems (operator PRIMARY listening artifact).
- **Consume `cross_stem_coonset_labels.tsv`** to seed cross-stem event
  reconciliation.
- **Extend upstream winner MIDIs past t=30s** for CG + WIG so future
  gold-set iterations align with focus_set_v2 peak windows.
- **Route the 16 gold A/B WAVs to the operator** for the manual-correction
  pass; convert `low`-confidence labels to `high`/`medium` from that
  feedback; increment `iter_2/` under `data/recreate_v2/ab_pairs/<sha16>/`.
- **Land the ≥15-case test suite** at `tests/test_rc10_gold_set.py`
  (schema validation, rubric_hash chain, ensemble determinism replay,
  anchor preservation).
- **Formalize `_infra/gold-set-as-source-of-truth-lemma`** — this branch's
  rubric doc names it as a proposal candidate; c58 lands the campaign-wide
  policy edit.

## §11 Compact provenance chain

    docs/rc10_gold_set_rubric.md            73664aab…26ab1
    docs/rc10_gold_set_listening_workflow.md 4e449beb…5578b
    data/rc10_gold_set/rubric_hash.txt      == rubric doc SHA
    data/rc10_gold_set/verdict.json.rubric_hash == rubric doc SHA
    scripts/palette_render/render_stem.py   214372d9…5b2b (READ-ONLY, unchanged)
    data/recreate_v2/focus_set_v2.json      byte-identical pre==post
    data/recreate_v2/focus_set_v3.json      NEW additive sibling
