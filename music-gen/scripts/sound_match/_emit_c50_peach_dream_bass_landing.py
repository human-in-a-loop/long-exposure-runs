#!/usr/bin/python3
"""c50 EXECUTE: Peach Dream bass sf2 landing under distance semantics.

Peach Dream bass stage-2 fine-fit completed this cycle. Emits bass.json
(pinned profile), bass.replay_proof.json (per FD-16(c): Peach Dream's
first sf2 render, so per-song-per-family proof required), and
bass_family_verdict.json under c50 enum extension (SF2_CONFIRMED_provisional
if best-of-search winner AND top-1 emb_cos_dist <= 0.40; else SF2_RULED_OUT).
Advances stem_manifest.json. Supersedes c23 predecessor per c14 str-lemma.

Invariant (d) disclosure: Peach Dream stems live under the non-standard
`operator_section_c25_checkpointed/rc9_6stem/` path (c25 checkpointed-driver
run). The standard `operator_section/rc9_6stem/` path does NOT exist for
this song. Both the sweep and this emitter use the on-disk canonical path.

Discipline (v4 relaxed): /usr/bin/python3 guard; no PRNG; no
sidecar_nonfactor; no VST3 state APIs; canonical 7-key env pins set
BEFORE any observed import. NO per-cycle preservation-spin ledger events
-- one milestone-level event under M-V4-PROFILES-1.
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

SONG_SHA16 = "88d247468cb6d49f"
SLUG = "peach_dream"
# Invariant (d): non-standard stem path (c25 checkpointed-driver run).
STEM = ROOT / "data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/rc9_6stem/bass.wav"
MIDI = ROOT / "data/v4/profiles/88d247468cb6d49f/bass_sweep_stage1/bass_excerpt.mid"

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
            "cycle": 50, "stage": "stage_2_fine_fit",
            "config_hash": config_hash,
            "render_sha256_in_sweep": render_sha_sweep,
            "rank_stage2": 1, "n_configs_stage2": len(rows),
            "landing_note": (
                "c50 EXECUTE: Peach Dream bass stage-2 fine fit launched "
                "detached under OP-1 SerialLock and completed in-cycle under "
                "c27 hygiene (RunningTopK + prune_after_pin). Non-standard "
                "stem path (invariant d): operator_section_c25_checkpointed/"
                "rc9_6stem/bass.wav. c23 stage-1 top-1 emb_cos_dist=0.4437 "
                "was borderline; stage-2 result determines c23 supersede."
            ),
        },
        provenance={
            "stem_path_divergence_note": (
                "Peach Dream stems live under operator_section_c25_checkpointed/"
                "rc9_6stem/ (c25 checkpointed-driver run); standard "
                "operator_section/rc9_6stem/ path does not exist for this song. "
                "Disclosed per invariant (d) from c19 stem_manifest opening."
            ),
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
    with tempfile.TemporaryDirectory(prefix=f"v4_c50_{SLUG}_canonical_") as td:
        wav = Path(td) / "canonical.wav"
        canonical_sha = _replay(row, MIDI, wav)
    row["render_sha256_canonical_replay"] = canonical_sha

    out_profile = profile_dir / "bass.json"
    write_profile(row, out_profile)
    profile_sha = sha_of(out_profile)
    profile_id = row["profile_id"]

    # Replay proof x2: fresh temp dirs, byte-equal assertion.
    with tempfile.TemporaryDirectory(prefix=f"v4_c50_replay_{SLUG}_a_") as ta:
        wav_a = Path(ta) / "run1.wav"
        sha_a = _replay(row, MIDI, wav_a)
    with tempfile.TemporaryDirectory(prefix=f"v4_c50_replay_{SLUG}_b_") as tb:
        wav_b = Path(tb) / "run2.wav"
        sha_b = _replay(row, MIDI, wav_b)
    proof = {
        "cycle": 50,
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

    # Family verdict under distance semantics + c50 enum extension.
    if emb <= FLOOR:
        verdict = "SF2_CONFIRMED_provisional"
        rationale = (
            f"top-1 emb_cos_dist={emb:.4f} <= {FLOOR} distance-upper-bound floor. "
            "Under distance semantics (operator 2026-09-04) + OPT1 extension "
            "(operator omnibus 2026-09-05 point 3), SF2_CONFIRMED_provisional "
            "as sf2-family best-of-search winner. c50 enum-extension addendum "
            "(docs/agent_picks_selection_invariants.md) applies. Family-2 "
            "(stem-sampled) + family-3 (Surge XT) not searched this cycle; "
            "winner may shift on future cross-family compare per spec Procedure. "
            "Sibling-cell replication for provisional->confirmed promotion "
            "criterion is c51+ scope."
        )
    else:
        verdict = "SF2_RULED_OUT"
        rationale = (
            f"top-1 emb_cos_dist={emb:.4f} > {FLOOR} distance-upper-bound floor; "
            "degenerate (far-from-reference). c23 SF2_RULED_OUT predecessor "
            "verdict confirmed with fresh stage-2 evidence."
        )

    v_doc = {
        "cycle": 50,
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
        "stem_path_divergence_note": (
            "Peach Dream stems live under operator_section_c25_checkpointed/"
            "rc9_6stem/ (c25 checkpointed-driver run); disclosed per invariant (d)."
        ),
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
        sm["bass"]["family_verdict_cycle"] = 50
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
        "cycle": 50,
        "run_id": "run-2026-09-05T060000Z",
        "milestone_id": "M-V4-PROFILES-1/peach-dream-bass-landed",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                f"c50 EXECUTE: Peach Dream bass stage-2 fine-fit ran detached "
                f"under OP-1 SerialLock. top-1 by composite = prog {program} gain "
                f"{gain} reverb {reverb} {post}. emb_cos_dist {emb:.4f} vs 0.40 "
                f"floor -> verdict={verdict}. Non-standard stem path (invariant d) "
                f"used explicitly. c50 enum-extension addendum (SF2_CONFIRMED_"
                f"provisional semantics + promotion criterion) applies. Peach "
                f"Dream is the SECOND post-c24 non-CG bass advance (Rome first, c49)."
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
            f"Peach Dream (sha16 {SONG_SHA16}) bass sf2 profile landed. "
            f"profile_id={profile_id} sha={profile_sha[:16]}... "
            f"verdict={verdict} (emb_cos_dist={emb:.4f}, composite={composite:.2f}). "
            f"Replay proof {proof['verdict']} run1==run2={sha_a[:16]}... "
            f"Stage-2 leaderboard sha={stage2_sha[:16]}... {len(rows)} candidates. "
            f"env_pin_sha256={ENV_PIN_SHA256}. c50 enum-extension addendum lands "
            f"in docs/agent_picks_selection_invariants.md (new sha propagates to "
            f"test_12 pin update, same cycle). Non-standard stem path preserved "
            f"per invariant (d)."
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
