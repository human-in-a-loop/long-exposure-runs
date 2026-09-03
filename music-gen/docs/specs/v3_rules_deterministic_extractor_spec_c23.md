# V3 Rules Deterministic Extractor — Spec (Cycle 23, M-V3-RULES-1)

## Milestone
M-V3-RULES-1 — First activation of the operator's rules-hashed contract for
the M-V3 arc, under the c23 operator directive extending the determinism
stance to the generation half of the pipeline.

## Provenance and predecessors
- c9 rules schema (`data/rules/ledger.jsonl`) — READ-ONLY here.
- c15 i3 D-minor ledger (`data/rules/ledger_i3_dminor.jsonl`) — READ-ONLY.
- c40 rated-corpus ledger (`data/rules/ledger_rated_corpus.jsonl`) — READ-ONLY.
- c22 unified driver `scripts/v3_spine/recreate_v3.py` + env-pin manifest.
- Operator-approved v3 deliveries (READ-ONLY corpus):
  - Chicken Grease  — song sha16 `31a164f845f8e27e` (c5 → v3-spine palette
    render).
  - Rome            — song sha16 `51e433ade2a845e1` (c20 delivery).
  - What If I Go    — song sha16 `252eb21ce7df7328` (c21 restart delivery).
  - Disco A         — song sha16 `cdd2717e52820ff6` (c21 delivery).

## Determinism contract (operator, c23)
1. Rules extraction is a pure deterministic program: for a fixed input
   corpus, `rules_artifact.jsonl` is byte-identical across two fresh
   `tempfile.mkdtemp()` runs on the same host.
2. No PRNG in the extractor. Where a downstream consumer expects a
   `random_state`, the artifact records `random_state: 0` as a static
   field, not a seed drawn from anywhere.
3. No hidden clock: every timestamp field emitted into the artifact is a
   fixed constant (see `EXTRACT_TS_ISO`), never `datetime.now(...)`.
4. Iteration order is content-sorted: stems in fixed order
   `["bass","drums","guitar","piano","vocals","other"]`, songs in fixed
   sha16-lex order, rules in `(rule_type, rule_id)` lex order.
5. Interpreter guard: every stub under `scripts/v3_rules/` begins with
   `#!/usr/bin/env /usr/bin/python3` header AND runtime assert
   `sys.executable == "/usr/bin/python3"`.
6. Forbidden imports (AST-enforced by the test suite):
   - `sidecar_nonfactor` (any submodule).
   - `random`, `numpy.random`, `torch.random`, `secrets`.
   - VST3 state APIs: any attribute access matching
     `get_state|save_state|save_preset|load_state|set_state` (c31/c35).
7. Anchor preservation: pre==post byte-exact for ≥30 SHAs listed below.

## Three-way rubric_hash_v3_rules chain
The rubric_hash chain is the operator's "rules-hashed contract" primitive:
one hash must appear byte-identical in three places, and any mismatch is a
LANDS-blocker per FD-1 ("no tuning, no retry, no fallback — operator
decides").

- **Position A (self-hash of this doc)**: `sha256(bytes of this file)`.
  Computed post-write and pinned into `data/v3/rules/rubric_hash.txt`.
- **Position B (pinned file)**: `data/v3/rules/rubric_hash.txt` — a single
  line, 64 hex chars + trailing newline, mtime STRICTLY less than any
  file created under `scripts/v3_rules/`.
- **Position C (verdict field)**: `verdict.rubric_hash_v3_rules` inside
  `data/v3/rules/verdict.json`.

The test `test_rubric_hash_v3_rules_three_way_byte_equality` asserts
A == B == C. This is the first activation of the rules-hashed contract
for the M-V3 arc; earlier v3-spine work used `rubric_hash_v2` and
`rubric_hash_v3` — those chains are unchanged by this cycle.

## Survey-open-source-first (operator, c23)
Per the "survey-open-source-first" rule, before we write any constraint
sampler or grammar we enumerate on-disk / fetchable libraries and record
what is available under the current proxy without attempting a fetch. The
extractor emits `data/v3/rules/fetchability_ladder.jsonl` with one JSON
object per candidate:

- `music21` — MIT-licensed symbolic music toolkit; would provide chord
  labeling, key detection, meter analysis. Fetchability probe: import
  attempt (no `pip install`); result recorded as `on_disk` or
  `not_on_disk`.
- `mingus` — LGPL-3 music theory library; scales/chords helpers.
- `jsonschema` — MIT; already-common dependency; would validate the
  emitted rule objects against the c9 schema.
- `sklearn` — BSD-3; statistical priors (histograms, KDE) for the
  eventual sampler; not used by the extractor prototype.

`no_fetch_attempts: true` is recorded on every row. Any library reported
as `not_on_disk` is out of scope for this cycle and the operator's
"survey-open-source-first" rule is respected by falling back to
first-principles Python (stdlib + `mido` where a MIDI reader is needed;
`mido` is a pre-existing dependency of the v3 pipeline).

## Rule schema (extension of c9 with v3 per-stem provenance)
Each rule is a JSON object with these fields, matching c9's schema exactly
where the field name is shared, and adding a `provenance_pointers[].stem`
key to carry the v3 per-stem attribution.

```
{
  "schema_v":       1,
  "event_type":     "rule",
  "rule_type":      "harmonic" | "rhythmic" | "melodic" | "form" | "arrangement",
  "rule_id":        "rule_" + hex16(sha256(canonical_params)),
  "event_id":       hex32(sha256(rule_id + "|" + song_sha16 + "|" + stem)),
  "extractor":      "extract.<rule_type>",
  "extractor_version": "v3-rules-c23-1",
  "parameters":     {…},                # rule_type-specific
  "provenance_pointers": [
    {
      "song_sha16":  "<16 hex>",
      "stem":        "bass"|"drums"|"guitar"|"piano"|"vocals"|"other"|"full_mix",
      "measure_range": [start, end],
      "midi_track_index": <int>,        # 0-based index into merged.mid
      "midi_ticks_per_beat": <int>
    }
  ],
  "scope": {"level": "song"|"section"|"measure", "start_s": <float>, "end_s": <float>},
  "confidence": <float in [0,1]>,
  "parameters_random_state": 0,         # static; no PRNG present
  "ts": EXTRACT_TS_ISO                  # constant
}
```

The five `rule_type` values are the c9 whitelist. Per-stem provenance is
required because v3 doctrine is per-stem (htdemucs_6s → MuScriptor per-
stem); a rule attributed to "the song" must carry its stem index.

## Input corpus
Four operator-approved v3 renderings, READ-ONLY:

| Song sha16          | Source of merged.mid                                     |
|---------------------|----------------------------------------------------------|
| `31a164f845f8e27e`  | `data/v3_spine/31a164f845f8e27e/merged.mid`              |
| `51e433ade2a845e1`  | `data/v3/deliveries/51e433ade2a845e1/merged.mid`         |
| `252eb21ce7df7328`  | `data/v3/deliveries/252eb21ce7df7328/merged.mid`         |
| `cdd2717e52820ff6`  | `data/v3/deliveries/cdd2717e52820ff6/merged.mid`         |

Panels (`panel.json`) are read only for metadata (sample rate, song
duration). Panels are never a LANDS gate (FD-6). WAVs are not read.

## Extraction program
`scripts/v3_rules/extract_rules.py` performs a fixed sequence:

1. Assert interpreter (`/usr/bin/python3`); assert env pins
   (`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH` non-empty, `TZ=UTC`,
   `LC_ALL=C.UTF-8`).
2. Emit `fetchability_ladder.jsonl` (probe-only, no fetch).
3. For each song in sha16-lex order, for each stem in the fixed order,
   read the corresponding `mido.MidiFile` track deterministically and
   compute:
   - **harmonic**: unordered pitch-class histogram + monophonic chord
     window (Krumhansl-Schmuckler variant on a fixed 4-bar window,
     stdlib-only re-implementation; no music21 dependency in the
     prototype).
   - **rhythmic**: onset-density per bar, swing ratio (offbeat vs onbeat
     duration ratio), quantization grid inference (1/8, 1/16, 1/32).
   - **melodic**: interval histogram per stem; range in semitones.
   - **form**: section boundaries derived from silence-longer-than-1-bar;
     downbeat count.
   - **arrangement**: which stems are active in each 4-bar window.
4. Sort all emitted rules by `(rule_type, rule_id)` and write JSONL to
   `data/v3/rules/rules_artifact.jsonl` with `sort_keys=True,
   separators=(",", ":"), ensure_ascii=True` and a trailing `\n` per
   line.
5. Compute `sha256` of the written file bytes and write to
   `data/v3/rules/rules_artifact.sha256` as a single hex line.

## Byte-determinism proof
`test_byte_determinism_two_fresh_runs` shells the extractor twice under
two fresh `tempfile.mkdtemp()` roots (`--out-dir` argument) and compares
the resulting `rules_artifact.jsonl` SHA-256 for equality. Any mismatch
is a LANDS-blocker.

## Verdict
`data/v3/rules/verdict.json` carries:

```
{
  "milestone": "M-V3-RULES-1",
  "cycle": 23,
  "clone": 2,
  "fork": "d5530f8d1ccc",
  "rubric_hash_v3_rules": "<64 hex>",
  "rules_artifact_sha256": "<64 hex>",
  "byte_determinism": {"runs": 2, "sha_equal": true},
  "n_rules_by_type": {"harmonic": N, "rhythmic": N, "melodic": N,
                       "form": N, "arrangement": N},
  "corpus_song_sha16s": [ "31a164f845f8e27e", "51e433ade2a845e1",
                          "252eb21ce7df7328", "cdd2717e52820ff6" ],
  "tests_pass_over_total": [P, T],
  "operator_ear_dependency": false,
  "panel_is_never_lands_gate": true
}
```

## Test suite (≥12/15 green required)
`tests/test_v3_rules_deterministic_extractor.py`:

1. `test_interpreter_guard_present` — grep `/usr/bin/python3` in extractor.
2. `test_no_prng_imports` — AST-scan for `random`, `numpy.random`,
   `torch.random`, `secrets` in `scripts/v3_rules/`.
3. `test_no_sidecar_nonfactor_imports` — AST-scan for `sidecar_nonfactor`.
4. `test_no_vst3_state_apis` — regex scan for
   `get_state|save_state|save_preset|load_state|set_state\(` in
   `scripts/v3_rules/`.
5. `test_rubric_doc_mtime_before_scripts` — this file's mtime is strictly
   less than any file under `scripts/v3_rules/`.
6. `test_rubric_hash_v3_rules_three_way_byte_equality` — Position A ==
   Position B == Position C.
7. `test_fetchability_ladder_no_fetch_attempts` — every row has
   `no_fetch_attempts: true`.
8. `test_rules_artifact_schema_conforms_to_c9_types` — every rule has
   `rule_type in {harmonic, rhythmic, melodic, form, arrangement}`.
9. `test_per_stem_provenance_present` — every `provenance_pointers[]`
   entry has a `stem` key from the fixed whitelist.
10. `test_byte_determinism_two_fresh_runs` — extractor is byte-identical
    across two `tempfile.mkdtemp()` runs.
11. `test_rules_artifact_self_anchor_sha` — `rules_artifact.sha256`
    equals `sha256(rules_artifact.jsonl bytes)`.
12. `test_readonly_anchor_preservation` — a snapshot of ≥30 anchor SHAs
    taken before extraction equals the post-extraction snapshot.
13. `test_c9_c15_c40_ledgers_untouched` — the three predecessor ledgers
    are byte-identical pre vs post.
14. `test_ledger_events_have_agent_and_clone_fields` — every event
    emitted this cycle has `agent="worker"`, `agent_original` starting
    with `worker-clone-`, and `clone="2"`.
15. `test_corpus_covers_four_operator_approved_songs` — the four song
    sha16s appear in provenance.

Target: ≥12/15 green.

## Anchor preservation (≥30 SHAs pre==post byte-exact)
Snapshot script asserts pre==post byte-exact equality for at least these
anchors (populated by the extractor's `--anchor-snapshot` mode):

- `scripts/palette_render/render_stem.py` (`214372d9…5b2b`)
- `scripts/v3_spine/midi_from_json_events.py`
- `scripts/v3_spine/recreate_v3.py`
- `scripts/v3_spine/v3_pipeline/env_pin.py`
- `data/rules/ledger.jsonl`  (c9)
- `data/rules/ledger_i3_dminor.jsonl`  (c15)
- `data/rules/ledger_rated_corpus.jsonl`  (c40)
- `data/v3/deliveries/{31a164f845f8e27e,51e433ade2a845e1,252eb21ce7df7328,cdd2717e52820ff6}/manifest.json`
- `data/v3/deliveries/{31a164f845f8e27e,51e433ade2a845e1,252eb21ce7df7328,cdd2717e52820ff6}/panel.json`
- `data/v3_spine/31a164f845f8e27e/merged.mid`
- `data/v3/deliveries/{51e433ade2a845e1,252eb21ce7df7328,cdd2717e52820ff6}/merged.mid`
- The c22 rubric doc `docs/v3_spine_canonical_midi_serializer_spec.md`
- The c22 driver spec file `docs/PIVOT_v3_simplest_robust_pipeline.md`
- All previously landed rules_v1 schema files under
  `scripts/rules/schema/`.

## Ledger events (6 named + 2 housekeeping, all under M-V3-RULES-1/*)
Every event carries `agent="worker"`, `agent_original="worker-clone-2"`,
`clone="2"`, `fork="d5530f8d1ccc"`, `cycle=23`.

1. `M-V3-RULES-1/rubric-committed`
2. `M-V3-RULES-1/fetchability-probed`
3. `M-V3-RULES-1/extractor-implemented`
4. `M-V3-RULES-1/artifact-emitted`
5. `M-V3-RULES-1/byte-det-verified`
6. `M-V3-RULES-1/verdict-emitted`
7. `_archive/cycle-23-scratch-clone-2` (housekeeping)
8. `_infra/adopt-cycle23-tests-clone-2` (housekeeping)

## Fixed decisions honored
- FD-1 (byte-det failure = operator decides, no auto-fallback).
- FD-6 (panel is NEVER a LANDS gate; operator ear is the only authority).
- c33 harness-clone-namespace-guard (infra families get `-clone-2` suffix
  when written from this clone context).
- c48 env-var flags default-OFF (never referenced in extractor code
  paths).

## Anti-patterns explicitly NOT attempted
- VST3 state APIs (c31/c35).
- M-EAR-1 Path A under N=55 (c22/c23/c25 invalidated).
- CLAP fetch (c11 HF SSL failure).
- Hand-orchestrating song recreation (c22 operator directive).
- Hand-composing songs (`agentic_composition:true` fallback only per c23).
- PRNG anywhere in the extraction path.
