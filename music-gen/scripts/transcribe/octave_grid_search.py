"""M-TRANS-1/basic-pitch/octave-suppression — 3×3 grid driver.

For each cell (T_min ∈ {50, 100, 200} ms) × (overlap_min ∈ {0.3, 0.5, 0.7}):
  1. Apply ``suppress_octaves`` to the BASS JSONL only (drums/other are
     passed through unchanged so we cleanly isolate the bass contribution).
  2. Re-evaluate all three stems with the cycle-6 evaluator
     (``scripts.transcribe.eval_transcription.eval_pair``) so the numbers
     are comparable to the cycle-6 baseline.
  3. Compute deltas vs. the cycle-6 baseline row in
     ``data/transcribe/results.tsv``.

Outputs
-------
    data/transcribe/octave_suppression/grid_search.tsv    (39 rows)

Row format (tab-separated):
    mix_id  T_min_ms  overlap_min
    bass_precision  bass_recall  bass_F1
    drums_precision  drums_recall  drums_F1
    other_precision  other_recall  other_F1
    bass_F1_uplift  drums_F1_delta  other_F1_delta
    passes_harmless  notes_kept  notes_suppressed

Special sentinel rows:
    T_min_ms = "baseline", overlap_min = "baseline"  → cycle-6 numbers
    mix_id   = "aggregate"                            → averaged over the 3 mixes

Determinism: pure function over frozen inputs; no RNG anywhere.

Interpreter: /usr/bin/python3.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"wrong interpreter: {sys.executable}"

# NB: importing octave_suppression only; NO import of sidecar_nonfactor.
from scripts.transcribe.eval_transcription import eval_pair, load_jsonl  # noqa: E402
from scripts.transcribe.octave_suppression import suppress_octaves  # noqa: E402

ROOT = Path("/home/user/long-exposure-runs/music-gen")
REF_ROOT = ROOT / "data/transcribe/reference"
BP_ROOT = ROOT / "data/transcribe/basic_pitch"
OUT_DIR = ROOT / "data/transcribe/octave_suppression"
OUT_TSV = OUT_DIR / "grid_search.tsv"

MIXES = ["synth_030s", "synth_060s", "synth_090s"]
STEMS = ["drums", "bass", "other"]

T_MIN_GRID = [50, 100, 200]
OVERLAP_MIN_GRID = [0.3, 0.5, 0.7]

HARMLESS_DELTA = -0.02
HEADER = [
    "mix_id",
    "T_min_ms",
    "overlap_min",
    "bass_precision",
    "bass_recall",
    "bass_F1",
    "drums_precision",
    "drums_recall",
    "drums_F1",
    "other_precision",
    "other_recall",
    "other_F1",
    "bass_F1_uplift",
    "drums_F1_delta",
    "other_F1_delta",
    "passes_harmless",
    "notes_kept",
    "notes_suppressed",
]


def _load(path: Path) -> list[dict]:
    return load_jsonl(path)


def _fmt(x: float) -> str:
    return f"{x:.4f}"


def _fmt_int(x: int) -> str:
    return str(int(x))


def _baseline_per_mix() -> dict[tuple[str, str], dict[str, float]]:
    """Evaluate the raw cycle-6 basic-pitch JSONL against reference.

    Rebuilds the numbers from JSONL so the baseline row is byte-tied to
    the exact evaluator settings and does not silently drift if
    results.tsv is stale.
    """
    out: dict[tuple[str, str], dict[str, float]] = {}
    for mix in MIXES:
        for stem in STEMS:
            ref = _load(REF_ROOT / mix / f"{stem}.reference.jsonl")
            est = _load(BP_ROOT / mix / f"{stem}.jsonl")
            is_drum = stem == "drums"
            out[(mix, stem)] = eval_pair(ref, est, is_drum)
    return out


def _run_cell(
    baselines: dict[tuple[str, str], dict[str, float]],
    mix: str,
    t_min_ms: int,
    overlap_min: float,
) -> dict:
    """Evaluate one (mix, T_min, overlap_min) cell.  Filter bass only."""
    bass_est = _load(BP_ROOT / mix / "bass.jsonl")
    kept, suppressed = suppress_octaves(bass_est, t_min_ms, overlap_min)

    per_stem: dict[str, dict[str, float]] = {}
    for stem in STEMS:
        ref = _load(REF_ROOT / mix / f"{stem}.reference.jsonl")
        if stem == "bass":
            est = kept
        else:
            est = _load(BP_ROOT / mix / f"{stem}.jsonl")
        per_stem[stem] = eval_pair(ref, est, is_drum=(stem == "drums"))

    bass_uplift = per_stem["bass"]["f1"] - baselines[(mix, "bass")]["f1"]
    drums_delta = per_stem["drums"]["f1"] - baselines[(mix, "drums")]["f1"]
    other_delta = per_stem["other"]["f1"] - baselines[(mix, "other")]["f1"]
    passes = (drums_delta >= HARMLESS_DELTA) and (other_delta >= HARMLESS_DELTA)

    return {
        "per_stem": per_stem,
        "bass_uplift": bass_uplift,
        "drums_delta": drums_delta,
        "other_delta": other_delta,
        "passes_harmless": passes,
        "notes_kept": len(kept),
        "notes_suppressed": len(suppressed),
    }


def _row_baseline(mix: str, baselines) -> list[str]:
    b = baselines[(mix, "bass")]
    d = baselines[(mix, "drums")]
    o = baselines[(mix, "other")]
    return [
        mix,
        "baseline",
        "baseline",
        _fmt(b["precision"]),
        _fmt(b["recall"]),
        _fmt(b["f1"]),
        _fmt(d["precision"]),
        _fmt(d["recall"]),
        _fmt(d["f1"]),
        _fmt(o["precision"]),
        _fmt(o["recall"]),
        _fmt(o["f1"]),
        _fmt(0.0),
        _fmt(0.0),
        _fmt(0.0),
        "True",
        _fmt_int(len(_load(BP_ROOT / mix / "bass.jsonl"))),
        _fmt_int(0),
    ]


def _row_cell(mix: str, t_min: int, overlap: float, res: dict) -> list[str]:
    return [
        mix,
        str(t_min),
        f"{overlap:.1f}",
        _fmt(res["per_stem"]["bass"]["precision"]),
        _fmt(res["per_stem"]["bass"]["recall"]),
        _fmt(res["per_stem"]["bass"]["f1"]),
        _fmt(res["per_stem"]["drums"]["precision"]),
        _fmt(res["per_stem"]["drums"]["recall"]),
        _fmt(res["per_stem"]["drums"]["f1"]),
        _fmt(res["per_stem"]["other"]["precision"]),
        _fmt(res["per_stem"]["other"]["recall"]),
        _fmt(res["per_stem"]["other"]["f1"]),
        _fmt(res["bass_uplift"]),
        _fmt(res["drums_delta"]),
        _fmt(res["other_delta"]),
        str(bool(res["passes_harmless"])),
        _fmt_int(res["notes_kept"]),
        _fmt_int(res["notes_suppressed"]),
    ]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    baselines = _baseline_per_mix()

    rows: list[list[str]] = [list(HEADER)]

    # Baseline rows (one per mix).
    for mix in MIXES:
        rows.append(_row_baseline(mix, baselines))

    # Per-cell rows (9 cells × 3 mixes = 27 rows).
    per_cell_by_mix: dict[tuple[int, float], dict[str, dict]] = {}
    for t_min in T_MIN_GRID:
        for overlap in OVERLAP_MIN_GRID:
            per_cell_by_mix[(t_min, overlap)] = {}
            for mix in MIXES:
                res = _run_cell(baselines, mix, t_min, overlap)
                per_cell_by_mix[(t_min, overlap)][mix] = res
                rows.append(_row_cell(mix, t_min, overlap, res))

    # Aggregate row per cell (average across mixes).
    for t_min in T_MIN_GRID:
        for overlap in OVERLAP_MIN_GRID:
            cells = per_cell_by_mix[(t_min, overlap)]
            def _avg_ps(stem, metric):
                return sum(cells[m]["per_stem"][stem][metric] for m in MIXES) / len(MIXES)
            def _avg(field):
                return sum(cells[m][field] for m in MIXES) / len(MIXES)

            all_pass = all(cells[m]["passes_harmless"] for m in MIXES)
            row = [
                "aggregate",
                str(t_min),
                f"{overlap:.1f}",
                _fmt(_avg_ps("bass", "precision")),
                _fmt(_avg_ps("bass", "recall")),
                _fmt(_avg_ps("bass", "f1")),
                _fmt(_avg_ps("drums", "precision")),
                _fmt(_avg_ps("drums", "recall")),
                _fmt(_avg_ps("drums", "f1")),
                _fmt(_avg_ps("other", "precision")),
                _fmt(_avg_ps("other", "recall")),
                _fmt(_avg_ps("other", "f1")),
                _fmt(_avg("bass_uplift")),
                _fmt(_avg("drums_delta")),
                _fmt(_avg("other_delta")),
                str(bool(all_pass)),
                _fmt_int(sum(cells[m]["notes_kept"] for m in MIXES)),
                _fmt_int(sum(cells[m]["notes_suppressed"] for m in MIXES)),
            ]
            rows.append(row)

    # Aggregate baseline row (rounds out the "aggregate" mix_id class).
    def _avg_base(stem, metric):
        return sum(baselines[(m, stem)][metric] for m in MIXES) / len(MIXES)
    rows.append(
        [
            "aggregate",
            "baseline",
            "baseline",
            _fmt(_avg_base("bass", "precision")),
            _fmt(_avg_base("bass", "recall")),
            _fmt(_avg_base("bass", "f1")),
            _fmt(_avg_base("drums", "precision")),
            _fmt(_avg_base("drums", "recall")),
            _fmt(_avg_base("drums", "f1")),
            _fmt(_avg_base("other", "precision")),
            _fmt(_avg_base("other", "recall")),
            _fmt(_avg_base("other", "f1")),
            _fmt(0.0),
            _fmt(0.0),
            _fmt(0.0),
            "True",
            _fmt_int(sum(len(_load(BP_ROOT / m / "bass.jsonl")) for m in MIXES)),
            _fmt_int(0),
        ]
    )

    OUT_TSV.write_text("\n".join("\t".join(r) for r in rows) + "\n")

    # Console summary.
    print(f"wrote {OUT_TSV}: {len(rows) - 1} data rows")
    print(f"aggregate bass F1 baseline = {_avg_base('bass', 'f1'):.4f}")
    best_cell = None
    best_uplift = -1e9
    for t_min in T_MIN_GRID:
        for overlap in OVERLAP_MIN_GRID:
            cells = per_cell_by_mix[(t_min, overlap)]
            uplift = sum(cells[m]["bass_uplift"] for m in MIXES) / len(MIXES)
            drums_d = sum(cells[m]["drums_delta"] for m in MIXES) / len(MIXES)
            other_d = sum(cells[m]["other_delta"] for m in MIXES) / len(MIXES)
            passes = (drums_d >= HARMLESS_DELTA) and (other_d >= HARMLESS_DELTA)
            marker = "*" if passes else " "
            print(
                f" {marker} T_min={t_min:>3} overlap={overlap} uplift={uplift:+.4f} "
                f"drumsΔ={drums_d:+.4f} otherΔ={other_d:+.4f}"
            )
            if passes and uplift > best_uplift:
                best_uplift = uplift
                best_cell = (t_min, overlap)
    print(f"\nbest (subject to harmless): {best_cell} uplift={best_uplift:+.4f}")


if __name__ == "__main__":
    main()
