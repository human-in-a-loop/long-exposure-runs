---
created: 2026-09-10T04:11:04Z
cycle: 90
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/runners-decision-c90
---

# v5 runners — orchestration reproducibility (c90 decision: option (a), checked in)

The c89 auditor's stated gap: the per-cycle pipeline runners (prune → pins/prereg → smoke → detached launch → independent
second process → flag-off regression → score ×2 → listening copies → demo delivery → figure → byte-det assembly → tests) lived
only in the worker's session scratchpad, so the ORCHESTRATION (not the outputs) was reproducible only from the pinned command
strings. Every generator command is pinned on disk regardless (`data/v5/logs/gen_iter0N_cNN.launch.json` → `generate_command`,
`data/v5/gen/byte_determinism_cNN.json` → `entries.<name>.command`); this directory closes the gap two ways:

1. `run_from_launch_json.py` — generic: prints (dry-run, default) or launches detached (`--execute --out <fresh> --log <file>`)
   the EXACT pinned command; refuses to execute on a drifted `scripts/v5/generate_v5.py` unless `--allow-drift`. Dry-run
   reproduction is byte-for-byte (asserted at c90 on the iteration-5 launch JSON and the iteration-4 flag-off entry; test_c90_close).
2. `c89/` — the ten c89 scratchpad runners copied VERBATIM (their originals were still on disk at c90 open; SHAs below). They are
   historical records of how c89 was orchestrated, not maintained tools: they hard-code the workspace path and the c89 cycle
   number, and `launch_iter05_c89.py` refuses to run if `data/v5/gen/iteration_05` already exists (it does). Re-running any of
   them is NOT a replay proof; the proofs are the byte-det records. To re-render iteration 5 into a fresh directory use (1).

| c89 runner | sha256 |
|---|---|
| `p0_prune_c89.py` | `69d7a1c3fe3b9026…` |
| `p0_pins_prereg_c89.py` | `5a8ea06bbead9246…` |
| `smoke_f5_c89.py` | `08148e173f00718c…` |
| `run_iter05_c89.py` | `4588a725ee8dee8c…` |
| `launch_iter05_c89.py` | `09386ec052ed9607…` |
| `indep_c89.py` | `e22b2c890a154b17…` |
| `flagoff_c89.py` | `15dd06ee83ef7bf5…` |
| `deliver_f5_demo_c89.py` | `2100d363b795a915…` |
| `bytedet_c89.py` | `25251682745a8929…` |
| `run_tests_c89.py` | `260f7c8c7a7180ae…` |

Nothing under `data/v5/gen/iteration_0*/`, `data/v4/generated/**` or any READ-ONLY anchor is touched by anything here unless
`--execute --in-place` is passed deliberately. `/usr/bin/python3` guard; no PRNG.
