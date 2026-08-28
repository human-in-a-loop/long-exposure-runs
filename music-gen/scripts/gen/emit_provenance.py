#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:20:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 00b3ae64444c)
# milestone: M-GEN-1/first-generation
# ---
"""Emit data/gen/provenance_v1.jsonl — full stage-by-stage provenance chain.

Each row records (stage, input_shas, output_shas, script_version). The
chain reconstructs from any intermediate stage forward: given the
sampled rule_ids you can find the MusicXML sha; given the MusicXML sha
you find the MIDI sha; and so on to the scoring JSON sha.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def build_provenance(
    *,
    ledger_path: Path,
    sampling_manifest_path: Path,
    xml_path: Path,
    midi_path: Path,
    bare_wav_path: Path,
    effects_wav_path: Path,
    scoring_json_path: Path,
    effects_rung: str,
    sf2_sha256: str,
) -> list[dict]:
    manifest = json.loads(Path(sampling_manifest_path).read_text())
    chosen = manifest["chosen_rule_ids"]
    xml_sha = _sha256(Path(xml_path))
    midi_sha = _sha256(Path(midi_path))
    bare_sha = _sha256(Path(bare_wav_path))
    fx_sha = _sha256(Path(effects_wav_path))
    scoring_sha = _sha256(Path(scoring_json_path))
    ledger_sha = _sha256(Path(ledger_path))
    manifest_sha = _sha256(Path(sampling_manifest_path))

    rows = [
        {
            "stage": "sample_rules",
            "input_shas": {"rules_ledger.jsonl": ledger_sha},
            "output_shas": {"sampling_manifest.json": manifest_sha},
            "chosen_rule_ids": chosen,
            "script": "scripts/gen/sample_rules.py",
            "script_version": "gen-sample-v1",
        },
        {
            "stage": "assemble_score",
            "input_shas": {"sampling_manifest.json": manifest_sha,
                           "rules_ledger.jsonl": ledger_sha},
            "output_shas": {"generated.musicxml": xml_sha},
            "chosen_rule_ids": chosen,
            "script": "scripts/gen/assemble_score.py",
            "script_version": "gen-assemble-v1",
        },
        {
            "stage": "xml_to_midi",
            "input_shas": {"generated.musicxml": xml_sha},
            "output_shas": {"generated.mid": midi_sha},
            "script": "scripts/score/bridge.py::xml_to_midi",
            "script_version": "M-SCORE-1/bridge-api",
        },
        {
            "stage": "render_bare",
            "input_shas": {"generated.mid": midi_sha,
                           "FluidR3_GM.sf2": sf2_sha256},
            "output_shas": {"bare_midi.wav": bare_sha},
            "script": "scripts/tex/render_bare_midi.py",
            "script_version": "M-TEX-1/stage-by-stage cycle-9",
            "sr_hz": 44100,
            "channels": 2,
        },
        {
            "stage": "render_effects",
            "input_shas": {"bare_midi.wav": bare_sha},
            "output_shas": {"effects_layered.wav": fx_sha},
            "script": "scripts/tex/render_effects_layered.py",
            "script_version": "M-TEX-1/stage-by-stage cycle-9",
            "chain_rung": effects_rung,
        },
        {
            "stage": "score_generation",
            "input_shas": {"bare_midi.wav": bare_sha,
                           "effects_layered.wav": fx_sha},
            "output_shas": {"scoring_v1.json": scoring_sha},
            "script": "scripts/gen/score_generation.py",
            "script_version": "gen-score-v1",
        },
    ]
    return rows


def _main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path, default=Path("data/rules/ledger.jsonl"))
    ap.add_argument("--sampling-manifest", type=Path, default=Path("data/gen/sampling_manifest.json"))
    ap.add_argument("--xml", type=Path, default=Path("data/gen/generated.musicxml"))
    ap.add_argument("--midi", type=Path, default=Path("data/gen/renders/generated.mid"))
    ap.add_argument("--bare-wav", type=Path, default=Path("data/gen/renders/bare_midi.wav"))
    ap.add_argument("--fx-wav", type=Path, default=Path("data/gen/renders/effects_layered.wav"))
    ap.add_argument("--scoring", type=Path, default=Path("data/gen/scoring_v1.json"))
    ap.add_argument("--render-manifest", type=Path, default=Path("data/gen/render_manifest.json"))
    ap.add_argument("--out", type=Path, default=Path("data/gen/provenance_v1.jsonl"))
    args = ap.parse_args(argv)

    rm = json.loads(args.render_manifest.read_text())
    rows = build_provenance(
        ledger_path=args.ledger,
        sampling_manifest_path=args.sampling_manifest,
        xml_path=args.xml,
        midi_path=args.midi,
        bare_wav_path=args.bare_wav,
        effects_wav_path=args.fx_wav,
        scoring_json_path=args.scoring,
        effects_rung=rm["effects_rung"],
        sf2_sha256=rm["sf2_sha256"],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"[emit_provenance] wrote {len(rows)} rows -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
