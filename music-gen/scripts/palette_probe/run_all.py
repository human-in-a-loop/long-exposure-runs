#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T02:30:00Z
# cycle: 31
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-instrument-determinism
# ---
"""Cycle-31 driver: run each palette instrument probe × 2 in fresh temp
dirs, verify SHA-256 byte-identity on render.wav and pinned_state.json,
apply ONE refinement (pinned save/load state) if the initial run drifts,
and emit the verdict TSV + per-instrument SHA files + fetchability
ladder JSONL.

No PRNG. /usr/bin/python3 guarded. Cycle-9 chain NOT imported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.palette_probe import _shared as sh  # noqa: E402

assert sys.executable == "/usr/bin/python3", sys.executable

WORKSPACE = Path(__file__).resolve().parents[2]
OUT_ROOT = WORKSPACE / "data" / "palette_probe"
PER_INST = OUT_ROOT / "per_instrument"
INSTRUMENTS = [
    {
        "key": "surge_xt",
        "script": WORKSPACE / "scripts" / "palette_probe" / "surge_xt.py",
        "fetchable_check": lambda: Path("/usr/lib/vst3/Surge XT.vst3").exists(),
        "loader_pathway": "dawdreamer_vst3",
        "binary_path": "/usr/lib/vst3/Surge XT.vst3",
        "supports_state_pinning": True,
    },
    {
        "key": "dexed",
        "script": WORKSPACE / "scripts" / "palette_probe" / "dexed.py",
        "fetchable_check": lambda: Path("/usr/lib/vst3/Dexed.vst3").exists(),
        "loader_pathway": "dawdreamer_vst3",
        "binary_path": "/usr/lib/vst3/Dexed.vst3",
        "supports_state_pinning": True,
    },
    {
        "key": "sfizz",
        "script": WORKSPACE / "scripts" / "palette_probe" / "sfizz.py",
        "fetchable_check": lambda: (
            Path("/usr/bin/sfizz_render").exists()
            and (WORKSPACE / "data" / "texture" / "test.sfz").exists()
        ),
        "loader_pathway": "sfizz_render_cli",
        "binary_path": "/usr/bin/sfizz_render",
        "supports_state_pinning": False,  # CLI has no plugin state buffer
    },
]

ENV = {
    **os.environ,
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}

TSV_COLS = [
    "instrument", "fetchable", "loadable",
    "run1_wav_sha", "run2_wav_sha", "run1_state_sha", "run2_state_sha",
    "sha_equal_initial", "refinement_applied", "refinement_description",
    "run1_wav_sha_refined", "run2_wav_sha_refined", "verdict",
]


def _sha(p: Path) -> str:
    return sh.sha256_of_path(p)


def _run_probe(script: Path, out_dir: Path, extra: list[str] | None = None) -> tuple[bool, str]:
    cmd = ["/usr/bin/python3", str(script), "--out-dir", str(out_dir)]
    if extra:
        cmd.extend(extra)
    r = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=300)
    if r.returncode != 0:
        return False, (r.stderr or r.stdout)[:2000]
    return True, ""


def _probe_pair(script: Path, extra_first: list[str] | None = None,
                extra_second: list[str] | None = None) -> dict:
    """Run probe twice in fresh temp dirs (kept under workspace so sandbox allows them)."""
    scratch = OUT_ROOT / "_scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    d1 = Path(tempfile.mkdtemp(prefix="run1_", dir=str(scratch)))
    d2 = Path(tempfile.mkdtemp(prefix="run2_", dir=str(scratch)))
    ok1, err1 = _run_probe(script, d1, extra_first)
    ok2, err2 = _run_probe(script, d2, extra_second)
    result = {"d1": d1, "d2": d2, "ok1": ok1, "ok2": ok2, "err1": err1, "err2": err2}
    if ok1 and ok2:
        result["wav1"] = _sha(d1 / "render.wav")
        result["wav2"] = _sha(d2 / "render.wav")
        result["st1"] = _sha(d1 / "pinned_state.json")
        result["st2"] = _sha(d2 / "pinned_state.json")
    return result


def _record_shas(inst_key: str, wav1: str, wav2: str, st1: str, st2: str,
                 pinned_state_src: Path) -> None:
    d = PER_INST / inst_key
    d.mkdir(parents=True, exist_ok=True)
    (d / "run1_wav_sha").write_text(wav1 + "\n")
    (d / "run2_wav_sha").write_text(wav2 + "\n")
    (d / "run1_state_sha").write_text(st1 + "\n")
    (d / "run2_state_sha").write_text(st2 + "\n")
    if pinned_state_src.exists():
        shutil.copyfile(pinned_state_src, d / "pinned_state.json")


def _record_refined_shas(inst_key: str, wav1r: str, wav2r: str) -> None:
    d = PER_INST / inst_key
    d.mkdir(parents=True, exist_ok=True)
    (d / "run1_wav_sha_refined").write_text(wav1r + "\n")
    (d / "run2_wav_sha_refined").write_text(wav2r + "\n")


def _write_refinement_json(inst_key: str, drift_source: str, pinning_change: str,
                           drift_before: float, state_drift_keys: list[str]) -> None:
    d = PER_INST / inst_key
    d.mkdir(parents=True, exist_ok=True)
    payload = {
        "drift_source": drift_source,
        "pinning_change": pinning_change,
        "wav_max_abs_drift_before": drift_before,
        "state_drift_keys": state_drift_keys,
    }
    (d / "refinement.json").write_text(sh.canonical_json(payload) + "\n")


def _diff_wav_max_abs(a: Path, b: Path) -> float:
    """Max-abs int16-sample difference between two WAVs, normalized to [0,1]."""
    import wave
    import numpy as np
    try:
        with wave.open(str(a), "rb") as wa, wave.open(str(b), "rb") as wb:
            fa = wa.readframes(wa.getnframes())
            fb = wb.readframes(wb.getnframes())
        arr_a = np.frombuffer(fa, dtype=np.int16).astype(np.int32)
        arr_b = np.frombuffer(fb, dtype=np.int16).astype(np.int32)
        n = min(len(arr_a), len(arr_b))
        if n == 0:
            return 0.0
        return float(np.max(np.abs(arr_a[:n] - arr_b[:n]))) / 32768.0
    except Exception:
        return -1.0


def _diff_state_keys(a: Path, b: Path) -> list[str]:
    try:
        sa = json.loads(a.read_text())
        sb = json.loads(b.read_text())
    except Exception:
        return ["<UNPARSEABLE>"]
    keys = []
    for k in set(sa) | set(sb):
        if sa.get(k) != sb.get(k):
            keys.append(k)
    return sorted(keys)


def _emit_fetchability(rows: list[dict]) -> None:
    """Append to fetchability ladder JSONL (one row per instrument)."""
    p = OUT_ROOT / "fetchability_ladder.jsonl"
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def _emit_tsv(rows: list[dict]) -> None:
    p = OUT_ROOT / "instrument_determinism.tsv"
    with open(p, "w") as f:
        f.write("\t".join(TSV_COLS) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in TSV_COLS) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-refinement", action="store_true",
                    help="For debugging: skip the refinement pass.")
    args = ap.parse_args()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "_scratch").mkdir(parents=True, exist_ok=True)

    tsv_rows: list[dict] = []
    fetch_rows: list[dict] = []

    for inst in INSTRUMENTS:
        key = inst["key"]
        row: dict = {"instrument": key}
        fetchable = inst["fetchable_check"]()
        row["fetchable"] = "true" if fetchable else "false"
        fetch_entry = {
            "instrument": key,
            "fetchable": fetchable,
            "loader_pathway": inst["loader_pathway"],
            "binary_path": inst["binary_path"],
            "binary_present": Path(inst["binary_path"]).exists(),
            "reference_sfz_present": (
                (WORKSPACE / "data" / "texture" / "test.sfz").exists()
                if key == "sfizz" else None
            ),
        }
        if not fetchable:
            row.update({
                "loadable": "false", "run1_wav_sha": "", "run2_wav_sha": "",
                "run1_state_sha": "", "run2_state_sha": "",
                "sha_equal_initial": "false", "refinement_applied": "false",
                "refinement_description": "instrument not fetchable in workspace",
                "run1_wav_sha_refined": "", "run2_wav_sha_refined": "",
                "verdict": "STILL_GAP",
            })
            fetch_entry["loadable"] = False
            fetch_entry["failure_reason"] = "binary or reference file missing"
            tsv_rows.append(row)
            fetch_rows.append(fetch_entry)
            continue

        # Run × 2 fresh
        r = _probe_pair(inst["script"])
        loadable = r["ok1"] and r["ok2"]
        row["loadable"] = "true" if loadable else "false"
        fetch_entry["loadable"] = loadable
        if not loadable:
            fetch_entry["failure_reason"] = (r["err1"] or r["err2"])[:500]
            row.update({
                "run1_wav_sha": "", "run2_wav_sha": "",
                "run1_state_sha": "", "run2_state_sha": "",
                "sha_equal_initial": "false",
                "refinement_applied": "false",
                "refinement_description": "instrument not loadable — see fetchability ladder",
                "run1_wav_sha_refined": "", "run2_wav_sha_refined": "",
                "verdict": "STILL_GAP",
            })
            tsv_rows.append(row)
            fetch_rows.append(fetch_entry)
            continue

        wav1, wav2, st1, st2 = r["wav1"], r["wav2"], r["st1"], r["st2"]
        _record_shas(key, wav1, wav2, st1, st2, r["d1"] / "pinned_state.json")

        eq_initial = (wav1 == wav2) and (st1 == st2)
        row.update({
            "run1_wav_sha": wav1, "run2_wav_sha": wav2,
            "run1_state_sha": st1, "run2_state_sha": st2,
            "sha_equal_initial": "true" if eq_initial else "false",
        })

        if eq_initial:
            row.update({
                "refinement_applied": "false", "refinement_description": "",
                "run1_wav_sha_refined": "", "run2_wav_sha_refined": "",
                "verdict": "GREEN",
            })
            tsv_rows.append(row)
            fetch_rows.append(fetch_entry)
            continue

        # Drift detected — apply ONE refinement.
        state_drift = _diff_state_keys(r["d1"] / "pinned_state.json",
                                       r["d2"] / "pinned_state.json")
        drift_amt = _diff_wav_max_abs(r["d1"] / "render.wav",
                                      r["d2"] / "render.wav")

        if args.skip_refinement or not inst["supports_state_pinning"]:
            row.update({
                "refinement_applied": "false",
                "refinement_description": "refinement pathway unavailable for this instrument",
                "run1_wav_sha_refined": "", "run2_wav_sha_refined": "",
                "verdict": "STILL_GAP",
            })
            _write_refinement_json(key, "wav_render_drift",
                                    "no pinning available", drift_amt, state_drift)
            tsv_rows.append(row)
            fetch_rows.append(fetch_entry)
            continue

        # Refinement: capture state from run1 of a warm-up pass, then
        # force both refinement runs to load it. This pins internal
        # plugin RNG / init state that lives outside parameter space.
        warm = Path(tempfile.mkdtemp(prefix="warm_", dir=str(OUT_ROOT / "_scratch")))
        state_bin = OUT_ROOT / "_scratch" / f"{key}_pinned_state.bin"
        ok_w, err_w = _run_probe(
            inst["script"], warm,
            ["--state-out", str(state_bin)],
        )
        pinning_change = (
            f"Captured plugin.get_state() from a warm-up render and "
            f"replayed via plugin.load_state() in both refinement runs. "
            f"external_state_sha256 is now the SHA-256 of the pinned state buffer."
        )
        if not ok_w or not state_bin.exists() or state_bin.stat().st_size == 0:
            row.update({
                "refinement_applied": "true",
                "refinement_description": (
                    "attempted plugin.get_state() capture; the plugin's "
                    "DawDreamer state API returned empty or failed — no "
                    "further pinning available"
                ),
                "run1_wav_sha_refined": "", "run2_wav_sha_refined": "",
                "verdict": "STILL_GAP",
            })
            _write_refinement_json(key, "wav_render_drift",
                                    "plugin state API empty", drift_amt, state_drift)
            tsv_rows.append(row)
            fetch_rows.append(fetch_entry)
            continue

        r2 = _probe_pair(inst["script"],
                         extra_first=["--state-in", str(state_bin)],
                         extra_second=["--state-in", str(state_bin)])
        if r2["ok1"] and r2["ok2"]:
            wav1r, wav2r = r2["wav1"], r2["wav2"]
            st1r, st2r = r2["st1"], r2["st2"]
            eq_refined = (wav1r == wav2r) and (st1r == st2r)
            _record_refined_shas(key, wav1r, wav2r)
            _write_refinement_json(key, "wav_render_drift", pinning_change,
                                   drift_amt, state_drift)
            row.update({
                "refinement_applied": "true",
                "refinement_description": pinning_change,
                "run1_wav_sha_refined": wav1r,
                "run2_wav_sha_refined": wav2r,
                "verdict": "REDEFINED_GAP" if eq_refined else "STILL_GAP",
            })
            # Overwrite the per-instrument pinned_state.json with the
            # refined-run version so the report references pinned state.
            if eq_refined:
                shutil.copyfile(
                    r2["d1"] / "pinned_state.json",
                    PER_INST / key / "pinned_state.json",
                )
        else:
            row.update({
                "refinement_applied": "true",
                "refinement_description": (
                    "refinement probe pair failed to complete: "
                    + (r2["err1"] or r2["err2"])[:200]
                ),
                "run1_wav_sha_refined": "", "run2_wav_sha_refined": "",
                "verdict": "STILL_GAP",
            })

        tsv_rows.append(row)
        fetch_rows.append(fetch_entry)

    _emit_tsv(tsv_rows)
    _emit_fetchability(fetch_rows)

    # Print a compact summary for the log.
    for row in tsv_rows:
        print(f"{row['instrument']:12s} "
              f"fetchable={row['fetchable']:5s} "
              f"loadable={row['loadable']:5s} "
              f"eq_initial={row['sha_equal_initial']:5s} "
              f"refined={row['refinement_applied']:5s} "
              f"verdict={row['verdict']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
