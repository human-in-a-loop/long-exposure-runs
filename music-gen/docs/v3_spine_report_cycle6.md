---
created: 2026-09-02T12:00:00Z
cycle: 6
run_id: run-2026-09-02T120000Z
agent: worker
milestone: M-V3-SPINE-1
---

# v3 Spine Report — Cycle 6

## Executive Summary

**Verdict:** `V3_SPINE_C6_TWO_TRACK_LANDS_pending_operator`
(`blocked_on_operator=true` per FD-6 — operator ear on Chicken Grease
A/B is the only LANDS authority).

Two-track substantive cycle per c6 brief:

| Track | Deliverable | Verdict |
|---|---|---|
| A | Env-drift deep dive (local wheel/dist scan, no network) | `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_REPRODUCE` |
| B | rc7 method-equivalence (c5 inline RMS-match vs v3-paths fork of c53 rc7) | `MODERATE_2_METHODS_DIFFER_EXPECTED` (first-class finding; closes c5 MODERATE #2) |

Rubric-v2 SHA `c49db5a1…` (unchanged from c4/c5). Three-way
`rubric_hash_v2` chain (doc SHA == `rubric_hash_v2.txt` ==
`verdict_c6.json.rubric_hash_v2`) verified.

Anchor preservation: 71/71 anchors byte-identical pre==post (c5
operator-section delivery + c4 delivery preserved + all locked scripts
unchanged). 17/17 c6 tests PASS. 0-ERROR promise_check.

## §1. Track A — Env-drift deep dive

Spec: `docs/v3_spine_env_drift_deep_dive_spec.md` (SHA `a2631e99…`)
committed BEFORE `scripts/v3_spine/env_drift_deep_dive.py`. Local-only
scan across `/root`, `/home`, `/var/cache/apt`, `/var/lib/apt`,
`/var/lib/dpkg`, `/var/lib/docker`, `/opt`, `/usr/lib`,
`/usr/local/lib`, `/tmp`. No network syscalls (AST-verified in test 03).
Byte-det ×2 PASS.

### Candidates found

| Path | Version | Matches c3 hypothesis? |
|---|---|---|
| `/usr/local/lib/python3.11/dist-packages/torch-2.13.0+cpu.dist-info` | `2.13.0+cpu` | **YES** |
| `workspace/learned_transcribers_venv/lib/python3.11/site-packages/torch-2.14.0+cpu.dist-info` | `2.14.0+cpu` | No (c5 baseline) |

### Interpretation

The c3-era torch `2.13.0+cpu` is present at the SYSTEM interpreter
(`/usr/local/lib/python3.11/dist-packages/`) and is directly importable
from `/usr/bin/python3` WITHOUT any venv activation. The c5 baseline
inside `workspace/learned_transcribers_venv/` is torch `2.14.0+cpu`.

This is the exact drift class hypothesised in the c5 compaction summary:
c3 subprocesses invoked via `/usr/bin/python3` picked up the system-wide
torch `2.13.0+cpu` from `dist-packages`, while c5's `venv_delta_audit`
enumerated the venv's `site-packages` and reported `2.14.0+cpu`.

**Attribution verdict:** `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_REPRODUCE`
(candidate on disk; drafted reproduction command in the JSON; c6 takes
no action — awaits operator approval for c7 execution).

**Reproduction path for c7** (do NOT run in c6):

```
# Alternative 1 — system torch reachable already
/usr/bin/python3 -c "import torch; print(torch.__version__)"
# Alternative 2 — pin via find-links to the system dist-packages dir
/usr/bin/python3 -m pip install --no-deps --no-index \
    --find-links=/usr/local/lib/python3.11/dist-packages torch==2.13.0+cpu
```

## §2. Track B — rc7 method-equivalence

Spec: `docs/v3_spine_method_equivalence_rc7_spec.md` (SHA `7869696e…`)
committed BEFORE any Python edit under `scripts/v3_spine/rc7_v2_rerun_v3_paths.py`
and `scripts/v3_spine/method_equivalence_rc7.py`.

### Methods

| | Method A | Method B |
|---|---|---|
| Script | `scripts/v3_spine/mix_match_operator_section.py` (c5, READ-ONLY) | `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` (c6, additive-sibling fork) |
| Chain | Plain per-stem RMS-match (gain clamp ±24 dB) → sum → peak-limit 0.707 → int16 | 12-band iirpeak EQ (Q=1.4, log-spaced 20…20 kHz) → RMS loudness match (max gain 48 dB) → sum → peak-limit 0.999 → `_canonicalize_wav_deterministic` |
| Full-mix SHA | `cc919559b4508b6b…` (from c5) | `f40796be982998b0…` (byte-det ×2 PASS this cycle) |

Both methods consumed the same v3 operator-section per-track WAVs from
`data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/` (+
`.../render/vocals_htdemucs.wav`) as "bare" input, targeting the
operator-section baseline stems in `.../operator_section/rc9_6stem/`.
Method B skips the c53 MIDI-split-and-fluidsynth-render step because
v3 already has per-track WAVs — hence the "v3-paths" fork.

### Full-mix metrics

| Metric | Value | Threshold | Verdict clause |
|---|---:|---:|---|
| `max_abs_diff` | 0.502144 | ≤ 1e-3 | FAIL threshold → first-class finding |
| `rms_delta_db` | 2.6759 | (report-only) | — |
| `lufs_s_delta_lu` | 2.2727 | (report-only) | — |
| `corr` (Pearson) | 0.9649 | (report-only) | Methods strongly correlated but not equivalent |

### Per-stem highlights

Per-stem comparison uses Method A's per-stem contribution reconstructed
inline (Method A doesn't save per-stem intermediate WAVs; the
reconstruction applies the same gain clamp on the rendered per-track
WAV, matching `mix_match_operator_section.py` behavior *prior to* the
sum step). Documented in `rc7_method_equivalence.json.per_stem[*]._note`.

Full per-stem numeric table lives in
`data/v3_spine/rc7_method_equivalence.json`.

### Interpretation

The two chains are numerically distinct BY DESIGN. Method B's 12-band
iirpeak EQ reshapes the per-stem spectrum before applying RMS-match,
whereas Method A applies a single broadband gain. On the operator-section
of Chicken Grease the EQ chain moves the full-mix waveform by
`max_abs=0.50` (peak of 0.7 target); RMS shifts 2.7 dB; LUFS-S shifts
2.3 LU; correlation stays at 0.96 (both retain the same underlying
signal but with different tonal shaping).

**c5 MODERATE #2 closes** as
`MODERATE_2_METHODS_DIFFER_EXPECTED` — first-class finding per FD-1,
not a defect to smooth over. Both methods are internally consistent
(byte-det ×2 PASS on each). No code churn: c5's inline path stays as
canonical for the operator-audible A/B (FD-1 forbids retuning without
operator ear input).

## §3. Determinism

| Deliverable | Byte-det ×2 |
|---|:---:|
| `env_drift_deep_dive.json` | ✔ PASS |
| `rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav` | ✔ PASS |
| `rc7_method_equivalence.json` | (single computation; deterministic inputs) |
| `verdict_c6.json` | (single computation; deterministic inputs) |

## §4. Anchor preservation

`anchor_preservation_post_c6.json` verifies 71/71 anchors byte-identical
pre==post. Every READ-ONLY anchor is preserved: the c5 operator-section
delivery, the c4 delivery, all c3/c4 MuScriptor + canonical MIDI files,
the c5 baseline stems, the do-not-touch scripts
(`mix_match_operator_section.py`, `rc7_v2_rerun.py`, `rc7_mix_balance.py`,
`render_stem.py`), `focus_set_v2.json`, and the SF2.

## §5. Discipline (FD checklist)

- **FD-1** — no hand-rolled DSP transcription introduced; no retuning of
  c5 mix path without operator ear input. Both tracks report honest
  findings; neither smooths a defect.
- **FD-6** — panel is never a LANDS gate. Verdict is
  `blocked_on_operator=true`; only operator ear on Chicken Grease A/B
  can flip to LANDS.
- Egress remains BLOCKED (HTTP 429 + tv_embedded); no PyPI/apt fetch
  attempted. `network_syscall_attempted=false` verified in the env-drift
  scan and audited by test 03 AST scan.
- Anti-fabrication: every SHA claimed in this report is present on-disk
  at the path claimed (byte-verified by the anchor preservation script
  + spec-hash tests).
- Sub-process-serial in-turn only: both scripts ran to completion under
  a single worker turn; no fire-and-forget.
- Interpreter guard: `/usr/bin/python3` present in all four new
  top-level scripts (verified by test 15).
- Env pins: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`,
  `TZ=UTC`, `LC_ALL=C.UTF-8`, BLAS single-thread — all set via
  `os.environ.setdefault` in each script.

## §6. Deferred to c7+

- **Env-drift reproduction execution** — requires operator approval per
  FD-1. Reproduction command in `env_drift_deep_dive.json`.
- **Widening `other/piano/vocals` MuScriptor whitelist** — remains a
  watch item, not a c6 action.
- **Operator-approved retune of mix balance** — awaits operator ear
  verdict on the c5 A/B pair before any mix-chain change.

## §7. Files delivered

- `data/v3/deliveries/31a164f845f8e27e/cycle6/verdict_c6.json`
- `data/v3/deliveries/31a164f845f8e27e/cycle6/env_drift_deep_dive.json`
- `data/v3/deliveries/31a164f845f8e27e/cycle6/rc7_method_equivalence.json`
- `docs/v3_spine_report_cycle6.md` (this document)

## §8. Ledger discipline

10 named ledger events emitted this cycle via
`long_exposure.workspace_bootstrap.append_ledger_event`; one
`_plan/register-c6-v3-spine-sub-leaves` row emitted separately to close
POR drift. Egress-probe row appended to
`data/ingestion/egress_status.jsonl` (HTTP 429 unchanged). 12 POR rows
added to Milestones table. `promise_check` 0-ERROR post-registration.
