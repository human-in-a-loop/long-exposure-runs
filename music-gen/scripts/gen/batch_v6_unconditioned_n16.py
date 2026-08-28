#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T23:30:00Z
# cycle: 25
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork dc8cba4b79eb)
# milestone: M-GEN-1/batch-v6-unconditioned-n16
# ---
"""Batch-v6-N16 driver: cycle-13 unconditioned sampler at N=16.

Uses ``scripts.gen.sample_rules.sample_ruleset`` (cycle-10/13 unconditioned
SHA-256-tiebreak sampler, NO rejection loop, NO exclusion set) so N > K per
rule_type is testable — each salt draws independently. Reads the cycle-15
I3-augmented 86-row ledger and drives the coherence gate + assemble +
render + score pipeline verbatim from ``scripts.gen`` (same modules as
batch_v2 / batch_v3_i3 / batch_v4 / batch_v5_n16).

Cycle-15 ``scripts.rules.sampling.i4_stratified`` is intentionally NOT
imported — verified by ``tests/test_batch_v6_unconditioned.py`` and by
``scripts/gen/batch_v6_anchor_check.py``.

Reads (read-only):
    data/rules/ledger_i3_dminor.jsonl   -- I3-augmented 86-row source

Writes:
    data/gen/batch_v6/
        song_<s>/generated.musicxml     for s in 0..15
        song_<s>/generated.mid
        song_<s>/bare_midi.wav
        song_<s>/effects_layered.wav
        song_<s>/scoring.json
        song_<s>/coercions.json
        song_<s>/sampling_manifest.json
        song_<s>/rules.json
        summary.tsv
        provenance.jsonl
        batch_manifest.json
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Env pins BEFORE downstream imports pull numpy/torch.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)

# Cycle-13 unconditioned sampler + frozen pipeline.
from scripts.gen.sample_rules import sample_ruleset  # noqa: E402
from scripts.gen.coherence_gate import enforce_coherence  # noqa: E402
from scripts.gen.assemble_score import assemble_score  # noqa: E402
from scripts.gen.render_pipeline import render  # noqa: E402
from scripts.gen.score_generation import score  # noqa: E402


I3_LEDGER = _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl"
V6_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v6"

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
SALTS = tuple(range(16))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _run_one_song(salt: int, ledger: Path, batch_root: Path) -> Dict:
    out_dir = batch_root / f"song_{salt}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rs_raw = sample_ruleset(ledger, salt=salt)
    rs_coerced, coercions = enforce_coherence(rs_raw)

    xml_path = out_dir / "generated.musicxml"
    assemble_score(rs_coerced, xml_path, duration_s=30.0)

    manifest = render(xml_path, out_dir, duration_s=30.0)

    scoring_json = out_dir / "scoring.json"
    score(Path(manifest.bare_wav_path), Path(manifest.effects_wav_path), scoring_json)

    coercions_json = out_dir / "coercions.json"
    coercions_json.write_text(json.dumps({
        "salt": salt,
        "n_coercions": len(coercions),
        "coercions": coercions,
        "gate_applied_summary": rs_coerced.sampling_manifest.get("coherence_gate", {}),
        "raw_rule_ids": rs_raw.rule_ids(),
        "coerced_rule_ids": rs_coerced.rule_ids(),
    }, indent=2, sort_keys=True))

    sampling_manifest_path = out_dir / "sampling_manifest.json"
    sampling_manifest_path.write_text(json.dumps({
        "salt": salt,
        "chosen_rule_ids": rs_coerced.rule_ids(),
        "raw_rule_ids": rs_raw.rule_ids(),
        "sampling_manifest": rs_coerced.sampling_manifest,
    }, indent=2, sort_keys=True))

    rules_json_path = out_dir / "rules.json"
    rules_json_path.write_text(json.dumps({
        "salt": salt,
        "raw_rule_ids": rs_raw.rule_ids(),
        "coerced_rule_ids": rs_coerced.rule_ids(),
    }, indent=2, sort_keys=True))

    scoring = json.loads(scoring_json.read_text())

    try:
        out_dir_rel = str(out_dir.resolve().relative_to(_REPO))
    except ValueError:
        out_dir_rel = str(out_dir)
    return {
        "salt": salt,
        "out_dir": out_dir_rel,
        "raw_rule_ids": rs_raw.rule_ids(),
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
            "sampling_manifest": _sha256(sampling_manifest_path),
            "rules_json": _sha256(rules_json_path),
        },
        "render": {
            "effects_rung": manifest.effects_rung,
            "sf2_sha256": manifest.sf2_sha256,
        },
        "scoring": scoring,
    }


def _flatten_row(rec: Dict) -> Dict[str, str]:
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
    ledger_sha = _sha256(ledger_path)
    rows = []
    for rec in records:
        salt = rec["salt"]
        sha = rec["sha"]
        rows.append({"salt": salt, "stage": "sample_rules_unconditioned",
                     "input_shas": {"rules_ledger": ledger_sha, "salt": salt},
                     "output_shas": {"chosen_rule_ids": rec["raw_rule_ids"]}})
        rows.append({"salt": salt, "stage": "coherence_gate",
                     "input_shas": {"chosen_rule_ids": rec["raw_rule_ids"]},
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


def run(batch_root: Path = V6_BATCH_ROOT) -> Dict:
    batch_root = Path(batch_root)
    batch_root.mkdir(parents=True, exist_ok=True)

    ledger_sha_pre = _sha256(I3_LEDGER)

    records: List[Dict] = []
    for salt in SALTS:
        print(f"[batch_v6_unconditioned_n16] salt={salt} ...", flush=True)
        rec = _run_one_song(salt, I3_LEDGER, batch_root)
        records.append(rec)
        print(f"    xml={rec['sha']['musicxml'][:16]} mid={rec['sha']['midi'][:16]}"
              f" bare={rec['sha']['bare_wav'][:16]} fx={rec['sha']['effects_wav'][:16]}",
              flush=True)

    _assert_non_silent(records)
    _write_summary_tsv(records, batch_root / "summary.tsv")
    _write_provenance(records, batch_root / "provenance.jsonl", I3_LEDGER)

    ledger_sha_post = _sha256(I3_LEDGER)
    if ledger_sha_pre != ledger_sha_post:
        raise AssertionError("I3 ledger SHA drifted across run")

    manifest = {
        "milestone": "M-GEN-1/batch-v6-unconditioned-n16",
        "sampler": "cycle13_unconditioned_sha256_tiebreak",
        "sampler_module": "scripts.gen.sample_rules",
        "i4_stratified_imported": False,
        "source_ledger": "data/rules/ledger_i3_dminor.jsonl",
        "source_ledger_sha256": ledger_sha_pre,
        "n_songs": len(records),
        "salts": list(SALTS),
        "K_distribution_at_N16": {
            "harmonic": 20,
            "rhythmic": 18,
            "melodic": 18,
            "form": 15,
            "arrangement": 15,
        },
        "K_distribution_note": ("Cycle-12 breadth-expansion actual per-rule_type counts; "
                                 "brief stated (H=20,R=15,M=15,F=15,A=15) but true counts "
                                 "for R/M are 18 each. Only {form, arrangement} are strictly "
                                 "sub-N at K=15 < N=16. Rubric applied as literally frozen."),
        "provenance_chain": {
            "cycle_9_dawdreamer_chain": "scripts/tex/render_effects_layered.py",
            "cycle_13_render_pipeline": "scripts/gen/render_pipeline.py",
            "cycle_13_sampler": "scripts/gen/sample_rules.py",
        },
        "per_song": [{"salt": r["salt"], "sha": r["sha"],
                      "raw_rule_ids": r["raw_rule_ids"],
                      "coerced_rule_ids": r["coerced_rule_ids"],
                      "n_coercions": r["n_coercions"]} for r in records],
    }
    (batch_root / "batch_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path, default=V6_BATCH_ROOT)
    args = ap.parse_args(argv)
    m = run(args.batch_root)
    print(f"[batch_v6_unconditioned_n16] done. {m['n_songs']} songs; "
          f"ledger={m['source_ledger_sha256'][:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
