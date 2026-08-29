#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:05:30Z
# cycle: 34
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v1
# ---
"""Batch orchestrator — salts 0, 1, 2 → verdict against frozen rubric.

Sequence:
  1. Render each salt via render_song.render_song → per-salt outputs.
  2. Measure panel(original_synth_030s, palette_bare) → panel_original.tsv
     and panel(c9_fluidsynth_only_bare, palette_bare) → panel_fluidsynth.tsv
     via scripts.texture.panel.texture_distance (READ-ONLY).
  3. Assemble batch_manifest.json + summary.tsv.
  4. Compute spread_analysis.json via scripts.gen_palette_batch_v1.spread_analysis.
  5. Resolve verdict against docs/palette_driven_batch_v1_rubric.md;
     write verdict.json with rubric_hash byte-equal to rubric_hash.txt.
  6. Write anchor_preservation.json snapshotting c33 palette-render +
     c31 palette-v1 SHAs.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.texture.panel import texture_distance, PUBLIC_KEYS  # noqa: E402
from scripts.gen_palette_batch_v1.render_song import render_song  # noqa: E402
from scripts.gen_palette_batch_v1.spread_analysis import compute_spread  # noqa: E402

OUT_DIR = _REPO / "data" / "gen_palette_batch_v1"
SALTS = (0, 1, 2)
NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")

# c9 read-only anchor pair (also used by c33 as reference)
C9_ORIGINAL = _REPO / "data" / "tex" / "renders" / "synth_030s" / "original.wav"
C9_FLUIDSYNTH_ONLY = _REPO / "data" / "tex" / "renders" / "synth_030s" / "bare_midi.wav"

# c33 single-seed reference deltas — for the "≥ half" test of BATCH_SPREAD_EXPECTED
# Sourced from data/palette_render/panel_fluidsynth_vs_palette.tsv verbatim.
C33_FLUIDSYNTH_VS_PALETTE = {
    "mel_l1_db": 23.67853609720866,
    "spectral_centroid_rmse_hz": 3094.505481736623,
    "rms_env_rmse": 0.06498941034078598,
    "lufs_m_rmse_lu": 6.688534736633301,
}


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _read_wav(p: Path) -> tuple[np.ndarray, int]:
    y, sr = sf.read(str(p), always_2d=True)
    return y, sr


def _panel(a: Path, b: Path) -> dict:
    ya, sra = _read_wav(a)
    yb, srb = _read_wav(b)
    if sra != srb:
        raise RuntimeError(f"SR mismatch: {a}={sra} vs {b}={srb}")
    return texture_distance(ya, yb, sra)


def _write_tsv(panel: dict, out_path: Path) -> None:
    keys = sorted(PUBLIC_KEYS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\t".join(keys) + "\n")
        row = []
        for k in keys:
            v = panel.get(k)
            row.append("" if v is None else str(v))
        f.write("\t".join(row) + "\n")


def _panels_finite(panel: dict) -> tuple[bool, str]:
    if set(panel.keys()) != set(PUBLIC_KEYS):
        return False, f"key-set mismatch: {sorted(panel.keys())}"
    for k in NUMERIC_KEYS:
        v = panel.get(k)
        if v is None or not np.isfinite(v):
            return False, f"non-finite numeric key {k}: {v}"
    return True, "ok"


def _anchor_snapshot() -> dict:
    def _dir_shas(d: Path) -> dict:
        if not d.exists():
            return {}
        return {p.name: _sha256_file(p) for p in sorted(d.iterdir())
                if p.is_file() and p.suffix in (".py", ".json", ".yaml", ".yml", ".txt")}
    return {
        "scripts_palette_render": _dir_shas(_REPO / "scripts" / "palette_render"),
        "scripts_palette": _dir_shas(_REPO / "scripts" / "palette"),
        "scripts_palette_schema": _dir_shas(_REPO / "scripts" / "palette" / "schema"),
        "scripts_palette_probe": _dir_shas(_REPO / "scripts" / "palette_probe"),
        "scripts_texture_panel": _sha256_file(_REPO / "scripts" / "texture" / "panel.py"),
        "data_rules_ledger": _sha256_file(_REPO / "data" / "rules" / "ledger.jsonl"),
    }


def _resolve_verdict(per_salt: list[dict],
                     per_salt_panels: dict[int, dict[str, dict]],
                     spread: dict) -> tuple[str, dict]:
    """Resolve verdict against the frozen rubric."""
    reasons: list[str] = []
    # BATCH_FAILS gate.
    for s in per_salt:
        salt = s["salt"]
        if not s["bare_combined_sha_equal"]:
            reasons.append(f"salt={salt} bare_combined SHAs differ across runs")
        for stem, eq in s["per_stem_sha_equal"].items():
            if not eq:
                reasons.append(f"salt={salt} stem={stem} per-stem SHAs differ")
    for salt, panels in per_salt_panels.items():
        for pname, panel in panels.items():
            ok, msg = _panels_finite(panel)
            if not ok:
                reasons.append(f"salt={salt} panel={pname}: {msg}")

    if reasons:
        return "BATCH_FAILS", {"reasons": reasons}

    # Distinct SHA count.
    sha_set = {s["bare_combined_sha_run1"] for s in per_salt}
    n_distinct = len(sha_set)

    # IQR-vs-half-c33 test on panel_fluidsynth_vs_palette.
    any_key_meets = False
    per_key_iqr_flags = {}
    for k in NUMERIC_KEYS:
        iqr = spread["per_key"]["panel_fluidsynth"][k]["iqr"]
        half_c33 = 0.5 * abs(C33_FLUIDSYNTH_VS_PALETTE[k])
        meets = iqr >= half_c33
        per_key_iqr_flags[k] = {"iqr": iqr, "half_c33": half_c33, "meets": meets}
        if meets:
            any_key_meets = True

    if n_distinct >= 2 and any_key_meets:
        return "BATCH_SPREAD_EXPECTED", {
            "distinct_sha_count": n_distinct,
            "any_iqr_meets_half_c33": True,
            "per_key_iqr_flags": per_key_iqr_flags,
        }
    if n_distinct == 1:
        return "BATCH_SPREAD_COLLAPSED", {
            "distinct_sha_count": 1,
            "reason": "all 3 salts yield the SAME bare_combined.wav SHA",
            "per_key_iqr_flags": per_key_iqr_flags,
        }
    # Partial collapse (2 distinct, no key meets threshold): still COLLAPSED
    return "BATCH_SPREAD_COLLAPSED", {
        "distinct_sha_count": n_distinct,
        "reason": "SHA distinct but no numeric-family IQR meets the half-of-c33 bar",
        "per_key_iqr_flags": per_key_iqr_flags,
    }


def run_batch() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rubric_hash = (OUT_DIR / "rubric_hash.txt").read_text().strip()

    # Verify c9 anchor pair present.
    if not C9_ORIGINAL.is_file() or not C9_FLUIDSYNTH_ONLY.is_file():
        raise RuntimeError(f"c9 anchor pair missing: {C9_ORIGINAL} / {C9_FLUIDSYNTH_ONLY}")

    per_salt: list[dict] = []
    per_salt_panels: dict[int, dict[str, dict]] = {}
    per_song_dir = OUT_DIR / "per_song"
    per_song_dir.mkdir(parents=True, exist_ok=True)

    for salt in SALTS:
        song_dir = per_song_dir / f"{salt}"
        song_dir.mkdir(parents=True, exist_ok=True)
        song = render_song(salt, song_dir)
        per_salt.append(song)

        bare_wav = Path(song["bare_combined_wav"])
        panel_original = _panel(C9_ORIGINAL, bare_wav)
        panel_fluidsynth = _panel(C9_FLUIDSYNTH_ONLY, bare_wav)
        _write_tsv(panel_original, song_dir / "panel_original.tsv")
        _write_tsv(panel_fluidsynth, song_dir / "panel_fluidsynth.tsv")
        per_salt_panels[salt] = {
            "panel_original": panel_original,
            "panel_fluidsynth": panel_fluidsynth,
        }

    # summary.tsv
    with open(OUT_DIR / "summary.tsv", "w") as f:
        f.write("salt\tpanel\t" + "\t".join(sorted(PUBLIC_KEYS)) + "\n")
        for salt in SALTS:
            for pname, panel in per_salt_panels[salt].items():
                row = [str(salt), pname]
                for k in sorted(PUBLIC_KEYS):
                    v = panel.get(k)
                    row.append("" if v is None else str(v))
                f.write("\t".join(row) + "\n")

    # spread_analysis
    spread = compute_spread(per_salt, per_salt_panels)
    (OUT_DIR / "spread_analysis.json").write_text(
        json.dumps(spread, sort_keys=True, indent=2) + "\n"
    )

    # verdict
    verdict, evidence = _resolve_verdict(per_salt, per_salt_panels, spread)

    # anchor snapshot
    anchor_snapshot = _anchor_snapshot()
    (OUT_DIR / "anchor_preservation.json").write_text(
        json.dumps({
            "captured_at": "post-batch",
            "anchors": anchor_snapshot,
        }, sort_keys=True, indent=2) + "\n"
    )

    # batch_manifest
    manifest = {
        "cycle": 34,
        "branch": "clone-2 (fork 43802db1a81c)",
        "milestone": "M-GEN-1/palette-driven-batch-v1",
        "salts": list(SALTS),
        "rubric_hash": rubric_hash,
        "per_salt": [
            {
                "salt": s["salt"],
                "rule_ids_by_type": {
                    rt: s["assignment_rows"][0]["provenance_pointers"]
                    for rt in ("harmonic",)  # pointers are identical across stems per song
                },
                "provenance_pointers": s["assignment_rows"][0]["provenance_pointers"],
                "assignment_ids": [a["assignment_id"] for a in s["assignment_rows"]],
                "per_stem_instrument": {a["stem"]: a["instrument"] for a in s["assignment_rows"]},
                "bare_combined_sha_run1": s["bare_combined_sha_run1"],
                "bare_combined_sha_run2": s["bare_combined_sha_run2"],
                "bare_combined_sha_equal": s["bare_combined_sha_equal"],
                "per_stem_sha_equal": s["per_stem_sha_equal"],
            }
            for s in per_salt
        ],
        "verdict": verdict,
    }
    (OUT_DIR / "batch_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    )

    # verdict.json (embeds rubric_hash verbatim)
    verdict_obj = {
        "verdict": verdict,
        "rubric_hash": rubric_hash,
        "evidence": evidence,
        "distinct_bare_combined_shas": sorted({s["bare_combined_sha_run1"] for s in per_salt}),
        "per_salt_panel_key_summaries": {
            str(salt): {
                pname: {k: panel.get(k) for k in sorted(PUBLIC_KEYS)}
                for pname, panel in per_salt_panels[salt].items()
            }
            for salt in SALTS
        },
        "c33_single_seed_reference_deltas": C33_FLUIDSYNTH_VS_PALETTE,
    }
    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict_obj, sort_keys=True, indent=2) + "\n"
    )

    return {"verdict": verdict, "manifest": manifest, "spread": spread}


def main() -> int:
    result = run_batch()
    print(json.dumps({"verdict": result["verdict"]}, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
