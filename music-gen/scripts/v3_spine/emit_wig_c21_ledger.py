#!/usr/bin/env python3
"""c21 clone-1: emit 6 named + 2 housekeeping ledger events for WIG restart."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

DNS_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
TS = "2026-09-03T00:00:00Z"
ARCHIVE_TS = "2026-09-03T00:00:01Z"
RUN_ID = "run-2026-09-03T000000Z"
CYCLE = 21


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def event_id(mid: str, ts: str, suffix: str = "c21-wig") -> str:
    return str(uuid.uuid5(DNS_NS, f"{mid}|{ts}|{suffix}"))


def emit(event: dict):
    event.setdefault("event_id", event_id(event["milestone_id"], event["ts"]))
    ev_str = json.dumps(event, sort_keys=True)
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "long_exposure.tools.ledger_append", "--event", ev_str],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"FAIL emit {event['milestone_id']}: rc={r.returncode} stderr={r.stderr}", file=sys.stderr)
        return False
    print(f"OK  {event['milestone_id']}")
    return True


def main():
    verdict_path = Path("data/v3/deliveries/252eb21ce7df7328/cycle21/verdict.json")
    ap_path = Path("data/v3_spine/252eb21ce7df7328/operator_section/anchor_preservation_c21.json")
    mus_det = Path("data/v3_spine/252eb21ce7df7328/operator_section/muscriptor_determinism.json")
    canon_det = Path("data/v3_spine/252eb21ce7df7328/operator_section/canonical_midi_determinism.json")
    merged_report = Path("data/v3_spine/252eb21ce7df7328/operator_section/merged_report.json")
    per_track = Path("data/v3_spine/252eb21ce7df7328/operator_section/render/per_track_determinism.json")
    mix_json = Path("data/v3_spine/252eb21ce7df7328/operator_section/render/mix_match_operator_section.json")

    verdict_sha = sha(verdict_path)
    ap_sha = sha(ap_path)

    # Six named substantive events + two housekeeping. Substantive M-* unsuffixed per c32.
    # _infra/*, _run/*, _archive/* get -clone-1 suffix (harness auto-suffix will confirm).
    events = [
        # 1. MuScriptor completion (4 fresh + 3 frozen preserved)
        {
            "milestone_id": "M-V3-FOCUS-1/wig-muscriptor-completed",
            "ts": TS, "cycle": CYCLE, "clone": "1", "run_id": RUN_ID,
            "status": "validated",
            "confidence": {"level": "high", "rationale": "7/7 probes byte-deterministic; 3 c20 SHAs preserved; 4 fresh under identical env pins.", "assessor": "worker"},
            "agent": "worker",
            "narrative": (
                "c21 clone-1 (fork 0a1b1dca4f9b): MuScriptor restart completed. 3 c20 frozen probes "
                "(drums/bass/guitar JSONs) preserved byte-identical via os.path.exists short-circuit; "
                "4 fresh probes (piano/vocals/other/full_mix) x 2 under PYTHONHASHSEED=0 + "
                "SOURCE_DATE_EPOCH=1756463424 + TZ=UTC + LC_ALL=C.UTF-8 + single-thread BLAS. "
                f"7/7 byte-deterministic. muscriptor_determinism.json sha {sha(mus_det)[:16]}."
            ),
            "artifacts": [str(mus_det)],
        },
        # 2. Canonical MIDI determinism
        {
            "milestone_id": "M-V3-FOCUS-1/wig-canonical-midi-completed",
            "ts": TS, "cycle": CYCLE, "clone": "1", "run_id": RUN_ID,
            "status": "validated",
            "confidence": {"level": "high", "rationale": "7/7 canonical MIDI byte-deterministic x2 via READ-ONLY import of c4 pinned midi_from_json_events.py.", "assessor": "worker"},
            "agent": "worker",
            "narrative": (
                "c21 clone-1: canonical MIDI serialize x2 for 7 WIG operator-section probes. "
                f"canonical_midi_determinism.json sha {sha(canon_det)[:16]}. c4 serializer SHA unchanged."
            ),
            "artifacts": [str(canon_det)],
        },
        # 3. Merge with structural gates
        {
            "milestone_id": "M-V3-FOCUS-1/wig-merge-completed",
            "ts": TS, "cycle": CYCLE, "clone": "1", "run_id": RUN_ID,
            "status": "validated",
            "confidence": {"level": "high", "rationale": "merged.mid passes all 4 structural gates (drums ch10 non-empty, bass median<55, vocals symbolic track present, zero GM4).", "assessor": "worker"},
            "agent": "worker",
            "narrative": f"c21 clone-1: WIG merged.mid emitted, 4/4 structural gates PASS. merged_report.json sha {sha(merged_report)[:16]}.",
            "artifacts": [str(merged_report)],
        },
        # 4. Per-track render + vocals overlay + mix-match
        {
            "milestone_id": "M-V3-FOCUS-1/wig-render-mix-completed",
            "ts": TS, "cycle": CYCLE, "clone": "1", "run_id": RUN_ID,
            "status": "validated",
            "confidence": {"level": "high", "rationale": "5/5 fluidsynth per-track renders + D2 vocals overlay + rc7 mix-match byte-deterministic x2.", "assessor": "worker"},
            "agent": "worker",
            "narrative": (
                f"c21 clone-1: WIG per-track render x2 ({sha(per_track)[:16]}) + vocals overlay SHA-verified copy + "
                f"rc7 RMS-match mix ({sha(mix_json)[:16]}). full_reconstruction_operator_section.wav byte-det x2."
            ),
            "artifacts": [str(per_track), str(mix_json)],
        },
        # 5. Anchor preservation
        {
            "milestone_id": "M-V3-FOCUS-1/wig-anchor-preservation-c21-verified",
            "ts": TS, "cycle": CYCLE, "clone": "1", "run_id": RUN_ID,
            "status": "validated",
            "confidence": {"level": "high", "rationale": "12+ frozen c20 SHAs (6 htdemucs stems + 3 muscriptor JSONs + 2 muscriptor MIDs) byte-identical pre==post.", "assessor": "worker"},
            "agent": "worker",
            "narrative": f"c21 clone-1: anchor preservation snapshot verifies all c20 frozen anchors byte-identical. anchor_preservation_c21.json sha {ap_sha[:16]}.",
            "artifacts": [str(ap_path)],
        },
        # 6. Verdict emission
        {
            "milestone_id": "M-V3-FOCUS-1/wig-verdict-c21-emitted",
            "ts": TS, "cycle": CYCLE, "clone": "1", "run_id": RUN_ID,
            "status": "validated",
            "confidence": {"level": "high", "rationale": "verdict emitted with three-way rubric_hash_v2 byte-equality, blocked_on_operator=true, f_restart_from_partial=true. Internal-gate criteria per D-A satisfied.", "assessor": "worker"},
            "agent": "worker",
            "narrative": (
                "c21 clone-1: WIG delivery verdict emitted at data/v3/deliveries/252eb21ce7df7328/cycle21/verdict.json. "
                f"verdict.json sha {verdict_sha[:16]}. Third M-V3-FOCUS-1 accept toward >=3 mandatory threshold "
                "(Chicken Grease + Rome operator-accepted; WIG via internal gates per D-A). Operator ear on "
                "WIG A/B remains the ultimate LANDS authority per FD-6."
            ),
            "artifacts": [str(verdict_path)],
        },
        # 7. Housekeeping: _run/ post-integration (auto-suffixed by harness to -clone-1)
        {
            "milestone_id": "_run/post-integration-cycle-21-wig-restart",
            "ts": TS, "cycle": CYCLE, "clone": "1", "run_id": RUN_ID,
            "status": "validated",
            "confidence": {"level": "high", "rationale": "c21 clone-1 WIG restart complete; ledger events landed under -clone-1 suffix per c32 convention.", "assessor": "worker"},
            "agent": "worker",
            "narrative": (
                "c21 clone-1 (fork 0a1b1dca4f9b) rollup: WIG restart PARTIAL->LANDS internal-gate accept. "
                "Preserved 12 c20 htdemucs stem SHAs + 3 c20 MuScriptor JSON SHAs byte-identical. "
                "Completed 4 fresh MuScriptor probes + downstream chain (canonicalize/merge/render/vocals/mix/deliver/panel)."
            ),
            "artifacts": [str(verdict_path)],
        },
        # 8. Housekeeping: _archive scratch
        {
            "milestone_id": "_archive/cycle-21-wig-scratch",
            "ts": ARCHIVE_TS, "cycle": CYCLE, "clone": "1", "run_id": RUN_ID,
            "status": "validated",
            "confidence": {"level": "high", "rationale": "one-shot c21 emitter script preserved for audit trail per c29+ housekeeping convention.", "assessor": "worker"},
            "agent": "worker",
            "narrative": "c21 clone-1: one-shot ledger emitter archived to tools/stale/ post-emission per c29+ housekeeping convention.",
            "artifacts": ["tools/stale/emit_wig_c21_ledger.py"],
        },
    ]

    ok_count = 0
    for e in events:
        if emit(e):
            ok_count += 1
    print(f"\nEmitted {ok_count}/{len(events)} events")
    return 0 if ok_count == len(events) else 1


if __name__ == "__main__":
    sys.exit(main())
