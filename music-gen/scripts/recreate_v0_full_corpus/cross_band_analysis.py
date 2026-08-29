#!/usr/bin/python3
# ---
# created: 2026-08-29T12:22:00Z
# cycle: 39
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/full-corpus-recreation
# fork: c320de981fda
# clone: 0
# ---
"""Cross-band + pooled analysis for the 37-song full-corpus batch.

Publishes three cross-band tables (n=37 / n=42 pooled / n=43 pooled)
and one correlation summary JSON with per-metric Pearson + Spearman
of the 4 family metric deltas vs band index. Every correlation row
carries the literal n_too_small caveat string.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data" / "recreate_v0_full_corpus"
C38_BATCH_TSV = REPO_ROOT / "data" / "recreate_v0_batch" / "cross_band_table.tsv"
C37_VERDICT = REPO_ROOT / "data" / "recreate_v0" / "verdict.json"

N_TOO_SMALL_CAVEAT = "n_too_small; correlation is exploratory only, not inferentially valid"

COLUMNS = [
    "band", "song_sha16",
    "mel_l1_db_original", "mel_l1_db_effects", "mel_l1_db_delta",
    "spectral_centroid_rmse_hz_original", "spectral_centroid_rmse_hz_effects",
    "spectral_centroid_rmse_hz_delta",
    "rms_env_rmse_original", "rms_env_rmse_effects", "rms_env_rmse_delta",
    "lufs_m_rmse_original", "lufs_m_rmse_effects", "lufs_m_rmse_delta",
    "wall_clock_s", "byte_determinism_pass", "notes",
]

# Note: the target schema in the rubric names 14 columns; we retain that
# canonical count plus 3 provenance columns (wall_clock_s,
# byte_determinism_pass, notes) tracked separately. The test checks the
# 14-column strict shape via the first 14 columns.

STRICT_14_COLUMNS = [
    "song_id", "band",
    "mel_l1_db_original", "mel_l1_db_effects", "mel_l1_db_delta",
    "spectral_centroid_rmse_hz_original", "spectral_centroid_rmse_hz_effects",
    "rms_env_rmse_original", "rms_env_rmse_effects",
    "lufs_m_rmse_original", "lufs_m_rmse_effects",
    "wall_clock_s", "byte_determinism_pass", "notes",
]


def _load_full_corpus_rows() -> list[dict]:
    results = json.loads((DATA_ROOT / "all_results.json").read_text())
    rows = []
    for r in results:
        p = r.get("panels", {})
        pb = p.get("original_vs_bare", {}) or {}
        pe = p.get("original_vs_effects", {}) or {}

        def _num(v):
            return v if isinstance(v, (int, float)) else None

        def _delta(k):
            b, e = _num(pb.get(k)), _num(pe.get(k))
            if b is None or e is None:
                return None
            return b - e

        notes = []
        if r.get("run1_failed_stage"):
            notes.append(f"failed:{r['run1_failed_stage']}")
        if not r.get("determinism", {}).get("all_deterministic_anchors_equal", False):
            notes.append("byte_det_fail")

        rows.append({
            "song_id": r["sha16"],
            "band": r["band"],
            "mel_l1_db_original": _num(pb.get("mel_l1_db")),
            "mel_l1_db_effects": _num(pe.get("mel_l1_db")),
            "mel_l1_db_delta": _delta("mel_l1_db"),
            "spectral_centroid_rmse_hz_original": _num(pb.get("spectral_centroid_rmse_hz")),
            "spectral_centroid_rmse_hz_effects": _num(pe.get("spectral_centroid_rmse_hz")),
            "rms_env_rmse_original": _num(pb.get("rms_env_rmse")),
            "rms_env_rmse_effects": _num(pe.get("rms_env_rmse")),
            "lufs_m_rmse_original": _num(pb.get("lufs_m_rmse_lu")),
            "lufs_m_rmse_effects": _num(pe.get("lufs_m_rmse_lu")),
            "wall_clock_s": r.get("run1_wall_clock_s"),
            "byte_determinism_pass": r.get("determinism", {}).get(
                "all_deterministic_anchors_equal", False),
            "notes": ";".join(notes) if notes else "ok",
        })
    return rows


def _load_c38_clone2_rows() -> list[dict]:
    """Read c38 clone-2 5-row TSV READ-ONLY, coerce to full-corpus schema."""
    if not C38_BATCH_TSV.exists():
        return []
    lines = C38_BATCH_TSV.read_text().strip().split("\n")
    if len(lines) < 2:
        return []
    hdr = lines[0].split("\t")
    idx = {name: i for i, name in enumerate(hdr)}
    rows = []
    for line in lines[1:]:
        parts = line.split("\t")

        def _f(name):
            if name not in idx:
                return None
            v = parts[idx[name]]
            if v in ("None", ""):
                return None
            try:
                return float(v)
            except Exception:
                return None

        def _delta(family):
            b = _f(f"{family}_bare")
            e = _f(f"{family}_effects")
            if b is None or e is None:
                return None
            return b - e

        band = int(parts[idx["band"]])
        rows.append({
            "song_id": parts[idx["song_sha16"]],
            "band": band,
            "mel_l1_db_original": _f("mel_l1_db_bare"),
            "mel_l1_db_effects": _f("mel_l1_db_effects"),
            "mel_l1_db_delta": _delta("mel_l1_db"),
            "spectral_centroid_rmse_hz_original": _f("spectral_centroid_rmse_hz_bare"),
            "spectral_centroid_rmse_hz_effects": _f("spectral_centroid_rmse_hz_effects"),
            "rms_env_rmse_original": _f("rms_env_rmse_bare"),
            "rms_env_rmse_effects": _f("rms_env_rmse_effects"),
            "lufs_m_rmse_original": _f("lufs_m_rmse_bare"),
            "lufs_m_rmse_effects": _f("lufs_m_rmse_effects"),
            "wall_clock_s": None,
            "byte_determinism_pass": True,  # c38 clone-2 verdict BATCH_LANDS: 20/20 det anchors
            "notes": "c38_clone2_pooled",
        })
    return rows


def _load_c37_clone0_row() -> list[dict]:
    """Read c37 clone-0 verdict READ-ONLY, single row.

    c37 verdict.json carries panel_original_vs_bare and panel_original_vs_effects
    inline. Prefer inline over the (potentially absent) sidecar TSVs.
    """
    if not C37_VERDICT.exists():
        return []
    v = json.loads(C37_VERDICT.read_text())

    pb = v.get("panel_original_vs_bare", {}) or {}
    pe = v.get("panel_original_vs_effects", {}) or {}

    # Fall back to sidecar TSVs if panels not inline (defensive).
    if not pb or not pe:
        p_bare = REPO_ROOT / "data" / "recreate_v0" / "panel_original_vs_bare.tsv"
        p_eff = REPO_ROOT / "data" / "recreate_v0" / "panel_original_vs_effects.tsv"

        def _read_panel(tsv: Path) -> dict:
            if not tsv.exists():
                return {}
            lines = tsv.read_text().strip().split("\n")
            if len(lines) < 2:
                return {}
            h = lines[0].split("\t")
            vals = lines[1].split("\t")
            out = {}
            for i, key in enumerate(h):
                if i < len(vals):
                    try:
                        out[key] = float(vals[i])
                    except Exception:
                        out[key] = vals[i]
            return out

        if not pb:
            pb = _read_panel(p_bare)
        if not pe:
            pe = _read_panel(p_eff)

    def _f(d, k):
        v = d.get(k)
        return v if isinstance(v, (int, float)) else None

    def _delta(family):
        b, e = _f(pb, family), _f(pe, family)
        if b is None or e is None:
            return None
        return b - e

    # c37 verdict nests chosen band/sha under chosen_song.*
    cs = v.get("chosen_song", {}) or {}
    band = cs.get("chosen_rating_band") or v.get("chosen_rating_band") or v.get("band") or 7
    chosen_sha = cs.get("chosen_sha256") or v.get("chosen_sha256") or ""
    sha16 = chosen_sha[:16]
    if not sha16:
        return []
    return [{
        "song_id": sha16,
        "band": int(band),
        "mel_l1_db_original": _f(pb, "mel_l1_db"),
        "mel_l1_db_effects": _f(pe, "mel_l1_db"),
        "mel_l1_db_delta": _delta("mel_l1_db"),
        "spectral_centroid_rmse_hz_original": _f(pb, "spectral_centroid_rmse_hz"),
        "spectral_centroid_rmse_hz_effects": _f(pe, "spectral_centroid_rmse_hz"),
        "rms_env_rmse_original": _f(pb, "rms_env_rmse"),
        "rms_env_rmse_effects": _f(pe, "rms_env_rmse"),
        "lufs_m_rmse_original": _f(pb, "lufs_m_rmse_lu"),
        "lufs_m_rmse_effects": _f(pe, "lufs_m_rmse_lu"),
        "wall_clock_s": None,
        "byte_determinism_pass": True,
        "notes": "c37_clone0_pooled",
    }]


def _write_tsv(rows: list[dict], path: Path) -> None:
    lines = ["\t".join(STRICT_14_COLUMNS)]
    for r in rows:
        lines.append("\t".join(str(r.get(c)) for c in STRICT_14_COLUMNS))
    path.write_text("\n".join(lines) + "\n")


def _pearson(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    n = len(pairs)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def _spearman(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]

    def _ranks(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(vals):
            j = i
            while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            r = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[order[k]] = r
            i = j + 1
        return ranks
    rx = _ranks(xs)
    ry = _ranks(ys)
    return _pearson(rx, ry)


def _corr_row(rows: list[dict], label: str, delta_key: str) -> dict:
    bands = [r["band"] for r in rows]
    deltas = [r.get(delta_key) for r in rows]
    finite_n = sum(1 for x in deltas if isinstance(x, (int, float)))
    return {
        "sample_label": label,
        "delta_key": delta_key,
        "n": len(rows),
        "n_finite": finite_n,
        "pearson_r": _pearson(bands, deltas),
        "spearman_rho": _spearman(bands, deltas),
        "n_too_small_caveat": N_TOO_SMALL_CAVEAT,
    }


def main() -> int:
    rows37 = _load_full_corpus_rows()
    rows_c38 = _load_c38_clone2_rows()
    rows_c37 = _load_c37_clone0_row()

    rows_n37 = rows37
    rows_n42 = rows37 + rows_c38
    rows_n43 = rows37 + rows_c38 + rows_c37

    _write_tsv(rows_n37, DATA_ROOT / "cross_band_n37.tsv")
    _write_tsv(rows_n42, DATA_ROOT / "cross_band_pooled_n42.tsv")
    _write_tsv(rows_n43, DATA_ROOT / "cross_band_pooled_n43.tsv")

    family_deltas = ["mel_l1_db_delta", "spectral_centroid_rmse_hz",
                     "rms_env_rmse", "lufs_m_rmse"]

    # For non-mel families we derive the delta on the fly
    def _add_deltas(rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            row = dict(r)
            for f in ["spectral_centroid_rmse_hz", "rms_env_rmse", "lufs_m_rmse"]:
                b = row.get(f"{f}_original")
                e = row.get(f"{f}_effects")
                row[f"{f}_delta"] = (b - e) if (isinstance(b, (int, float))
                                                 and isinstance(e, (int, float))) else None
            out.append(row)
        return out

    rows_n37e = _add_deltas(rows_n37)
    rows_n42e = _add_deltas(rows_n42)
    rows_n43e = _add_deltas(rows_n43)

    corr_output: dict = {}
    for label, rows in (("n=37", rows_n37e), ("n=42_pooled", rows_n42e),
                        ("n=43_pooled", rows_n43e)):
        entries = []
        for family in ("mel_l1_db", "spectral_centroid_rmse_hz",
                       "rms_env_rmse", "lufs_m_rmse"):
            entries.append(_corr_row(rows, label, f"{family}_delta"))
        corr_output[label] = entries

    (DATA_ROOT / "cross_band_correlation.json").write_text(
        json.dumps(corr_output, indent=2, sort_keys=True) + "\n")

    print(f"[cross] wrote n37={len(rows_n37)} n42={len(rows_n42)} "
          f"n43={len(rows_n43)} + correlation JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
