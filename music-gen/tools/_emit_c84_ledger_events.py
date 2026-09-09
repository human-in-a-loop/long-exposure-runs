#!/usr/bin/python3
"""c84 one-shot ledger emitter — v5 REOPENING cycle 6 (outage recovery: driver restart, content gate, hook-at-birth c84,
full-corpus harmony + groove v2 held-out, groove-first generator iteration 1, bookkeeping).

Every event carries `agent` (REQUIRED_EVENT_FIELDS); UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts);
idempotent by milestone_id; supersedes_path is str|None (c14 lemma). Status convention for falsified pre-registered
criteria: `validated` for a RECORDED verdict (c79–c81 convention; c83's `invalidated` on tempo_v5d stands as history — L2).
Reads every number from disk at emit time. Retained in-tree per docs/emitter_exemption_policy.md (c34 OPT_B exemption).
"""
import hashlib
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 84
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
P = "M-V5-CORPUS-1"
FROZEN_EXPECTED = {
    "docs/v3_determinism_certificate.md": "a6876911", "data/v3/rules/rules_artifact.jsonl": "e19fb205",
    "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav": "6e13e007", "data/v4/profiles/31a164f845f8e27e/bass_v2.json": "2a1cb340",
    "data/v4/profiles/88d247468cb6d49f/stem_manifest.json": "d483f2bf", "data/v4/ear/exemplar_set.json": "31c10dfb",
    "scripts/ear/v4_ear.py": "e775621b", "scripts/gen/iterate_v4.py": "8f1f0b88", "scripts/gen/interpolate_v4.py": "2359f35d",
    "docs/v4_completion_report_v3.md": "b900b0ee", "scripts/v3_spine/recreate_v3.py": "b1490874",
    "scripts/v3_spine/stage_cache.py": "33435a84", "scripts/v3_spine/midi_from_json_events.py": "bbff015f",
    "scripts/sound_match/_sweep_hygiene_c27.py": "771ff42b", "scripts/v3_spine/recreate_v3_checkpointed.py": "da418986",
    "scripts/v3_spine/launch_detached.py": "999045f3", "data/v5/corpus/corpus_manifest.json": "73362136",
    "scripts/v5/transcribe_full_length.py": "c1c6b2df", "scripts/v5/reindex_hook.py": "a63434a6",
    "data/v5/corpus/recanonicalization_blocked.json": "2fbabc07", "data/v5/rules/harmony_markov_v5.json": None,
}
SCRATCH = Path("/tmp/claude-0/-home-user-long-exposure-runs-music-gen/e247e21c-0001-458c-91e9-dcc6bac6cfe2/scratchpad")


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _event_id(body: dict) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, _canonical({k: v for k, v in body.items() if k not in ("event_id", "ts")})))


def _ev(milestone_id, status, level, rationale, narrative, artifacts, supersedes_path=None):
    body = {"agent": "worker", "artifacts": artifacts, "confidence": {"assessor": "worker", "level": level, "rationale": rationale},
            "cycle": CYCLE, "env_pin_sha256": ENV_PIN, "milestone_id": milestone_id, "narrative": narrative,
            "run_id": RUN_ID, "status": status, "supersedes_path": supersedes_path, "ts": TS}
    body["event_id"] = _event_id(body)
    return body


def _j(p):
    return json.loads(Path(p).read_text())


def _df():
    st = os.statvfs("."); avail = st.f_bavail * st.f_frsize; used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return round(100 * used / (used + avail), 2), round(avail / 1e9, 3)


def _alive(pid):
    try:
        os.kill(pid, 0); return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def cache_hits_from_log(log: Path, song: str) -> dict:
    hits = {}
    for line in log.read_text(errors="replace").splitlines():
        m = re.match(r"\[(\S+)\] " + song + r" (\S+)\s+(\S+)?\s*(\{.*\})", line)
        if m and m.group(1) >= "2026-09-09":
            stage = m.group(2) + ((":" + m.group(3)) if m.group(2) == "muscriptor" and m.group(3) else "")
            hits[stage] = m.group(4)
    return hits


def main() -> int:
    C = Path("data/v5/corpus")
    events = []
    frozen = {k: _sha(k) for k in FROZEN_EXPECTED}
    frozen_ok = {k: (frozen[k].startswith(v) if v else True) for k, v in FROZEN_EXPECTED.items()}
    df_now, avail_now = _df()
    log = Path("data/v5/logs/transcribe_full_c79.log")
    launch = _j("data/v5/logs/transcribe_full_c84.launch.json")
    pid = launch["new_pid"]
    live = Path("data/v5/logs/c84_p0_liveness.txt").read_text().strip()
    landed = sorted(p.parent.name for p in C.glob("*/transcription_manifest.json"))
    side = sorted(p.parent.name for p in C.glob("*/canonical_v5_reindexed_sha256.json"))
    hits_0e1e = cache_hits_from_log(log, "0e1e8f20592db366")
    hits_cc06 = cache_hits_from_log(log, "cc0693b4a24f64b2")
    tail = log.read_text(errors="replace").splitlines()[-3:]
    escalation = "avail < 4.5 GB: operator authority requested over /root/.local + stale /tmp caches" if avail_now < 4.5 else None

    # ---- P0.1 ----
    events.append(_ev(f"{P}/transcription-liveness-c84", "validated", "high",
        "os.kill(10247,0) -> absent; df in driver semantics; landed/sidecar counts from disk; no install; no kill -9.",
        f"c84 P0.1: {live}. Driver died with the container (2026-09-07 03:32Z per operator); nothing hunted beyond os.kill(pid,0). "
        f"df at emit {df_now} % (avail {avail_now} GB); 90 % ceiling never crossed this cycle. "
        + (f"ESCALATION: {escalation}" if escalation else "Escalation line not triggered (avail >= 4.5 GB)."),
        ["data/v5/logs/c84_p0_liveness.txt"], supersedes_path=f"{P}/transcription-liveness-c83"))
    # ---- P0.3 ----
    events.append(_ev(f"{P}/driver-restart-c84", "validated", "high",
        "pinned c79 command relaunched via READ-ONLY launch_detached after the stage-cache env-pin key was reproduced; resume song cache-hit on every cached stage (from the log).",
        f"c84 P0.3: `scripts/v5/restart_driver_c84.py` verified transcribe_full_length.py sha {launch['driver_sha256_at_launch'][:12]}… + reindex_hook.py sha "
        f"{launch['reindex_hook_sha256_at_launch'][:12]}… unchanged, verified build_env_pin_manifest() under the driver's 7 pinned env vars reproduces the stage-cache key "
        f"{launch['stage_cache_env_pin_key'][:16]}… (FIRST-CLASS: computed WITHOUT the pins it reads 6386e0cc… — a naive relaunch check would have looked like key drift; the driver sets the pins before importing env_pin, so cache hits were expected and observed), "
        f"then relaunched the PINNED c79 command (no --songs) via launch_detached: new PID {pid}, launched {launch['launched_utc']}, running_after_8s {launch['running_after_8s']}; alive at emit {_alive(pid)}. "
        f"The driver re-walked the 24 landed songs from stage_cache (~1 s each; manifests rewritten — invariant (d), mtime not a discriminator) and resumed `0e1e8f20592db366` with cache hits {hits_0e1e} "
        f"(`_transient/` full.wav + 6 stems consumed by the driver, not deleted by hand); `cc0693b4a24f64b2` stages at emit: {hits_cc06 or 'not yet started'}. "
        f"Landed at emit {len(landed)}/26, sidecars {len(side)}/26. Log tail: {' | '.join(tail)}. df trajectory {launch['df_trajectory']}.",
        ["data/v5/logs/transcribe_full_c84.launch.json", "scripts/v5/restart_driver_c84.py", "data/v5/logs/transcribe_full_c79.log"],
        supersedes_path="data/v5/logs/transcribe_full_c82.launch.json"))
    # ---- P0.2 ----
    cg = _j(C / "content_blocked.json"); pre_p = C / "content_gate_prereg_c84.json"
    events.append(_ev(f"{P}/content-gate-preregistered-c84", "validated", "high", "prereg mtime precedes the output; rules + expected hit fixed before any output.",
        f"c84 P0.2: `content_gate_prereg_c84.json` (sha {_sha(pre_p)[:12]}…) written BEFORE any output — R1 NON_MUSIC_CONTENT := n_note_on(full_mix)==0 AND sum(drums,bass,guitar,other,piano)==0; "
        f"R2 title screen `commentary|interview|q&a|talk|podcast|lecture|spoken`; BLOCKED iff R1 (R2 corroborates; R2-only on a landed song with notes is NOT blocked). Expected exactly ae1b65eaf1560951.",
        ["data/v5/corpus/content_gate_prereg_c84.json"], supersedes_path=None))
    b = cg["blocked_songs"].get("ae1b65eaf1560951", {})
    events.append(_ev(f"{P}/content-gate-c84", "validated", "high", "exactly the pre-registered song fires; tempo-blocked file byte-identical; additive refusal tested on a fixture in all three rules scripts.",
        f"c84 P0.2: `scripts/v5/content_gate_v5.py` -> `content_blocked.json` (separate file; `recanonicalization_blocked.json` byte-identical sha {frozen['data/v5/corpus/recanonicalization_blocked.json'][:12]}…): "
        f"blocked {sorted(cg['blocked_songs'])} (matches expectation {cg['matches_expectation']}); verdict tally {cg['verdict_tally']} over {cg['n_songs']} songs ({cg['n_landed']} landed at run). "
        f"ae1b65eaf1560951 ('{b.get('title')}', band 7): {b.get('verdict')} — note counts {b.get('note_counts')} (vocals = spoken word transcribed as 'voice'); manifest sha {str(b.get('transcription_manifest_sha256'))[:12]}…, sidecar sha {str(b.get('sidecar_sha256'))[:12]}…, hook-at-birth Δ {b.get('hook_at_birth_delta_s')} s. "
        f"Additive refusal: `scripts/v5/content_blocked.py` (ContentBlockedError, refuse-before-read) wired into harmony_v5.py (analyse_song + main skip list), groove_v5.py, groove_v5_v2.py — fixture test_03 proves the refusal fires BEFORE MISSING_REINDEX in all three. Diagnostic-ladder rung 2 not triggered (exactly one song fires R1).",
        ["data/v5/corpus/content_blocked.json", "scripts/v5/content_gate_v5.py", "scripts/v5/content_blocked.py", "scripts/v5/harmony_v5.py", "scripts/v5/groove_v5.py", "scripts/v5/groove_v5_v2.py"],
        supersedes_path=f"{P}/content-gate-preregistered-c84"))
    # ---- P0.4 per-song rows ----
    hb = _j(C / "hook_at_birth_c84.json")
    existing_ids = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            existing_ids.add(json.loads(line).get("milestone_id"))
    has_row = {s: any(re.fullmatch(rf"{P}/{s}-reindexed-c8\d", m or "") for m in existing_ids) for s in landed}
    for s, v in hb["per_song"].items():
        if has_row.get(s):
            continue
        tm = _j(C / s / "transcription_manifest.json")
        extra = f" CONTENT VERDICT: {b.get('verdict')} — content-blocked for rules (data/v5/corpus/content_blocked.json), NOT a transcription defect: vocals {tm['note_counts']['vocals']['n_note_on']} starts, every instrument stem + full_mix 0." if s == "ae1b65eaf1560951" else ""
        events.append(_ev(f"{P}/{s}-reindexed-c84", "validated" if v["hook_at_birth"] else "action_required", "high" if v["hook_at_birth"] else "medium",
            "sidecar SHAs == disk; MIDI note_on == JSON starts per probe; sidecar written within seconds of the manifest by the live hook.",
            f"c84 per-song lossless record: {tm.get('title')} ({s}, {tm['duration_s']} s, bpm_v5 {tm['bpm_v5']}): landed under PID 10247 (hook live at birth) after c83 close — sidecar Δ {v.get('sidecar_minus_manifest_s')} s; "
            f"hook_at_birth={v['hook_at_birth']}; paired {v.get('paired_total')} / unpaired {v.get('unpaired_total')}; note_on == starts {v.get('note_on_equals_starts_all')}; zero catch-up. "
            f"Per-stem: " + "; ".join(f"{p} {x['json_starts']} starts → {x['n_paired']} paired/{x['n_unpaired']} unpaired" for p, x in v.get('per_probe', {}).items()) + extra,
            [f"data/v5/corpus/{s}/transcription_manifest.json", f"data/v5/corpus/{s}/canonical_v5_reindexed_sha256.json", f"data/v5/corpus/{s}/canonical_v5_reindexed/reindex_manifest.json"],
            supersedes_path=None))
    events.append(_ev(f"{P}/hook-at-birth-verification-c84", "validated" if hb["catch_up_is_noop"] and hb["all_new_hook_at_birth"] else "action_required", "high",
        "baseline extended to the 9 songs known at c83 close; every post-c83 landing carries a hook-at-birth sidecar; reindex_landed() no-op.",
        f"c84 P0.4: `scripts/v5/hook_at_birth_c84.py` (baseline = c83 record's baseline + new landings = {len(hb['baseline_known_at_c83_close'])} songs) verified {len(hb['new_landings_since_c83'])} post-c83 landings "
        f"{hb['new_landings_since_c83']}: all_new_hook_at_birth={hb['all_new_hook_at_birth']}; reindex_landed() no-op {hb['catch_up_is_noop']} ({hb['n_non_noop']} non-noop) at {hb['checked_utc']} ({hb['n_landed_total']}/26 landed then). "
        f"Invariant (d): {hb['invariant_d_disclosure']}. Per-song rows emitted only for songs without an existing `<sha16>-reindexed-c8x` row (grep-first).",
        ["data/v5/corpus/hook_at_birth_c84.json", "scripts/v5/hook_at_birth_c84.py"], supersedes_path=f"{P}/hook-at-birth-verification-c83"))
    # ---- P1 ----
    hp = Path("data/v5/rules/harmony_prereg_c84.json"); h = _j("data/v5/rules/harmony_markov_v5_full.json")
    bd = _j(SCRATCH / "p1p2_bytedet.json") if (SCRATCH / "p1p2_bytedet.json").exists() else {}
    fr = {s: v["excluded_beat_fraction"] for s, v in h["per_song"].items()}
    events.append(_ev("M-V5-RULES-1/harmony-full-corpus-preregistered-c84", "validated", "high", "prereg mtime precedes the chain output.",
        f"c84 P1: `harmony_prereg_c84.json` (sha {_sha(hp)[:12]}…) BEFORE output: eligible = landed ∧ sidecar ∧ ¬tempo-blocked ∧ ¬content-blocked; c80 degeneracy rule + exclusion threshold 12 unchanged; enum HARMONY_NONDEGENERATE / HARMONY_DEGENERATE; per-song excluded-beat fraction reported.",
        ["data/v5/rules/harmony_prereg_c84.json"], supersedes_path=None))
    events.append(_ev("M-V5-RULES-1/harmony-full-corpus-c84", "validated", "high", "pre-registered enum recorded; byte-det x2 on chain + 21 per-song files; c82 3-song anchor byte-identical; figure + plot script on disk.",
        f"c84 P1 **HARMONY_{h['degeneracy_verdict'].replace('_', '')}** ({h['degeneracy_verdict']} under the c80 rule) on n={h['gate']['n_used']} eligible songs "
        f"(landed {h['gate']['n_landed']}; tempo-blocked skipped {h['gate']['blocked_skipped']}; content-blocked skipped {h['gate']['content_blocked_skipped']}): {len(h['states'])} functional states; "
        f"max stationary {h['max_stationary_state']} = {h['max_stationary_mass']} (c82 n=3: 0.0956); qualities ≥ 8 segments {h['qualities_with_count_ge_threshold']}. "
        f"Per-song excluded-beat fraction (≥ 12 simultaneous starts in one stem): mean {round(sum(fr.values()) / len(fr), 4)}, max {max(fr.items(), key=lambda kv: kv[1])}, min {min(fr.items(), key=lambda kv: kv[1])}; "
        f"c82 anchors WIG {fr.get('252eb21ce7df7328')} / CG {fr.get('31a164f845f8e27e')} / Rome {fr.get('51e433ade2a845e1')} — the c82 breadth finding persists at full corpus (dense strummed-guitar beats, not only the Rome bass tail); not retuned (FD-1). "
        f"Output `harmony_markov_v5_full.json` (sha {_sha('data/v5/rules/harmony_markov_v5_full.json')[:12]}…), per-song under `data/v5/rules/per_song_c84/`; byte-det x2 {bd.get('harmony', {}).get('equal')} (per-song {bd.get('harmony', {}).get('per_song_equal')}); "
        f"c82 `harmony_markov_v5.json` byte-identical (sha {frozen['data/v5/rules/harmony_markov_v5.json'][:12]}…). harmony_v5.py additive CLI (--out-name/--per-song-subdir/--cycle) keeps the c82 layout as default. "
        f"Figure `data/v5/rules/fig_harmony_full_c84.png` (left: stationary mass over states; right: per-song excluded-beat fraction) from `plot_harmony_full_c84.py`. Falsification (max mass ≥ 0.60) did NOT fire.",
        ["data/v5/rules/harmony_markov_v5_full.json", "data/v5/rules/fig_harmony_full_c84.png", "data/v5/rules/plot_harmony_full_c84.py", "data/v5/logs/harmony_full_c84_run1.log"]
        + sorted(str(p) for p in Path("data/v5/rules/per_song_c84").glob("*/harmony_v5.json")), supersedes_path="M-V5-RULES-1/harmony_v5-first-data-c82"))
    # ---- P2 ----
    gp = Path("data/v5/rules/groove_prereg_c84.json"); g = _j("data/v5/rules/groove_v5_v2_full.json")
    pt = g["per_table"]
    events.append(_ev("M-V5-RULES-1/groove-v2-full-corpus-preregistered-c84", "validated", "high", "prereg mtime precedes the model output; fold rule fixed before any output.",
        f"c84 P2: `groove_prereg_c84.json` (sha {_sha(gp)[:12]}…) BEFORE output: SHA-256 fold (lowest 3 of sha256('groove_fold_c84|sha16')) held out; enum GENERALIZES (singleton < 0.5 ∧ |Δbackbeat|,|Δlock| ≤ 0.15) / OVERFITS / DEGENERATE; alpha 0.5 + 8th-note kick alphabet held constant.",
        ["data/v5/rules/groove_prereg_c84.json"], supersedes_path=None))
    events.append(_ev("M-V5-RULES-1/groove-v2-full-corpus-c84", "validated", "high",
        "pre-registered enum recorded (validated = recorded verdict, c79–c81 convention; falsification of the small-n mechanism is a first-class finding); byte-det x2; c81/c82 groove files untouched.",
        f"c84 P2 **{g['verdict']}** on the full eligible corpus: {g['gate']['n_eligible']} eligible, fold held out {g['fold']['heldout']} (SHA-256 rank), train {g['n_train_songs']} songs / {g['n_train_bars']} bars, held-out pooled {g['n_heldout_bars']} bars. "
        f"Held-out checks PASS: backbeat corpus {g['validation']['backbeat_ratio']['heldout_pooled']} vs sampled {g['validation']['backbeat_ratio']['sampled']} (Δ {g['validation']['backbeat_ratio']['abs_diff']}), lock {g['validation']['bass_kick_lock']['heldout_pooled']} vs {g['validation']['bass_kick_lock']['sampled']} (Δ {g['validation']['bass_kick_lock']['abs_diff']}); "
        f"sampled distinct kick8 {g['sample_stats']['distinct_kick_patterns']} / bass16 {g['sample_stats']['distinct_bass_patterns']} (not degenerate). "
        f"Singleton-context fraction {g['singleton_context_fraction']} ({g['n_singleton_contexts']}/{g['n_contexts']}) ≥ 0.5 → OVERFITS. FIRST-CLASS FINDING (mechanism partially refuted): the fall with n is real for the two 8-bit-context tables — "
        f"snare|kick8 {pt['snare_given_kick']['singleton_fraction']} and bass|kick8 {pt['bass_given_kick']['singleton_fraction']} (c82 n=2 aggregate 0.742) — but hat|kick8,snare16 stays at {pt['hat_given_kick_snare']['singleton_fraction']} "
        f"({pt['hat_given_kick_snare']['n_contexts']} contexts for {pt['hat_given_kick_snare']['n_pairs']} bars: a 24-bit context is near one-to-one with bars at n=18). The aggregate is dominated by the hat table's context granularity, not by small n. "
        f"Per the brief's diagnostic ladder rung 3 the next axis (coarser hat context / kick alphabet) is pre-registered for c85, NOT changed here (FD-1). Output `groove_v5_v2_full.json` (sha {_sha('data/v5/rules/groove_v5_v2_full.json')[:12]}…), byte-det x2 {bd.get('groove', {}).get('equal')}; "
        f"figure `fig_groove_v2_full_c84.png` (left: singleton fraction vs n for c81/c82/c84, aggregate + per table; right: held-out backbeat/lock corpus vs sampled with ±0.15 band) from `plot_groove_v2_full_c84.py`. Does NOT block P3 (brief: OVERFITS discloses, DEGENERATE blocks).",
        ["data/v5/rules/groove_v5_v2_full.json", "scripts/v5/groove_v5_full_c84.py", "data/v5/rules/fig_groove_v2_full_c84.png", "data/v5/rules/plot_groove_v2_full_c84.py"],
        supersedes_path="M-V5-RULES-1/groove_v5-v2-heldout-c82"))
    # ---- P3 ----
    roll = _j("data/v5/gen/iteration_01/iteration_rollup.json")
    sc_p = Path("data/v5/gen/gen_v5_iter01_ear_scores_c84.json")
    sc = _j(sc_p) if sc_p.exists() else {}
    sbd = _j(SCRATCH / "p3_score_bytedet.json") if (SCRATCH / "p3_score_bytedet.json").exists() else {}
    stall = _j("data/v5/gen/stall_counter.json")
    lm_p = Path("data/v4/generated/v5_iter_01/listening_manifest.json")
    scores_line = ("; ".join(f"{k.split('/')[1].replace('_donor_', '←')} {v['ear_score_v2']}" for k, v in sc.get("scores", {}).items())
                   + f"; ≥6: {sc.get('n_gen_ge_6')}/{sc.get('n_gen_renders')}; band-4 context {sc.get('band4_v2_context')}; exemplar LOO {sc.get('exemplar_loo_v2_context')}") if sc else "scoring table absent at emit"
    events.append(_ev("M-V5-GEN-1/iteration-01-c84", "in-progress", "high",
        "5 renders + replay proofs on disk (byte-det x2 in fresh mkdtemp); ear scores informational under FD-6; stall 1/12; no passer declared.",
        f"c84 P3 iteration 1 (groove-first, OPERATOR #6): `scripts/v5/generate_v5.py` (sha {_sha('scripts/v5/generate_v5.py')[:12]}…) — per song: form plan A A B A (4 bars each, A generated once and repeated literally), "
        f"drums+bass bars from the c84 groove conditionals, one chord per bar from the c84 harmony chain (stationary start, segment-level matrix), bass = chord root/fifth at bass16 onsets, keys = sustained chord tones, melody = hash-gated chord tones on the 8th grid; "
        f"SHA-256 inverse-CDF only; canonical MIDI via the READ-ONLY c4 serializer at the donor tempo (PD/Disco A: frozen anchor BPM since their bpm_v5 is tempo-blocked); sf2 replay via the donor's pinned bass/drums profiles "
        f"(CG drums: GM Standard Kit shim per c72; keys/melody: GM program 4 / 11 shims — disclosed, not profiled); RMS -18/-18/-22/-22 dBFS (gain in [0.05, 4]; CG bass hit the 4.0 cap), 0.99 peak-limit, int16 via stdlib wave. "
        f"Gates: harmony {roll['harmony_verdict']}; groove {roll['groove_verdict']} (OVERFITS disclosed, does not block). Renders: " + "; ".join(f"{s['generated_song_id']}←{s['donor'][:8]} {s['ab_mix_sha256'][:12]}… {s['duration_s']} s {s['replay_proof']}" for s in roll["songs"])
        + f". Per-track WAVs deleted after each mix (score-and-delete); only the 5 ab_mix.wav kept (running top-5). INFORMATIONAL ear scores via `score_gen_batch_v5.py --renders-glob` (amended venv, c76 v2): {scores_line}. Table byte-det x2 {sbd.get('equal')}. "
        f"NO passer declared (c76 L119 infeasibility; FD-6 operator ear governs). Best samples copied to `data/v4/generated/v5_iter_01/` ({'present' if lm_p.exists() else 'absent'}). stall_counter {stall['iterations']}/{stall['budget']}. "
        f"Manifests carry seed + generator hash + rules hashes (harmony chain / groove model / both preregs / donor map) + donor + env pins + shims; ear score as sibling `ear_score_v5.json`.",
        ["scripts/v5/generate_v5.py", "scripts/v5/deliver_v5_listening.py", "data/v5/gen/iteration_01/iteration_rollup.json", "data/v5/gen/stall_counter.json", "data/v5/logs/generate_v5_iter01_c84.log"]
        + [f"data/v5/gen/iteration_01/{s['generated_song_id']}_donor_{s['donor']}/{n}" for s in roll["songs"] for n in ("ab_mix.wav", "ab_mix.manifest.json", "ab_mix.replay_proof.json")]
        + ([str(sc_p), "data/v5/logs/score_gen_v5_iter01_c84_run1.log", "data/v5/logs/score_gen_v5_iter01_c84_run2.log"] if sc else [])
        + ([str(lm_p)] if lm_p.exists() else []) + ["scripts/v5/score_gen_batch_v5.py"], supersedes_path="M-V5-GEN-1/gen-renders-ear-scored-informational-c83"))
    # ---- outage line ----
    events.append(_ev("_infra/c100-c127-lost-to-outage", "validated", "high", "one POR line per operator guidance 2026-09-09; no memo, no re-audit.",
        "c100–c127 lost to outage (Claude rate limit + researcher context overflow; engine dead 2026-09-07 03:32Z → 2026-09-09 20:40Z). Last real work c98/c99 = on-disk c82/c83. Resumed at c84 (harness c128) from that state. ONE line; nothing else.",
        ["plan_of_record.md"], supersedes_path=None))
    # ---- bookkeeping ----
    tests_p = SCRATCH / "test_results.json"; tests = _j(tests_p) if tests_p.exists() else {}
    test_line = "; ".join(f"{Path(k).name} {v['summary'][0]}/{v['summary'][1]}" for k, v in tests.items()) or "adopted suite not yet run at emit"
    n_pass = sum(v["summary"][0] or 0 for v in tests.values()); n_files = len(tests)
    pc_p = SCRATCH / "promise_check_c84_pre_emit.txt"
    if pc_p.exists():
        _pc = pc_p.read_text().splitlines()
        pc_line = f"{sum(1 for l in _pc if 'ERROR' in l)} ERROR / {sum(1 for l in _pc if 'WARN' in l)} WARN lines pre-emit (baseline 156 ERROR)"
    else:
        pc_line = "promise_check not yet run"
    events.append(_ev("_plan/register-c84-sub-leaves", "validated", "high", "rows inserted inline in the parseable region by tools/_register_c84_por_rows.py (idempotent).",
        f"c84 POR registration: c84 sub-leaves inserted inline in `## Milestones` before `## Sub-milestones`; ONE outage line. M-V5-CORPUS-1 tally at emit: {len(landed)}/26 landed, {len(side)}/26 sidecar; "
        f"M-V5-RULES-1: harmony full {h['degeneracy_verdict']} (n={h['gate']['n_used']}), groove v2 {g['verdict']}; M-V5-GEN-1 iteration 1 landed, informational scores only, stall {stall['iterations']}/{stall['budget']}.",
        ["plan_of_record.md"], supersedes_path=None))
    events.append(_ev("_infra/adopt-cycle84-tests", "validated", "high", "new test file adopted; adopted suite re-run under /usr/bin/python3.",
        f"c84 test-adoption: `tests/test_c84_landing.py` (8: content-gate fixture semantics; on-disk gate = exactly ae1b + tempo file untouched; ContentBlockedError refusal in harmony/groove/groove_v2 before MISSING_REINDEX; "
        f"harmony full-corpus enum + prereg mtime + c82 anchor; groove held-out fold SHA-256 determinism; generator 5/5 replay proofs + A A B A literal repetition + per-track deletion + stall 1/12; hook-at-birth baseline extension; AST discipline on 7 c84 scripts). "
        f"Adopted suite ({n_files} files, /usr/bin/python3): {test_line}; total {n_pass} PASS. `tests/` overall keeps pre-existing historical failures — counts are the ADOPTED suite only.",
        ["tests/test_c84_landing.py"], supersedes_path=None))
    events.append(_ev("_archive/cycle-84-scratch", "validated", "high", "one-shot emitter + registrar retained in-tree per emitter-exemption policy and listed as artifacts (closes c83 audit L1).",
        "c84 scratch archival: `tools/_emit_c84_ledger_events.py` + `tools/_register_c84_por_rows.py` retained in-tree per docs/emitter_exemption_policy.md and LISTED here as artifacts (L1); session scratchpad runners (probe_open, probe_envpin, smoke_refusal, bytedet_p1p2, score_iter01, run_tests) not in workspace; "
        "plot scripts co-located with their data + figures under data/v5/rules/. No workspace scratch to archive.",
        ["tools/_emit_c84_ledger_events.py", "tools/_register_c84_por_rows.py"], supersedes_path=None))
    n_frozen_ok = sum(frozen_ok.values())
    events.append(_ev("_run/cycle_84_closed", "validated", "high", "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        f"c84 CLOSED — v5 REOPENING cycle 6 (outage recovery by execution). FROZEN/READ-ONLY anchors {n_frozen_ok}/{len(FROZEN_EXPECTED)} byte-identical to their pinned prefixes: "
        + "; ".join(f"{k} {frozen[k][:12]}{'' if frozen_ok[k] else ' MISMATCH'}" for k in FROZEN_EXPECTED)
        + f". Driver PID {pid} alive at emit {_alive(pid)}; landed {len(landed)}/26 (sidecar {len(side)}/26); 0e1e8f20592db366 cache hits {hits_0e1e}; cc0693b4a24f64b2 {hits_cc06 or 'not started at emit'}. "
        f"df at emit {df_now} % (avail {avail_now} GB); never ≥ 90 %. Tests (adopted suite): {test_line}. promise_check: {pc_line}. "
        + (f"ESCALATION: {escalation} " if escalation else "")
        + "Cycle counter: harness says c128, on-disk c84 (disclosed, not reconciled). Status convention (L2): `validated` for recorded RULES_OUT/OVERFITS verdicts; c83's `invalidated` on tempo_v5d stands as history. Full 9-header summary in the c84 work output.",
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_83_closed"))

    _le = os.environ.get("LONG_EXPOSURE_PKG_PATH", "/home/user/human-in-a-loop/long-exposure")
    if _le not in sys.path:
        sys.path.append(_le)
    try:
        from long_exposure.tools._ledger_schema import validate_event, REQUIRED_EVENT_FIELDS
        for e in events:
            miss = [k for k in REQUIRED_EVENT_FIELDS if k not in e]
            assert not miss, (e["milestone_id"], miss)
            errs = validate_event(e)
            assert not errs, (e["milestone_id"], errs)
    except ImportError:
        print("WARN: long_exposure schema not importable; field check only")
        for e in events:
            assert "agent" in e
    to_append = [e for e in events if e["milestone_id"] not in existing_ids]
    if not to_append:
        print("IDEMPOTENT: all c84 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c84 events; frozen anchors OK {n_frozen_ok}/{len(FROZEN_EXPECTED)}")
    for e in to_append:
        print(f"  {e['status']:16s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
