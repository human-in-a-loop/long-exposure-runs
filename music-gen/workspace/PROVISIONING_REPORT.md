# Workspace provisioning report — 2026-08-28

Environment: Ubuntu 24.04.4 LTS, Python 3.11, 4 CPU cores, no GPU.
Provisioned via `provision.sh`; verified via `smoke_test.py` —
**all 14 smoke stages PASS** (no partials, no failures).

## Installed and verified

| Component | Version | Role | Smoke evidence |
|---|---|---|---|
| Ardour | 8.4.0 (apt) | DAW proper | headless session created on disk via `ardour8-new_empty_session`; `ardour8-lua`, `ardour8-export`, `ardour8-new_session` all shipped |
| DawDreamer | 0.9.0 (pip) | headless render engine | rendered test MIDI through Surge XT VST3, 9 s audio, peak 0.45 |
| Pedalboard | 0.9.24 (pip) | effect chains in Python | compressor→reverb→gain→limiter chain applied; external VST3 ("Surge XT Effects") loads |
| Surge XT | 1.3.4 (official .deb) | wavetable/hybrid synth (VST3 + LV2) | drove the DawDreamer render |
| Dexed | 1.0.1 (official build) | FM (DX7) synth (VST3 + CLAP) | installed to /usr/lib/vst3, /usr/lib/clap |
| sfizz | 1.2.3 (source build) | SFZ sampler, `sfizz_render` CLI | rendered test MIDI through a synthetic SFZ instrument, 8.7 s audio |
| fluidsynth + FluidR3 GM | 2.3.4 (apt) | SF2 sampler / quick MIDI render | rendered test MIDI to 10.8 s WAV |
| MuseScore | 3.2.3 (apt) | score bridge | headless (QT_QPA_PLATFORM=offscreen) MIDI→MusicXML→MIDI round trip, notes preserved |
| ffmpeg | 6.1.1 (apt) | transcode/media | WAV→MP3 transcode |
| LV2 plugin palette | apt suites | effects/instruments | 382 LV2 plugins visible to hosts: Calf, LSP, x42, Surge, Dragonfly Reverb, AVL Drums, DPF, amsynth, ZynAddSubFX, synthv1/samplv1/drumkv1 |
| librosa | 0.11.0 (pip) | analysis / texture panel | mel-distance + RMS-envelope + tempo computed on rendered audio |
| demucs | 4.1.0 (pip, torch 2.13 CPU) | source separation | htdemucs weights downloaded and cached; 2-stem separation ran on synthetic mix |
| basic-pitch | 0.4.0 (pip, TF 2.15) | transcription baseline | transcribed 32 notes from the fluidsynth render |
| pretty_midi / mido / soundfile | pip | MIDI + audio I/O | authored the test MIDI; read/wrote all WAVs |
| yt-dlp | 2026.08.19 (pip) | playlist harvester | version/import check only — no YouTube fetch performed |

## Smoke chain proven end to end

MIDI authored → MuseScore score round trip → synth render (three independent
paths: fluidsynth/SF2, DawDreamer+Surge XT/VST3, sfizz/SFZ) → Pedalboard
effect chain → librosa texture-panel measurement → ffmpeg transcode, plus
Ardour session creation, demucs separation, and basic-pitch transcription.
All unattended, no display, no license prompts.

## Gaps and notes

- **Vital/Vitalium: not installed.** Not packaged in Ubuntu 24.04; upstream
  Vital binaries sit behind an account wall, and Vitalium ships via
  third-party repos or a DISTRHO-Ports source build. Surge XT covers the
  wavetable-synth role for now; treat Vitalium as an optional launch-time
  build if wanted.
- **sfizz plugins (LV2/VST3) not built** — the 1.2.3 library tarball builds
  `libsfizz` + `sfizz_render` only; plugin bundles live in a separate
  upstream repo. `sfizz_render` is the piece the autonomous pipeline needs.
- **GitHub release downloads through this workspace's proxy**: release-asset
  URLs (`github.com/<owner>/<repo>/releases/download/...`) pass through;
  GitHub's HTML and REST API do not. `provision.sh` therefore pins exact
  versions and asset filenames rather than querying "latest".
- **mscore3 needs `QT_QPA_PLATFORM=offscreen`** (it aborts without a
  display otherwise); smoke test and any pipeline code must set it.
- **JACK is not running** (no audio hardware in the container). Everything
  above renders offline/freewheeling, which is the intended mode for the
  autonomous run; Ardour's realtime audition paths are untested and unneeded.
- **This container is ephemeral.** The installation itself will not survive
  the session — `provision.sh` + a green `smoke_test.py` is the repeatable
  recipe, and re-running both is the launch precondition.
