---
created: 2026-08-28T07:00:00Z
cycle: 6
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RULES-1/schema
---

# M-RULES-1/schema — rules ledger schema v1

**Fork:** 3168fb0e47a1 / clone-1
**Author:** cyd7bevdr@mozmail.com
**Date:** 2026-08-28
**Status:** schema-half complete; extraction-half deferred to M-SCORE-1.

## 1. Objective and scope

Design and implement the typed rules ledger for M-RULES-1 so the moment
M-SCORE-1 lands and real rules can be extracted, the ledger accepts them
cleanly on first commit. This branch **closes the schema-half of
M-RULES-1** (schema, validator, ledger writer, synthetic-instance test
set). The extraction-half — "first extraction from 1 song's merged
score" — remains blocked on M-SCORE-1 and is explicitly out of scope
here.

The schema is JSON-Schema-draft-2020-12 authoritative, with a strict
YAML translation for human readability. Five rule types are supported
end-to-end: `harmonic`, `rhythmic`, `melodic`, `form`, `arrangement`.
Every rule carries `rule_id` / `rule_type` / `schema_v=1` /
`extractor` / `extractor_version` / `scope` / `provenance_pointers` /
`confidence ∈ [0,1]` / typed `parameters`. Append-only semantics are
provided by a supersede-as-event pattern (never in-place edit) mirrored
directly on `promise_ledger.jsonl`.

## 2. Design decisions

| Decision | Rationale |
|---|---|
| **Content-addressed `rule_id`** = `"rule_" + sha256(canonical_json({rule_type, scope, sorted_provenance_pointers, parameters}))[:16]` | Deterministic dedup at the source. Identical content → identical id; one-bit change → different id. Distinguishes "refinement" from "different rule" without human judgment. |
| **Append-only with supersede events** — never in-place edit | Preserves audit trail. Mirrors `promise_ledger.jsonl`. `effective_rules()` filters superseded rows at read-time. |
| **Unknown-type policy: REJECT** at both layers | `rule_type` is an `enum` of exactly five values. Anything else fails Layer 1 with the enum error string. Future v2 could quarantine into a backlog; today we reject. Documented in `scripts/rules/schema/README.md`. |
| **Two-layer validator** (JSON Schema + hand-written Python) | JSON Schema handles shapes / patterns / enums / bounds mechanically. Python enforces what JSON Schema cannot express portably: PCH sum-to-1, scope end>start, form section order, cross-row duplicate rule_id, supersede-target existence. |
| **`additionalProperties: false` at every level** | A stray field is rejected — including any non-factor field (`genre`, `artist`, `era`, …). Non-factor isolation is a side-benefit of the schema rigor and is exercised by a dedicated planted-invalid test. |
| **Two row kinds** distinguished by `event_type` (`rule`, `supersede`) | Cleanest way to keep supersede events on the same ledger without polluting the rule row shape with optional `superseded_by` back-pointers. |
| **Continuous `confidence` ∈ [0,1]**, calibration deferred | Recommended in the research brief. Discrete {low, medium, high} would prematurely lock in a scale before the trained ear (M-EAR-1) is in place to calibrate. |

## 3. Schema tables

### 3.1 Common fields (all rows)

| Field | Type | Constraint |
|---|---|---|
| `event_type` | string | `enum ["rule", "supersede"]` |
| `schema_v` | integer | `const 1` |
| `event_id` | string | `^[0-9a-f]{32}$` (UUID4-hex convention, matches `promise_ledger`) |
| `ts` | string | RFC 3339 `date-time` |
| `extractor` | string | non-empty |
| `extractor_version` | string | non-empty |

### 3.2 `event_type: "rule"` — additional fields

| Field | Type | Constraint |
|---|---|---|
| `rule_id` | string | `^rule_[0-9a-f]{16}$` (content-derived) |
| `rule_type` | string | `enum ["harmonic","rhythmic","melodic","form","arrangement"]` |
| `scope` | object | `{level ∈ song|section|measure, start_s ≥ 0, end_s ≥ 0}`; Layer 2 enforces `end_s > start_s` (song/section) or `end_s ≥ start_s` (measure). `additionalProperties: false`. |
| `provenance_pointers` | array | `minItems: 1`. Each item: `{transcription_event_id (32-hex), measure_range [int≥0, int≥0], clip_id? (16-hex)}`. `additionalProperties: false`. |
| `confidence` | number | `[0, 1]` |
| `parameters` | object | typed per `rule_type` — see §3.4 |

### 3.3 `event_type: "supersede"` — additional fields

| Field | Type | Constraint |
|---|---|---|
| `supersedes_rule_id` | string | `^rule_[0-9a-f]{16}$` — must reference an earlier `rule` event |
| `new_rule_id` | string | `^rule_[0-9a-f]{16}$` — must reference an earlier `rule` event; must differ from `supersedes_rule_id` |
| `reason` | string | 1–500 chars, free text |

### 3.4 Typed `parameters` union per `rule_type`

Enforced via `if/then/else` chain inside `allOf` in the JSON Schema.

- **harmonic** — `{ "key": "<TONIC>_<MODE>" (regex `^[A-G][b#]?_(major|minor|dorian|phrygian|lydian|mixolydian|aeolian|locrian)$`), "chord_progression": [roman_numeral, …] (minItems 1; regex `^(I|II|…|vii)[b#]?(m|dim|aug|maj7|m7|7)?$`), "cadence": enum["authentic","plagal","half","deceptive","none"] }`.
- **rhythmic** — `{ "tempo_bpm": number ∈ (0, 300), "meter": "<num>/<den>" (regex `^[1-9][0-9]?/[1-9][0-9]?$`), "pattern": array of enum["kick","snare","hihat","cymbal","tom","rest"] (minItems 1), "swing_ratio": number ∈ [0.5, 0.75] }`.
- **melodic** — `{ "contour": enum["arch","ascending","descending","static","undulating"], "range_semitones": integer ∈ [0, 48], "pitch_class_histogram": array length 12 of number ∈ [0, 1] (Layer 2 enforces sum-to-1 within `abs_tol=1e-6`) }`.
- **form** — `{ "sections": [{ "label": string (regex `^[A-Z][a-z]?[0-9]?$`), "start_measure": int ≥ 0, "end_measure": int ≥ 0 (Layer 2 enforces > start_measure) }, …] (minItems 1) }`.
- **arrangement** — `{ "instrumentation": [string, …] (minItems 1), "density_over_time": [number ∈ [0,1], …] (minItems 2), "layer_events": [{ "t_s": number ≥ 0, "op": enum["add","remove","swap"], "layer": string }, …] }`.

## 4. Round-trip determinism

- **25 synthetic instances** authored under
  `scripts/rules/schema/examples/<rule_type>/` (5 per type), built
  deterministically by `scripts/rules/schema/examples/build_examples.py`.
- **All 25 pass** `validate_row(row) == []` (Layer 1 + Layer 2 clean).
- **All 25** write → `json.loads` → canonical-JSON-compare yields identical
  string (`test_round_trip_determinism`).
- **All 25** rule_ids are reproducible: `derive_rule_id(rule)` matches
  the committed file's `rule_id` value on both computes
  (`test_rule_id_reproducibility`).

Example (harmonic_01):

```
file:    scripts/rules/schema/examples/harmonic/harmonic_01_rule_10bf79e885ab75ba.json
rule_id: rule_10bf79e885ab75ba
event_id: 9d11fa100daac4dc1c295f226dce53a5
scope:   {"level": "song", "start_s": 0.0, "end_s": 180.0}
```

## 5. Planted-invalid rejection matrix

`tests/test_rules_schema.py` plants **11 invalid instances** (each a
one-line mutation of a valid synthetic example). Every one is caught by
either Layer 1 or Layer 2 with a specific error-string keyword the test
grep-checks.

| # | Planted invalid | Caught by | Grep keyword in error |
|---|---|---|---|
| 1 | `rule_type = "symbolic"` (unknown type) | Layer 1 (enum) | `rule_type`, `enum`, `'symbolic'` |
| 2 | `provenance_pointers = []` | Layer 1 (`minItems`) | `provenance_pointers`, `non-empty` |
| 3 | `confidence = 1.5` | Layer 1 (`maximum`) | `confidence`, `maximum` |
| 4 | `confidence = -0.1` | Layer 1 (`minimum`) | `confidence`, `minimum` |
| 5 | PCH sum = 0.9990 (short by 0.001) | **Layer 2** | `pitch_class_histogram sum` |
| 6 | form section `end_measure = start_measure` | **Layer 2** | `end_measure`, `start_measure` |
| 7 | `scope = {section, start_s=30, end_s=30}` | **Layer 2** | `scope.end_s`, `scope.start_s` |
| 8 | extra top-level field `"genre": "rock"` (non-factor leak) | Layer 1 (`additionalProperties`) | `additional`, `genre` |
| 9 | `harmonic.key = "H_major"` (H not a note) | Layer 1 (`pattern`) | `key`, `pattern` |
| 10 | `rhythmic.swing_ratio = 0.9` (> 0.75) | Layer 1 (`maximum`) | `swing_ratio`, `maximum` |
| 11 | Duplicate `rule_id` across two rows | `validate_batch` cross-row | `duplicate rule_id` |

Plus four **ledger-writer contract** tests:

| # | Planted misuse | Caught by |
|---|---|---|
| L1 | Write same `rule_id` twice via `write_rule` | `LedgerError: duplicate rule_id` at write time |
| L2 | Write supersede pointing at nonexistent `rule_id` | `LedgerError: … not found in ledger` |
| L3 | Grep `ledger.py` source for `open(..., "w")` or `"r+"` | absent → append-only enforced |
| L4 | Full supersede chain (write A, write B, supersede A→B) | `effective_rules()` returns only B |

**Total: 15 planted-invalid checks, all caught.** (Brief asked for ≥10.)

## 6. Ledger integration

- Path: `data/rules/ledger.jsonl` — created empty this cycle
  (`ensure_ledger_exists()`). Extractors deferred to M-SCORE-1 and the
  M-RULES-1/extraction sub-milestone.
- Writer opens with `mode="a"` only. `flush() + os.fsync()` after every
  append. Enforcement is grep-tested (§5, L3).
- Duplicate `rule_id` rejected at write time (§5, L1). This is stricter
  than a load-time check — it guarantees the file on disk never
  contains a duplicate.
- Supersede rows require both `supersedes_rule_id` and `new_rule_id` to
  already exist as `rule` events in the ledger (§5, L2). Extractors
  therefore MUST write the replacement rule before the supersede row.
- `read_ledger()` streams rows in insertion order; malformed JSON lines
  are skipped (defensive: the ledger is append-only, but a partial write
  from a killed process should not brick the reader).
- `effective_rules()` walks the supersede table and returns only
  non-superseded rule rows (§5, L4). Transitive: A→B, B→C yields only
  C.

## 7. Interface for M-SCORE-1's forthcoming extractors

An extractor that emits rules from a merged score must:

```python
from scripts.rules.ledger import write_rule, LedgerError
from scripts.rules.rule_id import derive_rule_id
import hashlib, uuid

# 1. Compose the content-only fields.
rule_content = {
    "rule_type": "harmonic",                                    # one of 5
    "scope":     {"level": "song", "start_s": 0.0, "end_s": T},
    "provenance_pointers": [
        {"transcription_event_id": <32-hex from M-TRANS-1>,
         "measure_range": [0, N],
         "clip_id": <16-hex from M-INGEST-1>},   # optional
    ],
    "confidence": 0.87,                                         # [0, 1]
    "parameters": {...},                                         # typed per rule_type
}

# 2. Derive the deterministic id.
rid = derive_rule_id(rule_content)

# 3. Fill in event-level fields.
row = {
    "event_type":        "rule",
    "schema_v":          1,
    "event_id":          uuid.uuid4().hex,        # 32-hex
    "ts":                <ISO8601 UTC>,
    "extractor":         "score_bridge_v1",
    "extractor_version": "1.0.0",
    "rule_id":           rid,
    **rule_content,
}

# 4. Write. Raises LedgerError on validation failure or duplicate.
try:
    write_rule(row)
except LedgerError as e:
    log.warning("rule rejected: %s", e)          # decide: skip, refine, or supersede
```

**Schema-version discovery.** Extractors read `schema_v` from the
top-level `const` in `scripts/rules/schema/rules_v1.json`. When v2
lands, the schema filename bumps to `rules_v2.json`, `schema_v` becomes
a `const 2`, and this module gains a version-switch. The `$id`
namespace convention (`https://music-gen/rules/rules_vN`) enforces this.

**To replace a rule (refinement, correction):** never edit. Instead:
(i) `write_rule(new_row_with_fresh_rule_id)`; (ii)
`write_supersede({event_type: "supersede", ..., supersedes_rule_id: old_id, new_rule_id: new_id, reason: "…"})`.

## 8. Interface for M-GEN-1's forthcoming generator

```python
from scripts.rules.ledger import effective_rules

rules = effective_rules()                            # only non-superseded rows
by_type = {rt: [r for r in rules if r["rule_type"] == rt]
           for rt in ("harmonic", "rhythmic", "melodic", "form", "arrangement")}

# by_type["harmonic"] is a list[dict]; each dict has a typed "parameters"
# block guaranteed to match §3.4.
```

The generator filters by `rule_type`, walks the typed parameters, and
composes a fresh score. No transcription IDs or clip IDs are required
to consume rules — provenance is provenance, not input. If the
generator ever needs to trace a rule back to its source, the
`provenance_pointers` list is the path back into M-TRANS-1 and
M-INGEST-1.

## 9. Known limitations and next-cycle refinements

1. **Confidence is uncalibrated.** `[0, 1]` is a scale, not a
   probability. Calibration is a task for M-EAR-1 (or a dedicated
   confidence-calibration sub-milestone) once rated audio arrives.
2. **Roman-numeral chord grammar is diatonic + secondary dominants.**
   Modal interchange, borrowed chords, and jazz-style extensions
   beyond `maj7|m7|7|dim|aug|m` fail the regex today. Extend the
   pattern when M-SCORE-1 shows real coverage need.
3. **PCH sum-to-1 is float-tolerant.** `abs_tol=1e-6`. Extractors that
   accumulate histograms in fp32 must renormalize before writing.
4. **`measure_range` bound checking is not cross-checked against
   transcription events.** JSON Schema requires `[int ≥ 0, int ≥ 0]`
   and Layer 2 accepts it as-is; verifying `measure_range[1] > [0]`
   *and* lies within the referenced transcription's measure count is
   deferred until M-TRANS-1 defines the transcription-event shape.
5. **No cross-song rule composition.** A rule's `scope` binds it to a
   single song's timeline. Aggregate/motif rules that span multiple
   songs will need a v2 field (`song_ids: [<16-hex>, …]`).
6. **`layer_events[i].t_s ≤ scope.end_s` is a soft Layer-2 check.**
   JSON Schema can't reference `scope.end_s` from a sibling field
   portably. Layer 2 catches it; a schema-only consumer would not.
7. **Ledger is single-writer.** No file locking. Concurrent writers on
   the same JSONL file would corrupt line boundaries. Extractors run
   serially inside the campaign loop; if that ever changes, add
   `fcntl.flock` around `_append`.
8. **`extractor_version` is a free-form string.** SemVer is a convention,
   not a schema constraint. Cross-extractor comparison ("did
   extractor_v1.0.0 disagree with v1.0.1?") needs a version-parser to
   be reliable.
9. **`jsonschema` was newly added.** Version pin: `jsonschema==4.26.0`
   (see §10). If the classifier stack later rejects this version
   (unlikely: pure Python), a downgrade to 4.20+ works too.

## 10. Reproducibility

| Component | Version / path |
|---|---|
| Interpreter | `/usr/bin/python3` (sys.executable guard on every entry point) |
| `jsonschema` | 4.26.0 (installed this cycle; classifier + 90-check cross-branch test still all-PASS) |
| PyYAML | 6.0.1 |
| MIDI dependencies | absent (schema branch — no audio, no MIDI) |
| Canonical JSON | `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=True)` |
| Rule_id hash | `hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()[:16]` |
| Random seeds | none (fully deterministic) |
| Fixed timestamp in synthetic instances | `2026-08-28T00:00:00Z` (so committed files are byte-stable across regenerations) |
| Files | `scripts/rules/schema/rules_v1.json` (222 lines), `rules_v1.yaml` (370 lines, auto-generated), `validate.py` (186), `ledger.py` (193), `rule_id.py` (65), `tests/test_rules_schema.py` (413) |

### To reproduce from scratch

```bash
pip install jsonschema
/usr/bin/python3 scripts/rules/schema/examples/build_examples.py    # writes 25 synthetic instances
/usr/bin/python3 scripts/rules/schema/build_yaml.py                  # writes rules_v1.yaml + asserts round-trip
/usr/bin/python3 scripts/rules/ledger.py                             # creates empty data/rules/ledger.jsonl
PYTHONPATH=. /usr/bin/python3 tests/test_rules_schema.py             # 25/25 PASS (11 planted invalids + ledger contract + isolation)
PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py # 90/90 PASS (was 68 before this cycle)
```
