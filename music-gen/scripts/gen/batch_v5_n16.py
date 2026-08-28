#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T22:00:00Z
# cycle: 23
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 3fbd8c1ab57c)
# milestone: M-GEN-1/batch-v5-n16
# ---
"""Batch-v5-N16 driver: pure salt-range extension of batch-v4 to N=16.

Salt-range extension only: same I3 augmented ledger (source), same I4
stratified sampler (rejection), same cycle-13 batch-v2 render pipeline
(coherence gate + assemble + render + score), same cycle-9 pinned
DawDreamer chain. Only the loop range grows 8 -> 16.

Because ``I4Sampler`` is stateful (per-rule_type ``already_picked`` set
accumulated in salt-order) and deterministic under (ledger, salt,
already_picked), driving it over ``range(16)`` produces the SAME rule
picks at salts 0..7 that batch-v4 produced, plus 8 new picks at salts
8..15. Downstream stages are pure functions of the picks, so all 32
batch-v4 SHAs (4 file kinds x 8 salts) MUST reproduce byte-identically
under salts 0..7. Falsifying that anchor invalidates the extension
assumption.

Reads (read-only):
    data/rules/ledger_i3_dminor.jsonl   -- I3-augmented 86-row source
    data/rules/i3_dminor_manifest.json  -- I3 augmentation manifest

Writes:
    data/gen/batch_v5_n16/
        song_<s>/generated.musicxml     for s in 0..15
        song_<s>/generated.mid
        song_<s>/bare_midi.wav
        song_<s>/effects_layered.wav
        song_<s>/scoring.json
        song_<s>/coercions.json
        song_<s>/sampling_manifest.json
        song_<s>/rules.json             -- per-rule_type sampled rule ids
        summary.tsv
        provenance.jsonl
        batch_manifest.json             -- compound provenance chain
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

# Frozen cycle-13/15 pieces, imported verbatim.
from scripts.rules.sampling.i4_stratified import I4Sampler  # noqa: E402
from scripts.gen.coherence_gate import enforce_coherence  # noqa: E402
from scripts.gen.assemble_score import assemble_score  # noqa: E402
from scripts.gen.render_pipeline import render  # noqa: E402
from scripts.gen.score_generation import score  # noqa: E402


I3_LEDGER = _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl"
I3_MANIFEST = _REPO / "data" / "rules" / "i3_dminor_manifest.json"
V5_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v5_n16"
V4_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v4"
I4_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v3_i4"
I3_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v3_i3"
V2_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v2"
SOURCE_LEDGER = _REPO / "data" / "rules" / "ledger.jsonl"

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
SALTS = tuple(range(16))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _snapshot_dir_shas(root: Path) -> Dict[str, str]:
    """SHA-256 of every regular file under root, keyed by root-relative path."""
    out: Dict[str, str] = {}
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = _sha256(p)
    return out


def _read_ledger_open_mode_assertion() -> None:
    """Content-hash the source and augmented ledgers against the manifest."""
    m = json.loads(I3_MANIFEST.read_text())
    live_i3 = _sha256(I3_LEDGER)
    if live_i3 != m["augmented_ledger_sha256"]:
        raise AssertionError(
            f"I3-augmented ledger content-hash drift: "
            f"live={live_i3} vs manifest={m['augmented_ledger_sha256']}"
        )
    live_src = _sha256(SOURCE_LEDGER)
    if live_src != m["source_ledger_sha256"]:
        raise AssertionError(
            f"Source ledger content-hash drift: "
            f"live={live_src} vs manifest={m['source_ledger_sha256']}"
        )


def _run_one_song(sampler: I4Sampler, salt: int, batch_root: Path) -> Dict:
    out_dir = batch_root / f"song_{salt}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rs_raw = sampler.sample(salt)
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

    # rules.json (per brief §Deliverables).
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
        rows.append({"salt": salt, "stage": "sample_rules_i4",
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


def run(batch_root: Path = V5_BATCH_ROOT) -> Dict:
    batch_root = Path(batch_root)
    batch_root.mkdir(parents=True, exist_ok=True)

    # 1. Read-only preconditions.
    _read_ledger_open_mode_assertion()
    src_pre = _sha256(SOURCE_LEDGER)
    i3_pre = _sha256(I3_LEDGER)

    # 2. Snapshot anchor directories BEFORE.
    pre_shas = {
        "batch_v2":    _snapshot_dir_shas(V2_BATCH_ROOT),
        "batch_v3_i3": _snapshot_dir_shas(I3_BATCH_ROOT),
        "batch_v3_i4": _snapshot_dir_shas(I4_BATCH_ROOT),
        "batch_v4":    _snapshot_dir_shas(V4_BATCH_ROOT),
    }

    # 3. Drive the I4Sampler over 0..15. Same statefulness discipline as
    #    batch_v3_i4/batch_v4_compound; extension is monotonic in salt order.
    sampler = I4Sampler(I3_LEDGER)
    records: List[Dict] = []
    for salt in SALTS:
        print(f"[batch_v5_n16] salt={salt} ...", flush=True)
        rec = _run_one_song(sampler, salt, batch_root)
        records.append(rec)
        print(f"    xml={rec['sha']['musicxml'][:16]} mid={rec['sha']['midi'][:16]}"
              f" bare={rec['sha']['bare_wav'][:16]} fx={rec['sha']['effects_wav'][:16]}",
              flush=True)

    _assert_non_silent(records)
    _write_summary_tsv(records, batch_root / "summary.tsv")
    _write_provenance(records, batch_root / "provenance.jsonl", I3_LEDGER)

    # 4. Anchor-preservation SHAs POST-run.
    post_shas = {
        "batch_v2":    _snapshot_dir_shas(V2_BATCH_ROOT),
        "batch_v3_i3": _snapshot_dir_shas(I3_BATCH_ROOT),
        "batch_v3_i4": _snapshot_dir_shas(I4_BATCH_ROOT),
        "batch_v4":    _snapshot_dir_shas(V4_BATCH_ROOT),
    }
    for name in ("batch_v2", "batch_v3_i3", "batch_v3_i4", "batch_v4"):
        if pre_shas[name] != post_shas[name]:
            raise AssertionError(
                f"anchor-preservation FAILED for {name}: "
                f"pre-run and post-run SHAs differ"
            )
    src_post = _sha256(SOURCE_LEDGER)
    i3_post = _sha256(I3_LEDGER)
    if (src_pre, i3_pre) != (src_post, i3_post):
        raise AssertionError("ledger SHA drift across run")

    # 5. Batch manifest.
    i3_m = json.loads(I3_MANIFEST.read_text())
    manifest = {
        "milestone": "M-GEN-1/batch-v5-n16",
        "sampler": "i4_stratified_rejection_sha256",
        "source_ledger": "data/rules/ledger_i3_dminor.jsonl",
        "source_ledger_sha256": i3_pre,
        "source_row_count": i3_m["augmented_row_count"],
        "harmonic_K": i3_m["harmonic_K_after"],
        "n_songs": len(records),
        "salts": list(SALTS),
        "K_distribution_at_N16": {
            "harmonic": 20,
            "rhythmic": 15,
            "melodic": 15,
            "form": 15,
            "arrangement": 15,
        },
        "provenance_chain": {
            "cycle_9_dawdreamer_chain": "scripts/tex/render_effects_layered.py",
            "cycle_13_render_pipeline": "scripts/gen/render_pipeline.py",
            "cycle_15_i4_sampler": "scripts/rules/sampling/i4_stratified.py",
            "cycle_15_i3_augmentation": "scripts/rules/sampling/i3_dminor.py",
            "i3_augmented_ledger_sha256": i3_m["augmented_ledger_sha256"],
            "i3_source_ledger_sha256": i3_m["source_ledger_sha256"],
        },
        "per_song": [{"salt": r["salt"], "sha": r["sha"],
                      "raw_rule_ids": r["raw_rule_ids"],
                      "coerced_rule_ids": r["coerced_rule_ids"],
                      "n_coercions": r["n_coercions"]} for r in records],
        "final_already_picked": sampler.snapshot(),
        "anchor_preservation": {
            "batch_v2_unchanged": True,
            "batch_v3_i3_unchanged": True,
            "batch_v3_i4_unchanged": True,
            "batch_v4_unchanged": True,
            "source_ledger_sha256_pre": src_pre,
            "source_ledger_sha256_post": src_post,
            "i3_ledger_sha256_pre": i3_pre,
            "i3_ledger_sha256_post": i3_post,
        },
    }
    (batch_root / "batch_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path, default=V5_BATCH_ROOT)
    args = ap.parse_args(argv)
    m = run(args.batch_root)
    print(f"[batch_v5_n16] done. {m['n_songs']} songs; ledger={m['source_ledger_sha256'][:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
