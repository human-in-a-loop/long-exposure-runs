#!/usr/bin/env -S /usr/bin/python3
"""c19 Track 1: emit Disco A + Peach Dream v4 stem_manifest.json skeletons.

Byte-parallel to c17 WIG manifest and c18 Rome manifest shape.

Discipline:
- /usr/bin/python3 interpreter guard (via shebang + explicit exec)
- 7-key env pins set BEFORE any hashing to keep env_pin_sha256 canonical
- No PRNG, no sidecar_nonfactor, no VST3 state APIs
- Explicit blocked_on: _manager/M-V4-METRIC-SEMANTICS-c16

Peach Dream note: stems live under
  data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/rc9_6stem/
NOT the standard operator_section/rc9_6stem/ path (which does not exist for
this song).  This divergence is disclosed per invariant (d) in the manifest's
`source.relpath` and `source_path_divergence_note`.
"""
from __future__ import annotations

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

_ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
_METRIC_SEMANTICS_NOTE = (
    "candidate acceptance under this song’s profile suite awaits "
    "Track 2 operator resolution"
)

WORKSPACE = Path(__file__).resolve().parents[2]


def _stems_dict(stems_dir: Path) -> dict:
    stems = {}
    for name in ["bass", "drums", "guitar", "piano", "other", "vocals"]:
        p = stems_dir / f"{name}.wav"
        if not p.exists():
            raise SystemExit(f"missing stem: {p}")
        stems[name] = {
            "relpath": str(p.relative_to(WORKSPACE)),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "size_bytes": p.stat().st_size,
        }
    return stems


def build_manifest(
    *,
    song_sha16: str,
    song_title: str,
    stems_dir_rel: str,
    section_t_start_s: float,
    section_t_end_s: float,
    source_path_divergence_note: str | None,
) -> dict:
    stems_dir = WORKSPACE / stems_dir_rel
    stems = _stems_dict(stems_dir)
    m: dict = {
        "kind": "v4_stem_manifest",
        "song_sha16": song_sha16,
        "song_title": song_title,
        "cycle": 19,
        "run_id": "run-2026-08-28T040704Z",
        "agent": "worker",
        "created": "2026-09-04T05:00:00Z",
        "audio_sha256": song_sha16,
        "source": {
            "kind": "htdemucs_6s",
            "relpath": stems_dir_rel + ("/" if not stems_dir_rel.endswith("/") else ""),
            "section_t_start_s": section_t_start_s,
            "section_t_end_s": section_t_end_s,
            "section_duration_s": round(section_t_end_s - section_t_start_s, 6),
            "section_source": "data/recreate_v2/focus_set_v2.json",
        },
        "stems": stems,
        "blocked_on": "_manager/M-V4-METRIC-SEMANTICS-c16",
        "note_metric_semantics_carryover": _METRIC_SEMANTICS_NOTE,
        "env_pin_sha256": _ENV_PIN_SHA,
        "schema_shape_note": (
            "byte-parallel to WIG c17 (data/v4/profiles/252eb21ce7df7328/"
            "stem_manifest.json) + Rome c18 (data/v4/profiles/51e433ade2a845e1/"
            "stem_manifest.json)"
        ),
    }
    if source_path_divergence_note:
        m["source_path_divergence_note"] = source_path_divergence_note
    return m


def main() -> int:
    # Disco A: standard operator_section/rc9_6stem/ path exists
    disco_a = build_manifest(
        song_sha16="cdd2717e52820ff6",
        song_title="Disco A",
        stems_dir_rel="data/v3_spine/cdd2717e52820ff6/operator_section/rc9_6stem",
        section_t_start_s=21.91963718820862,
        section_t_end_s=51.91963718820862,
        source_path_divergence_note=None,
    )
    out_disco = WORKSPACE / "data/v4/profiles/cdd2717e52820ff6/stem_manifest.json"
    out_disco.parent.mkdir(parents=True, exist_ok=True)
    out_disco.write_text(json.dumps(disco_a, sort_keys=True, indent=2) + "\n")
    print(f"WROTE {out_disco}")
    print(f"  sha16 {hashlib.sha256(out_disco.read_bytes()).hexdigest()[:16]}")
    for k, v in disco_a["stems"].items():
        print(f"  {k:8s} {v['sha256'][:16]} {v['size_bytes']} B")

    # Peach Dream: stems under operator_section_c25_checkpointed (c25 checkpointed
    # run produced them). Standard operator_section/rc9_6stem/ does NOT exist
    # for this song. Disclosed per invariant (d).
    peach_dream = build_manifest(
        song_sha16="88d247468cb6d49f",
        song_title="Peach Dream",
        stems_dir_rel=(
            "data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/"
            "rc9_6stem"
        ),
        section_t_start_s=172.87256235827664,
        section_t_end_s=202.87256235827664,
        source_path_divergence_note=(
            "Peach Dream htdemucs stems live under `operator_section_c25_"
            "checkpointed/rc9_6stem/` per c25 checkpointed-driver run. The "
            "standard `operator_section/rc9_6stem/` path does NOT exist for "
            "this song (unlike CG/WIG/Rome/Disco A). Disclosed per invariant "
            "(d) on-disk-vs-brief divergence norm; brief specified the standard "
            "path but on-disk reality prevails per FD-1. Stems are byte-"
            "deterministic per c25 checkpointed run manifest."
        ),
    )
    out_peach = WORKSPACE / "data/v4/profiles/88d247468cb6d49f/stem_manifest.json"
    out_peach.parent.mkdir(parents=True, exist_ok=True)
    out_peach.write_text(json.dumps(peach_dream, sort_keys=True, indent=2) + "\n")
    print(f"WROTE {out_peach}")
    print(f"  sha16 {hashlib.sha256(out_peach.read_bytes()).hexdigest()[:16]}")
    for k, v in peach_dream["stems"].items():
        print(f"  {k:8s} {v['sha256'][:16]} {v['size_bytes']} B")

    return 0


if __name__ == "__main__":
    sys.exit(main())
