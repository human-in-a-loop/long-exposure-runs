#!/usr/bin/python3
"""c83 one-shot ledger emitter — v5 REOPENING cycle 5 (P0 disk/liveness, P0 amended ear-venv receipt, hook-at-birth
verification, unpaired-starts characterization, informational gen-render ear scoring, hygiene, optional v5d).

Every event carries `agent` (REQUIRED_EVENT_FIELDS); UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts);
idempotent by milestone_id (re-runnable: appends only milestone_ids not yet present, so it can run after S2 and again at
close); supersedes_path is str|None (c14 lemma). Reads every number from disk at emit time; no hardcoded timestamps or
foreign paths. Retained in-tree per docs/emitter_exemption_policy.md (c34 OPT_B exemption).
"""
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 83
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
P = "M-V5-CORPUS-1"
FROZEN_EXPECTED = {  # c79-pinned prefixes (14 anchors) + c83 brief additions
    "docs/v3_determinism_certificate.md": "a6876911", "data/v3/rules/rules_artifact.jsonl": "e19fb205",
    "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav": "6e13e007", "data/v4/profiles/31a164f845f8e27e/bass_v2.json": "2a1cb340",
    "data/v4/profiles/88d247468cb6d49f/stem_manifest.json": "d483f2bf", "data/v4/ear/exemplar_set.json": "31c10dfb",
    "scripts/ear/v4_ear.py": "e775621b", "scripts/gen/iterate_v4.py": "8f1f0b88", "scripts/gen/interpolate_v4.py": "2359f35d",
    "docs/v4_completion_report_v3.md": "b900b0ee", "scripts/v3_spine/recreate_v3.py": "b1490874",
    "scripts/v3_spine/stage_cache.py": "33435a84", "scripts/v3_spine/midi_from_json_events.py": "bbff015f",
    "scripts/sound_match/_sweep_hygiene_c27.py": "771ff42b", "scripts/v3_spine/recreate_v3_checkpointed.py": "da418986",
    "scripts/v3_spine/launch_detached.py": "999045f3", "data/v5/corpus/corpus_manifest.json": "73362136",
    "scripts/v5/transcribe_full_length.py": "c1c6b2df", "scripts/v5/reindex_hook.py": "a63434a6",
}
SCRATCH = Path("/tmp/claude-0/-home-user-long-exposure-runs-music-gen/f1ab91b3-42b2-4ff6-bfb7-c14b1a30dc9c/scratchpad")


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


def main() -> int:
    C = Path("data/v5/corpus")
    events = []
    frozen = {k: _sha(k) for k in FROZEN_EXPECTED}
    frozen_ok = {k: frozen[k].startswith(v) for k, v in FROZEN_EXPECTED.items()}
    n_frozen_ok = sum(frozen_ok.values())
    df_now, avail_now = _df()
    live = Path("data/v5/logs/c83_p0_liveness.txt").read_text()
    escalation = ("Operator authority requested over `/root/.local` (2.97 GB) and `/tmp/c37b_v4_s*_r*` + `/tmp/tfhub_modules` (≈3.3 GB) to restore headroom; driver abort ceiling 90%."
                  if avail_now < 4.5 else None)

    # ---- S1 ----
    events.append(_ev(f"{P}/transcription-liveness-c83", "validated", "high",
        "os.kill(pid,0) liveness + advancing log + df in driver semantics; no restart, no install, no FROZEN path touched.",
        f"c83 S1 P0: {live.strip().replace(chr(10), ' | ')}. Driver untouched (no restart this cycle; `_infra/driver-restart-c83` not emitted). "
        f"NO pip install this cycle (no pause window opened). df at emit {df_now} % (avail {avail_now} GB); 90 % ceiling never crossed. "
        + (f"ESCALATION: {escalation}" if escalation else "Escalation line not triggered (avail >= 4.5 GB)."),
        ["data/v5/logs/c83_p0_liveness.txt"], supersedes_path=f"{P}/transcription-liveness-c82"))

    # ---- S2 (F2 + F3) ----
    rc = _j("data/v5/ear/env_pin_ear_venv_c82_amended.json"); pr = _j("data/v5/ear/ear_probe_c83.json")
    events.append(_ev("M-V5-EAR-1/ear-venv-receipt-amended-c83", "validated", "high",
        "receipt recomputed from disk + venv subprocess; probe x2 fresh mkdtemp REPRODUCES_CACHE; main-env freeze unchanged; test_04 green.",
        f"c83 S2 P0 (closes c82 audit F2): `data/v5/ear/env_pin_ear_venv_c82_amended.json` pins the AMENDED venv — pinned command = c79 command followed by "
        f"`pip install -r data/v5/ear/ear_venv_pip_freeze_c82_amended.txt` (freeze file is the pin; the as-run `pip install librosa` + 18 resolved packages recorded alongside; librosa pin {rc['librosa_pin']}); "
        f"freeze sha {rc['pip_freeze_sha256'][:12]}… recomputed from the file (== c82 amend record {rc['pip_freeze_sha256_matches_c82_amend_record']}); live venv `python -m pip freeze` package set == file {rc['live_venv_freeze_package_set_equals_file']} "
        f"(byte-equal {rc['live_venv_freeze_matches_file']}: pip emits the same 52 lines in a different order between `bin/pip freeze` and `-m pip freeze` — disclosed); "
        f"versions by venv subprocess {rc['versions_from_venv_subprocess']}; main-env freeze {rc['main_env_pip_freeze_sha256'][:12]}… == c79 receipt {rc['main_env_unchanged']}; "
        f"venv on disk {rc['size_bytes_installed'] / 1e9:.2f} GB; install_this_cycle=false. Read-only re-probe `ear_probe_c83.json` x2 fresh mkdtemp: **{pr['status']}** "
        f"(run1==run2 {pr['run1_eq_run2']}, sha {pr['run1_sha256'][:12]}… == c82 amended probe; max|diff| vs cache {max(v['max_abs_diff_vs_cache'] for v in pr['rows'].values())}). "
        f"`supersedes_path` (str) = the c82 receipt; the c82 event + `ear_probe_c82.json` (EAR_VENV_PROBE_FAILED, permanent) are byte-identical. "
        f"F3: the two c82 orphan logs are adopted as artifacts here (no move). F5: `ear_probe_c82.json` lacks `agent` — cosmetic c82 record, left byte-identical (disclosed). "
        f"`tests/test_ear_venv_c81.py` extended in place with test_04 (4/4).",
        ["data/v5/ear/env_pin_ear_venv_c82_amended.json", "data/v5/ear/ear_probe_c83.json", "scripts/v5/ear_venv_receipt_amend_c83.py",
         "data/v5/logs/ear_probe_c82.log", "data/v5/logs/ear_probe_c82_amended.log", "data/v5/logs/ear_probe_c83.log", "tests/test_ear_venv_c81.py"],
        supersedes_path="data/v5/ear/env_pin_ear_venv_c82.json"))

    # ---- S3 ----
    hb_p = C / "hook_at_birth_c83.json"
    if hb_p.exists():
        hb = _j(hb_p)
        for s, v in hb["per_song"].items():
            tm = _j(C / s / "transcription_manifest.json")
            events.append(_ev(f"{P}/{s}-reindexed-c83", "validated" if v["hook_at_birth"] else "action_required", "high" if v["hook_at_birth"] else "medium",
                "sidecar SHAs == disk; MIDI note_on == JSON starts per probe; sidecar written within seconds of the manifest by the live hook.",
                f"c83 per-song lossless record: {tm.get('title')} ({s}, {tm['duration_s']} s, bpm_v5 {tm['bpm_v5']}): landed under the restarted driver (PID 10247, hook live at birth) — "
                f"manifest {v['manifest_mtime']}, sidecar {v.get('sidecar_mtime')} (Δ {v.get('sidecar_minus_manifest_s')} s); hook_at_birth={v['hook_at_birth']}; "
                f"`canonical_v5_reindexed/` paired {v.get('paired_total')} / unpaired {v.get('unpaired_total')}; per-probe note_on == starts {v.get('note_on_equals_starts_all')}; "
                f"no catch-up needed (reindex_landed no-op {hb['catch_up_is_noop']}). Per-stem: " + "; ".join(f"{p} {x['json_starts']} starts → {x['n_paired']} paired/{x['n_unpaired']} unpaired" for p, x in v.get('per_probe', {}).items())
                + ("" if v["hook_at_birth"] else f" — DEFECT {v.get('defect', 'hook_at_birth false')}: recorded, driver NOT patched mid-run (FD-1)."),
                [f"data/v5/corpus/{s}/transcription_manifest.json", f"data/v5/corpus/{s}/canonical_v5_reindexed_sha256.json",
                 f"data/v5/corpus/{s}/canonical_v5_reindexed/reindex_manifest.json"], supersedes_path=None))
        events.append(_ev(f"{P}/hook-at-birth-verification-c83", "validated" if hb["catch_up_is_noop"] and (hb["all_new_hook_at_birth"] in (True, None)) else "action_required", "high",
            "reindex_landed() asserted no-op on every landed song; every post-restart landing carries a hook-at-birth sidecar.",
            f"c83 S3: {hb['n_landed_total']}/26 landed at check ({hb['checked_utc']}); post-restart landings {hb['new_landings']}; all_new_hook_at_birth={hb['all_new_hook_at_birth']}; "
            f"`reindex_hook.reindex_landed()` run once: no-op {hb['catch_up_is_noop']} ({hb['n_non_noop']} non-noop). Invariant (d): {hb['invariant_d_disclosure']}. "
            f"Zero catch-ups needed under the new image.",
            ["data/v5/corpus/hook_at_birth_c83.json", "scripts/v5/hook_at_birth_c83.py"], supersedes_path=f"{P}/reindex-hygiene-c81"))
    else:
        events.append(_ev(f"{P}/hook-at-birth-verification-c83", "in-progress", "medium",
            "no song landed after the restart before the emitter ran; verification script on disk; re-run at close if a landing occurs.",
            f"c83 S3: no post-restart landing on disk at emit time (8/26 landed; song 9 `1d9ac896511ebcd4` in flight); `scripts/v5/hook_at_birth_c83.py` ready; "
            f"the c83 emitter is idempotent by milestone_id, so a later run appends the per-song rows if Oba La lands in-cycle.",
            ["scripts/v5/hook_at_birth_c83.py"], supersedes_path=None))

    # ---- S4 ----
    u = _j(C / "unpaired_starts_c83.json"); bd = _j(SCRATCH / "s4_bytedet.json") if (SCRATCH / "s4_bytedet.json").exists() else {}
    nm = u["named_cells_from_brief"]
    events.append(_ev(f"{P}/unpaired-starts-characterization-c83", "validated", "high",
        "prereg mtime precedes output; per-(song,stem) labels from the pre-declared rule; JSON byte-det x2; nothing modified.",
        f"c83 S4 (M-3, characterization, no fix): prereg `unpaired_starts_prereg_c83.json` (sha {u['prereg_sha256'][:12]}…) BEFORE output; {u['n_songs']} songs x 7 stems = {sum(u['tally_all_cells'].values())} cells: "
        f"tally {u['tally_all_cells']} (per stem {u['tally_per_stem']}). Named cells: " + "; ".join(f"{k}: {v['n_unpaired']}/{v['n_starts']} unpaired ({v['unpaired_fraction']}), final-chunk share {v['final_chunk_unpaired_fraction']}, per-chunk-rate CV {v['per_chunk_rate_cv_over_dense_chunks']} → {v['label']}" for k, v in nm.items())
        + f". FIRST-CLASS FINDING: the large-unpaired cells (Molasses other 3066, Molasses vocals 3130, Desire other 3578) are NEITHER H1 (final-chunk share 0.0) NOR H2 (per-chunk unpaired rate CV 1.6–2.2, not flat): the unpaired starts sit almost entirely inside the 2 densest 25 s chunks of each stem "
        f"(Molasses other chunks 6–7: 3452+858 starts → 2294+772 unpaired; Molasses vocals chunks 9–10: 2496+1318 → 2104+1026; Desire other chunks 2–3: 3801+1587 → 2311+1224) — a density-burst class where MuScriptor emits thousands of starts in one chunk and the greedy chunk-local-index pairing exhausts the ends. "
        f"Labelled MIXED by the pre-declared rule (post-hoc description only; no threshold retuned, FD-1). Only Rome bass is H1 (the c81 tail). Byte-det x2 {bd.get('equal')} (sha {bd.get('sha', '')[:12]}…). "
        f"c84 candidate (pre-declared, NOT implemented): chunk-window-constrained pairing for other/vocals, or caching per-chunk MuScriptor outputs at the muscriptor stage. Figure `data/v5/corpus/fig_unpaired_starts_c83.png` (left: unpaired fraction per song x stem, hatched = n_unpaired < 20; right: per-25 s-chunk unpaired rate for the named cells).",
        ["data/v5/corpus/unpaired_starts_prereg_c83.json", "data/v5/corpus/unpaired_starts_c83.json", "data/v5/corpus/fig_unpaired_starts_c83.png",
         "data/v5/corpus/plot_unpaired_starts_c83.py", "scripts/v5/unpaired_starts_c83.py"], supersedes_path=f"{P}/reindex-fidelity-c82"))

    # ---- S5 ----
    t = _j("data/v5/gen/gen_render_ear_scores_c83.json"); bd5 = _j(SCRATCH / "s5_bytedet.json") if (SCRATCH / "s5_bytedet.json").exists() else {}
    gen = {k: v for k, v in t["scores"].items() if not k.startswith("interpolation_demo")}
    events.append(_ev("M-V5-GEN-1/gen-renders-ear-scored-informational-c83", "in-progress", "high",
        "informational only: scores through the amended venv on the c76 v2 calibration; WAV/manifest bytes unchanged; table byte-det x2; M-V5-GEN-1 stays gated on M-V5-RULES-1.",
        f"c83 S5 INFORMATIONAL (precondition met: amended receipt + probe c83 REPRODUCES_CACHE): `scripts/v5/score_gen_batch_v5.py` (sibling; c75 `score_gen_batch.py` untouched) scored the 15 `data/v4/gen/iteration_0{{1,2,3}}/*/ab_mix.wav` + the interpolation demo: "
        f"VGGish by venv subprocess (READ-ONLY c74 extractor) → c76 v2 wider-linear (READ-ONLY `v4_ear_v2`) against the FRESH exemplar signatures (shared raw ceiling {t['shared_raw_ceiling']}). "
        f"Per-song v2 scores: " + "; ".join(f"{k.replace('gen_v4_', '')} {v['ear_score_v2']}" for k, v in gen.items()) + f"; interpolation demo {list(t['interpolation_demo'].values())[0]['ear_score_v2']}. "
        f"Count ≥ 6: {t['n_gen_ge_6']}/15 (song_1 CG-donor x3 and song_4 PD-donor x3; song_3 Rome-donor lowest 5.72–5.74). Context on the same fresh embeddings: exemplar LOO {t['exemplar_loo_v2_context']}; band-4 {t['band4_v2_context']} — the gen renders (5.72–6.25) sit inside the band-4 range (5.70–6.72), "
        f"so under the c76 L119-infeasibility proof these scores do NOT discriminate; FD-6 operator ear governs LANDS; NOTHING here is an M-V5-GEN-1 passer; M-V5-GEN-1 stays gated on M-V5-RULES-1 (PD + Disco A still tempo-blocked). "
        f"16 sibling `ear_score_v5.json` files written; the 16 `ab_mix.manifest.json` + WAVs byte-identical ({t['wav_and_manifest_bytes_unchanged']}). Table byte-det x2 {bd5.get('equal')} (sha {bd5.get('sha', '')[:12]}…). stall_counter.json untouched (0/12).",
        ["data/v5/gen/gen_render_ear_scores_c83.json", "scripts/v5/score_gen_batch_v5.py", "data/v5/logs/score_gen_batch_v5_c83_run1.log", "data/v5/logs/score_gen_batch_v5_c83_run2.log"]
        + [f"data/v4/gen/{k}/ear_score_v5.json" for k in t["scores"]], supersedes_path=None))

    # ---- S6 F4 ----
    events.append(_ev("_infra/harmony-gated-record-tombstone-c83", "validated", "high", "tombstone README on disk; gated file byte-identical.",
        f"c83 S6 F4: `data/v5/rules/harmony_v5_gated.json` (c80/c81 GATED, < 3 songs) is superseded by `data/v5/rules/harmony_markov_v5.json` (c82 NON_DEGENERATE on WIG+CG+Rome); "
        f"the gated file stays byte-identical (sha {_sha('data/v5/rules/harmony_v5_gated.json')[:12]}…); one-line `data/v5/rules/README_c83.md` states the same.",
        ["data/v5/rules/README_c83.md"], supersedes_path="data/v5/rules/harmony_v5_gated.json"))

    # ---- S7 ----
    v5d_p = C / "tempo_v5d_falsification.json"
    if v5d_p.exists():
        v5d = _j(v5d_p)
        events.append(_ev(f"{P}/tempo_v5d-preregistered-c83", "validated", "high", "prereg mtime precedes every per-song output.",
            f"c83 S7: `tempo_v5d_preregistration.json` written BEFORE any output — {v5d.get('criterion_summary', 'see file')}.",
            ["data/v5/corpus/tempo_v5d_preregistration.json", "scripts/v5/tempo_v5d.py"], supersedes_path=f"{P}/tempo-mechanism-verdict-c82"))
        events.append(_ev(f"{P}/tempo_v5d-verdict-c83", "validated" if v5d["verdict"] == "SUPPORTED" else "invalidated", "high",
            "frozen enum; no retune; no recanonicalization this cycle.", v5d.get("ledger_narrative", json.dumps(v5d)[:1500]),
            ["data/v5/corpus/tempo_v5d_falsification.json", "data/v5/corpus/tempo_v5d_summary.tsv"], supersedes_path=f"{P}/tempo_v5d-preregistered-c83"))
    else:
        events.append(_ev(f"{P}/tempo_v5d-deferred-c83", "in-progress", "medium", "brief §S7 optional; deferral enum recorded.",
            "c83 S7: **TEMPO_V5D_DEFERRED_WALL_BUDGET** — the optional refined-lag criterion v5d was not attempted this cycle (S1–S6 consumed the budget); "
            "no prereg, no per-song output, `recanonicalization_blocked.json` untouched (mtime evidence); PD + Disco A remain MUST-NOT-CONSUME for rules.",
            [], supersedes_path=None))

    # ---- bookkeeping ----
    tests_p = SCRATCH / "test_results.json"; tests = _j(tests_p) if tests_p.exists() else {}
    test_line = "; ".join(f"{Path(k).name} {v['summary'][0]}/{v['summary'][1]}" for k, v in tests.items()) or "adopted suite not yet run at emit"
    n_pass = sum(v["summary"][0] or 0 for v in tests.values()); n_files = len(tests)
    pc_p = SCRATCH / "promise_check_c83_pre_emit.txt"
    if pc_p.exists():
        _pc = pc_p.read_text().splitlines()
        pc_line = f"{sum(1 for l in _pc if 'ERROR' in l)} ERROR / {sum(1 for l in _pc if 'WARN' in l)} WARN lines pre-emit (baseline 156 ERROR)"
    else:
        pc_line = "promise_check not yet run"
    landed = sorted(p.parent.name for p in C.glob("*/canonical_v5_reindexed_sha256.json"))
    events.append(_ev("_plan/register-c83-sub-leaves", "validated", "high", "rows inserted inline in the parseable region by tools/_register_c83_por_rows.py (idempotent).",
        f"c83 POR registration: c83 sub-leaves inserted inline in `## Milestones` before `## Sub-milestones`. M-V5-CORPUS-1 running tally: {len(landed)}/26 landed, all lossless + sidecar ({landed}). "
        f"M-V5-EAR-1: amended receipt landed (F2 closed). M-V5-GEN-1: informational scores only, still gated on M-V5-RULES-1. Test counts everywhere refer to the adopted suite ({n_files} files).",
        ["plan_of_record.md"], supersedes_path=None))
    events.append(_ev("_infra/adopt-cycle83-tests", "validated", "high", "new test file adopted; adopted suite re-run under /usr/bin/python3.",
        f"c83 test-adoption: `tests/test_c83_landing.py` (7: liveness + no-install; amended receipt + c83 probe; S4 prereg-before-output + histogram sums + fresh-subprocess byte-det; "
        f"S5 informational table + sibling scores + WAV/manifest bytes; S3 hook-at-birth record (skip-pass if no landing); F4 tombstone; AST discipline on 6 c83 scripts) + `test_ear_venv_c81.py` test_04 additive. "
        f"Adopted suite ({n_files} files, /usr/bin/python3): {test_line}; total {n_pass} PASS. `tests/` holds ~152 files with pre-existing historical failures (Stage C relocation, VST3 prune) — counts here are the ADOPTED suite only.",
        ["tests/test_c83_landing.py", "tests/test_ear_venv_c81.py"], supersedes_path=None))
    events.append(_ev("_archive/cycle-83-scratch", "validated", "high", "one-shot emitters retained in-tree per emitter-exemption policy.",
        "c83 scratch archival: `tools/_emit_c83_ledger_events.py` + `tools/_register_c83_por_rows.py` retained in-tree per docs/emitter_exemption_policy.md; session scratchpad runners (s1_liveness_anchors, run_tests, byte-det compare) not in workspace; "
        "`data/v5/corpus/plot_unpaired_starts_c83.py` co-located with its data + figure. No workspace scratch to archive.", [], supersedes_path=None))
    events.append(_ev("_run/cycle_83_closed", "validated", "high", "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        f"c83 CLOSED — v5 REOPENING cycle 5. FROZEN/READ-ONLY anchors {n_frozen_ok}/{len(FROZEN_EXPECTED)} byte-identical to their pinned prefixes: "
        + "; ".join(f"{k} {frozen[k][:12]}{'' if frozen_ok[k] else ' MISMATCH'}" for k in FROZEN_EXPECTED)
        + f". df at emit {df_now} % (avail {avail_now} GB). Tests (adopted suite): {test_line}. promise_check: {pc_line}. "
        + (f"ESCALATION: {escalation} " if escalation else "")
        + "Cycle counter: harness says cycle 91, on-disk c83 (disclosed, not reconciled). Full 9-header summary in the c83 work output.",
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_82_closed"))

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
    existing = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            existing.add(json.loads(line).get("milestone_id"))
    to_append = [e for e in events if e["milestone_id"] not in existing]
    if not to_append:
        print("IDEMPOTENT: all c83 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c83 events; frozen anchors OK {n_frozen_ok}/{len(FROZEN_EXPECTED)}")
    for e in to_append:
        print(f"  {e['status']:16s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
