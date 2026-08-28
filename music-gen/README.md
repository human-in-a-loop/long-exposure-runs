# music-gen

**Status: planning / prompt-framing stage only. No run has been launched.**

This directory holds the framed long-exposure prompt for the Music-Gen
campaign — a transcription-first, rules-extracting pipeline from harvested
audio to deterministic new-song generation, with a trainable 1–7 "ear" and a
professional-DAW (Ableton or Pro Tools) control layer built on the layered
corpus-mining pattern (deterministic floor, agentic ceiling).

- `music_gen_long_exposure_prompt.md` — the campaign prompt: mission, fixed
  design decisions, six tracks, end-to-end pipeline spine, phase/fan-out
  plan, deliverables, success criteria, guardrails, and initial hypotheses.

Before launch this directory will additionally need a
`long-exposure.config.yaml` scoped to it as its `working_directory`
(see `trading-research/<topic>/` for the pattern). Launching requires an
explicit human go-ahead; nothing here authorizes a run.

Corpus artifacts (downloaded audio, clips, stems) are private research inputs
and must never be committed here — only code, schemas, metrics, and reports
are publishable.
