#!/usr/bin/python3
"""c84 P0.2 — pre-registered content gate for the v5 corpus (NON-MUSIC items).

created: 2026-09-09T20:50:00Z
cycle: 84
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/content-gate-c84

Reads data/v5/corpus/content_gate_prereg_c84.json (must pre-date every output — mtime gate asserted here),
applies the two pre-registered rules to the 26 corpus_manifest.json songs:
  R1 (content):  n_note_on(full_mix) == 0 AND sum(n_note_on over drums,bass,guitar,other,piano) == 0
                 from the landed transcription_manifest.json note_counts.
  R2 (title):    re.search(r"commentary|interview|q&a|talk|podcast|lecture|spoken", title, re.I).
BLOCKED := R1 fires. R2 is corroboration (R2_ONLY on a landed song with notes is NOT blocked; R2 on an unlanded song
is R2_PENDING_TRANSCRIPTION). Writes data/v5/corpus/content_blocked.json (separate from the tempo-blocked file).
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; READ-ONLY inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TITLE_RE = re.compile(r"commentary|interview|q&a|talk|podcast|lecture|spoken", re.I)
INSTRUMENT_STEMS = ("drums", "bass", "guitar", "other", "piano")
SIDECAR = "canonical_v5_reindexed_sha256.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def classify(song: dict, corpus: Path) -> dict:
    sha16 = song["sha16"]
    title = str(song.get("title") or "")
    d = corpus / sha16
    tm_p = d / "transcription_manifest.json"
    rec = {"sha16": sha16, "title": title, "band": song.get("band"), "landed": tm_p.exists(),
           "r2_title_hit": bool(TITLE_RE.search(title)), "r2_match": (TITLE_RE.search(title).group(0) if TITLE_RE.search(title) else None)}
    if tm_p.exists():
        tm = json.loads(tm_p.read_text())
        nc = {k: int(v["n_note_on"]) for k, v in tm["note_counts"].items()}
        rec["note_counts"] = nc
        rec["r1_full_mix_zero"] = nc.get("full_mix", -1) == 0
        rec["r1_instrument_sum"] = sum(nc.get(s, 0) for s in INSTRUMENT_STEMS)
        rec["r1_fires"] = rec["r1_full_mix_zero"] and rec["r1_instrument_sum"] == 0
        rec["blocked"] = bool(rec["r1_fires"])
        if rec["r1_fires"] and rec["r2_title_hit"]:
            rec["verdict"] = "NON_MUSIC_CONTENT_R1_AND_R2"
        elif rec["r1_fires"]:
            rec["verdict"] = "NON_MUSIC_CONTENT_R1_ONLY"
        elif rec["r2_title_hit"]:
            rec["verdict"] = "R2_ONLY_NOT_BLOCKED"
        else:
            rec["verdict"] = "MUSIC"
        if rec["blocked"]:
            rec["transcription_manifest_sha256"] = _sha(tm_p)
            sc = d / SIDECAR
            rec["sidecar_sha256"] = _sha(sc) if sc.exists() else None
            rec["sidecar_present"] = sc.exists()
            if sc.exists():
                dt = sc.stat().st_mtime - tm_p.stat().st_mtime
                rec["hook_at_birth_delta_s"] = round(dt, 3)
                rec["hook_at_birth"] = 0 <= dt <= 5.0
    else:
        rec["r1_fires"] = None
        rec["blocked"] = False
        rec["verdict"] = "R2_PENDING_TRANSCRIPTION" if rec["r2_title_hit"] else "NOT_LANDED"
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v5 pre-registered content gate")
    ap.add_argument("--manifest", default="data/v5/corpus/corpus_manifest.json")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--prereg", default="data/v5/corpus/content_gate_prereg_c84.json")
    ap.add_argument("--out", default="data/v5/corpus/content_blocked.json")
    args = ap.parse_args(argv)
    os.chdir(_WS)
    corpus = Path(args.corpus_dir)
    prereg_p = Path(args.prereg)
    prereg = json.loads(prereg_p.read_text())
    out_p = Path(args.out)
    if out_p.exists() and out_p.stat().st_mtime < prereg_p.stat().st_mtime:
        raise SystemExit("PREREG_AFTER_OUTPUT: pre-registration must precede every output (FD-1)")
    man = json.loads(Path(args.manifest).read_text())
    songs = sorted([s for s in man["songs"] if s.get("in_v5_corpus")], key=lambda s: s["v5_priority_rank"])
    rows = [classify(s, corpus) for s in songs]
    blocked = {r["sha16"]: {k: r[k] for k in ("title", "band", "verdict", "note_counts", "transcription_manifest_sha256",
                                              "sidecar_sha256", "sidecar_present", "hook_at_birth_delta_s", "hook_at_birth") if k in r}
               for r in rows if r["blocked"]}
    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    out = {"schema_version": 1, "cycle": 84, "run_id": "run-2026-09-06T000000Z", "agent": "worker",
           "milestone": "M-V5-CORPUS-1/content-gate-c84", "env_pin_sha256": ENV_PIN_SHA256,
           "prereg_path": str(prereg_p), "prereg_sha256": _sha(prereg_p), "rules": prereg["rules"],
           "expected_blocked": prereg["expected"]["blocked"],
           "blocked_songs": blocked, "n_blocked": len(blocked),
           "matches_expectation": sorted(blocked) == sorted(prereg["expected"]["blocked"]),
           "verdict_tally": dict(sorted(tally.items())), "n_songs": len(rows), "n_landed": sum(1 for r in rows if r["landed"]),
           "per_song": rows,
           "gate": "harmony_v5.py / groove_v5.py / groove_v5_v2.py read this file and raise ContentBlockedError before reading any MIDI of a blocked song (c84 additive refusal).",
           "fd1": "no retune: if more than the expected song fires R1, that is recorded here as a finding, not fixed by loosening R1."}
    out_p.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(f"content gate: blocked {sorted(blocked)} (expected {prereg['expected']['blocked']}; match={out['matches_expectation']}); tally {out['verdict_tally']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
