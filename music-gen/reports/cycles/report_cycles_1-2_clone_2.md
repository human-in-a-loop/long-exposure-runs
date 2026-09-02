---
title: "Music-Gen v3 RULES Milestone — Fanout Clone 2: First Activation of M-V3-RULES-1 (Cycles 1–2)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 RULES Milestone — Fanout Clone 2: First Activation of M-V3-RULES-1 (Cycles 1–2)

## Abstract

This report covers Cycles 1 and 2 of a fanout-clone branch spawned from the Music-Gen v3 campaign to open the M-V3-RULES-1 milestone for the first time. The clone (fork `d5530f8d1ccc`, clone 2) was assigned under the c23 operator directive's "determinism-for-generation-half" stance and the operator's 2026-09-02 "KEEP MOVING, DO NOT WAIT FOR APPROVAL" directive that closed M-V3-FOCUS-1 with three-of-three operator-ear accepts on the mandatory Chicken Grease and two focus songs (What If I Go and Disco A). The clone's scoped objective was to design and prototype a deterministic rules-extraction program over the operator-approved v3-rendered corpus — the four focus-song merged.mid deliveries from Cycles 5, 20, and 21 (Chicken Grease `31a164f845f8e27e`, What If I Go `252eb21ce7df7328`, Rome `51e433ade2a845e1`, Disco A `cdd2717e52820ff6`) — with a frozen three-way `rubric_hash_v3_rules` byte-equality chain committed before any script was written and a byte-determinism ×2 gate on the emitted rules artifact. Cycle 1 delivered the required output artifact `docs/v3_rules_deterministic_extractor_spec_c23.md` (13 058 bytes, SHA `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`), landed the prototype extractor at `scripts/v3_rules/extract_rules.py`, and emitted the rules artifact at `data/v3/rules/rules_artifact.jsonl` (47 662 bytes, SHA `e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`) — 76 typed rules across five rule types (harmonic 18, rhythmic 18, melodic 18, form 18, arrangement 4) with per-stem provenance from the v3 doctrine — plus 15/15 tests green, 33 read-only anchors preserved byte-identical, a fetchability ladder recording the survey-open-source-first library enumeration, and an internal auditor verdict `V3_RULES_LANDS_pending_operator` with `operator_ear_dependency=false` because M-V3-RULES-1 has no ear-gate. Cycle 2 was an explicit bookkeeping-only no-op cycle per the research brief; the auditor performed live SHA re-verification on every anchor with byte-exact match to the Cycle 1 delivery and closed the branch under `COMPLETE` and `[[BRANCH_COMPLETE]]`. This is the first activation of the operator's rules-hashed contract for the M-V3 arc, and it opens the campaign's generation-half by materializing a corpus of extracted rules that a subsequent M-V3-GEN-1 milestone can consume as its input.

## 1. Introduction and scope

The v3 campaign's milestone structure required M-V3-SPINE-1 (per-song per-stem reconstruction pipeline) and M-V3-FOCUS-1 (at least three focus-song accepts) to close before the downstream milestones — M-V3-CORPUS-1 (corpus breadth), M-V3-RULES-1 (rules extraction), M-V3-EAR-1 (ear model), and M-V3-GEN-1 (generation) — could open. M-V3-SPINE-1 closed at Cycle 20 with the operator's ear judgment on the Cycle 5 Chicken Grease reconstruction. M-V3-FOCUS-1 closed with redundancy across Cycles 20–21 fanout arcs and became fully operator-ear-blessed on 2026-09-02 (three-of-three accepts on Chicken Grease + WIG + Disco A). The operator's directive on the same date — "KEEP MOVING, DO NOT WAIT FOR APPROVAL" — released the campaign to open the generation-half milestones without waiting for further per-song ear judgment on the remaining PARTIAL cases (Peach Dream, Rome).

The c23 operator directive named the immediate opening as M-V3-RULES-1 under a "determinism-for-generation-half" stance: the rules-extraction step that feeds the eventual M-V3-GEN-1 generator must be byte-deterministic under fixed environment pins so that the generator's inputs are reproducible cycle over cycle. The directive also invoked the standing "survey-open-source-first" rule (enumerate candidate library dependencies before writing custom logic, with an on-disk-vs-blocked fetchability probe under the proxy that never attempts actual fetches).

This report is the merge-disposition summary for clone 2 of fork `d5530f8d1ccc`. Sibling clones in the same fork run parallel opening work on other downstream milestones; they are covered in separate reports.

The clone's scoped objective as issued:

- **Pin the rubric document** `docs/v3_rules_deterministic_extractor_spec_c23.md` before any script under `scripts/v3_rules/`, with a three-way `rubric_hash_v3_rules` byte-equality chain (doc SHA == `data/v3/rules/rubric_hash.txt` content == verdict field).
- **Enumerate constraint/grammar/statistical-sampler libraries** (music21, mingus, jsonschema-driven grammar, sklearn) via a fetchability probe under the proxy — no fetch attempts, `fetchability_ladder.jsonl` records what is on disk versus blocked.
- **Prototype `scripts/v3_rules/extract_rules.py`** that reads the four operator-approved deliveries read-only and extracts typed rules per the c9 rule schema (harmonic, rhythmic, melodic, form, arrangement) but with per-stem provenance from v3 doctrine.
- **Emit** `data/v3/rules/rules_artifact.jsonl` plus a self-anchor `rules_artifact.sha256`.
- **Prove byte-determinism ×2**: two fresh `tempfile.mkdtemp()` runs produce byte-identical `rules_artifact.jsonl`.
- **Preserve read-only predecessor ledgers** (c9 `data/rules/ledger.jsonl`, c15 `ledger_i3_dminor.jsonl`, c40 `ledger_rated_corpus.jsonl`) unchanged; write only to the fresh `data/v3/rules/` shard.
- **Hygiene**: interpreter guard `/usr/bin/python3`, zero PRNG imports (or explicit `random_state=0` recorded in the artifact), zero `sidecar_nonfactor` imports, zero VST3 state APIs.
- **Test suite** at `tests/test_v3_rules_deterministic_extractor.py` with at least 12 of 15 tests passing.
- **Six named plus two housekeeping ledger events** under `M-V3-RULES-1/*`.

The required output artifact is `docs/v3_rules_deterministic_extractor_spec_c23.md`.

## 2. Cycle 1: full M-V3-RULES-1 opening

### 2.1 Rubric freeze (before any script)

`docs/v3_rules_deterministic_extractor_spec_c23.md` (13 058 bytes, SHA `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`) was committed before any script under `scripts/v3_rules/`, with the mtime hard-verified. Its pinned hash file at `data/v3/rules/rubric_hash.txt` carries the same SHA verbatim. The rubric defines the extractor's five rule types (harmonic, rhythmic, melodic, form, arrangement), the per-stem provenance schema extending the c9 rule schema with the v3 doctrine's stem-level annotations, the byte-determinism ×2 mandatory sub-clause, the fetchability-ladder survey requirements, and the acceptance rule that panel measurements are never a LANDS gate (FD-6 continues to hold on M-V3-RULES-1 even though the milestone has no ear-gate).

### 2.2 Fetchability ladder (survey-open-source-first)

The clone probed the on-disk availability of four candidate library families named by the directive without attempting any network fetch, and recorded the outcomes at `data/v3/rules/fetchability_ladder.jsonl` (484 bytes). The chosen implementation strategy per the ladder outcomes: pure stdlib plus `mido` (already vendored via the campaign's mido 1.3.3 pin), no music21, no mingus, no jsonschema-driven grammar, no sklearn. This decision minimizes external dependency surface while satisfying the deterministic-extraction contract.

### 2.3 Prototype extractor and rules artifact

`scripts/v3_rules/extract_rules.py` reads the four operator-approved deliveries as read-only inputs:

- Chicken Grease (`31a164f845f8e27e`) — merged.mid from Cycle 5, operator-blessed on 2026-09-02.
- What If I Go (`252eb21ce7df7328`) — merged.mid from Cycle 21 clone-1 restart (SHA `a93f5c2ae16e5cace42b98886f6ce3eae4bb47393bef9d2abe631aadbe526578`).
- Rome (`51e433ade2a845e1`) — merged.mid from Cycle 20 clone-1 (SHA `c28b8686684fddfc841a27e96e299a93f1099fe99a5de4e461935ff2a9cfcd8a`).
- Disco A (`cdd2717e52820ff6`) — merged.mid from Cycle 21 clone-0 (SHA-16 `7e6f131f07f0d33c`).

Determinism mechanism: pure stdlib plus mido; canonical JSON serialization via `_canonical_json(sort_keys=True, separators=(",",":"))`; fixed extraction timestamp `2026-09-02T00:00:00Z`; content-hashed `rule_id` per rule (16-hex derived from the canonical parameters); explicit `parameters_random_state=0` recorded per rule; no PRNG imports; no rendering; no plugin state.

Emitted rules artifact `data/v3/rules/rules_artifact.jsonl` (47 662 bytes, SHA `e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`): 76 rules total across five rule types with the per-stem provenance schema:

| Rule type | Count |
|---|---:|
| harmonic | 18 |
| rhythmic | 18 |
| melodic | 18 |
| form | 18 |
| arrangement | 4 |

Each rule row carries: `event_type: "rule"`, `event_id` (16-hex content hash), `rule_id` (16-hex content hash), `rule_type`, `extractor` (extractor family, e.g. `extract.arrangement`), `extractor_version` (`v3-rules-c23-1`), `parameters` (rule-type-specific typed body), `parameters_random_state: 0`, `provenance_pointers` (array pinning source song SHA-16, stem name, MIDI track index, PPQ, measure range), `scope` (level and time-window), `schema_v: 1`, `confidence` (deterministic per-rule score, e.g. 0.65 on arrangement rules with sensible window coverage), and `ts` (fixed `2026-09-02T00:00:00Z`).

Sample rule (arrangement, first row on WIG):

```
{
  "rule_type": "arrangement",
  "extractor": "extract.arrangement",
  "extractor_version": "v3-rules-c23-1",
  "parameters": {
    "n_windows": 2,
    "window_bars": 4,
    "windows": [
      {"active_stems": ["bass","drums","piano","vocals","other"], "window_bar_start": 0},
      {"active_stems": ["piano","vocals","other"], "window_bar_start": 4}
    ]
  },
  "provenance_pointers": [{
    "song_sha16": "252eb21ce7df7328",
    "stem": "full_mix",
    "midi_track_index": -1,
    "midi_ticks_per_beat": 480,
    "measure_range": [0, 6]
  }],
  "rule_id": "rule_5be3c9c61efabc51",
  "confidence": 0.65,
  "parameters_random_state": 0,
  "ts": "2026-09-02T00:00:00Z",
  "schema_v": 1
}
```

Self-anchor at `data/v3/rules/rules_artifact.sha256` (65 bytes, SHA-16 `25946f7d5b80874d`) — a plain-text sidecar recording the artifact SHA for downstream cross-checking.

### 2.4 Byte-determinism ×2

The extractor was run twice into fresh `tempfile.mkdtemp()` directories under identical environment pins. Both runs produced the same artifact SHA `e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`. The verdict records this in `byte_determinism = { runs: 2, sha_equal: true, run_sha: "e19fb205…" }`. Byte-determinism ×2 gate PASS.

### 2.5 Anchor preservation

`data/v3/rules/anchor_preservation_c23.json` (5 588 bytes) records the read-only snapshot of 33 predecessor anchors, all matching pre-versus-post byte-identically. The three named read-only predecessor ledgers — c9 `data/rules/ledger.jsonl`, c15 `ledger_i3_dminor.jsonl`, c40 `ledger_rated_corpus.jsonl` — are all preserved unchanged (`all_match=true`). Writes to the fresh `data/v3/rules/` shard did not touch any predecessor tree.

### 2.6 Test suite

`tests/test_v3_rules_deterministic_extractor.py` — 15 cases, 15/15 PASS. Cases cover: three-way rubric hash chain byte-equality; extractor imports without side effects; per-rule schema validation; per-rule content-hashed `rule_id` reproducibility; byte-determinism ×2 assertion (running the extractor twice and comparing SHAs); interpreter guard `/usr/bin/python3` in the extractor's shebang; no PRNG imports (AST scan for `random`, `numpy.random`); no `sidecar_nonfactor` imports; no VST3 state APIs (AST scan for `get_state`, `set_state`, `save_state`); read-only preservation of the c9, c15, c40 predecessor ledgers; fetchability ladder shape; rules artifact non-empty; per-rule provenance-pointer non-empty; rule-type distribution matches the verdict's `n_rules_by_type` block; `parameters_random_state=0` present on every rule.

### 2.7 Verdict

`data/v3/rules/verdict.json` (17-key schema) emitted with:

- `milestone = M-V3-RULES-1`
- `cycle = 23`, `fork = d5530f8d1ccc`, `clone = 2`
- `rubric_hash_v3_rules = e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5` (three-way chain byte-equal at document SHA == `rubric_hash.txt` content == verdict field)
- `corpus_song_sha16s = [31a164f845f8e27e, 252eb21ce7df7328, 51e433ade2a845e1, cdd2717e52820ff6]`
- `n_rules_total = 76`; `n_rules_by_type = { harmonic: 18, rhythmic: 18, melodic: 18, form: 18, arrangement: 4 }`
- `rules_artifact_sha256 = e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`
- `byte_determinism = { runs: 2, sha_equal: true, run_sha: "e19fb205…" }`
- `tests_pass_over_total = [15, 15]`
- `extractor_version = v3-rules-c23-1`; `extract_ts_iso = 2026-09-02T00:00:00Z`
- `operator_ear_dependency = false` (M-V3-RULES-1 has no ear-gate); `panel_is_never_lands_gate = true`
- `env_pins = { PYTHONHASHSEED: 0, SOURCE_DATE_EPOCH: 1756463424, TZ: UTC, LC_ALL: C.UTF-8 }`
- `notes` array: first activation of rules-hashed contract for M-V3 arc; extends c9 rule schema with per-stem provenance from v3 doctrine; no PRNG present, `parameters_random_state=0` recorded per rule; panel is never a LANDS gate (FD-6); byte-determinism failure would be operator-decides per FD-1.

The verdict schema deliberately omits a `verdict` string field. This is disclosed honestly as MODERATE #2 for c24 handoff — the auditor's internal verdict of `V3_RULES_LANDS_pending_operator` (accepted at the prior turn) is recorded in the merge-report narrative, and downstream reporting can materialize a `verdict` label from the schema in a future cycle.

### 2.8 Housekeeping ledger

Eight events emitted to the shadow ledger `data/v3/rules/ledger_c23_clone_2.jsonl` (3 055 bytes): six named substantive `M-V3-RULES-1/*` rows plus two housekeeping. The recurring shadow-ledger drift pattern (MINOR-1 across the c20/c21/c22 fanout arcs) reproduces here: rows land in the shadow ledger and await concat into the primary `promise_ledger.jsonl` at post-merge integration per the c33/c48 auto-suffix concat path.

### 2.9 Required output artifact

`docs/v3_rules_deterministic_extractor_spec_c23.md` (13 058 bytes, SHA `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`) landed under `docs/` per the directive. Merge report at workspace-root fallback path `merge_report_c23_clone_2_fork_d5530f8d1ccc.md` (6 542 bytes) for root-conductor `cp` to the intended fanout path `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-2/merge_report.md` at merge time (same c20/c21 clone-2 precedent for the workspace-sandbox path relocation).

## 3. Cycle 2: bookkeeping-only no-op and branch closure

Cycle 2's research brief was an explicit bookkeeping-only no-op mandate: zero writes, zero anchor touches, zero manufactured scope; the substantive work of Cycle 1 is complete and further activity would violate the no-null-cycle-validation rule and the anti-Hold-Pattern invariant. The worker honored the mandate verbatim: zero writes performed; zero new files under `scripts/v3_rules/`; zero writes under `data/v3/rules/`; zero `tests/test_v3_rules_*` edits; zero new ledger events.

The Cycle 2 auditor performed live SHA re-verification against every anchor from the Cycle 1 delivery:

| Anchor | Live SHA-16 | Byte-match |
|---|---|:---:|
| `docs/v3_rules_deterministic_extractor_spec_c23.md` | `e81ff589200f6d6b` (13 058 B) | ✓ |
| `data/v3/rules/rubric_hash.txt` content | `e81ff58920 0f6d6b…3d71e5` | ✓ |
| `data/v3/rules/verdict.json`.rubric_hash_v3_rules | `e81ff58920 0f6d6b…3d71e5` | ✓ |
| `data/v3/rules/rules_artifact.jsonl` | `e19fb205b282dabb` (47 662 B) | ✓ |
| `data/v3/rules/rules_artifact.sha256` | `25946f7d5b80874d` (65 B) | ✓ present |
| `data/v3/rules/ledger_c23_clone_2.jsonl` | 3 055 B on disk | ✓ present |
| `data/v3/rules/fetchability_ladder.jsonl` | 484 B on disk | ✓ present |
| `data/v3/rules/anchor_preservation_c23.json` | 5 588 B on disk | ✓ present |
| `merge_report_c23_clone_2_fork_d5530f8d1ccc.md` | 6 542 B on disk | ✓ present |

Three-way rubric_hash_v3_rules chain byte-equal at `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`. Every sufficiency criterion in the fanout-clone directive is met on disk. Every anchor is unchanged. The clone's substantive scope is genuinely exhausted.

Under the `<no-null-cycle-validation>` rule the auditor issued `COMPLETE` with `[[BRANCH_COMPLETE]]`. The three MODERATE and one MINOR c24 handoff items (shadow-ledger schema rename, `verdict.json` label materialization, plain-assert test-convention policy call, main-ledger concat gated on schema rename) are explicit root-conductor / post-merge territory by construction, out of clone-2 scope.

## 4. Merge disposition and campaign-level significance

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]`. The required output artifact exists at the required path; the extractor prototype, rules artifact, self-anchor, 33-anchor preservation snapshot, 15/15 test suite, byte-determinism ×2 proof, eight-row shadow-ledger shard, and workspace-fallback merge report are all on disk unchanged. Every hard anchor byte-identical pre-versus-post live-verified across both cycles.

**Handoffs for root conductor c24+ (bookkeeping only; substantive on-disk artifacts already landed):**

1. **Shadow-ledger main-concat (MODERATE, recurring non-blocking).** Eight-row shadow-ledger shard (six substantive `M-V3-RULES-1/*` plus two housekeeping) at `data/v3/rules/ledger_c23_clone_2.jsonl` awaits concat into primary `promise_ledger.jsonl` at post-merge integration per the c33/c48 auto-suffix concat path. Gated on the schema-rename item below.
2. **Shadow-ledger schema rename (MODERATE).** The row schema in the shadow ledger uses field names that need reconciliation with the primary ledger schema before concat. Root-conductor post-merge integration step.
3. **`verdict.json` label materialization (MODERATE).** The verdict's 17-key schema deliberately omits a `verdict` string field; the auditor's internal `V3_RULES_LANDS_pending_operator` is recorded in the merge-report narrative. Downstream reporting may want to materialize a `verdict` label field from the schema in a future cycle for consistency with c4–c22 verdict shapes.
4. **Plain-assert test convention (MINOR, campaign-wide policy call).** The c23 test suite uses plain `assert` statements rather than a pytest framework. Neither convention is wrong; the choice is a policy call the root conductor may want to make explicit for consistency across future rule/generation tests.

**Campaign-level significance.** This is the **first activation of the operator's rules-hashed contract for the M-V3 arc**. The rules-extraction step that feeds the eventual M-V3-GEN-1 generator is now instantiated, byte-deterministic under fixed environment pins, and reproducing across two independent runs at the same content-hashed SHAs. The 76-rule artifact is the campaign's first materialized bridge from the operator-approved reconstruction corpus (four v3 focus songs) to the downstream generation-half milestones. Every rule carries per-stem provenance pointing back to a specific song, stem, MIDI track index, and measure range, so a subsequent M-V3-GEN-1 that samples rules from this artifact can trace each generation-step's origin back to the operator-approved source material.

The extractor's implementation choice — pure stdlib plus mido, no music21/mingus/jsonschema/sklearn — is a Fixed Decision 1 win: dependency surface minimized, determinism guaranteed by canonical JSON plus fixed timestamps plus content-hashed rule IDs, no PRNG anywhere, no plugin state, no rendering. The fetchability ladder honestly records that the survey-open-source-first rule was applied and the on-disk availability of the four candidate library families was probed without any fetch attempt.

## 5. Campaign-level state at end of arc

**M-V3-SPINE-1**: operator-ear-LANDED since 2026-09-02 on Cycle 5 Chicken Grease reconstruction. Unchanged.

**M-V3-FOCUS-1**: closed with three-of-three operator-ear accepts (Chicken Grease mandatory + WIG + Disco A) on 2026-09-02. Rome and Peach Dream remain pending operator ear but non-blocking under the operator's "KEEP MOVING" directive.

**M-V3-CORPUS-1**: opening / status held by other fork-`d5530f8d1ccc` clones (out of this clone's scope).

**M-V3-RULES-1**: **first activation LANDED at c23 clone-2 (this branch)** with rules artifact `e19fb205b282dabb…`, three-way rubric chain byte-equal at `e81ff589200f6d6b…`, byte-determinism ×2 PASS, 15/15 tests, 33 anchors preserved. No ear-gate.

**M-V3-EAR-1, M-V3-GEN-1**: downstream of M-V3-RULES-1; opening timing depends on root-conductor c24+ integration and any peer-clone parallel work in fork `d5530f8d1ccc`.

**Discipline observations.** Fifteen consecutive audits across this session with zero fabrications. Live-verification pattern (inline python3+hashlib SHA checks) unchanged. The recurring MINOR-1 shadow-ledger main-concat drift and MINOR-2 brief rubric-drift patterns are stable campaign-wide (present on c20, c21, c22, c23); workers correctly adapt to on-disk truth per FD-1; neither blocks LANDS when substantive artifacts are on disk. All banned anti-patterns (VST3 state extraction under c31 STILL_GAP + c35 SPINE, CLAP HF SSL fetch under c11, M-EAR-1 Path A audits under N=55, c37 pretty_midi merge_partial) had zero re-attempts this cycle.

## 6. Conclusions

Clone 2 of fork `d5530f8d1ccc` executed the c23 first-activation of M-V3-RULES-1 cleanly under the operator's determinism-for-generation-half stance and the standing survey-open-source-first rule. The rubric document was pinned before any script was written; the extractor prototype was implemented as pure stdlib plus mido (no external dependency surface beyond what the campaign already vendors); the four operator-approved v3 focus-song merged.mid deliveries were consumed read-only; 76 typed rules landed across five rule types with per-stem provenance in the extended c9 schema; byte-determinism ×2 held across two fresh-tempdir runs at the same content-hashed SHA; 15 of 15 tests passed; the three-way `rubric_hash_v3_rules` chain held byte-equal; every read-only predecessor ledger (c9, c15, c40) preserved unchanged. Cycle 2 was a correct bookkeeping-only no-op; the branch closes under `[[BRANCH_COMPLETE]]`.

This is the campaign's first materialization of a rules-hashed contract inside the M-V3 arc. The 76-rule artifact becomes the input a subsequent M-V3-GEN-1 milestone will consume, with each rule traceable back to a specific operator-approved song, stem, and measure range. The generation-half of the campaign is now open in a form that carries the same anti-fabrication and byte-determinism disciplines that carried the reconstruction-half from Cycle 3 forward.

## Appendix: Implementation Details

### A.1 Delivered artifacts

Required output artifact: `docs/v3_rules_deterministic_extractor_spec_c23.md` (13 058 bytes, SHA `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`).

Rules artifact: `data/v3/rules/rules_artifact.jsonl` (47 662 bytes, SHA `e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`).

Self-anchor: `data/v3/rules/rules_artifact.sha256` (65 bytes, SHA-16 `25946f7d5b80874d`).

Pinned rubric hash file: `data/v3/rules/rubric_hash.txt` (content `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5`).

Verdict: `data/v3/rules/verdict.json` (17-key schema, three-way chain byte-equal).

Fetchability ladder: `data/v3/rules/fetchability_ladder.jsonl` (484 bytes).

Anchor preservation snapshot: `data/v3/rules/anchor_preservation_c23.json` (5 588 bytes, 33 anchors, `all_match=true`).

Shadow ledger: `data/v3/rules/ledger_c23_clone_2.jsonl` (3 055 bytes, 8 events).

Extractor: `scripts/v3_rules/extract_rules.py`.

Test suite: `tests/test_v3_rules_deterministic_extractor.py` (15 cases, 15/15 PASS).

Merge report workspace-fallback: `merge_report_c23_clone_2_fork_d5530f8d1ccc.md` (6 542 bytes); root-conductor `cp` to `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-2/merge_report.md` at merge time.

### A.2 Integrity chains

Three-way `rubric_hash_v3_rules` chain: `docs/v3_rules_deterministic_extractor_spec_c23.md` SHA `e81ff589200f6d6b52d7a68f813e8120a544bfb371f8e0a45a2ac7f8793d71e5` == `data/v3/rules/rubric_hash.txt` content == verdict `rubric_hash_v3_rules` field.

Rules-artifact self-anchor: `data/v3/rules/rules_artifact.sha256` content == `data/v3/rules/rules_artifact.jsonl` SHA-256 == `verdict.rules_artifact_sha256` == `e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186`.

### A.3 Corpus consumed (READ-ONLY)

Four operator-approved v3-rendered focus-song deliveries via their `merged.mid`:

| Song | sha16 | Source cycle |
|---|---|---|
| Chicken Grease | `31a164f845f8e27e` | c5 (operator-blessed 2026-09-02) |
| What If I Go | `252eb21ce7df7328` | c21 clone-1 restart (merged.mid SHA `a93f5c2ae16e5cace42b98886f6ce3eae4bb47393bef9d2abe631aadbe526578`) |
| Rome | `51e433ade2a845e1` | c20 clone-1 (merged.mid SHA `c28b8686684fddfc841a27e96e299a93f1099fe99a5de4e461935ff2a9cfcd8a`) |
| Disco A | `cdd2717e52820ff6` | c21 clone-0 (merged.mid SHA-16 `7e6f131f07f0d33c`) |

### A.4 Rules artifact composition

76 rules total across 5 rule types:

| Rule type | Count | Extractor family |
|---|---:|---|
| harmonic | 18 | `extract.harmonic` |
| rhythmic | 18 | `extract.rhythmic` |
| melodic | 18 | `extract.melodic` |
| form | 18 | `extract.form` |
| arrangement | 4 | `extract.arrangement` |

Per-rule schema fields: `event_type`, `event_id` (16-hex), `rule_id` (16-hex content-hashed), `rule_type`, `extractor`, `extractor_version` (`v3-rules-c23-1`), `parameters` (typed body), `parameters_random_state: 0`, `provenance_pointers` (song SHA-16, stem, MIDI track index, PPQ, measure range), `scope` (level, start_s, end_s), `schema_v: 1`, `confidence` (deterministic per-rule score), `ts` (fixed `2026-09-02T00:00:00Z`).

### A.5 Byte-determinism ×2 proof

`byte_determinism = { runs: 2, sha_equal: true, run_sha: "e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186" }` recorded in the verdict. Two fresh `tempfile.mkdtemp()` runs under identical env pins produced byte-identical artifacts.

### A.6 Test suite (15/15 PASS)

Cases: three-way rubric chain byte-equality; extractor imports without side effects; per-rule schema validation; per-rule content-hashed `rule_id` reproducibility; byte-determinism ×2 assertion; interpreter guard `/usr/bin/python3`; no PRNG (AST scan for `random`, `numpy.random`); no `sidecar_nonfactor`; no VST3 state APIs (AST scan for `get_state`, `set_state`, `save_state`); read-only preservation of c9/c15/c40 predecessor ledgers; fetchability ladder shape; rules artifact non-empty; per-rule provenance-pointer non-empty; rule-type distribution matches `n_rules_by_type`; `parameters_random_state=0` on every rule.

### A.7 Fetchability ladder (survey-open-source-first)

Four candidate library families probed on-disk without any fetch attempts:

- music21 — on-disk availability recorded in `fetchability_ladder.jsonl`.
- mingus — on-disk availability recorded.
- jsonschema-driven grammar — recorded.
- sklearn — recorded.

Implementation decision per the ladder: pure stdlib + mido (already vendored via campaign's mido 1.3.3 pin).

### A.8 Anchor preservation (33 anchors byte-identical pre==post)

Recorded at `data/v3/rules/anchor_preservation_c23.json` with `all_match=true`. Includes the three named predecessor ledgers: c9 `data/rules/ledger.jsonl`; c15 `ledger_i3_dminor.jsonl`; c40 `ledger_rated_corpus.jsonl` — all byte-identical.

### A.9 Verdict schema (17 keys, `verdict` label deliberately omitted)

Keys: `byte_determinism`, `clone`, `corpus_song_sha16s`, `cycle`, `env_pins`, `extract_ts_iso`, `extractor_version`, `fork`, `milestone`, `n_rules_by_type`, `n_rules_total`, `notes`, `operator_ear_dependency`, `panel_is_never_lands_gate`, `rubric_hash_v3_rules`, `rules_artifact_sha256`, `tests_pass_over_total`.

Auditor internal verdict: `V3_RULES_LANDS_pending_operator` (recorded in merge-report narrative; MODERATE #2 handoff for materialization).

### A.10 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`. Recorded in `verdict.env_pins`.

### A.11 Handoffs for root conductor c24+

MODERATE #1 (shadow-ledger main-concat, recurring non-blocking): 8-row shadow shard at `data/v3/rules/ledger_c23_clone_2.jsonl` awaits c33/c48 auto-suffix concat.

MODERATE #2 (schema rename): shadow-ledger row schema needs reconciliation with primary ledger schema before concat.

MODERATE #3 (`verdict.json` label materialization): 17-key schema omits `verdict` string field; auditor's internal `V3_RULES_LANDS_pending_operator` recorded in merge-report narrative; downstream may materialize label in future cycle for consistency with c4–c22 verdict shapes.

MINOR (plain-assert test convention, campaign-wide policy call): c23 test suite uses plain `assert` rather than pytest framework; policy call for consistency across future rule/generation tests.

### A.12 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | 00e31c13-4488-44a0-afe8-4d7537ff24ba | e02570aa-52a3-4ebc-be9c-8a145cf021d5 | 3dba5d81-7879-4414-b9ad-07774442fefa |
| 2 | c812527b-7cfe-49ef-87a8-b6714950edfa | 9eb6eae1-39b3-47b1-b54b-39a69952f8b8 | ab6a0e07-cc65-4a46-ad8e-d730fd2e599c |

### A.13 Fanout metadata

Fork `d5530f8d1ccc`. Clone 2 of the M-V3-RULES-1 first-activation assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-2/merge_report.md` for root-conductor pickup; workspace-root fallback at `merge_report_c23_clone_2_fork_d5530f8d1ccc.md`. Sibling clones (parallel opening work on other downstream milestones) reported separately.
