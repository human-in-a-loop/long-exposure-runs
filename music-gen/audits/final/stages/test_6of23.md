# Final Audit — Stage 30 of 48 (test 6/23)

- Preceding stage: 29 of 48 (test 5/23) — findings F20-F23
- Working dir: `/home/user/long-exposure-runs/music-gen`
- Expected file: `audits/final/stages/test_6of23.md` ✓

## Probes run this stage

1. **`long_exposure/` install-path recovery** — resolve import + report file locations, cross-check pip metadata / sys.path.
2. **Rubric-hash chain sample-verify** — three-way byte-equality (doc SHA == `rubric_hash.txt` == `verdict.json.rubric_hash`) on 5 cycles: c45 ear_v2, c47 ear_v2p1, c48 harness_v3, c51 rc7, c53 rc10-guitar-piano.
3. **`docs/*_report.md` ↔ ledger event coverage** — sample 7 recent shipping docs; verify each appears in some ledger event's `artifacts` list.
4. **`_infra/*-clone-N` suffix invariant** — check every infra-family emission from c33+ that involves clone/fork context for correct auto-suffix per the c33 writer guard.

## Findings

| # | Severity | Verdict    | Summary |
|---|----------|------------|---------|
| F24 | INFO | CONFIRMED | `long_exposure/` installs from sibling repo — F20 downgrade |
| F25 | INFO | CONFIRMED | Three-way rubric_hash byte-equality holds on 5/5 sampled cycles |
| F26 | INFO | CONFIRMED | 7/7 sampled docs referenced by ledger artifacts (F19 narrowed) |
| F27 | INFO | CONFIRMED | c33 auto-suffix invariant holds; 16 apparent flags all root-context |

Stage produces no new CRITICAL / MAJOR / MODERATE findings. Two prior findings materially downgrade: F20 MAJOR → INFO (source located), F19 scope narrowed to cycle-report coverage only.

---

### F24 — `long_exposure/` install-path recovery (INFO / CONFIRMED)

Direct import test:
```
IMPORT_OK      /home/user/human-in-a-loop/long-exposure/long_exposure/__init__.py
SCHEMA_OK      /home/user/human-in-a-loop/long-exposure/long_exposure/tools/_ledger_schema.py
BOOTSTRAP_OK   /home/user/human-in-a-loop/long-exposure/long_exposure/workspace_bootstrap.py
sys.path[1]:   /home/user/human-in-a-loop/long-exposure
```

**Interpretation.** The SSoT for c14/c22/c33/c48 hardening is not co-located with the run — it lives in a sibling repo (`/home/user/human-in-a-loop/long-exposure/`) that the outer orchestration harness inserts into `sys.path`. That is why F20's on-disk grep under `music-gen/` returned nothing: nothing was ever supposed to live there. Every `long_exposure.*` import in the run scripts resolves cleanly to the sibling repo's copy, which is why every c48 verdict artifact ships internally-consistent (three-way rubric_hash byte-equality, on-disk line-745 event_id `658231db-…` reproducing under flag OFF).

**Residual doc-hygiene concern (not a finding).** Neither `music_gen_long_exposure_prompt.md` nor `CLAUDE.md`/`README.md` (none present at run root beyond the prompt file) names the install location. An auditor without access to the outer harness sees a scary absence. A one-line note in the prompt would eliminate the confusion; noted for the final report's residual-debt section, not filed as a finding.

**F20 disposition.** DOWNGRADED from MAJOR → INFO. Will be re-classified in the document stage's reconciliation log.

---

### F25 — Rubric-hash chain cross-cycle (INFO / CONFIRMED)

| Cycle | Name | Doc SHA (16) | Txt SHA (16) | Verdict hash (16) | Chain |
|-------|------|--------------|--------------|--------------------|-------|
| c45   | ear_v2      | 01948b6efe6ca5e9 | 01948b6efe6ca5e9 | 01948b6efe6ca5e9 | PASS |
| c47   | ear_v2p1    | 2920875671ea98b1 | 2920875671ea98b1 | 2920875671ea98b1 | PASS |
| c48   | harness_v3  | 17c5025504d1aca9 | 17c5025504d1aca9 | 17c5025504d1aca9 | PASS |
| c51   | rc7         | 0e11f704e12c62f8*| 0e11f704e12c62f8*| 0e11f704e12c62f8 | PASS |
| c53   | rc10-gp     | c7fe33a742a98f9b | c7fe33a742a98f9b | c7fe33a742a98f9b | PASS |

\* c51 rc7 sub-leaves cite the **c50 v2 rubric** (`docs/m_recreate_2_accurate_small_set_rubric_v2.md`) — this is the plan-of-record intent (rc7 is a sub-leaf of `M-RECREATE-2/accurate-small-set-v2`). Initial NAK was operator error on my part looking for a per-branch `rc7_mix_balance_match_rubric.md` that never existed. c51 also carries its own preregistration docs (`docs/render_stem_signature_v3.md` + `docs/rc7_eq_curve_fit_method.md`) as method-pinning artifacts distinct from the umbrella rubric.

**Conclusion.** Rubric discipline is holding uniformly across the audited slice. Complements F18's mtime-discipline PASS.

---

### F26 — Report ↔ ledger coverage (INFO / CONFIRMED)

7 sampled docs, each present in at least one ledger event's `artifacts` array:

| Doc | In ledger? |
|-----|------------|
| `docs/rc7_v2_rerun_report.md` | PASS |
| `docs/rc10_guitar_piano_scorecard.md` | PASS |
| `docs/harness_and_writer_hardening_v3_rubric.md` | PASS |
| `docs/rc10_drums_bass_rubric.md` | PASS |
| `docs/ear_real_label_training_v2p1_rubric.md` | PASS |
| `docs/rc7_impl_report.md` | PASS |
| `docs/palette_driven_bare_render_report.md` | PASS |

**F19 narrowing.** F19's original phrasing ("report-coverage gaps at cycles 19/41/42") is correct as-stated but should not be read as generalized doc-ledger detachment — the shipping-doc-to-ledger link is intact where it matters. F19 will be recorded in the final report as narrowly about per-cycle summary reports, not about shipping deliverables.

---

### F27 — Clone-suffix invariant (INFO / CONFIRMED)

Scanned 287 infra-family events (`_infra/`, `_run/`, `_plan/`, `_archive/`, `_manager/`) from c33+ (post `_infra/harness-clone-namespace-guard` landing). 16 apparent violations flagged by the naïve heuristic; on manual review all 16 are legitimate root-context emissions:

- `_run/cycle_N_launched` (N ∈ {33,34,35,36}) — root-scope launch markers, one per cycle
- `_infra/adopt-fanout-artifacts-cycle{33,34}-*` — root post-merge cleanup adopting orphan artifacts
- `_run/post-merge-integration-fork-33a2a8003c84` (c38), `-420a6b028dfb` (c47) — root integrators
- `_plan/register-*-clone-namespaced-milestones` (c37, c38) — root plan updates listing per-clone rows
- `_run/cycle_44_closed` — root close marker
- `_plan/c46-line-745-supersedes-field-added` (c47) — root plan amendment

Sole edge case: `_manager/ear-sb3-statistic-degeneracy-fallback-statistic-clone-1/verdict-recorded` (c37) — `-clone-1` appears mid-path as the parent-milestone qualifier; the sub-leaf `verdict-recorded` suffix follows. Legitimate parent/child pattern; the parent segment already carries the clone attribution.

**Conclusion.** c33 writer-guard is holding correctly. 251 valid auto-suffixed events + 20 documented carve-outs + 16 root-context (correctly unsuffixed) = 287. Zero real violations. Complements F23 by confirming that the c33/c34 fork-based/cycle-based naming drift is cosmetic (report/integration events) rather than a correctness gap in the writer contract.

---

## Gate check

- [x] Every fix (this is a diagnostic stage — no fixes applied) verified against its original finding: **F20 recheck** confirms fix by resolution (import succeeds); no regression introduced.
- [x] Regressions in adjacent behavior: none — read-only probes.
- [x] New issues introduced: none.

## What's next (planned probes for stage 31 / test 7/23)

1. **`corpus/ratings/ratings_manifest.tsv` audio-band-7 gap deep-check** — verify F21's claim that band-7 has zero manifest coverage; check whether band-7 mp3s (10 on-disk) have any provenance sidecar or JSONL.
2. **`data/anchor_manifest_v1.json` freshness** — c35 froze 18 anchors, c47 added the 19th (SOURCE_DATE_EPOCH). Verify the manifest is still consistent with on-disk SHAs.
3. **`tools/stale/` inventory sanity** — `_archive/cycle-N-scratch` events claim archives; verify a sample land at correct paths under `tools/stale/`.
4. **`workspace_bootstrap.append_ledger_event` used correctly** — grep for direct `open('promise_ledger.jsonl','a')` bypasses of the writer's schema validation (must be zero).

<checkpoint>
  <stage>test</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~190k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran 4 diagnostic probes for stage 30. Located long_exposure/ install (sibling repo — downgrades F20 MAJOR→INFO), verified rubric-hash discipline on 5 cycles PASS, confirmed 7/7 sampled docs are in-ledger (narrows F19), verified c33 clone-suffix guard holding (0 real violations of 287 events).</what-i-did>
  <next-action>Stage 31 (test 7/23): band-7 provenance gap, anchor-manifest freshness, tools/stale inventory, direct-writer-bypass grep.</next-action>
  <gate-check>Continuing in test stage; stage-30 file written; 4 findings appended (F24-F27, all INFO).</gate-check>
</checkpoint>
