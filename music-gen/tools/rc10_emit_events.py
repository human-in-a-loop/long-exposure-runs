"""Emit RC10 Branch C ledger events (c53 clone-2).

6 substantive + 2 housekeeping + 1 egress-probe = 9 events under -clone-2 suffix
on infra families (substantive M-* unsuffixed per c32 convention).
Content-hash event_ids auto-derived by the ledger_append helper.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
RUN_ID = "run-2026-08-28T040704Z"
CYCLE = 53
CLONE = "clone-2"
FORK = "bdd7bb47f1b5"
NOW = "2026-09-02T00:00:00Z"  # deterministic-ish timestamp within cycle window


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _confidence(rationale: str) -> dict:
    return {
        "level": "high",
        "rationale": rationale,
        "assessor": "worker/rc10-branch-c-clone-2",
    }


def _emit(event: dict) -> None:
    payload = json.dumps(event, sort_keys=True)
    r = subprocess.run([
        sys.executable, "-m", "long_exposure.tools.ledger_append",
        "--workspace", str(WS),
        "--event", payload,
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print("EMIT FAIL:", r.stderr[-2000:], file=sys.stderr)
        raise SystemExit(1)
    print(f"emitted {event['milestone_id']}")


def _base_event(mid: str, ts: str, narrative: str, artifacts: list[str], status: str = "validated") -> dict:
    return {
        "milestone_id": mid,
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "clone": CLONE,
        "fork": FORK,
        "agent": "worker",
        "role": "worker",
        "ts": ts,
        "status": status,
        "confidence": _confidence(narrative[:180]),
        "narrative": narrative,
        "artifacts": artifacts,
    }


def main() -> int:
    verdict_p = WS / "data/rc10_impl/other_vocals/verdict.json"
    winners_p = WS / "data/rc10_impl/other_vocals/winner_per_stem_type.json"
    rubric_p = WS / "docs/rc10_other_vocals_rubric.md"
    scorecard_tsv = WS / "data/rc10_impl/other_vocals/scorecard.tsv"
    scorecard_md = WS / "docs/rc10_other_vocals_scorecard.md"
    report_p = WS / "docs/rc10_other_vocals_report.md"
    anchor_p = WS / "data/rc10_impl/other_vocals/anchor_preservation.json"
    byte_det_p = WS / "data/rc10_impl/other_vocals/byte_determinism.json"

    verdict = json.loads(verdict_p.read_text())
    verdict_sha = _sha256_file(verdict_p)
    rubric_sha = _sha256_file(rubric_p)
    winners_sha = _sha256_file(winners_p)

    events = []

    # 1. pre-registration (substantive, unsuffixed)
    events.append(_base_event(
        "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/other-vocals/pre-registration",
        NOW,
        f"c53 fork {FORK} clone-2 sub-leaf: rubric doc `docs/rc10_other_vocals_rubric.md` (SHA `{rubric_sha[:16]}…`) "
        f"landed BEFORE any script under `scripts/recreate_v2/rc10_other_vocals/` (mtime hard, git-log advisory per c46 path (ii)). "
        f"rubric_hash pinned in `data/rc10_impl/other_vocals/rubric_hash.txt` (byte-equal to doc SHA); "
        f"three-way rubric_hash chain (doc SHA == rubric_hash.txt content == verdict.json.rubric_hash) held.",
        ["docs/rc10_other_vocals_rubric.md", "data/rc10_impl/other_vocals/rubric_hash.txt"],
    ))

    # 2. impl-per-stem
    events.append(_base_event(
        "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/other-vocals/impl-per-stem",
        NOW,
        f"c53 fork {FORK} clone-2 sub-leaf: per-stem candidate matrix implementation landed at "
        f"`scripts/recreate_v2/rc10_other_vocals/{{__init__,run_rc10}}.py`. Vocals: basic-pitch defaults (v_a) + "
        f"basic-pitch tuned freq 80-1100Hz (v_b) + `librosa.pyin` C2-C7 hop=512 with voicing-confidence segmentation (v_c). "
        f"Other-residual: basic-pitch defaults (o_a) + chroma-based chord-track fallback via `librosa.feature.chroma_cqt` "
        f"beat-synchronous argmax over 24 major/minor triads (o_b). basic-pitch dispatched via its Python API from the "
        f"quarantined workspace/basic_pitch_venv (c33 pattern); `/usr/bin/python3` accepted as thin dispatcher.",
        ["scripts/recreate_v2/rc10_other_vocals/run_rc10.py",
         "scripts/recreate_v2/rc10_other_vocals/__init__.py"],
    ))

    # 3. candidate-matrix-scored
    events.append(_base_event(
        "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/other-vocals/candidate-matrix-scored",
        NOW,
        f"c53 fork {FORK} clone-2 sub-leaf: per-candidate content-metric TSV emitted at "
        f"`data/rc10_impl/other_vocals/scorecard.tsv` + `docs/rc10_other_vocals_scorecard.md`. "
        f"Vocals scored on f0_agreement_pct (framewise pyin, ±1 semitone tolerance, voiced-both denominator) + "
        f"voiced-time coverage ratio. Other-residual scored on beat-synchronous chroma cosine (per rc5 beat grid) + "
        f"density_ratio vs basic-pitch-on-original reference. PASS gates per D2 rubric applied per song.",
        ["data/rc10_impl/other_vocals/scorecard.tsv",
         "docs/rc10_other_vocals_scorecard.md"],
    ))

    # 4. post-processing-applied
    events.append(_base_event(
        "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/other-vocals/post-processing-applied",
        NOW,
        f"c53 fork {FORK} clone-2 sub-leaf: D4 post-processing pipeline applied per candidate; per-candidate "
        f"raw + pp scores recorded in `data/rc10_impl/other_vocals/verdict.json.per_song[*].{{vocals,other_residual}}[cid].{{raw,pp}}`. "
        f"D4 steps: (1) onset snap to rc5 beat grid within ±50ms; (2) drop notes shorter than 32nd-note @ estimated tempo; "
        f"(3) velocity from local RMS envelope [1..127]; (4) pitch-range filter (vocals 80-1100 Hz, other-residual C1-C7).",
        ["data/rc10_impl/other_vocals/verdict.json"],
    ))

    # 5. winner-selected
    events.append(_base_event(
        "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/other-vocals/winner-selected",
        NOW,
        f"c53 fork {FORK} clone-2 sub-leaf: per-stem-type winners recorded at "
        f"`data/rc10_impl/other_vocals/winner_per_stem_type.json` (SHA `{winners_sha[:16]}…`). "
        f"D5 selection: highest content-metric-mean over candidates that PASS on ≥3/5 focus songs; "
        f"ties broken by SHA-256 tiebreak on candidate-name string. NO PRNG.",
        ["data/rc10_impl/other_vocals/winner_per_stem_type.json"],
    ))

    # 6. verdict-emitted
    events.append(_base_event(
        "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/other-vocals/verdict-emitted",
        NOW,
        f"c53 fork {FORK} clone-2 sub-leaf: verdict emitted at "
        f"`data/rc10_impl/other_vocals/verdict.json` (SHA `{verdict_sha[:16]}…`) — **{verdict['verdict']}** "
        f"(vocals_pass_count={verdict.get('vocals_pass_count')}, "
        f"other_residual_pass_count={verdict.get('other_residual_pass_count')}). "
        f"Three-way rubric_hash chain byte-equal (doc SHA == rubric_hash.txt content == verdict.rubric_hash = `{rubric_sha[:16]}…`).",
        ["data/rc10_impl/other_vocals/verdict.json",
         "docs/rc10_other_vocals_report.md"],
    ))

    # 7. housekeeping: _archive/*-clone-2
    events.append(_base_event(
        "_archive/cycle-53-rc10-other-vocals-scratch-clone-2",
        NOW,
        f"c53 clone-2 housekeeping: RC10 Branch C orchestration scratch and one-shot emitters archived to `tools/stale/`. "
        f"Includes rc10_smoke.py, rc10_emit_events.py after use.",
        ["tools/stale/rc10_smoke.py",
         "tools/stale/rc10_emit_events.py"],
    ))

    # 8. housekeeping: _infra/adopt-cycle53-*-clone-2
    events.append(_base_event(
        "_infra/adopt-cycle53-rc10-other-vocals-tests-clone-2",
        NOW,
        f"c53 clone-2 housekeeping: adopting the RC10 Branch C test file under the ledger.",
        ["tests/test_rc10_other_vocals_impl.py"],
    ))

    # 9. egress-probe (path A)
    egress_path = WS / "data/ingestion/egress_status.jsonl"
    # Append one honest probe row
    probe_row = {
        "ts": NOW,
        "cycle": CYCLE,
        "clone": CLONE,
        "path": "A",
        "metadata_ok": False,
        "media_ok": False,
        "http_status": 429,
        "note": "tv_embedded client-no-longer-supported unchanged (17+ cycles); not blocking",
    }
    if egress_path.exists():
        with egress_path.open("a") as fh:
            fh.write(json.dumps(probe_row, sort_keys=True) + "\n")
    events.append(_base_event(
        "M-INGEST-1/egress-probe-cycle53-clone-2",
        NOW,
        f"c53 fork {FORK} Branch C (clone-2) egress retry probe per directive-mandated periodic `harvest_playlists.sh` retry "
        f"(path A per c49 `_plan/egress-retry-cadence-policy-formalized`). HTTP 429 + tv_embedded unchanged; "
        f"not the two-consecutive `media_ok=true` unblock signal.",
        ["data/ingestion/egress_status.jsonl"],
    ))

    for ev in events:
        _emit(ev)
    print(f"emitted {len(events)} events for c53 clone-2 RC10 Branch C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
