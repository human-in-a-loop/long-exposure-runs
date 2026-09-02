# Test stage 20 of 23 — c53 clone-2 RC10 other-residual + vocals (`M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/other_vocals`)

**Slice rationale.** With stage 41 having directly probed c54 clone-0 (RC10 drums+bass), stage 42 c53 clone-1 (RC10 guitar+piano), stage 43 c51 fork `38eba9f21a61` clone-1 Branch B (RC2+RC3 upstream MIDI producer), the only un-directly-probed RC10 gate node remaining is c53 clone-2's **RC10 other-residual + vocals** verdict at `data/rc10_impl/other_vocals/verdict.json`. Directly probing this node closes the six-stem RC10 coverage under the operator UPDATE #4 gate on directly-audited foundations (no residual "trusted transitively via parent_rubric_hash" nodes remain in the six-stem chain).

## 7-probe checklist

### PROBE 1 — three-way rubric_hash chain — **PASS**

| Anchor | SHA-256 |
| --- | --- |
| `docs/rc10_other_vocals_rubric.md` (live doc SHA) | `571296bca46991f69219377be4dd24184c9b1292d33fdc5c2f690e2732ab3620` |
| `data/rc10_impl/other_vocals/rubric_hash.txt` (content) | `571296bca46991f69219377be4dd24184c9b1292d33fdc5c2f690e2732ab3620` |
| `data/rc10_impl/other_vocals/verdict.json.rubric_hash` | `571296bca46991f69219377be4dd24184c9b1292d33fdc5c2f690e2732ab3620` |

All three byte-equal.

### PROBE 2 — verdict enum + per-song coverage — **PASS**

- `verdict = "RC10_OTHER_VOCALS_LANDS"` (rubric enum member).
- `other_residual_pass_count = 3` (≥3 required).
- `vocals_pass_count = 4` (≥3 required).
- `per_song = 5` (all 5 focus songs measured).
- **Winners:**
  - other_residual: `candidate=o_b`, mean chroma cosine `0.664`, `postprocessed=false`, songs_passed=3, tiebreak SHA `4efd907e…8a0aaf`.
  - vocals: `candidate=v_a`, mean F0 agreement pct `88.736`, `postprocessed=true`, songs_passed=4, tiebreak SHA `7aef6eec…df4969`.
- `d2_gates` present: other_residual (density_ratio ∈ [0.5, 2.0], mean_chroma_cosine ≥ 0.55); vocals (coverage_ratio ∈ [0.5, 2.0], f0_agreement_pct ≥ 60.0).
- `focus_set_v2_sha256 = 8908dae0…6a1a5ca` (frozen c50 D1-picker anchor).

### PROBE 3 — byte-determinism × 2 — **PASS**

`data/rc10_impl/other_vocals/byte_determinism.json`:

- `midi_byte_determinism_holds = true`
- `n_midi_files_byte_equal = 50 / 50` (10 candidates × 5 songs across two fresh `tmp/rc10_run{1,2}/out/` roots)
- `mismatches = []`
- `per_song_metrics_equal = true`
- `verdict_and_winners_equal = true`
- Env pins recorded: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH`, `TZ=UTC`, `LC_ALL=C.UTF-8`, single-thread BLAS (`OMP=MKL=OPENBLAS=1`), `TF_CPP_MIN_LOG_LEVEL`, `TF_ENABLE_ONEDNN_OPTS`.

### PROBE 4 — anchor preservation live re-hash — **PASS**

`data/rc10_impl/other_vocals/anchor_preservation.json` enumerates 26 anchors (`n_anchors=26`). Live re-hash: **26/26 SHA-256 match**. Zero mismatches, zero missing files.

### PROBE 5 — c33 `render_stem.py` invariant SHA — **PASS (preserved)**

| Anchor | SHA-256 |
| --- | --- |
| Live `scripts/palette_render/render_stem.py` | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` |
| Expected (stage 43 pin) | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` |

Byte-identical. RC10 other+vocals does not import the palette render surface (this stage confirms it did not touch it either).

### PROBE 6 — hygiene — **PASS**

Under `scripts/recreate_v2/rc10_other_vocals/` (2 Python files: `__init__.py`, `run_rc10.py`):
- PRNG scan (`import random`, `from random`, `np.random`, `random.random/seed/randint`): **0 hits**.
- `sidecar_nonfactor` import scan: **0 hits**.
- Interpreter guard: `run_rc10.py` uses `#!/usr/bin/env python3` shebang + module-docstring-documented c33 quarantined-venv subprocess dispatch pattern (dispatches into `workspace/basic_pitch_venv` for librosa + basic_pitch + pretty_midi; directly executable inside that venv). Matches the c33 quarantined-venv precedent. See observation 1 below.

### PROBE 7 — test suite size — **PASS**

`tests/test_rc10_other_vocals_impl.py` uses an in-file `_t(name, cond, detail)` micro-runner (same style as many c53 test files, not pytest-collectable `def test_*`). Numbered test cases 01–18: **18 unique test cases** (rubric-doc-present, rubric-hash byte-equal to doc SHA, rubric mtime < scripts, verdict enum, three-way rubric_hash byte-equality, winners-json shape, per_song = 5 focus songs, A/B pairs present, no PRNG, interpreter guard, no sidecar_nonfactor, c48 env-var flags default OFF, 10 baseline stems present, c50 v2 rubric SHA anchor preserved, and 4 more).

## Cross-branch RC10 six-stem consistency table

Post-stage-44 status of the operator UPDATE #4 six-stem RC10 gate (all rows now directly probed):

| Stem-type | Cycle / branch | Verdict node | Winner | Directly probed |
| --- | --- | --- | --- | --- |
| drums | c54 clone-0 | `RC10_DRUMS_BASS_LANDS` (drums half) | (per c54 winner_per_stem) | stage 41 |
| bass | c54 clone-0 | `RC10_DRUMS_BASS_LANDS` (bass half) | (per c54 winner_per_stem) | stage 41 |
| guitar | c53 clone-1 | `RC10_GUITAR_PIANO_LANDS` (guitar half, 4/5 PASS) | `C2_tuned` | stage 42 |
| piano | c53 clone-1 | `RC10_GUITAR_PIANO_LANDS` (piano half, 5/5 PASS) | `C2_tuned` | stage 42 |
| other-residual | c53 clone-2 | `RC10_OTHER_VOCALS_LANDS` (other-residual half, 3/5 PASS) | `o_b` (raw) | **stage 44 (this stage)** |
| vocals | c53 clone-2 | `RC10_OTHER_VOCALS_LANDS` (vocals half, 4/5 PASS) | `v_a` (post-processed) | **stage 44 (this stage)** |

Upstream MIDI-producer coverage (stage 43 completed the un-directly-probed RC2+RC3 node under c51 fork `38eba9f21a61` clone-1 Branch B). All six-stem RC10 gate nodes and their upstream substantive MIDI producers now have direct-probe coverage in the final-audit record.

## Findings

**Findings appended to `audits/final/findings.jsonl`: 0.**

## Below-MINOR observations (bookkeeping — not findings)

1. **Interpreter-guard idiom variation.** `run_rc10.py` uses shebang (`#!/usr/bin/env python3`) + explicit venv dispatch documented in the module docstring, rather than a literal `sys.executable == '/usr/bin/python3'` assertion (the pattern used in some sibling stubs). Both satisfy the c33 quarantined-venv precedent; the docstring is explicit about the dispatch mechanism. Zero correctness impact; noted only because a mechanical grep for `/usr/bin/python3` in the file body returns no hit despite the intent being present.
2. **Documented LUFS-I approximation.** `verdict.json.notes` records "LUFS-I -23 approximated by RMS-dBFS -23 (pyloudnorm unavailable in venv)" and "o_b chroma cosine computed on templated MIDI pitch-class implication (see rubric deviation)". Both are honest, rubric-anticipated deviations already surfaced in the c53 report chain (parallel to c53 clone-1 guitar+piano's ±0.5 LU relaxation for peak-limited signals); not defects.
3. **Test runner style.** `test_rc10_other_vocals_impl.py` uses an in-file `_t()` micro-runner (33 `_t(` call-sites collapsing to 18 unique numbered test IDs) rather than pytest `def test_*`. Consistent with c53 sibling test files; reduces discoverability under a plain `pytest tests/` sweep but the runner is invoked as a top-level script per the module's own protocol.

## Coverage delta

With stage 44 landed, every un-directly-probed RC10 six-stem verdict node has direct-probe coverage in the final-audit record. The RC10 all-six-stem gate for operator UPDATE #4 is now transitively backed by six directly-probed per-stem-type verdicts plus three directly-probed upstream MIDI producers (c51 Branch A RC1+RC9 for vocals/guitar/piano via stage 42 chain, c51 Branch B RC2+RC3 for drums/bass via stage 43, and c33 palette_render + c53 clone-2 hydration for other-residual + vocals via this stage).
