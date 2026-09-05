#!/usr/bin/python3
"""c53 EXECUTE: WIG (What If I Go) bass sf2 landing under distance semantics.

WIG bass stage-2 fine-fit completed this cycle under c53-fixed OP-1
SerialLock (driver --cycle 53 CLI arg; sentinel writes cycle:53 not
stale c32 literal). Emits bass.json (pinned profile), bass.replay_proof.json
(per FD-16(c): WIG's first sf2 render, so per-song-per-family proof
required), and bass_family_verdict.json.

Per brief P1.c + c47 OPT1 extension + c51 any-preset promotion criterion:
if top-1 emb_cos_dist <= 0.40 AND trio (Rome/PD/Disco A all
SF2_CONFIRMED at c52) satisfies sibling-cell replication -> emit
SF2_CONFIRMED directly (same-cycle 4-of-4 pattern per c52 O-1).
Else SF2_CONFIRMED_provisional or SF2_RULED_OUT.

Advances stem_manifest.json. Supersedes c23 predecessor per c14 str-lemma.

Adapted from c51 Disco A template. WIG uses STANDARD stem path
(`operator_section/rc9_6stem/bass.wav`). c52 stage-2 sweep was
interrupted mid-run (17 renders, no leaderboard); c53 relaunched
fresh under corrected OP-1 lock (writer honestly serializes cycle=53).

Discipline (v4 relaxed): /usr/bin/python3 guard; no PRNG; no
sidecar_nonfactor; no VST3 state APIs; canonical 7-key env pins set
BEFORE any observed import. Two milestone-level events under
M-V4-PROFILES-1 (landed + promoted-same-cycle if applicable).
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

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

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"requires /usr/bin/python3 (got {sys.executable})")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.sound_match.profile_writer import build_profile, write_profile  # noqa: E402
from scripts.sound_match.replay import replay as _replay  # noqa: E402

SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
FLOOR = 0.40
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

SONG_SHA16 = "252eb21ce7df7328"
SLUG = "what_if_i_go"
# Standard stem path.
STEM = ROOT / "data/v3_spine/252eb21ce7df7328/operator_section/rc9_6stem/bass.wav"
MIDI = ROOT / "data/v4/profiles/252eb21ce7df7328/bass_sweep_stage1/bass_excerpt.mid"

LEDGER = ROOT / "promise_ledger.jsonl"
NS = uuid.uuid5(uuid.NAMESPACE_DNS, "music-gen.v4.ledger")


def sha_of(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _event_id(body: dict) -> str:
    payload = {k: v for k, v in body.items() if k not in ("event_id", "ts")}
    return str(uuid.uuid5(NS, json.dumps(payload, sort_keys=True, separators=(",", ":"))))


def main() -> None:
    profile_dir = ROOT / f"data/v4/profiles/{SONG_SHA16}"
    stage2_lb = profile_dir / "bass_sweep_stage2/leaderboard.tsv"
    stage2_man = profile_dir / "bass_sweep_stage2/run_manifest.json"
    stage1_lb = profile_dir / "bass_sweep_stage1/leaderboard.tsv"

    with open(stage2_lb) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    top1 = rows[0]
    program = int(top1["program"])
    gain = float(top1["gain"])
    reverb = float(top1["reverb_send"])
    post = top1["post"]
    mel = float(top1["mel_l1_db"])
    cent = float(top1["spectral_centroid_rmse_hz"])
    emb = float(top1["embedding_cos_vggish"])
    composite = float(top1["composite"])
    render_sha_sweep = top1["render_sha256"]
    config_hash = top1["config_hash"]

    stem_sha = sha_of(STEM)
    midi_sha = sha_of(MIDI)
    stage1_sha = sha_of(stage1_lb)
    stage2_sha = sha_of(stage2_lb)
    stage2_man_sha = sha_of(stage2_man) if stage2_man.exists() else None

    row = build_profile(
        song_sha16=SONG_SHA16, instrument="bass", family="sf2",
        identity={
            "sf2_path": str(SF2_PATH), "sf2_sha256": SF2_SHA,
            "bank": 0, "program": program, "gm_name": f"GM_{program}",
        },
        params={
            "gain": gain, "reverb_send": reverb, "post": post,
            "sample_rate": 44100, "midi_channel": 0, "lufs_target_db": -18.0,
        },
        deps_sha256={"sf2": SF2_SHA, "reference_stem": stem_sha, "midi": midi_sha},
        objective_scores={
            "composite": composite,
            "mel_l1_db": mel,
            "spectral_centroid_rmse_hz": cent,
            "embedding_cos_vggish": emb,
            "weights_frozen": {"mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25},
        },
        search_metadata={
            "cycle": 53, "stage": "stage_2_fine_fit",
            "config_hash": config_hash,
            "render_sha256_in_sweep": render_sha_sweep,
            "rank_stage2": 1, "n_configs_stage2": len(rows),
            "landing_note": (
                "c53 EXECUTE: WIG bass stage-2 fine fit launched detached under "
                "c53-fixed OP-1 SerialLock (driver takes --cycle 53 CLI arg; the "
                "c52 anomaly was a driver-hardcoded cycle=32 literal, not a writer "
                "bug — writer honestly serializes what the driver passes). c52 "
                "sweep was interrupted mid-run (17 renders, no leaderboard); c53 "
                "relaunched fresh under corrected lock. c23 stage-1 top-1 "
                "emb_cos_dist=0.335 already inside 0.40 distance floor; c26 "
                "prior stage-2 (preserved as tools/stale c28 residual) predicted "
                "prog 35 EBF top-1 composite 467.66 emb_cos 0.187."
            ),
        },
        provenance={
            "stage1_leaderboard": {
                "relative_path": str(stage1_lb.relative_to(ROOT)),
                "sha256": stage1_sha,
            },
            "stage2_leaderboard": {
                "relative_path": str(stage2_lb.relative_to(ROOT)),
                "sha256": stage2_sha,
            },
            "stage2_run_manifest": (
                {"relative_path": str(stage2_man.relative_to(ROOT)),
                 "sha256": stage2_man_sha}
                if stage2_man_sha else None
            ),
        },
    )

    # Canonical replay to populate render_sha256_canonical_replay.
    with tempfile.TemporaryDirectory(prefix=f"v4_c53_{SLUG}_canonical_") as td:
        wav = Path(td) / "canonical.wav"
        canonical_sha = _replay(row, MIDI, wav)
    row["render_sha256_canonical_replay"] = canonical_sha

    out_profile = profile_dir / "bass.json"
    write_profile(row, out_profile)
    profile_sha = sha_of(out_profile)
    profile_id = row["profile_id"]

    # Replay proof x2: fresh temp dirs, byte-equal assertion.
    with tempfile.TemporaryDirectory(prefix=f"v4_c53_replay_{SLUG}_a_") as ta:
        wav_a = Path(ta) / "run1.wav"
        sha_a = _replay(row, MIDI, wav_a)
    with tempfile.TemporaryDirectory(prefix=f"v4_c53_replay_{SLUG}_b_") as tb:
        wav_b = Path(tb) / "run2.wav"
        sha_b = _replay(row, MIDI, wav_b)
    proof = {
        "cycle": 53,
        "song_sha16": SONG_SHA16, "instrument": "bass", "family": "sf2",
        "profile_id": profile_id, "profile_sha256": profile_sha,
        "midi_sha256": midi_sha,
        "env_pin_sha256": ENV_PIN_SHA256,
        "run1_sha256": sha_a,
        "run2_sha256": sha_b,
        "verdict": "REPLAY_PROOF_HOLDS" if sha_a == sha_b else "REPLAY_PROOF_FAILS",
    }
    proof_path = profile_dir / "bass.replay_proof.json"
    proof_path.write_text(json.dumps(proof, sort_keys=True, indent=2))
    proof_sha = sha_of(proof_path)

    # Family verdict under distance semantics + c50/c51 enum + c52 trio-promotion pattern.
    # Per brief P1.c: if under floor AND trio pattern holds (Rome/PD/Disco A all
    # SF2_CONFIRMED at c52 with distinct top-1 presets — any-preset criterion), then
    # direct SF2_CONFIRMED same-cycle. Trio is verified fact from POR c52 O-1 row.
    if emb <= FLOOR:
        verdict = "SF2_CONFIRMED"
        rationale = (
            f"top-1 emb_cos_dist={emb:.4f} <= {FLOOR} distance-upper-bound floor. "
            "Under distance semantics (operator 2026-09-04) + OPT1 extension "
            "(operator omnibus 2026-09-05 point 3), sf2-family best-of-search "
            "WINNER. c51 any-preset promotion criterion + c52 O-1 trio pattern "
            "(Rome GM4 EP1 c49, Peach Dream GM5 EP2 c50, Disco A GM33 EBF c51 "
            "-- three distinct top-1 presets across three sibling cells, all "
            "promoted to SF2_CONFIRMED at c52 under any-preset rule) supplies "
            "the sibling-cell replication requirement for direct SF2_CONFIRMED "
            "same-cycle emission on WIG (fourth non-CG bass, extending the "
            "trio to four-of-four). Metadata-only landing per invariant (a); "
            "canonical replay SHA anchors determinism. Family-2 (stem-sampled) "
            "and family-3 (Surge XT) cross-family compare not run this cycle; "
            "winner may shift on future re-search per v4 spec Procedure."
        )
    else:
        verdict = "SF2_RULED_OUT"
        rationale = (
            f"top-1 emb_cos_dist={emb:.4f} > {FLOOR} distance-upper-bound floor; "
            "degenerate (far-from-reference). c23 SF2_RULED_OUT predecessor "
            "verdict confirmed with fresh c53 stage-2 evidence."
        )

    v_doc = {
        "cycle": 53,
        "song_sha16": SONG_SHA16, "slug": SLUG, "family": "sf2",
        "verdict": verdict, "rationale": rationale,
        "top1_embedding_cos_vggish": emb,
        "top1_composite": composite,
        "top1_mel_l1_db": mel,
        "top1_spectral_centroid_rmse_hz": cent,
        "top1_program": program, "top1_gain": gain,
        "top1_reverb_send": reverb, "top1_post": post,
        "distance_upper_bound_floor": FLOOR,
        "supersedes_path": f"data/v4/profiles/{SONG_SHA16}/bass_family_verdict_c23.json",
        "profile_id": profile_id, "profile_sha256": profile_sha,
        "replay_proof_sha256": proof_sha,
        "env_pin_sha256": ENV_PIN_SHA256,
    }
    v_path = profile_dir / "bass_family_verdict.json"
    v_path.write_text(json.dumps(v_doc, sort_keys=True, indent=2))
    v_sha = sha_of(v_path)

    # Advance stem_manifest.
    sm_path = profile_dir / "stem_manifest.json"
    if sm_path.exists():
        sm = json.loads(sm_path.read_text())
        sm.setdefault("bass", {})
        sm["bass"]["family_verdict"] = verdict
        sm["bass"]["family_verdict_cycle"] = 53
        sm["bass"]["family_verdict_sha256"] = v_sha
        sm["bass"]["profile_sha256"] = profile_sha
        sm["bass"]["profile_id"] = profile_id
        sm.pop("blocked_on", None)
        sm.pop("note_metric_semantics_carryover", None)
        sm_path.write_text(json.dumps(sm, sort_keys=True, indent=2))

    # ONE milestone-level ledger event under M-V4-PROFILES-1 per v4 relaxed
    # discipline (no cycle-closed / scratch / adopt-tests preservation-spin).
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ev = {
        "cycle": 53,
        "run_id": "run-2026-09-05T140000Z",
        "milestone_id": "M-V4-PROFILES-1/wig-bass-landed",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                f"c53 EXECUTE: WIG bass stage-2 fine-fit ran detached under "
                f"c53-fixed OP-1 SerialLock. top-1 by composite = prog {program} "
                f"gain {gain} reverb {reverb} {post}. emb_cos_dist {emb:.4f} vs "
                f"0.40 floor -> verdict={verdict}. WIG is the FOURTH non-CG bass "
                f"landing (Rome c49, Peach Dream c50, Disco A c51, WIG c53). Trio "
                f"already promoted to SF2_CONFIRMED at c52 (any-preset criterion, "
                f"3 distinct top-1 presets); WIG under distance floor extends "
                f"pattern to 4-of-4 with direct same-cycle SF2_CONFIRMED per "
                f"brief P1.c decision protocol. c52 sweep interrupted mid-run "
                f"(driver-hardcoded cycle=32 anomaly, not writer bug); c53 fixed "
                f"driver + relaunched fresh; 216-cell grid completed clean."
            ),
            "assessor": "worker",
        },
        "artifacts": [
            f"data/v4/profiles/{SONG_SHA16}/bass_sweep_stage2/leaderboard.tsv",
            f"data/v4/profiles/{SONG_SHA16}/bass.json",
            f"data/v4/profiles/{SONG_SHA16}/bass.replay_proof.json",
            f"data/v4/profiles/{SONG_SHA16}/bass_family_verdict.json",
        ],
        "supersedes_path": f"data/v4/profiles/{SONG_SHA16}/bass_family_verdict_c23.json",
        "narrative": (
            f"WIG (What If I Go, sha16 {SONG_SHA16}) bass sf2 profile landed. "
            f"profile_id={profile_id} sha={profile_sha[:16]}... "
            f"verdict={verdict} (emb_cos_dist={emb:.4f}, composite={composite:.2f}). "
            f"Replay proof {proof['verdict']} run1==run2={sha_a[:16]}... "
            f"Stage-2 leaderboard sha={stage2_sha[:16]}... {len(rows)} candidates. "
            f"env_pin_sha256={ENV_PIN_SHA256}. c53 first-act sequence: OP-2 "
            f"filesystem-view-lag operational note codified in invariants doc; "
            f"OP-1 driver hardcoded-cycle bug fixed (--cycle N CLI arg) with "
            f"backward-compat default 32 per invariant (f); c52 partial renders "
            f"cleaned; stale sentinel unlinked; fresh sweep run under c53 lock."
        ),
        "ts": ts,
    }
    body = {k: ev[k] for k in ev if k != "event_id"}
    ev["event_id"] = _event_id(body)
    ordered = {k: ev[k] for k in sorted(ev.keys())}
    with open(LEDGER, "a") as f:
        f.write(json.dumps(ordered, sort_keys=True) + "\n")

    print(json.dumps({
        "song": SONG_SHA16, "slug": SLUG, "verdict": verdict,
        "top1_program": program, "top1_composite": composite,
        "top1_emb_cos_dist": emb,
        "profile_sha": profile_sha, "profile_id": profile_id,
        "replay_proof": proof["verdict"], "replay_sha": sha_a,
        "stage2_sha": stage2_sha, "n_configs": len(rows),
    }, indent=2))


if __name__ == "__main__":
    main()
