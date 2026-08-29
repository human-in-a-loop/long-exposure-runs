#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T10:45:00Z
# cycle: 38
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/second-real-audio-batch
# fork: 33a2a8003c84
# clone: 2
# ---
"""Fill in docs/recreate_v0_batch_report.md from verdict.json + panels."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data" / "recreate_v0_batch"
REPORT = REPO_ROOT / "docs" / "recreate_v0_batch_report.md"
V1_REPORT = REPO_ROOT / "docs" / "ear_real_label_training_v1_report.md"

RUBRIC_HASH = (DATA_ROOT / "rubric_hash.txt").read_text().strip()


def _tbl_row(row: dict) -> str:
    return ("| {band} | {sha16} | {mel_bare} | {mel_eff} | {mel_delta} | "
            "{sc_bare} | {sc_eff} | {sc_delta} | {rms_bare} | {rms_eff} | "
            "{rms_delta} | {lufs_bare} | {lufs_eff} | {lufs_delta} |"
            ).format(**row)


def _fmt(v, prec=3):
    if v is None:
        return "—"
    if isinstance(v, str):
        return v
    try:
        return f"{float(v):.{prec}f}"
    except Exception:
        return str(v)


def main() -> int:
    verdict = json.loads((DATA_ROOT / "verdict.json").read_text())
    corr = json.loads((DATA_ROOT / "cross_band_correlation.json").read_text())
    anchors = json.loads((DATA_ROOT / "anchor_preservation.json").read_text())
    chosen = json.loads((DATA_ROOT / "chosen_songs.json").read_text())

    # v1 caveat branch
    v1_present = V1_REPORT.exists()
    if v1_present:
        caveat_line = (
            f"Cite Branch A: [`{V1_REPORT.relative_to(REPO_ROOT)}`]("
            f"../{V1_REPORT.relative_to(REPO_ROOT)}) — v1 real-label ear "
            f"model report present on disk at write time; per Branch C "
            f"contract, cite by document path only (never import artifact)."
        )
    else:
        caveat_line = (
            "**preview_untrained_ear: c36 M-EAR-1/real-label-training-v0 "
            "verdict INSUFFICIENT — this score is exploratory only, not a "
            "validated rating**"
        )

    # Per-song rows for the ear caveat section
    per_song_lines = []
    for f in verdict["per_song_findings"]:
        per_song_lines.append(
            f"- **Band {f['band']} · sha `{f['sha16']}`** — "
            f"`{f['relpath']}`: "
            f"pipeline={'OK' if f['run1_failed_stage'] is None else 'FAIL@'+str(f['run1_failed_stage'])}, "
            f"byte-det×2={'OK' if f['byte_det_x2'] else 'DRIFT'}, "
            f"mel_l1_db_delta={_fmt(f['mel_l1_db_delta_bare_minus_effects'])} dB. "
            f"{caveat_line}"
        )
    per_song_block = "\n".join(per_song_lines) if per_song_lines else "_no per-song findings_"

    # Cross-band table
    tsv_path = DATA_ROOT / "cross_band_table.tsv"
    tbl_md = ""
    if tsv_path.exists():
        lines = tsv_path.read_text().strip().split("\n")
        hdr = lines[0].split("\t")
        tbl_md = "| " + " | ".join(hdr) + " |\n"
        tbl_md += "|" + "|".join(["---"] * len(hdr)) + "|\n"
        for L in lines[1:]:
            cols = L.split("\t")
            def _f(x):
                try:
                    return f"{float(x):.3f}"
                except Exception:
                    return x
            tbl_md += "| " + " | ".join(_f(c) for c in cols) + " |\n"

    # Correlation block
    corr_md = ""
    for fam, row in sorted(corr.items()):
        corr_md += (f"- **{fam}**: n={row['n']}, "
                    f"Pearson r={_fmt(row['pearson_r'])}, "
                    f"Spearman ρ={_fmt(row['spearman_rho'])}. "
                    f"_{row['n_too_small_caveat']}_\n")

    # Compose report
    md = f"""---
created: 2026-08-29T11:00:00Z
cycle: 38
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-1/second-real-audio-batch
fork: 33a2a8003c84
clone: 2
rubric_hash: {RUBRIC_HASH}
---

# M-RECREATE-1/second-real-audio-batch — Clone-2 Report

**Fork:** 33a2a8003c84 · **Clone:** 2 · **Cycle:** 38
**Milestone:** `M-RECREATE-1/second-real-audio-batch` (peer sub-milestone
under G1, per the c29 state-machine lemma — NOT a child of the
terminal-validated c37 `M-RECREATE-1/first-real-audio`).

**Rubric SHA-256 (frozen 2026-08-29T10:30:00Z):**
`{RUBRIC_HASH}`
committed BEFORE any file under `scripts/recreate_v0_batch/` (mtime-order
test + git-log order test enforce this — the git-log gate is
`MERGE_DEFERRED` in this clone's environment; the mtime gate is enforced
in-clone).

## 1. Verdict

**{verdict['verdict']}** — {verdict['reason']}

| Field | Value |
|---|---|
| n_songs | {verdict['n_songs']} |
| n_pipeline_ok | {verdict['n_pipeline_ok']}/{verdict['n_songs']} |
| n_byte_det_x2 | {verdict['n_byte_det_x2']}/{verdict['n_songs']} |
| n_positive_mel_delta | {verdict['n_positive_mel_delta']}/{verdict['n_songs']} |
| anchors_unchanged | {verdict['anchors_unchanged']} |
| rubric_hash | `{verdict['rubric_hash']}` |
| total_wall_seconds | {verdict.get('total_wall_seconds')} |

## 2. Selection (SHA-256 tiebreak per bucket + band-6 second-lowest)

Excluded: `{chosen['excluded_relpath']}` (c37 clone-0's song).
Candidates after exclusion: {chosen['n_candidates_after_exclusion']}.

| Band | Slot | SHA-256 (prefix) | Relpath | Bytes |
|---|---|---|---|---|
"""
    for s in chosen['chosen_songs']:
        md += f"| {s['band']} | {s['slot_kind']} | `{s['sha256'][:16]}` | `{s['relpath']}` | {s['bytes']} |\n"

    md += f"""
## 3. Cross-band panel table

Two panels per song (5 songs × 2 panels = 10 TSVs) via `M-TEX-1/panel`;
aggregated at `data/recreate_v0_batch/cross_band_table.tsv`.

{tbl_md}

**Deltas** are `bare − effects`; positive = effects narrows gap.

## 4. Cross-band correlation (n=5, exploratory only)

{corr_md}

## 5. Byte-determinism × 2

Every one of the 20 anchors (5 songs × 4 anchors: merged.musicxml,
merged.midi, bare_midi.wav, effects.wav) run twice into independent
fresh out-dirs under the same environment pins (`OMP/MKL/OPENBLAS=1`,
`torch.manual_seed(0)`). Results in per-song
`per_song_result.json.determinism`; aggregate:
`{verdict['n_byte_det_x2']}/{verdict['n_songs']}` songs 4/4 byte-det.

Any drift on `effects.wav` is documented as substantive characterization
per c36 Branch C VST3-nondeterminism finding, NOT hidden.

## 6. Preview_untrained_ear caveat

{caveat_line}

Per-song application:

{per_song_block}

## 7. Anchor preservation

{anchors['n_anchors']} c37 clone-0 upstream anchors +
recreate_v0 stage scripts + c37 data anchors:
**unchanged = {anchors['unchanged']}**.
{("Changed: " + ", ".join(anchors.get('changed', {}).keys())) if not anchors['unchanged'] else "All byte-identical pre/post batch run."}

## 8. Rubric commitment order

- Rubric doc on disk: `docs/recreate_v0_batch_rubric.md`
- Rubric hash file: `data/recreate_v0_batch/rubric_hash.txt`
- Rubric hash: `{RUBRIC_HASH}`
- **mtime gate:** rubric mtime ≤ every script mtime under
  `scripts/recreate_v0_batch/` — enforced by
  `tests/test_recreate_v0_batch.py::test_04_rubric_mtime_precedes_scripts`.
- **git-log gate:** deferred to merge conductor (this clone's
  environment does not permit `git add`/`git commit`).
  `tests/test_recreate_v0_batch.py::test_05_rubric_git_log_order` records
  the deferral explicitly.

## 9. c39 handoff seeds (independent of verdict polarity)

Per the research brief §c39 handoff seeds — chosen conditionally on
this cycle's verdict `{verdict['verdict']}`:

- **If `BATCH_LANDS`**: c39 opens (a) merging cross-band results with
  Branch A's v1 model; (b) `M-RECREATE-1/full-corpus-recreation`
  on remaining 37 songs.
- **If `BATCH_PARTIAL` with byte-det failure(s) on effects.wav**: c39
  lifts c36 Branch C VST3 characterization onto per-band data.
- **If `BATCH_PARTIAL` with mel_l1_db-delta failure(s)**: c39 opens
  `_manager/effects-chain-band-selectivity` investigation.
- **If `BATCH_FAILS`**: c39 opens stage-isolation branch reproducing
  the failure minimally, with named-band-bias analysis if failures
  concentrate on one band.
- **Regardless**: cross-band correlation coefficients (statistically
  weak at n=5) become the seed hypothesis for c40+ larger-N tests.

## 10. Test coverage

`tests/test_recreate_v0_batch.py` — 15 named test cases:

1. AST: no PRNG in `select_songs.py`.
2. `chosen_songs.json` excludes `016__LOCAL__05_02.mp3`.
3. Each chosen SHA-256 matches actual file bytes.
4. Rubric mtime ≤ every script mtime.
5. Rubric commit predates every script commit (`MERGE_DEFERRED`).
6. `verdict.json.rubric_hash` byte-equals `rubric_hash.txt`.
7. Per-song stage manifests: 5 songs × 8 stages = 40.
8. Byte-determinism × 2: 20 SHA-equal assertions.
9. `cross_band_table.tsv` has 5 rows × 14 columns.
10. `cross_band_correlation.json` carries literal `n_too_small_caveat`.
11. No writes under c37 `data/recreate_v0/` (via anchor preservation).
12. Literal preview_untrained_ear caveat present (v1 or v0 branch).
13. c37 upstream anchor preservation (≥18 anchors).
14. AST: no Branch A / Branch B imports.
15. AST: no forbidden state calls (`get_state`, `save_state`, etc.);
    no `sidecar_nonfactor` / `i4_stratified` imports; interpreter
    guard on every executable script.

Run: `PYTHONPATH=. /usr/bin/python3 tests/test_recreate_v0_batch.py`

END OF REPORT.
"""
    REPORT.write_text(md)
    print(f"Wrote {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
