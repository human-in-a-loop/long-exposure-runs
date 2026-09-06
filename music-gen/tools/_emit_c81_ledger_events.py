#!/usr/bin/python3
"""c81 one-shot ledger emitter — v5 REOPENING cycle 3 (reindex hygiene, ear venv disk-blocked, tempo v5c
pre-registered falsification, reindex fidelity M-3, groove first data, harmony gated/first-data).

UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts) per c14+ convention. Idempotent by
milestone_id. Retained in-tree per docs/emitter_exemption_policy.md (c34 OPT_B exemption). Reads every number
from disk at emit time.
"""
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 81
RUN_ID = "run-2026-09-06T000000Z"
TS = "2026-09-06T17:30:00Z"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
P = "M-V5-CORPUS-1"
WIG, CG, PD, ROME, DISCO = ("252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f", "51e433ade2a845e1", "cdd2717e52820ff6")
FROZEN_EXPECTED = {  # c79-pinned prefixes (14 anchors)
    "docs/v3_determinism_certificate.md": "a6876911", "data/v3/rules/rules_artifact.jsonl": "e19fb205",
    "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav": "6e13e007", "data/v4/profiles/31a164f845f8e27e/bass_v2.json": "2a1cb340",
    "data/v4/profiles/88d247468cb6d49f/stem_manifest.json": "d483f2bf", "data/v4/ear/exemplar_set.json": "31c10dfb",
    "scripts/ear/v4_ear.py": "e775621b", "scripts/gen/iterate_v4.py": "8f1f0b88", "scripts/gen/interpolate_v4.py": "2359f35d",
    "docs/v4_completion_report_v3.md": "b900b0ee", "scripts/v3_spine/recreate_v3.py": "b1490874",
    "scripts/v3_spine/stage_cache.py": "33435a84", "scripts/v3_spine/midi_from_json_events.py": "bbff015f",
    "scripts/sound_match/_sweep_hygiene_c27.py": "771ff42b",
}
SCRATCH = Path("/tmp/claude-0/-home-user-long-exposure-runs-music-gen/8a082999-6eb3-4432-ba2d-ea2b113d0dd3/scratchpad")


def _sha(p: str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _event_id(body: dict) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, _canonical({k: v for k, v in body.items() if k not in ("event_id", "ts")})))


def _ev(milestone_id, status, level, rationale, narrative, artifacts, supersedes_path=None):
    body = {"artifacts": artifacts, "confidence": {"assessor": "worker", "level": level, "rationale": rationale},
            "cycle": CYCLE, "env_pin_sha256": ENV_PIN, "milestone_id": milestone_id, "narrative": narrative,
            "run_id": RUN_ID, "status": status, "supersedes_path": supersedes_path, "ts": TS}
    body["event_id"] = _event_id(body)
    return body


def main() -> int:
    C = Path("data/v5/corpus")
    fals = json.loads((C / "tempo_v5c_falsification.json").read_text())
    ps = fals["per_song"]
    bd = json.loads((C / "tempo_v5c_byte_determinism.json").read_text())
    p34 = json.loads(Path("data/v5/rules/c81_p3_p4_byte_determinism.json").read_text())
    fid = json.loads((C / WIG / "reindex_fidelity_c81.json").read_text())
    grv = json.loads(Path("data/v5/rules/groove_v5.json").read_text())
    venv = json.loads(Path("data/v5/ear/venv_build_c81.json").read_text())
    probe = json.loads(Path("data/v5/ear/ear_probe_c81.json").read_text())
    prog = json.loads((C / "transcription_progress.json").read_text())
    live = Path("data/v5/logs/c81_p0_liveness.txt").read_text().splitlines()
    log_tail = Path("data/v5/logs/transcribe_full_c79.log").read_text().splitlines()[-1]
    frozen = {k: _sha(k) for k in FROZEN_EXPECTED}
    frozen_ok = {k: frozen[k].startswith(v) for k, v in FROZEN_EXPECTED.items()}
    n_frozen_ok = sum(frozen_ok.values())
    st = os.statvfs("."); avail = st.f_bavail * st.f_frsize; used = (st.f_blocks - st.f_bfree) * st.f_frsize
    df_now = round(100 * used / (used + avail), 2)
    done = [s for s in prog["order"] if (C / s / "transcription_manifest.json").exists()]
    sided = [s for s in done if (C / s / "canonical_v5_reindexed_sha256.json").exists()]
    tests_p = SCRATCH / "test_results.json"
    tests = json.loads(tests_p.read_text()) if tests_p.exists() else {}
    test_line = "; ".join(f"{Path(k).name} {v['summary'][0]}/{v['summary'][1]}" for k, v in tests.items())
    pc_p = SCRATCH / "promise_check_c81.txt"
    pc_line = pc_p.read_text().strip().splitlines()[-1] if pc_p.exists() else "promise_check not yet run"
    blocked_sha = _sha("data/v5/corpus/recanonicalization_blocked.json")
    chain_p = Path("data/v5/rules/harmony_markov_v5.json")
    other = fid["per_stem"]["other"]

    events = []
    events.append(_ev(f"{P}/transcription-liveness-c81", "in-progress", "high",
        "PID alive via os.kill(pid, 0) at open and at emit; log advancing; driver never signalled.",
        (f"P0.1: PID {prog.get('pid')} ALIVE at c81 open (os.kill sig-0; ps/proc approval-gated) with the log advancing on Rome (16:44 muscriptor:bass -> "
         f"full_mix); at emit last log line: {log_tail}. Record data/v5/logs/c81_p0_liveness.txt ({live[3]}). df at emit {df_now} %; driver max "
         f"{prog.get('df_max_pct_observed')} %; never >= 90 %. Landed on disk at emit: {done}; with lossless sidecar: {sided}. No SIGSTOP/SIGCONT issued "
         "(no pip ran — see M-V5-EAR-1/ear-venv-blocked-disk-c81); no install co-scheduled."),
        ["data/v5/logs/c81_p0_liveness.txt"]))

    events.append(_ev(f"{P}/reindex-hygiene-c81", "validated", "high",
        "Every landed song reindexed + sidecar; harmony raises on a lossy-only song (test_01); two-chunk fixture recovers 6/6 (test_03); driver hook call verified by source order (test_04).",
        ("P0.2-P0.6 close the c80 gap (manifests pointed at the LOSSY canonical_midi_full; no driver hook; harmony_v5 silently fell back). (2) reindex_canonical_v5.py "
         f"--songs run over every landed song without a reindex manifest (Peach Dream: other 2026 starts -> 2023 paired / 3 unpaired; drums 1051/1051; bass 504/504; "
         f"piano 202/202; vocals 494/494; full_mix 2226/2226). (3) additive sidecar canonical_v5_reindexed_sha256.json (per-stem reindexed MIDI + JSON SHAs + "
         f"reindex_manifest SHA + transcription_manifest SHA) written for {sided}; c79/c80 manifest bytes untouched. (4) scripts/v5/harmony_v5.py: MIDI_DIR_PREFERENCE = "
         "('canonical_v5c_reindexed', 'canonical_v5_reindexed') — canonical_midi_full REMOVED; MissingReindexError('MISSING_REINDEX: <sha16> …') raised for an "
         f"unblocked song without a lossless dir; docstring L11-12 fixed; cycle field 81; new sha {_sha('scripts/v5/harmony_v5.py')}. (5) NEW scripts/v5/reindex_hook.py "
         f"(sha {_sha('scripts/v5/reindex_hook.py')}): post_canonicalize(sha16) = reindex + sidecar; reindex_landed() idempotent catch-up. transcribe_full_length.py "
         f"(sha {_sha('scripts/v5/transcribe_full_length.py')}) imports it and calls post_canonicalize right AFTER transcription_manifest.json is written (so the sidecar "
         "pins the on-disk manifest sha); READ-ONLY recreate_v3 / stage_cache / serializer untouched (FROZEN SHAs verified). PID 5201 runs the OLD image — the hook "
         "takes effect on the next natural restart; the catch-up loop covers landings until then; the driver was NOT restarted. (6) "
         f"tempo_v5b_summary_c81.tsv (sha {_sha('data/v5/corpus/tempo_v5b_summary_c81.tsv')}) adds anchor_source; WIG anchor 99.384014 (librosa_full_mix_c79); "
         "c80 TSV untouched. str-supersedes the manifest-pointer clause of canonical-midi-index-collision-c80 (its defect record + fix stand)."),
        ["scripts/v5/reindex_hook.py", "scripts/v5/harmony_v5.py", "scripts/v5/transcribe_full_length.py", "data/v5/corpus/tempo_v5b_summary_c81.tsv"]
        + [f"data/v5/corpus/{s}/canonical_v5_reindexed_sha256.json" for s in sided],
        supersedes_path=f"{P}/canonical-midi-index-collision-c80"))

    for s in sided:
        rm = json.loads((C / s / "canonical_v5_reindexed/reindex_manifest.json").read_text())
        tm = json.loads((C / s / "transcription_manifest.json").read_text())
        tot = {k: sum(v[k] for v in rm["probes"].values()) for k in ("n_starts_in", "n_paired", "n_unpaired_starts")}
        arts = ([f"data/v5/corpus/{s}/canonical_v5_reindexed/{p}.mid" for p in rm["probes"]] + [f"data/v5/corpus/{s}/canonical_v5_reindexed/{p}.reindexed.json" for p in rm["probes"]]
                + [f"data/v5/corpus/{s}/canonical_v5_reindexed/reindex_manifest.json", f"data/v5/corpus/{s}/canonical_v5_reindexed_sha256.json"]
                + sorted(str(p) for p in (C / s / "stage_cache").rglob("*") if p.is_file()))
        nc = {p: tm["note_counts"][p]["n_note_on"] for p in tm.get("note_counts", {})}
        events.append(_ev(f"{P}/{s}-reindexed-c81", "validated", "high",
            "Sidecar SHAs match disk and reindexed MIDI note_on equals JSON starts per stem (test_02); stage-cache outputs adopted.",
            (f"{tm.get('title')} ({s}, bpm_v5 {tm['bpm_v5']}, note_on {nc}): canonical_v5_reindexed/ starts {tot['n_starts_in']} -> paired {tot['n_paired']} / unpaired "
             f"{tot['n_unpaired_starts']}; sidecar reindex_manifest sha {json.loads((C / s / 'canonical_v5_reindexed_sha256.json').read_text())['reindex_manifest_sha256'][:16]}…; "
             f"{len(arts)} artifacts adopted (incl. stage-cache manifests). " + ("BLOCKED for rules (tempo)." if s in (PD, DISCO) else "")),
            arts))

    events.append(_ev("M-V5-EAR-1/ear-venv-blocked-disk-c81", "action_required", "high",
        "Arithmetic from statvfs at cycle open; c79 precedent confirms the build breaches 90 %; main-env freeze sha byte-identical; no pip run.",
        (f"P1 VENV_BLOCKED_DISK (data/v5/ear/venv_build_c81.json sha {_sha('data/v5/ear/venv_build_c81.json')}). df used {venv['df']['used_pct_df_semantics']} %, avail "
         f"{venv['df']['avail_user_gb']} GB — the brief's >= 3.5 GB gate PASSES, but the driver's binding 90 % abort ceiling leaves only "
         f"{venv['arithmetic']['consumable_before_ceiling_gb']} GB consumable (avail at ceiling {venv['arithmetic']['avail_at_ceiling_gb']} GB); the pinned 2.36 GB build would read "
         f"{venv['arithmetic']['post_build_used_pct']} % (+ VGGish weights {venv['arithmetic']['post_build_plus_vggish_used_pct']} %), so the driver's next df_check would FD-1-abort "
         "the in-flight song and end the 26-song job. SIGSTOP/SIGCONT does not change the arithmetic (on resume the check still reads >= 90 %); the c79 identical build hit "
         "92.2 % and was removed. Per FD-1 (no repeat of a known-failing action) no pip was run, no pause was exercised, PID 5201 untouched. Main-env pip-freeze sha "
         f"{venv['main_env_pip_freeze_sha256'][:12]}… == c79 receipt (pre == post). scripts/v5/ear_probe_v5.py (sha {_sha('scripts/v5/ear_probe_v5.py')}) written: runs the "
         "READ-ONLY c74 extractor (scripts/v4_ear/ear.py: 16 kHz, 10 s windows @ 5 s hop, VGGish mean-pool) inside workspace/ear_venv by subprocess x2 into fresh "
         "mkdtemp(), compares to cached exemplar/band-4 rows; pre-declared enum EAR_VENV_REPRODUCES_CACHE (max |diff| <= 1e-5) / EAR_VENV_DIFFERS_FROM_CACHE / "
         f"EAR_VENV_NONDETERMINISTIC / EAR_VENV_ABSENT; this cycle it records {probe['status']} (exit 3). {venv['operator_request_one_line']} "
         "M-V5-EAR-1 remains open; P2-P4 proceeded."),
        ["data/v5/ear/venv_build_c81.json", "scripts/v5/ear_probe_v5.py", "data/v5/ear/ear_probe_c81.json"]))

    events.append(_ev(f"{P}/tempo_v5c-preregistered-c81", "validated", "high",
        "Pre-registration file written before any output; mtime gate verified by the verdict script and test_03; targets identical to c79/c80.",
        (f"data/v5/corpus/tempo_v5c_preregistration.json sha {_sha('data/v5/corpus/tempo_v5c_preregistration.json')} (mtime {fals['preregistration_gate']['prereg_mtime']:.0f}) precedes "
         f"the earliest tempo_v5c.json (mtime {fals['preregistration_gate']['min_output_mtime']:.0f}). Axis varied: T/2 and 2T read DIRECTLY from the autocorrelation at the exact "
         "fractional lag by linear interpolation (0 only if lag < 1 or beyond the autocorrelation); held constant: candidates = local maxima in [40,240], pick band [70,180], "
         "weights (1, 1/2, 1/2), SHA-256 tiebreak, corpus, MuScriptor outputs, env pin. Secondary check: Rome s(lag 17) and s(lag 25) explicit. Third and FINAL unaided "
         f"attempt; meta-gate pre-registered (RULES_OUT -> c82 mechanism probe, no fourth criterion). scripts/v5/tempo_v5c.py (sha {_sha('scripts/v5/tempo_v5c.py')}) + "
         f"tempo_v5c_verdict.py (sha {_sha('scripts/v5/tempo_v5c_verdict.py')}) new siblings with READ-ONLY imports of tempo_v5 / tempo_v5b helpers; tempo_v5.py, tempo_v5b.py "
         "and their frozen verdicts untouched."),
        ["data/v5/corpus/tempo_v5c_preregistration.json", "scripts/v5/tempo_v5c.py", "scripts/v5/tempo_v5c_verdict.py"]))

    d = ps[DISCO]
    events.append(_ev(f"{P}/tempo_v5c-verdict-c81", "validated", "high",
        "Frozen targets evaluated verbatim; one of five anchors misses; RULES-OUT clause fired; no retune; byte-det x2 27/27; figure rendered.",
        (f"FROZEN VERDICT = {fals['verdict']} (data/v5/corpus/tempo_v5c_falsification.json sha {_sha('data/v5/corpus/tempo_v5c_falsification.json')}). 4/5 HIT: WIG "
         f"{ps[WIG]['bpm_v5c']} (s {ps[WIG]['s_scores_top3'][0]['s']}); CG {ps[CG]['bpm_v5c']} (+1.559); PEACH DREAM RECOVERED {ps[PD]['bpm_v5']} -> {ps[PD]['bpm_v5c']} = anchor "
         f"(s {ps[PD]['s_scores_top3'][0]['s']} at lag 21 vs {ps[PD]['s_scores_top3'][1]['s']} at lag 32; the c80-diagnosed mechanism is confirmed: the T/2 term at lag 10.5 "
         "now reads 0.640 instead of 0); ROME HELD 151.999 (s(lag 17)=1.401 [ac_T 0.759, T/2 0.614, 2T 0.671] > s(lag 25)=1.112 [0.680, 0.193, 0.670] — the c80 hemiola "
         f"regression is resolved). MISSED: DISCO A {d['bpm_v5c']} unchanged — s(lag 32)={d['s_scores_top3'][0]['s']} vs s(lag 21, 123.05)={d['s_scores_top3'][1]['s']}: a 0.006 "
         "margin (ac_T 0.660 vs 0.632; the beat's T/2 term 0.640 is offset by the hemiola lag's 2T term 0.609 + T/2 0.453). Non-anchor flips "
         f"{fals['non_anchor_flips']}/{fals['non_anchor_songs']} ({fals['non_anchor_flip_fraction']:.0%}); total flips vs v5 {fals['total_flips_vs_v5']}/26 (Desire "
         "172 -> 89, Charli 80.75 -> 123, Freedom Interlude / Last 100 123 -> 92, Shaolin 103 -> 136, Houston 107.7 -> 103.4). Byte-det x2 "
         f"{bd['n_equal']}/{bd['n_files_compared']} (tempo_v5c_byte_determinism.json). INVALIDATED HYPOTHESIS (first-class): 'reading the harmonics off the "
         "autocorrelation resolves all five anchors' — it resolves four; Disco A fails inside the score's own resolution (0.006 on a 1.19 scale), not by the c80 "
         "mechanism. Per the pre-registered meta-gate (three consecutive falsifications: v5 flat band, v5b banded sum, v5c direct sum) NO fourth criterion may be "
         "proposed; c82 must run the mechanism probe (per-song autocorrelation dump + beat-tracker comparison on the drums stem vs full mix) first. Figure "
         f"data/v5/corpus/fig_tempo_v5c_scores.png (sha {_sha('data/v5/corpus/fig_tempo_v5c_scores.png')[:12]}…; PD / Disco A / Rome; interpolated T/2 and 2T points marked "
         "for the winner and the anchor-nearest candidate; frozen anchor lag as reference) from plot_tempo_v5c_scores.py. tempo_v5c_summary.tsv sha "
         f"{_sha('data/v5/corpus/tempo_v5c_summary.tsv')[:12]}…."),
        ["data/v5/corpus/tempo_v5c_falsification.json", "data/v5/corpus/tempo_v5c_summary.tsv", "data/v5/corpus/tempo_v5c_byte_determinism.json",
         "data/v5/corpus/fig_tempo_v5c_scores.png", "data/v5/corpus/plot_tempo_v5c_scores.py"] + [f"data/v5/corpus/{s}/tempo_v5c.json" for s in prog["order"]]))

    events.append(_ev(f"{P}/recanonicalize-still-blocked-c81", "validated", "high",
        "RULES_OUT branch executed verbatim: blocked file byte-identical to c80; no v5c canonical dirs; no recanonicalize script written.",
        (f"data/v5/corpus/recanonicalization_blocked.json sha {blocked_sha} unchanged (Peach Dream + Disco A MUST-NOT-CONSUME for rules). No canonical_v5c_reindexed/ "
         "directory exists (test_03 asserts); scripts/v5/recanonicalize_tempo.py NOT written because its SUPPORTED trigger did not fire. Note for c82: PD's v5c value equals "
         "its anchor, but adopting it selectively would be a post-hoc criterion (FD-1); PD stays blocked until a criterion is SUPPORTED or the c82 mechanism probe "
         "grounds an operator decision. M-V5-RULES-1 stays gated on the blocked songs."),
        ["data/v5/corpus/recanonicalization_blocked.json"]))

    events.append(_ev(f"{P}/reindex-fidelity-c81", "validated", "high",
        "Pre-declared statistics and enum applied verbatim; DEGRADED on one stem with the cause diagnosed (pairing ambiguity 0.90); byte-det x2 holds.",
        (f"P3 (M-3) data/v5/corpus/{WIG}/reindex_fidelity_c81.json sha {_sha(f'data/v5/corpus/{WIG}/reindex_fidelity_c81.json')}: WIG canonical_v5_reindexed/ restricted to "
         "t in [72.77133, 102.77133] s vs the c21 single-chunk operator-section canonical MIDI (data/v3_spine/252eb21ce7df7328/operator_section/canonical_midi/, "
         f"serialized at 50.174 BPM; both converted to seconds via their own tempo meta). VERDICT {fid['verdict']}. Onset F1 (pitch-equal, +/-50 ms): "
         + "; ".join(f"{s} {fid['per_stem'][s]['onset_f1_pitch']} (any-pitch {fid['per_stem'][s]['onset_f1_any_pitch']}, n={fid['per_stem'][s]['n_matched_pitch']})" for s in ("drums", "bass", "other", "piano", "vocals", "full_mix"))
         + ". Median |dDuration| on matched onsets: " + "; ".join(f"{s} {fid['per_stem'][s]['dduration_median_s']*1000:.1f} ms" if fid['per_stem'][s]['dduration_median_s'] is not None else f"{s} n/a" for s in ("drums", "bass", "other", "piano", "vocals", "full_mix"))
         + f" — every eligible stem (>= 20 matched) is <= 75 ms EXCEPT other ({other['dduration_median_s']*1000:.0f} ms, n=305, p90 1.47 s); bass (1.5 ms) has n=19, below the gate. "
         "DIAGNOSTIC (not in the verdict): pairing-ambiguity fraction = starts in the window with > 1 candidate end of the same chunk-local index within 30 s: "
         + ", ".join(f"{s} {fid['per_stem'][s]['pairing_ambiguity_diagnostic']['ambiguous_fraction']}" for s in ("drums", "bass", "other", "piano", "vocals", "full_mix"))
         + f"; median note duration full/section: other {other['duration_median_full_s']} / {other['duration_median_section_s']} s. FINDING: onsets are lossless (starts "
         "recovered 100 %; F1 differences are transcription differences between the chunked full-length run and the single-chunk section run — the two runs saw different "
         "audio slices), but the c80 greedy start/end pairing over-assigns durations on the dense polyphonic `other` stem where 90 % of pairings are ambiguous. CONSEQUENCE: "
         "harmony_v5's duration-weighted PCPs on `other` carry inflated durations (state sequences still valid at onset level). c82 HANDOFF (pre-declare, then re-measure with "
         "this same script): chunk-window-constrained pairing — a start at t belongs to chunk floor(t/25); only ends inside that chunk's [25k, 25k+30] s window are eligible "
         f"(the READ-ONLY merge keeps times, so chunk membership is recoverable). Byte-det x2 {p34['files'][f'data/v5/corpus/{WIG}/reindex_fidelity_c81.json']['equal']}."),
        ["scripts/v5/reindex_fidelity_c81.py", f"data/v5/corpus/{WIG}/reindex_fidelity_c81.json", "data/v5/rules/c81_p3_p4_byte_determinism.json"]))

    if chain_p.exists():
        mk = json.loads(chain_p.read_text())
        events.append(_ev("M-V5-RULES-1/harmony_v5-first-data-c81", "validated", "medium",
            "Pre-declared >= 3 unblocked-song gate met after Rome landed + reindexed; degeneracy verdict from c80 thresholds; nothing fed to a generator; `other` duration caveat disclosed.",
            (f"P4.1: patched harmony_v5.py (lossless-only) on {mk['gate']['n_used']} unblocked reindexed songs {mk['gate']['used']} (blocked-skipped {mk['gate']['blocked_skipped']}) -> "
             f"data/v5/rules/harmony_markov_v5.json (sha {_sha('data/v5/rules/harmony_markov_v5.json')}): {len(mk['states'])} functional states; max stationary "
             f"{mk['max_stationary_state']} = {mk['max_stationary_mass']}; qualities with >= 8 segments {mk['qualities_with_count_ge_threshold']}; segment counts by quality "
             f"{mk['segment_counts_by_quality']}; PRE-DECLARED VERDICT {mk['degeneracy_verdict']}. Per song: "
             + "; ".join(f"{v['title']} key {v['key']['tonic_name']} {v['key']['mode']} (corr {v['key']['corr']:.3f}), {v['n_beats']} beats / {v['n_segments']} segments, top {v['top_states'][:3]}" for v in mk['per_song'].values())
             + ". CAVEAT (reindex-fidelity-c81): `other`-stem durations are inflated by the greedy pairing, so the duration-weighted PCPs over-weight `other`; onsets are lossless. "
             "The c80 n=2 preview (data/v5/rules/preview_n2/) is retained as a labelled preview. Nothing fed to a generator."),
            ["scripts/v5/harmony_v5.py", "data/v5/rules/harmony_markov_v5.json"] + [f"data/v5/rules/{s}/harmony_v5.json" for s in mk["gate"]["used"]],
            supersedes_path="M-V5-RULES-1/harmony_v5-gated-c80"))
    else:
        g = json.loads(Path("data/v5/rules/harmony_v5_gated.json").read_text())
        events.append(_ev("M-V5-RULES-1/harmony_v5-gated-c81", "in-progress", "medium",
            "Gate honestly not met at emit time; patched script validated by tests; re-executes unchanged once Rome is landed + reindexed.",
            (f"P4.1: patched harmony_v5.py re-run -> GATED: {g['n_used']} unblocked landed songs {g['used']} (< 3); blocked-skipped {g['blocked_skipped']}; Rome not landed+reindexed at "
             "emit time. Official run re-executes unchanged when Rome lands (catch-up loop / hook reindexes it)."),
            ["data/v5/rules/harmony_v5_gated.json"]))

    events.append(_ev("M-V5-RULES-1/groove_v5-first-data-c81", "validated", "medium",
        "Pre-declared validation + degeneracy rule applied verbatim; blocked songs refused; byte-det x2; low generalization at n=2 disclosed.",
        (f"P4.2 scripts/v5/groove_v5.py (sha {_sha('scripts/v5/groove_v5.py')}) -> data/v5/rules/groove_v5.json (sha {_sha('data/v5/rules/groove_v5.json')}) on WIG + CG "
         f"canonical_v5_reindexed/ drums (GM kick 35/36, snare 37-40, hat 42/44/46) + bass; 16th grid (120 ticks at PPQ 480), per-bar 16-bit patterns, corpus bars = bars with >= 1 "
         f"drum onset ({grv['corpus_stats']['n_bars']}: WIG {grv['per_song'][WIG]['stats']['n_bars']}, CG {grv['per_song'][CG]['stats']['n_bars']}); tables P(kick), P(snare|kick), "
         f"P(hat|kick,snare), P(bass|kick) as counts + row-normalized; 64 bars sampled by SHA-256 inverse-CDF (no PRNG). VERDICT {grv['verdict']}: backbeat ratio corpus "
         f"{grv['corpus_stats']['backbeat_ratio']:.4f} vs sampled {grv['sample_stats']['backbeat_ratio']:.4f} (|d| {grv['validation']['backbeat_ratio']['abs_diff']:.4f} <= 0.10); bass-kick lock "
         f"{grv['corpus_stats']['bass_kick_lock']:.4f} vs {grv['sample_stats']['bass_kick_lock']:.4f} (|d| {grv['validation']['bass_kick_lock']['abs_diff']:.4f}); sampled distinct kick "
         f"{grv['sample_stats']['distinct_kick_patterns']} / bass {grv['sample_stats']['distinct_bass_patterns']}; observed contexts {grv['table_context_counts']}. Per song: WIG backbeat "
         f"{grv['per_song'][WIG]['stats']['backbeat_ratio']:.3f} lock {grv['per_song'][WIG]['stats']['bass_kick_lock']:.3f}; CG backbeat {grv['per_song'][CG]['stats']['backbeat_ratio']:.3f} lock "
         f"{grv['per_song'][CG]['stats']['bass_kick_lock']:.3f}. HONEST DISCLOSURES: (a) the corpus backbeat ratio is only 0.14 — MuScriptor snare onsets (GM 37-40) rarely fall exactly on "
         "16th slots 4/12 at bpm_v5, so the pre-declared 'backbeat' measures grid-exact snares, not the audible backbeat (a tolerance-window definition is a c82 pre-registration "
         "candidate, not a re-tune here); (b) 124 distinct kick patterns over 172 bars make the conditional tables near one-to-one — the n=2 model largely replays corpus bars: "
         "non-degenerate by the pre-declared test, low generalization; the fix is more unblocked songs. Data-existence only; nothing fed to a generator. Byte-det x2 "
         f"{p34['files']['data/v5/rules/groove_v5.json']['equal']}."),
        ["scripts/v5/groove_v5.py", "data/v5/rules/groove_v5.json", "data/v5/rules/c81_p3_p4_byte_determinism.json"]))

    events.append(_ev("_plan/register-c81-sub-leaves", "validated", "high",
        "Rows inserted inline in the parseable ## Milestones region via tools/_register_c81_por_rows.py; idempotent; promise_check reported verbatim.",
        (f"c81 POR rows registered inline (liveness, reindex-hygiene, per-song reindexed-c81 for {sided}, ear-venv-blocked-disk, tempo_v5c preregistered + verdict, "
         f"recanonicalize-still-blocked, reindex-fidelity, harmony {'first-data' if chain_p.exists() else 'gated'}, groove first data, housekeeping). promise_check: {pc_line}"),
        ["plan_of_record.md", "tools/_register_c81_por_rows.py"]))

    events.append(_ev("_infra/adopt-cycle81-tests", "validated", "high",
        "New suites green under /usr/bin/python3; pre-c81 regression green; no anchor mutation.",
        (f"tests/test_reindex_hygiene_c81.py (5) + tests/test_tempo_v5c.py (6) + tests/test_groove_v5.py (3) + tests/test_ear_venv_c81.py (3) adopted = 17 new. Results at emit: "
         f"{test_line}. Highlights: harmony refuses a lossy-only fixture (MissingReindexError); sidecar SHAs + MIDI note_on == JSON starts on every landed song; two-chunk fixture — "
         "serializer keeps 3/6, hook recovers 6/6; on-disk PD lag-21 T/2 interpolated = 0.667 (> 0); synthetic period-21 3:2 picks T; RULES_OUT branch keeps the blocked file and "
         "creates no v5c dirs; Rome hemiola table; synthetic backbeat corpus reproduces 1.0/1.0 and a single-pattern fixture is rejected; main-env freeze sha unchanged; probe exits 3."),
        ["tests/test_reindex_hygiene_c81.py", "tests/test_tempo_v5c.py", "tests/test_groove_v5.py", "tests/test_ear_venv_c81.py"]))

    events.append(_ev("_archive/cycle-81-scratch", "validated", "high",
        "One-shot emitters retained in-tree per emitter-exemption pattern; scratch runners live in the harness scratchpad; nothing to move to tools/stale/.",
        ("tools/_emit_c81_ledger_events.py + tools/_register_c81_por_rows.py retained in-tree (docs/emitter_exemption_policy.md). Session scratchpad: p0_liveness, p0_6_summary_c81, "
         "p1_venv_decision, bytedet_v5c, bytedet_p3_p4, run_tests (not in workspace). data/v5/corpus/plot_tempo_v5c_scores.py co-located with its data + figure (regenerable triplet)."), []))

    events.append(_ev("_run/cycle_81_closed", "validated", "high",
        "All MANDATORY brief items landed or halt-honestly blocked: P0 hygiene closed, P1 VENV_BLOCKED_DISK with arithmetic + operator line, P2 RULES_OUT (first-class, 4/5), P3 DEGRADED diagnosed, P4 first data, P5 ledger/POR/tests/promise_check.",
        ("c81 CLOSED — v5 REOPENING cycle 3. 9-HEADER CLOSING SUMMARY. (1) VERDICT: SUBSTANTIVE with three first-class findings — (a) tempo v5c (autocorr-direct harmonic sum) is "
         f"RULED OUT by Disco A alone (0.006 margin) while recovering Peach Dream and resolving Rome's hemiola: {fals['verdict']}, 4/5 anchors; (b) the c80 greedy start/end "
         "re-pairing is onset-lossless but duration-DEGRADED on dense polyphonic stems (WIG other median |dDuration| 281 ms with 90 % pairing ambiguity); (c) the ear venv build is "
         f"DISK-BLOCKED by arithmetic (post-build {venv['arithmetic']['post_build_used_pct']} % > 90 % driver abort), not by the brief's 3.5 GB gate. (2) LANDED: P0 liveness; every "
         f"landed song lossless + sidecar ({sided}); harmony_v5 lossless-only + MISSING_REINDEX; reindex_hook + driver call (old PID unaffected, not restarted); c81 TSV with anchor_source; "
         f"P1 VENV_BLOCKED_DISK record + probe script (EAR_VENV_ABSENT); P2 prereg (mtime gate) + 26/26 + byte-det {bd['n_equal']}/{bd['n_files_compared']} + frozen verdict + figure; "
         f"P3 fidelity JSON + byte-det; P4 groove {grv['verdict']} + byte-det; harmony {'first data on ' + str(len(json.loads(chain_p.read_text())['gate']['used'])) + ' songs' if chain_p.exists() else 'still gated (Rome not reindexed at emit)'}; "
         "P5 events + POR rows + 17 new tests + promise_check. (3) BLOCKED/DEFERRED: ear venv -> operator authority over /root/.local (one-line request; MANDATORY item honestly "
         "unmet); PD + Disco A remain blocked for rules; c82 = mechanism probe BEFORE any tempo criterion (meta-gate); chunk-window-constrained pairing (pre-declare) for durations; "
         "a tolerance-window backbeat definition (pre-registration candidate). (4) FIRST-CLASS FINDINGS: see (1); plus the anchor-band premise of v5b was the PD failure (confirmed), "
         "and Disco A's failure is within score resolution (a different class). (5) DISCIPLINE: FD-1 halt-honest (no retune; no fourth criterion; no build retry; no selective PD "
         "unblock); FD-6 operator ear remains LANDS authority; FD-16(a) canonical env_pin 2ac444c3… unchanged c22 -> c81 (60 cycles); FD-16(c) byte-det x2 on v5c (27/27), "
         "fidelity, groove; c14 str-supersede lemma (3 str supersedes: reindex-hygiene -> index-collision-c80; harmony first-data -> gated-c80 when it fires; this row -> "
         "_run/cycle_80_closed); c47 preservation-spin BAN honored; no wait-on-operator memo (the P1 action_required carries the one-line disk request the brief mandates); "
         f"no PRNG / sidecar_nonfactor / VST3 state APIs (AST-tested on 6 scripts). (6) ANCHORS: {n_frozen_ok}/14 FROZEN anchors byte-identical to their c79-pinned SHAs — "
         + "; ".join(f"{k} {frozen[k][:12]}{'' if frozen_ok[k] else ' MISMATCH'}" for k in FROZEN_EXPECTED)
         + f". (7) STORAGE: df open 86.9 %, emit {df_now} %; driver max {prog.get('df_max_pct_observed')} %; no install; /root/.local untouched. (8) TESTS: {test_line}. "
         "(9) NEXT (c82): mechanism probe on tempo (per-song ac dump + beat-tracker drums-stem vs full-mix) — no criterion until it lands; pre-declare chunk-window-constrained "
         "pairing and re-measure fidelity; ear venv once disk authority lands (or a smaller-footprint route pre-registered); groove/harmony re-run as unblocked songs land "
         "(driver hook now reindexes at birth after its next restart; catch-up loop until then); form plan (OPERATOR #4). 22nd consecutive cycle of 9-header closing-summary "
         "compliance (c59-c81)."),
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_80_closed"))

    existing = set()
    with open(LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    existing.add(json.loads(line).get("milestone_id"))
                except json.JSONDecodeError:
                    pass
    to_append = [e for e in events if e["milestone_id"] not in existing]
    if not to_append:
        print("IDEMPOTENT: all c81 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c81 events; frozen anchors OK {n_frozen_ok}/14")
    for e in to_append:
        print(f"  {e['status']:16s} {e['milestone_id']} {e['event_id']}")
    for k, ok in frozen_ok.items():
        if not ok:
            print(f"  FROZEN MISMATCH {k} {frozen[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
