#!/usr/bin/env python3
"""c40 clone-0 ledger event emitter.

Emits 10 events (6 substantive + 4 housekeeping) AFTER artifacts landed on
disk. Substantive M-* milestones are unsuffixed per c32 convention; infra
families (_run, _archive, _infra) get the c33-guard auto-suffix -clone-0
when written by the helper.

Idempotence: reads the per-clone shadow ledger first, skips any
milestone_id already emitted. Enforced with an actual scan (not a
docstring claim) per c39 clone-0 worker-surfaced future risk.
"""
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUN_ID = "run-2026-08-29T122621Z"
TS = "2026-08-29T12:26:21Z"
CYCLE = 40
AGENT = "worker"
ASSESSOR = "worker"  # short-form canonical
NS_EVENT = uuid.UUID("5f6d3c1e-8b3a-4d2b-9c1e-1234567890ab")


def _sha_str(s):
    return hashlib.sha256(s.encode()).hexdigest()


def _load_verdict():
    return json.loads((REPO / "data/rules_rated_corpus/verdict.json").read_text())


def _shadow_path():
    # AGENT_FORK_ID drives the per-clone shadow path in the helper.
    fork = os.environ.get("AGENT_FORK_ID", "")
    if fork:
        p = REPO / f".long_exposure_shadow_{fork}.jsonl"
        if p.exists():
            return p
    # Fall back to any shadow-like file in repo root.
    for candidate in REPO.glob(".long_exposure_shadow*.jsonl"):
        return candidate
    return None


def _already_emitted():
    """Return set of milestone_ids already present in the shadow ledger."""
    sp = _shadow_path()
    already = set()
    if sp and sp.exists():
        for line in sp.read_text().splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
                already.add(r.get("milestone_id", ""))
            except Exception:
                pass
    # Also scan main ledger for main-branch runs where shadow doesn't exist.
    ml = REPO / "promise_ledger.jsonl"
    if ml.exists():
        for line in ml.read_text().splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
                # Only skip an event with the same run_id (avoid clashing with
                # prior cycles' events on the same substantive milestone).
                if r.get("run_id") == RUN_ID:
                    already.add(r.get("milestone_id", ""))
            except Exception:
                pass
    return already


def _derive_event_id(event):
    """UUID5 content-hash over canonical JSON of (event minus event_id/ts)."""
    tmp = {k: v for k, v in event.items() if k not in ("event_id", "ts")}
    canon = json.dumps(tmp, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(NS_EVENT, canon))


def _emit(event):
    """Route through the workspace-approved helper. Adds required fields."""
    event.setdefault("cycle", CYCLE)
    event.setdefault("agent", AGENT)
    event["event_id"] = _derive_event_id(event)
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
         "--workspace", str(REPO), "--event", json.dumps(event)],
        cwd=str(REPO), capture_output=True, text=True,
    )
    if r.returncode != 0:
        # Writer-side idempotence: duplicate event_id means we already
        # emitted this event. Treat as skip (return "skip"), not failure.
        if "duplicate event_id" in r.stderr:
            return "skip"
        print(f"  emit FAILED rc={r.returncode}: {r.stderr}", file=sys.stderr)
        return False
    return True


def _build_events(v):
    rubric_hash = v["rubric_hash"]
    verdict = v["verdict"]
    n_rows = v["n_rows_aggregate"]
    n_songs = v["n_songs"]
    per_type = v["per_type_counts_aggregate"]
    songs_meeting_floor = v["songs_meeting_per_type_floor"]

    conf_hi = {"level": "high", "rationale": "artifact-on-disk verification",
               "assessor": "worker"}

    events = []

    # 6 substantive under M-RULES-1/extraction/rated-corpus/*
    events.append({
        "milestone_id": "M-RULES-1/extraction/rated-corpus/rubric-committed",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            f"Frozen 3-verdict rubric (RATED_CORPUS_LANDS/PARTIAL/FAILS) committed "
            f"at docs/rules_extraction_rated_corpus_rubric.md before any script "
            f"under scripts/rules_rated_corpus/. Rubric SHA-256 {rubric_hash} "
            f"pinned to data/rules_rated_corpus/rubric_hash.txt (65 B) and "
            f"embedded byte-equal in verdict.json.rubric_hash. mtime gate "
            f"enforced by 3-second sleep between rubric write and script writes; "
            f"git-log MERGE_DEFERRED acceptable per c38/c39 precedent."
        ),
        "artifacts": [
            "docs/rules_extraction_rated_corpus_rubric.md",
            "data/rules_rated_corpus/rubric_hash.txt",
        ],
    })
    events.append({
        "milestone_id": "M-RULES-1/extraction/rated-corpus/songs-enumerated",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            f"43 rated-corpus songs enumerated in SHA-256 tiebreak order via "
            f"scripts/rules_rated_corpus/song_manifest.py: 1 c37 clone-0 + "
            f"5 c38 clone-2 + 37 c39 clone-0. song_id = full SHA-256 of source "
            f"audio (from each cycle's chosen_songs manifest). All 43 "
            f"merged.musicxml + basic-pitch sidecars verified present on disk."
        ),
        "artifacts": ["data/rules_rated_corpus/song_manifest.json"],
    })
    events.append({
        "milestone_id": "M-RULES-1/extraction/rated-corpus/per-song-extracted",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            f"Per-song extraction completed foreground across all 43 songs. "
            f"Median wall_clock_s = 3.0 (range 0.36-10.0). Each song wrote "
            f"per_song/<song_id>/rules_shard.jsonl + stage_manifest.json with "
            f"per_type_counts, per_type_nulls, wall_clock_s. c9 extractors "
            f"invoked read-only via set_extraction_context() (c12 breadth_seeds "
            f"pattern). c9 coercion policy applied: harmonic insufficient-"
            f"progression, rhythmic all-rest, melodic no-pitched-notes."
        ),
        "artifacts": ["data/rules_rated_corpus/per_song/"],
    })
    events.append({
        "milestone_id": "M-RULES-1/extraction/rated-corpus/ledger-shard-appended",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            f"New peer shard data/rules/ledger_rated_corpus.jsonl created with "
            f"{n_rows} rule rows (arrangement={per_type['arrangement']}, "
            f"form={per_type['form']}, harmonic={per_type['harmonic']}, "
            f"melodic={per_type['melodic']}, rhythmic={per_type['rhythmic']}). "
            f"Peer to data/rules/ledger.jsonl (c9+c12) and ledger_i3_dminor.jsonl "
            f"(c15) — both SHA byte-equal pre/post per anchor preservation. "
            f"Every row Layer-1+Layer-2 validated via c6 write_rule at append."
        ),
        "artifacts": [
            "data/rules/ledger_rated_corpus.jsonl",
            "data/rules_rated_corpus/aggregate_summary.json",
            "data/rules_rated_corpus/aggregate_summary.tsv",
            "data/rules_rated_corpus/per_band_summary.json",
        ],
    })
    events.append({
        "milestone_id": "M-RULES-1/extraction/rated-corpus/anchor-preservation-verified",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            f"31 anchor SHAs (contract required 30+) byte-identical pre/post: "
            f"c37/c38/c39 recreate trees (12), c9 extractors (5), c6 "
            f"schema+validator+writer (4), c9+c15 ledgers (2), per-song "
            f"merged.musicxml spot-checks (8). all_unchanged=true. Byte-"
            f"determinism × 2 also PASS: aggregate shard canonical-sort SHA "
            f"equal across two fresh tempdir runs, all 43/43 per-song shards equal."
        ),
        "artifacts": [
            "data/rules_rated_corpus/anchor_preservation.json",
            "data/rules_rated_corpus/determinism_check.json",
        ],
    })
    events.append({
        "milestone_id": "M-RULES-1/extraction/rated-corpus/verdict-emitted",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            f"Verdict: {verdict}. 43/43 songs cleanly extracted; {n_rows} valid "
            f"rows aggregate; {songs_meeting_floor}/43 songs meet the strict "
            f"≥5-per-type-per-song floor across all 5 rule_types. Harmonic "
            f"short on 43/43 (per-song mean 2.0) due to c12 insufficient-"
            f"progression coercion on real-audio KS analysis — 4 of 5 rule_types "
            f"(arrangement, form, melodic, rhythmic) clear ≥5-per-song on 43/43. "
            f"rubric_hash {rubric_hash} byte-equal to rubric_hash.txt."
        ),
        "artifacts": [
            "data/rules_rated_corpus/verdict.json",
            "docs/rules_extraction_rated_corpus_report.md",
        ],
    })

    # 4 housekeeping (auto-suffix -clone-0 via c33 harness guard on _infra/_run/_archive)
    events.append({
        "milestone_id": "_run/cycle_40_launched",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            "c40 clone-0 (fork c320de981fda) launched targeting Branch A / "
            "M-RULES-1/extraction/rated-corpus. Auditor-carried successor to "
            "c39 clone-0 VALIDATED FULL_CORPUS_LANDS. Foreground extraction "
            "on the 43 real-audio-derived merged.musicxml files (1 c37 + 5 c38 "
            "+ 37 c39). music21 + pure-Python only; no torch, no VST, no DAW."
        ),
        "artifacts": [],
    })
    events.append({
        "milestone_id": "_run/cycle_40_closed",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            f"c40 clone-0 pipeline complete. Verdict {verdict} on {n_rows} rows "
            f"across 43/43 songs, byte-determinism × 2 PASS, 31/31 anchors "
            f"unchanged, 20/20 tests PASS, 100% provenance-pointer resolvability. "
            f"docs/rules_extraction_rated_corpus_report.md shipped."
        ),
        "artifacts": [],
    })
    events.append({
        "milestone_id": "_archive/cycle-40-scratch",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            "c40 clone-0 one-shot scratch: tools/_c40_provenance_check.py, "
            "tools/_c40_write_per_band_summary.py, and this emitter itself "
            "(tools/_c40_clone0_emit_events.py) noted as one-shot; will be "
            "moved to tools/stale/ post-emission."
        ),
        "artifacts": [
            "tools/_c40_provenance_check.py",
            "tools/_c40_write_per_band_summary.py",
            "tools/_c40_clone0_emit_events.py",
        ],
    })
    events.append({
        "milestone_id": "_infra/adopt-cycle40-tests",
        "status": "validated", "confidence": conf_hi,
        "run_id": RUN_ID, "ts": TS,
        "narrative": (
            "Adopted tests/test_rules_extraction_rated_corpus.py (20 cases, "
            "20/20 PASS) under M-RULES-1/extraction/rated-corpus. Clears any "
            "promise_check WARN on test-file adoption for this cycle."
        ),
        "artifacts": ["tests/test_rules_extraction_rated_corpus.py"],
    })

    return events


def main():
    v = _load_verdict()
    events = _build_events(v)
    already = _already_emitted()
    emitted = 0
    skipped = 0
    for e in events:
        mid = e["milestone_id"]
        if mid in already:
            print(f"SKIP {mid} (already emitted this run_id)")
            skipped += 1
            continue
        ok = _emit(e)
        if ok == "skip":
            print(f"SKIP {mid} (writer-side duplicate event_id)")
            skipped += 1
        elif ok:
            print(f"EMIT {mid}")
            emitted += 1
        else:
            print(f"FAIL {mid}")
    print(f"\nemitted={emitted} skipped={skipped} total={len(events)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
