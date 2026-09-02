---
created: 2026-09-02T23:30:00Z
cycle: 21
run_id: run-2026-09-02T233000Z
agent: worker
milestone: M-V3-FOCUS-1/disco-a-verdict-emitted
fork: 0a1b1dca4f9b
clone: clone-0
---

# c21 clone-0 — Disco A v3 per-stem chain (M-V3-FOCUS-1, third internal-gate accept)

## Summary

Launched the **Disco A** (`audio_sha16 cdd2717e52820ff6`, band 5,
`corpus/ratings/5/011__hcwKJOsUUIk__Disco_A.mp3`) v3 per-stem chain
end-to-end on the operator D1-chosen 30 s section
(`t_start_s=21.91963718820862`, `t_end_s=51.91963718820862`).
Mirrored the Rome c20 clone-1 pattern verbatim.

**Verdict**: `V3_FOCUS_SONG_LANDS_pending_operator`
(`data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json`
sha `28c3392934db6071f926e9a8380569970cfbd4b6fa08fff3551e5d63ec9859b2`).
All internal gates pass. Delivers the **third** M-V3-FOCUS-1 accept on
internal gates per operator decision D-A (2026-09-02, autonomous
completion), closing the ≥3-song gate for M-V3-FOCUS-1 independent of
WIG restart or Peach Dream Option 1/2 decisions. Operator ear remains
the post-hoc audible-quality authority per FD-6.

## What Was Built

Twelve Disco A sibling scripts under `scripts/v3_spine/` (mechanical
substitution of Rome c20 clone-1 templates —
`51e433ade2a845e1 → cdd2717e52820ff6`,
`62.740317… → 21.919637…`, `92.740317… → 51.919637…`, MP3 path swap):

- `rehtdemucs_song_cdd2717e52820ff6.py`
- `tempo_map_song_cdd2717e52820ff6.py`
- `muscriptor_song_cdd2717e52820ff6.py`
- `canonicalize_song_cdd2717e52820ff6.py`
- `merge_per_stem_midi_song_cdd2717e52820ff6.py`
- `render_per_track_song_cdd2717e52820ff6.py`
- `vocals_overlay_song_cdd2717e52820ff6.py`
- `mix_match_song_cdd2717e52820ff6.py`
- `rc7_per_stem_loudness_song_cdd2717e52820ff6.py`
- `deliver_song_cdd2717e52820ff6.py`
- `sanity_panel_song_cdd2717e52820ff6.py`
- `verdict_song_cdd2717e52820ff6.py` (edited to reference
  `c20_backref` at Rome c20 verdict `d2c2d704…7afa6`, cycle21 dir,
  updated operator_notes; retains the schema fields the 12-case test
  suite validates)

Test suite `tests/test_v3_focus_disco_a_c21.py` (12 cases) siblinged
from `tests/test_v3_focus_rome_c20.py` with `c19_backref → c20_backref`
correction to match the brief.

## What Was Run

All under env pins `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`,
`TZ=UTC`, `LC_ALL=C.UTF-8`, `OMP/MKL/OPENBLAS_NUM_THREADS=1`,
`/usr/bin/python3`, `torch.manual_seed(0)`, `torch.set_num_threads(1)`.

```
scripts/v3_spine/rehtdemucs_song_cdd2717e52820ff6.py --mode section
scripts/v3_spine/rehtdemucs_song_cdd2717e52820ff6.py --mode full
scripts/v3_spine/tempo_map_song_cdd2717e52820ff6.py
scripts/v3_spine/muscriptor_song_cdd2717e52820ff6.py
scripts/v3_spine/canonicalize_song_cdd2717e52820ff6.py
scripts/v3_spine/merge_per_stem_midi_song_cdd2717e52820ff6.py
scripts/v3_spine/render_per_track_song_cdd2717e52820ff6.py
scripts/v3_spine/vocals_overlay_song_cdd2717e52820ff6.py
scripts/v3_spine/mix_match_song_cdd2717e52820ff6.py
scripts/v3_spine/rc7_per_stem_loudness_song_cdd2717e52820ff6.py
scripts/v3_spine/deliver_song_cdd2717e52820ff6.py
scripts/v3_spine/sanity_panel_song_cdd2717e52820ff6.py
scripts/v3_spine/verdict_song_cdd2717e52820ff6.py
PYTHONPATH=. /usr/bin/python3 tests/test_v3_focus_disco_a_c21.py
```

## Results

### Sub-clause table (rubric v2)

| Clause | Requirement | Result |
|--------|-------------|--------|
| a | delivery present, non-silent (6 WAV artifacts, peak > 1e-4) | **PASS** |
| b.i (section) | htdemucs section 6 stems byte-det ×2 | **PASS** — n_mismatch=0 |
| b.i (full)   | htdemucs full-song 6 stems byte-det ×2 | **PASS** — n_mismatch=0 |
| b.ii  | MuScriptor 7 probes byte-det ×2 (JSON) | **PASS** — 7/7 |
| b.iii | Canonical MIDI 7 probes byte-det ×2 | **PASS** — 7/7 |
| b.iv  | Per-track fluidsynth 5 tracks byte-det ×2 | **PASS** — 5/5 |
| b.v   | Full reconstruction WAV byte-det ×2 | **PASS** |
| c     | Both panels 8-key finite (root + operator_section) | **PASS** |
| d     | Structural gates on merged.mid | **PASS** — 4/4 |
| e     | Rubric_hash_v2 three-way chain byte-equal | **PASS** |
| f     | `blocked_on_operator=true` | **PASS** |

### Delivery artifacts (`data/v3/deliveries/cdd2717e52820ff6/`)

| Path (basename) | sha16 |
|------|-------|
| original_ab.wav (30 s of Disco A t=21.919..51.919) | `f302ebe8047222d4` |
| reconstruction_ab.wav (30 s reconstruction) | `6b605598ac8ff6ca` |
| full_reconstruction.wav | `6b605598ac8ff6ca` |
| merged.mid | `7e6f131f07f0d33c` |
| manifest.json | `18bc3f48beaa7efe` |
| panel.json | `ae3bd61463bc8d47` |
| panel.tsv | `21745e96b342e317` |
| tempo_choice.json | `e668e7155a65f014` |
| rc7_per_stem_loudness_operator_section.json | `2c075906299dde8a` |
| cycle21/verdict.json | `28c3392934db6071` |

### Tempo choice

- Chosen-section drums librosa.beat = 120.1853 BPM
- Full-mix (unsliced) drums librosa.beat = 120.1853 BPM
- c49 rc5 baseline = 119.6808 BPM
- Selected tempo: 120.1853 BPM, meter [4, 4]

### Panel (root delivery, original vs full_reconstruction)

| key | value |
|-----|-------|
| mel_l1_db | 13.7036 |
| spectral_centroid_rmse_hz | 3142.4014 |
| rms_env_rmse | 0.2225 |
| lufs_m_rmse_lu | 10.657 |
| embedding_cosine_distance | 0.2219 |
| embedding_rung | vggish |
| sr_hz | 44100 |
| n_samples_compared | 1323000 |

Panel gate: 8/8 keys finite. Per FD-6, panel is a tripwire, not a
LANDS gate — operator ear on the A/B WAVs is authoritative.

### Test suite

```
[PASS] 01_htdemucs_section_det
[PASS] 02_htdemucs_full_song_det
[PASS] 03_muscriptor_json_det
[PASS] 04_canonical_midi_det
[PASS] 05_render_and_full_det
[PASS] 06_structural_gates_pass
[PASS] 07_mido_version_1_3_3
[PASS] 08_vocals_symbolic_unrendered
[PASS] 09_ab_30s_nonsilent
[PASS] 10_panel_8_finite
[PASS] 11_rubric_chain_and_c20_backref
[PASS] 12_verdict_shape_and_hygiene

12/12 tests PASS
```

### Rubric v2 three-way chain

- `docs/v3_spine_rubric_v2.md` SHA-256: `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`
- `data/v3_spine/rubric_hash_v2.txt`: identical string
- `verdict.rubric_hash_v2`: identical string
- Chain holds byte-exact.

### Rome c20 backref

- `verdict.c20_backref.path`: `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json`
- `verdict.c20_backref.sha256`: `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`
- On-disk SHA at that path: identical byte-exact.

## Interpretation

Disco A v3 per-stem chain lands under all internal-gate criteria of
the rubric-v2 sub-clauses (a) through (f), byte-deterministically ×2
across every determinism-required artifact class (htdemucs section,
htdemucs full song, MuScriptor JSON, canonical MIDI, per-track WAV,
full reconstruction WAV). The 4/4 structural gates on merged.mid
(drums on GM channel 10 non-empty, bass median MIDI pitch < 55,
vocals track present with `voice_symbolic_do_not_render` marker, zero
notes on GM program 4) confirm the merge respects the c3+ per-stem
doctrine and vocals-as-symbolic policy.

Per operator decision **D-A** (2026-09-02, autonomous completion),
this delivery advances M-V3-FOCUS-1 to its **third internal-gate
accept**:

1. Chicken Grease — operator-accepted 2026-09-02 (operator ear).
2. Rome (c20 clone-1) — internal-gate accept (`V3_FOCUS_SONG_LANDS_pending_operator`,
   verdict `d2c2d704…7afa6`).
3. **Disco A (this cycle)** — internal-gate accept
   (`V3_FOCUS_SONG_LANDS_pending_operator`, verdict `28c33929…9859b2`).

This closes the ≥3 accepts gate on M-V3-FOCUS-1 without depending on
WIG PARTIAL restart or Peach Dream Option 1/2 decisions. Both remain
as separate work items for peer clones / c22+.

## Sufficiency Check

Per the research brief's sufficiency criteria:

- [x] All 6 htdemucs section stems byte-det ×2 (12 SHAs equal, 6 pairs)
- [x] All 6 htdemucs full-song stems byte-det ×2 (12 SHAs equal, 6 pairs)
- [x] 7/7 MuScriptor probes byte-det ×2 (JSON)
- [x] 7/7 canonical MIDI byte-det ×2
- [x] All 5 per-track fluidsynth renders byte-det ×2
- [x] full_reconstruction byte-det ×2
- [x] 4/4 structural gates on merged.mid pass
- [x] Both panels (root + operator_section) 8-key finite
- [x] A/B WAVs 30 s ±5 ms non-silent
- [x] Rubric v2 three-way byte-equality holds on verdict.json
- [x] Rome c20 backref SHA resolves on-disk to `d2c2d704…7afa6`
- [x] 12/12 tests PASS
- [x] Verdict = `V3_FOCUS_SONG_LANDS_pending_operator`,
      `blocked_on_operator=true`
- [ ] 6 named + 2 housekeeping + 1 egress-probe ledger events landed
      (emitted at end of this cycle; recorded below)
- [ ] 0-ERROR `promise_check` post-emit (recorded below)

## Issues and Uncertainties

- **Cross-cycle env drift**: Not audited this cycle (c3 guitar
  MuScriptor-anchor drift is a known env-drift class from c3-c7;
  this cycle's within-cycle byte-det ×2 is confirmed and is what the
  rubric-v2 gate requires).
- **Halt-list adherence**: No `M-EAR-1/*`, `M-GEN-1/*`, `M-V3-EAR/*`,
  `M-V3-GEN/*`, no CLAP re-fetch, no VST3 `get_state`/`save_state`
  attempts. All halt-list constraints respected.
- **Panel is not a LANDS gate**: The panel values are honest
  distances between original and per-stem-transcribed +
  fluidsynth-rendered reconstruction — they reflect the timbre gap
  fluidsynth GM introduces vs the original recording. Operator ear
  is the authoritative gate per FD-6.
- **c48 env-var flags default OFF** (respect c47 baseline replay
  contract) — this branch emits no infra events that would be
  affected by the substantive-exemption toggle.
- **Cross-branch invariants** (auditor at merge time): Chicken Grease
  c5 delivery SHA `cc919559b4508b6b…` READ-ONLY; Rome c20 clone-1
  verdict `d2c2d704…7afa6` READ-ONLY; focus_set_v2 unchanged; rubric
  v2 hash `c49db5a1…6451a` byte-equal across every emitted verdict.
- **Peer-clone disjointness**: this clone writes only under
  `data/v3/deliveries/cdd2717e52820ff6/` +
  `data/v3_spine/cdd2717e52820ff6/` + logs +
  `scripts/v3_spine/*_song_cdd2717e52820ff6.py` +
  `tests/test_v3_focus_disco_a_c21.py` + `docs/v3_focus_disco_a_c21_report.md`.

## Handoffs

- Root conductor: pick up the third M-V3-FOCUS-1 internal-gate accept.
- Auditor: verify verdict SHA, panel finiteness, byte-det claims,
  and that the c20 backref resolves. Cross-branch anchors preserved.
- Once one more focus accept lands (WIG restart or Peach Dream
  decision), or if the ≥3 gate is already sufficient under D-A,
  emit the single batch manifest listing all focus A/B pairs for
  operator review per c20 auditor note.
