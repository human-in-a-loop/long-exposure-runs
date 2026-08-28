---
created: 2026-08-28T15:00:40Z
cycle: 12
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/post-merge-integration-fork-ed041ef4c1dc
supersedes: fork-ddd71e9bdb0e capstone (cycle 11)
---

# Post-Merge Integration Report — fork ed041ef4c1dc (cycle 12)

## Fanout outcome

Three clones landed. Zero cross-branch file-tree overlap; each clone
wrote under a disjoint subtree and the hardened concat (delivered by
clone-1) validated every merged row at collapse time.

| Clone | Milestone                              | Verdict          | Deliverable                                    |
|-------|----------------------------------------|------------------|------------------------------------------------|
| 0     | M-RULES-1/extraction/breadth-seeds     | validated/high   | docs/rules_extraction_breadth_report.md        |
| 1     | _infra/fanout-concat-hardening         | validated/high   | docs/fanout_concat_hardening.md                |
| 2     | M-DAW-SPIKE-1/gap-closure              | validated/medium | docs/daw_spike_gap_closure_report.md           |

## Per-clone summary

### Clone 0 — M-RULES-1/extraction/breadth-seeds

Cycle-9 rule extractors (harmonic, rhythmic, melodic, form,
arrangement) run over the two M-INGEST-1/breadth-second-seeds merged
MusicXML scores (`seed_mid_50s`, `synth_060s`). **48 new typed rule
rows appended** (24 per seed) to `data/rules/ledger.jsonl`, growing
the ledger 28 → **76 rows** — 3× the ≥15-row target.

Regression contract preserved bit-for-bit: the prefix-28 SHA-256 of
the post-expansion ledger equals the cycle-9 anchor
`4fe722adde034c099ff9e65437f0d5c138cb3dd2595089960150af5c2546fc4b`.
Post-expansion whole-ledger SHA:
`a6fd53e9bf9a10f6885888b0bb7d11a9a2aa97007e38ef0e6d47f4ef7d2857ae`.

Extractor-side coercions added via a `NullWithReason` helper on
`scripts/rules/extract/_common.py` without touching the schema.
Eight `null-with-reason: insufficient-progression` entries recorded
(measure-scope harmonic on `unique_chords=1` windows) — honest
coercion, not fabrication.

**Mechanical unlock hit**: the cycle-11-flagged (salt 1, salt 4)
arrangement collision resolves — rule_id changes from
`rule_b75cc391f671037a` under both salts pre-expansion to two
distinct rule_ids post-expansion. Overall salt-collision pair count
drops 5 → 4 (sub-proportional to the 3× pool growth; three of four
residual pairs involve salt = 4, flagged as a research finding for
cycle 13).

### Clone 1 — _infra/fanout-concat-hardening

`long_exposure.workspace_bootstrap.concat_clone_ledgers` tightened
to route every merged row through the SSoT
`_ledger_schema.validate_event`, enforce per-candidate-milestone
monotonic file-order timestamps, sort merged events per milestone
by `(ts, content_hash_tiebreak)`, and write atomically via temp +
`os.replace`. Typed `LedgerConcatError` (real subclass of
`LedgerSchemaError`) with field-named messages on drift. Public API
signature unchanged.

Test coverage: `tests/test_fanout_concat_validation.py` — 10 named
cases pass in all 3 documented invocation flavors. Cross-branch
test extended with §24 (7 concat-hardening invariants).

Honest finding surfaced (report §5): 7 pre-existing cycle-1-era
file-order ts monotonicity violations across M-INGEST-1 milestones
and 2 `_run/clone-*-scope-complete` milestones are detected when
the current ledger is fed as a *candidate* stream to the hardened
concat. Main ledger content is grandfathered against monotonicity
(schema is not — 220+/220+ pass validation); the invariant applies
to candidate streams, which matches the tool's actual use pattern.
Recurrence prevented for all future fanout collapses.

### Clone 2 — M-DAW-SPIKE-1/gap-closure

Cycle-3 coverage matrix (6 GREEN / 1 PARTIAL / 2 GAP) advanced to
**cycle-12 (8 GREEN / 1 PARTIAL / 0 GAP / 1 redefined-GAP)** on
`data/daw_spike/coverage_matrix_v2.json`; heatmap at
`docs/figures/daw_spike_coverage_v2.png`.

| GAP  | Fallback exercised                          | Verdict         | Evidence                                             |
|------|---------------------------------------------|-----------------|------------------------------------------------------|
| GAP-1 | Fluidsynth pre-render + hand-authored Source/Region/Playlist audio-region XML | **redefined-GAP** | env_correlation = 1.000, peak_ratio_db = 0.00 dB (gap1_midi_import_measurement.json) |
| GAP-2 | Replace Surge XT Effects VST3 reverb with ACE Reverb LV2 (a-reverb.lv2); author wet-mix automation | **still-GAP with sharper diagnosis** | second/first RMS ratio = 1.0000 vs cycle-1 baseline 2.05 / DawDreamer reference 2.46 (gap2_lv2_measurement.json). Ardour Lua `plugin_automation()` fails on LV2 as well as VST3 — gap is broader than cycle-1's VST3-scoped diagnosis. |

Parent `M-DAW-SPIKE-1` remains validated/high per cycle 3; this
cycle updates axis-level detail only.

## Post-merge actions taken

Five rollup capstone events emitted via the hardened
`workspace_bootstrap.append_ledger_event()`:

1. `_infra/adopt-fanout-artifacts-m-daw-spike-1-cycle12` — validated/high (adopts the Ardour session-tree files clone-2 flagged as orphans in its post-merge note).
2. `_plan/register-post-merge-integration-fork-ed041ef4c1dc` — validated/high.
3. `_infra/cross-branch-integration-test-cycle12` — validated/high (verification pass; test extensions attributed to clone events).
4. `_run/post-merge-integration-fork-ed041ef4c1dc` — validated/high (capstone).
5. `_archive/integration-scratch-fork-ed041ef4c1dc` — validated/high (drives `tools/stale/_integrate_fork_ed041ef4c1dc.py`; supersedes the cycle-11 fork-ddd71e9bdb0e driver).

No plan-of-record drift required: clone-1 and clone-2 registered
their milestone rows in `plan_of_record.md` directly during their
branches; clone-0's `M-RULES-1/extraction/breadth-seeds` row was
registered in cycle 12 (pre-fork).

## Environment state (unchanged from cycle 11)

- `torch 2.13.0+cpu`
- `torchvision 0.28.0` (with `torch.library.register_fake` no-op workaround for `torchvision::nms`)
- `numpy 1.26.4` (M-CLASS-1 downgrade accepted cycle 6)
- `basic-pitch 0.4.0` quarantined at `workspace/basic_pitch_venv`
- `music21 9.1.0`, `mscore3 3.2.3` headless, `mir_eval 0.8.2`
- Single-thread BLAS pins throughout
- Egress: still blocked per `corpus/CORPUS_STATUS.md`;
  `workspace/harvest_playlists.sh` retry mechanism established in
  earlier cycles (M-INGEST-1/egress-ready-automation state machine
  will fire training + rating pipelines unattended on two consecutive
  `media_ok=true` egress-status rows).

## Anti-patterns preserved (do not re-attempt without new information)

- `M-TRANS-1/basic-pitch/octave-suppression` — invalidated/high (cycle 8): true achievable aggregate uplift +0.15 under the spec's single-pass rule, below the +0.3 success bar.
- `M-TEX-1/panel/embedding` — invalidated/medium (cycle 11): CLAP unreachable at HF SSL cert (rung 1.2); VGGish rung live as fallback.

## Handoff to next cycle (researcher)

Highest-value follow-ups surfaced by this fanout:

1. **Cycle-13 batch-v2 rerun on the 76-row ledger.** The live salt=0
   selection will change for melodic / form / arrangement on the
   expanded ledger (cycle-11 batch-v1 anchors remain pinned in a
   saved `sampling_manifest.json` and §23 of the cross-branch
   integration test still passes reading that JSON). Cycle 13 must
   expect and document this — it is not a bug.
2. **Salt=4 over-representation probe.** Three of four post-expansion
   collision pairs involve salt = 4. Salts 5..9 on the 76-row
   ledger, plus a non-F_major seed to move the structural-diversity
   axis, would distinguish "hash-space geometry for small-N pools"
   from "salt = 4 specifically maps unfavourably in this rule
   space".
3. **Structural-diversity bottleneck hypothesis.** 3× pool growth
   produced only ~20 % collision-rate reduction; probe by adding a
   non-F_major seed with different instrumentation.
4. **GAP-2 fallback #1 remains open**: read `libs/ardour/plugin_insert.cc`
   for the missing Lua-side automation-arming call. Cycle-12's
   fallback #2 established the gap is broader than cycle-1's
   VST3-scoped diagnosis, so this fallback becomes more valuable.
5. **DawDreamer plugin-catalog breadth-probe** (with torchvision
   workaround live): Dragonfly / MVerb / LSP LV2 reverbs could seed
   a `M-GEN-1/batch-v2+` effects chain disjoint from the cycle-9
   pinned chain.
6. **GAP-1 XML schema promotion**: the audio-region fragment in
   `scripts/daw_spike/gap_closure_midi_import.py` is stable enough
   to promote to `scripts/daw_spike/ardour_region_xml.py` when a
   second call-site needs it.
7. **CLAP question open**: does CLAP flip/reinforce/blur VGGish's
   family-disagreement signal on the cycle-9 triplet and the
   cycle-10 `synth_060s` pair? Blocked until egress unblock or a
   pre-seeded `roberta-base` cache.
8. **M-EAR-1 parent milestone rollup**: baseline WARN since cycle 6.
   All sub-milestones validated; parent roll-up event pending —
   researcher/auditor call whether to roll up now or wait for
   live-armed training.

## Load-bearing anchors

```
head -28 data/rules/ledger.jsonl | sha256sum
→ 4fe722adde034c099ff9e65437f0d5c138cb3dd2595089960150af5c2546fc4b   (cycle-9 anchor, preserved)

sha256sum data/rules/ledger.jsonl
→ a6fd53e9bf9a10f6885888b0bb7d11a9a2aa97007e38ef0e6d47f4ef7d2857ae   (post-expansion)
```

## Session references

- Fork: `ed041ef4c1dc`
- Cycle: 12 (post-merge integration rollup)
- Run: `run-2026-08-28T040704Z`
- Working directory: `/home/user/long-exposure-runs/music-gen`
- Supersedes: fork-ddd71e9bdb0e capstone (cycle 11)
