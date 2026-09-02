# v3-Spine: Operator Whitelist → MuScriptor Label Mapping (cycle 3)

Operator semantic categories (per `music_gen_v3_prompt.md` and the 2026-09-02
directive) mapped to MuScriptor's actual `list-instruments` vocabulary.
Probed live via `workspace/learned_transcribers_venv/bin/muscriptor list-instruments`
this cycle; raw vocab pinned in `data/v3_spine/muscriptor_instrument_vocab.json`.

| Operator stem | Operator semantic labels                                        | MuScriptor `--instruments` string used                               | Notes |
|---|---|---|---|
| drums   | `drums`                                                               | `drums`                                                              | 1-to-1. |
| bass    | `electric_bass, acoustic_bass`                                        | `electric_bass,acoustic_bass`                                        | 1-to-1. |
| guitar  | `acoustic_guitar, electric_guitar_clean, electric_guitar_distorted`   | `acoustic_guitar,clean_electric_guitar,distorted_electric_guitar`    | Operator's `electric_guitar_clean`/`_distorted` are MuScriptor's `clean_electric_guitar`/`distorted_electric_guitar` — word-order flipped. Mapped exactly. |
| piano   | `acoustic_piano, electric_piano, organ`                               | `acoustic_piano,electric_piano,organ`                                | 1-to-1. |
| other   | "remaining pitched groups"                                            | `synth_lead,synth_pad,synth_strings,orchestra_hit,chromatic_percussion` | Interpreted `other` as synth+chromatic-perc content, excluding categories already claimed by drums/bass/guitar/piano/vocals. `chromatic_percussion` (marimba/vibes) included as it commonly bleeds into htdemucs `other`. Orchestral categories (`violin`/`cello`/`brass_section`/etc.) NOT included as this is a funk/soul track where they are absent by prior. |
| vocals  | `voice`                                                               | `voice`                                                              | 1-to-1. Symbolic MIDI only (D2 hybrid overlays `vocals.wav` directly at render). |

## MISSING_LABEL findings

None. Every operator semantic label maps to at least one MuScriptor vocab entry.

## Vocab-choice honest disclosure

The **operator vocab** `other = "remaining pitched groups"` is under-specified.
This cycle's interpretation includes `synth_*` + `chromatic_percussion` + `orchestra_hit`
(5 categories). Excluded: the 15 orchestral categories (strings, brass, woodwinds)
and `orchestral_harp`/`timpani`, on the prior that Chicken Grease has none of them.
If the operator prefers to include additional groups in `other`, this is a
one-line change in the WHITELIST table in `scripts/v3_spine/_run_muscriptor_batch.py`.

Empirically this cycle: with this vocab, MuScriptor emitted **zero events** for both
the `other` stem and the `piano` stem's 30 s section (`t=233.6..263.6 s`). The
underlying htdemucs `other.wav` and `piano.wav` therefore either (a) contain
content outside the whitelisted MuScriptor categories, or (b) are too quiet
in this section to cross MuScriptor's threshold. Both stems' JSON output is
the byte-string `[]` (SHA `4f53cda1…202b945`) and their MIDI is a minimal
empty-track container (SHA `b4134d5c…dc75e10b`). This is a **content finding**,
not a nondeterminism finding.
