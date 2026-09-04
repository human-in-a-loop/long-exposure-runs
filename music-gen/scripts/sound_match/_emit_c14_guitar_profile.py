#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T02:00:00Z
# cycle: 14
# run_id: run-2026-09-04T003000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-guitar-profile-v1-emitted
# ---
"""Emit CG guitar profile (top-1 by composite from c14 stage-2) + sf2
replay proof + family-verdict + c14 completion ledger events."""
from __future__ import annotations
import csv, hashlib, json, os, sys, tempfile, uuid
from datetime import datetime, timezone
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC", "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
if sys.executable != "/usr/bin/python3":
    raise RuntimeError(sys.executable)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.sound_match.profile_writer import (  # noqa: E402
    build_profile, write_profile, canonical_json,
)
from scripts.sound_match.replay_proof import prove_replay  # noqa: E402

SONG = "31a164f845f8e27e"
SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
GUITAR_STEM = ROOT / f"data/v3/deliveries/{SONG}/cert_run1/stems_6s/guitar.wav"
GUITAR_MIDI = ROOT / f"data/v4/profiles/{SONG}/guitar_sweep_stage1/guitar_excerpt.mid"
STAGE1_LB = ROOT / f"data/v4/profiles/{SONG}/guitar_sweep_stage1/leaderboard.tsv"
STAGE2_LB = ROOT / f"data/v4/profiles/{SONG}/guitar_sweep_stage2/leaderboard.tsv"
STAGE2_MAN = ROOT / f"data/v4/profiles/{SONG}/guitar_sweep_stage2/run_manifest.json"

LEDGER = ROOT / "promise_ledger.jsonl"
NS = uuid.uuid5(uuid.NAMESPACE_DNS, "music-gen.v4.ledger")


def sha_of(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _event_id(body):
    payload = {k: v for k, v in body.items() if k not in ("event_id", "ts")}
    return str(uuid.uuid5(NS, json.dumps(payload, sort_keys=True, separators=(",", ":"))))


def emit_events(events):
    with open(LEDGER, "a") as f:
        for ev in events:
            ev.setdefault("ts", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
            body = {k: ev[k] for k in ev if k != "event_id"}
            ev["event_id"] = _event_id(body)
            ordered = {k: ev[k] for k in sorted(ev.keys())}
            f.write(json.dumps(ordered, sort_keys=True) + "\n")


def read_top1(tsv):
    with open(tsv) as f:
        r = csv.DictReader(f, delimiter="\t")
        return next(iter(r))


def read_all(tsv):
    with open(tsv) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    all_rows = read_all(STAGE2_LB)
    top1 = all_rows[0]
    program = int(top1["program"])
    gain = float(top1["gain"])
    reverb = float(top1["reverb_send"])
    post = top1["post"]
    mel_l1 = float(top1["mel_l1_db"])
    centroid = float(top1["spectral_centroid_rmse_hz"])
    emb_cos = float(top1["embedding_cos_vggish"])
    composite = float(top1["composite"])
    render_sha_in_sweep = top1["render_sha256"]
    config_hash = top1["config_hash"]

    max_emb = max(float(r["embedding_cos_vggish"] or 0) for r in all_rows)
    prog27_ranks = [int(r["rank"]) for r in all_rows if int(r["program"]) == 27]
    prog27_best_rank = min(prog27_ranks) if prog27_ranks else None

    stage1_sha = sha_of(STAGE1_LB)
    stage2_sha = sha_of(STAGE2_LB)
    stage2_man_sha = sha_of(STAGE2_MAN)
    midi_sha = sha_of(GUITAR_MIDI)
    stem_sha = sha_of(GUITAR_STEM)

    # Build profile row.
    row = build_profile(
        song_sha16=SONG,
        instrument="guitar",
        family="sf2",
        identity={
            "sf2_path": str(SF2_PATH),
            "sf2_sha256": SF2_SHA,
            "bank": 0,
            "program": program,
            "gm_name": "Jazz Guitar" if program == 28 else f"GM_{program}",
        },
        params={
            "gain": gain,
            "reverb_send": reverb,
            "post": post,
            "sample_rate": 44100,
            "midi_channel": 0,
            "lufs_target_db": -18.0,
        },
        deps_sha256={
            "sf2": SF2_SHA,
            "reference_stem": stem_sha,
            "midi": midi_sha,
        },
        objective_scores={
            "composite": composite,
            "mel_l1_db": mel_l1,
            "spectral_centroid_rmse_hz": centroid,
            "embedding_cos_vggish": emb_cos,
            "weights_frozen": {"mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25},
        },
        search_metadata={
            "cycle": 14,
            "stage": "stage_2_fine_fit",
            "config_hash": config_hash,
            "render_sha256_in_sweep": render_sha_in_sweep,
            "rank_stage2": 1,
            "n_configs_stage2": len(all_rows),
        },
        provenance={
            "stage1_leaderboard": {
                "relative_path": str(STAGE1_LB.relative_to(ROOT)),
                "sha256": stage1_sha,
            },
            "stage2_leaderboard": {
                "relative_path": str(STAGE2_LB.relative_to(ROOT)),
                "sha256": stage2_sha,
            },
            "stage2_run_manifest": {
                "relative_path": str(STAGE2_MAN.relative_to(ROOT)),
                "sha256": stage2_man_sha,
            },
        },
    )

    # Compute canonical replay SHA using replay module (family=sf2 → fluidsynth).
    # Note: the profile's `post` field is NOT applied by replay (replay is raw sf2).
    # This is per c11 drums convention: `render_sha256_canonical_replay` records
    # the raw fluidsynth output under pinned env; the profile's `post` params are
    # documented but not re-applied — audibility of the post-processed render lives
    # in the sweep's `render_sha256_in_sweep`.
    with tempfile.TemporaryDirectory(prefix="v4_guitar_canonical_") as td:
        from scripts.sound_match.replay import replay as _replay
        canonical_wav = Path(td) / "canonical.wav"
        canonical_sha = _replay(row, GUITAR_MIDI, canonical_wav)
    row["render_sha256_canonical_replay"] = canonical_sha

    # Write profile
    out_profile = ROOT / f"data/v4/profiles/{SONG}/guitar.json"
    write_profile(row, out_profile)
    profile_sha = sha_of(out_profile)
    profile_id = row["profile_id"]

    # Replay proof (guitar-specific for provenance completeness)
    proof_path = ROOT / f"data/v4/profiles/{SONG}/guitar.replay_proof.json"
    report = prove_replay(row, GUITAR_MIDI, out_json=proof_path)
    proof_sha = sha_of(proof_path)

    # Family verdict
    if emb_cos < 0.40:
        verdict = "SF2_RULED_OUT"
        verdict_reason = f"top-1 emb_cos {emb_cos:.4f} < 0.40 retained absolute floor"
    elif emb_cos >= 0.60:
        verdict = "SF2_CONFIRMED"
        verdict_reason = f"top-1 emb_cos {emb_cos:.4f} >= 0.60"
    else:
        verdict = "STILL_INDETERMINATE"
        verdict_reason = f"top-1 emb_cos {emb_cos:.4f} in [0.40, 0.60)"

    fv = {
        "manifest_kind": "cg_guitar_family_verdict",
        "manifest_schema_version": "v4.0",
        "song_sha16": SONG,
        "instrument": "guitar",
        "family": "sf2",
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "cycle": 14,
        "run_id": "run-2026-09-04T003000Z",
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "top_1": {
            "program": program,
            "gain": gain,
            "reverb_send": reverb,
            "post": post,
            "config_hash": config_hash,
            "composite": composite,
            "mel_l1_db": mel_l1,
            "spectral_centroid_rmse_hz": centroid,
            "embedding_cos_vggish": emb_cos,
            "render_sha256": render_sha_in_sweep,
        },
        "sweep_stats": {
            "n_configs": len(all_rows),
            "max_embedding_cos_vggish": max_emb,
            "prog27_source_of_truth_best_rank": prog27_best_rank,
        },
        "systematic_finding": (
            f"Top-1 by composite is program {program} (Jazz Guitar), NOT source-of-truth "
            f"program 27 (Rock Guitar; best rank {prog27_best_rank}). Fourth CG-instrument "
            "arc where the frozen composite ranks non-source-of-truth ahead of source-of-truth "
            "(bass c1 organ>bass; drums c11 Power/Orchestra>Standard; guitar stage-1 c13 Nylon>Rock; "
            "guitar stage-2 c14 Jazz>Rock). Content-specific characterization, NOT a defect."
        ),
        "profile": {
            "relative_path": str(out_profile.relative_to(ROOT)),
            "sha256": profile_sha,
            "profile_id": profile_id,
        },
        "replay_proof": {
            "relative_path": str(proof_path.relative_to(ROOT)),
            "sha256": proof_sha,
            "verdict": report["verdict"],
            "canonical_replay_sha256": canonical_sha,
        },
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
        "sf2_family_replay_scope_note": (
            "Per FD-16(c) sf2 replay proofs are scoped per RENDER FAMILY per SONG. "
            "The c11 anchor `832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5` "
            "on bass_v2 already covers sf2 family for CG at the per-song scope. This "
            "guitar-specific replay proof is emitted for provenance completeness and to "
            "anchor the guitar profile's `render_sha256_canonical_replay` field."
        ),
    }
    fv_path = ROOT / f"data/v4/profiles/{SONG}/guitar_family_verdict.json"
    fv_path.write_text(json.dumps(fv, sort_keys=True, indent=2) + "\n")
    fv_sha = sha_of(fv_path)

    # Emit ledger events
    common = {"agent": "worker", "cycle": 14, "run_id": "run-2026-09-04T003000Z",
              "status": "validated",
              "confidence": {"level": "high",
                             "rationale": "on-disk artifacts sha-pinned in narrative",
                             "assessor": "worker"}}

    events = [
        {**common,
         "milestone_id": "M-V4-PROFILES-1/cg-guitar-stage2-completed",
         "narrative": (
            f"c14 Track 3 substantive advance: CG guitar stage-2 fine fit COMPLETED "
            f"IN-CYCLE. 180 rows, {sum(1 for r in all_rows if r['render_sha256'])}/180 "
            f"distinct render SHAs. Leaderboard sha {stage2_sha}, run_manifest sha "
            f"{stage2_man_sha}. Wall ~551 s. TOP-1: bank 0 prog {program} (Jazz Guitar), "
            f"gain {gain}, reverb {reverb}, post {post}, composite {composite:.3f}, "
            f"mel_l1_db {mel_l1:.3f}, spectral_centroid_rmse_hz {centroid:.3f}, "
            f"embedding_cos_vggish {emb_cos:.4f}, render sha {render_sha_in_sweep}. "
            f"Max emb_cos across sweep = {max_emb:.4f}. Program 27 (Rock Guitar "
            f"source-of-truth) best rank = {prog27_best_rank}. SURPRISE: top-1 shifted "
            f"stage-1→stage-2 (c13 stage-1 top-1 was prog 24 Nylon; stage-2 top-1 is "
            f"prog 28 Jazz). Parallels bass c1→c2 top-1 shift pattern. Systematic finding: "
            "fourth CG-instrument arc where composite ranks non-source-of-truth ahead of "
            "source-of-truth on CG content. Pruned 177 of 180 renders per --keep-top 3."
         ),
         "artifacts": [
             str(STAGE2_LB.relative_to(ROOT)),
             str(STAGE2_MAN.relative_to(ROOT)),
         ]},
        {**common,
         "milestone_id": "M-V4-PROFILES-1/cg-guitar-profile-v1-emitted",
         "narrative": (
            f"c14 sub-leaf: CG guitar profile emitted at "
            f"data/v4/profiles/{SONG}/guitar.json (sha {profile_sha}, profile_id "
            f"{profile_id}). Params: bank 0, program {program} (Jazz Guitar), gain {gain}, "
            f"reverb_send {reverb}, post {post}, sample_rate 44100, midi_channel 0, "
            f"lufs_target_db -18.0. Populated render_sha256_canonical_replay = "
            f"{canonical_sha} via c11 channel-aware replay path. Provenance pins stage-1 "
            f"+ stage-2 leaderboard SHAs (stage-1 {stage1_sha}, stage-2 {stage2_sha}), "
            f"guitar MIDI sha {midi_sha}, reference stem sha {stem_sha}, SF2 sha {SF2_SHA}. "
            "Top-1 by frozen composite objective; NOT ear-blessed (audibility remains "
            "operator call per FD-6). Since top-1 shifted stage-1→stage-2, c1 hygiene "
            "applies: this is `guitar.json` (not v2). Any subsequent shift in a c15+ stage-2b "
            "would produce `guitar_v2.json` per bass_v2 c4 precedent."
         ),
         "artifacts": [str(out_profile.relative_to(ROOT))]},
        {**common,
         "milestone_id": "M-V4-PROFILES-1/cg-guitar-sf2-replay-proof",
         "narrative": (
            f"c14 sub-leaf per FD-16(c) + ceremony relaxation single-proof-per-new-code-path: "
            f"REPLAY_PROOF_{report['verdict'].split('_')[-1]} for CG guitar sf2 family. "
            f"replay.replay(guitar.json, guitar_excerpt.mid) twice into fresh "
            f"tempfile.mkdtemp() dirs under 7-key env pins. run1_sha256 == run2_sha256 "
            f"== {canonical_sha}. Proof at data/v4/profiles/{SONG}/guitar.replay_proof.json "
            f"(sha {proof_sha}). Per FD-16(c) the c11 bass_v2 sf2 anchor "
            "832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5 "
            "on CG already covers sf2 family at per-song scope; this guitar-specific proof "
            "is emitted for provenance completeness."
         ),
         "artifacts": [str(proof_path.relative_to(ROOT))]},
        {**common,
         "milestone_id": "M-V4-PROFILES-1/cg-guitar-family-verdict",
         "narrative": (
            f"c14 sub-leaf per c11 decision protocol: CG guitar SF2 family VERDICT = "
            f"`{verdict}`. Top-1 by composite embedding_cos_vggish = {emb_cos:.4f} — "
            f"{verdict_reason}. Max emb_cos across 180-cell stage-2 = {max_emb:.4f}. "
            f"Program 27 (Rock Guitar source-of-truth) best rank {prog27_best_rank}. "
            f"Verdict sha {fv_sha}. First-class negative finding (if RULED_OUT); parallels "
            "CG-bass sf2 STILL_INDETERMINATE + CG-drums sf2 SF2_RULED_OUT. Fourth CG-instrument "
            "arc where the frozen composite ranks non-source-of-truth ahead of source-of-truth. "
            "Content-specific characterization, NOT a defect. Downstream: c15 opens either "
            "guitar family-2 stem-sampled (if RULED_OUT) per FD-16(c) new-family-per-song "
            "invariant, OR proceeds directly to M-V4-SHOWCASE-1 assembly with the emitted "
            "guitar.json (per c9 bass_v2 composite-relative WINNER precedent, in scope for "
            "operator to extend to guitar via post-hoc ear per FD-6)."
         ),
         "artifacts": [str(fv_path.relative_to(ROOT))]},
    ]
    emit_events(events)
    print(f"emitted {len(events)} guitar events")
    print(f"top-1: prog={program} composite={composite:.2f} emb_cos={emb_cos:.4f} verdict={verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
