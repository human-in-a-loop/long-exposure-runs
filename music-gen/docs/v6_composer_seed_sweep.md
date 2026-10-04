# Seed sweep 20261004T231012Z

seeds 0..11 x 3 fixtures x modes plain,humanize = 72 cases; bars 32; all caps pass in 72/72 cases after the repair pass (45/72 before it); repairs applied 66 ({'parallel_fifth': 9, 'parallel_octave': 20, 'leap_unresolved': 14, 'leading_tone_unresolved': 23}); forced violations 0 (0 realised on the song's chord pairs; 0 realised keys-rule violations in all); harmony junction re-samples 6.

`before` = the same seed composed with repair_pass=False (constructive layers only); `after` = with repair.py. Counts are the validators' raw metrics (total = summed over cases where the metric is a count). A forced keys_voicing flag sits on a LABEL slot and so appears at every recurrence; `realized` says whether that recurrence's actual neighbour violates.

| rule | cap | cases violating before | after | max count before | after | total count before | after |
|---|---|---|---|---|---|---|---|
| parallel_fifths | <= 1 (per_64_bars) | 10 | 0 | 2 | 0 | 12 | 0 |
| parallel_octaves | <= 1 (per_64_bars) | 18 | 0 | 2 | 0 | 22 | 0 |
| unresolved_sevenths | <= 2 (song) | 0 | 0 | 0 | 0 | 0 | 0 |
| leading_tone_unresolved_at_cadence | <= 1 (song) | 1 | 0 | 2 | 0 | 19 | 0 |
| melodic_leaps_unresolved | <= 2 (per_64_bars) | 0 | 0 | 1 | 0 | 10 | 0 |
| melody_range_violations | == 0 (song) | 0 | 0 | 0 | 0 | 0 | 0 |
| melody_strong_beat_non_chord_tones | <= 0.05 (fraction) | 0 | 0 | 0.0 | 0.0 | None | None |
| bass_root_missing_on_change | == 0 (song) | 0 | 0 | 0 | 0 | 0 | 0 |
| cadences_realized | == 1.0 (fraction) | 0 | 0 | 1.0 | 1.0 | None | None |
| harmonic_rhythm_realized | == 1.0 (fraction) | 0 | 0 | 1.0 | 1.0 | None | None |
| voice_crossing | <= 2 (per_64_bars) | 0 | 0 | 0 | 0 | 0 | 0 |
| section_repeat_integrity | == True (song) | 0 | 0 | None | None | None | None |
| timing_ks_max | <= 0.25 (song) | - | 0 | - | 0.1556 | - | None |
| velocity_std_min | >= 8.0 (song) | - | 0 | - | 9.902 | - | None |
| swing_in_corpus_iqr | == True (song) | - | 0 | - | None | - | None |
| section_repeat_skeleton_integrity | == True (song) | - | 0 | - | None | - | None |
| section_repeat_surface_differs | == True (song) | - | 0 | - | None | - | None |

## Forced violations (logged with reason)

none

## Cases failing a cap without a forced violation

none
