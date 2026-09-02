# Merge report — c53 fork bdd7bb47f1b5 clone-2 (RC10 Branch C)

**Note:** the instance-side canonical location
`/home/user/music-gen-instance/fork-bdd7bb47f1b5/clone-2/merge_report.md` is outside
this session's writable workspace; this workspace copy is the canonical worker output
and the harness / conductor should mirror or link it into the instance-side path on
merge.

## Verdict
`RC10_OTHER_VOCALS_LANDS` — both stems PASS D2 gates on ≥3/5 focus songs.

- vocals: winner **v_a** (basic-pitch defaults, D4-postprocessed), 4/5 songs pass, mean f0_agreement = **88.74%**
- other-residual: winner **o_b** (chroma-based chord track), 3/5 songs pass, mean chroma cosine = **0.664**

## Ledger events emitted (9 total)
Under fork bdd7bb47f1b5 / clone-2. Substantive `M-*` unsuffixed per c32 convention;
infra families under `-clone-2` suffix. Event IDs auto-derived as UUID5 content-hash
via `long_exposure.tools._ledger_schema.content_hash_event_id`.

Substantive (6):
1. `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/other-vocals/pre-registration`
2. `.../other-vocals/impl-per-stem`
3. `.../other-vocals/candidate-matrix-scored`
4. `.../other-vocals/post-processing-applied`
5. `.../other-vocals/winner-selected`
6. `.../other-vocals/verdict-emitted`

Housekeeping (2):
7. `_archive/cycle-53-rc10-other-vocals-scratch-clone-2`
8. `_infra/adopt-cycle53-rc10-other-vocals-tests-clone-2`

Egress probe (1):
9. `M-INGEST-1/egress-probe-cycle53-clone-2` (path A per c49 policy; 429 + tv_embedded unchanged)

## Deliverables (all on-disk, byte-deterministic × 2)
- `docs/rc10_other_vocals_report.md` — required output artifact
- `docs/rc10_other_vocals_rubric.md` — pre-registered (mtime gate honored, git-log advisory)
- `docs/rc10_other_vocals_scorecard.md`
- `scripts/recreate_v2/rc10_other_vocals/{__init__,run_rc10}.py`
- `tests/test_rc10_other_vocals_impl.py` — 18/18 pass
- `data/rc10_impl/other_vocals/{rubric_hash.txt, verdict.json, winner_per_stem_type.json, scorecard.tsv, byte_determinism.json, anchor_preservation.json}`
- 140 A/B pair WAV files under `data/recreate_v2/ab_pairs/<sha16>/{vocals,other_residual}/iter_<candidate>_<variant>/{original,rendered}.wav`

## Rubric-hash chain
`docs/rc10_other_vocals_rubric.md` SHA-256 = rubric_hash.txt content = verdict.rubric_hash =
`571296bca46991f69219377be4dd24184c9b1292d33fdc5c2f690e2732ab3620`.

## Byte-determinism × 2
- 50/50 candidate MIDI files SHA-256 equal across two fresh temp-dir runs
- verdict + winners + per-song metrics equal
- 0 mismatches

## Anchor preservation
26 SHAs snapshotted (spec ≥25); all READ-ONLY anchors byte-identical pre==post.
Covers c49 v1 rubric+hash, c50 v2 rubric+hash, c51 Branch A verdict.json, c52 render_stem.py,
focus_set_v2, all 10 baseline stems, 5 rc5 tempo estimates, own rubric+hash pin.

## Cross-branch conflict scan
Disjoint from Branch A (`{drums,bass}/`) and Branch B (`{guitar,piano}/`).
No shared writable anchors. Cross-branch integration is safe.

## Deviations documented
1. **LUFS-I -23 → RMS-dBFS -23 proxy** — `pyloudnorm` unavailable in venv.
2. **`o_b` chroma via templated MIDI** — chroma-family metrics are synth-timbre invariant.
3. **c46 git-log gate advisory** — mtime gate enforced hard.

## promise_check
0 ERRORs post-emission. Pre-existing WARNs (~24) unchanged (unrelated to RC10).

## Test suite
`tests/test_rc10_other_vocals_impl.py` — 18/18 PASS.

## Honest capability-ceiling notes
- **Chicken Grease vocals v_a coverage 0.29**: c49 baseline stem 0..30s but focus_set_v2 D1
  chosen_section is 233.6..263.6s — same upstream baseline-capture mismatch Branch A recorded at
  27.81%. Not a transcription capability ceiling.
- **Chicken Grease + Dojo Cuts other_residual o_a chroma 0.15**: basic-pitch under-transcribes
  the htdemucs residual on percussive/layered content — motivated the `o_b` chord-track fallback.
- **Density gate asymmetry**: `density_ratio` denominator = `o_a` count; when `o_a` under-transcribes,
  `o_b`'s dense chord track fails the ratio gate even at high chroma agreement. Rubric-side
  refinement candidate for c54+.

## c54 handoff
1. Cross-branch scorecard consolidation at `data/rc10_impl/scorecard_all_stems.tsv` after concat.
2. Apply D7 six-stem gate for `M_RECREATE_2_LANDS` candidacy.
3. Consider reference-density fix in D2 other-residual gate.
4. When pyloudnorm becomes available, re-normalize A/B pairs to true LUFS-I -23.
