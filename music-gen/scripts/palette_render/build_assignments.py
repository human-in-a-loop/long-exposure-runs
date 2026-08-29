#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T04:33:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render
# ---
"""Build per-stem palette assignments from rules ledger.

Reads three rows from data/rules/ledger.jsonl (harmonic + rhythmic +
arrangement). Choice is deterministic: for each rule_type, the row with
the lexicographically smallest SHA-256(rule_id) hex wins. NO PRNG.

Per-stem dispatch policy:
  drums → fluidsynth_gm (always; c9 anchored path).
  bass  → sfizz if data/texture/test.sfz fetchable; else fluidsynth_gm.
  other → sfizz if data/texture/test.sfz fetchable; else fluidsynth_gm.

Writes:
  data/palette_render/assignments.jsonl (one line per stem).
  data/palette_render/fetchability_ladder.jsonl (append).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette.provenance import compute_assignment_id  # noqa: E402
from scripts.palette.validate import validate_row  # noqa: E402

LEDGER_PATH = _REPO / "data" / "rules" / "ledger.jsonl"
SFZ_PATH = _REPO / "data" / "texture" / "test.sfz"
SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_EXPECTED_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"

STEMS = ("drums", "bass", "other")
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
    """Return {rule_type: rule_id_str} deterministically via SHA-256 tiebreak."""
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
            raise RuntimeError(f"no rules of type {rt} in ledger")
        # SHA-256 tiebreak: winner = lexicographically smallest SHA hex.
        winner = min(by_type[rt], key=lambda rid: _sha256_hex_bytes(rid.encode("ascii")))
        chosen[rt] = winner
    return chosen


def probe_fetchability(ladder_path: Path) -> dict:
    """Probe SF2 + SFZ + sfizz_render + fluidsynth. Append rows to ladder."""
    ladder_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # SF2
    if SF2_PATH.is_file():
        sha = _sha256_file(SF2_PATH)
        row = {"timestamp": now, "resource": str(SF2_PATH), "source": "system",
               "status": "ok" if sha == SF2_EXPECTED_SHA else "corrupt",
               "sha": sha}
        if sha != SF2_EXPECTED_SHA:
            row["error_message"] = f"expected {SF2_EXPECTED_SHA}"
    else:
        row = {"timestamp": now, "resource": str(SF2_PATH), "source": "system",
               "status": "missing", "error_message": "file not found"}
    rows.append(row)

    # SFZ
    if SFZ_PATH.is_file():
        rows.append({"timestamp": now, "resource": str(SFZ_PATH),
                     "source": "workspace", "status": "ok",
                     "sha": _sha256_file(SFZ_PATH)})
    else:
        rows.append({"timestamp": now, "resource": str(SFZ_PATH),
                     "source": "workspace", "status": "missing",
                     "error_message": "SFZ not fetchable → bass/other fall back to fluidsynth_gm"})

    # Binaries
    for binp in ("/usr/bin/fluidsynth", "/usr/bin/sfizz_render"):
        p = Path(binp)
        if p.is_file():
            rows.append({"timestamp": now, "resource": binp, "source": "system",
                         "status": "ok", "sha": _sha256_file(p)})
        else:
            rows.append({"timestamp": now, "resource": binp, "source": "system",
                         "status": "missing", "error_message": "binary not found"})

    with open(ladder_path, "a") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    sf2_ok = any(r["resource"] == str(SF2_PATH) and r["status"] == "ok" for r in rows)
    sfz_ok = any(r["resource"] == str(SFZ_PATH) and r["status"] == "ok" for r in rows)
    fluid_ok = any(r["resource"] == "/usr/bin/fluidsynth" and r["status"] == "ok" for r in rows)
    sfizz_ok = any(r["resource"] == "/usr/bin/sfizz_render" and r["status"] == "ok" for r in rows)
    return {"sf2_ok": sf2_ok, "sfz_ok": sfz_ok, "fluid_ok": fluid_ok, "sfizz_ok": sfizz_ok,
            "sf2_sha": _sha256_file(SF2_PATH) if SF2_PATH.is_file() else None,
            "sfz_sha_bundle": _sfz_bundle_sha() if SFZ_PATH.is_file() else None}


def _sfz_bundle_sha() -> str:
    """SHA-256 of SFZ + all its referenced samples (matches c31 sfizz probe pattern)."""
    if not SFZ_PATH.is_file():
        return "SFZ_MISSING"
    h = hashlib.sha256()
    h.update(SFZ_PATH.read_bytes())
    text = SFZ_PATH.read_text()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("sample="):
            samp = s.split("=", 1)[1].strip()
            sp = SFZ_PATH.parent / samp
            if sp.exists():
                h.update(b"\n---SAMPLE---\n")
                h.update(sp.read_bytes())
    return h.hexdigest()


def _sfizz_version() -> str:
    import subprocess
    try:
        r = subprocess.run(["/usr/bin/sfizz_render", "--version"],
                           capture_output=True, text=True, timeout=5)
        s = (r.stdout or r.stderr).strip().splitlines()
        return s[0] if s else "unknown"
    except Exception:
        return "unknown"


def build_assignment_row(stem: str, provenance_pointers: list[str],
                         fetch: dict) -> dict:
    """Assemble one palette-assignment row conforming to palette_v1.json."""
    if stem == "drums":
        instrument = "fluidsynth_gm"
    else:
        instrument = "sfizz" if fetch["sfz_ok"] and fetch["sfizz_ok"] else "fluidsynth_gm"

    if instrument == "fluidsynth_gm":
        pinned_state = {
            "plugin_name": "fluidsynth_gm",
            "plugin_version": "gm-sf2-2.1",
            "parameter_dict": {
                "gain": 1.0,
                "sample_rate": 44100.0,
            },
            "external_state_sha_optional": fetch["sf2_sha"] or (
                "0" * 64),
        }
    else:
        pinned_state = {
            "plugin_name": "sfizz",
            "plugin_version": _sfizz_version(),
            "parameter_dict": {
                "cli_block_size": 512.0,
                "cli_polyphony": 64.0,
                "cli_quality": 1.0,
                "cli_sample_rate": 44100.0,
            },
            "external_state_sha_optional": fetch["sfz_sha_bundle"] or (
                "0" * 64),
        }

    row = {
        "schema_v": "palette_v1",
        "stem": stem,
        "instrument": instrument,
        "pinned_state": pinned_state,
        "provenance_pointers": sorted(provenance_pointers),
        "extractor_version": "palette_v1_c31",
    }
    row["assignment_id"] = compute_assignment_id(row)
    return row


def build_and_write(out_path: Path, fetch: dict) -> list[dict]:
    """Build all three assignment rows, validate, write JSONL, return list."""
    chosen = pick_rule_ids()
    pointers = sorted(chosen.values())

    rows = []
    for stem in STEMS:
        row = build_assignment_row(stem, pointers, fetch)
        errors = validate_row(row)
        if errors:
            raise RuntimeError(f"validation failed for stem={stem}: {errors}")
        rows.append(row)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return rows


def main() -> int:
    ladder = _REPO / "data" / "palette_render" / "fetchability_ladder.jsonl"
    fetch = probe_fetchability(ladder)
    rows = build_and_write(_REPO / "data" / "palette_render" / "assignments.jsonl", fetch)
    print(json.dumps({"rows_written": len(rows),
                      "instruments": [r["instrument"] for r in rows],
                      "assignment_ids": [r["assignment_id"] for r in rows],
                      "provenance_pointers": rows[0]["provenance_pointers"]},
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
