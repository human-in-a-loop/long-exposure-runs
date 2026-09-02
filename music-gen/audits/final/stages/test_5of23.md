# Final Audit — Stage 29 of 48 (Test 5 of 23)

**Stage:** test (5/23) — infrastructure invariants + provenance-chain probes
**Working dir:** `/home/user/long-exposure-runs/music-gen`
**Preceding stage:** test_4of23 (F16–F19: egress schema drift, anchor-preservation schema drift, rubric-mtime discipline HELD, report-coverage gap at c19/c41/c42 + c56-58 report ahead of ledger)

## Probes run this stage

1. **c48 ledger-writer invariants** — line-745 `event_id` under flag OFF + three-way `rubric_hash` byte-equality for `_infra/harness-and-writer-hardening-v3`.
2. **Rated-corpus manifest ↔ on-disk audio provenance** — schema check + per-band count reconciliation between `corpus/ratings/ratings_manifest.tsv` and `corpus/ratings/{4,5,6,7}/*.mp3`.
3. **Test-suite collection surface** — `ast.parse` sweep on all 74 `tests/test_*.py`.
4. **`_run/post-merge-integration-*` completeness** — cross-check each named fanout fork against a dedicated integration ledger event.

## Findings

| #    | Severity | Verdict    | Summary |
|------|----------|------------|---------|
| F20  | MAJOR    | CONFIRMED  | `long_exposure/` source tree missing from disk despite c14/c22/c33/c48 chain edits |
| F21  | MODERATE | CONFIRMED  | Ratings manifest schema drift: 80 rows (bands 4/5/6) vs 43 on-disk mp3s (bands 4/5/6/7) |
| F22  | INFO     | CONFIRMED  | Test-suite parse-clean 74/74; plain-assert pattern common (documented) |
| F23  | MODERATE | CONFIRMED  | 3 forks lack dedicated `_run/post-merge-integration-*` events (c31 cfc5009, c33 4595e91, c34 43802db) |

## F20 — `long_exposure/` source tree missing (MAJOR, CONFIRMED)

**Evidence:**
- `long_exposure/workspace_bootstrap.py`: **file not present** anywhere in the repo (`glob "**/workspace_bootstrap.py" == []`).
- `long_exposure/tools/_ledger_schema.py`: **file not present**.
- `long_exposure/` directory does not exist at repo root; no `scripts/long_exposure`, `workspace/long_exposure`, or `src/long_exposure` alternates present.
- Yet `data/harness_and_writer_hardening_v3/verdict.json.verdict == "HARNESS_AND_WRITER_HARDENING_LANDS"` and three-way `rubric_hash` byte-equality PASS: doc SHA-256 == `rubric_hash.txt` content == `verdict.rubric_hash` (all `17c5025504d1aca9…`).
- Line-745 event_id on-disk (`_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1`) equals the expected UUID5 `658231db-5d86-56e5-8ca9-2a9bed7fdf9f` under c48 sub-fix-2 flag OFF — matches the ledger's pinned claim.

**Interpretation:** the c48 verdict artifacts (verdict.json, rubric_hash.txt, baseline_replay_manifest.jsonl, and the line-745 event_id snapshot on disk) are all internally consistent, so the c48 work **did land** at the time it was recorded. But the source-code edits it made to `long_exposure/workspace_bootstrap.py` and `long_exposure/tools/_ledger_schema.py` cannot be inspected because the whole tree is gone. Three possibilities:

1. **`long_exposure` is installed as a Python site-package** (via `pip install -e long_exposure/` earlier, then the source dir deleted). `python3 -m long_exposure.tools.promise_check .` would still import from `site-packages`. This is the least alarming reading and consistent with the pytest-less test-invocation pattern (`PYTHONPATH=. /usr/bin/python3 …`).
2. **Source moved or reorganized** and the ledger's file-path claims are stale. Ledger integrity is unaffected but code review is impaired.
3. **Source was accidentally deleted post-c48** and current promise-check runs are relying on cached bytecode.

**Impact:** the c14/c22/c33/c48 infrastructure-hardening chain — the campaign's SSoT for ledger-schema invariants, per-clone namespace guard, and env-var toggle contracts — is un-auditable at source level from this working copy. All downstream claims that reference `long_exposure/*` file SHAs cannot be re-verified this cycle. Follow-up needed from operator to clarify install path.

**Not a fix:** audit-only; but this belongs in the final report §Residual debt as the top item.

## F21 — Ratings manifest schema drift vs on-disk corpus (MODERATE, CONFIRMED)

**Evidence:**
- `corpus/ratings/ratings_manifest.tsv`: 80 rows with columns `rating, playlist_id, video_id, title, duration_s, url`. **No `audio_path`, no `audio_sha256`, no `on_disk_present` column.** Per-band tally: 20 band-4, 30 band-5, 30 band-6, **0 band-7**.
- `corpus/ratings/{4,5,6,7}/*.mp3` on-disk: **10 band-4 + 10 band-5 + 13 band-6 + 10 band-7 = 43 mp3s**.

**Discrepancies:**
1. **Cardinality asymmetry** — manifest registers 80 songs (would-be pool after egress unblock); disk has 43 (subset the operator delivered directly). c45 `M-EAR-1/real-label-training-v2` acknowledges the "43/80 corpus caveat" — the pipeline is honest about it.
2. **Band-7 provenance gap** — 10 band-7 mp3s exist on disk (referenced by c37 `M-RECREATE-1/first-real-audio-clone-0` using `corpus/ratings/7/016__LOCAL__05_02.mp3`) but **band-7 is not represented in the manifest at all**. Provenance chain from manifest → audio breaks entirely for band-7.
3. **No cross-reference column** — consumers of the manifest cannot tell which of the 80 rows are downloadable-vs-already-delivered without walking the disk.

**Impact:** the manifest is a registration document, not an execution manifest. The two data structures serve different purposes but the boundary is not codified. A downstream reader consuming the manifest alone would miss band-7 entirely and would over-count the delivered corpus by 37 (80 − 43). c46 mapping-clarified paragraph on rubric-improvement thresholds partly compensates, but a first-class `on_disk_present` + `disk_path` + `disk_sha256` column set on the manifest (or a sibling `on_disk_manifest.tsv`) would close the gap cleanly.

## F22 — Test-suite collection surface (INFO, CONFIRMED)

**Evidence:** `ast.parse` sweep of all 74 `tests/test_*.py`:
- **74/74 parse-clean** (zero syntax errors).
- 3 most recent (all c53–c54): `test_rc10_drums_bass.py` (15 test funcs + 1 TestClass), `test_rc10_other_vocals_impl.py` (0 test funcs, 0 TestClasses — uses plain-assert pattern `_t(name, cond, detail)` documented at the module docstring), `test_rc10_guitar_piano.py` (19 test funcs).

**Note:** the plain-assert invocation pattern (`PYTHONPATH=. /usr/bin/python3 tests/test_<name>.py`) was formalized at c6 for `test_rules_schema.py` (per POR `M-RULES-1/schema/tests`) and remains the dominant pattern through c54. Not a defect; documented and enforced by the interpreter-guard convention.

## F23 — post-merge-integration event completeness (MODERATE, CONFIRMED)

**Evidence:** 23 `_run/post-merge-integration-*` events in ledger. Cross-referenced against fanout forks the POR mentions:

| Cycle | Fork | Integration event? |
|---|---|---|
| c31 | cfc5009aca96 | **MISSING** (per POR: reconciliation folded into `_infra/fanout-namespace-convention` c32 codification, no dedicated `_run/*` row) |
| c33 | 4595e91f7574 | **MISSING** |
| c34 | 43802db1a81c | **MISSING** |
| c35 | 07063458736e | present |
| c36 | 87da4f517029 | present |
| c37 | 675abd086911 | present |
| c38 | 33a2a8003c84 | present |
| c47 | 420a6b028dfb | present |
| c48 | multiple | `_run/post-merge-integration-cycle-48-reconciliation` (cycle-based, not fork-based) |
| c51 | 38eba9f21a61 | `_run/post-merge-integration-cycle-51` (cycle-based) |
| c53 | 18817b483ed4 + bdd7bb47f1b5 | `_run/post-merge-integration-cycle-53-54-rc10` (cycle-based, combined) |

**Impact:** c31 gap is documented (POR explicitly says the c32 codification event absorbed it). c33/c34 gaps are undocumented — those cycles ran substantive branches (c33 Branch A + Branch B palette-render machinery; c34 palette_schema_v2 + cross-seed + palette-driven-batch-v1) whose merge-time reconciliation is invisible in the ledger's `_run/*` family. Bookkeeping gap only — the substantive work landed (verified by other test stages). Naming-convention drift between fork-based (`_run/post-merge-integration-fork-<hash>`) and cycle-based (`_run/post-merge-integration-cycle-<N>[-suffix]`) started at c48; a canonical adoption note is not on the ledger.

## Gate check (test stage)

- **All findings classified?** YES — F20 MAJOR, F21 MODERATE, F22 INFO, F23 MODERATE.
- **Any new issues introduced?** NO — read-only probes throughout.
- **Regressions in adjacent behavior?** N/A — audit-only.
- **Every fix verified?** N/A — no fixes attempted.

## What's next (stage 30 = test 6/23)

Planned probes:
1. **`long_exposure/` install-path recovery** — check `pip show long_exposure`, `sys.path`, and `python3 -c 'import long_exposure; print(long_exposure.__file__)'` to answer F20's install-location question.
2. **Rubric-hash chain sample-verify** — pick 5 rubric doc / verdict pairs from c37/c45/c48/c51/c53 and confirm the three-way byte-equality invariant holds on-disk.
3. **`docs/*_report.md` ↔ ledger event coverage** — sample 5 recent reports and verify each references at least one landed ledger event.
4. **`_infra/*-clone-N` suffix invariant** — grep all `_infra/*`, `_run/*`, `_manager/*` ids in ledger from c33+ and verify every one has a `-clone-<N>` suffix or a documented root-context.

<checkpoint>
  <stage>test (5/23) — stage 29 of 48</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~210k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran 4 infra + provenance probes. Surfaced 4 findings: F20 MAJOR (long_exposure/ source tree missing though c48 verdict + line-745 event_id + rubric_hash chain all consistent), F21 MODERATE (ratings manifest 80 rows bands 4/5/6 vs 43 on-disk mp3s bands 4/5/6/7 — band-7 has zero manifest coverage), F22 INFO (74/74 test files parse-clean), F23 MODERATE (3 forks c31/c33/c34 lack dedicated post-merge-integration events).</what-i-did>
  <next-action>Advance to test 6/23 (stage 30); probe long_exposure install-path recovery, rubric-hash chain sample-verify, report ↔ ledger coverage, clone-suffix invariant sweep.</next-action>
  <gate-check>Stage 29 file written to expected path; findings sidecar appended to findings.jsonl.</gate-check>
</checkpoint>
