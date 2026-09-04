#!/usr/bin/env python3
# ------------------------------------------------------------------
# c12 Track 1 (MANDATORY): independent replay regression re-verify.
#
# Closes c11 audit MODERATE (replay.py channel-aware fix).  Invokes the
# c11-fixed replay module from a FRESH subprocess under the 7-key env
# pins, twice per anchor into fresh tempdirs, asserting SHA equality
# against the c11 pinned anchors:
#   bass_v2 : 832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5
#   drums   : dadafcfc0153f00269e00e9d5d5fee8fe0b5da2f13cc6dc23a55fe80f2fe64c8
#
# FD-1: if either fails, no tuning/retry — the c11 fix is defective and
# halt is recorded honestly.
#
# Result written to
#   data/v4/profiles/31a164f845f8e27e/_replay_regression_c12.json
#
# created: 2026-09-04
# cycle: 12
# run_id: run-2026-09-04T000000Z
# agent: worker
# milestone: _infra/replay-channel-aware-independent-reverify-c12
# ------------------------------------------------------------------

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

# 7-key env-pin canonical (replay-time).  MUST match c11.
_ENV_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}

# c11 pinned anchors that must reproduce byte-identically.
_BASS_V2_ANCHOR = (
    "832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5"
)
_DRUMS_ANCHOR = (
    "dadafcfc0153f00269e00e9d5d5fee8fe0b5da2f13cc6dc23a55fe80f2fe64c8"
)

_WORKSPACE = Path(__file__).resolve().parents[2]
_PROFILE_DIR = _WORKSPACE / "data" / "v4" / "profiles" / "31a164f845f8e27e"
_OUT_JSON = _PROFILE_DIR / "_replay_regression_c12.json"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _canon_env_pin_sha256() -> str:
    canonical = json.dumps(_ENV_PINS, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _apply_env_pins() -> None:
    for k, v in _ENV_PINS.items():
        os.environ[k] = v


def _load_profile(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _replay_once(profile_path: Path, midi_path: Path,
                 out_wav: Path) -> None:
    """Invoke the c11 replay module to render (profile, midi) -> wav."""
    sys.path.insert(0, str(_WORKSPACE))
    # Import lazily so the pins in os.environ have effect at replay time.
    from scripts.sound_match import replay as replay_mod  # type: ignore

    profile = _load_profile(profile_path)
    # replay.replay(profile_dict, midi_path, out_wav_path)
    replay_mod.replay(profile, str(midi_path), str(out_wav))


def _verify_anchor(profile_path: Path, midi_path: Path,
                   anchor_sha: str, label: str) -> dict:
    if not profile_path.exists():
        return {
            "label": label,
            "status": "MISSING_PROFILE",
            "profile_path": str(profile_path),
        }
    if not midi_path.exists():
        return {
            "label": label,
            "status": "MISSING_MIDI",
            "midi_path": str(midi_path),
        }
    shas: list[str] = []
    for i in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f"c12_{label}_run{i}_") as td:
            out_wav = Path(td) / "out.wav"
            _replay_once(profile_path, midi_path, out_wav)
            shas.append(_sha256_file(out_wav))
    match_anchor = shas[0] == anchor_sha
    match_between = shas[0] == shas[1]
    return {
        "label": label,
        "status": ("REGRESSION_HOLDS" if (match_anchor and match_between)
                   else "REGRESSION_FAILS"),
        "run1_sha256": shas[0],
        "run2_sha256": shas[1],
        "anchor_sha256": anchor_sha,
        "match_anchor": match_anchor,
        "match_between_runs": match_between,
        "profile_path": str(profile_path.relative_to(_WORKSPACE)),
        "midi_path": str(midi_path.relative_to(_WORKSPACE)),
    }


def main() -> int:
    _apply_env_pins()
    env_pin_sha = _canon_env_pin_sha256()

    bass_v2_profile = _PROFILE_DIR / "bass_v2.json"
    drums_profile = _PROFILE_DIR / "drums.json"

    # MIDI paths: pull from the c11 replay proofs.
    def _midi_from_proof(pjson: Path) -> Path:
        with open(pjson) as f:
            proof = json.load(f)
        mp = proof.get("midi_path")
        if mp is None:
            raise SystemExit(f"midi_path missing in {pjson}")
        return _WORKSPACE / mp if not Path(mp).is_absolute() else Path(mp)

    bass_midi = _midi_from_proof(
        _PROFILE_DIR / "bass_v2.replay_proof.json")
    drums_midi = _midi_from_proof(
        _PROFILE_DIR / "drums.replay_proof.json")

    results = [
        _verify_anchor(bass_v2_profile, bass_midi,
                       _BASS_V2_ANCHOR, "bass_v2"),
        _verify_anchor(drums_profile, drums_midi,
                       _DRUMS_ANCHOR, "drums"),
    ]

    # Verdict aggregation: both must REGRESSION_HOLDS.
    all_hold = all(r.get("status") == "REGRESSION_HOLDS" for r in results)
    verdict = ("REPLAY_REGRESSION_HOLDS" if all_hold
               else "REPLAY_REGRESSION_FAILS")

    doc = {
        "schema_version": "v1.0",
        "milestone_id": (
            "_infra/replay-channel-aware-independent-reverify-c12"),
        "cycle": 12,
        "purpose": (
            "Closes c11 audit MODERATE (replay.py channel-aware fix). "
            "Independent from-fresh-subprocess re-verify of bass_v2 and "
            "drums replay anchors, twice per anchor into fresh tempdirs."
        ),
        "env_pins": dict(_ENV_PINS),
        "env_pin_sha256": env_pin_sha,
        "results": results,
        "verdict": verdict,
    }

    _OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(_OUT_JSON, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"WROTE {_OUT_JSON}")
    print(f"verdict: {verdict}")
    for r in results:
        print(f"  {r.get('label')}: {r.get('status')}")

    return 0 if all_hold else 1


if __name__ == "__main__":
    sys.exit(main())
