"""One-shot ledger emitter for M-SCORE-1 sub-milestones (cycle 8 clone 0).

Emits four events:
  M-SCORE-1/round-trip
  M-SCORE-1/merged-full-song
  M-SCORE-1/bridge-api
  M-SCORE-1 (parent roll-up)

The append_ledger_event helper does NOT auto-add event_id (lesson from
cycle-7 integrator, 4 rows lost); every event dict must include it.
"""
import uuid
from datetime import datetime, timezone
from pathlib import Path

from long_exposure.tools.ledger_append import append_ledger_event


WS = Path("/home/user/long-exposure-runs/music-gen")
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
RUN_ID = "run-2026-08-28T040704Z"


def _base(mid, status, conf, summary, artifacts):
    return {
        "event_id": uuid.uuid4().hex,
        "timestamp": NOW,
        "cycle": 8,
        "run_id": RUN_ID,
        "agent": "worker",
        "milestone_id": mid,
        "status": status,
        "confidence": conf,
        "summary": summary,
        "artifacts": [str(a) for a in artifacts],
    }


ROUND_TRIP = _base(
    "M-SCORE-1/round-trip",
    "validated", "high",
    "8-bar seed round-trip: 88/88 notes preserved on xml_to_midi (pitch "
    "multi-set exact, onset drift 0.00 ms, duration drift ≤ 1 tick at "
    "PPQ=480 ≈ 2 ms). Two full round trips (xml→mid→xml→mid) produce "
    "byte-identical MIDI (sha e2493fc7f7e3a4df) and byte-identical scrubbed "
    "MusicXML (sha 71d0e1eaf1d798ad). Determinism scrub covers mscore3 "
    "3.2.3 injected fields (<encoding-date>, <software>, <source>, "
    "<supports>, <encoder>, <creator MuseScore>, title-echoes) plus "
    "music21-generated 32-hex-digit part/instrument IDs (P/I/S normalized "
    "in first-occurrence order). Test suite §1a, §1b, §2a, §2b, §2c "
    "(5/5 PASS). See docs/score_bridge_report.md §1.",
    [
        "scripts/score/seed_score.py",
        "scripts/score/bridge.py",
        "tests/test_score_bridge.py",
        "data/score/seed_8bar.musicxml",
    ],
)

MERGED = _base(
    "M-SCORE-1/merged-full-song",
    "validated", "high",
    "Merged 30-s M-SEP-1 synth-mix score assembled from cycle-6 basic-pitch "
    "outputs (drums/bass/other JSONL sha 01ba4719.../c7165998.../90ea9a10... "
    "first 16 hex). Identity-merge fidelity (bridge preservation metric): "
    "F1 = 1.0000 on ALL 3 stems vs basic-pitch input MIDIs "
    "(drums 0/0, bass 44/44, other 78/78 notes). F1 vs M-SEP-1 tiled GT: "
    "drums 0.0000 (BP outputs 0 notes; upstream-bounded), bass 0.4746 "
    "(matches cycle-6 baseline exactly; upstream octave-doubling — sibling "
    "clone 1 targets +0.3 uplift), other 0.7317 (recall = 1.0; slight "
    "improvement over cycle-6's 0.72). The bridge does not degrade "
    "basic-pitch's quality; every gap vs GT inherits from cycle-6 "
    "transcription upstream noise. Merge invariant: per-stem note counts "
    "PRESERVED exactly across the merge (test §3c). Determinism: two full "
    "runs produce byte-identical merged XML and MIDI (test §4a, §4b). "
    "Multi-voice cap workaround (mscore3 3.2.3 collapses >1 voice/part on "
    "MIDI export) via interval-graph coloring: one part per voice "
    "partition, named {stem}__v{k}; parts_mapping.json sidecar maps "
    "tracks back to stems. Test suite §3a, §3b (3 stems), §3c (3 stems), "
    "§4a, §4b (9/9 PASS). See docs/score_bridge_report.md §2, §3.",
    [
        "scripts/score/jsonl_to_midi.py",
        "scripts/score/bridge.py",
        "data/score/stems_from_bp/bass.mid",
        "data/score/stems_from_bp/drums.mid",
        "data/score/stems_from_bp/other.mid",
        "data/score/merged_synth030s.musicxml",
        "data/score/merged_synth030s.mid",
        "data/score/merged_synth030s.parts_mapping.json",
    ],
)

BRIDGE_API = _base(
    "M-SCORE-1/bridge-api",
    "validated", "high",
    "Public API: xml_to_midi, midi_to_xml, merge_stems_to_score, "
    "ScoreBridgeError (typed). Interpreter-guarded /usr/bin/python3. "
    "Non-factor isolation: zero imports of scripts.classifier."
    "sidecar_nonfactor across scripts/score/*.py + tests/test_score_bridge.py "
    "(test §6a). Failure-mode surfacing: malformed XML (silent-rc-0 trap "
    "on stderr 'is not a valid musicxml file'), missing input, timeout, "
    "missing stem MIDI — every path raises ScoreBridgeError with a "
    "non-empty diagnostic (test §5a-d). mscore3 3.2.3 subprocess "
    "machinery, temp-file management, determinism scrubbing, and "
    "music21 authoring all hidden behind the four-symbol API. "
    "Cross-branch integration test §15 added (10 M-SCORE-1 checks). "
    "Test suite: 23/23 PASS. Report: docs/score_bridge_report.md — "
    "all 7 required sections (round-trip proof, F1 tables, API "
    "reference, failure modes, environment/reproducibility, isolation, "
    "determinism-scrub list).",
    [
        "scripts/score/__init__.py",
        "scripts/score/bridge.py",
        "scripts/score/jsonl_to_midi.py",
        "scripts/score/seed_score.py",
        "tests/test_score_bridge.py",
        "tests/test_integration_cross_branch.py",
        "docs/score_bridge_report.md",
    ],
)

PARENT = _base(
    "M-SCORE-1",
    "validated", "high",
    "Parent roll-up: MuseScore programmatic bridge delivered. Three "
    "sub-milestones VALIDATED: round-trip (byte-identical seed round trip "
    "after scrub; 88/88 notes preserved), merged-full-song (identity-merge "
    "F1 = 1.0000 on all 3 stems vs BP input; F1 vs GT bounded by cycle-6 "
    "upstream, diagnosis in report §3), bridge-api (stable 4-symbol "
    "surface, typed errors, interpreter guard, isolation, 23/23 tests). "
    "UNBLOCKS M-RULES-1 extraction-half (needs a merged full-song score) "
    "and M-TEX-1 parent stage-by-stage (needs bare-MIDI rendering as "
    "start of the texture ladder). Cross-branch integration test "
    "extended to 212 checks (0 failures). Environment: mscore3 3.2.3 "
    "headless (QT_QPA_PLATFORM=offscreen); Python 3.11.15 / numpy 1.26.4 "
    "/ music21 9.1.0 (adopted this cycle; classifier + integration tests "
    "remain green) / mir_eval 0.8.2. Non-factor isolation contract "
    "green. Ready for cycle-9 post-merge integration.",
    [
        "docs/score_bridge_report.md",
    ],
)

for event in (ROUND_TRIP, MERGED, BRIDGE_API, PARENT):
    append_ledger_event(WS, event)
    print(f"appended: {event['milestone_id']} ({event['status']}/{event['confidence']})")
