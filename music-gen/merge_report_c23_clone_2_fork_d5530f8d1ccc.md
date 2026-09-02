# Merge report — c23 clone-2 fork d5530f8d1ccc — M-V3-RULES-1

Written to workspace-root fallback: the external path
`/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-2/merge_report.md`
is outside the writable workspace by construction (sandbox lists it as
blocked); root-conductor territory to relay this file into the fork tree.

## Verdict
- **Milestone**: `M-V3-RULES-1`  (first activation of the rules-hashed
  contract for the M-V3 arc)
- **Verdict**: `V3_RULES_LANDS_pending_operator` — 15/15 tests green,
  byte-determinism ×2 proven, three-way `rubric_hash_v3_rules` chain
  byte-equal. Operator decides per FD-1 on any downstream drift.
- **Base SHA at start of cycle**: `c442ef890747447cdeeee68c2b8831d524a87365`
- **Cycle**: 23
- **Clone**: 2
- **Fork**: `d5530f8d1ccc`

## rubric_hash_v3_rules (three-way chain)
- Position A (self-hash of doc): `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`
- Position B (`data/v3/rules/rubric_hash.txt`): `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`
- Position C (`verdict.json:rubric_hash_v3_rules`): `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`

A == B == C confirmed by
`test_rubric_hash_v3_rules_three_way_byte_equality`.

## Rules artifact
- Path: `data/v3/rules/rules_artifact.jsonl`
- SHA-256: `e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`
- Self-anchor: `data/v3/rules/rules_artifact.sha256`
- Total rules: 76
  - harmonic: 18
  - rhythmic: 18
  - melodic: 18
  - form: 18
  - arrangement: 4
- Corpus songs covered (four operator-approved):
  `31a164f845f8e27e` (CG), `51e433ade2a845e1` (Rome),
  `252eb21ce7df7328` (WIG), `cdd2717e52820ff6` (Disco A).

## Byte-determinism proof
Two fresh `tempfile.mkdtemp()` runs under the pinned env produced the
same SHA:
- run0 sha=`e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`
- run1 sha=`e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`
- `EQUAL` (see `test_byte_determinism_two_fresh_runs`).

## Env pins in effect
`PYTHONHASHSEED=0`, `TZ=UTC`, `LC_ALL=C.UTF-8`,
`SOURCE_DATE_EPOCH=1756463424`, interpreter `/usr/bin/python3`.

## Fetchability probe (survey-open-source-first)
`data/v3/rules/fetchability_ladder.jsonl` — one row per candidate, all
with `no_fetch_attempts: true`:
- `jsonschema` — on_disk
- `mingus`     — on_disk / not_on_disk (per probe, ImportError recorded)
- `music21`    — probed
- `sklearn`    — probed

The prototype uses stdlib + `mido` (pre-existing v3 dep); no library
that would have required a network fetch is imported.

## Test suite (15/15 green)
`tests/test_v3_rules_deterministic_extractor.py`

1. test_interpreter_guard_present — PASS
2. test_no_prng_imports — PASS
3. test_no_sidecar_nonfactor_imports — PASS
4. test_no_vst3_state_apis — PASS
5. test_rubric_doc_mtime_before_scripts — PASS
6. test_rubric_hash_v3_rules_three_way_byte_equality — PASS
7. test_fetchability_ladder_no_fetch_attempts — PASS
8. test_rules_artifact_schema_conforms_to_c9_types — PASS
9. test_per_stem_provenance_present — PASS
10. test_byte_determinism_two_fresh_runs — PASS
11. test_rules_artifact_self_anchor_sha — PASS
12. test_readonly_anchor_preservation — PASS
13. test_c9_c15_c40_ledgers_untouched — PASS
14. test_ledger_events_have_agent_and_clone_fields — PASS
15. test_corpus_covers_four_operator_approved_songs — PASS

## Anchor preservation
`data/v3/rules/anchor_preservation_c23.json` — 33 anchors, all
pre==post byte-exact. Includes c9/c15/c40 ledgers, c22 v3-spine driver
+ env_pin, all four operator-approved deliveries' `panel.json` +
`operator_section/*.json` + `merged.mid`, `render_stem.py`
(`214372d9…5b2b`), c9 rules_v1 schema files.

## Ledger events (6 named + 2 housekeeping, under M-V3-RULES-1/*)
Path: `data/v3/rules/ledger_c23_clone_2.jsonl` — 8 events, each with
`agent=worker`, `agent_original=worker-clone-2`, `clone=2`,
`fork=d5530f8d1ccc`, `cycle=23`:

1. `M-V3-RULES-1/rubric-committed`
2. `M-V3-RULES-1/fetchability-probed`
3. `M-V3-RULES-1/extractor-implemented`
4. `M-V3-RULES-1/artifact-emitted`
5. `M-V3-RULES-1/byte-det-verified`
6. `M-V3-RULES-1/verdict-emitted`
7. `_archive/cycle-23-scratch-clone-2`
8. `_infra/adopt-cycle23-tests-clone-2`

The clone-namespace suffix `-clone-2` is applied to the two
housekeeping events per c32 fanout-namespace convention / c33 harness
guard.

## Files produced this cycle (worker outputs only)
- `docs/v3_rules_deterministic_extractor_spec_c23.md`         (rubric doc)
- `data/v3/rules/rubric_hash.txt`                             (pin B)
- `scripts/v3_rules/__init__.py`                              (package)
- `scripts/v3_rules/extract_rules.py`                         (extractor)
- `tests/test_v3_rules_deterministic_extractor.py`            (15 tests)
- `data/v3/rules/fetchability_ladder.jsonl`                   (probe)
- `data/v3/rules/rules_artifact.jsonl`                        (artifact)
- `data/v3/rules/rules_artifact.sha256`                       (self-anchor)
- `data/v3/rules/anchor_preservation_c23.json`                (33 anchors)
- `data/v3/rules/verdict.json`                                (verdict + pin C)
- `data/v3/rules/ledger_c23_clone_2.jsonl`                    (8 events)
- `merge_report_c23_clone_2_fork_d5530f8d1ccc.md`             (this file)

## Fixed decisions honored
- FD-1: byte-det failure → operator decides. Not triggered (SHA-equal ×2).
- FD-6: panel is NEVER a LANDS gate; operator ear is only authority.
- c9 rule schema preserved; per-stem provenance added, whitelist untouched.
- c22 unified driver + env_pin manifest untouched (anchor pre==post).
- c32 fanout-namespace suffix `-clone-2` on housekeeping events.
- c33 harness-clone-namespace-guard respected (writes under
  `data/v3/rules/` shard; no c9/c15/c40 ledger mutation).
- c48 env-var flags default-OFF (never referenced).

## Anti-patterns explicitly NOT attempted
- VST3 state APIs (c31/c35 forbidden; AST test scan clean).
- M-EAR-1 Path A under N=55 (c22/c23/c25 invalidated).
- CLAP fetch (c11 HF SSL failure).
- Hand-composing songs (`agentic_composition:true` fallback only per c23).
- PRNG anywhere in extraction path (AST + attribute scan clean;
  `parameters_random_state: 0` static field recorded per rule).

## Blockers / operator-decides
None. Byte-det passed, three-way chain byte-equal, anchors preserved,
c9/c15/c40 ledgers untouched. LANDS is `pending_operator` review of the
extractor design + rules_artifact.jsonl content per FD-1/FD-6.
