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

Corpus artifacts (downloaded audio, clips, stems) are private research inputs
and must never be committed here — only code, schemas, measurements, and
reports are publishable.
