#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T12:10:00Z
# cycle: 11
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork ddd71e9bdb0e)
# milestone: M-GEN-1/batch-v1
# ---
"""Batch orchestrator: 5 songs across salts 0..4, coherence-gated.

Pipeline per song (salt s in 0..4):
    1. rs_raw = sample_ruleset(ledger, salt=s)
    2. rs_coerced, coercions = enforce_coherence(rs_raw)
    3. assemble_score(rs_coerced, out_dir/'generated.musicxml', duration_s=30.0)
    4. render(xml, out_dir) → generated.mid, bare_midi.wav, effects_layered.wav
    5. score(bare, effects, out_dir/'scoring.json')
    6. write coercions.json and per-song provenance rows.

Aggregates written to data/gen/batch_v1/:
    * summary.tsv         (one row per salt with heuristics + panel + ear + coercions_json)
    * provenance.jsonl    (per-song stage rows: input_shas -> output_shas)
    * batch_manifest.json (top-level SHAs + collision assertion)

Determinism / non-collision assertions run at the end.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Pins must be set BEFORE downstream imports pull in numpy/torch.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.gen.sample_rules import sample_ruleset  # noqa: E402
from scripts.gen.coherence_gate import enforce_coherence  # noqa: E402
from scripts.gen.assemble_score import assemble_score  # noqa: E402
from scripts.gen.render_pipeline import render  # noqa: E402
from scripts.gen.score_generation import score  # noqa: E402


SALTS = (0, 1, 2, 3, 4)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _batch_root(base: Path | None = None) -> Path:
    return (base or _REPO) / "data" / "gen" / "batch_v1"


def _run_one_song(salt: int, ledger: Path, batch_root: Path) -> Dict:
    out_dir = batch_root / f"song_{salt}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sample
    rs_raw = sample_ruleset(ledger, salt=salt)

    # 2. Coherence gate
    rs_coerced, coercions = enforce_coherence(rs_raw)

    # 3. Assemble score
    xml_path = out_dir / "generated.musicxml"
    assemble_score(rs_coerced, xml_path, duration_s=30.0)

    # 4. Render (writes mid, bare, effects into out_dir with fixed names)
    manifest = render(xml_path, out_dir, duration_s=30.0)

    # 5. Score
    scoring_json = out_dir / "scoring.json"
    score(Path(manifest.bare_wav_path), Path(manifest.effects_wav_path), scoring_json)

    # 6. Per-song artifacts
    coercions_json = out_dir / "coercions.json"
    coercions_json.write_text(json.dumps({
        "salt": salt,
        "n_coercions": len(coercions),
        "coercions": coercions,
        "gate_applied_summary": rs_coerced.sampling_manifest.get("coherence_gate", {}),
        "raw_rule_ids": rs_raw.rule_ids(),
        "coerced_rule_ids": rs_coerced.rule_ids(),
    }, indent=2, sort_keys=True))

    # Sampling manifest for this song (with assembler summary).
    sampling_manifest_path = out_dir / "sampling_manifest.json"
    sampling_manifest_path.write_text(json.dumps({
        "salt": salt,
        "chosen_rule_ids": rs_coerced.rule_ids(),
        "sampling_manifest": rs_coerced.sampling_manifest,
    }, indent=2, sort_keys=True))

    scoring = json.loads(scoring_json.read_text())

    try:
        out_dir_rel = str(out_dir.resolve().relative_to(_REPO))
    except ValueError:
        out_dir_rel = str(out_dir)
    return {
        "salt": salt,
        "out_dir": out_dir_rel,
        "coerced_rule_ids": rs_coerced.rule_ids(),
        "n_coercions": len(coercions),
        "coercions": coercions,
        "sha": {
            "musicxml": _sha256(xml_path),
            "midi": manifest.midi_sha256,
            "bare_wav": manifest.bare_wav_sha256,
            "effects_wav": manifest.effects_wav_sha256,
            "scoring_json": _sha256(scoring_json),
            "coercions_json": _sha256(coercions_json),
        },
        "render": {
            "effects_rung": manifest.effects_rung,
            "sf2_sha256": manifest.sf2_sha256,
        },
        "scoring": scoring,
    }


def _flatten_row(rec: Dict) -> Dict[str, str]:
    """Take a song record and emit a flat dict for one TSV row."""
    sc = rec["scoring"]
    heur = sc.get("heuristics", {})
    panel = sc.get("texture_panel_bare_vs_effects", {})
    ear = sc.get("ear", {})
    meta = sc.get("meta_tracker_single_clip", {})

    def _h(name):
        v = heur.get(name, {}).get("mess_scale")
        return "" if v is None else f"{float(v):.6f}"

    def _p(name):
        v = panel.get(name)
        return "" if v is None else (str(v) if isinstance(v, str) else f"{float(v):.6f}")

    return {
        "salt": str(rec["salt"]),
        "sha_musicxml": rec["sha"]["musicxml"][:16],
        "sha_midi": rec["sha"]["midi"][:16],
        "sha_bare_wav": rec["sha"]["bare_wav"][:16],
        "sha_effects_wav": rec["sha"]["effects_wav"][:16],
        "heur_melody": _h("melody_quality"),
        "heur_timbre": _h("timbre_quality"),
        "heur_form": _h("form_quality"),
        "heur_dynamics": _h("dynamics_quality"),
        "meta_dynamics_trajectory_db": ("" if meta.get("dynamics_trajectory_db") is None
                                        else f"{float(meta['dynamics_trajectory_db']):.4f}"),
        "meta_form_coherence": ("" if meta.get("form_coherence") is None
                                else f"{float(meta['form_coherence']):.6f}"),
        "panel_mel_l1_db": _p("mel_l1_db"),
        "panel_spectral_centroid_rmse_hz": _p("spectral_centroid_rmse_hz"),
        "panel_rms_env_rmse": _p("rms_env_rmse"),
        "panel_lufs_m_rmse_lu": _p("lufs_m_rmse_lu"),
        "panel_embedding_cosine": _p("embedding_cosine_distance"),
        "panel_embedding_rung": _p("embedding_rung"),
        "ear_prediction": str(ear.get("prediction", "")),
        "ear_calibration": str(ear.get("calibration", "")),
        "n_coercions": str(rec["n_coercions"]),
        "coercions_json": json.dumps([c["coercion"] for c in rec["coercions"]], separators=(",", ":")),
    }


def _write_summary_tsv(records: List[Dict], out: Path) -> None:
    rows = [_flatten_row(r) for r in records]
    header = list(rows[0].keys())
    lines = ["\t".join(header)]
    for r in rows:
        lines.append("\t".join(r[k] for k in header))
    out.write_text("\n".join(lines) + "\n")


def _write_provenance(records: List[Dict], out: Path, ledger_path: Path) -> None:
    """One row per song stage with input_shas -> output_shas transitions."""
    ledger_sha = _sha256(ledger_path)
    rows = []
    for rec in records:
        salt = rec["salt"]
        sha = rec["sha"]
        rows.append({"salt": salt, "stage": "sample_rules",
                     "input_shas": {"rules_ledger": ledger_sha, "salt": salt},
                     "output_shas": {"chosen_rule_ids": rec["coerced_rule_ids"]}})
        rows.append({"salt": salt, "stage": "coherence_gate",
                     "input_shas": {"chosen_rule_ids": rec["coerced_rule_ids"]},
                     "output_shas": {"n_coercions": rec["n_coercions"],
                                     "coerced_rule_ids": rec["coerced_rule_ids"]}})
        rows.append({"salt": salt, "stage": "assemble_score",
                     "input_shas": {"coerced_rule_ids": rec["coerced_rule_ids"]},
                     "output_shas": {"musicxml": sha["musicxml"]}})
        rows.append({"salt": salt, "stage": "xml_to_midi",
                     "input_shas": {"musicxml": sha["musicxml"]},
                     "output_shas": {"midi": sha["midi"]}})
        rows.append({"salt": salt, "stage": "render_bare",
                     "input_shas": {"midi": sha["midi"],
                                    "sf2_sha256": rec["render"]["sf2_sha256"]},
                     "output_shas": {"bare_wav": sha["bare_wav"]}})
        rows.append({"salt": salt, "stage": "render_effects",
                     "input_shas": {"bare_wav": sha["bare_wav"],
                                    "effects_rung": rec["render"]["effects_rung"]},
                     "output_shas": {"effects_wav": sha["effects_wav"]}})
        rows.append({"salt": salt, "stage": "score_generation",
                     "input_shas": {"bare_wav": sha["bare_wav"],
                                    "effects_wav": sha["effects_wav"]},
                     "output_shas": {"scoring_json": sha["scoring_json"]}})
    out.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")


def _assert_no_collisions(records: List[Dict]) -> None:
    for field in ("musicxml", "midi", "bare_wav", "effects_wav"):
        shas = [r["sha"][field] for r in records]
        if len(set(shas)) != len(shas):
            raise AssertionError(f"SHA collision on {field}: {shas}")


def _assert_non_silent(records: List[Dict]) -> None:
    import soundfile as sf
    import numpy as np
    for rec in records:
        for name in ("bare_midi.wav", "effects_layered.wav"):
            p = _REPO / rec["out_dir"] / name
            y, sr = sf.read(str(p), always_2d=True)
            peak = float(np.abs(y).max())
            if peak <= 1e-4:
                raise AssertionError(f"salt={rec['salt']} {name} silent peak={peak}")


def run_batch(ledger: Path | None = None, batch_root: Path | None = None) -> Dict:
    ledger = Path(ledger) if ledger else (_REPO / "data" / "rules" / "ledger.jsonl")
    batch_root = Path(batch_root) if batch_root else _batch_root()
    batch_root.mkdir(parents=True, exist_ok=True)

    records: List[Dict] = []
    for salt in SALTS:
        print(f"[batch_v1] salt={salt} …")
        rec = _run_one_song(salt, ledger, batch_root)
        records.append(rec)
        print(f"    coerced={list(rec['coerced_rule_ids'].values())}")
        print(f"    xml={rec['sha']['musicxml'][:16]} mid={rec['sha']['midi'][:16]}"
              f" bare={rec['sha']['bare_wav'][:16]} fx={rec['sha']['effects_wav'][:16]}")

    _assert_no_collisions(records)
    _assert_non_silent(records)

    _write_summary_tsv(records, batch_root / "summary.tsv")
    _write_provenance(records, batch_root / "provenance.jsonl", ledger)

    manifest = {
        "milestone": "M-GEN-1/batch-v1",
        "n_songs": len(records),
        "salts": list(SALTS),
        "ledger_sha256": _sha256(ledger),
        "per_song": [{"salt": r["salt"], "sha": r["sha"],
                      "coerced_rule_ids": r["coerced_rule_ids"],
                      "n_coercions": r["n_coercions"]} for r in records],
    }
    (batch_root / "batch_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--batch-root", type=Path, default=_batch_root())
    args = ap.parse_args(argv)
    m = run_batch(args.ledger, args.batch_root)
    print(f"[batch_v1] done. {m['n_songs']} songs; ledger={m['ledger_sha256'][:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
