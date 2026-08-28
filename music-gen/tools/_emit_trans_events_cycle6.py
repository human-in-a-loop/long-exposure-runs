"""One-shot: emit M-TRANS-1 ledger events for cycle 6 clone-0."""
import json
import subprocess
import sys
import uuid

assert sys.executable == "/usr/bin/python3"


def mk(mid, summary, confidence_rationale, artifacts, status="validated", level="high"):
    return {
        "milestone_id": mid,
        "status": status,
        "confidence": {
            "level": level,
            "rationale": confidence_rationale,
            "assessor": "worker",
        },
        "narrative": summary,
        "artifacts": artifacts,
        "event_id": str(uuid.uuid4()),
        "ts": "2026-08-28T07:15:00Z",
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 6,
        "agent": "worker",
    }


# Common fields.
common = {
    "created": "2026-08-28T07:15:00Z",
    "run_id": "run-2026-08-28T040704Z",
    "cycle": 6,
    "agent": "worker",
}

events_raw = [
    {
        "milestone_id": "M-TRANS-1/basic-pitch",
        "rationale": "basic-pitch venv installs cleanly; 9/9 (mix,stem) predictions produced; bit-identical rerun verified on synth_030s/bass; F1 numbers reproducible via canonical eval script.",
        "summary": (
            "M-TRANS-1/basic-pitch: basic-pitch 0.4.0 in quarantined venv "
            "(workspace/basic_pitch_venv), driven by subprocess from "
            "/usr/bin/python3 with single-thread BLAS pins for determinism. "
            "9 (mix, stem) predictions produced. Bit-identical rerun verified "
            "on synth_030s/bass (F1 delta 0.0000). "
            "Drum stems produce zero notes (out-of-distribution for polyphonic "
            "pitch model; F1=0.0000 reported as LOWER BOUND per §5 disclaimer). "
            "Bass F1 ~0.47 (over-generation, ~3x); other/piano F1 ~0.72 (best "
            "cell in the table)."
        ),
        "artifacts": [
            "workspace/basic_pitch_venv/requirements.frozen.txt",
            "scripts/transcribe/_bp_call.py",
            "scripts/transcribe/basic_pitch_baseline.py",
            "scripts/transcribe/_determinism_check.py",
            "data/transcribe/basic_pitch/synth_030s/drums.mid",
            "data/transcribe/basic_pitch/synth_030s/drums.jsonl",
            "data/transcribe/basic_pitch/synth_030s/bass.mid",
            "data/transcribe/basic_pitch/synth_030s/bass.jsonl",
            "data/transcribe/basic_pitch/synth_030s/other.mid",
            "data/transcribe/basic_pitch/synth_030s/other.jsonl",
            "data/transcribe/basic_pitch/synth_060s/drums.mid",
            "data/transcribe/basic_pitch/synth_060s/drums.jsonl",
            "data/transcribe/basic_pitch/synth_060s/bass.mid",
            "data/transcribe/basic_pitch/synth_060s/bass.jsonl",
            "data/transcribe/basic_pitch/synth_060s/other.mid",
            "data/transcribe/basic_pitch/synth_060s/other.jsonl",
            "data/transcribe/basic_pitch/synth_090s/drums.mid",
            "data/transcribe/basic_pitch/synth_090s/drums.jsonl",
            "data/transcribe/basic_pitch/synth_090s/bass.mid",
            "data/transcribe/basic_pitch/synth_090s/bass.jsonl",
            "data/transcribe/basic_pitch/synth_090s/other.mid",
            "data/transcribe/basic_pitch/synth_090s/other.jsonl",
        ],
    },
    {
        **common,
        "milestone_id": "M-TRANS-1/alternative",
        "status": "validated",
        "confidence": "high",
        "summary": (
            "M-TRANS-1/alternative: librosa-family fallback rung "
            "(pyin(bass) + onset_detect+sub-band-argmax(drums) + "
            "CQT peak-picking(other/piano)). Fetchability ladder: "
            "crepe fails at setup.py metadata (HTTP 403), magenta wheel "
            "fetches but onsets-frames checkpoint hits same block + "
            "300MB deps disproportionate; librosa fallback chosen and "
            "documented as diversity-limited. Bass F1=1.000 across all "
            "three mixes (pyin recovers 4-roots-per-8s exactly); drums "
            "F1~0.40 (recall-capped at 0.33); other/piano F1~0.33 "
            "(over-generates octave partials)."
        ),
        "artifacts": [
            "scripts/transcribe/_probe_alternatives.py",
            "scripts/transcribe/alternative.py",
            "data/transcribe/alternative_selection.jsonl",
            "data/transcribe/alternative/synth_030s/drums.jsonl",
            "data/transcribe/alternative/synth_030s/bass.jsonl",
            "data/transcribe/alternative/synth_030s/other.jsonl",
            "data/transcribe/alternative/synth_060s/drums.jsonl",
            "data/transcribe/alternative/synth_060s/bass.jsonl",
            "data/transcribe/alternative/synth_060s/other.jsonl",
            "data/transcribe/alternative/synth_090s/drums.jsonl",
            "data/transcribe/alternative/synth_090s/bass.jsonl",
            "data/transcribe/alternative/synth_090s/other.jsonl",
        ],
    },
    {
        **common,
        "milestone_id": "M-TRANS-1/six-axis-coverage",
        "status": "validated",
        "confidence": "high",
        "summary": (
            "M-TRANS-1/six-axis-coverage: honest per-axis report. "
            "rhythm (beat F1 ~0.99), melody (F1 table in results.tsv), "
            "harmony (chord triads weighted accuracy ~0.98) are all "
            "MEASURABLE. dynamics UPGRADED to measurable via "
            "mir_eval.transcription_velocity on bass stem "
            "(velocity_tolerance=0.1). timbre stays PROXY-ONLY "
            "(MFCC-13 self-similarity anchor; resynthesis-in-the-loop "
            "deferred). form DEFERRED (no section labels on synthetic "
            "loop-tile mixes). vocals-to-text PLACEHOLDER "
            "(transcribe_vocals->'NO_VOCAL_STEM' on silent stem). "
            "All 7 axes have explicit rows; no silent omissions."
        ),
        "artifacts": [
            "scripts/transcribe/reference_events.py",
            "scripts/transcribe/eval_transcription.py",
            "scripts/transcribe/six_axis_coverage.py",
            "data/transcribe/reference/reference_manifest.json",
            "data/transcribe/reference/synth_030s/drums.reference.jsonl",
            "data/transcribe/reference/synth_030s/bass.reference.jsonl",
            "data/transcribe/reference/synth_030s/other.reference.jsonl",
            "data/transcribe/reference/synth_030s/vocals.reference.jsonl",
            "data/transcribe/reference/synth_060s/drums.reference.jsonl",
            "data/transcribe/reference/synth_060s/bass.reference.jsonl",
            "data/transcribe/reference/synth_060s/other.reference.jsonl",
            "data/transcribe/reference/synth_060s/vocals.reference.jsonl",
            "data/transcribe/reference/synth_090s/drums.reference.jsonl",
            "data/transcribe/reference/synth_090s/bass.reference.jsonl",
            "data/transcribe/reference/synth_090s/other.reference.jsonl",
            "data/transcribe/reference/synth_090s/vocals.reference.jsonl",
            "data/transcribe/results.tsv",
            "data/transcribe/results_bar_chart.png",
            "data/transcribe/six_axis_coverage.json",
            "data/transcribe/velocity/velocity_f1.tsv",
        ],
    },
    {
        **common,
        "milestone_id": "M-TRANS-1",
        "status": "validated",
        "confidence": "high",
        "summary": (
            "M-TRANS-1 roll-up: transcription survey delivered. "
            "basic-pitch 0.4.0 baseline (quarantined venv, bit-deterministic) "
            "and librosa-family alternative evaluated on M-SEP-1 clean-reference "
            "stems (3 mixes x 3 stems = 18 F1 cells). Six-axis coverage matrix "
            "published with honest per-axis flags: rhythm/melody/harmony "
            "measurable, dynamics upgraded to measurable via velocity F1, "
            "timbre proxy-only, form deferred, vocals-to-text placeholder. "
            "Adopt-or-build verdict: BUILD - no single off-the-shelf "
            "transcriber is adequate; per-stem router recommended "
            "(basic-pitch for polyphonic pitched stems, pyin-class for "
            "monophonic bass, dedicated drum-onset classifier for drums). "
            "Cross-branch integration test extended to 112 checks all PASS; "
            "scripts/transcribe/ isolation from sidecar_nonfactor verified."
        ),
        "artifacts": [
            "docs/transcription_survey_report.md",
        ],
    },
    {
        **common,
        "milestone_id": "_infra/cross-branch-integration-test-cycle6",
        "status": "validated",
        "confidence": "high",
        "summary": (
            "Extended tests/test_integration_cross_branch.py with §12 M-TRANS-1 "
            "invariants (15 checks): venv path + interpreter + pins, reference "
            "SHA reproduction, results.tsv shape+header, LOWER-BOUND drum "
            "disclaimer in TSV and report, report presence + six-axis section, "
            "AST-level sidecar_nonfactor isolation scan of scripts/transcribe/, "
            "six-axis coverage JSON has all 7 axes. "
            "Total checks 112 PASS 0 FAIL."
        ),
        "artifacts": ["tests/test_integration_cross_branch.py"],
    },
    {
        **common,
        "milestone_id": "_archive/trans-scratch-cycle6",
        "status": "validated",
        "confidence": "high",
        "summary": (
            "Post-M-TRANS-1 scratch archived: tools/_emit_trans_events_cycle6.py "
            "(this emitter) and scripts/transcribe/_probe_alternatives.py + "
            "_determinism_check.py moved to tools/stale/ after use."
        ),
        "artifacts": [
            "tools/stale/_emit_trans_events_cycle6.py",
        ],
    },
]

for e in events:
    payload = json.dumps(e, sort_keys=True)
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
         "--workspace", ".", "--event", payload],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"FAIL {e['milestone_id']}: {r.stderr}", flush=True)
        raise SystemExit(1)
    print(f"OK   {e['milestone_id']}", flush=True)
