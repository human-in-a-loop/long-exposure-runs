# Stage 41 of 48 — Test 17 of 23

**Slice**: c54 fork bdd7bb47f1b5 Branch A clone-0 RC10 drums+bass sub-leaves under
`M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-bass-*`.

**Rationale for slice**: freshest validated milestone chain per session handoff
guidance; not yet audited. Peer to the c53 clone-1 RC10 guitar+piano milestone
family (also unaudited by this session as of stage 40).

## Milestone family verified

Six c54 sub-leaves under `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`:

- `drums-bass-pre-registration` — rubric SHA landed BEFORE any script.
- `drums-bass-impl-per-stem` — `scripts/recreate_v2/rc10_drums_bass/*.py` (9 files).
- `drums-bass-post-processing-applied` — D4 with/without measurement.
- `drums-bass-winner-selected` — winner_per_stem.json.
- `drums-bass-verdict-emitted` — `RC10_DRUMS_BASS_LANDS`.
- `M-INGEST-1/egress-probe-cycle54-clone-0` — periodic-retry probe row.

## Probes (all PASS)

1. **Three-way rubric_hash chain byte-equal.**
   `sha256(docs/rc10_drums_bass_rubric.md)` = `a79bee01b4c97a1282f476a01915f4f9119fa23d369e5be2b0b72fbee05fd919`
   == `data/rc10_drums_bass_impl/rubric_hash.txt` content (byte-equal)
   == `verdict.json.rubric_hash`. Chain holds.

2. **Verdict shape correct.** `verdict.json` = `RC10_DRUMS_BASS_LANDS` with
   drums 5/5 pass (sole candidate `onset_band_energy`, mean composite 1.0),
   bass 3/5 pass (winner `pyin_mono`, mean composite 0.908 vs `bp_defaults`
   0.799 also-passes-3/5 broken by composite tiebreak vs `bp_tuned`
   0.777 passes 0). Rubric-permissible: winner selection prefers PASS then
   max composite per D5.

3. **Byte-determinism × 2 across 84 artifacts.**
   `byte_determinism.json` records `n_total=84, n_match=84, n_mismatch=0,
   mismatch_files=[]`. 5 songs × (3 bass candidates + 1 drums candidate) × 2
   D4 flavors × (metrics.json + notes.json) = 80 + 4 additional = 84. ✓

4. **Anchor preservation live-verified.** 29-entry `anchor_preservation.json`
   re-hashed against the current on-disk state: 29/29 SHAs byte-match,
   0 mismatches, 0 missing. Notably preserved: `data/rc1_rc9_impl/verdict.json`
   (c51 Branch A), `data/rc2_rc3_impl/verdict.json` (c51 Branch B),
   `data/rc5_impl/<sha16>/rc5_tempo_estimate.json` (c53 Branch C — used as
   `bpm_used` upstream anchor per scorecard column).

5. **c33 render_stem.py do-not-touch invariant.** SHA
   `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` byte-identical
   to stage 38+39+40 pins. `anchor_preservation.py` §48-51 explicitly pins it.

6. **Isolation + hygiene invariants.**
   - Zero `sidecar_nonfactor` imports across all 9 rc10_drums_bass scripts.
   - Zero PRNG: grep for `random.`, `np.random`, `torch.rand*`, `random_state`
     returns empty across the module.
   - Interpreter guard present on all 9 scripts via
     `#!/usr/bin/env /usr/bin/python3` shebang + runtime
     `sys.executable != "/usr/bin/python3"` check in `_common.py`.

## Minor observations (below MODERATE threshold — logged only)

- **`byte_determinism.json` schema difference vs c53 peer.** The c54 file
  records only `{n_total, n_match, n_mismatch, mismatch_files, run{1,2}_sha}` —
  no `env_pins` block, no tempdirs. The c53 clone-1 guitar+piano peer records
  `env_pins`, `run_id`, `clone`, `fork`, etc. inline. c54's env pins are
  documented in `verdict.json`-adjacent context and the plan-of-record's
  success criterion; the byte-det artifact just doesn't self-carry them.
  Below MINOR.

- **`anchor_preservation.json` structure is single-snapshot.** The file
  records 29 SHAs but no explicit pre/post pair and no `preservation_holds`
  bool. The narrative claims "byte-identical pre==post" which is verified
  operationally by the live re-hash above matching all 29 SHAs — but the
  artifact itself is only a pinned-baseline snapshot, not a comparison
  record. Below MINOR (verifiable externally, as demonstrated).

- **`#!/usr/bin/env /usr/bin/python3` shebang form.** `env(1)` receives an
  absolute path rather than a bare interpreter name; unusual but functional
  (env just execs the given path). Below MINOR.

## Findings appended: 0

No CRITICAL or MODERATE defects. All success criteria on the six sub-leaves
resolve to PASS against on-disk evidence.

## Next stage

Stage 42 of 48 — test 18 of 23. Remaining unaudited high-value slices per
session handoff: c53 clone-1 RC10 guitar+piano (60-row scorecard, 10 A/B
pair WAVs, `RC10_GUITAR_PIANO_LANDS` verdict); c51 Branch B RC2+RC3
`data/rc2_rc3_impl/` (drums onset transcription + bass transcription MIDIs
consumed by c53 stage-40 rerun); c50 rubric-v2 supersede chain +
`_plan/m-recreate-2-rubric-v2-supersede` supersedes_path str per c14 lemma;
`_infra/anchor-manifest-v1` 18→19 entry evolution (c35 → c47 SOURCE_DATE_EPOCH
pin).
