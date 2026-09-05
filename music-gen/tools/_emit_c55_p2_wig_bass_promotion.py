#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-05T16:15:00Z
# cycle: 55
# run_id: run-2026-09-05T160000Z
# agent: worker
# milestone: _lands/wig-bass-sf2-confirmed-c55
# ---
"""c55 P2: promote WIG bass sf2 family verdict STILL_INDETERMINATE -> SF2_CONFIRMED
under sibling-replication criterion (Rome/PD/DA all SF2_CONFIRMED at c52).

Metadata-only promotion per invariant (a) (no re-render). c28 landing artifacts
(bass.json, bass.replay_proof.json) preserved byte-identical. Only the family
verdict + stem_manifest bass.family_verdict advance.

Invariant (d) disclosure: the stage-2 leaderboard file
`data/v4/profiles/252eb21ce7df7328/bass_sweep_stage2/leaderboard.tsv` was
present at c28 landing (sha e146183c...) but is absent on disk at c55 (pruned
by c53-c55 relaunch attempts that were interrupted mid-run). Historical SHA is
recorded immutably in bass.json.provenance.stage2_leaderboard.sha256. The 43
partial render subdirs from the aborted c55 relaunch + the stale c53-anomaly
sentinel were cleaned this cycle per c27 hygiene.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIG = "252eb21ce7df7328"
PROFILE_DIR = ROOT / "data" / "v4" / "profiles" / WIG
VERDICT_PATH = PROFILE_DIR / "bass_family_verdict.json"
STEM_MANIFEST_PATH = PROFILE_DIR / "stem_manifest.json"
BASS_JSON_PATH = PROFILE_DIR / "bass.json"
REPLAY_PROOF_PATH = PROFILE_DIR / "bass.replay_proof.json"


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


PRE_VERDICT_SHA = sha256_of(VERDICT_PATH)
PRE_STEM_MANIFEST_SHA = sha256_of(STEM_MANIFEST_PATH)
PRE_BASS_JSON_SHA = sha256_of(BASS_JSON_PATH)
PRE_REPLAY_PROOF_SHA = sha256_of(REPLAY_PROOF_PATH)

# Load c28 verdict for provenance fields.
pre_verdict = json.loads(VERDICT_PATH.read_text())

# Construct SF2_CONFIRMED verdict per Rome (c52) shape.
new_verdict = {
    "cycle": 28,
    "distance_upper_bound_floor": 0.4,
    "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    "family": "sf2",
    "profile_id": pre_verdict["profile_id"],
    "profile_sha256": PRE_BASS_JSON_SHA,
    "promoted_at": "2026-09-05T16:15:00Z",
    "promoted_from_verdict": "STILL_INDETERMINATE",
    "promotion_authority": (
        "c47 operator omnibus 2026-09-05 part 3 (SF2_CONFIRMED lifted on "
        "non-CG bass) + c51 clarification of any-preset criterion + c52 "
        "three-way sibling replication (Rome c49 GM4 EP1, Peach Dream c50 "
        "GM5 EP2, Disco A c51 GM33 EBF) + c55 P2 brief directive "
        "'Promote directly to SF2_CONFIRMED under sibling-replication "
        "criterion'"
    ),
    "promotion_cycle": 55,
    "rationale": (
        "top-1 emb_cos_dist=0.1874 <= 0.4 distance-upper-bound floor. Under "
        "distance semantics (operator 2026-09-04) + OPT1 extension "
        "(operator omnibus 2026-09-05 point 3), SF2_CONFIRMED as sf2-family "
        "best-of-search winner (composite-relative). Family-2 (stem-sampled) "
        "+ family-3 (Surge XT) not searched this cycle; winner may shift on "
        "future cross-family compare per spec Procedure section. Non-CG "
        "bass tally now 4/4 SF2_CONFIRMED (Rome + Peach Dream + Disco A + WIG)."
    ),
    "replay_proof_sha256": PRE_REPLAY_PROOF_SHA,
    "slug": "what_if_i_go",
    "song_sha16": WIG,
    "supersedes_path": (
        "data/v4/profiles/252eb21ce7df7328/bass_family_verdict.json@"
        f"c28_pre_promotion_sha256_{PRE_VERDICT_SHA[:16]}"
    ),
    "top1_composite": pre_verdict["top1_composite"],
    "top1_embedding_cos_vggish": pre_verdict["top1_embedding_cos_vggish"],
    "top1_gain": pre_verdict["top1_gain"],
    "top1_mel_l1_db": pre_verdict["top1_mel_l1_db"],
    "top1_post": pre_verdict["top1_post"],
    "top1_program": pre_verdict["top1_program"],
    "top1_reverb_send": pre_verdict["top1_reverb_send"],
    "verdict": "SF2_CONFIRMED",
    "invariant_d_disclosures": [
        (
            "stage-2 leaderboard file "
            "data/v4/profiles/252eb21ce7df7328/bass_sweep_stage2/leaderboard.tsv "
            "recorded in bass.json provenance (sha e146183c0b736493aa5c4658cc7381e25e6ed77388496f25be85070981710ad0) "
            "is ABSENT on disk at c55; pruned by c53-c55 relaunch attempts "
            "that were interrupted mid-run. Historical SHA preserved "
            "immutably in bass.json.provenance.stage2_leaderboard.sha256 as "
            "provenance anchor; no re-render per invariant (a). c47 omnibus "
            "part 4 (preservation-spin BANNED) precludes re-launching solely "
            "to reproduce a lost artifact whose SHA is already anchored."
        ),
        (
            "Brief P2 prescribed Monitor task `bivimybxh`; that task lived "
            "in a prior session and did not survive to c55. PID 4492 from "
            "the c55-brief-noted previous session was DEAD at c55 open. "
            "Applied brief's 'if interrupted mid-run: clean partial dir + "
            "relaunch detached' branch, then recognized that c28 landing "
            "artifacts already suffice for SF2_CONFIRMED promotion under "
            "sibling-replication authority; no re-launch needed per "
            "invariant (a) + c47 omnibus part 4."
        ),
    ],
}

VERDICT_PATH.write_text(json.dumps(new_verdict, indent=2, sort_keys=True) + "\n")
POST_VERDICT_SHA = sha256_of(VERDICT_PATH)

# Update stem_manifest.bass to reflect new verdict.
stem_manifest = json.loads(STEM_MANIFEST_PATH.read_text())
stem_manifest["bass"] = {
    "family_verdict": "SF2_CONFIRMED",
    "family_verdict_cycle": 55,
    "family_verdict_sha256": POST_VERDICT_SHA,
    "promoted_from_verdict": "STILL_INDETERMINATE",
    "promoted_from_sha256": PRE_VERDICT_SHA,
}
STEM_MANIFEST_PATH.write_text(json.dumps(stem_manifest, indent=2, sort_keys=True) + "\n")
POST_STEM_MANIFEST_SHA = sha256_of(STEM_MANIFEST_PATH)

# Verify bass.json + replay_proof.json byte-identical pre==post (invariant a).
POST_BASS_JSON_SHA = sha256_of(BASS_JSON_PATH)
POST_REPLAY_PROOF_SHA = sha256_of(REPLAY_PROOF_PATH)
assert POST_BASS_JSON_SHA == PRE_BASS_JSON_SHA, "bass.json drift violates invariant (a)"
assert POST_REPLAY_PROOF_SHA == PRE_REPLAY_PROOF_SHA, "replay proof drift violates invariant (a)"

# Emit `_lands/wig-bass-sf2-confirmed-c55` ledger event.
event = {
    "milestone_id": "_lands/wig-bass-sf2-confirmed-c55",
    "cycle": 55,
    "status": "validated",
    "confidence": {
        "level": "high",
        "rationale": (
            "P2 landed. WIG bass sf2 family verdict promoted "
            "STILL_INDETERMINATE -> SF2_CONFIRMED under c47 omnibus part 3 "
            "(SF2_CONFIRMED lifted on non-CG bass) + c52 sibling-replication "
            "criterion (Rome + Peach Dream + Disco A all SF2_CONFIRMED). "
            "Top-1 emb_cos_dist=0.1874 well below 0.4 distance-upper-bound "
            "floor. Metadata-only promotion per invariant (a); bass.json + "
            "bass.replay_proof.json byte-identical pre==post. Non-CG bass "
            "tally advances 3/4 -> 4/4 SF2_CONFIRMED."
        ),
        "assessor": "worker",
    },
    "narrative": (
        "c55 Priority 2 landing. WIG (sha16 252eb21ce7df7328) bass sf2 "
        "family verdict promoted from STILL_INDETERMINATE (c28) to "
        "SF2_CONFIRMED (c55) per operator omnibus 2026-09-05 part 3 + c51 "
        "any-preset criterion + c52 three-way sibling-replication (Rome/PD/"
        "Disco A all SF2_CONFIRMED at 2026-09-05 13:59 UTC) + explicit c55 "
        "brief directive. Top-1 profile: bank 0 program 35 (Electric Bass "
        "Fretless), gain 0.5, reverb 0.3, post EQ_and_compressor, composite "
        "467.66, emb_cos_dist 0.1874 (well below 0.4 distance-upper-bound "
        "floor). Promotion metadata-only per invariant (a): bass.json sha "
        "fec2aadc59e6c67a0957740c8085f205507d32b679eca8f3ad85d1cd8344eb00 "
        "byte-identical pre==post; bass.replay_proof.json sha "
        "41454404a4f323e919c8471447ae6b104131f4069adff84ebf5438ad2da3c5bf "
        "byte-identical pre==post; only bass_family_verdict.json and "
        "stem_manifest.json.bass advanced. Pre-promotion verdict "
        "sha=8b847954532062b7c4a7148ddce51b02c952f09c0f9a557a6a3aa862e0860a0e "
        f"preserved via supersedes_path inline @-notation; post sha={POST_VERDICT_SHA}. "
        "stem_manifest pre sha=ef9fd87c61e2f872e59bafe8c0b64b49dbf9529215ce4d53b3e9d3a8e7e4aeb5 "
        f"-> post sha={POST_STEM_MANIFEST_SHA}. c55-P1 OP-1 writer full fix "
        "(landed earlier this cycle at event_id "
        "59a46d00-e067-54f6-a190-7f6a542118c3) unblocked this landing. "
        "Housekeeping: cleaned 43 partial render subdirs from the aborted "
        "c53-c55 relaunch attempts + unlinked stale c53-anomaly sentinel "
        "(PID 4492 dead, cycle:32/2025-08-29 stale payload) per c27 "
        "hygiene before promotion. Invariant (d) disclosures (see verdict "
        "JSON): stage-2 leaderboard file pruned/lost across relaunch "
        "attempts but SHA immutably anchored in bass.json provenance; brief-"
        "prescribed Monitor task `bivimybxh` was from prior session and did "
        "not survive to c55. Non-CG bass tally 3/4 -> 4/4 SF2_CONFIRMED "
        "(Rome + PD + Disco A + WIG)."
    ),
    "artifacts": [
        "data/v4/profiles/252eb21ce7df7328/bass_family_verdict.json",
        "data/v4/profiles/252eb21ce7df7328/stem_manifest.json",
    ],
    "supersedes_path": (
        "data/v4/profiles/252eb21ce7df7328/bass_family_verdict.json@"
        f"c28_pre_promotion_sha256_{PRE_VERDICT_SHA[:16]}"
    ),
    "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    "run_id": "run-2026-09-05T160000Z",
    "agent": "worker",
    "ts": "2026-09-05T16:15:00Z",
    "promotion_authority_verbatim": (
        "c47 operator omnibus 2026-09-05 part 3 (SF2_CONFIRMED lifted on "
        "non-CG bass) + c51 clarification of any-preset criterion + c52 "
        "three-way sibling replication + c55 brief P2 directive"
    ),
    "before_sha": {
        "data/v4/profiles/252eb21ce7df7328/bass_family_verdict.json": PRE_VERDICT_SHA,
        "data/v4/profiles/252eb21ce7df7328/stem_manifest.json": PRE_STEM_MANIFEST_SHA,
        "data/v4/profiles/252eb21ce7df7328/bass.json": PRE_BASS_JSON_SHA,
        "data/v4/profiles/252eb21ce7df7328/bass.replay_proof.json": PRE_REPLAY_PROOF_SHA,
    },
    "after_sha": {
        "data/v4/profiles/252eb21ce7df7328/bass_family_verdict.json": POST_VERDICT_SHA,
        "data/v4/profiles/252eb21ce7df7328/stem_manifest.json": POST_STEM_MANIFEST_SHA,
        "data/v4/profiles/252eb21ce7df7328/bass.json": POST_BASS_JSON_SHA,
        "data/v4/profiles/252eb21ce7df7328/bass.replay_proof.json": POST_REPLAY_PROOF_SHA,
    },
    "non_cg_bass_tally": {
        "before": "3/4 SF2_CONFIRMED (Rome + Peach Dream + Disco A)",
        "after": "4/4 SF2_CONFIRMED (Rome + Peach Dream + Disco A + WIG)",
    },
}

content = {k: v for k, v in event.items() if k not in ("event_id", "ts")}
canon = json.dumps(content, sort_keys=True, separators=(",", ":"))
event["event_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, canon))

line = json.dumps(event, sort_keys=True, separators=(",", ":"))
with open(ROOT / "promise_ledger.jsonl", "a") as f:
    f.write(line + "\n")

print(f"WIG bass PROMOTED SF2_CONFIRMED")
print(f"  pre_verdict_sha  = {PRE_VERDICT_SHA}")
print(f"  post_verdict_sha = {POST_VERDICT_SHA}")
print(f"  pre_stem_sha     = {PRE_STEM_MANIFEST_SHA}")
print(f"  post_stem_sha    = {POST_STEM_MANIFEST_SHA}")
print(f"  bass.json BYTE-IDENTICAL pre==post: {POST_BASS_JSON_SHA == PRE_BASS_JSON_SHA}")
print(f"  replay.json BYTE-IDENTICAL pre==post: {POST_REPLAY_PROOF_SHA == PRE_REPLAY_PROOF_SHA}")
print(f"  event_id = {event['event_id']}")
print(f"  tally: 3/4 -> 4/4 SF2_CONFIRMED")
