# Refactor & cleanup plan — 2026-09-03 (operator-executed)

**Trigger**: operator directive after M-V3-FOCUS landed 5/5. The v3 run
proved the pipeline but left ~48 script dirs, 226 docs, and ~4.6 GB of
working data accumulated across three pipeline generations and many
messy/null cycles. This stage cleans and simplifies so future long-exposure
runs start from a coherent codebase. **No feature is deleted** — only stale
versions, superseded working data, and namespace clutter. Everything
removed from the working tree remains in git history; the inventory doc
records each disposition.

Companion docs:
- `REFACTOR_2026-09-03_inventory.md` — per-item keep/archive/delete table.
- `ARCHITECTURE_v4_simplified.md` — the simplified architecture (including
  the sound-matching deterministic/agentic split policy) future runs build on.

## Stages (executed in order; each ends with a CHECK and a commit)

**Stage A — Data & disk cleanup.**
Delete superseded working data (old-generation outputs, regenerable
intermediates, probe junk), keeping: final deliveries (A/B + full
reconstructions + manifests + MIDI + panels), per-song operator-section
6-stem references and transcription JSONs (needed by the future
sound-matching layer), gold set, ear/gen/rules data, ingestion receipts,
corpus. Tombstone notes at every pruned path.
CHECK: disk ≥ 8 GB free; every kept delivery still opens (soxi/ffprobe);
tombstones in place.

**Stage B — Scripts consolidation.**
Keep the newest working version of every feature family + the proven core;
delete superseded generations (git history preserves). Result: a scripts
tree where each dir is either core pipeline or the current version of a
feature.
CHECK: `python -m compileall` clean on all kept scripts; the checkpointed
driver's imports resolve; inventory table matches the tree.

**Stage C — Docs & reports organization.**
Move run-generated cycle reports/rubrics (~200 files) into
`docs/run_archive/`; keep operator/architecture/decision docs at top
level; guidance snapshots into `docs/guidance/`. Nothing deleted.
CHECK: `ls docs` shows < 25 top-level files, all operator-relevant;
archive counts match what was moved.

**Stage D — Workspace & environment cleanup.**
Delete `workspace/_probe` (137 MB probe junk) and stray merge-report
files; prune collapsed fork dirs + old resume logs from the v3 instance
(state + sessions.db + latest log kept); remove the empty stale
`music-gen-instance` dir; keep run1 archive; clear rebuilt pip/uv caches
but NEVER torch-hub/huggingface model checkpoints (demucs/vggish weights
live there) or `workspace/models` (MuScriptor weights).
CHECK: demucs, MuScriptor, fluidsynth, and the SF2 still resolve;
`workspace/smoke_test.py` still passes its import stages.

**Stage E — Verification & handoff.**
(1) Re-run the checkpointed driver on Peach Dream — should be a fast
cache-hit run proving the pipeline works post-refactor end-to-end;
(2) update `music_gen_v3_prompt.md` → v4 layout pointers + the
sound-matching policy; (3) write `docs/CODEBASE_GUIDE.md` — the map a
fresh long-exposure researcher reads first.
CHECK: driver exits 0 with stages hit from cache and byte-identical
outputs vs the approved delivery; prompt references only paths that exist.

## Invariants (hold at every stage)
- Corpus audio, receipts, and manifests untouched.
- All operator-approved delivery audio untouched.
- No audio/weights/venvs committed to git (existing .gitignore rules).
- Every deletion is either regenerable-by-command (noted) or in git history.
- Commit + push after each stage.
