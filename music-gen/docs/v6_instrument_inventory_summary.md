# Instrument sources — Phase 4 (instrument realism)

Inventory: `workspace/instruments/INVENTORY.json` — 40 libraries, 172 playable entries, 0 rejected.

Disk used by `workspace/instruments/` (incl. `_renders/`): **2.75 GB** (downloaded libraries 2.49 GB; renders 429 MB).

Backends: `sfizz_render 1.2.3` (.sfz), `fluidsynth 2.3.4` (.sf2), `dawdreamer 0.9.0` (Surge XT 1.3.4 / Dexed 1.0.1 VST3).
Test render: 4 bars @ 100 BPM, 3 velocity tiers, role register (see `scripts/v6/render_patch_test.py`).

## Role -> available options

| role | n | library | instrument | backend | license | RMS dBFS |
|---|---|---|---|---|---|---|
| piano | 12 | salamander_grand_piano | Salamander Grand Piano V3 | sfz | CC-BY-3.0 | -31.84 |
|  |  | salamander_grand_piano | Salamander Grand Piano V3 (retuned) | sfz | CC-BY-3.0 | -31.89 |
|  |  | upright_piano_kw | Upright Piano KW | sfz | CC0-1.0 | -28.67 |
|  |  | old_piano_fb | Old Piano FB (honky-tonk) | sfz | CC0-1.0 | -27.26 |
|  |  | freepats_gm | Piano [0:0] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -24.38 |
|  |  | freepats_gm | Bright Piano [0:1] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -24.72 |
|  |  | musescore_general | Grand Piano [0:0] | sf2 | MIT | -30.57 |
|  |  | musescore_general | Bright Grand Piano [0:1] | sf2 | MIT | -31.18 |
|  |  | generaluser_gs | Grand Piano [0:0] | sf2 | GeneralUser-GS-License-2.0 | -29.02 |
|  |  | generaluser_gs | Bright Grand Piano [0:1] | sf2 | GeneralUser-GS-License-2.0 | -29.29 |
|  |  | fluidr3_gm | Yamaha Grand Piano [0:0] | sf2 | MIT | -27.86 |
|  |  | fluidr3_gm | Bright Yamaha Grand [0:1] | sf2 | MIT | -28.33 |
| electric_piano | 15 | fm_piano1 | FM Piano 1 (DX7-style) | sfz | CC0-1.0 | -23.58 |
|  |  | fm_piano2 | FM Piano 2 (DX7-style) | sfz | CC0-1.0 | -26.37 |
|  |  | freepats_gm | Electric Piano 1 [0:4] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -21.73 |
|  |  | freepats_gm | Electric Piano 2 [0:5] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -23.71 |
|  |  | musescore_general | Tine Electric Piano [0:4] | sf2 | MIT | -24.96 |
|  |  | musescore_general | FM Electric Piano [0:5] | sf2 | MIT | -29.18 |
|  |  | generaluser_gs | Tine Electric Piano [0:4] | sf2 | GeneralUser-GS-License-2.0 | -27.31 |
|  |  | generaluser_gs | FM Electric Piano [0:5] | sf2 | GeneralUser-GS-License-2.0 | -32.17 |
|  |  | fluidr3_gm | Rhodes EP [0:4] | sf2 | MIT | -23.11 |
|  |  | fluidr3_gm | Legend EP 2 [0:5] | sf2 | MIT | -26.77 |
|  |  | surge_xt | Surge XT: DX EP | dawdreamer | GPL-3.0-only | -21.48 |
|  |  | surge_xt | Surge XT: Soft Suitcase | dawdreamer | GPL-3.0-only | -19.34 |
|  |  | surge_xt | Surge XT: EP 1 | dawdreamer | GPL-3.0-only | -22.24 |
|  |  | dexed | Dexed: Chroma 5 Y [4] | dawdreamer | GPL-3.0-only | -21.38 |
|  |  | dexed | Dexed: FLEXI    4 [15] | dawdreamer | GPL-3.0-only | -20.17 |
| organ | 16 | drawbar_organ_emulation | Drawbar Organ Emulation | sfz | CC0-1.0 | -24.2 |
|  |  | percussive_organ_emulation | Percussive Organ Emulation | sfz | CC0-1.0 | -21.22 |
|  |  | rock_organ_emulation | Rock Organ Emulation | sfz | CC0-1.0 | -22.93 |
|  |  | freepats_gm | Drawbar Organ [0:16] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -21.73 |
|  |  | freepats_gm | Percussive Organ [0:17] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -21.67 |
|  |  | freepats_gm | Rock Organ [0:18] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -23.83 |
|  |  | musescore_general | Drawbar Organ [0:16] | sf2 | MIT | -26.74 |
|  |  | musescore_general | Percussive Organ [0:17] | sf2 | MIT | -24.0 |
|  |  | musescore_general | Rock Organ [0:18] | sf2 | MIT | -26.01 |
|  |  | generaluser_gs | Tonewheel Organ [0:16] | sf2 | GeneralUser-GS-License-2.0 | -28.18 |
|  |  | generaluser_gs | Percussive Organ [0:17] | sf2 | GeneralUser-GS-License-2.0 | -27.18 |
|  |  | generaluser_gs | Rock Organ [0:18] | sf2 | GeneralUser-GS-License-2.0 | -27.38 |
|  |  | fluidr3_gm | DrawbarOrgan [0:16] | sf2 | MIT | -24.06 |
|  |  | fluidr3_gm | Percussive Organ [0:17] | sf2 | MIT | -22.59 |
|  |  | fluidr3_gm | Rock Organ [0:18] | sf2 | MIT | -22.54 |
|  |  | surge_xt | Surge XT: Organ 1 | dawdreamer | GPL-3.0-only | -19.84 |
| electric_bass | 9 | finger_bass_yr | Finger Bass YR | sfz | CC0-1.0 | -25.73 |
|  |  | picked_bass_yr | Picked Bass YR | sfz | CC0-1.0 | -28.13 |
|  |  | freepats_gm | Electric Bass 1 [0:33] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -19.57 |
|  |  | musescore_general | Fingered Bass [0:33] | sf2 | MIT | -24.15 |
|  |  | musescore_general | Picked Bass [0:34] | sf2 | MIT | -24.67 |
|  |  | generaluser_gs | Finger Bass [0:33] | sf2 | GeneralUser-GS-License-2.0 | -25.15 |
|  |  | generaluser_gs | Pick Bass [0:34] | sf2 | GeneralUser-GS-License-2.0 | -28.69 |
|  |  | fluidr3_gm | Fingered Bass [0:33] | sf2 | MIT | -24.65 |
|  |  | fluidr3_gm | Picked Bass [0:34] | sf2 | MIT | -25.18 |
| acoustic_bass | 3 | musescore_general | Acoustic Bass [0:32] | sf2 | MIT | -22.62 |
|  |  | generaluser_gs | Acoustic Bass [0:32] | sf2 | GeneralUser-GS-License-2.0 | -24.64 |
|  |  | fluidr3_gm | Acoustic Bass [0:32] | sf2 | MIT | -23.2 |
| synth_bass | 16 | lately_bass | Lately Bass | sfz | CC0-1.0 | -23.52 |
|  |  | synth_bass_1 | Synth Bass 1 | sfz | CC0-1.0 | -26.45 |
|  |  | synth_bass_2 | Synth Bass 2 | sfz | CC0-1.0 | -23.24 |
|  |  | freepats_gm | Synth Bass 1 [0:38] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -24.1 |
|  |  | freepats_gm | Synth Bass 2 [0:39] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -20.88 |
|  |  | musescore_general | Synth Bass 1 [0:38] | sf2 | MIT | -25.36 |
|  |  | musescore_general | Synth Bass 2 [0:39] | sf2 | MIT | -25.55 |
|  |  | generaluser_gs | Synth Bass 1 [0:38] | sf2 | GeneralUser-GS-License-2.0 | -25.52 |
|  |  | generaluser_gs | Synth Bass 2 [0:39] | sf2 | GeneralUser-GS-License-2.0 | -26.76 |
|  |  | fluidr3_gm | Synth Bass 1 [0:38] | sf2 | MIT | -24.42 |
|  |  | fluidr3_gm | Synth Bass 2 [0:39] | sf2 | MIT | -18.08 |
|  |  | surge_xt | Surge XT: Fingered | dawdreamer | GPL-3.0-only | -22.61 |
|  |  | surge_xt | Surge XT: Bass 1 | dawdreamer | GPL-3.0-only | -16.39 |
|  |  | surge_xt | Surge XT: E-Bass | dawdreamer | GPL-3.0-only | -21.51 |
|  |  | dexed | Dexed: Thunder  3 [11] | dawdreamer | GPL-3.0-only | -17.82 |
|  |  | dexed | Dexed: PHAROH [3] | dawdreamer | GPL-3.0-only | -20.59 |
| electric_guitar | 15 | eguitar_fsbs_clean | EGuitar FSBS clean (bridge) | sfz | CC0-1.0 | -25.3 |
|  |  | eguitar_fsbs_direct | EGuitar FSBS direct (DI) | sfz | CC0-1.0 | -25.81 |
|  |  | eguitar_fsbs_jazz | EGuitar FSBS jazz tone | sfz | CC0-1.0 | -23.23 |
|  |  | freepats_gm | E. Guitar Jazz [0:26] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -21.13 |
|  |  | freepats_gm | E. Guitar Clean [0:27] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -22.34 |
|  |  | freepats_gm | E. Guitar Muted [0:28] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -29.69 |
|  |  | musescore_general | Jazz Guitar [0:26] | sf2 | MIT | -27.97 |
|  |  | musescore_general | Clean Guitar [0:27] | sf2 | MIT | -22.33 |
|  |  | musescore_general | Palm Muted Guitar [0:28] | sf2 | MIT | -28.33 |
|  |  | generaluser_gs | Jazz Guitar [0:26] | sf2 | GeneralUser-GS-License-2.0 | -25.81 |
|  |  | generaluser_gs | Clean Guitar [0:27] | sf2 | GeneralUser-GS-License-2.0 | -30.23 |
|  |  | generaluser_gs | Muted Guitar [0:28] | sf2 | GeneralUser-GS-License-2.0 | -31.7 |
|  |  | fluidr3_gm | Jazz Guitar [0:26] | sf2 | MIT | -23.79 |
|  |  | fluidr3_gm | Clean Guitar [0:27] | sf2 | MIT | -22.92 |
|  |  | fluidr3_gm | Palm Muted Guitar [0:28] | sf2 | MIT | -28.87 |
| acoustic_guitar | 10 | spanish_classical_guitar | Spanish Classical Guitar (nylon) | sfz | CC0-1.0 | -26.21 |
|  |  | fss_steel_string_guitar | FSS Steel String Guitar | sfz | GPL-3.0-or-later WITH FreePats-sample-exception | -21.73 |
|  |  | freepats_gm | Nylon-String Guitar [0:24] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -23.68 |
|  |  | freepats_gm | Steel-String Guitar [0:25] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -19.26 |
|  |  | musescore_general | Nylon String Guitar [0:24] | sf2 | MIT | -26.07 |
|  |  | musescore_general | Steel String Guitar [0:25] | sf2 | MIT | -29.56 |
|  |  | generaluser_gs | Nylon Guitar [0:24] | sf2 | GeneralUser-GS-License-2.0 | -28.21 |
|  |  | generaluser_gs | Steel Guitar [0:25] | sf2 | GeneralUser-GS-License-2.0 | -30.79 |
|  |  | fluidr3_gm | Nylon String Guitar [0:24] | sf2 | MIT | -22.56 |
|  |  | fluidr3_gm | Steel String Guitar [0:25] | sf2 | MIT | -27.07 |
| drums | 23 | muldjord_kit | Muldjord Kit (rock, stereo) | sfz | CC-BY-4.0 | -44.32 |
|  |  | salamander_drumkit | Salamander Drumkit (OH mics) | sfz | CC-BY-SA-3.0 | -42.29 |
|  |  | freepats_gm | Percussion [128:0] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -28.7 |
|  |  | musescore_general | Standard [128:0] | sf2 | MIT | -28.27 |
|  |  | musescore_general | Room [128:8] | sf2 | MIT | -25.87 |
|  |  | musescore_general | Power [128:16] | sf2 | MIT | -24.71 |
|  |  | musescore_general | Jazz [128:32] | sf2 | MIT | -24.61 |
|  |  | musescore_general | Brush [128:40] | sf2 | MIT | -24.95 |
|  |  | generaluser_gs | Standard 1 [128:0] | sf2 | GeneralUser-GS-License-2.0 | -31.73 |
|  |  | generaluser_gs | Room [128:8] | sf2 | GeneralUser-GS-License-2.0 | -32.97 |
|  |  | generaluser_gs | Power [128:16] | sf2 | GeneralUser-GS-License-2.0 | -29.95 |
|  |  | generaluser_gs | Jazz [128:32] | sf2 | GeneralUser-GS-License-2.0 | -31.93 |
|  |  | generaluser_gs | Brush [128:40] | sf2 | GeneralUser-GS-License-2.0 | -32.56 |
|  |  | fluidr3_gm | Standard [128:0] | sf2 | MIT | -31.1 |
|  |  | fluidr3_gm | Room [128:8] | sf2 | MIT | -29.42 |
|  |  | fluidr3_gm | Power [128:16] | sf2 | MIT | -25.77 |
|  |  | fluidr3_gm | Jazz [128:32] | sf2 | MIT | -28.23 |
|  |  | fluidr3_gm | Brush [128:40] | sf2 | MIT | -28.76 |
|  |  | avl_drumkits_sf2 | AVL Black Pearl 4pc | sf2 | CC-BY-SA-3.0 | -26.78 |
|  |  | avl_drumkits_sf2 | AVL Red Zeppelin 4pc | sf2 | CC-BY-SA-3.0 | -26.93 |
|  |  | avl_drumkits_sf2 | AVL Blonde Bop | sf2 | CC-BY-SA-3.0 | -27.26 |
|  |  | avl_drumkits_sf2 | AVL Blonde Bop HR | sf2 | CC-BY-SA-3.0 | -27.91 |
|  |  | avl_drumkits_sf2 | AVL Buskmans Holiday | sf2 | CC-BY-SA-3.0 | -30.51 |
| pad | 19 | new_age_pad | New Age Pad | sfz | CC0-1.0 | -24.23 |
|  |  | sweep_pad | Sweep Pad | sfz | CC0-1.0 | -21.77 |
|  |  | synth_pad_bowed | Synth Pad Bowed | sfz | CC0-1.0 | -22.76 |
|  |  | synth_pad_choir | Synth Pad Choir | sfz | CC0-1.0 | -22.1 |
|  |  | freepats_gm | Synth New Age [0:88] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -21.37 |
|  |  | freepats_gm | Synth Pad Choir [0:91] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -19.43 |
|  |  | musescore_general | Fantasia [0:88] | sf2 | MIT | -26.26 |
|  |  | musescore_general | Warm Pad [0:89] | sf2 | MIT | -28.13 |
|  |  | musescore_general | Space Voice [0:91] | sf2 | MIT | -22.75 |
|  |  | generaluser_gs | Fantasia [0:88] | sf2 | GeneralUser-GS-License-2.0 | -24.34 |
|  |  | generaluser_gs | Warm Pad [0:89] | sf2 | GeneralUser-GS-License-2.0 | -25.06 |
|  |  | generaluser_gs | Space Voice [0:91] | sf2 | GeneralUser-GS-License-2.0 | -31.67 |
|  |  | fluidr3_gm | Fantasia [0:88] | sf2 | MIT | -29.81 |
|  |  | fluidr3_gm | Warm Pad [0:89] | sf2 | MIT | -19.71 |
|  |  | fluidr3_gm | Space Voice [0:91] | sf2 | MIT | -21.96 |
|  |  | surge_xt | Surge XT: Pad 1 | dawdreamer | GPL-3.0-only | -22.56 |
|  |  | surge_xt | Surge XT: MKS-70 Warm Pad | dawdreamer | GPL-3.0-only | -21.95 |
|  |  | dexed | Dexed: Slow3D Pad [30] | dawdreamer | GPL-3.0-only | -15.44 |
|  |  | dexed | Dexed: OB GenvivY [7] | dawdreamer | GPL-3.0-only | -20.86 |
| strings_pad | 9 | synth_strings_1 | Synth Strings 1 | sfz | CC0-1.0 | -22.64 |
|  |  | synth_strings_2 | Synth Strings 2 | sfz | CC0-1.0 | -24.76 |
|  |  | musescore_general | Strings Fast [0:48] | sf2 | MIT | -23.46 |
|  |  | musescore_general | Strings Slow [0:49] | sf2 | MIT | -23.49 |
|  |  | generaluser_gs | Fast Strings [0:48] | sf2 | GeneralUser-GS-License-2.0 | -24.43 |
|  |  | generaluser_gs | Slow Strings [0:49] | sf2 | GeneralUser-GS-License-2.0 | -24.73 |
|  |  | fluidr3_gm | Strings [0:48] | sf2 | MIT | -22.22 |
|  |  | fluidr3_gm | Slow Strings [0:49] | sf2 | MIT | -20.4 |
|  |  | surge_xt | Surge XT: Subtle Comb Strings | dawdreamer | GPL-3.0-only | -20.35 |
| lead | 15 | synth_bass_lead | Synth Bass+Lead | sfz | CC0-1.0 | -27.12 |
|  |  | synth_square | Synth Square Lead | sfz | CC0-1.0 | -25.14 |
|  |  | synth_fifths | Synth Fifths Lead | sfz | CC0-1.0 | -28.62 |
|  |  | synth_calliope | Synth Calliope Lead | sfz | CC0-1.0 | -22.44 |
|  |  | freepats_gm | Synth Square [0:80] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -22.82 |
|  |  | musescore_general | Square Lead [0:80] | sf2 | MIT | -27.36 |
|  |  | musescore_general | Saw Lead [0:81] | sf2 | MIT | -26.81 |
|  |  | generaluser_gs | Square Lead [0:80] | sf2 | GeneralUser-GS-License-2.0 | -29.96 |
|  |  | generaluser_gs | Saw Lead [0:81] | sf2 | GeneralUser-GS-License-2.0 | -29.22 |
|  |  | fluidr3_gm | Square Lead [0:80] | sf2 | MIT | -24.35 |
|  |  | fluidr3_gm | Saw Wave [0:81] | sf2 | MIT | -27.78 |
|  |  | surge_xt | Surge XT: Classic Lead 1 | dawdreamer | GPL-3.0-only | -13.52 |
|  |  | surge_xt | Surge XT: Crisp PWM | dawdreamer | GPL-3.0-only | -23.54 |
|  |  | dexed | Dexed: SAW EM UP [8] | dawdreamer | GPL-3.0-only | -20.02 |
|  |  | dexed | Dexed: LAURIE [1] | dawdreamer | GPL-3.0-only | -22.29 |
| brass | 9 | synth_brass_1 | Synth Brass 1 | sfz | CC0-1.0 | -20.33 |
|  |  | synth_brass_2 | Synth Brass 2 | sfz | CC0-1.0 | -18.99 |
|  |  | freepats_gm | Synth Brass 1 [0:62] | sf2 | GPL-3.0-or-later WITH FreePats-sample-exception | -17.96 |
|  |  | musescore_general | Brass Section [0:61] | sf2 | MIT | -24.72 |
|  |  | musescore_general | Synth Brass 1 [0:62] | sf2 | MIT | -25.38 |
|  |  | generaluser_gs | Brass Section [0:61] | sf2 | GeneralUser-GS-License-2.0 | -25.65 |
|  |  | generaluser_gs | Synth Brass 1 [0:62] | sf2 | GeneralUser-GS-License-2.0 | -27.54 |
|  |  | fluidr3_gm | Brass Section [0:61] | sf2 | MIT | -23.18 |
|  |  | fluidr3_gm | Synth Brass 1 [0:62] | sf2 | MIT | -20.58 |
| percussion | 1 | world_percussion | World Percussion | sfz | CC0-1.0 | -33.68 |

## Libraries

| slug | format | size MB | license | source |
|---|---|---|---|---|
| salamander_grand_piano | sfz | 746.9 | [CC-BY-3.0](https://creativecommons.org/licenses/by/3.0/) | https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SFZ+FLAC-V3+20200602.tar.gz |
| upright_piano_kw | sfz | 33.9 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://freepats.zenvoid.org/Piano/UprightPianoKW/UprightPianoKW-SFZ+FLAC-20220221.7z |
| old_piano_fb | sfz | 6.7 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/old-piano-FB/releases/download/2020-04-01/PianoFB-small-SFZ+FLAC-20200401.7z |
| fm_piano1 | sfz | 25.3 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/fm-piano1/releases/download/2019-09-16/FM-Piano1-SFZ+FLAC-20190916.7z |
| fm_piano2 | sfz | 9.2 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/fm-piano2/releases/download/2016-11-12/FM-Piano2-SFZ+FLAC-20161112.7z |
| finger_bass_yr | sfz | 3.4 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/electric-bass-YR/releases/download/2019-09-30/FingerBassYR-SFZ+FLAC-20190930.7z |
| picked_bass_yr | sfz | 2.9 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/electric-bass-YR/releases/download/2019-09-30/PickedBassYR-SFZ+FLAC-20190930.7z |
| lately_bass | sfz | 1.3 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/lately-bass/releases/download/2024-04-09/LatelyBass-SFZ+FLAC-20240409.7z |
| synth_bass_1 | sfz | 1.0 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-bass-1/releases/download/2019-07-23/SynthBass1-SFZ+FLAC-20190723.7z |
| synth_bass_2 | sfz | 2.8 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-bass-2/releases/download/2021-04-05/SynthBass2-SFZ+FLAC-20210405.7z |
| synth_bass_lead | sfz | 4.2 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-bass-lead/releases/download/2020-05-22/SynthBassLead-SFZ+FLAC-20200522.7z |
| eguitar_fsbs_clean | sfz | 129.4 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/electric-guitar-FSBS-clean/releases/download/2026-08-07/EGuitarFSBS-clean-SFZ+FLAC-20260807.7z |
| eguitar_fsbs_direct | sfz | 78.6 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/electric-guitar-FSBS-direct/releases/download/2022-09-11/EGuitarFSBS-direct-SFZ+FLAC-20220911.7z |
| eguitar_fsbs_jazz | sfz | 67.7 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/electric-guitar-FSBS-jazz/releases/download/2026-08-07/EGuitarFSBS-jazz-SFZ+FLAC-20260807.7z |
| spanish_classical_guitar | sfz | 5.3 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://freepats.zenvoid.org/Guitar/SpanishClassicalGuitar/SpanishClassicalGuitar-SFZ+FLAC-20190618.7z |
| fss_steel_string_guitar | sfz | 26.4 | [GPL-3.0-or-later WITH FreePats-sample-exception](https://freepats.zenvoid.org/licenses.html#GPL_exception) | https://freepats.zenvoid.org/Guitar/FSS-SteelStringGuitar/FSS-SteelStringGuitar-SFZ-20200521.tar.xz |
| drawbar_organ_emulation | sfz | 6.5 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://freepats.zenvoid.org/Organ/DrawbarOrganEmulation/DrawbarOrganEmulation-SFZ-20190712.tar.xz |
| percussive_organ_emulation | sfz | 14.5 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://freepats.zenvoid.org/Organ/PercussiveOrganEmulation/PercussiveOrganEmulation-SFZ-20190715.tar.xz |
| rock_organ_emulation | sfz | 13.6 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://freepats.zenvoid.org/Organ/RockOrganEmulation/RockOrganEmulation-SFZ-20190715.tar.xz |
| muldjord_kit | sfz | 168.1 | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) | https://github.com/freepats/muldjordkit/releases/download/2020-10-18/MuldjordKit-SFZ+FLAC-20201018.7z |
| salamander_drumkit | sfz | 502.0 | [CC-BY-SA-3.0](https://creativecommons.org/licenses/by-sa/3.0/) | https://archive.org/download/SalamanderDrumkit/salamanderDrumkit.tar.bz2 |
| new_age_pad | sfz | 4.6 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/new-age/releases/download/2019-07-30/NewAge-SFZ+FLAC-20190730.7z |
| sweep_pad | sfz | 3.1 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/sweep-pad/releases/download/2019-08-13/SweepPad-SFZ+FLAC-20190813.7z |
| synth_pad_bowed | sfz | 12.2 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-pad-bowed/releases/download/2019-07-19/SynthPadBowed-SFZ+FLAC-20190719.7z |
| synth_pad_choir | sfz | 6.9 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-pad-choir/releases/download/2020-05-16/SynthPadChoir-SFZ+FLAC-20200516.7z |
| synth_strings_1 | sfz | 3.9 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-strings-1/releases/download/2020-05-28/SynthStrings1-SFZ+FLAC-20200528.7z |
| synth_strings_2 | sfz | 5.9 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-strings-2/releases/download/2020-05-28/SynthStrings2-SFZ+FLAC-20200528.7z |
| synth_square | sfz | 7.4 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-square/releases/download/2020-05-12/SynthSquare-SFZ+FLAC-20200512.7z |
| synth_fifths | sfz | 8.1 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-fifths/releases/download/2020-05-19/SynthFifths-SFZ+FLAC-20200519.7z |
| synth_calliope | sfz | 3.8 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-calliope/releases/download/2020-05-12/SynthCalliope-SFZ+FLAC-20200512.7z |
| synth_brass_1 | sfz | 3.2 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-brass-1/releases/download/2021-04-26/SynthBrass1-SFZ+FLAC-20210426.7z |
| synth_brass_2 | sfz | 2.1 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/synth-brass-2/releases/download/2024-06-10/SynthBrass2-SFZ+FLAC-20240610.7z |
| world_percussion | sfz | 8.6 | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | https://github.com/freepats/world-percussion/releases/download/2020-09-05/WorldPercussion-SFZ+FLAC-20200905.7z |
| freepats_gm | sf2 | 322.2 | [GPL-3.0-or-later WITH FreePats-sample-exception](https://freepats.zenvoid.org/licenses.html#GPL_exception) | https://freepats.zenvoid.org/SoundSets/FreePats-GeneralMIDI/FreePatsGM-SF2-20221026.7z |
| musescore_general | sf2 | 215.6 | [MIT](https://opensource.org/licenses/MIT) | https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf2 |
| generaluser_gs | sf2 | 32.3 | [GeneralUser-GS-License-2.0](https://www.schristiancollins.com/generaluser.php) | https://archive.org/download/general-user-gs-v-2.0.2-doc-r-4/GeneralUser_GS_v2.0.2--doc_r4.zip |
| fluidr3_gm | sf2 | 148.4 | [MIT](https://opensource.org/licenses/MIT) | (preinstalled: Debian fluid-soundfont-gm) |
| avl_drumkits_sf2 | sf2 | 152.3 | [CC-BY-SA-3.0](https://creativecommons.org/licenses/by-sa/3.0/) | (preinstalled: Debian avldrums.lv2 / x42 AVL Drumkits sf2 export) |
| surge_xt | dawdreamer | 0.0 | [GPL-3.0-only](https://github.com/surge-synthesizer/surge/blob/main/LICENSE) | (preinstalled: Surge XT 1.3.4 VST3 + /usr/share/surge-xt/patches_factory) |
| dexed | dawdreamer | 0.0 | [GPL-3.0-only](https://github.com/asb2m10/dexed/blob/master/LICENSE) | (preinstalled: Dexed 1.0.1 VST3, default cartridge) |

## Rejected entries (silent or render error)

none

## Recommended default patch pool per role

Priority order; the generator should sample from these per song (first two are the realistic 'A/B' pair).

- **piano**: `salamander_grand_piano` / Salamander Grand Piano V3 (sfz); `upright_piano_kw` / Upright Piano KW (sfz); `generaluser_gs` / Grand Piano [0:0] (sf2); `old_piano_fb` / Old Piano FB (honky-tonk) (sfz)
- **electric_piano**: `fm_piano1` / FM Piano 1 (DX7-style) (sfz); `musescore_general` / Tine Electric Piano [0:4] (sf2); `surge_xt` / Surge XT: Soft Suitcase (dawdreamer); `surge_xt` / Surge XT: DX EP (dawdreamer); `fm_piano2` / FM Piano 2 (DX7-style) (sfz)
- **organ**: `drawbar_organ_emulation` / Drawbar Organ Emulation (sfz); `percussive_organ_emulation` / Percussive Organ Emulation (sfz); `rock_organ_emulation` / Rock Organ Emulation (sfz)
- **electric_bass**: `finger_bass_yr` / Finger Bass YR (sfz); `picked_bass_yr` / Picked Bass YR (sfz); `generaluser_gs` / Finger Bass [0:33] (sf2); `generaluser_gs` / Pick Bass [0:34] (sf2); `musescore_general` / Fingered Bass [0:33] (sf2)
- **acoustic_bass**: `generaluser_gs` / Acoustic Bass [0:32] (sf2); `musescore_general` / Acoustic Bass [0:32] (sf2)
- **synth_bass**: `lately_bass` / Lately Bass (sfz); `synth_bass_1` / Synth Bass 1 (sfz); `surge_xt` / Surge XT: Fingered (dawdreamer); `dexed` / Dexed: Thunder  3 [11] (dawdreamer)
- **electric_guitar**: `eguitar_fsbs_clean` / EGuitar FSBS clean (bridge) (sfz); `eguitar_fsbs_jazz` / EGuitar FSBS jazz tone (sfz); `eguitar_fsbs_direct` / EGuitar FSBS direct (DI) (sfz); `generaluser_gs` / Muted Guitar [0:28] (sf2); `musescore_general` / Palm Muted Guitar [0:28] (sf2); `generaluser_gs` / Clean Guitar [0:27] (sf2)
- **acoustic_guitar**: `spanish_classical_guitar` / Spanish Classical Guitar (nylon) (sfz); `fss_steel_string_guitar` / FSS Steel String Guitar (sfz); `generaluser_gs` / Nylon Guitar [0:24] (sf2); `generaluser_gs` / Steel Guitar [0:25] (sf2)
- **drums**: `salamander_drumkit` / Salamander Drumkit (OH mics) (sfz); `muldjord_kit` / Muldjord Kit (rock, stereo) (sfz); `avl_drumkits_sf2` / AVL Black Pearl 4pc (sf2); `avl_drumkits_sf2` / AVL Blonde Bop HR (sf2); `generaluser_gs` / Brush [128:40] (sf2); `generaluser_gs` / Room [128:8] (sf2); `musescore_general` / Jazz [128:32] (sf2); `generaluser_gs` / Standard 1 [128:0] (sf2)
- **pad**: `new_age_pad` / New Age Pad (sfz); `synth_pad_bowed` / Synth Pad Bowed (sfz); `synth_pad_choir` / Synth Pad Choir (sfz); `surge_xt` / Surge XT: Pad 1 (dawdreamer); `surge_xt` / Surge XT: MKS-70 Warm Pad (dawdreamer); `dexed` / Dexed: Slow3D Pad [30] (dawdreamer); `generaluser_gs` / Warm Pad [0:89] (sf2)
- **strings_pad**: `synth_strings_1` / Synth Strings 1 (sfz); `synth_strings_2` / Synth Strings 2 (sfz); `musescore_general` / Strings Fast [0:48] (sf2); `surge_xt` / Surge XT: Subtle Comb Strings (dawdreamer)
- **lead**: `synth_square` / Synth Square Lead (sfz); `synth_fifths` / Synth Fifths Lead (sfz); `synth_calliope` / Synth Calliope Lead (sfz); `surge_xt` / Surge XT: Classic Lead 1 (dawdreamer); `surge_xt` / Surge XT: Crisp PWM (dawdreamer); `dexed` / Dexed: SAW EM UP [8] (dawdreamer)
- **brass**: `generaluser_gs` / Brass Section [0:61] (sf2); `musescore_general` / Brass Section [0:61] (sf2); `synth_brass_1` / Synth Brass 1 (sfz); `synth_brass_2` / Synth Brass 2 (sfz)
- **percussion**: `world_percussion` / World Percussion (sfz)

## Not sourced / caveats

- **Determinism**: `sfizz_render` and `fluidsynth` renders are byte-identical across runs *when the sfz is loaded through the generated `*.ram.sfz` wrapper* (`<control> hint_ram_based=1`). Without it, sfizz streams long one-shot tails from disk in a background thread and 1 of 3 renders of the Salamander Drumkit differed (max |diff| 0.008, 9.5% of samples, starting at 1.67 s). Surge XT and Dexed via DawDreamer are **not** bit-deterministic (both differed between two identical renders); treat the `dawdreamer` backend as audition-only or freeze its output once per song.
- **Not sourced**: Karoryfer (Meatbass, Black and Green) — the freebies page routes through a shop/checkout flow, no direct asset URLs; sfzinstruments GitHub repos (SalamanderDrumkit, karoryfer.*, jlearman.*) — github.com HTML/codeload/API all return 403 through the proxy, and `add_repo` has no access to that org (the Salamander Drumkit was taken from archive.org instead); VSCO-2 Community Edition — vis.versilstudios.com fails TLS through the proxy and the set is ~3 GB; Virtual Playing Orchestra — skipped (size); Timbres of Heaven / Arachno — hosts not probed after the budget was met, and both have redistribution-restricted licenses; HuggingFace mirrors (`projectlosangeles/SFZ-Instruments` 12.5 GB, `soundfonts4u`) are re-uploads tagged CC-BY-NC-SA by the uploader, so they were skipped.
- **GeneralUser GS**: schristiancollins.com serves a JS-only page (no direct asset path), so the official 2.0.2 release zip was taken from its archive.org mirror; the sf2 INFO chunk reads 'GeneralUser GS 2.0.2 / S. Christian Collins' and `documentation/LICENSE.txt` is included.
- **Dexed**: 1.0.1 ships only its own default cartridge (no Yamaha ROM1A 'E.PIANO 1'/'BASS 1'); its electric_piano entries are decaying FM keys chosen by envelope analysis, not a Rhodes clone. The FreePats FM Piano 1/2 (CC0, sampled DX7-style) are the better e-piano picks.
- **Realism caveats**: FreePats synth pads/leads/strings/brass are single-velocity-layer GM-style synth samples (useful for variety, not 'realistic' horns); real horn sections only exist in the GM sf2 banks (GeneralUser GS / MuseScore_General 'Brass Section'). Muted/palm-muted electric guitar exists only as GM program 28 in the sf2 banks (the FreePats DI Strat can be processed with pedalboard instead). Upright bass only as GM program 32. Brushed kit: GeneralUser GS / MuseScore_General 'Brush' (128:40) plus AVL Blonde Bop HR.
- **Licenses**: everything is CC0 / CC-BY / CC-BY-SA / MIT / GPL-with-sample-exception / GeneralUser GS License v2.0 — all fine for a private, never-released research project. CC-BY-SA items (Salamander Drumkit, AVL kits) and GPL-exception items would need attribution/share-alike only on release.
- Preinstalled banks (FluidR3_GM, AVL sf2 kits, Surge XT, Dexed) are listed with absolute paths and `preinstalled: true`; they count 0 MB toward downloads.
