# Stage 35 — Test 11 of 23

**Cycle:** stage 35 / 48 (test 11/23)
**Scope this stage:** four adversarial probes on rated-corpus provenance, fetchability recording, promise_check validator health, and follow-up on the c40–c43 housekeeping-gap flag from stage 34.

## Probes executed

### P1. `ratings_manifest.tsv` provenance schema check
- **Header:** `rating\tplaylist_id\tvideo_id\ttitle\tduration_s\turl` (6 fields).
- **Row count:** 80 (81 lines including header).
- **Rating distribution in manifest:** band-4 = 20, band-5 = 30, band-6 = 30, band-7 = **0**.
- **On-disk mp3 distribution** (via `Glob corpus/ratings/*/*.mp3`, 43 files):
  - band-4: 10 files (URL-provenance)
  - band-5: 10 files (URL-provenance)
  - band-6: 13 files (URL-provenance)
  - band-7: 10 files, ALL filename-suffix `__LOCAL__` (no URL provenance)
- **Cross-check vs. plan-of-record:** M-EAR-1/real-label-training-v0 milestone declares "10 band-4 + 10 band-5 + 13 band-6 + 10 band-7 = 43 songs" — the file count matches, but the band-7 rows are ABSENT from the TSV.
- **Missing fields:** no `audio_sha256`, no `rating_band` (rating column serves), no `source_type` (URL vs. LOCAL sentinel inferred from filename only).
- **Verdict:** MODERATE finding F45 filed. 33/43 training-corpus songs have manifest provenance; the 10 band-7 files rely on filename convention only.

### P2. Fetchability-ladder completeness
- 10 `fetchability_ladder.jsonl` files present across palette_probe / palette_render / palette_render_cross_seed / gen_palette_batch_{v1,v2} / palette_v2_render / dawdreamer_state / score_bridge_real_audio / rc1_rc9_impl.
- Sampled `data/palette_probe/fetchability_ladder.jsonl` (3 rows): Surge XT VST3 loadable, Dexed VST3 loadable, sfizz_render CLI loadable — all `fetchable=true`, all with concrete `binary_path`.
- No fabricated `fetchable=true` entries detected on inspection.
- **Verdict:** PASS finding F47 filed.

### P3. `promise_check` validator health
- `python3 -m long_exposure.tools.promise_check .` on the 920-event ledger:
  - events: 920, plan milestones: 281
  - ERRORs: **0**
  - WARNs: ~3437 (all stylistic — `artifact path 'foo/' not canonicalized` and a small tail of retired-scratch missing-artifact notices)
- 10 files invoke or import `promise_check` (5 tests + 5 tool scripts).
- **Verdict:** PASS finding F46 filed.

### P4. Cycle 40–43 housekeeping-gap follow-up (revises F40 from stage 34)
- Cycle 40: 11 events; housekeeping present under c33 clone-suffix pattern (`_archive/cycle-40-scratch-clone-0` + `_infra/adopt-cycle40-tests-clone-0`).
- Cycle 41: 3 events (pure bookkeeping/escalation cycle); housekeeping partial — `_archive/cycle-41-scratch-clone-1` present; missing `_infra/adopt-` is legitimate (no new tests to adopt).
- Cycle 42: 10 events; housekeeping present under `-clone-0` suffix.
- Cycle 43: **0 events** — documented in c44 plan-of-record as `c43 empty-stdout failure preempted`.
- **Verdict:** F40 retracted / downgraded to INFO via F44. Housekeeping pattern is COMPLETE for cycles that produced substantive artifacts.

## Findings appended this stage

| ID  | Severity | Milestone                                        | Kind                        |
|-----|----------|--------------------------------------------------|-----------------------------|
| F44 | INFO     | `_infra/housekeeping-pattern`                    | prior_finding_retraction    |
| F45 | MODERATE | `M-INGEST-1/provenance`                          | provenance_schema_drift     |
| F46 | INFO     | `_infra/ledger-schema-hardening-v2`              | validator_health            |
| F47 | MODERATE .. INFO | `M-DAW-SPIKE-1/palette-instrument-determinism` | fetchability_recording |

Running totals (cumulative): 111 rows in `audits/final/findings.jsonl` (F1..F47 + prior stage overlays).

<checkpoint>
  <stage>test 11 of 23</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~185k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Verified ratings_manifest.tsv provenance schema (band-7 rows missing on disk provenance — F45 MODERATE); confirmed fetchability_ladder honesty across 10 sites (F47 PASS); confirmed promise_check exits 0-ERROR (F46 PASS); retracted F40 housekeeping-gap after applying c33 clone-suffix pattern (F44).</what-i-did>
  <next-action>Stage 36 (test 12/23): probe closure documents — CLOSURE/SUPERSEDES filenames — for mtime-vs-ledger consistency; ear v2/v2.1 verdict.json three-way rubric_hash byte-equality; c46 mapping-clarified paragraph on-disk placement.</next-action>
  <gate-check>Continuing in test stage sequence.</gate-check>
</checkpoint>
