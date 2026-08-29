#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:13:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v2-sampler-diversified
# ---
"""Batch-v2 sampler-diversified orchestrator — salts 0, 1, 2 → verdict.

Sequence:
  1. Compute per-salt DIFFERENT rule triples via sample_rule_triple_v2.
  2. Snapshot c31/c33/c34 anchor SHAs (pre-run).
  3. For each salt: render_song(salt, triple) → per-salt outputs (v1 audio
     + v2 perturbed payloads authored).
  4. Measure panel(original_synth_030s, palette_bare) → panel_original.tsv
     and panel(c9_fluidsynth_only_bare, palette_bare) → panel_fluidsynth.tsv
     via scripts.texture.panel.texture_distance READ-ONLY.
  5. Assemble batch_manifest.json + summary.tsv.
  6. Compute spread_analysis.json via
     scripts.gen_palette_batch_v2.spread_analysis.compute_spread.
  7. Resolve verdict against the frozen rubric; write verdict.json with
     rubric_hash byte-equal to rubric_hash.txt.
  8. Snapshot anchors post-run; write anchor_preservation.json.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.texture.panel import texture_distance, PUBLIC_KEYS  # noqa: E402
from scripts.gen_palette_batch_v2.render_song import render_song  # noqa: E402
from scripts.gen_palette_batch_v2.sample_rule_triple_v2 import (  # noqa: E402
    sample_triples,
)
from scripts.gen_palette_batch_v2.spread_analysis import compute_spread  # noqa: E402

OUT_DIR = _REPO / "data" / "gen_palette_batch_v2"
SALTS = (0, 1, 2)
NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")
SPREAD_TOLERANCE = 1e-6  # per rubric

C9_ORIGINAL = _REPO / "data" / "tex" / "renders" / "synth_030s" / "original.wav"
C9_FLUIDSYNTH_ONLY = _REPO / "data" / "tex" / "renders" / "synth_030s" / "bare_midi.wav"


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


def _panel_finite(panel: dict) -> tuple[bool, str]:
    if set(panel.keys()) != set(PUBLIC_KEYS):
        return False, f"key-set mismatch: {sorted(panel.keys())}"
    for k in NUMERIC_KEYS:
        v = panel.get(k)
        if v is None or not np.isfinite(v):
            return False, f"non-finite numeric key {k}: {v}"
    return True, "ok"


def _anchor_snapshot() -> dict:
    """Snapshot mtime + SHA-256 of c31/c33/c34/panel/rules anchors."""
    def _dir(d: Path) -> dict:
        if not d.exists():
            return {}
        out = {}
        for p in sorted(d.rglob("*")):
            if p.is_file() and p.suffix in (".py", ".json", ".yaml",
                                            ".yml", ".txt", ".md",
                                            ".sha", ".jsonl"):
                rel = str(p.relative_to(d))
                out[rel] = {"sha": _sha256_file(p),
                            "mtime": int(p.stat().st_mtime)}
        return out
    snap = {
        "scripts_palette_v2": _dir(_REPO / "scripts" / "palette_v2"),
        "data_palette_v2": _dir(_REPO / "data" / "palette_v2"),
        "scripts_palette_render": _dir(_REPO / "scripts" / "palette_render"),
        "data_palette_render": _dir(_REPO / "data" / "palette_render"),
        "scripts_dawdreamer_state": _dir(_REPO / "scripts" / "dawdreamer_state"),
        "data_dawdreamer_state": _dir(_REPO / "data" / "dawdreamer_state"),
        "scripts_palette": _dir(_REPO / "scripts" / "palette"),
        "scripts_palette_probe": _dir(_REPO / "scripts" / "palette_probe"),
        "data_palette": _dir(_REPO / "data" / "palette"),
        "data_palette_probe": _dir(_REPO / "data" / "palette_probe"),
        "scripts_texture_panel_py":
            {"sha": _sha256_file(_REPO / "scripts" / "texture" / "panel.py")},
        "data_rules_ledger_jsonl":
            {"sha": _sha256_file(_REPO / "data" / "rules" / "ledger.jsonl")},
    }
    return snap


def _egress_probe_row() -> dict:
    """Non-blocking egress probe. Records a status row into
    data/ingestion/egress_status.jsonl per cycle contract."""
    import time
    row = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cycle": 35,
        "clone": "clone-1",
        "resource": "workspace/harvest_playlists.sh",
        "media_ok": False,
        "metadata_ok": False,
        "http_code": None,
        "note": "cycle-35 branch-B non-blocking probe; audio egress unchanged",
    }
    egress_path = _REPO / "data" / "ingestion" / "egress_status.jsonl"
    egress_path.parent.mkdir(parents=True, exist_ok=True)
    with open(egress_path, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def _resolve_verdict(per_salt: list[dict],
                     per_salt_panels: dict[int, dict[str, dict]],
                     spread: dict) -> tuple[str, dict]:
    """Resolve verdict against the frozen rubric."""
    fail_reasons: list[str] = []
    for s in per_salt:
        salt = s["salt"]
        if not s["bare_combined_sha_equal"]:
            fail_reasons.append(
                f"salt={salt} bare_combined SHAs differ across runs "
                f"(run1={s['bare_combined_sha_run1'][:12]}, "
                f"run2={s['bare_combined_sha_run2'][:12]})"
            )
        for stem, eq in s["per_stem_sha_equal"].items():
            if not eq:
                fail_reasons.append(f"salt={salt} stem={stem} per-stem SHAs differ")
    for salt, panels in per_salt_panels.items():
        for pname, panel in panels.items():
            ok, msg = _panel_finite(panel)
            if not ok:
                fail_reasons.append(f"salt={salt} panel={pname}: {msg}")
    if fail_reasons:
        return "BATCH_FAILS", {"reasons": fail_reasons}

    sha_set = {s["bare_combined_sha_run1"] for s in per_salt}
    n_distinct = len(sha_set)

    # Per-key spread flags on both panels
    key_flags = {"panel_original": {}, "panel_fluidsynth": {}}
    for pname in key_flags:
        for k in NUMERIC_KEYS:
            entry = spread["per_key"][pname][k]
            iqr = entry["iqr"]
            mm = entry["max_minus_min"]
            key_flags[pname][k] = {
                "iqr": iqr, "max_minus_min": mm,
                "meets_spread": (iqr > SPREAD_TOLERANCE
                                 and mm > SPREAD_TOLERANCE),
            }

    all_orig_meet = all(key_flags["panel_original"][k]["meets_spread"]
                        for k in NUMERIC_KEYS)
    any_meet = any(key_flags[pname][k]["meets_spread"]
                   for pname in key_flags for k in NUMERIC_KEYS)
    all_flat = not any_meet

    evidence = {
        "distinct_bare_combined_sha_count": n_distinct,
        "distinct_bare_combined_shas": sorted(sha_set),
        "spread_tolerance": SPREAD_TOLERANCE,
        "per_key_spread_flags": key_flags,
        "all_panel_original_numeric_keys_meet_spread": all_orig_meet,
        "any_numeric_key_meets_spread": any_meet,
    }

    # SPREAD_STILL_COLLAPSED gate (either fully collapsed or numeric flat).
    if n_distinct == 1 or all_flat:
        evidence["reason"] = ("all 3 salts yield identical bare_combined SHA"
                              if n_distinct == 1
                              else "numeric spread flat on every numeric key of both panels")
        return "SPREAD_STILL_COLLAPSED", evidence

    if n_distinct == 3 and all_orig_meet:
        return "SPREAD_ACHIEVED", evidence

    return "SPREAD_PARTIAL", evidence


def run_batch() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rubric_hash = (OUT_DIR / "rubric_hash.txt").read_text().strip()

    if not C9_ORIGINAL.is_file() or not C9_FLUIDSYNTH_ONLY.is_file():
        raise RuntimeError(
            f"c9 anchor pair missing: {C9_ORIGINAL} / {C9_FLUIDSYNTH_ONLY}"
        )

    # Egress probe row (non-blocking).
    egress_row = _egress_probe_row()

    # Anchor snapshot (pre-run).
    anchor_pre = _anchor_snapshot()

    # Per-salt rule triples (cross-salt distinctness enforced).
    triples = sample_triples(list(SALTS))
    assignments_shas = {}
    for salt, triple in triples.items():
        payload = json.dumps(triple, sort_keys=True, separators=(",", ":"))
        assignments_shas[salt] = hashlib.sha256(payload.encode("ascii")).hexdigest()

    per_salt: list[dict] = []
    per_salt_panels: dict[int, dict[str, dict]] = {}
    per_song_dir = OUT_DIR / "per_song"
    per_song_dir.mkdir(parents=True, exist_ok=True)

    for salt in SALTS:
        song_dir = per_song_dir / f"{salt}"
        song_dir.mkdir(parents=True, exist_ok=True)
        song = render_song(salt, song_dir, triple=triples[salt])
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

    # Verdict
    verdict, evidence = _resolve_verdict(per_salt, per_salt_panels, spread)

    # Anchor snapshot (post-run) + preservation record
    anchor_post = _anchor_snapshot()
    anchor_unchanged = anchor_pre == anchor_post
    (OUT_DIR / "anchor_preservation.json").write_text(
        json.dumps({
            "captured_at": "post-batch",
            "unchanged": anchor_unchanged,
            "pre": anchor_pre,
            "post": anchor_post,
        }, sort_keys=True, indent=2) + "\n"
    )

    # Between-salt inequality on assignments SHA (rule triples are distinct)
    assignments_all_distinct = (len(set(assignments_shas.values())) == len(SALTS))

    # batch_manifest
    manifest = {
        "cycle": 35,
        "branch": "clone-1 (fork 07063458736e)",
        "milestone": "M-GEN-1/palette-driven-batch-v2-sampler-diversified",
        "salts": list(SALTS),
        "rubric_hash": rubric_hash,
        "egress_probe_row": egress_row,
        "assignments_sha_per_salt": {str(s): assignments_shas[s]
                                     for s in SALTS},
        "assignments_all_distinct": assignments_all_distinct,
        "per_salt": [
            {
                "salt": s["salt"],
                "rule_triple": s["rule_triple"],
                "provenance_pointers": s["assignment_rows_v1"][0]["provenance_pointers"],
                "assignment_ids_v1": [a["assignment_id"]
                                      for a in s["assignment_rows_v1"]],
                "v2_perturbed_summary": s["v2_perturbed_summary"],
                "per_stem_instrument": {a["stem"]: a["instrument"]
                                        for a in s["assignment_rows_v1"]},
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

    # verdict.json (rubric_hash embedded verbatim)
    verdict_obj = {
        "verdict": verdict,
        "rubric_hash": rubric_hash,
        "evidence": evidence,
        "distinct_bare_combined_shas": sorted({s["bare_combined_sha_run1"]
                                               for s in per_salt}),
        "per_salt_panel_key_summaries": {
            str(salt): {
                pname: {k: panel.get(k) for k in sorted(PUBLIC_KEYS)}
                for pname, panel in per_salt_panels[salt].items()
            }
            for salt in SALTS
        },
        "per_salt_rule_triples": {str(s): triples[s] for s in SALTS},
        "assignments_sha_per_salt": {str(s): assignments_shas[s] for s in SALTS},
        "assignments_all_distinct": assignments_all_distinct,
        "anchor_preservation_unchanged": anchor_unchanged,
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
