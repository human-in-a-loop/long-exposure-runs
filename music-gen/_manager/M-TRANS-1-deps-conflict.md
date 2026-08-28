# M-TRANS-1 dependency-conflict manager note

<!--
created: 2026-08-28T06:35:00Z
run_id: run-2026-08-28T040704Z
cycle: 5
agent: worker
milestone: _manager/M-TRANS-1-deps-conflict
-->

## Purpose

Canonical on-disk anchor for the `_manager/M-TRANS-1-deps-conflict` event chain.
The ledger events under this milestone_id are the authoritative history; this
file just gives the ledger a real file to point at.

## Chain of decisions

1. **cycle 3 (worker)** — flagged: M-CLASS-1 branch installed
   `numpy==2.4.6` + `tensorflow==2.21.0`, which breaks `basic-pitch==0.4.0`
   (pins `tensorflow<2.15.1`). Three named resolutions surfaced.
2. **cycle 4 (researcher)** — recommendation: option (b) quarantined venv
   for basic-pitch. Preserves the classifier stack and keeps M-CLASS-1
   reproducible.
3. **cycle 4 (worker, M-TEX-1/panel clone)** — side effect: numpy was
   downgraded 2.4.6 → 1.26.4 as a transitive resolution when installing
   `laion-clap==1.1.7` for the embedding-ladder rung. Classifier stack
   still passes; 68/68 cross-branch integration checks green.
4. **cycle 5 (worker, this file)** — reconciliation: numpy is now compatible
   with basic-pitch's numpy floor. Remaining conflict narrows to
   tensorflow (2.21.0 vs `<2.15.1`). Option (b) quarantined venv is still
   the recommended path but only needs to pin tensorflow, not numpy.

## What the researcher entering M-TRANS-1 should do

- Create `workspace/basic_pitch_venv/` with `/usr/bin/python3 -m venv`.
- Install: `basic-pitch==0.4.0` plus its transitive tensorflow pin.
- Verify the top-level environment is untouched by re-running
  `PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py`
  (must remain 68/68 PASS).
- Use `data/separation/synth_mix/midi/{drums,bass,piano}.mid` as the
  note-level F1 ground truth (per clone-0 M-SEP-1 handoff).
