# music-gen

**Status: planning / prompt-framing stage only. No run has been launched.**

This directory holds the framed prompt for the Music-Gen project: a system
that learns how songs work by taking them apart (harvest → curate → separate
→ transcribe → score → MIDI → DAW) and writes new ones deterministically from
the extracted rules and texture heuristics, judged by a trainable 1–7 "ear."

- `music_gen_long_exposure_prompt.md` — the prompt: intent, fixed decisions,
  the system piece by piece, order of work, definition of done, and conduct
  rules.

Launching requires an explicit human go-ahead plus a run config scoped to
this directory; nothing here authorizes a run.

## Workspace pre-provisioning (before launch)

The run is autonomous, so its tools must be installed and verified in the
workspace ahead of time. All are open source and headless-capable:

- **Ardour** (DAW proper) — with a dummy/headless audio backend configured,
  plus its Lua/OSC control surface enabled.
- **DawDreamer** and **Pedalboard** (Python headless render engines) for the
  automated effect-chain and texture loops.
- **Open plugin palette** — Surge XT, Vital, Dexed, sfizz (with soundfonts),
  LSP, x42, Calf (LV2/VST3 builds).
- **MuseScore** (headless-capable CLI mode) for the score bridge.
- **Audio/ML tooling** — ffmpeg, a playlist harvester, source-separation and
  transcription packages per the survey, plus Python audio stack (librosa,
  pretty_midi, mido, soundfile, etc.).
- A smoke-test script proving the chain MIDI → session → effects → rendered
  audio runs unattended in the workspace. Green smoke test is a launch
  precondition.

This is now implemented in `workspace/`: run `workspace/provision.sh`, then
`workspace/smoke_test.py` (all stages must PASS). See
`workspace/PROVISIONING_REPORT.md` for the verified install (2026-08-28,
Ubuntu 24.04: all 14 smoke stages green) and known gaps.

Corpus artifacts (downloaded audio, clips, stems) are private research inputs
and must never be committed here — only code, schemas, measurements, and
reports are publishable.
