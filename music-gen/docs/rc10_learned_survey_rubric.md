<!--
created: 2026-09-02T07:00:00Z
cycle: 57
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/learned-transcribers
-->

# RC10 W3 Learned Transcriber Survey — Rubric

Peer sub-milestone under
`M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`
per c29 state-machine lemma. Not a child of c53/c54/c55 terminal-validated
sub-leaves.

## D1 Fetchability ladder

Four candidate families. Every install attempt logged to
`data/rc10_learned_survey/fetchability_ladder.jsonl` with per-rung
`{family, rung, url, http_status, sha256_if_success, failure_mode_if_fail,
ts}`.

| Family | Rung | Method |
|---|---|---|
| Drums-A (Omnizart drum sub-module) | 1 | `pip install omnizart` in fresh venv |
| Drums-A | 2 | `omnizart download-checkpoints` (drum sub-module) |
| Drums-B (OaF-drums) | 1 | GitHub release wheel + weights |
| Bass/Vocals-f0 (torchcrepe) | 1 | `pip install torchcrepe==0.0.24` |
| Bass/Vocals-f0 | 2 | Bundled weights self-check |
| Piano (ByteDance) | 1 | `pip install piano_transcription_inference` |
| Piano | 2 | Weight fetch (Zenodo/GitHub release) |
| Multi-instr (MT3-class) | 1 | Probe HuggingFace + GitHub release paths |
| Multi-instr | 2 | Wheel + weights (if rung-1 CDN clears) |

All fetches through `HTTPS_PROXY`. Honest FETCH_FAIL rows preserved on
rejection (c11 CLAP precedent — this is a DISTINCT model set; the
c11-blacklisted `laion-clap-htsat` HuggingFace path is grep-forbidden).

## D2 Quarantined venv

`workspace/learned_transcribers_venv/` — DISJOINT from
`workspace/basic_pitch_venv` (TF/torch version isolation).
`/usr/bin/python3` outer + venv-python inner via subprocess.

Env pins on every invocation:

```
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
PYTHONHASHSEED=0
SOURCE_DATE_EPOCH=1756463424
TZ=UTC
LC_ALL=C.UTF-8
```

Plus `torch.manual_seed(0)` at inner-script entry (single allowlist site,
AST-grep verified).

Venv-python-guard on inner scripts; c48 env-flags default OFF via
`os.environ.setdefault`.

## D3 Smoke test (BEFORE gold-set dependency)

For each successfully-installed model, run against ONE focus stem from
`data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/` (Chicken Grease):

- Omnizart-drum / OaF-drums → `drums.wav`
- torchcrepe → `bass.wav` (also probe `vocals.wav`)
- ByteDance piano → `piano.wav`
- MT3-class → full mix (constructed from stem sum if needed)

Emit per-model `data/rc10_learned_survey/<model>/notes.json`. Run TWICE
into fresh `tempfile.mkdtemp()` dirs; assert SHA-256 equality on
`notes.json`.

## D4 Gold-set accuracy scoring (CONDITIONAL on Branch A)

Poll `data/rc10_gold_set/*/verdict.json` mid-cycle. If verdict ∈
{GOLD_SET_LANDS, GOLD_SET_PARTIAL}, compute note-level F1 with tolerance
{pitch=±0, class=exact, onset_time=50 ms}; restrict to gold `confidence ∈
{high, medium}`.

Emit `data/rc10_learned_survey/accuracy_vs_gold.tsv`:
`model, song, stem, section, gold_note_count, model_note_count, precision,
recall, f1`.

Else emit `data/rc10_learned_survey/smoke_test_only.flag` +
`deferred_scoring_reason: "branch_a_gold_set_not_landed_mid_cycle"` in
verdict.json.

## D5 Cross-stem reconciliation stub

Poll Branch B `data/rc10_musical_time/cross_stem_energy_per_onset.tsv`.
If landed: emit
`data/rc10_learned_survey/cross_stem_reconciliation_stub.tsv` with
`{onset_s, drum_owner_energy_dB, bass_owner_energy_dB, assignment}`
(assignment=`shared` if both ≥ 60% of max stem energy at onset). Else
emit `deferred_no_energy_table.sentinel` + header-only TSV.

## D6 Widened drum vocabulary via native taxonomy

If Omnizart-drum or OaF-drums installs and native output supports ≥5
classes, preserve verbatim in notes.json (do NOT collapse to 3
c55-classes). If output is 3-class only, honest note in report §D6.
Per-song BIC-chosen k is c58 scope.

## D7 Verdict enum

- **LEARNED_SURVEY_LANDS**: ≥1 model installs + smoke-tests successfully
  (byte-det × 2) AND (if gold-scored) ≥ 0.40 note-F1 on CG drums OR bass.
- **LEARNED_SURVEY_PARTIAL**: ≥1 model installs but smoke-test fails
  deterministically, OR gold-scored F1 < 0.40 on both CG drums AND bass.
- **FETCH_FAILS_ALL**: zero models install; per-rung failure log
  documents the block.

## §3 Falsifiable success criteria (from research brief)

(a) Rubric doc mtime < every `.py` under
`scripts/recreate_v2/learned_transcribers/` (test 01 hard; test 02 SOFT
git-log per c46 amendment).
(b) Three-way `rubric_hash` byte-equality (doc SHA == `rubric_hash.txt`
== `verdict.json.rubric_hash`).
(c) Fetchability ladder JSONL ≥ 4 rows (one per family minimum).
(d) `workspace/learned_transcribers_venv/` present; DISJOINT from
`basic_pitch_venv/` (distinct paths, distinct site-packages).
(e) For each installed model: `notes.json` produced; run1 SHA == run2 SHA.
(f) Conditional on Branch A: `accuracy_vs_gold.tsv` OR
`smoke_test_only.flag`.
(g) Cross-stem stub TSV or sentinel.
(h) `laion-clap-htsat` NOT in fetchability_ladder (grep-verified).
(i) READ-ONLY anchors byte-identical pre==post: c50 v2 rubric SHA
`0e11f704…debe1f`; c33 `render_stem.py` SHA `214372d9…5b2b`; c53/c54/c55
rubric+winner+verdict SHAs.
(j) c55 v2 impl trees byte-identical pre==post.
(k) `basic_pitch_venv/` byte-unchanged.
(l) No PRNG except `torch.manual_seed(0)`.
(m) `/usr/bin/python3` guard on top-level orchestrators; venv-python
guard on inner; c48 env-flags default OFF.
(n) No `sidecar_nonfactor` import (AST-grep clean).
(o) ≥15/15 tests green in `tests/test_rc10_learned_survey.py`.
(p) 0-ERROR promise_check post-emission.
(q) Verdict ∈ enum above.

## §5 Non-goals

- No v3/v4 of c55 classifier family.
- Do NOT re-open c11 CLAP anti-pattern; distinct model set.
- Do NOT modify `basic_pitch_venv/`.
- Do NOT touch c55 v2 impl trees or `render_stem.py`.
- Do NOT modify c50 v2 rubric.
- Do NOT ship W4 concatenative resynthesis; c58 scope.
- No PRNG except `torch.manual_seed(0)`.
