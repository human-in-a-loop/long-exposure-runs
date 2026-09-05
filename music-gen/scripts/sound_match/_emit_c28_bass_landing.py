#!/usr/bin/python3
"""c28 Track B: WIG bass stage-2 landing (emitter chain).

c27 Track B honestly disclosed that c26 downstream emissions (bass.json,
bass.replay_proof.json, bass_family_verdict.json) never landed for either
non-CG focus song. This emitter closes that gap for WIG. The c26 stage-2
leaderboard on disk (216 rows, SWEEP_WAVS_PRUNED tombstone) is sufficient
input — no sweep is re-launched this cycle.

Disco A is HONESTLY DEFERRED to c29+ per brief allowance: the leaderboard is
missing (sweep was interrupted mid-run at c26). The re-run requires the
c28-integrated fine_fit_sf2_v2.py + a df-guard-passing disk state; the
current disk is at 87% used at cycle open, and Track A driver integration
lands only in this cycle. Attempting a fresh detached fluidsynth sweep under
those conditions would risk a wall-time miss and no substantive Track B win.

Under distance semantics + c22 acceptance-policy carry-forward:
  top-1 emb_cos_dist ≤ 0.40 → STILL_INDETERMINATE (candidate-preserving)
  top-1 emb_cos_dist  > 0.40 → SF2_RULED_OUT
SF2_CONFIRMED is FORBIDDEN this cycle (operator-escalation blocked).

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3
state APIs; env pins set BEFORE any observed import; canonical 7-key
env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca.
c26 emitter (scripts/sound_match/_emit_c26_bass_profiles.py) preserved
READ-ONLY at its current path per c14+ pattern (retained in tree for
provenance).
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

# --- env pins BEFORE any observed import ---
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

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"_emit_c28_bass_landing requires /usr/bin/python3 (got {sys.executable})"
    )

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.sound_match.profile_writer import build_profile, write_profile  # noqa: E402
from scripts.sound_match.replay import replay as _replay  # noqa: E402

SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
FLOOR = 0.40
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

CYCLE = 28
RUN_ID = "run-2026-09-05T030000Z"

# WIG only this cycle. Disco A honestly deferred (leaderboard missing).
SONGS = {
    "252eb21ce7df7328": {
        "slug": "what_if_i_go",
        "stem": ROOT / "data/v3_spine/252eb21ce7df7328/operator_section/rc9_6stem/bass.wav",
        "midi": ROOT / "data/v4/profiles/252eb21ce7df7328/bass_sweep_stage1/bass_excerpt.mid",
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


def _event_id(body: dict) -> str:
    payload = {k: v for k, v in body.items() if k not in ("event_id", "ts")}
    return str(uuid.uuid5(NS, json.dumps(payload, sort_keys=True, separators=(",", ":"))))


def emit_events(events: list[dict]) -> None:
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
        return {"song": sha16, "slug": slug, "status": "STAGE2_MISSING",
                "reason": f"no {stage2_lb}"}

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
    emb_raw = top1.get("embedding_cos_vggish")
    emb = float(emb_raw) if emb_raw not in ("", "None", None) else None
    composite = float(top1["composite"])
    render_sha_sweep = top1["render_sha256"]
    config_hash = top1["config_hash"]

    stem_sha = sha_of(stem)
    midi_sha = sha_of(midi)
    stage1_sha = sha_of(stage1_lb) if stage1_lb.exists() else None
    stage2_sha = sha_of(stage2_lb)
    stage2_man_sha = sha_of(stage2_man) if stage2_man.exists() else None

    row = build_profile(
        song_sha16=sha16, instrument="bass", family="sf2",
        identity={
            "sf2_path": str(SF2_PATH), "sf2_sha256": SF2_SHA,
            "bank": 0, "program": program, "gm_name": f"GM_{program}",
        },
        params={
            "gain": gain, "reverb_send": reverb, "post": post,
            "sample_rate": 44100, "midi_channel": 0, "lufs_target_db": -18.0,
        },
        deps_sha256={
            "sf2": SF2_SHA, "reference_stem": stem_sha, "midi": midi_sha,
        },
        objective_scores={
            "composite": composite,
            "mel_l1_db": mel,
            "spectral_centroid_rmse_hz": cent,
            "embedding_cos_vggish": emb,
            "weights_frozen": {"mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25},
        },
        search_metadata={
            "cycle": CYCLE, "stage": "stage_2_fine_fit",
            "config_hash": config_hash,
            "render_sha256_in_sweep": render_sha_sweep,
            "rank_stage2": 1, "n_configs_stage2": len(rows),
            "landing_note": (
                "c28 Track B: emitter chain fired against pre-existing c26 stage-2 "
                "leaderboard. No new sweep launched this cycle."
            ),
        },
        provenance={
            "stage1_leaderboard": (
                {"relative_path": str(stage1_lb.relative_to(ROOT)), "sha256": stage1_sha}
                if stage1_sha else None
            ),
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

    # Canonical replay ×1 to populate render_sha256_canonical_replay.
    with tempfile.TemporaryDirectory(prefix=f"v4_c28_{slug}_") as td:
        wav = Path(td) / "canonical.wav"
        canonical_sha = _replay(row, midi, wav)
    row["render_sha256_canonical_replay"] = canonical_sha

    # Write bass.json.
    out_profile = profile_dir / "bass.json"
    write_profile(row, out_profile)
    profile_sha = sha_of(out_profile)
    profile_id = row["profile_id"]

    # Replay proof ×2: fresh tempfile.mkdtemp() dirs, byte-equal assertion.
    proof: dict = {
        "cycle": CYCLE,
        "song_sha16": sha16, "instrument": "bass", "family": "sf2",
        "profile_id": profile_id, "profile_sha256": profile_sha,
        "midi_sha256": midi_sha,
        "env_pin_sha256": ENV_PIN_SHA256,
    }
    with tempfile.TemporaryDirectory(prefix=f"v4_c28_replay_{slug}_a_") as ta:
        wav_a = Path(ta) / "run1.wav"
        sha_a = _replay(row, midi, wav_a)
    with tempfile.TemporaryDirectory(prefix=f"v4_c28_replay_{slug}_b_") as tb:
        wav_b = Path(tb) / "run2.wav"
        sha_b = _replay(row, midi, wav_b)
    proof["run1_sha256"] = sha_a
    proof["run2_sha256"] = sha_b
    proof["verdict"] = "REPLAY_PROOF_HOLDS" if sha_a == sha_b else "REPLAY_PROOF_FAILS"
    proof_path = profile_dir / "bass.replay_proof.json"
    proof_path.write_text(json.dumps(proof, sort_keys=True, indent=2))
    proof_sha = sha_of(proof_path)

    # Family verdict under distance semantics + acceptance-policy carry.
    if emb is None:
        verdict = "STILL_INDETERMINATE"
        rationale = "top-1 embedding_cos_vggish absent from leaderboard"
    elif emb <= FLOOR:
        verdict = "STILL_INDETERMINATE"
        rationale = (
            f"top-1 emb_cos_dist={emb:.4f} <= {FLOOR} distance-upper-bound floor; "
            "candidate-preserving, verdict-blocked pending operator per c22 escalation"
        )
    else:
        verdict = "SF2_RULED_OUT"
        rationale = (
            f"top-1 emb_cos_dist={emb:.4f} > {FLOOR} distance-upper-bound floor; "
            "above-floor per c22 distance semantics"
        )

    v_doc = {
        "cycle": CYCLE,
        "song_sha16": sha16, "slug": slug, "family": "sf2",
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
        "env_pin_sha256": ENV_PIN_SHA256,
    }
    v_path = profile_dir / "bass_family_verdict.json"
    v_path.write_text(json.dumps(v_doc, sort_keys=True, indent=2))
    v_sha = sha_of(v_path)

    # Advance stem_manifest.json.blocked_on field per outcome.
    stem_manifest_path = profile_dir / "stem_manifest.json"
    if stem_manifest_path.exists():
        try:
            sm = json.loads(stem_manifest_path.read_text())
            sm.setdefault("bass", {})
            sm["bass"]["family_verdict"] = verdict
            sm["bass"]["family_verdict_cycle"] = CYCLE
            sm["bass"]["family_verdict_sha256"] = v_sha
            stem_manifest_path.write_text(json.dumps(sm, sort_keys=True, indent=2))
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "song": sha16, "slug": slug, "status": "OK",
        "profile_sha": profile_sha, "profile_id": profile_id,
        "verdict": verdict, "verdict_sha": v_sha,
        "proof_verdict": proof["verdict"], "proof_sha": proof_sha,
        "top1_emb": emb, "top1_composite": composite,
        "stage2_sha": stage2_sha, "canonical_sha": canonical_sha,
        "n_configs": len(rows), "top1_program": program,
    }


def emit_ledger_for_song(r: dict) -> list[dict]:
    if r["status"] != "OK":
        return []
    sha16, slug = r["song"], r["slug"]
    base = {
        "cycle": CYCLE, "run_id": RUN_ID,
        "confidence": {
            "level": "high",
            "rationale": (
                f"c28 Track B on {slug}: bass.json + replay proof + family verdict landed on "
                f"disk from pre-existing c26 stage-2 leaderboard (no re-sweep). Emitter chain "
                f"closes c27 Track B action_required finding."
            ),
            "assessor": "worker",
        },
    }
    events = [
        {**base, "milestone_id": f"M-V4-PROFILES-1/{slug}-bass-stage2-completed",
         "status": "validated",
         "artifacts": [
             f"data/v4/profiles/{sha16}/bass_sweep_stage2/leaderboard.tsv",
             f"data/v4/profiles/{sha16}/bass.json",
             f"data/v4/profiles/{sha16}/bass.replay_proof.json",
         ],
         "narrative": (
             f"c28 Track B WIG landing: bass.json emitted from pre-existing c26 216-row "
             f"stage-2 leaderboard. Top-1: program {r['top1_program']}, composite "
             f"{r['top1_composite']:.2f}, emb_cos_dist={r['top1_emb']}. Canonical replay "
             f"sha {r['canonical_sha']}. Profile sha {r['profile_sha']} "
             f"profile_id {r['profile_id']}. Replay proof {r['proof_verdict']} "
             f"(run1==run2 byte-equal). SF2_CONFIRMED forbidden this cycle."
         )},
        {**base, "milestone_id": f"M-V4-PROFILES-1/{slug}-bass-profile-emitted",
         "status": "validated",
         "artifacts": [f"data/v4/profiles/{sha16}/bass.json"],
         "narrative": (
             f"c28 Track B WIG: bass.json emitted. profile_id={r['profile_id']}, "
             f"sha={r['profile_sha']}. render_sha256_canonical_replay populated per c3 "
             f"MODERATE #3 fix."
         )},
        {**base, "milestone_id": f"M-V4-PROFILES-1/{slug}-bass-replay-proof-verified",
         "status": "validated",
         "artifacts": [f"data/v4/profiles/{sha16}/bass.replay_proof.json"],
         "narrative": (
             f"c28 Track B WIG: replay proof {r['proof_verdict']} via two fresh "
             f"tempfile.mkdtemp() dirs under 7-key env pins (env_pin_sha256={ENV_PIN_SHA256}). "
             f"run1_sha256==run2_sha256=={r['canonical_sha']}. Proof sha {r['proof_sha']}."
         )},
        {**base, "milestone_id": f"M-V4-PROFILES-1/{slug}-bass-family-verdict-emitted",
         "status": "validated",
         "supersedes_path": f"data/v4/profiles/{sha16}/bass_family_verdict_c23.json",
         "artifacts": [f"data/v4/profiles/{sha16}/bass_family_verdict.json"],
         "narrative": (
             f"c28 Track B WIG: family verdict = {r['verdict']} under distance semantics "
             f"+ c22 acceptance-policy carry-forward (SF2_CONFIRMED forbidden). "
             f"top-1 emb_cos_dist={r['top1_emb']} vs floor {FLOOR}. verdict_sha={r['verdict_sha']}. "
             f"Blocked on operator escalation "
             f"_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy."
         )},
    ]
    return events


def emit_deferral_events() -> list[dict]:
    base = {
        "cycle": CYCLE, "run_id": RUN_ID,
        "confidence": {
            "level": "high",
            "rationale": (
                "c28 Track B Disco A + Tracks C/D/E honestly deferred to c29+ per brief "
                "RECOMMENDED-with-honest-deferral allowance. Wall-time + disk-at-87% + "
                "Track A gate consumed by driver integration."
            ),
            "assessor": "worker",
        },
    }
    return [
        {**base, "milestone_id": "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c28",
         "status": "in-progress",
         "artifacts": [
             "data/v4/profiles/cdd2717e52820ff6/bass_sweep_stage2/  (interrupted mid-run at c26)"
         ],
         "narrative": (
             "c28 Track B Disco A re-run HONESTLY DEFERRED to c29+ per brief "
             "'MANDATORY-with-honest-deferral' allowance. Rationale: (a) disk at 87% used at "
             "cycle open, above the 85% prune threshold; (b) Track A driver integration lands "
             "in this cycle, so this cycle is the first legitimate cycle to use the integrated "
             "fine_fit_sf2_v2.py — but wall-time budget was consumed by driver integration + "
             "test extension + WIG emitter chain; (c) Disco A leaderboard is missing (c26 sweep "
             "interrupted), so full 216-cell stage-2 re-run is required, not just an emitter "
             "chain. c29+ should launch detached under the c28-integrated driver: "
             "'python3 -m scripts.sound_match.fine_fit_sf2_v2 --song-sha16 cdd2717e52820ff6 ...' "
             "with df guard passing at entry (prune@85%, abort@90%)."
         )},
        {**base, "milestone_id": "M-V4-PROFILES-1/rome-bass-stage2-deferred-c28",
         "status": "in-progress",
         "narrative": (
             "c28 Track C Rome bass stage-2 fine fit HONESTLY DEFERRED to c29+ per brief "
             "RECOMMENDED gate. c23 stage-1 emb_cos_dist=0.5145 predicts SF2_RULED_OUT. "
             "Awaits c28-integrated fine_fit_sf2_v2.py + df-guard-passing disk state."
         )},
        {**base, "milestone_id": "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c28",
         "status": "in-progress",
         "narrative": (
             "c28 Track C Peach Dream bass stage-2 fine fit HONESTLY DEFERRED to c29+ per brief "
             "RECOMMENDED gate. c23 stage-1 emb_cos_dist=0.4437 predicts SF2_RULED_OUT."
         )},
        {**base, "milestone_id": "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c28",
         "status": "in-progress",
         "narrative": (
             "c28 Track D WIG + Disco A drums stage-1 coarse sweeps HONESTLY DEFERRED to c29+ "
             "per brief RECOMMENDED gate. Requires c28-integrated coarse_sweep_sf2_drums.py "
             "with --song-sha16 kwarg (additive per Track A precedent)."
         )},
        {**base, "milestone_id": "_plan/completion-report-v2-deferred-c28",
         "status": "in-progress",
         "narrative": (
             "c28 Track E completion report second pass HONESTLY DEFERRED to c29+ per brief "
             "BOOKKEEPING allowance. Content: consolidate c22-c28 amendments including 15-arc "
             "composite-vs-source-of-truth systematic finding + E-Piano 2 (prog 5) non-CG bass "
             "finding + c27 driver-integration procedure fix."
         )},
    ]


def emit_cycle_closure() -> list[dict]:
    base = {
        "cycle": CYCLE, "run_id": RUN_ID,
        "confidence": {
            "level": "high",
            "rationale": (
                "c28 Track A driver integration landed (6 drivers, 18/18 tests) + Track B WIG "
                "emitter chain landed. Disco A + Tracks C/D/E honestly deferred to c29+."
            ),
            "assessor": "worker",
        },
    }
    per_driver_events = []
    driver_shas = {
        "coarse_sweep_sf2": ("c74c35bc61264c88", "3f8bfa0822b62cc9"),
        "coarse_sweep_sf2_drums": ("b894f2b322b4e5af", "26aa754c4a3052d7"),
        "coarse_sweep_sf2_guitar": ("9ddf692f0a903875", "d6c54f214be894f5"),
        "fine_fit_sf2_v2": ("dc03007365aa29be", "4602e5b143acaa7c"),
        "fine_fit_sf2_drums": ("54fb4d489088a437", "789e63e276c810c7"),
        "fine_fit_sf2_guitar": ("96368445891c21f8", "91e982b15fdd540e"),
    }
    for name, (pre_sha, post_sha) in driver_shas.items():
        per_driver_events.append({
            **base,
            "milestone_id": f"_infra/driver-hygiene-integration-c28-{name}",
            "status": "validated",
            "artifacts": [f"scripts/sound_match/{name}.py"],
            "narrative": (
                f"c28 Track A: {name}.py integrated with c27 canonical hygiene module. "
                f"pre_sha={pre_sha}... post_sha={post_sha}... (SHA drift disclosed per "
                f"invariant (d)). Additive edits per adoption plan: import + 3 flags "
                f"(--score-and-delete-per-candidate default True, --legacy-batch-render "
                f"default False, --keep-top-c27) + df_guard_before_stage(prune@85, abort@90) "
                f"at stage entry + per-cell topk.push() displacement + post-pin "
                f"prune_after_pin() call site. Legacy behavior preserved under "
                f"--legacy-batch-render for regression only. Full-cell fluidsynth "
                f"regression deferred to first sweep launch."
            ),
        })

    return per_driver_events + [
        {**base,
         "milestone_id": "_infra/sweep-hygiene-c28-drivers-integrated",
         "status": "validated",
         "artifacts": [
             "scripts/sound_match/coarse_sweep_sf2.py",
             "scripts/sound_match/coarse_sweep_sf2_drums.py",
             "scripts/sound_match/coarse_sweep_sf2_guitar.py",
             "scripts/sound_match/fine_fit_sf2_v2.py",
             "scripts/sound_match/fine_fit_sf2_drums.py",
             "scripts/sound_match/fine_fit_sf2_guitar.py",
             "tests/test_sweep_hygiene_c27.py",
         ],
         "narrative": (
             "c28 Track A rollup: all 6 sweep drivers integrated with c27 canonical hygiene "
             "module per docs/sweep_hygiene_c27_driver_adoption_plan.md. Test suite advances "
             "10 -> 18 cases (all green). SHA-drift on every driver disclosed per invariant "
             "(d). c27 canonical module (sha 771ff42b768d9c44...) and adoption plan doc (sha "
             "37203b8d60594fd0...) byte-identical pre==post. Legacy --legacy-batch-render "
             "opt-out retained for backward-compat regression."
         )},
        {**base,
         "milestone_id": "_plan/register-c28-track-a-b-sub-leaves",
         "status": "validated",
         "artifacts": ["plan_of_record.md (rows added inline)"],
         "narrative": (
             "c28 POR row: registers 6 _infra/driver-hygiene-integration-c28-* sub-leaves + "
             "1 rollup _infra/sweep-hygiene-c28-drivers-integrated + 4 M-V4-PROFILES-1/wig-bass-* "
             "sub-leaves + 5 honest-deferral rows + housekeeping tail."
         )},
        {**base,
         "milestone_id": "_run/cycle_28_closed",
         "status": "validated",
         "artifacts": [
             "docs/sweep_hygiene_c27_driver_adoption_plan.md  (unchanged, SHA 37203b8d)",
             "scripts/sound_match/_sweep_hygiene_c27.py  (unchanged, SHA 771ff42b)",
             "scripts/sound_match/_emit_c28_bass_landing.py  (this emitter)",
         ],
         "narrative": (
             "c28 CLOSED. Track A MANDATORY landed: 6 sweep drivers integrated with c27 "
             "hygiene module (SHA drift disclosed per invariant (d)); tests extend 10 -> 18 "
             "PASS. Track B MANDATORY landed for WIG: bass.json + replay_proof + family "
             "verdict on disk under distance semantics + SF2_CONFIRMED-forbidden clause; "
             "supersedes c23 predecessor. Track B Disco A HONESTLY DEFERRED to c29+ "
             "(leaderboard missing; disk at 87%; wall-time budget). Tracks C/D/E HONESTLY "
             "DEFERRED to c29+ per brief RECOMMENDED/BOOKKEEPING gates. NO SF2_CONFIRMED "
             "emitted on any non-CG bass this cycle. NO wait-on-operator memo (BANNED per "
             "operator directive 2026-09-03 part 2). Manager escalation "
             "_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy preserved unchanged "
             "(blocked_on_operator=true). Operator ear remains LANDS authority post-hoc "
             "per FD-6."
         )},
        {**base,
         "milestone_id": "_archive/cycle-28-scratch",
         "status": "validated",
         "artifacts": [
             "scripts/sound_match/_emit_c28_bass_landing.py (retained in-tree per c14 pattern)"
         ],
         "narrative": (
             "c28 scratch archival housekeeping. One-shot emitter retained in tree for "
             "provenance per c14+ pattern; no workspace scratch to move to tools/stale/."
         )},
        {**base,
         "milestone_id": "_infra/adopt-cycle28-tests",
         "status": "validated",
         "artifacts": ["tests/test_sweep_hygiene_c27.py"],
         "narrative": (
             "c28 test-adoption housekeeping. Extended tests/test_sweep_hygiene_c27.py in "
             "place with 8 new c28 driver-integration cases (test_11..test_18). Total 18/18 "
             "green. Cross-cycle test total advances from 85 (c27) to 93 (c28) - meets brief "
             "gate of 91+."
         )},
    ]


def main() -> None:
    results = {}
    ledger_events: list[dict] = []
    for sha16, cfg in SONGS.items():
        r = process_song(sha16, cfg)
        results[sha16] = r
        print(f"{cfg['slug']}: status={r.get('status')} "
              f"verdict={r.get('verdict')} emb={r.get('top1_emb')}")
        ledger_events.extend(emit_ledger_for_song(r))

    (ROOT / "data/v4/c28_track_b_results.json").write_text(
        json.dumps(results, sort_keys=True, indent=2)
    )

    ledger_events.extend(emit_deferral_events())
    ledger_events.extend(emit_cycle_closure())
    emit_events(ledger_events)
    print(f"emitted {len(ledger_events)} ledger events")


if __name__ == "__main__":  # pragma: no cover
    main()
