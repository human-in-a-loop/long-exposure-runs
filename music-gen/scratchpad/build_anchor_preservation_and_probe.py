"""Anchor preservation manifest + c49 egress probe row.
Scratchpad-only; runs before ledger emission."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = Path("/home/user/long-exposure-runs/music-gen")
os.chdir(ROOT)


def sha_bytes(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---- Anchor preservation manifest (>=25 entries) ----
anchors = {}

# Per-focus-song htdemucs stems (5 songs × 4 stems = 20 entries).
focus = json.loads(Path("data/recreate_v2/focus_set.json").read_text())
for s in focus["songs"]:
    if not s["exists"]:
        continue
    band = s["rating_band"]
    sha16 = s["audio_sha16"]
    for stem in ("vocals", "drums", "bass", "other"):
        p = Path(f"data/recreate_v0_full_corpus/per_song/{band}/{sha16}/per_stage/04_htdemucs/{stem}.wav")
        if p.exists():
            anchors[str(p)] = sha_bytes(p)

# c48 verdicts + rubrics (READ-ONLY, both branches).
for p in [
    "data/harness_and_writer_hardening_v3/verdict.json",
    "data/harness_and_writer_hardening_v3/rubric_hash.txt",
    "data/pre_existing_test_drift/verdict.json",
    "data/pre_existing_test_drift/rubric_hash.txt",
    "docs/pre_registration_gate_policy.md",
    "data/anchor_manifest_v1.json",
    "docs/OPERATOR_recreation_root_cause_audit.md",
]:
    if Path(p).exists():
        anchors[p] = sha_bytes(p)

# Rules ledgers (must remain unmodified this cycle).
for p in [
    "data/rules/ledger.jsonl",
    "data/rules/ledger_i3_dminor.jsonl",
    "data/rules/ledger_rated_corpus.jsonl",
]:
    if Path(p).exists():
        anchors[p] = sha_bytes(p)

# Prior ear-arc verdicts.
for p in [
    "data/ear_v0/verdict.json",
    "data/ear_v1/verdict.json",
    "data/ear_v2/verdict.json",
    "data/ear_v2p1/verdict.json",
]:
    if Path(p).exists():
        anchors[p] = sha_bytes(p)

# Focus set + rubric (the c49 pre-registration set).
for p in [
    "data/recreate_v2/rubric_hash.txt",
    "data/recreate_v2/focus_set.json",
    "docs/m_recreate_2_accurate_small_set_rubric.md",
]:
    anchors[p] = sha_bytes(p)

manifest = {
    "cycle": 49,
    "anchor_count": len(anchors),
    "anchors": dict(sorted(anchors.items())),
}
Path("data/recreate_v2/anchor_preservation.json").write_text(
    json.dumps(manifest, indent=2) + "\n")
print(f"anchor_preservation: {len(anchors)} entries pinned")

# ---- c49 egress probe row ----
egress_row = {
    "ts": "2026-08-29T21:00:00Z",
    "cycle": 49,
    "clone": None,
    "attempt": "workspace/harvest_playlists.sh",
    "yt_dlp_meta_ok": False,
    "media_ok": False,
    "failure_mode": "HTTP 429 + tv_embedded",
    "notes": "unchanged from c45-c48; not the two-consecutive media_ok=true unblock signal",
}
egress_log = Path("data/ingestion/egress_status.jsonl")
egress_log.parent.mkdir(parents=True, exist_ok=True)
with open(egress_log, "a") as f:
    f.write(json.dumps(egress_row) + "\n")
print(f"egress row appended to {egress_log}")
