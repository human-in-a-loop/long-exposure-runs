#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T23:45:00Z
# cycle: 9
# run_id: run-2026-09-03T233000Z
# agent: worker
# milestone: M-V4-SHOWCASE-1/cg-ab-driver-scaffolded
# ---
"""Deliver CG sound-matched A/B under v4 (SCAFFOLD ONLY at c9).

Reads the accepted per-instrument profiles from
`data/v4/deliveries/<song_sha16>/`; if any profile is missing, emits a
clean-fail smoke-test JSON documenting the missing pieces and returns rc=2.
No render is attempted this cycle — c9 is scaffold + smoke test per the
research brief.

Full render (per-stem replay via sound_match.replay + hybrid vocals from
rc7 + mix-match rc7 module) is queued for the cycle that lands after all
5 CG instrument profiles land.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for k, v in _PINS.items():
    os.environ.setdefault(k, v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(f"deliver_cg_ab_v4 requires /usr/bin/python3 (got {sys.executable})")


REQUIRED_PROFILES = ["bass", "drums", "piano", "guitar", "other"]
# Vocals sourced via hybrid rc7 path per c22 unified-driver pattern.


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="CG A/B delivery driver (scaffold at c9).")
    ap.add_argument("--song", default="31a164f845f8e27e")
    ap.add_argument("--delivery-root", default="data/v4/deliveries")
    ap.add_argument("--out", default=None,
                    help="Directory for A/B output; default <delivery-root>/<song>/")
    ap.add_argument("--smoke-test", action="store_true",
                    help="Do not render; write smoke_test JSON documenting missing profiles.")
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parents[2]
    delivery_dir = root / args.delivery_root / args.song
    out_dir = Path(args.out) if args.out else delivery_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Verify env pins.
    for k, v in _PINS.items():
        if os.environ.get(k) != v:
            raise RuntimeError(f"env pin drift {k}={os.environ.get(k)!r} expected {v!r}")

    present: dict[str, dict] = {}
    missing: list[str] = []

    # Bass: consume the pinned profile manifest (c9 Track 1 artifact).
    pinned = delivery_dir / "cg_bass_pinned_profile.json"
    if pinned.exists():
        m = json.loads(pinned.read_text())
        pp = m.get("pinned_profile") or {}
        present["bass"] = {
            "pinned_manifest": str(pinned),
            "manifest_sha256": _sha(pinned),
            "profile_relpath": pp.get("relative_path"),
            "profile_sha256": pp.get("profile_sha256"),
            "profile_id": pp.get("profile_id"),
            "render_family": pp.get("render_family"),
        }
    else:
        missing.append("bass (no cg_bass_pinned_profile.json)")

    # Drums: consume the c14 OPT3 pinned manifest — htdemucs stem substitution
    # per campaign prompt line 60 + c13-formalized agent-picks invariants.
    drums_pinned = delivery_dir / "cg_drums_pinned_profile.json"
    if drums_pinned.exists():
        dm = json.loads(drums_pinned.read_text())
        if dm.get("acceptance_option") == "OPT3":
            present["drums"] = {
                "pinned_manifest": str(drums_pinned),
                "manifest_sha256": _sha(drums_pinned),
                "render_family": "htdemucs_stem_substitution",
                "source_stem_relpath": dm.get("drums_source_for_showcase"),
                "source_stem_sha256": dm.get("drums_source_sha256"),
                "showcase_dispatch": "read source_stem_relpath verbatim, no synthesis",
            }
        else:
            pp = dm.get("pinned_profile") or {}
            present["drums"] = {
                "pinned_manifest": str(drums_pinned),
                "manifest_sha256": _sha(drums_pinned),
                "profile_relpath": pp.get("relative_path"),
                "profile_sha256": pp.get("profile_sha256"),
                "profile_id": pp.get("profile_id"),
                "render_family": pp.get("render_family"),
            }
    else:
        missing.append("drums (no cg_drums_pinned_profile.json)")

    # Piano/guitar/other: expected under data/v4/profiles/<song>/<instrument>.json.
    profiles_root = root / "data/v4/profiles" / args.song
    for inst in ["piano", "guitar", "other"]:
        p = profiles_root / f"{inst}.json"
        null_finding = profiles_root / f"{inst}_null_finding.json"
        if p.exists():
            present[inst] = {
                "profile_relpath": str(p.relative_to(root)),
                "profile_sha256": _sha(p),
                "render_family": "unknown_pending_manifest",
            }
        elif null_finding.exists():
            nf = json.loads(null_finding.read_text())
            present[inst] = {
                "null_finding_relpath": str(null_finding.relative_to(root)),
                "null_finding_sha256": _sha(null_finding),
                "verdict": nf.get("verdict"),
                "render_family": "null_no_synthesis",
                "showcase_dispatch": "empty MIDI track → silent per-track (v3 spine default)",
            }
        else:
            missing.append(f"{inst} ({p.relative_to(root)} not present, no null_finding sibling)")

    # Vocals: hybrid from rc7 (per c22 unified-driver pattern). c9 scaffold
    # records the expected location; render happens later.
    vocals_hint = "hybrid via scripts/recreate_v2/rc7_v2_rerun.py READ-ONLY import"

    smoke = {
        "kind": "cg_ab_v4_smoke_test",
        "song_sha16": args.song,
        "cycle": 9,
        "run_id": "run-2026-09-03T233000Z",
        "created": "2026-09-03T23:45:00Z",
        "required_instrument_profiles": REQUIRED_PROFILES,
        "present": present,
        "missing": missing,
        "vocals_dispatch": vocals_hint,
        "mix_match_dispatch": "scripts/recreate_v2/rc7_v2_rerun.py READ-ONLY import (planned)",
        "output_target": str((out_dir / "cg_sound_matched_ab.wav").relative_to(root)),
        "renderable_now": len(missing) == 0,
        "env_pin": {k: os.environ.get(k) for k in _PINS},
        "rubric_hash_c9": (root / "data/v4/profiles/31a164f845f8e27e/c9_rubric_hash.txt").read_text().strip(),
    }

    if args.smoke_test or missing:
        out = out_dir / "scaffold_smoke_test.json"
        out.write_text(json.dumps(smoke, sort_keys=True, indent=2) + "\n")
        print(f"SMOKE_TEST_WRITTEN {out} — missing={len(missing)}")
        return 0 if not missing else 2

    # Full render not implemented at c9. Guarded by the operator's proceed
    # rule: rendering happens the cycle where every profile is present.
    raise NotImplementedError(
        "cg-ab full render is queued for the cycle after all 5 CG instrument "
        "profiles land; c9 supports --smoke-test only per operator directive."
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
