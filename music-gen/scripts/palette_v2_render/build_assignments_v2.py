#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:05:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-schema-v2-hydration-render
# ---
"""Build three per-stem palette_v2 assignment rows.

Per-stem dispatch (frozen; no PRNG):
  drums -> fluidsynth_gm      pinned_state.format = v1_flat
  bass  -> surge_xt (VST3)    pinned_state.format = v2_iterated_params
  other -> dexed   (VST3)     pinned_state.format = v2_iterated_params

Rule provenance: SHA-256 tiebreak over rule_id across harmonic/rhythmic/
arrangement rule_types on data/rules/ledger.jsonl (same as c33). No PRNG.

Every row validated through both layers of scripts.palette_v2.validate.
Any validation failure raises -> caller emits RENDER_FAILS.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette_v2.provenance import (  # noqa: E402
    compute_assignment_id_v2,
    sha256_iterated_params,
    anchor_iterated_params,
)
from scripts.palette_v2.validate import validate_row  # noqa: E402

LEDGER_PATH = _REPO / "data" / "rules" / "ledger.jsonl"
SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_EXPECTED_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"

VST3_PATHS = {
    "surge_xt": "/usr/lib/vst3/Surge XT.vst3",
    "dexed":    "/usr/lib/vst3/Dexed.vst3",
}

ANCHOR_DIR = _REPO / "data" / "dawdreamer_state" / "per_plugin"

# Per-stem instrument assignment (frozen).
STEM_INSTRUMENT = {
    "drums": "fluidsynth_gm",
    "bass":  "surge_xt",
    "other": "dexed",
}

RULE_TYPES = ("harmonic", "rhythmic", "arrangement")


def _sha256_hex_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def pick_rule_ids() -> dict:
    """Deterministic {rule_type: rule_id} via SHA-256 tiebreak."""
    by_type: dict[str, list[str]] = {rt: [] for rt in RULE_TYPES}
    with open(LEDGER_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            rt = row.get("rule_type")
            rid = row.get("rule_id")
            if rt in by_type and isinstance(rid, str) and rid.startswith("rule_"):
                by_type[rt].append(rid)
    chosen: dict[str, str] = {}
    for rt in RULE_TYPES:
        if not by_type[rt]:
            raise RuntimeError(f"no rules of type {rt}")
        winner = min(by_type[rt], key=lambda rid: _sha256_hex_bytes(rid.encode("ascii")))
        chosen[rt] = winner
    return chosen


def probe_fetchability(ladder_path: Path) -> dict:
    """Probe SF2 + VST3 plugins + DawDreamer import + fluidsynth binary."""
    ladder_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # SF2
    if SF2_PATH.is_file():
        sha = _sha256_file(SF2_PATH)
        rows.append({"timestamp": now, "resource": str(SF2_PATH), "source": "system",
                     "status": "ok" if sha == SF2_EXPECTED_SHA else "corrupt", "sha": sha})
    else:
        rows.append({"timestamp": now, "resource": str(SF2_PATH), "source": "system",
                     "status": "missing", "error_message": "file not found"})

    # VST3 plugins
    for key, path in VST3_PATHS.items():
        p = Path(path)
        if p.exists():
            rows.append({"timestamp": now, "resource": path, "source": "system",
                         "status": "ok"})
        else:
            rows.append({"timestamp": now, "resource": path, "source": "system",
                         "status": "missing",
                         "error_message": f"VST3 not found: {key}"})

    # DawDreamer
    try:
        import dawdreamer  # noqa: F401
        rows.append({"timestamp": now, "resource": "python:dawdreamer",
                     "source": "system", "status": "ok",
                     "version": getattr(dawdreamer, "__version__", "0.9.0")})
    except Exception as e:
        rows.append({"timestamp": now, "resource": "python:dawdreamer",
                     "source": "system", "status": "import_failed",
                     "error_message": f"{type(e).__name__}: {e}"})

    # fluidsynth binary
    p = Path("/usr/bin/fluidsynth")
    if p.is_file():
        rows.append({"timestamp": now, "resource": "/usr/bin/fluidsynth",
                     "source": "system", "status": "ok",
                     "sha": _sha256_file(p)})
    else:
        rows.append({"timestamp": now, "resource": "/usr/bin/fluidsynth",
                     "source": "system", "status": "missing"})

    with open(ladder_path, "a") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    def _ok(res):
        return any(r["resource"] == res and r["status"] == "ok" for r in rows)
    return {"sf2_ok": _ok(str(SF2_PATH)),
            "surge_xt_ok": _ok(VST3_PATHS["surge_xt"]),
            "dexed_ok": _ok(VST3_PATHS["dexed"]),
            "dawdreamer_ok": _ok("python:dawdreamer"),
            "fluidsynth_ok": _ok("/usr/bin/fluidsynth"),
            "sf2_sha": _sha256_file(SF2_PATH) if SF2_PATH.is_file() else None}


def _load_p1_anchor(plugin_name: str) -> dict:
    """Load the c33 P1 anchor dict for a VST3 plugin. READ-ONLY."""
    p = ANCHOR_DIR / plugin_name / "p1_state_v2.json"
    return json.loads(p.read_text())


def _dexed_or_surge_pinned_state(plugin_name: str) -> dict:
    """Build a v2_iterated_params pinned_state from the c33 P1 anchor."""
    iterated = _load_p1_anchor(plugin_name)
    # Anchor key set + plugin_version from provenance module
    _keys, plugin_version = anchor_iterated_params(plugin_name)
    return {
        "format": "v2_iterated_params",
        "plugin_name": plugin_name,
        "plugin_version": plugin_version,
        "iterated_params": iterated,
        "iteration_size": len(iterated),
        "iteration_sha_256": sha256_iterated_params(iterated),
    }


def _drums_pinned_state(sf2_sha: str | None) -> dict:
    """Build a v1_flat pinned_state for drums (fluidsynth_gm)."""
    return {
        "format": "v1_flat",
        "plugin_name": "fluidsynth_gm",
        "plugin_version": "gm-sf2-2.1",
        "parameter_dict": {
            "gain": 1.0,
            "sample_rate": 44100.0,
        },
        "external_state_sha_optional": sf2_sha or ("0" * 64),
    }


def build_assignment_row_v2(stem: str, provenance_pointers: list[str],
                            fetch: dict) -> dict:
    instrument = STEM_INSTRUMENT[stem]
    if instrument == "fluidsynth_gm":
        pinned_state = _drums_pinned_state(fetch.get("sf2_sha"))
    else:
        pinned_state = _dexed_or_surge_pinned_state(instrument)

    row = {
        "schema_v": "palette_v2",
        "stem": stem,
        "instrument": instrument,
        "pinned_state": pinned_state,
        "provenance_pointers": sorted(provenance_pointers),
        # Schema pins extractor_version to the palette_v2_c34 constant
        # (peer schema version, not the cycle we're consuming it in).
        "extractor_version": "palette_v2_c34",
    }
    row["assignment_id_v2"] = compute_assignment_id_v2(row)
    return row


def build_and_write(out_path: Path, fetch: dict) -> list[dict]:
    chosen = pick_rule_ids()
    pointers = sorted(chosen.values())

    rows = []
    for stem in ("drums", "bass", "other"):
        row = build_assignment_row_v2(stem, pointers, fetch)
        errors = validate_row(row)
        if errors:
            raise RuntimeError(
                f"palette_v2 validation failed for stem={stem}: {errors[:5]}")
        rows.append(row)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return rows


def main() -> int:
    out = _REPO / "data" / "palette_v2_render"
    ladder = out / "fetchability_ladder.jsonl"
    fetch = probe_fetchability(ladder)
    rows = build_and_write(out / "assignments_v2.jsonl", fetch)
    summary = {
        "rows_written": len(rows),
        "instruments": [r["instrument"] for r in rows],
        "assignment_ids_v2": [r["assignment_id_v2"] for r in rows],
        "provenance_pointers": rows[0]["provenance_pointers"],
        "fetch": fetch,
    }
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
