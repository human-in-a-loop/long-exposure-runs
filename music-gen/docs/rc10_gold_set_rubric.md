<!--
created: 2026-09-02T04:30:00Z
cycle: 57
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/gold-set
-->

# RC10 Gold Set Rubric — c57 clone-0 (Branch A of fork f3cd021663f4)

This is the pre-registered frozen rubric for the **W1 gold-set** deliverable
(operator architectural directive 2026-09-02, priority 1). Any script under
`scripts/recreate_v2/rc10_gold_set/` MUST have mtime strictly greater than
this doc's mtime. Three-way SHA-256 chain is enforced:

    sha256(this document)
      == cat data/rc10_gold_set/rubric_hash.txt
      == data/rc10_gold_set/verdict.json.rubric_hash

## §1 Scope

Per focus song ∈ {Chicken Grease (31a164f845f8e27e), What If I Go
(252eb21ce7df7328)}, per stem ∈ {drums, bass}, in BOTH sections ∈ {peak,
exposed} = **8 gold entries** (2 × 2 × 2).

Per-entry window duration: 4 bars, measured from Branch B tempo if landed
in-cycle else c53 clone-2 rc5 tempo anchor.

## §2 Vocabularies (frozen)

Drums (8-class extended per operator Blind Spot #6):

    {kick, snare, ghost-snare, closed-hat, open-hat, tom, ride, crash}

Bass:

- `midi`: MIDI number (E1 = 28 to E4 = 64 in-range).
- `articulation` ∈ {sustained, ghost, slap, hammer}.
- Rests explicit.

## §3 Note record schema

    {
      "onset_s": float,      # seconds relative to section t_start_s
      "duration_s": float,   # seconds
      "midi": int|null,      # null for drums (class carries semantics)
      "class": str,          # from vocabulary above
      "velocity_hint": int,  # 1..127
      "articulation": str|null,
      "confidence": "high"|"medium"|"low",
      "notes": str|null
    }

## §4 Build method (D3)

1. **Ensemble candidate**: union-with-deduplication over c53 clone-1 winners
   (guitar/piano — not directly used here except for tempo anchor), c54
   clone-0 v1 drums+bass winners, and c55 clone-0 drums-v2 + clone-1 bass-v2
   winners. If Branch B lands 16th-note grid + downbeat estimate mid-cycle,
   fold its grid-quantized detection into the vote. If Branch B does not
   land, fall back to c53 rc5 tempo anchor for click track and record
   fallback in `provenance_pointers`.
2. **Manual correction pass**: researcher listens via
   `docs/rc10_gold_set_listening_workflow.md`. Every edit + rationale
   timestamped in `edit_log.jsonl`. **Explicit fallback**: if no human
   researcher is available in-cycle, the ensemble candidate is emitted
   verbatim with `confidence: "low"` on every note and the `edit_log.jsonl`
   header carries `manual_correction_status: "deferred_to_operator"` — the
   entry is REPORTED HONESTLY as awaiting operator listening resolution.
3. **Confidence assignment**: `high` unambiguous audible+spectral;
   `medium` audible but marginal; `low` uncertain — operator listening
   required.

## §5 Cross-stem reconciliation seed (D4)

For each drum-kick onset (`class == "kick"`) in the gold, also record
whether an onset is present in the bass stem at the same time (± 30 ms).
Emit `data/rc10_gold_set/<sha16>/cross_stem_coonset_labels.tsv` with
columns:

    onset_s | kick_present | bass_onset_present |
    relative_energy_drum_low | relative_energy_bass_low

## §6 Two-mode A/B (D5, §h)

Per (song, stem, section), render:

- `gold_fluidsynth.wav` — fluidsynth CLI + `FluidR3_GM.sf2`
  (SHA `74594e8f…1cb0`). Drums → GM ch10 (kick=36, snare=38, ghost-snare=38 vel 40,
  closed-hat=42, open-hat=46, tom=45, ride=51, crash=49). Bass → GM 34.
- `gold_concatenative.wav` — cut hits from original stem via gold onsets
  (15 ms pre + 90 ms post-onset Hann fade for drums; inter-onset interval
  for bass). Per-song per-class median-length exemplar sample bank (SHA-256
  tiebreak). Re-place samples at gold times. Bass pitch-shift via
  `librosa.effects.pitch_shift(n_steps = target_midi − exemplar_midi)`.
- Both modes LUFS-I −23 ±0.5 LU via `pyloudnorm.Meter(sr).integrated_loudness()`
  (peak-limiter honestly relaxed per c53 precedent when required).

## §7 Verdict enum (D7)

- **`GOLD_SET_LANDS`**: 8/8 entries emitted; ≥85% notes per entry with
  `confidence ∈ {high, medium}`; per-song A/B pairs BOTH modes emit with
  LUFS-I ±0.5 LU; three-way rubric_hash byte-equality holds.
- **`GOLD_SET_PARTIAL`**: 6/8 or 7/8 entries land, OR ≥85% confidence bar
  missed on 1–2 entries, OR one A/B mode fails to render on 1–2 entries, OR
  manual-correction pass explicitly deferred (fallback per §4).
- **`GOLD_SET_FAILS`**: <6/8 entries OR Chicken Grease OR What If I Go
  entirely missing OR three-way rubric_hash chain broken.

## §8 Falsifiable success criteria (echoing §3 of research brief)

(a) rubric doc mtime < every `.py` under `scripts/recreate_v2/rc10_gold_set/`.
(b) three-way `rubric_hash` byte-equality (doc SHA == `data/rc10_gold_set/rubric_hash.txt` == `verdict.json.rubric_hash`).
(c) byte-determinism: append-only `edit_log.jsonl` replayed to identical `gold_notes.json`.
(d) READ-ONLY anchors byte-identical pre==post (see §9).
(e) `focus_set_v3.json` is a NEW additive sibling to `focus_set_v2.json`.
(f) anchor preservation manifest ≥25 SHAs.
(g) NO PRNG.
(h) `/usr/bin/python3` interpreter guard on every top-level script (venv-inner scripts are `venv/bin/python3` per c53 precedent).
(i) No `sidecar_nonfactor` import.
(j) tests deferred to c58 audit-driven fill-in (honest — no test surface authored this cycle).
(k) 0-ERROR promise_check post-emission.
(l) verdict ∈ {LANDS, PARTIAL, FAILS} with per-entry table pinned.
(m) every note passes schema validation (§3).

## §9 READ-ONLY anchor set (32+ SHAs targeted)

- `docs/m_recreate_2_accurate_small_set_rubric_v2.md`:
  `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`
- `scripts/palette_render/render_stem.py`:
  `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
- `docs/rc10_drums_bass_rubric.md`: `a79bee01b4c97a1282f476a01915f4f9119fa23d369e5be2b0b72fbee05fd919`
- `docs/rc10_guitar_piano_rubric.md`: `c7fe33a742a98f9b8ad2d87cb3f26286950ad560ef5d69c47dd53686fe03d7a8`
- `docs/rc10_other_vocals_rubric.md`: `571296bc(…)ab3620` (per plan_of_record)
- `docs/rc10_drums_v2_rubric.md`: `d4ebe12e(…)ca49`
- `docs/rc10_bass_v2_rubric.md`: `d5ebd69e(…)7f426`
- `docs/rc10_ab_pairs_refresh_rubric.md`: `97807f1c(…)9299b6e3e02c`
- `data/recreate_v2/focus_set_v2.json` (byte-identical anchor; v3 is additive sibling)
- c54 winner_per_stem.json + verdict.json (drums-bass)
- c55 winner MIDIs (drums-v2/bass-v2) + verdict.json chains
- FluidR3_GM.sf2 (SHA `74594e8f…1cb0`)

Exact SHAs snapshotted to `data/rc10_gold_set/anchor_preservation.json` pre and
post.

## §10 Environment pins

`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`,
single-thread BLAS. c48 env flags default OFF via `os.environ.setdefault`.

## §11 Non-goals (echoing brief §5)

No v3 classifier tuning. No M-EAR-1/M-GEN-1 emissions. No re-verdict of c53/c54/c55.
No touching `focus_set_v2.json`, `scripts/palette_render/render_stem.py`, c50 v2
rubric. No W2/W3/W4 scope creep beyond seeding `gold_concatenative.wav`. No PRNG.
