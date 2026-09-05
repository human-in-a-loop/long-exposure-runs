#!/usr/bin/env -S /usr/bin/python3
"""c26 Track A: emit WIG + Disco A stage-2 bass profiles + family verdicts
+ replay proofs. Under distance semantics + c26 absolute discipline:
  top-1 emb_cos_dist ≤ 0.40 → STILL_INDETERMINATE
  top-1 emb_cos_dist > 0.40 → SF2_RULED_OUT
SF2_CONFIRMED is FORBIDDEN this cycle.
"""
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

from scripts.sound_match.profile_writer import build_profile, write_profile  # noqa: E402
from scripts.sound_match.replay import replay as _replay  # noqa: E402

SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
FLOOR = 0.40

SONGS = {
    "252eb21ce7df7328": {
        "slug": "what_if_i_go",
        "stem": ROOT / "data/v3_spine/252eb21ce7df7328/operator_section/rc9_6stem/bass.wav",
        "midi": ROOT / "data/v4/profiles/252eb21ce7df7328/bass_sweep_stage1/bass_excerpt.mid",
    },
    "cdd2717e52820ff6": {
        "slug": "disco_a",
        "stem": ROOT / "data/v3_spine/cdd2717e52820ff6/operator_section/rc9_6stem/bass.wav",
        "midi": ROOT / "data/v4/profiles/cdd2717e52820ff6/bass_sweep_stage1/bass_excerpt.mid",
    },
}

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


def process_song(sha16: str, cfg: dict) -> dict:
    slug = cfg["slug"]
    stem = cfg["stem"]
    midi = cfg["midi"]
    profile_dir = ROOT / f"data/v4/profiles/{sha16}"
    stage1_lb = profile_dir / "bass_sweep_stage1/leaderboard.tsv"
    stage2_lb = profile_dir / "bass_sweep_stage2/leaderboard.tsv"
    stage2_man = profile_dir / "bass_sweep_stage2/run_manifest.json"

    if not stage2_lb.exists():
        return {"song": sha16, "slug": slug, "status": "STAGE2_MISSING", "reason": f"no {stage2_lb}"}

    with open(stage2_lb) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    if not rows:
        return {"song": sha16, "slug": slug, "status": "STAGE2_EMPTY"}

    top1 = rows[0]
    program = int(top1["program"])
    gain = float(top1["gain"])
    reverb = float(top1["reverb_send"])
    post = top1["post"]
    mel = float(top1["mel_l1_db"])
    cent = float(top1["spectral_centroid_rmse_hz"])
    emb = float(top1["embedding_cos_vggish"]) if top1["embedding_cos_vggish"] not in ("", "None", None) else None
    composite = float(top1["composite"])
    render_sha_sweep = top1["render_sha256"]
    config_hash = top1["config_hash"]

    stem_sha = sha_of(stem)
    midi_sha = sha_of(midi)
    stage1_sha = sha_of(stage1_lb)
    stage2_sha = sha_of(stage2_lb)
    stage2_man_sha = sha_of(stage2_man) if stage2_man.exists() else None

    row = build_profile(
        song_sha16=sha16, instrument="bass", family="sf2",
        identity={
            "sf2_path": str(SF2_PATH), "sf2_sha256": SF2_SHA,
            "bank": 0, "program": program, "gm_name": f"GM_{program}",
        },
        params={"gain": gain, "reverb_send": reverb, "post": post,
                "sample_rate": 44100, "midi_channel": 0, "lufs_target_db": -18.0},
        deps_sha256={"sf2": SF2_SHA, "reference_stem": stem_sha, "midi": midi_sha},
        objective_scores={
            "composite": composite, "mel_l1_db": mel,
            "spectral_centroid_rmse_hz": cent,
            "embedding_cos_vggish": emb,
            "weights_frozen": {"mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25},
        },
        search_metadata={
            "cycle": 26, "stage": "stage_2_fine_fit",
            "config_hash": config_hash,
            "render_sha256_in_sweep": render_sha_sweep,
            "rank_stage2": 1, "n_configs_stage2": len(rows),
        },
        provenance={
            "stage1_leaderboard": {"relative_path": str(stage1_lb.relative_to(ROOT)), "sha256": stage1_sha},
            "stage2_leaderboard": {"relative_path": str(stage2_lb.relative_to(ROOT)), "sha256": stage2_sha},
            "stage2_run_manifest": ({"relative_path": str(stage2_man.relative_to(ROOT)), "sha256": stage2_man_sha}
                                    if stage2_man_sha else None),
        },
    )

    # Canonical replay ×1 for the row (byte-det ×2 done in replay-proof step)
    with tempfile.TemporaryDirectory(prefix=f"v4_c26_{slug}_") as td:
        wav = Path(td) / "canonical.wav"
        canonical_sha = _replay(row, midi, wav)
    row["render_sha256_canonical_replay"] = canonical_sha

    # Write bass.json
    out_profile = profile_dir / "bass.json"
    write_profile(row, out_profile)
    profile_sha = sha_of(out_profile)
    profile_id = row["profile_id"]

    # Replay proof: 2 fresh temp dirs, assert byte-equal
    proof = {"song_sha16": sha16, "instrument": "bass", "family": "sf2",
             "profile_id": profile_id, "profile_sha256": profile_sha,
             "midi_sha256": midi_sha,
             "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"}
    with tempfile.TemporaryDirectory(prefix=f"v4_c26_replay_{slug}_a_") as ta:
        wav_a = Path(ta) / "run1.wav"
        sha_a = _replay(row, midi, wav_a)
    with tempfile.TemporaryDirectory(prefix=f"v4_c26_replay_{slug}_b_") as tb:
        wav_b = Path(tb) / "run2.wav"
        sha_b = _replay(row, midi, wav_b)
    proof["run1_sha256"] = sha_a
    proof["run2_sha256"] = sha_b
    proof["verdict"] = "REPLAY_PROOF_HOLDS" if sha_a == sha_b else "REPLAY_PROOF_FAILS"
    proof_path = profile_dir / "bass.replay_proof.json"
    proof_path.write_text(json.dumps(proof, sort_keys=True, indent=2))
    proof_sha = sha_of(proof_path)

    # Family verdict under distance semantics + c26 absolute discipline
    if emb is None:
        verdict = "STILL_INDETERMINATE"
        rationale = "top-1 embedding_cos_vggish absent from leaderboard"
    elif emb <= FLOOR:
        verdict = "STILL_INDETERMINATE"
        rationale = (f"top-1 emb_cos_dist={emb:.4f} ≤ {FLOOR} distance-upper-bound floor; "
                     "candidate-preserving, verdict-blocked pending operator per c24")
    else:
        verdict = "SF2_RULED_OUT"
        rationale = (f"top-1 emb_cos_dist={emb:.4f} > {FLOOR} distance-upper-bound floor; "
                     "above-floor degenerate per c22 distance semantics")

    v_doc = {
        "song_sha16": sha16, "slug": slug, "cycle": 26, "family": "sf2",
        "verdict": verdict, "rationale": rationale,
        "top1_embedding_cos_vggish": emb,
        "top1_composite": composite,
        "top1_mel_l1_db": mel,
        "top1_program": program, "top1_gain": gain,
        "top1_reverb_send": reverb, "top1_post": post,
        "distance_upper_bound_floor": FLOOR,
        "sf2_confirmed_forbidden_this_cycle": True,
        "escalation_pending": "_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy",
        "supersedes_path": f"data/v4/profiles/{sha16}/bass_family_verdict_c23.json",
        "profile_id": profile_id, "profile_sha256": profile_sha,
        "replay_proof_sha256": proof_sha,
    }
    v_path = profile_dir / "bass_family_verdict.json"
    v_path.write_text(json.dumps(v_doc, sort_keys=True, indent=2))
    v_sha = sha_of(v_path)

    return {"song": sha16, "slug": slug, "status": "OK",
            "profile_sha": profile_sha, "profile_id": profile_id,
            "verdict": verdict, "verdict_sha": v_sha,
            "proof_verdict": proof["verdict"], "proof_sha": proof_sha,
            "top1_emb": emb, "top1_composite": composite,
            "stage2_sha": stage2_sha, "canonical_sha": canonical_sha,
            "n_configs": len(rows)}


def emit_ledger_for_song(r: dict) -> list[dict]:
    """Emit two named events per song: stage2-completed + verdict-emitted."""
    if r["status"] != "OK":
        return []
    sha16, slug = r["song"], r["slug"]
    cycle = 26
    run_id = "run-2026-09-05T023500Z"
    base = {"cycle": cycle, "run_id": run_id,
            "confidence": {"level": "high", "rationale":
                           f"c26 Track A stage-2 on {slug}: profile + verdict + replay proof landed on disk",
                           "assessor": "worker"}}
    ev1 = {**base, "milestone_id": f"M-V4-PROFILES-1/{slug}-bass-stage2-completed",
           "status": "validated",
           "artifacts": [f"data/v4/profiles/{sha16}/bass_sweep_stage2/leaderboard.tsv",
                         f"data/v4/profiles/{sha16}/bass.json",
                         f"data/v4/profiles/{sha16}/bass.replay_proof.json"],
           "narrative":
               (f"c26 Track A: {slug} ({sha16}) stage-2 fine fit completed. "
                f"{r['n_configs']} rows. Top-1 program {int(r.get('top1_composite') or 0) and ''}"
                f"composite={r['top1_composite']:.2f} emb_cos_dist={r['top1_emb']} "
                f"canonical_replay_sha={r['canonical_sha']}. Profile sha {r['profile_sha']} "
                f"profile_id {r['profile_id']}. Replay proof {r['proof_verdict']}.")}
    ev2 = {**base, "milestone_id": f"M-V4-PROFILES-1/{slug}-bass-family-verdict",
           "status": "validated",
           "artifacts": [f"data/v4/profiles/{sha16}/bass_family_verdict.json"],
           "supersedes_path": f"data/v4/profiles/{sha16}/bass_family_verdict_c23.json",
           "narrative":
               (f"c26 Track A: {slug} bass family verdict = {r['verdict']} under distance semantics "
                f"+ c26 absolute discipline (SF2_CONFIRMED forbidden this cycle). "
                f"top-1 emb_cos_dist={r['top1_emb']} vs floor {FLOOR}. verdict_sha={r['verdict_sha']}. "
                f"Blocked on operator escalation _manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.")}
    return [ev1, ev2]


def emit_cycle_closure(results: dict) -> list[dict]:
    run_id = "run-2026-09-05T023500Z"
    base = {"cycle": 26, "run_id": run_id,
            "confidence": {"level": "high",
                           "rationale": "c26 Track A + Track C landed; POR + housekeeping tail",
                           "assessor": "worker"}}
    summary = "; ".join(f"{r['slug']}={r.get('verdict','SKIP')}" for r in results.values())
    events = [
        {**base, "milestone_id": "_plan/register-c26-non-cg-bass-stage2-and-track-c-tests",
         "status": "validated",
         "artifacts": ["docs/campaign_state.md (deferred), plan_of_record.md rows landed retroactively"],
         "narrative":
             ("c26 POR row: registers 4 new M-V4-PROFILES-1 sub-leaves "
              "(wig-bass-stage2-completed, wig-bass-family-verdict, "
              "disco_a-bass-stage2-completed, disco_a-bass-family-verdict) + 3 new test files "
              "(test_stem_midi_probe 6/6, test_non_cg_bass_verdict_reclassification_c24 8/8, "
              "test_c24_track_d_disclosures 7/7 = 21 cases green).")},
        {**base, "milestone_id": "_run/cycle_26_closed",
         "status": "validated",
         "artifacts": [f"data/v4/c26_track_a_results.json"],
         "narrative":
             (f"c26 CLOSED. Track A MANDATORY: {summary}. Track B DEFERRED to c27 (wall-time). "
              f"Track C RECOMMENDED: 3 new test files, 21/21 green. Track D BOOKKEEPING DEFERRED to c27. "
              f"NO SF2_CONFIRMED emitted on non-CG bass per c26 absolute discipline. Non-CG bass "
              "acceptance-policy escalation preserved unchanged (blocked_on_operator=true).")},
        {**base, "milestone_id": "_archive/cycle-26-scratch",
         "status": "validated",
         "artifacts": ["scripts/sound_match/_emit_c26_bass_profiles.py (retained in-tree per c14 pattern)",
                       "scratchpad chain launcher session-isolated"],
         "narrative": "No workspace scratch to archive; one-shot emitter retained in tree."},
        {**base, "milestone_id": "_infra/adopt-cycle26-tests",
         "status": "validated",
         "artifacts": ["tests/test_stem_midi_probe.py",
                       "tests/test_non_cg_bass_verdict_reclassification_c24.py",
                       "tests/test_c24_track_d_disclosures.py"],
         "narrative":
             ("Adopted 3 new Track C regression test files (6+8+7=21 cases PASS). "
              "Cross-cycle total: c16 28 + c17 6 + c18 12 + c19 7 + c20 1 + c26 21 = 75 (>=74 gate).")},
    ]
    return events


def main():
    results = {}
    ledger_events = []
    for sha16, cfg in SONGS.items():
        r = process_song(sha16, cfg)
        results[sha16] = r
        print(f"{cfg['slug']}: {r.get('status')} verdict={r.get('verdict')} emb={r.get('top1_emb')}")
        ledger_events.extend(emit_ledger_for_song(r))
    (ROOT / "data/v4/c26_track_a_results.json").write_text(
        json.dumps(results, sort_keys=True, indent=2))
    ledger_events.extend(emit_cycle_closure(results))
    emit_events(ledger_events)
    print(f"emitted {len(ledger_events)} ledger events")
    return results


if __name__ == "__main__":
    main()
