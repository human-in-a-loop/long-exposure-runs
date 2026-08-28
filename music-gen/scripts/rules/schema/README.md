# M-RULES-1/schema — rules ledger schema v1

**Authoritative artifact:** `rules_v1.json` (JSON Schema draft 2020-12).
**Derived view:** `rules_v1.yaml` (mechanically produced via `build_yaml.py`;
`yaml.safe_load(yaml) == json.load(json)` at every level).

## Design in one page

- **Two row kinds**, distinguished by `event_type`: `rule` (payload rows)
  and `supersede` (rewrite pointer rows). One line per row in
  `data/rules/ledger.jsonl`. Append-only.
- **Five rule types**, distinguished by `rule_type`: `harmonic`,
  `rhythmic`, `melodic`, `form`, `arrangement`. Each has a typed
  `parameters` block enforced by an `if/then/else` chain in the JSON
  Schema. Extractors cannot hide richness in an untyped dict.
- **`additionalProperties: false` at every level.** A stray field —
  including any non-factor field like genre/artist/era — is rejected.
- **Content-addressed `rule_id`:** `"rule_" + sha256(canonical_json({rule_type, scope, sorted_provenance_pointers, parameters}))[:16]`.
  Identical content → identical id (automatic dedup); one-bit change →
  different id (never confuses refinement with a fresh rule).
- **Unknown-type policy: REJECT.** `rule_type` is an `enum` of exactly
  five values. Anything else fails Layer 1 with the enum error string.
  A future v2 could quarantine into an `unknown_type_backlog`; today we
  reject.
- **Supersede is an EVENT, never an edit.** To change a rule: (i) write
  a new rule row with the updated content (fresh rule_id); (ii) write a
  supersede row pointing (old_rule_id → new_rule_id). The old rule row
  stays on disk. `effective_rules()` filters it out.

## Two-layer validator (`../validate.py`)

- **Layer 1 (mechanical):** `jsonschema.Draft202012Validator(schema).iter_errors(row)`.
- **Layer 2 (semantic):** what JSON Schema can't express portably —
  - `scope.end_s > scope.start_s` (song/section) / `>=` (measure).
  - Melodic PCH sum-to-1 within `abs_tol=1e-6`.
  - Form-section `end_measure > start_measure`.
  - Arrangement `layer_events[i].t_s` within `scope.end_s`.
  - Cross-row: duplicate `rule_id`; supersede target existence; supersede
    self-reference.

Both layers return a **list of error strings**. Never raise on validation
failure. Every field access `.get()`-guarded (inheriting the lesson from
M-INGEST-1 provenance MODERATE-2).

## Ledger writer contract (`../ledger.py`)

- `write_rule(row)`: validate → append single line to
  `data/rules/ledger.jsonl` → `flush + fsync`. Raises `LedgerError` on
  duplicate `rule_id`.
- `write_supersede(row)`: same, requires both `supersedes_rule_id` and
  `new_rule_id` to already exist in the ledger.
- `read_ledger()`: streams rows in insertion order (append-only reads).
- `effective_rules()`: applies supersede chain; returns only non-superseded
  rules.
- File is opened **only** with `mode="a"`. Never `"w"`. Never `"r+"`.
