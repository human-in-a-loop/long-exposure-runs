---
created: 2026-05-13T21:44:00Z
cycle: 14
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PUBLICBASE-2
---

# Public Baseline Prior Refresh

## Source List
- Primary MLCommons source: [13] `inference_results_v6.0` `summary_results.json`.
- Prior source-screen input: `physicalized-weights/data/public_baseline_sources.csv`; vendor rows remain secondary and are not used for calibration.
- Source fetch status: `ok`.

## MLPerf Result Fields Used
The script reads `ID`, `Submitter`, `Category`, `Suite`, `System`, `Model`, `Scenario`, `Accelerator`, `Total Accelerators`, `Performance_Result`, `Performance_Units`, `has_power`, and source location fields from primary MLCommons v6.0 result metadata.

| row | benchmark | scenario | submitter | hardware family | performance | has power |
|---|---|---|---|---|---|---|
| mlperf_v60_01 | deepseek-r1 | Server | Cisco | NVIDIA datacenter accelerator | 58553.3 Tokens/s | false |
| mlperf_v60_02 | deepseek-r1 | Server | CoreWeave | NVIDIA datacenter accelerator | 311531.0 Tokens/s | false |
| mlperf_v60_03 | deepseek-r1 | Server | Dell | NVIDIA datacenter accelerator | 46513.1 Tokens/s | false |
| mlperf_v60_04 | deepseek-r1 | Server | GigaComputing | NVIDIA datacenter accelerator | 35552.6 Tokens/s | false |
| mlperf_v60_05 | deepseek-r1 | Offline | Cisco | NVIDIA datacenter accelerator | 69251.4 Tokens/s | false |
| mlperf_v60_06 | deepseek-r1 | Offline | CoreWeave | NVIDIA datacenter accelerator | 627653.0 Tokens/s | false |
| mlperf_v60_07 | deepseek-r1 | Offline | Dell | NVIDIA datacenter accelerator | 69021.2 Tokens/s | false |
| mlperf_v60_08 | deepseek-r1 | Offline | GigaComputing | NVIDIA datacenter accelerator | 69617.4 Tokens/s | false |
| mlperf_v60_09 | deepseek-r1 | Interactive | GigaComputing | NVIDIA datacenter accelerator | 4934.65 Tokens/s | false |
| mlperf_v60_10 | deepseek-r1 | Interactive | NVIDIA | NVIDIA datacenter accelerator | 250634.0 Tokens/s | false |
| mlperf_v60_11 | gpt-oss-120b | Interactive | ASUSTeK | NVIDIA datacenter accelerator | 26005.8 Tokens/s | false |
| mlperf_v60_12 | gpt-oss-120b | Interactive | NVIDIA | NVIDIA datacenter accelerator | 677199.0 Tokens/s | false |

## Mapping To Campaign Terms
The mapping table covers programmable accelerator throughput priors, programmable accelerator energy priors, software-runtime priors, workload comparability, direct energy calibration usability, and safety-filter workload comparability. Throughput rows are bounded public priors only; they are not identical campaign workload measurements.

## Explicit Non-Mappings
- MLPerf benchmark workload differs from safety-filter feature/audit/fallback/update accounting
- no explicit comparable energy-per-request field in selected primary rows
- not the campaign safety-filter production/shadow/canary workload
- not_directly_energy_calibratable
- submitted system includes full benchmark stack, not isolated campaign software-runtime path
- No row supplies a lifecycle-valid evidence pack, measured hybrid total, accepted fast-path volume, fallback/audit/update accounting, provenance attestation, and privacy attestation.
- No energy value is inferred from throughput-only MLPerf evidence.

## Refresh Decision
| model term | action | null effect | evidence |
|---|---|---|---|
| programmable_accelerator_throughput_prior | strengthen_programmable_null | strengthens_or_preserves_programmable_baseline | primary_public_benchmark_prior |
| programmable_accelerator_energy_prior | not_calibratable_from_public_data | preserve_existing_energy_prior | blocked_direct_energy_calibration |
| software_runtime_prior | preserve_phase2_baseline | preserves_null | qualitative_context_only |
| safety_filter_workload_comparability | preserve_phase2_baseline | preserves_reopen_blocker | non_comparable_workload |
| phase2_stronger_baseline_downgrade | strengthen_programmable_null | strengthens_or_preserves_programmable_null | conservative_directional_refresh |

The conservative decision is `strengthen_programmable_null` with programmable-null effect `strengthened_or_preserved`. Phase 2 remains preserved because public MLPerf rows can affect only public programmable-baseline priors `B`, not the measured hybrid total `H`; these rows are not measured hybrid safety-filter production/shadow/canary evidence.

![conservative mapping from public MLPerf v6.0 programmable-baseline evidence to campaign model terms and directional effect on the null hypothesis.](../data/public_baseline_prior_refresh.png)

## Reproduction Commands
```bash
python3 physicalized-weights/scripts/public_baseline_prior_refresh.py
python3 physicalized-weights/tests/test_public_baseline_prior_refresh.py
file physicalized-weights/data/public_baseline_prior_refresh.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```
