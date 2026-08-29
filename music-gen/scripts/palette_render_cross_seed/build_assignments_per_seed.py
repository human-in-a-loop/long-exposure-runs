#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:16:00Z
# cycle: 34
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render/cross-seed
# ---
"""Per-seed palette assignment builder.

Reads the c12 `M-RULES-1/extraction/breadth-seeds/<seed>` rule_id subset
from `data/rules/breadth_expansion_summary.json`, then applies the same
SHA-256 tiebreak selection strategy as c33 (`scripts.palette_render.build_assignments`)
but restricted to THIS seed's rows across harmonic + rhythmic + arrangement
types. Delegates row construction to the c33 helper
`scripts.palette_render.build_assignments.build_assignment_row`
(imported READ-ONLY) so palette_v1 schema conformance is inherited verbatim
from c33 Branch A.

Both layers of `scripts.palette.validate` are exercised on every emitted row.

NO PRNG. /usr/bin/python3 guarded. No sidecar_nonfactor import.
c33 palette_render + c33 palette + c33 palette_probe imported READ-ONLY.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# READ-ONLY imports of c33 anchors.
from scripts.palette_render import build_assignments as _c33_build  # noqa: E402
from scripts.palette_render import render_stem as _c33_render_stem  # noqa: E402
from scripts.palette.validate import validate_row  # noqa: E402

RULE_TYPES = ("harmonic", "rhythmic", "arrangement")
STEMS = ("drums", "bass", "other")
LEDGER_PATH = _REPO / "data" / "rules" / "ledger.jsonl"
SUMMARY_PATH = _REPO / "data" / "rules" / "breadth_expansion_summary.json"

# Per-seed transcription MIDI paths (c13 breadth-seed anchors, READ-ONLY).
PER_SEED_MIDI = {
    "seed_mid_50s": {
        "drums": _REPO / "data" / "breadth" / "seed_mid_50s" / "transcriptions" / "drums.mid",
        "bass":  _REPO / "data" / "breadth" / "seed_mid_50s" / "transcriptions" / "bass.mid",
        "other": _REPO / "data" / "breadth" / "seed_mid_50s" / "transcriptions" / "other.mid",
    },
    "synth_060s": {
        "drums": _REPO / "data" / "breadth" / "synth_060s" / "transcriptions" / "drums.mid",
        "bass":  _REPO / "data" / "breadth" / "synth_060s" / "transcriptions" / "bass.mid",
        "other": _REPO / "data" / "breadth" / "synth_060s" / "transcriptions" / "other.mid",
    },
}


def _sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_seed_rule_ids(seed: str) -> set[str]:
    """Return set of rule_id strings owned by this seed per c12 breadth expansion."""
    summary = json.loads(SUMMARY_PATH.read_text())
    ids = summary["per_seed"][seed]["rule_ids"]
    return set(ids)


def pick_seed_rule_ids(seed: str) -> dict[str, str]:
    """SHA-256 tiebreak within this seed's rule_id subset per rule_type.

    Streams `data/rules/ledger.jsonl` read-only, filters to seed's rule_ids,
    then picks the row with the lexicographically-smallest SHA-256(rule_id).

    Raises RuntimeError if any of {harmonic, rhythmic, arrangement} has no
    candidate for this seed (which would flag a data-provenance gap).
    """
    subset = load_seed_rule_ids(seed)
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
            if rt in by_type and isinstance(rid, str) and rid in subset:
                by_type[rt].append(rid)
    chosen: dict[str, str] = {}
    for rt in RULE_TYPES:
        cands = by_type[rt]
        if not cands:
            raise RuntimeError(
                f"seed {seed}: no rules of type {rt} in breadth-seed subset "
                f"({len(subset)} total rule_ids for this seed)"
            )
        winner = min(cands, key=lambda rid: _sha256_hex_bytes(rid.encode("ascii")))
        chosen[rt] = winner
    return chosen


def build_assignments_for_seed(seed: str, out_dir: Path) -> list[dict]:
    """Build 3-row assignments.jsonl for one seed. Returns list of assignment dicts.

    Delegates row construction to the c33 helper
    `_c33_build.build_assignment_row` — that helper handles palette_v1
    schema conformance verbatim (parameter_dict, external_state_sha_optional,
    assignment_id via compute_assignment_id). The per-seed differentiation
    is in the provenance_pointers list (this seed's three chosen rule_ids)
    which flows into the c33 helper's canonical-JSON hash → per-seed
    distinct assignment_id.

    NB: c33's fetchability probe writes to
    data/palette_render/fetchability_ladder.jsonl. To avoid touching the
    c33 anchor directory, we invoke the probe with the per-seed ladder
    path — c33's probe_fetchability accepts an explicit `ladder_path`.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    chosen = pick_seed_rule_ids(seed)
    ladder = out_dir / "fetchability_ladder.jsonl"
    fetch = _c33_build.probe_fetchability(ladder)
    pointers = sorted(chosen.values())

    rows: list[dict] = []
    for stem in STEMS:
        row = _c33_build.build_assignment_row(stem, pointers, fetch)
        errs = validate_row(row)
        if errs:
            raise RuntimeError(f"seed {seed} stem {stem} validate_row failed: {errs}")
        rows.append(row)

    out_path = out_dir / "assignments.jsonl"
    with open(out_path, "w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    return rows


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True, choices=list(PER_SEED_MIDI.keys()))
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    rows = build_assignments_for_seed(a.seed, Path(a.out_dir))
    print(json.dumps({"seed": a.seed, "n_rows": len(rows),
                      "instruments": [r["instrument"] for r in rows],
                      "assignment_ids": [r["assignment_id"] for r in rows]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
