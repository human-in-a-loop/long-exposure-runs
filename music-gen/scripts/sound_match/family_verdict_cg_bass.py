#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 4
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-family-verdict
# ---
"""Adjudication driver for M-V4-PROFILES-1/cg-bass under the c3-brief
pre-registered three-way decision protocol.

Reads the c3 stage-2b leaderboard, applies the pre-registered decision
protocol, and emits::

    data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json

Also decides whether the c3 top-1 tuple shifts vs c2 (which triggers
emission of ``bass_v2.json`` sibling + a fresh sf2 replay proof under
the c3 stage-2b env pin -- executed by ``run_family_verdict_c4.py``,
not this module).

READ-ONLY imports from c1/c2/c3 modules. No PRNG. No `sidecar_nonfactor`.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

# env pins BEFORE any observed import
_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"family_verdict_cg_bass requires /usr/bin/python3 (got {sys.executable})"
    )


SONG_SHA16 = "31a164f845f8e27e"
STAGE2B_LEADERBOARD = Path(f"data/v4/profiles/{SONG_SHA16}/bass_stage2b/leaderboard.tsv")
STAGE2B_MANIFEST = Path(f"data/v4/profiles/{SONG_SHA16}/bass_stage2b/run_manifest.json")
STAGE1_LEADERBOARD = Path(f"data/v4/profiles/{SONG_SHA16}/bass_sweep_stage1/leaderboard.tsv")
C2_PROFILE = Path(f"data/v4/profiles/{SONG_SHA16}/bass.json")
C2_REPLAY_PROOF = Path(f"data/v4/profiles/{SONG_SHA16}/bass.replay_proof.json")
VERDICT_OUT = Path(f"data/v4/profiles/{SONG_SHA16}/bass_family_verdict.json")

C2_PROFILE_ID = "56cdc50a-dbbc-5a49-afc9-f3cf93a25c7d"
# Frozen c2 top-1 tuple (composite basis): (program, gain, reverb_send, post, sample_rate)
C2_TUPLE = {
    "program": 17,
    "gain": 0.5,
    "reverb_send": 0.3,
    "post": "none",
    "sample_rate": 44100,
}

# Decision protocol thresholds (frozen in c3 brief)
CONFIRMED_EMB_MIN = 0.60
RULED_OUT_EMB_MAX = 0.40
SPREAD_RATIO_MIN = 0.10
CONFIRMED_PROG33_TOP_K = 3
RULED_OUT_PROG33_TOP_K = 5
BASS_FAMILY_PROGRAMS = set(range(32, 40))  # 32..39 inclusive


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


_NUMERIC_FIELDS_ALWAYS = ("composite", "mel_l1_db", "spectral_centroid_rmse_hz",
                          "embedding_cos_vggish")
_NUMERIC_FIELDS_OPTIONAL = ("gain", "reverb_send")


def _read_leaderboard(path: Path) -> list[dict]:
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for k in _NUMERIC_FIELDS_ALWAYS:
                v = float(r[k])
                if v != v or v in (float("inf"), float("-inf")):
                    raise SystemExit(f"non-finite value {v!r} in {path.name} col {k}: {r}")
                r[k] = v
            for k in _NUMERIC_FIELDS_OPTIONAL:
                if k in r:
                    r[k] = float(r[k])
            r["program"] = int(r["program"])
            rows.append(r)
    return rows


def _spread(composites: list[float]) -> float:
    mx = max(composites)
    return (mx - min(composites)) / mx


def compute_metrics(rows: list[dict]) -> dict:
    n_rows = len(rows)
    distinct_shas = len({r["render_sha256"] for r in rows})
    prog33_rows = [r for r in rows if r["program"] == 33]
    prog33_count = len(prog33_rows)
    by_comp = sorted(rows, key=lambda r: r["composite"])
    by_emb = sorted(rows, key=lambda r: -r["embedding_cos_vggish"])

    def rank_of(sr):
        for i, r in enumerate(sr, 1):
            if r["program"] == 33:
                return i
        return None

    prog33_rank_composite = rank_of(by_comp)
    prog33_rank_embedding_cos = rank_of(by_emb)

    stage2b_composites = [r["composite"] for r in rows]
    spread_stage2b = _spread(stage2b_composites)
    c1_rows = _read_leaderboard(STAGE1_LEADERBOARD)
    spread_c1 = _spread([r["composite"] for r in c1_rows])
    spread_ratio = spread_stage2b / spread_c1 if spread_c1 > 0 else 0.0

    return {
        "n_rows_actual": n_rows,
        "n_rows_expected": 216,
        "n_distinct_render_shas": distinct_shas,
        "prog33_count": prog33_count,
        "prog33_rank_composite": prog33_rank_composite,
        "prog33_rank_embedding_cos": prog33_rank_embedding_cos,
        "spread_stage2b": spread_stage2b,
        "spread_c1_coarse": spread_c1,
        "spread_ratio_vs_c1_coarse": spread_ratio,
        "by_composite": by_comp,
        "by_embedding_cos": by_emb,
    }


def _row_summary(r: dict) -> dict:
    return {
        "program": r["program"],
        "preset_name": r["preset_name"],
        "gain": r["gain"],
        "reverb_send": r["reverb_send"],
        "post": r["post"],
        "composite": r["composite"],
        "embedding_cos_vggish": r["embedding_cos_vggish"],
        "mel_l1_db": r["mel_l1_db"],
        "spectral_centroid_rmse_hz": r["spectral_centroid_rmse_hz"],
        "render_sha256": r["render_sha256"],
    }


def _top1_tuple(r: dict) -> dict:
    return {
        "program": r["program"],
        "gain": r["gain"],
        "reverb_send": r["reverb_send"],
        "post": r["post"],
        "sample_rate": 44100,
    }


def decide_verdict(m: dict) -> tuple[str, dict]:
    """Apply pre-registered protocol. Returns (verdict_enum, clauses)."""
    top1_emb = m["by_embedding_cos"][0]["embedding_cos_vggish"]
    top1_by_emb_preset = m["by_embedding_cos"][0]["program"]
    prog33_rank_emb = m["prog33_rank_embedding_cos"]

    stage2b_truncated = m["n_rows_actual"] < m["n_rows_expected"]
    critically_thin = m["n_rows_actual"] < 108  # < half grid

    clauses = {
        "top1_embedding_cos_geq_0_60": top1_emb >= CONFIRMED_EMB_MIN,
        "prog33_in_top3_by_embedding_cos": prog33_rank_emb <= CONFIRMED_PROG33_TOP_K,
        "top1_preset_in_bass_family_32_39": top1_by_emb_preset in BASS_FAMILY_PROGRAMS,
        "spread_ratio_geq_0_10": m["spread_ratio_vs_c1_coarse"] >= SPREAD_RATIO_MIN,
        "top1_embedding_cos_lt_0_40": top1_emb < RULED_OUT_EMB_MAX,
        "prog33_not_in_top5_by_embedding_cos": prog33_rank_emb > RULED_OUT_PROG33_TOP_K,
        "stage2b_truncated": stage2b_truncated,
    }

    if critically_thin:
        return "STILL_INDETERMINATE", clauses

    confirmed = (
        clauses["top1_embedding_cos_geq_0_60"]
        and (
            clauses["prog33_in_top3_by_embedding_cos"]
            or clauses["top1_preset_in_bass_family_32_39"]
        )
        and clauses["spread_ratio_geq_0_10"]
    )
    ruled_out = (
        clauses["top1_embedding_cos_lt_0_40"]
        and clauses["prog33_not_in_top5_by_embedding_cos"]
    )
    if confirmed:
        return "SF2_CONFIRMED", clauses
    if ruled_out:
        return "SF2_RULED_OUT", clauses
    return "STILL_INDETERMINATE", clauses


def build_verdict_dict(
    m: dict,
    verdict: str,
    clauses: dict,
    env_pin_c3: str,
    c2_replay_env_pin: str,
    top1_delta_same_as_c2: bool,
) -> dict:
    return {
        "song_sha16": SONG_SHA16,
        "instrument": "bass",
        "verdict": verdict,
        "verdict_enum_frozen": [
            "SF2_CONFIRMED",
            "SF2_RULED_OUT",
            "STILL_INDETERMINATE",
        ],
        "clauses": clauses,
        "leaderboard_stats": {
            "n_rows_actual": m["n_rows_actual"],
            "n_rows_expected": m["n_rows_expected"],
            "n_distinct_render_shas": m["n_distinct_render_shas"],
            "prog33_count_expected": 36,
            "prog33_count": m["prog33_count"],
            "prog33_rank_composite": m["prog33_rank_composite"],
            "prog33_rank_embedding_cos": m["prog33_rank_embedding_cos"],
            "spread_stage2b_relative": m["spread_stage2b"],
            "spread_c1_coarse_relative": m["spread_c1_coarse"],
            "spread_ratio_vs_c1_coarse": m["spread_ratio_vs_c1_coarse"],
        },
        "top3_by_composite": [_row_summary(r) for r in m["by_composite"][:3]],
        "top3_by_embedding_cos": [_row_summary(r) for r in m["by_embedding_cos"][:3]],
        "top1_profile_delta_vs_c2": {
            "same_as_c2": top1_delta_same_as_c2,
            "c2_profile_id": C2_PROFILE_ID,
            "c2_parameter_tuple": C2_TUPLE,
            "c3_top1_by_composite_tuple": _top1_tuple(m["by_composite"][0]),
            "c3_top1_by_embedding_cos_tuple": _top1_tuple(m["by_embedding_cos"][0]),
            "profile_selection_metric": "composite",
        },
        "env_pin_sha256_c2_v1": c2_replay_env_pin,
        "env_pin_sha256_c3_stage2b_v2": env_pin_c3,
        "env_pin_shifted_c2_to_c3": env_pin_c3 != c2_replay_env_pin,
        "moderate_1_eq_inertness_closed": m["n_distinct_render_shas"] >= 200,
        "moderate_1_eq_inertness_status_detail": (
            "FULL — EQ v2 hypothesis confirmed" if m["n_distinct_render_shas"] >= 200
            else "PARTIAL — EQ v2 reduced collapse but did not eliminate it"
            if m["n_distinct_render_shas"] >= 100
            else "FALSIFIED — EQ v2 hypothesis rejected"
        ),
        "moderate_2_prog33_falsifiable_this_cycle": m["prog33_count"] == 36,
        "downstream_unblock": (
            "cg-drums" if verdict == "SF2_CONFIRMED"
            else "cg-bass-family2-stem-sampled" if verdict == "SF2_RULED_OUT"
            else "cg-bass-family2-stem-sampled_recommended_by_cost"
        ),
        "cycle": 4,
        "run_id": "run-2026-09-03T000000Z",
    }


def _read_env_pin_from_manifest(path: Path) -> str:
    return json.loads(path.read_text())["env_pin_sha256"]


def _read_env_pin_from_replay_proof(path: Path) -> str:
    return json.loads(path.read_text())["env_pin_sha256"]


def main() -> int:
    rows = _read_leaderboard(STAGE2B_LEADERBOARD)
    m = compute_metrics(rows)

    # Halt if program-33 invariant broken
    if m["prog33_count"] != 36:
        raise SystemExit(
            f"FD-1 halt: prog33_count={m['prog33_count']} != 36 "
            "(c3 sweep violated its unconditional-promotion invariant)"
        )

    verdict, clauses = decide_verdict(m)
    env_pin_c3 = _read_env_pin_from_manifest(STAGE2B_MANIFEST)
    c2_replay_env_pin = _read_env_pin_from_replay_proof(C2_REPLAY_PROOF)

    top1_by_comp = m["by_composite"][0]
    same_as_c2 = (
        top1_by_comp["program"] == C2_TUPLE["program"]
        and top1_by_comp["gain"] == C2_TUPLE["gain"]
        and top1_by_comp["reverb_send"] == C2_TUPLE["reverb_send"]
        and top1_by_comp["post"] == C2_TUPLE["post"]
    )

    verdict_dict = build_verdict_dict(
        m, verdict, clauses, env_pin_c3, c2_replay_env_pin, same_as_c2
    )
    VERDICT_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(VERDICT_OUT, "wb") as f:
        f.write(
            (json.dumps(verdict_dict, sort_keys=True, indent=2) + "\n").encode("utf-8")
        )
    print(json.dumps({"verdict": verdict, "path": str(VERDICT_OUT),
                      "verdict_sha256": _sha256_of_file(VERDICT_OUT)}, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
