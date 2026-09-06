#!/usr/bin/python3
"""c79 one-shot ledger emitter — v5 REOPENING cycle 1 (corpus foundations).

Emits (per c79 research brief §P5), reading on-disk artifact SHAs at emit time:
  1. _plan/adopt-operator-v5-reopening-directive-2026-09-06 (validated; str-supersedes _run/cycle_78_closed)
  2. _plan/operator-decisions-c79-amendment (validated)
  3. M-V5-CORPUS-1/corpus-manifest-emitted-c79 (validated)
  4. M-V5-CORPUS-1/tempo-v5-halt-honest-c79 (validated; first-class negative — frozen criterion RULES OUT)
  5. M-V5-CORPUS-1/full-length-transcription-launched-c79 (in-progress)
  6. M-V5-CORPUS-1/<song>-transcribed-c79 for each song finished in-cycle (validated)
  7. M-V5-EAR-1/ear-venv-probe-c79 (validated; venv built+verified then reclaimed for disk hygiene)
  8. _plan/register-c79-v5-reopening-sub-leaves (validated)
  9. _infra/adopt-cycle79-tests (validated)
 10. _archive/cycle-79-scratch (validated)
 11. _run/cycle_79_closed (validated)

UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts) per c14+ convention.
Idempotent by milestone_id. Retained in-tree per docs/emitter_exemption_policy.md
(`long_exposure/` is absent from this workspace; c34 OPT_B exemption).
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
CYCLE = 79
RUN_ID = "run-2026-09-06T000000Z"
TS = "2026-09-06T15:30:00Z"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"


def _sha(p: str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _sha_or(p: str) -> str:
    return _sha(p) if Path(p).exists() else "ABSENT"


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _event_id(body: dict) -> str:
    payload = {k: v for k, v in body.items() if k not in ("event_id", "ts")}
    return str(uuid.uuid5(uuid.NAMESPACE_URL, _canonical(payload)))


def _ev(milestone_id, status, level, rationale, narrative, artifacts, supersedes_path=None):
    body = {"artifacts": artifacts,
            "confidence": {"assessor": "worker", "level": level, "rationale": rationale},
            "cycle": CYCLE, "env_pin_sha256": ENV_PIN, "milestone_id": milestone_id,
            "narrative": narrative, "run_id": RUN_ID, "status": status,
            "supersedes_path": supersedes_path, "ts": TS}
    body["event_id"] = _event_id(body)
    return body


def main() -> int:
    man = json.loads(Path("data/v5/corpus/corpus_manifest.json").read_text())
    fals = json.loads(Path("data/v5/corpus/tempo_v5_falsification.json").read_text())
    bd = json.loads(Path("data/v5/corpus/tempo_v5_byte_determinism.json").read_text())
    launch = json.loads(Path("data/v5/logs/transcribe_full_c79.launch.json").read_text())
    prog_p = Path("data/v5/corpus/transcription_progress.json")
    prog = json.loads(prog_p.read_text()) if prog_p.exists() else {"songs": {}}
    earpin = json.loads(Path("data/v5/ear/env_pin_ear_venv.json").read_text())
    done = [s for s, v in prog.get("songs", {}).items() if v.get("status") == "done"]
    failed = {s: v for s, v in prog.get("songs", {}).items() if v.get("status") == "failed"}
    by_sha = {s["sha16"]: s for s in man["songs"]}
    df_max = prog.get("df_max_pct_observed")
    opdec_sha = _sha("docs/OPERATOR_DECISIONS.md")
    tempo_shas = {s["sha16"]: _sha(f"data/v5/corpus/{s['sha16']}/tempo_v5.json") for s in man["songs"]}

    events = []
    events.append(_ev(
        "_plan/adopt-operator-v5-reopening-directive-2026-09-06", "validated", "high",
        "Operator guidance received verbatim via live_guidance; adoption recorded on disk (OPERATOR_DECISIONS #20, POR M-V5-* rows, stall counter) at cycle open.",
        ("c79 adopts OPERATOR GUIDANCE 2026-09-06 (V5 RULES/GENERATION REOPENING). CONTEXT (verbatim): the operator evaluated the 15 "
         "generated candidates: QUALITY VERDICT POOR ('sound very strange'). Binding diagnosis: rules extracted from only ~66 bars (one 30 s "
         "section per song); harmony modeled as raw per-bar pitch-class dumps (near-unique states = random-walk dissonance); groove modeled "
         "as per-slot histograms averaged over bars (backbeat and kick/snare/bass-lock structure erased; drums merged into one stream); "
         "other/piano stems absent from rules inputs (transcribed to zero notes); WIG bpm 50.17 is a half-time mis-estimate; no "
         "repetition/motif structure; no working ear filter. The campaign REOPENS ONLY M-V4-RULES, M-V4-EAR, M-V4-GEN as v5 iterations — "
         "profiles, recreations, showcase, and certificates remain CLOSED and FROZEN. DECISIONS 1-8 (verbatim in docs/OPERATOR_DECISIONS.md #20): "
         "(1) CORPUS five focus songs full-length + remaining band-6/7 songs full-length via the checkpointed driver; fix tempo estimation; "
         "(2) HARMONY root+quality templates, common-key transposition, functional Markov chain; (3) GROOVE joint conditional model with "
         "kick/snare/hat split + cross-stem conditionals, degenerate models rejected honestly; (4) STRUCTURE section form plan with forced "
         "literal repetition; (5) EAR isolated venv, restored exemplar ear + >=6 gate, band-4-vs-band-7 fallback; (6) GENERATION groove-first; "
         "(7) TARGET 5 songs at ear >=6 + interpolation demo REQUIRED, stall budget 12, best samples to data/v4/generated/v5_iter_NN/; "
         "(8) all standing v4 doctrine in force; amend completion report and re-close cleanly. CYCLE-COUNTER DISCLOSURE (invariant d): the "
         "operator note says the run 'was hard-stopped at c87 during close-out'; the on-disk ledger's last cycle is 78 (tail 1977, "
         "_run/cycle_78_closed validated), so this reopening cycle is numbered c79 per on-disk reality; the c87 figure is presumed an "
         "orchestrator-side count and is disclosed, not reconciled. FROZEN (READ-ONLY): M-V4-CERT-1, M-V4-PROFILES-1, M-V4-SHOWCASE-1, "
         "data/v4/deliveries/**, data/v4/profiles/**, data/v3/deliveries/**, docs/v3_determinism_certificate.md (sha a6876911…), "
         "scripts/gen/iterate_v4.py (8f1f0b88…), scripts/gen/interpolate_v4.py (2359f35d…), scripts/ear/v4_ear*.py (e775621b…). "
         "This event str-supersedes _run/cycle_78_closed ONLY in its 'run ends here' clause (operator resume); c77/c78 verdict matrices stand. "
         "Generator stall counter reset: data/v5/gen/stall_counter.json = iterations 0 / budget 12 / passers 0 / target 5."),
        ["docs/OPERATOR_DECISIONS.md", "data/v5/gen/stall_counter.json", "plan_of_record.md"],
        supersedes_path="_run/cycle_78_closed"))

    events.append(_ev(
        "_plan/operator-decisions-c79-amendment", "validated", "high",
        "Additive append; pre/post SHAs pinned; no prior entry modified.",
        (f"docs/OPERATOR_DECISIONS.md entry #20 appended (v5 reopening verbatim + c79 first-cycle disclosures). Pre-append sha "
         f"b563caee0f81db969035674b20432d018424eb563dbd6102beb4e8b81dd0410b; post-append sha {opdec_sha}. Entries #1-#19 and the "
         "Standing constraints section unchanged."),
        ["docs/OPERATOR_DECISIONS.md"]))

    cd = man["count_disclosure"]
    events.append(_ev(
        "M-V5-CORPUS-1/corpus-manifest-emitted-c79", "validated", "high",
        "Byte-deterministic x2 (identical sha on two runs); every receipt-listed band-6/7 mp3 hashed; discrepancy vs operator count disclosed.",
        (f"scripts/v5/corpus_manifest.py -> data/v5/corpus/corpus_manifest.json sha {_sha('data/v5/corpus/corpus_manifest.json')} "
         f"(byte-det x2). Enumerated {cd['total_enumerated']} songs: band-6 {cd['band6_on_disk']} + band-7 {cd['band7_on_disk']} + "
         f"{cd['focus_songs_in_band5']} focus songs that live in BAND 5 (WIG 252eb21c…, Rome 51e433ad…, Disco A cdd2717e… per "
         "corpus/ratings/5/RECEIPTS.md). Operator decision #1 said '~7 total'; the receipts undercount is ~19 songs — all are marked "
         "in_v5_corpus=true with a deterministic priority order (focus[WIG,CG,PD,Rome,DiscoA] -> v4 ear exemplars[Essence,Desire,Molasses] "
         "-> 7 band-7 extras -> 11 band-6 extras; SHA-256('v5corpus|sha16') tiebreak within tier; no PRNG); transcription lands in that "
         "order, nothing truncated. ASSET INVENTORY FINDING (invariant d): NO full-song htdemucs_6s stems exist on disk for ANY song — every "
         "rc9_6stem / stems_6s / _run1_stems directory holds 30 s operator-section stems (~5.29 MB per stem); the brief's premise that "
         "Rome (c20) / Disco A (c21) full-song stems were cached is not borne out (their ledger narratives recorded SHAs but the WAVs "
         "were not retained). Existing MuScriptor JSONs are all 30 s sections (WIG 7, CG 35, PD 59, Rome 14, Disco A 14, others 0). "
         "Tempo anchors come from on-disk tempo_choice.json files; the brief's data/recreate_v2/baseline/<sha16>/rc5_tempo_bpm.json "
         "path is ABSENT on this instance."),
        ["scripts/v5/corpus_manifest.py", "data/v5/corpus/corpus_manifest.json"]))

    ps = fals["per_song"]
    events.append(_ev(
        "M-V5-CORPUS-1/tempo-v5-halt-honest-c79", "validated", "high",
        "Frozen falsification targets evaluated verbatim; RULES-OUT clause fired on two anchored songs; criterion not adjusted (FD-1). Byte-det x2 27/27.",
        (f"scripts/v5/tempo_v5.py (pre-registered: onset-strength hop 512 @ 22050; librosa beat_track baseline; candidates = librosa x {{0.5,1,2,4/3,3/4}} "
         f"U top-3 autocorr peaks in [70,180]; score = normalized autocorr at lag (max over +/-2% lag window) x plausibility weight; SHA-256 tiebreak) "
         f"ran on all 26 songs; 26 tempo_v5.json + tempo_v5_summary.tsv (sha {_sha('data/v5/corpus/tempo_v5_summary.tsv')}) byte-det x2 "
         f"({bd['n_equal']}/{bd['n_files_compared']} files; data/v5/corpus/tempo_v5_byte_determinism.json). FROZEN VERDICT = {fals['verdict']}. "
         f"Anchored songs: CG librosa 92.285 -> v5 92.285 (delta {ps['31a164f845f8e27e']['delta_bpm']:+.3f} vs rc5 90.726, within 2) PASS; "
         f"Rome 151.999 -> 151.999 (delta 0.000) PASS; Peach Dream librosa 123.047 (= anchor) -> v5 80.750 via ac_peak_1 (delta "
         f"{ps['88d247468cb6d49f']['delta_bpm']:+.3f}, ratio 0.656, NON-octave) FAIL; Disco A librosa 123.047 -> v5 80.750 (delta "
         f"{ps['cdd2717e52820ff6']['delta_bpm']:+.3f} vs 120.185, ratio 0.672, NON-octave) FAIL. Pre-registered RULES-OUT clause ('any anchored song "
         "regresses by a non-octave factor > 2 BPM => criterion too permissive; report the failing lag table') FIRED — the raw onset "
         "autocorrelation is a decaying function without metrical hierarchy and the 3:2-related lag (lag 32 = 80.75 BPM) out-scores the "
         "anchored lag (lag 21 = 123.05 BPM). Failing lag tables are in data/v5/corpus/tempo_v5_falsification.json; figure "
         "data/v5/corpus/fig_tempo_v5_autocorr.png (regenerable from plot_tempo_v5_autocorr.py). WIG FINDING: on the FULL-LENGTH mix librosa "
         f"already returns {ps['252eb21ce7df7328']['bpm_librosa_full_length']:.3f} BPM (v5 = same); the c20 50.17 value was librosa on the 30 s "
         "DRUMS STEM of the operator section (v3 tempo_map prefers the drums stem). The mechanism probe on that same drums stem "
         "(data/v5/corpus/252eb21ce7df7328/tempo_v5_wig_mechanism_probe.json) gives librosa 49.692 -> v5 99.384 via librosa_x_double, resolved by "
         "the plausibility band (49.69 has weight 0), NOT by autocorrelation dominance: ac(2T)/ac(T) = 0.321 on the drums stem and 1.045 on "
         "the full mix, so the strict RULES-IN clause ('2T exceeds T by >= 10 %') is NOT met. Mechanism verdict: stem-choice + band artifact, not "
         "a prior octave-bias on the mix. LAG-QUANTIZATION DISCLOSURE: all librosa tempi here are integer-lag quantized (lag 21 = 123.047, "
         "lag 22 = 117.454, lag 26 = 99.384, lag 32 = 80.750), ~5 BPM resolution near 120, so the PD/Disco A anchors carry the same quantization. "
         "Corpus-wide: 17/26 songs keep librosa (same), 9/26 move (7 via ac_peak, 1 three_quarters, 1 half). NO RETUNE this cycle; c80 "
         "pre-registers a metrically-aware criterion (tempogram / comb-filter with harmonic weighting) before any revision. Transcription proceeds "
         "with bpm_v5 per the brief's Rung-3 rule (MuScriptor JSON is tempo-independent; canonical MIDI re-serializes from cached JSON)."),
        ["scripts/v5/tempo_v5.py", "scripts/v5/tempo_v5_verdict.py", "data/v5/corpus/tempo_v5_summary.tsv",
         "data/v5/corpus/tempo_v5_falsification.json", "data/v5/corpus/tempo_v5_byte_determinism.json",
         "data/v5/corpus/fig_tempo_v5_autocorr.png", "data/v5/corpus/plot_tempo_v5_autocorr.py",
         "data/v5/corpus/252eb21ce7df7328/tempo_v5_wig_mechanism_probe.json"]
        + [f"data/v5/corpus/{s}/tempo_v5.json" for s in tempo_shas]))

    events.append(_ev(
        "M-V5-CORPUS-1/full-length-transcription-launched-c79", "in-progress", "high",
        "Detached launch verified running; per-stage cache manifests land under data/v5/corpus/<sha16>/stage_cache/; completion rolls to c80 from cache.",
        (f"scripts/v5/transcribe_full_length.py launched detached at {launch['launched_utc']} PID {launch['pid']} "
         f"(via READ-ONLY scripts/v3_spine/launch_detached.launch_detached, start_new_session=True — `setsid` is blocked by the sandbox), "
         f"log data/v5/logs/transcribe_full_c79.log, launch record data/v5/logs/transcribe_full_c79.launch.json. Pipeline per song: "
         "decode_full (ffmpeg 44.1k/16-bit stereo, transient) -> htdemucs_6s full-length (READ-ONLY recreate_v3._run_htdemucs_once) -> "
         "MuScriptor x7 probes (drums/bass/guitar/other/piano/vocals/full_mix; chunked 30 s / 5 s overlap via READ-ONLY recreate_v3._muscriptor_chunked, "
         "4 single-threaded workers; c3 vocab whitelists from docs/specs/v3_spine_instrument_whitelist_mapping.md incl. other = synth_lead,"
         "synth_pad,synth_strings,orchestra_hit,chromatic_percussion and vocals = voice) -> canonicalize (READ-ONLY c4 serializer at bpm_v5, "
         "4/4; never librosa default, never 120) -> transcription_manifest.json (per-stem note counts, drums by GM class kick 35/36 snare 37-40 "
         "hat 42/44/46, other/piano counts explicit, bar count at bpm_v5, stage-cache keys) -> delete transient full-length audio. Each stage keyed "
         f"by stage_cache.compute_key(stage, inputs, env_pin) with env_pin = build_env_pin_manifest()['env_pin_sha256'] = "
         f"{launch.get('env_pin_cache', prog.get('env_pin_sha256_cache_key', 'see progress.json'))} (differs from the FROZEN v4 cert pin 623df01f… by design — "
         "drift-detectable; the canonical 7-key pin 2ac444c3… is unchanged). MuScriptor per-probe caching makes a session-boundary kill lose "
         "at most one probe. HYGIENE: songs sequential; df checked before every stage (85 % warn / 90 % abort); the c27 df_guard prune step is "
         "deliberately NOT called because it deletes data/v4/profiles/**/*_sweep_stage*/*.wav which are FROZEN under this reopening; transient "
         "audio (full.wav + 6 stems, ~230 MB for WIG) is deleted after canonicalize; verify_det x2 not run in-line (would double a multi-hour "
         f"job; stage-cache manifests are the determinism record per c24 doctrine). Order = v5_priority_rank (WIG first). Songs done in-cycle: "
         f"{len(done)} {done}; failed: {failed if failed else 'none'}; df max observed {df_max}%. Observed WIG timings: htdemucs_6s 181 s for "
         "186 s of audio (~1x realtime, 1 torch thread). RESUME COMMAND (cache-resumable, idempotent): "
         f"{launch['resume_command']}"),
        ["scripts/v5/transcribe_full_length.py", "data/v5/logs/transcribe_full_c79.log",
         "data/v5/logs/transcribe_full_c79.launch.json", "data/v5/corpus/transcription_progress.json"]))

    for s in done:
        tm = json.loads(Path(f"data/v5/corpus/{s}/transcription_manifest.json").read_text())
        nc = {p: tm["note_counts"][p]["n_note_on"] for p in tm["note_counts"]}
        gm = tm["note_counts"]["drums"].get("gm_classes", {})
        events.append(_ev(
            f"M-V5-CORPUS-1/{s}-transcribed-c79", "validated", "high",
            "Full-length transcription completed with per-stem note counts and stage-cache keys; transient audio deleted; canonical MIDI at bpm_v5.",
            (f"{by_sha[s]['title']} ({s}, {tm['duration_s']} s, bpm_v5 {tm['bpm_v5']}): per-stem note_on counts {nc}; drums GM classes {gm}; "
             f"other/piano zero-finding: {tm['other_piano_zero_finding']}; bars at bpm_v5 = {tm['bar_count_at_bpm_v5']}; stage wall: "
             f"htdemucs {tm['stages']['htdemucs_6s'].get('wall_s')} s, muscriptor { {p: v.get('wall_s') for p, v in tm['stages']['muscriptor'].items()} }; "
             f"stage-cache keys {tm['cache_keys']}; transient audio deleted: {len(tm['transient_audio_deleted'])} files "
             f"({sum(d['bytes'] for d in tm['transient_audio_deleted'])/1e6:.0f} MB); df max {tm['df_max_pct_observed_so_far']}%. "
             f"Kept on disk: muscriptor_full/*.json + canonical_midi_full/*.mid + tempo_v5.json + transcription_manifest.json under data/v5/corpus/{s}/. "
             + ("TEMPO CAVEAT: this song's bpm_v5 disagrees with a librosa-matched anchor by a non-octave factor (see tempo-v5-halt-honest-c79); "
                "canonical MIDI is re-serializable from cached JSON once c80 revises the tempo criterion." if s in fals["failing_songs"] else "")),
            [f"data/v5/corpus/{s}/transcription_manifest.json"] + [f"data/v5/corpus/{s}/muscriptor_full/{p}.json" for p in nc]
            + [f"data/v5/corpus/{s}/canonical_midi_full/{p}.mid" for p in nc]))

    events.append(_ev(
        "M-V5-EAR-1/ear-venv-probe-c79", "validated", "medium",
        "Fetchability established (venv built, imports verified, pip-freeze receipt pinned); inference probe deferred for disk hygiene; main env untouched (freeze SHA pre==post).",
        (f"P4 one attempt: `{earpin['build_command']}` succeeded through the proxy in ~55 s (data/v5/logs/ear_venv_build_c79.log): numpy 1.26.4, "
         "tensorflow 2.21.0, tensorflow_hub 0.16.1, pyloudnorm 0.2.0, import probe OK (no CUDA, CPU). The install pushed df to 93 % (> the binding "
         "90 % abort ceiling) while the MANDATORY P3 transcription was running, so after capturing receipts (data/v5/ear/ear_venv_pip_freeze.txt sha "
         f"{earpin['pip_freeze_sha256']}, {earpin['n_packages']} packages; data/v5/ear/env_pin_ear_venv.json; 4 rows appended to "
         "data/v5/ear/fetchability_ladder.jsonl) the 2.3 GB venv was REMOVED (df -> 86.1 %). /root/.local (2.8 GB; c75 tensorflow pollution of the "
         "main interpreter's user-site) is outside the workspace and was left untouched pending operator adjudication. VGGish inference probe vs "
         "data/v4/ear/exemplar_embeddings.npz NOT run this cycle (DEFERRED_DISK; tfhub weights ~280 MB); CLAP not attempted (gated on VGGish). "
         "Main-env `pip freeze` sha 90ed1d9f0fd0a33e3be35653bf541f82ceadcd4d89c0013b9cdd0228544d639d pre == post. Rebuild is deterministic from "
         "the pinned command; P4 remains MANDATORY by c81 (brief) and the disk headroom question is handed to c80."),
        ["data/v5/ear/env_pin_ear_venv.json", "data/v5/ear/ear_venv_pip_freeze.txt", "data/v5/ear/fetchability_ladder.jsonl",
         "data/v5/logs/ear_venv_build_c79.log"]))

    events.append(_ev(
        "_plan/register-c79-v5-reopening-sub-leaves", "validated", "high",
        "Rows inserted inline in the parseable ## Milestones region (before ## Sub-milestones) via tools/_register_c79_por_rows.py; idempotent.",
        ("15 POR rows registered: 5 M-V5-* parents (CORPUS-1 depends M-V3-SPINE-2/stage-checkpointed-driver; RULES-1 depends CORPUS-1 and supersedes "
         "M-V4-RULES-1 semantics; EAR-1 depends M-V4-EAR-1 anchors READ-ONLY; GEN-1 depends RULES-1 + EAR-1 with stall budget 12; CLOSE-1 depends "
         "GEN-1) + 10 c79 sub-leaves/housekeeping ids. promise_check itself is not runnable in this workspace (`long_exposure/` absent — c34 OPT_B "
         "exemption); parser-boundary discipline (rows before ## Sub-milestones) is preserved."),
        ["plan_of_record.md", "tools/_register_c79_por_rows.py"]))

    events.append(_ev(
        "_infra/adopt-cycle79-tests", "validated", "high",
        "New suite 7/7 green under /usr/bin/python3; 35/35 pre-c79 regression green; no anchor mutation.",
        ("tests/test_tempo_v5.py 7/7 PASS: test_01 WIG not half-time (full 99.384; drums-section probe 49.692 -> 99.384); test_02 CG within 2 BPM "
         "(delta +1.559); test_03 PD frozen target recorded halt-honest (FAILED on disk; verdict RULES_OUT_CRITERION_TOO_PERMISSIVE asserted, "
         "target not relaxed); test_04 octave candidate set + plausibility weights; test_05 fresh-subprocess byte-det on 069ebba269efccc2 + corpus-wide "
         "27/27; test_06 AST scan (no PRNG / sidecar_nonfactor / VST3 state APIs; interpreter guards on 4 scripts); test_07 env_pin canonical + "
         "manifest shape (26 songs, WIG first). Regression: test_gen_interpolate_v4 6 + test_ear_v2_calibration_c76 9 + test_ear_batch_scoring_c75 8 + "
         "test_ear_v4_scaffold 5 + test_gen_iterate_v4 7 = 35/35 -> cross-cycle 42/42."),
        ["tests/test_tempo_v5.py"]))

    events.append(_ev(
        "_archive/cycle-79-scratch", "validated", "high",
        "One-shot emitters retained in-tree per emitter-exemption pattern; transient audio deleted by the driver; nothing to move to tools/stale/.",
        ("tools/_emit_c79_ledger_events.py + tools/_register_c79_por_rows.py retained in-tree (docs/emitter_exemption_policy.md sha fd2c33a7…). "
         "Session-scoped scratchpad probes (inventory, tempo x2 runner, launcher, venv build/reclaim) live under the harness scratchpad, not the "
         "workspace. Transient full-length audio is deleted per song by the driver; workspace/ear_venv removed for hygiene with receipts kept."),
        []))

    frozen = {
        "docs/v3_determinism_certificate.md": _sha("docs/v3_determinism_certificate.md"),
        "data/v3/rules/rules_artifact.jsonl": _sha("data/v3/rules/rules_artifact.jsonl"),
        "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav": _sha("data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav"),
        "data/v4/profiles/31a164f845f8e27e/bass_v2.json": _sha("data/v4/profiles/31a164f845f8e27e/bass_v2.json"),
        "data/v4/profiles/88d247468cb6d49f/stem_manifest.json": _sha("data/v4/profiles/88d247468cb6d49f/stem_manifest.json"),
        "data/v4/ear/exemplar_set.json": _sha("data/v4/ear/exemplar_set.json"),
        "scripts/ear/v4_ear.py": _sha("scripts/ear/v4_ear.py"),
        "scripts/gen/iterate_v4.py": _sha("scripts/gen/iterate_v4.py"),
        "scripts/gen/interpolate_v4.py": _sha("scripts/gen/interpolate_v4.py"),
        "scripts/v3_spine/recreate_v3.py": _sha("scripts/v3_spine/recreate_v3.py"),
        "scripts/v3_spine/stage_cache.py": _sha("scripts/v3_spine/stage_cache.py"),
        "scripts/v3_spine/midi_from_json_events.py": _sha("scripts/v3_spine/midi_from_json_events.py"),
        "docs/v4_completion_report_v3.md": _sha("docs/v4_completion_report_v3.md"),
    }
    events.append(_ev(
        "_run/cycle_79_closed", "validated", "high",
        "All MANDATORY briefs items landed (P0/P1/P2/P3-launch/P5); P2 verdict is a first-class negative per FD-1; P4 optional probe landed with honest deferral of inference.",
        ("c79 CLOSED — v5 REOPENING cycle 1 (corpus foundations). 9-HEADER CLOSING SUMMARY. (1) VERDICT: SUBSTANTIVE — corpus manifest + tempo v5 "
         "(halt-honest RULES-OUT) + full-length transcription LAUNCHED detached; campaign reopened for RULES/EAR/GEN only. (2) LANDED: P0 adoption "
         "(OPERATOR_DECISIONS #20 pre b563caee… post " + opdec_sha[:16] + "…; 15 POR rows; stall counter 0/12; c87-vs-c78 counter disclosure); "
         f"P1 corpus_manifest.json ({cd['total_enumerated']} songs, byte-det x2, ~7 -> 26 count disclosure, no full-length stems on disk); P2 tempo_v5 "
         f"26 songs byte-det x2 27/27, verdict {fals['verdict']} (PD 123.05 -> 80.75, Disco A 123.05 -> 80.75; CG/Rome hold; WIG full-length = 99.38 "
         "with the c20 50.17 traced to the drums-stem section), figure + lag tables; P3 transcribe_full_length.py launched PID "
         f"{launch['pid']} (WIG htdemucs 181 s; songs done in-cycle {done}); P4 ear venv BUILT+VERIFIED (numpy 1.26.4 / tf 2.21.0 / hub 0.16.1) then "
         "reclaimed for disk hygiene with receipts; P5 11+ events, 7/7 new tests, 42/42 cross-cycle. (3) BLOCKED/DEFERRED: VGGish inference probe "
         "(DEFERRED_DISK -> c80/c81, mandatory by c81); transcription completion for the remaining songs (resumes from cache at c80 with the pinned "
         "command); tempo criterion revision (c80 pre-registers a metrically-aware criterion; NO retune this cycle). (4) FIRST-CLASS FINDINGS: (a) "
         "operator's ~7-song corpus is 26 on the receipts; (b) no full-song stems existed on disk; (c) WIG 50.17 was a drums-stem 30 s artifact, "
         "not a full-mix property; (d) the flat-band autocorrelation criterion is too permissive (3:2 lag wins on PD/Disco A) — invalidated "
         "hypothesis recorded with lag tables; (e) all librosa tempi are integer-lag quantized (~5 BPM near 120). (5) DISCIPLINE: FD-1 halt-honest "
         "(no retune, no fabricated stems, deferrals with reasons); FD-6 operator ear remains LANDS authority; FD-16(a) canonical 7-key env_pin "
         "2ac444c3… unchanged c22 -> c79 (58 cycles; cache-key pin d9241686… recorded for drift detection); FD-16(c) tempo byte-det x2 27/27 + "
         "manifest byte-det x2; c14 str-supersede lemma (1 str supersede: adoption -> _run/cycle_78_closed); c47 preservation-spin BAN honored; "
         "no wait-on-operator memo; no PRNG / sidecar_nonfactor / VST3 state APIs (AST-tested). (6) ANCHORS byte-identical pre==post: "
         + "; ".join(f"{k} {v[:12]}…" for k, v in frozen.items()) +
         " (all match their ledger-pinned values; data/v4/profiles/** and data/v4/deliveries/** untouched — c27 prune step disabled in the v5 driver). "
         f"(7) STORAGE: df open 87 %, peak 93 % (ear venv, corrected within ~3 min by removing the venv), driver max observed {df_max}%; transient "
         "audio per song ~230-330 MB, deleted after canonicalize. (8) TESTS: 7/7 new + 35/35 regression = 42/42. (9) NEXT (c80): resume/poll "
         "transcription from cache (WIG/CG/PD/Rome/DiscoA first); pre-register a metrically-aware tempo criterion and re-evaluate the frozen targets; "
         "open M-V5-RULES-1 harmony root+quality chain once >=3 songs are transcribed; rebuild ear venv after disk headroom decision and run the VGGish "
         "probe (mandatory by c81). 20th consecutive cycle of 9-header closing-summary compliance (c59-c79)."),
        ["promise_ledger.jsonl", "plan_of_record.md"]))

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
        print("IDEMPOTENT: all c79 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c79 events")
    for e in to_append:
        print(f"  {e['status']:12s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
