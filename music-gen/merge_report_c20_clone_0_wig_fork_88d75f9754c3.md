# c20 clone-0 (fork 88d75f9754c3) — WIG (What If I Go) Merge Report

**Branch**: c20 fanout clone-0 (fork 88d75f9754c3, clone 0 of 3)
**Song**: What If I Go — sha16 `252eb21ce7df7328`, sha256 `252eb21ce7df7328e498b14f94afc8f38fec5c5fa85a9f815c7ee6ca94c4e59a`
**Rating band**: 5 · `corpus/ratings/5/021__pLuQ0MGLBXU__Mura_Masa_-_What_If_I_Go.mp3`
**Verdict**: `V3_FOCUS_SONG_LANDS_pending_operator` (verdict.json is authoritative; this doc summarizes)
**Chosen section**: t=72.77133..102.77133s (D1 chosen_section from `data/recreate_v2/focus_set_v2.json`)

**Note**: The conductor's expected merge-report path
`/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-0/merge_report.md`
is outside this session's writable scope (session is scoped to `/home/user/long-exposure-runs/music-gen`).
Report is written here at `merge_report_c20_clone_0_wig_fork_88d75f9754c3.md` in the workspace
root as the accessible fallback — same convention used by c57 clone-0 (see
`merge_report_c57_clone0.md`). Root conductor should pick it up from that path.

## Scope

Per c20 fanout clone-0 assignment (operator break-glass: env-drift investigation
CLOSED as `non_factor`; exit heartbeat cadence; build 4 remaining focus songs
end-to-end so operator can listen to whole focus set in one batch):

- Run the full proven v3 per-stem doctrine chain end-to-end on WIG's D1-chosen
  peak+exposed section, mirroring the c5 Chicken Grease Track B pattern exactly.
- Emit A/B WAVs, full-song reconstruction, manifest, panel, verdict under
  `data/v3/deliveries/252eb21ce7df7328/{,operator_section/,cycle20/}`.
- Preserve every c4–c19 READ-ONLY anchor (append-only discipline; no anchor edits).
- Add per-song sibling scripts under `scripts/v3_spine/*_wig.py` — the c5 CG
  originals are READ-ONLY and untouched.
- 12-case test file `tests/test_v3_focus_wig_c20.py`.
- 4-row housekeeping under `-clone-0` suffix (egress-probe / plan-register /
  adopt-tests / archive at ts+1s).

## Sibling scripts landed (append-only; c5 CG originals READ-ONLY)

1. `scripts/v3_spine/rehtdemucs_operator_section_wig.py` — htdemucs_6s on WIG
   operator section ×2 for byte-determinism.
2. `scripts/v3_spine/tempo_map_operator_section_wig.py` — `librosa.beat.beat_track`
   on WIG operator-section drums + full-mix cross-check.
3. `scripts/v3_spine/muscriptor_operator_section_wig.py` — per-stem MuScriptor
   with c3 vocab whitelists (35 labels), JSON+MIDI ×2, 7 probes (6 stems + full_mix).
4. `scripts/v3_spine/canonicalize_operator_section_probes_wig.py` — canonical
   MIDI via c4 READ-ONLY `midi_from_json_events.py` ×2, per-stem.
5. `scripts/v3_spine/merge_per_stem_midi_operator_section_wig.py` — merge with
   4/4 structural gates (drums ch10 non-empty · bass median<55 · vocals
   symbolic-track present · zero GM4).
6. `scripts/v3_spine/render_per_track_operator_section_wig.py` — fluidsynth
   per-track render ×2 with SF2 `74594e8f…1cb0`.
7. `scripts/v3_spine/vocals_overlay_operator_section_wig.py` — D2 vocals overlay
   via SHA-verified htdemucs vocals stem copy.
8. `scripts/v3_spine/mix_match_operator_section_wig.py` — rc7 Method A plain
   RMS-match mix ×2.
9. `scripts/v3_spine/sanity_panel_operator_section_wig.py` — 8-key panel + cross-
   window tripwire vs c5 CG panel.tsv (NEVER a LANDS gate per FD-6).
10. `scripts/v3_spine/deliver_operator_section_wig.py` — emit A/B WAVs + manifest.
11. `scripts/v3_spine/verdict_c20_wig.py` — emit
    `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json`.

Plus one housekeeping emitter (one-shot):

12. `tools/stale/cycle20_v3_wig_clone_0_scratch/emit_ledger_events_c20_wig_clone_0.py`
    — 4 rows appended to `promise_ledger.jsonl` with `-clone-0` suffix.

## Test file

- `tests/test_v3_focus_wig_c20.py` — 12 cases covering:
  htdemucs det ×2 · MuScriptor JSON det ×2 · canonical MIDI det ×2 · per-track
  render det ×2 · full_reconstruction det ×2 · 4/4 structural gates · mido==1.3.3
  · vocals symbolic marker · A/B 30s ±5ms non-silent · panel 8-key finite +
  tripwire · three-way rubric_hash_v2 chain byte-equal · hygiene grep (no PRNG,
  no `sidecar_nonfactor` in WIG scripts).

## Rubric-hash three-way chain

`c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` — expected to
hold byte-equal across `data/v3_spine/rubric_hash_v2.txt`, delivery manifest, and
verdict.json (verified by test 11).

## Anchor preservation

All c4–c19 CG delivery artifacts, all locked v3_spine scripts (rc7 originals,
render_stem, midi_from_json_events, mix_match_operator_section, torch213 probes
c7..c19, rehtdemucs_operator_section, etc.), SF2, spec docs, rubric-chain docs,
`focus_set_v2.json`, muscriptor vocab: untouched. All new artifacts land under
new paths (`data/v3_spine/252eb21ce7df7328/…`, `data/v3/deliveries/252eb21ce7df7328/…`,
`scripts/v3_spine/*_wig.py`, `tests/test_v3_focus_wig_c20.py`, this file).

## Non-factors and honest notes

- **Tempo halving on WIG operator section**: librosa on the section drums yields
  ~50.17 BPM; on section full mix ~99.38 BPM; RC5 whole-song baseline is
  200.89 BPM. All are consistent (each ~half the next). Pipeline uses drums-stem
  choice (matches c5 CG source convention). Reconstruction correctness does not
  depend on the specific tempo value — the tempo drives MIDI note timing which
  fluidsynth renders identically at any consistent BPM. Logged in `tempo_choice.json`
  under `delta_vs_rc5_baseline_bpm`.
- **Merge report path**: written to workspace root, not instance dir (see Note
  above).
- **Panel**: NEVER a LANDS gate per FD-6. Cross-window tripwire compares against
  c5 CG panel.tsv (different song, so tripwire is about scale not equality; the
  `note` field in `panel.json` records this explicitly).
- **c4–c19 heartbeat chain**: this clone does NOT emit a heartbeat verdict (no
  `verdict-c20-emitted` under M-V3-SPINE-1). Per operator break-glass, c20 exits
  heartbeat cadence in favour of focus-song build-out. The four housekeeping
  rows carry the substantive milestone under M-V3-FOCUS-1/wig-c20-clone-0/.

## Egress state

HTTP 429 + tv_embedded unchanged from c47–c19 registry. Egress-probe row
appended per c49 path B. Not blocking.

## Files landed

| Path | Description |
| ---- | ----------- |
| `data/v3/deliveries/252eb21ce7df7328/operator_section/original_ab_operator_section.wav` | 30s original A |
| `data/v3/deliveries/252eb21ce7df7328/operator_section/reconstruction_ab_operator_section.wav` | 30s reconstruction B |
| `data/v3/deliveries/252eb21ce7df7328/operator_section/full_reconstruction_operator_section.wav` | full section reconstruction |
| `data/v3/deliveries/252eb21ce7df7328/operator_section/manifest.json` | c5-format manifest with SHA/duration/peak per artifact |
| `data/v3/deliveries/252eb21ce7df7328/operator_section/panel.tsv` + `panel.json` | 8-key texture panel + tripwire |
| `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json` | `V3_FOCUS_SONG_LANDS_pending_operator` |
| `data/v3_spine/252eb21ce7df7328/operator_section/…` | intermediate artifacts (rc9_6stem, muscriptor, canonical_midi, merged.mid, render/, tempo_choice.json, all `*_determinism.json`) |
| `tests/test_v3_focus_wig_c20.py` | 12-case suite |
| `scripts/v3_spine/*_wig.py` | 11 per-song sibling scripts |
| `promise_ledger.jsonl` | +4 rows with `-clone-0` suffix |
| `merge_report_c20_clone_0_wig_fork_88d75f9754c3.md` | this file |

## Handoff

- Operator: A/B pair ready to listen at
  `data/v3/deliveries/252eb21ce7df7328/operator_section/{original,reconstruction}_ab_operator_section.wav`.
  When operator has listened to all four c20 focus-song A/Bs plus the c5 CG one
  (5 total), the ≥3/5 accept threshold opens M-V3-FOCUS-1 → M-V3-CORPUS-1.
- Auditor: verify verdict.json SHA, three-way rubric chain, and 12/12 test
  pass on `tests/test_v3_focus_wig_c20.py`.
- Root conductor: pick up this merge report from the workspace root (accessible
  fallback path — see Note above).
