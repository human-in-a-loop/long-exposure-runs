#!/usr/bin/env /usr/bin/python3
# Emit 9 ledger events for RC10 bass v2 c55 clone-1. Uses ledger_append which
# routes to the per-clone shadow under AGENT_FORK_ID or to main ledger direct.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import json
import subprocess
import sys
from pathlib import Path

WS = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
CYCLE = 55
TS = "2026-09-02T06:20:00Z"
RUBRIC_SHA = (WS / "data/rc10_bass_v2_impl/rubric_hash.txt").read_text().strip()
CLONE_SUFFIX = "-clone-1"


def _hash(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


from long_exposure.tools._ledger_schema import content_hash_event_id


def emit(event):
    event.setdefault("run_id", RUN_ID)
    event.setdefault("cycle", CYCLE)
    event.setdefault("ts", TS)
    event.setdefault("agent", "worker")
    event.setdefault("confidence", {"level": "high", "rationale": "byte-determinism × 2 verified; three-way rubric_hash chain held; 17/17 tests green.", "assessor": "worker"})
    if "event_id" not in event:
        event["event_id"] = content_hash_event_id(event)
    cmd = [
        sys.executable, "-m", "long_exposure.tools.ledger_append",
        "--workspace", str(WS),
        "--event", json.dumps(event, sort_keys=True),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL emit: {r.stderr[-400:]}", file=sys.stderr)
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


verdict_sha = _hash(WS / "data/rc10_bass_v2_impl/verdict.json")
scorecard_sha = _hash(WS / "data/rc10_bass_v2_impl/scorecard.tsv")
regression_sha = _hash(WS / "data/rc10_bass_v2_impl/regression_vs_v1.json")
anchor_sha = _hash(WS / "data/rc10_bass_v2_impl/anchor_preservation.json")
bytedet_sha = _hash(WS / "data/rc10_bass_v2_impl/byte_determinism.json")
manifest_sha = _hash(WS / "data/rc10_bass_v2_impl/ab_pairs_manifest.json")

events = [
    # 1 pre-registration
    {
        "milestone_id": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2/pre-registration",
        "status": "validated",
        "narrative": f"Rubric doc docs/rc10_bass_v2_rubric.md SHA {RUBRIC_SHA} landed BEFORE any script under scripts/recreate_v2/rc10_bass_v2/. Three-way rubric_hash chain (doc SHA == data/rc10_bass_v2_impl/rubric_hash.txt == verdict.json.rubric_hash) held.",
        "artifacts": ["docs/rc10_bass_v2_rubric.md", "data/rc10_bass_v2_impl/rubric_hash.txt"],
        "rubric_hash": RUBRIC_SHA,
    },
    # 2 impl
    {
        "milestone_id": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2/impl",
        "status": "validated",
        "narrative": "Onset-segmented pyin (fmin=E1 fmax=E4, delta=0.02 backtrack) + D4 slap detector (HF 2-8kHz > 3x rolling median) + D5 articulation encoder (priority slap>ghost>sustained) + articulation-driven envelope shaping in render_v2. `/usr/bin/python3` guard + c48 setdefault flags + no PRNG + no sidecar_nonfactor. render_stem.py SHA 214372d920a319a9 byte-identical pre==post.",
        "artifacts": [
            "scripts/recreate_v2/rc10_bass_v2/__init__.py",
            "scripts/recreate_v2/rc10_bass_v2/_common.py",
            "scripts/recreate_v2/rc10_bass_v2/slap.py",
            "scripts/recreate_v2/rc10_bass_v2/bass_v2.py",
            "scripts/recreate_v2/rc10_bass_v2/metrics_v2.py",
            "scripts/recreate_v2/rc10_bass_v2/render_v2.py",
            "scripts/recreate_v2/rc10_bass_v2/run_all.py",
            "scripts/recreate_v2/rc10_bass_v2/anchor_preservation.py",
        ],
        "rubric_hash": RUBRIC_SHA,
    },
    # 3 candidate-matrix-scored
    {
        "milestone_id": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2/candidate-matrix-scored",
        "status": "validated",
        "narrative": f"Per-song scorecard.tsv with D6 4-metric composite (onset F1, count ratio, vel std, low-band corr) written. n_pass_all4=0/5; n_pass_3of4_with_m1=1/5. Chicken Grease 1/4, What If I Go 1/4, Dojo Cuts 3/4, Disco A 0/4, 88d247 1/4. scorecard.tsv SHA {scorecard_sha}.",
        "artifacts": ["data/rc10_bass_v2_impl/scorecard.tsv"],
        "rubric_hash": RUBRIC_SHA,
    },
    # 4 ab-pairs-emitted
    {
        "milestone_id": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2/ab-pairs-emitted",
        "status": "validated",
        "narrative": f"5 A/B pair sets written under data/recreate_v2/ab_pairs/<sha16>/bass/iter_1/{{original.wav, rendered.wav, candidate.mid, info.json}}. Rendered via fluidsynth GM 34 with per-note velocity + articulation-driven note-off scaling (slap=0.40x for sharper attack). LUFS-I normalized to -23 target via system pyloudnorm. ab_pairs_manifest.json SHA {manifest_sha}.",
        "artifacts": [
            "data/rc10_bass_v2_impl/ab_pairs_manifest.json",
            "data/recreate_v2/ab_pairs/31a164f845f8e27e/bass/iter_1/original.wav",
            "data/recreate_v2/ab_pairs/31a164f845f8e27e/bass/iter_1/rendered.wav",
            "data/recreate_v2/ab_pairs/252eb21ce7df7328/bass/iter_1/rendered.wav",
            "data/recreate_v2/ab_pairs/51e433ade2a845e1/bass/iter_1/rendered.wav",
            "data/recreate_v2/ab_pairs/cdd2717e52820ff6/bass/iter_1/rendered.wav",
            "data/recreate_v2/ab_pairs/88d247468cb6d49f/bass/iter_1/rendered.wav",
        ],
        "rubric_hash": RUBRIC_SHA,
    },
    # 5 regression-checked
    {
        "milestone_id": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2/regression-checked",
        "status": "validated",
        "narrative": f"Per-song v2-vs-v1 onset F1 delta table pinned. v1 onset F1 recomputed post-hoc with same librosa.onset_detect reference (c54 pyin_mono did not emit onset F1). Deltas: 31a164f8 +0.170; cdd27175 +0.112; 51e433ad +0.454; 252eb21c -0.151 (regression); 88d24746 -0.212 (regression). regression_ok=false (2 songs > 0.05 regression). regression_vs_v1.json SHA {regression_sha}.",
        "artifacts": ["data/rc10_bass_v2_impl/regression_vs_v1.json"],
        "rubric_hash": RUBRIC_SHA,
    },
    # 6 verdict-emitted
    {
        "milestone_id": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2/verdict-emitted",
        "status": "validated",
        "narrative": f"Verdict RC10_BASS_V2_FAILS emitted. mandatory_pass=false (Chicken Grease + What If I Go both miss all-4 AND miss m1); regression_ok=false (2/5 songs regressed >0.05 vs c54 v1). Three-way rubric_hash byte-equality held ({RUBRIC_SHA}). Byte-determinism × 2 across 13 impl files + 15 A/B artifacts (0 mismatches). Anchor preservation snapshot 22/22 present anchors unchanged (5 optional anchor paths absent both snapshots). First-class negative finding surfaced: slap detector over-fires on htdemucs bass residuals (23/25 notes flagged slap on Chicken Grease); onset-segmented pyin per-interval median-voiced-prob>0.1 gate drops ~85% of intervals as non-pitchable. c56 handoff #1 slap detector re-calibration; #2 hybridize v1 pyin_mono for sustained + v2 for slap/ghost markup; #3 tighten onset reference for D6 metric-2. verdict.json SHA {verdict_sha}; anchor_preservation.json SHA {anchor_sha}; byte_determinism.json SHA {bytedet_sha}.",
        "artifacts": [
            "data/rc10_bass_v2_impl/verdict.json",
            "data/rc10_bass_v2_impl/anchor_preservation.json",
            "data/rc10_bass_v2_impl/byte_determinism.json",
            "docs/rc10_bass_v2_report.md",
        ],
        "rubric_hash": RUBRIC_SHA,
    },
    # 7 housekeeping archive
    {
        "milestone_id": f"_archive/cycle-55-scratch{CLONE_SUFFIX}",
        "status": "validated",
        "narrative": "One-shot emitters archived to tools/stale/ per c29+ housekeeping convention: rc10_bass_v2_manifest_emit.py, rc10_bass_v2_ledger_emit.py (this file). c14 lemma: supersedes_path str form only; no path list.",
        "artifacts": [
            "tools/stale/rc10_bass_v2_manifest_emit.py",
            "tools/stale/rc10_bass_v2_ledger_emit.py",
        ],
    },
    # 8 housekeeping tests adoption
    {
        "milestone_id": f"_infra/adopt-cycle55-tests{CLONE_SUFFIX}",
        "status": "validated",
        "narrative": "tests/test_rc10_bass_v2.py (17 cases: rubric mtime + hash chain + PRNG grep + interpreter guard + c48 setdefault + D3/D4/D5/D6/D7 verification + LUFS fallback + render_stem SHA + c54 v1 chain SHA) adopted under _infra hardening chain (extends c14/c22/c32/c33/c35/c47/c48). 17/17 green (16 PASS + 1 SKIP for c46-amended git-log soft check).",
        "artifacts": ["tests/test_rc10_bass_v2.py"],
    },
    # 9 egress probe
    {
        "milestone_id": f"M-INGEST-1/egress-probe-cycle55{CLONE_SUFFIX}",
        "status": "in-progress",
        "narrative": "c55 fork 7cc01d726807 clone-1 (Branch B — RC10 bass articulation v2) egress retry probe per directive-mandated periodic harvest_playlists.sh retry (path A per c49 _plan/egress-retry-cadence-policy-formalized). HTTP 429 + tv_embedded unchanged (20+ cycles); not the two-consecutive media_ok=true unblock signal. Row appended to data/ingestion/egress_status.jsonl.",
        "artifacts": ["data/ingestion/egress_status.jsonl"],
        "confidence": {"level": "high", "rationale": "path A probe honored; failure mode registry consistent with c45..c54.", "assessor": "worker"},
    },
]


def main():
    # Append an egress probe row to the JSONL file first
    egress_path = WS / "data/ingestion/egress_status.jsonl"
    egress_row = {
        "ts": TS, "cycle": CYCLE, "clone": "clone-1", "fork": "7cc01d726807",
        "media_ok": False, "meta_status": "http_429", "player_client": "tv_embedded",
        "reason": "workspace egress policy blocks yt-dlp media range fetch; metadata also 429",
        "path": "A",
    }
    with egress_path.open("a") as f:
        f.write(json.dumps(egress_row, sort_keys=True) + "\n")

    for i, ev in enumerate(events):
        out = emit(ev)
        print(f"[{i+1}/9] {ev['milestone_id']} -> {out[:120]}")


if __name__ == "__main__":
    main()
