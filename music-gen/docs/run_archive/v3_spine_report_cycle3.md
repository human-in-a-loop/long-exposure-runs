# M-V3-SPINE-1 Cycle-3 Report — Chicken Grease

**Song:** Chicken Grease, sha16 `31a164f845f8e27e`
**Cycle:** 3 of the v3 pivot (campaign cycle 58)
**Doctrine:** Per-stem transcription (OPERATOR DIRECTIVE 2026-09-02)
**Verdict:** `V3_SPINE_CHAIN_FAILS` — blocked_on_operator
**Deliverables:** `data/v3/deliveries/31a164f845f8e27e/{verdict.json, muscriptor_nondeterministic.json}`

## §1 — Cycle 1/2 triage

Verbatim `ls -la` at cycle-3 start:

```
data/v3/deliveries/31a164f845f8e27e/         (empty)
data/v3_spine/                               (rubric_hash.txt + subdir)
data/v3_spine/rubric_hash.txt                65 bytes, content b0031164…d54b555
data/v3_spine/31a164f845f8e27e/              (subdir)
  section.wav                                5292044 bytes, sha c107280e…fde6b49b
  anchor_preservation_pre.json               2536 bytes, sha a3d4c041…c83f8e
  anchor_preservation.json                   2656 bytes, sha b65e7d74…5b1e3da
  muscriptor/drums.mid                       1573 bytes, sha fa252589…2abe91
  muscriptor/drums.json                      36451 bytes, sha b4cafa16…f1d7704
  muscriptor/bass.mid                        663 bytes, sha b51f5d7c…d33a7ef5
  stems_6s/{drums,bass,guitar,other,piano,vocals}.wav   (6 × 5292044 bytes)
```

**Per-artifact disposition:** all cycle-1/2 artifacts are **per-stem-doctrine-aligned**
(section extract + 6 htdemucs_6s stems + MuScriptor per-stem outputs). None are
full-mix-superseded. Zero files moved to `tools/stale/cycle1_full_mix_superseded/`.
All adopted as valid inputs to cycle 3.

## §2 — 21-anchor pre-snapshot verification

`data/v3_spine/31a164f845f8e27e/anchor_preservation_pre.json` (SHA
`a3d4c041fbb9fa5b456fb29e797b1d9246d213c754053f90e7e6f77d07c83f8e`) enumerates
**21 anchors**. Verified by running
`scripts/v3_spine/anchor_preservation.py --song-sha16 31a164f845f8e27e` (post),
which returned `{"phase": "post", "n_anchors": 21, "all_match": true, "n_mismatch": 0}`.
No drift between cycle-2 snapshot and cycle-3 on-disk state.

**Verified anchor SHAs (spot-check):**
| Anchor | SHA | Notes |
|---|---|---|
| `/usr/share/sounds/sf2/FluidR3_GM.sf2` | `74594e8f…1cb0` | Matches prior-context (not fabricated) |
| `scripts/palette_render/render_stem.py` | `214372d9…5b2b` | Matches prior-context; DO-NOT-TOUCH lock preserved |
| `workspace/models/muscriptor-medium/model.safetensors` | `ac80adbd…7fb97ec` | Matches prior-context |
| `corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3` | `31a164f8…4b3049` | Matches song_sha16 header |
| `docs/v3_spine_rubric.md` | `b0031164…d54b555` | Three-way chain anchor |

Post-run re-check: `n_mismatch=0` across all 21. All READ-ONLY anchors preserved.

## §3 — MuScriptor instrument-vocab + operator-whitelist mapping

`workspace/learned_transcribers_venv/bin/muscriptor list-instruments` emits
**35 labels** (pinned in `data/v3_spine/muscriptor_instrument_vocab.json`).

**Mapping table** (full details in `docs/v3_spine_instrument_whitelist_mapping.md`):

| Operator stem | MuScriptor `--instruments` |
|---|---|
| drums | `drums` |
| bass | `electric_bass,acoustic_bass` |
| guitar | `acoustic_guitar,clean_electric_guitar,distorted_electric_guitar` |
| piano | `acoustic_piano,electric_piano,organ` |
| other | `synth_lead,synth_pad,synth_strings,orchestra_hit,chromatic_percussion` |
| vocals | `voice` |

**`MISSING_LABEL` findings:** zero. All operator semantic categories map to at
least one MuScriptor vocab entry (word-order flip on guitar handled explicitly).

## §4 — MuScriptor determinism per stem + full-mix

| Probe | Artifact | Run-1 SHA | Run-2 SHA | Equal? | Run-2 wall |
|---|---|---|---|---|---|
| drums | mid | `fa252589…2abe91` | `fa252589…2abe91` | **✓** | 68.5 s |
| drums | json | `b4cafa16…f1d7704` | `b4cafa16…f1d7704` | **✓** | 63.4 s |
| bass | **mid** | `b51f5d7c…d33a7ef5` (663 B) | `8d88b1f5…95a4c803` (639 B) | **✗ STOP** | 69.9 s |
| bass | json | `e80ab193…203ae853` | `e80ab193…203ae853` | **✓** | 63.7 s |
| guitar | mid | `f209c940…39ca9233` | *(deferred)* | — | — |
| guitar | json | `97b5a598…6f4ddabc` | *(deferred)* | — | — |
| other | mid | `b4134d5c…dc75e10b` (empty-track MIDI) | *(deferred)* | — | — |
| other | json | `4f53cda1…202b945` (SHA of `[]`) | *(deferred)* | — | — |
| piano | mid | `b4134d5c…dc75e10b` (empty-track MIDI) | *(deferred)* | — | — |
| piano | json | `4f53cda1…202b945` (SHA of `[]`) | *(deferred)* | — | — |
| vocals | mid | `5f50b174…5792b08c` | `5f50b174…5792b08c` | **✓** | 120.3 s |
| vocals | json | `00ab8959…62721500` | `00ab8959…62721500` | **✓** | 114.0 s |
| full_mix | mid | `c3186d82…c2c98e1a` | *(deferred pending operator decision)* | — | — |
| full_mix | json | `7d011b61…14420fb` | *(deferred pending operator decision)* | — | — |

**Rung-1 verdict: FAIL** on `(bass, midi)`. Falsifying tuple with byte-level
details (`first_diff_byte_offset=40`, `n_diff_bytes=365`, `len1=663`, `len2=639`)
pinned in `data/v3/deliveries/31a164f845f8e27e/muscriptor_nondeterministic.json`.

**Nuance:** `bass.json` reproduces byte-identically across the two runs. The
underlying model events ARE deterministic; only the MIDI container encoding
differs. Not a numerical stability issue — a MIDI-write serialization issue.

**Empty-transcription findings on `other` + `piano`:** both stems yielded 0 events
under the operator whitelist on this 30 s section. This is a content finding
(the stem contents don't fall into the chosen categories), not a nondeterminism
finding. Documented in `docs/v3_spine_instrument_whitelist_mapping.md` §Vocab-choice.

## §5 — Downstream pipeline

**NOT PERFORMED.** Per Fixed Decision 1 ("no tuning, no retry, no fallback —
operator decides"), rung-1 STOP forbids proceeding to merge/render/mix/deliver.
Sub-leaves NOT executed this cycle:

- `tempo-map-chosen` (deferred → c4)
- `gm-program-map-v3-extended` (module exists but not exercised)
- `per-stem-midi-merged` (deferred → c4)
- `full-mix-reconciliation-emitted` (deferred → c4)
- `render-plus-vocals-overlay` (deferred → c4)
- `mix-match-applied` (deferred → c4)
- `ab-delivery-emitted` (deferred → c4; **operator has no audible artifact this cycle**)
- `panel-regression-checked` (deferred → c4)

## §6 — Partial-state summary + tail hand-off to cycle 4

**Wall time used this cycle** (subprocess-serial in-turn):
- drums determinism × 2: 132 s (Run 2 both formats)
- Run-1 fills for bass.json + guitar/other/piano/vocals + full_mix: ~1230 s
- bass + vocals determinism × 2: 368 s
- **Total wall in MuScriptor probes: ~30 min**

**Completed prefix:** rubric committed; anchors preserved pre==post; vocab mapped;
6 stems + full-mix Run-1 SHAs pinned; drums+vocals ×2 pass, bass.mid ×2 fail.

**Cycle-4 hand-off (operator decision needed FIRST):**

`data/v3/deliveries/31a164f845f8e27e/muscriptor_nondeterministic.json`
names three options:

- **OPTION A** — canonicalize MIDIs from the byte-deterministic JSON events
  (bypass MuScriptor `--format midi`); the underlying transcription IS stable,
  only the MIDI container has content-dependent nondeterminism.
- **OPTION B** — reject and require MuScriptor upstream fix for the MIDI writer.
- **OPTION C** — pin `bass.mid` to Run-1 as a logged exception and proceed.

Whichever the operator chooses, cycle 4 continues the pipeline from step 6
(tempo_map.py) onward on the completed prefix + operator-chosen MIDI-canon path.

## §7 — Operator hand-off

**Zero audible artifacts delivered this cycle.** The operator ear listening loop
does not open until either (a) operator OK's OPTION A/B/C, or (b) MuScriptor
upstream fixes the MIDI-writer nondeterminism.

Two cycles (c1, c2) previously reported "waiting on background pipeline". Cycle 3
did the pipeline itself, subprocess-serial, and hit a real STOP condition on
rung-1. This is a **first-class negative finding**, not a null cycle. The chain
CANNOT be tuned around; the operator's Fixed Decision 1 forbids it.

**Files the operator should look at, in order:**

1. `data/v3/deliveries/31a164f845f8e27e/verdict.json` — top-level verdict
2. `data/v3/deliveries/31a164f845f8e27e/muscriptor_nondeterministic.json` — the falsifying tuple + option surface
3. `data/v3_spine/31a164f845f8e27e/muscriptor_determinism_per_stem.json` — full determinism table
4. `docs/v3_spine_instrument_whitelist_mapping.md` — instrument-vocab honest-disclosure of `other`+`piano` empty-transcription content finding
5. this file (`docs/v3_spine_report_cycle3.md`)

**No A/B WAVs, no full-song WAV, no panel TSV.** Per Fixed Decision 1.
