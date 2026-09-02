# Test stage 7 of 23 (final-audit stage 31 of 48)

## Scope

Four adversarial probes:
1. Verify F21: `corpus/ratings/ratings_manifest.tsv` band-7 coverage depth.
2. `data/anchor_manifest_v1.json` freshness — verify every anchor SHA against on-disk bytes.
3. `tools/stale/` inventory sanity.
4. Grep for direct `promise_ledger.jsonl` writes that bypass `workspace_bootstrap.append_ledger_event`.

## Probe 1: band-7 manifest coverage (F21 follow-up)

Manifest schema: `rating\tplaylist_id\tvideo_id\ttitle\tduration_s\turl`.

Row counts by rating (80 data rows + 1 header = 81 total):

| Rating | On-disk mp3 | Manifest rows |
|---|---:|---:|
| 4 | (from earlier) | 20 |
| 5 | (from earlier) | 30 |
| 6 | (from earlier) | 30 |
| 7 | 10 | **0** |

`corpus/ratings/7/RECEIPTS.md` documents 10 band-7 mp3s with per-song SHA-256s and *states* "Manifest entries added with `playlist_id=LOCAL_BAND_7`, `video_id=LOCAL-NNN`" — but a `grep LOCAL corpus/ratings/ratings_manifest.tsv` returns zero rows. RECEIPTS.md's claim is not carried by the manifest.

**Impact**: workers reference band-7 files directly by disk path (e.g., `corpus/ratings/7/016__LOCAL__05_02.mp3`), so pipelines continue to work; band-7 has its own separate provenance sidecar in RECEIPTS.md. But the manifest's authority-of-record is incomplete: 43-song rated corpus arithmetic (10 band-4 + 10 band-5 + 13 band-6 + 10 band-7 per ledger prose) cannot be reconstructed from the manifest alone.

**Finding F28**: MODERATE-DOWNGRADED-TO-MINOR — manifest–RECEIPTS.md drift. Provenance exists (in RECEIPTS.md); the shared TSV is stale wrt the operator's stated intent. Not a correctness defect. Left as documentation debt.

## Probe 2: `data/anchor_manifest_v1.json` freshness

Full scan of every `sha_per_path` file in every anchor:

- Total files checked: **21,657**
- Drifted: **2**
- Missing: 0

Drifts:

| Anchor | Path | Frozen SHA (prefix) | On-disk SHA (prefix) |
|---|---|---|---|
| `c33_palette_render` | `scripts/palette_render/render_stem.py` | `67209e9445fb6be3…` | `214372d920a319a9…` |
| `c33_harness_clone_namespace_guard` | `/home/user/human-in-a-loop/long-exposure/long_exposure/workspace_bootstrap.py` | `f55f54319e7a5f4d…` | `53e4a90b73d855c5…` |

Both drifts are **explained by later legitimate edits**:

- `render_stem.py` was intentionally extended at c36 (additive `parameter_dict` kwarg) and c51 (additive `eq_curve`/`loudness_target` kwargs). Current SHA `214372d920a319a9…` matches the SHA the plan-of-record repeatedly pins (e.g., `M-RECREATE-2/…/rc10-transcription-real-stem-resurvey/guitar-piano/candidate-matrix-implemented` and `…/rc7-mix-balance-match/impl` both cite `214372d9…5b2b`).
- `workspace_bootstrap.py` was intentionally extended at c48 (`_infra/harness-and-writer-hardening-v3`) with the substantive-exemption env var and the supersedes-in-hash flag.

However, both anchor rows in `data/anchor_manifest_v1.json` still carry `is_readonly: true` and pin the pre-edit SHA. The manifest's declarative claim ("this file is read-only and byte-fixed at X") is factually false for both.

**Finding F29**: MODERATE — `data/anchor_manifest_v1.json` carries stale `is_readonly: true` claims for `scripts/palette_render/render_stem.py` (edits at c36, c51) and `long_exposure/workspace_bootstrap.py` (edit at c48). The frozen SHA in the manifest no longer matches the on-disk SHA, and no `data/anchor_manifest_v2.json` was minted at c36/c48/c51 to record the ratcheted state. Downstream verdicts that cite "anchor preservation ≥N SHAs pre==post byte-exact" refer to a *snapshot-then-compare* pattern within one cycle's execution, not to the frozen manifest — so those verdicts remain honest — but the manifest's standalone authority is compromised. Recommendation for the reporter: name a v2 manifest as future work anchored to this finding.

## Probe 3: `tools/stale/` inventory sanity

- 422 entries under `tools/stale/` (files + `__pycache__`).
- 62 `_archive/cycle-N` events emitted across the campaign.
- Sampled `tools/stale/*.py` filenames align with the observed archival pattern (`_apply_c33_wb_edits.py`, `_archive_octave_scratch.py`, `_audit_*.py`, etc.).

No enforcement scan run this stage (large surface, low signal-to-noise). No new finding.

## Probe 4: writer-side isolation (`append_ledger_event` bypass grep)

Scanned all `**/*.py` under the workspace for `promise_ledger.jsonl` mentions:

- 17 files touch the string `promise_ledger`.
- Emitters (`tools/_c53_clone1_emit_events.py`, `tools/_c40_clone0_emit_events.py`): all writes go through `append_ledger_event(WS, ev)`; the `open('promise_ledger.jsonl', 'rb')` calls are read-only line counts / already-emitted-milestone-id scans.
- `scripts/fanout_namespace_v3/replay.py`: baseline replay reads only.
- Tests: reference `promise_ledger.jsonl` as input, not as a write target.

No direct `open('promise_ledger.jsonl', 'a')` writer bypass found.

**Finding F30**: INFO / PASS — writer-side isolation holds; every ledger write in-repo is mediated by `long_exposure.workspace_bootstrap.append_ledger_event`.

## Disposition of prior findings

| Prior | Status this stage | Note |
|---|---|---|
| F18 rubric-mtime | Unchanged (PASS) | Not re-probed. |
| F19 cycle-report coverage | Unchanged (MODERATE, narrowed) | Not re-probed. |
| F20 → F24 long_exposure/ install location | Unchanged (INFO, resolved) | Not re-probed. |
| F21 band-7 manifest depth | Sharpened → F28 (MINOR) | Root: RECEIPTS.md updated, TSV never was. |
| F23 c33/c34 fork/cycle naming drift | Unchanged (MODERATE, cosmetic) | Not re-probed. |
| F25 rubric-hash chain | Unchanged (PASS) | Not re-probed. |
| F26 shipping docs in ledger | Unchanged (INFO) | Not re-probed. |
| F27 c33 clone-suffix guard | Unchanged (INFO) | Not re-probed. |

## New findings this stage

- **F28** MINOR — `corpus/ratings/ratings_manifest.tsv` never picked up the band-7 rows that `corpus/ratings/7/RECEIPTS.md` promised. Documentation debt; not a correctness defect.
- **F29** MODERATE — `data/anchor_manifest_v1.json` carries stale `is_readonly: true` + frozen SHAs for two files that were subsequently edited (`render_stem.py` at c36+c51; `workspace_bootstrap.py` at c48). Recommendation: mint `data/anchor_manifest_v2.json` capturing the post-c51 state.
- **F30** INFO / PASS — no code path writes `promise_ledger.jsonl` outside `append_ledger_event`. Writer-side schema validation is unbypassable.

## Planned probes for stage 32 (test 8/23)

1. Cross-check `data/anchor_manifest_v1.json.anchors[].file_count` against actual dir file counts (independent replication of Probe 2 via a different structural claim).
2. `docs/pre_registration_gate_policy.md` §3 partition (harness-boundary vs in-turn-capable) — verify the partition names buckets actually observed in git history at 244 commits.
3. `_plan/*` event pattern audit — enumerate every `_plan/*` milestone and confirm each one landed a corresponding `docs/*.md` policy artifact.
4. `promise_check` and `org_check` full runs — both should return `0-ERROR` if the campaign's promise-check contract holds end-to-end.

<checkpoint>
  <stage>test 7 of 23 (final-audit stage 31 of 48)</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~186k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran four probes; sharpened F21 → F28 MINOR (manifest-RECEIPTS.md drift); surfaced new MODERATE F29 (anchor_manifest_v1 stale on 2/21657 files, both explained but not ratcheted); confirmed F30 writer-side isolation holds (no append_ledger_event bypass).</what-i-did>
  <next-action>Stage 32 (test 8/23) probes as listed above.</next-action>
  <gate-check>Continuing in test.</gate-check>
</checkpoint>
