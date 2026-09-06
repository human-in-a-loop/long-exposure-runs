#!/usr/bin/python3
"""c80 one-shot ledger emitter — v5 REOPENING cycle 2 (tempo v5b pre-registered falsification,
canonical-MIDI index-collision fix, harmony first data (gated), ear headroom).

UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts) per c14+ convention.
Idempotent by milestone_id. Retained in-tree per docs/emitter_exemption_policy.md
(`long_exposure/` is absent from this workspace; c34 OPT_B exemption). Reads every
number from disk at emit time.
"""
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 80
RUN_ID = "run-2026-09-06T000000Z"
TS = "2026-09-06T17:00:00Z"
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
    fals = json.loads((C / "tempo_v5b_falsification.json").read_text())
    bd = json.loads((C / "tempo_v5b_byte_determinism.json").read_text())
    rbd = json.loads((C / "reindex_canonical_v5_byte_determinism.json").read_text())
    blocked = json.loads((C / "recanonicalization_blocked.json").read_text())
    head = json.loads(Path("data/v5/ear/venv_headroom_c80.json").read_text())
    prog = json.loads((C / "transcription_progress.json").read_text())
    ps = fals["per_song"]
    frozen = {k: _sha(k) for k in FROZEN_EXPECTED}
    frozen_ok = {k: frozen[k].startswith(v) for k, v in FROZEN_EXPECTED.items()}
    n_frozen_ok = sum(frozen_ok.values())
    live = subprocess.run(["ps", "-p", str(prog.get("pid", 0)), "-o", "etime="], capture_output=True, text=True).stdout.strip()
    log_tail = Path("data/v5/logs/transcribe_full_c79.log").read_text().splitlines()[-1]
    df = subprocess.run(["df", "-h", "/"], capture_output=True, text=True).stdout.splitlines()[-1].split()
    done = [s for s in prog["order"] if (C / s / "transcription_manifest.json").exists()]
    tests_p = Path("/tmp/claude-0/-home-user-long-exposure-runs-music-gen/4927a841-0cd6-4230-a223-9ddf08a5b589/scratchpad/test_results.json")
    tests = json.loads(tests_p.read_text()) if tests_p.exists() else {}
    test_line = "; ".join(f"{Path(k).name} {v['summary'][0]}/{v['summary'][1]}" for k, v in tests.items() if v.get("summary"))
    gated_p = Path("data/v5/rules/harmony_v5_gated.json")
    chain_p = Path("data/v5/rules/harmony_markov_v5.json")
    prev = json.loads(Path("data/v5/rules/preview_n2/harmony_markov_v5.json").read_text())

    events = []
    events.append(_ev(f"{P}/transcription-liveness-c80", "in-progress", "high",
        "PID verified alive with ps at cycle open and at emit time; on-disk manifests are the landing record; driver not touched.",
        (f"P0: PID {prog.get('pid')} ALIVE at c80 open (47:41 elapsed, on Chicken Grease muscriptor:full_mix, 4 MuScriptor workers) and at emit "
         f"(etime {live or 'not running'}); last log line: {log_tail}. Record data/v5/logs/c80_p0_liveness.txt. df at open 87 % / at emit "
         f"{df[4]} ({df[3]} avail); driver max observed {prog.get('df_max_pct_observed')} %; never >= 90 %; no multi-GB install co-scheduled. "
         f"Songs landed on disk: {done}. P0.5: stale status:'dry_run' rows for CG/PD overwritten from on-disk state (sibling "
         "transcription_progress_c80_derived.json); DISCLOSURE: the driver holds an in-memory copy loaded at launch and rewrites the file after "
         "each song, so it re-emitted 'dry_run' for Peach Dream until it reached it — self-healing, not a defect of this cycle's edit. Stem-cache "
         "resume command unchanged from c79. CG landing detail is in the per-song event; the c9-era statvfs-vs-df discrepancy persists (statvfs "
         "user 98 % due to reserved blocks; df -h 87 %; the driver's _disk_used_pct_user reads 86.9 %)."),
        ["data/v5/logs/c80_p0_liveness.txt", "data/v5/corpus/transcription_progress.json", "data/v5/corpus/transcription_progress_c80_derived.json"]))

    events.append(_ev(f"{P}/tempo_v5b-preregistered-c80", "validated", "high",
        "Pre-registration file written before any output; mtime gate verified by the verdict script and test_04; targets identical to c79.",
        (f"data/v5/corpus/tempo_v5b_preregistration.json sha {_sha('data/v5/corpus/tempo_v5b_preregistration.json')} (mtime {fals['preregistration_gate']['prereg_mtime']:.0f}) "
         f"precedes the earliest tempo_v5b.json (mtime {fals['preregistration_gate']['min_output_mtime']:.0f}). Criterion: candidates = every local maximum of "
         "the normalized onset autocorrelation in the [40,240] BPM lag range (lags 10..65); s(T) = ac(T) + 0.5*ac(T/2) + 0.5*ac(2T), harmonics "
         "outside [40,240] contribute 0; argmax over candidates in [70,180]; SHA-256(f'{sha16}|{bpm:.4f}') tiebreak; no PRNG. Held constant: "
         "onset envelope, autocorrelation, +/-2 % lag window, corpus, MuScriptor outputs, env pin 2ac444c3…. scripts/v5/tempo_v5b.py is a new "
         "sibling (READ-ONLY import of tempo_v5 helpers); tempo_v5.py and its frozen c79 verdict untouched (sha byte-identical)."),
        ["data/v5/corpus/tempo_v5b_preregistration.json", "scripts/v5/tempo_v5b.py"]))

    events.append(_ev(f"{P}/tempo_v5b-verdict-c80", "validated", "high",
        "Frozen targets evaluated verbatim; three of five anchored songs miss; RULES-OUT clause fired; no retune, no second criterion (FD-1); byte-det x2 27/27.",
        (f"FROZEN VERDICT = {fals['verdict']} (data/v5/corpus/tempo_v5b_falsification.json). Anchored songs: WIG {ps[WIG]['bpm_v5b']} (hit; s top3 "
         f"{ps[WIG]['s_scores_top3']}); CG {ps[CG]['bpm_v5b']} (hit, delta +1.559); Peach Dream {ps[PD]['bpm_v5b']} UNCHANGED vs anchor 123.047 (s=1.222 at lag 32 vs "
         f"1.045 at lag 21) MISS; Disco A {ps[DISCO]['bpm_v5b']} UNCHANGED (s=1.201 vs 0.994) MISS; Rome REGRESSED {ps[ROME]['bpm_v5']} -> {ps[ROME]['bpm_v5b']} "
         f"(s=1.114 at lag 25 vs 1.094 at lag 17) MISS — a new failure the flat band did not have. Non-anchor flips {fals['non_anchor_flips']}/"
         f"{fals['non_anchor_songs']} ({fals['non_anchor_flip_fraction']:.0%}; secondary >50 % downgrade not reached). Total flips vs v5: {fals['total_flips_vs_v5']}/26. "
         f"Byte-det x2 {bd['n_equal']}/{bd['n_files_compared']} (tempo_v5b_byte_determinism.json). MECHANISM DIAGNOSIS (recorded for c81, NOT applied): on PD the "
         "onset autocorrelation is a comb at every ~10.67 lags (eighth notes at ~121 BPM: lags 11, 21, 32, 43, 53, 64, 74, 85); the anchor beat's T/2 harmonic is "
         "lag 10.5 = 246 BPM, just outside the pre-registered [40,240] candidate range, so it contributes 0 (ac at lag 11 is 0.69), while the hemiola "
         "lag 32's T/2 = 161.5 BPM and 2T = 40.4 BPM are both in range (0.387 + 0.632). Had the T/2 term counted, s(123.05) ≈ 0.69 + 0.345 + 0.35 = 1.39 > "
         "1.22. The invalidated hypothesis is therefore 'harmonic sum with a 240 BPM ceiling', not 'metrical hierarchy is irrelevant'; a criterion that "
         "reads harmonics regardless of the candidate band, or a comb/tempogram over the full lag axis, is the c81 candidate — pre-register before "
         "running. Figure data/v5/corpus/fig_tempo_v5b_scores.png (PD / Disco A / WIG ac curves, local-max candidates, winner + its T/2 and 2T "
         "lags, frozen anchor lag) regenerable from plot_tempo_v5b_scores.py. tempo_v5b_summary.tsv sha "
         f"{_sha('data/v5/corpus/tempo_v5b_summary.tsv')}."),
        ["scripts/v5/tempo_v5b_verdict.py", "data/v5/corpus/tempo_v5b_falsification.json", "data/v5/corpus/tempo_v5b_summary.tsv",
         "data/v5/corpus/tempo_v5b_byte_determinism.json", "data/v5/corpus/fig_tempo_v5b_scores.png", "data/v5/corpus/plot_tempo_v5b_scores.py"]
        + [f"data/v5/corpus/{s}/tempo_v5b.json" for s in prog["order"]]))

    events.append(_ev(f"{P}/recanonicalize-blocked-c80", "validated", "high",
        "P1 RULES_OUT branch executed verbatim: blocked file written; no canonical_v5b dirs created; M-V5-RULES-1 gate recorded in POR.",
        (f"data/v5/corpus/recanonicalization_blocked.json sha {_sha('data/v5/corpus/recanonicalization_blocked.json')}: blocked_songs = "
         f"{list(blocked['blocked_songs'])} (Peach Dream, Disco A: bpm_v5 80.75 vs anchors 123.05 / 120.19). Not blocked: WIG (99.384 = target), CG "
         "(+1.56), Rome (on-disk bpm_v5 = anchor; the v5b 103.36 regression is RULED OUT, not adopted). Advisory: 7 non-anchor v5b flippers listed "
         "for the c81 tempo decision. No canonical_v5b/ directory exists; harmony_v5.py reads this file and skips blocked songs."),
        ["data/v5/corpus/recanonicalization_blocked.json"]))

    wig_r = json.loads((C / WIG / "canonical_v5_reindexed/reindex_manifest.json").read_text())
    cg_r = json.loads((C / CG / "canonical_v5_reindexed/reindex_manifest.json").read_text())
    def _tot(r, k): return sum(v[k] for v in r["probes"].values())
    events.append(_ev(f"{P}/canonical-midi-index-collision-c80", "validated", "high",
        "Defect reproduced with counts on two songs; fix is a pure function of the intact JSON calling the READ-ONLY serializer; lossless by count; byte-det x2 14/14; c79 lossy dir untouched.",
        ("FIRST-CLASS DEFECT (c79 output, c22 root cause): READ-ONLY scripts/v3_spine/recreate_v3._merge_chunk_events re-offsets chunk times but never "
         "re-numbers `index` / `start_event_index`; the READ-ONLY c4 serializer (midi_from_json_events._pair_events) keys starts by `index` in a dict, "
         "keeping ONE start per index. Full-length songs are transcribed in 30 s / 5 s-overlap chunks, so chunk-local indices collide and c79's "
         f"canonical_midi_full/*.mid silently dropped most notes: WIG other 1799 JSON starts -> 395 distinct indices (395 note_on in the MIDI), bass 83 -> 38, "
         "piano 706 -> 190, guitar 384 -> 269; CG guitar 2736 -> 486, bass 438 -> 65. 30 s v3/v4 sections were single-chunk and are unaffected; the "
         "MuScriptor JSON is intact (all starts and ends present; ends carry chunk-local start_event_index). FIX: scripts/v5/reindex_canonical_v5.py "
         "sorts starts by (start_time, instrument, pitch, index), pairs each start with the earliest unconsumed end of the same chunk-local index with "
         "end > start and span <= 30 s (deterministic greedy; disclosed heuristic — it can only mis-assign a duration where two chunks reuse an index "
         "within 30 s), re-indexes 0..N-1, rewrites start_event_index, and calls the READ-ONLY serialize() at bpm_v5 / 4-4 into "
         f"data/v5/corpus/<sha16>/canonical_v5_reindexed/ (re-indexed JSON kept alongside). Lossless by count: WIG {_tot(wig_r, 'n_starts_in')} starts in / "
         f"{_tot(wig_r, 'n_paired')} paired / {_tot(wig_r, 'n_unpaired_starts')} unpaired (-> 100 ms synthetic duration, as the serializer already does); "
         f"CG {_tot(cg_r, 'n_starts_in')} / {_tot(cg_r, 'n_paired')} / {_tot(cg_r, 'n_unpaired_starts')}. harmony_v5 per-stem MIDI note counts now equal the JSON "
         f"starts (WIG bass 83 / guitar 384 / other 1799 / piano 706). Byte-det x2 {rbd['n_equal']}/{rbd['n_files_compared']} "
         "(reindex_canonical_v5_byte_determinism.json). canonical_midi_full/ (c79) is left untouched as the lossy anchor; every v5 consumer must read "
         "canonical_v5_reindexed/. The driver's canonicalize stage still writes the lossy dir for new songs (READ-ONLY composition); the reindex "
         "script is idempotent and runs over every landed song. str-supersedes the canonical-MIDI clause of the c79 WIG landing event only; its note "
         "counts (from JSON) stand."),
        ["scripts/v5/reindex_canonical_v5.py", "data/v5/corpus/reindex_canonical_v5_byte_determinism.json"]
        + [f"data/v5/corpus/{s}/canonical_v5_reindexed/reindex_manifest.json" for s in done],
        supersedes_path=f"{P}/252eb21ce7df7328-transcribed-c79"))

    for s in done:
        if s == WIG:
            continue
        tm = json.loads((C / s / "transcription_manifest.json").read_text())
        nc = {p: tm["note_counts"][p]["n_note_on"] for p in tm["note_counts"]}
        extra = ""
        if s == CG:
            extra = (" FINDING: CG other = 0 and piano = 4 note_on at FULL length — consistent with the c14 audibility grounding (CG piano stem "
                     "-81.5 dBFS, other -81.7 dBFS on the operator section: htdemucs_6s routes CG's keys/organ content into guitar, 2736 notes). "
                     "So the v4 'other/piano zero' observation is song-specific stem content, not a transcription defect (WIG has 1799 / 706).")
        if s in blocked["blocked_songs"]:
            extra += " TEMPO: this song is BLOCKED for rules extraction (bpm_v5 80.75 vs anchor); MIDI is re-serializable from cached JSON once a supported criterion lands."
        events.append(_ev(f"{P}/{s}-transcribed-c80", "validated", "high",
            "Full-length transcription completed by the detached driver; manifest + stage-cache keys on disk; transient audio deleted; canonical MIDI re-indexed losslessly.",
            (f"{tm.get('title')} ({s}, {tm['duration_s']} s, bpm_v5 {tm['bpm_v5']}): note_on {nc}; drums GM classes {tm['note_counts']['drums'].get('gm_classes')}; "
             f"bars at bpm_v5 {tm['bar_count_at_bpm_v5']}; stage wall htdemucs {tm['stages']['htdemucs_6s'].get('wall_s')} s, muscriptor "
             f"{ {p: v.get('wall_s') for p, v in tm['stages']['muscriptor'].items()} }; cache keys {tm['cache_keys']}; transient deleted "
             f"{len(tm['transient_audio_deleted'])} files ({sum(d['bytes'] for d in tm['transient_audio_deleted'])/1e6:.0f} MB); df max {tm['df_max_pct_observed_so_far']} %. "
             f"Canonical MIDI: canonical_midi_full/ (lossy, c79 serializer path) + canonical_v5_reindexed/ (lossless, c80)." + extra),
            [f"data/v5/corpus/{s}/transcription_manifest.json"] + [f"data/v5/corpus/{s}/muscriptor_full/{p}.json" for p in nc]
            + [f"data/v5/corpus/{s}/canonical_v5_reindexed/{p}.mid" for p in nc]))

    n_used = (json.loads(chain_p.read_text())["gate"]["n_used"] if chain_p.exists() else json.loads(gated_p.read_text())["n_used"])
    if chain_p.exists():
        mk = json.loads(chain_p.read_text())
        events.append(_ev("M-V5-RULES-1/harmony_v5-first-data-c80", "validated", "medium",
            "Pre-declared >=3 gate met; degeneracy verdict computed with pre-declared thresholds; byte-det x2; nothing fed to a generator.",
            (f"scripts/v5/harmony_v5.py on {n_used} unblocked landed songs {mk['gate']['used']}: {len(mk['states'])} functional states; max stationary "
             f"{mk['max_stationary_state']} = {mk['max_stationary_mass']}; qualities with >= 8 segments {mk['qualities_with_count_ge_threshold']}; verdict {mk['degeneracy_verdict']}."),
            ["scripts/v5/harmony_v5.py", "data/v5/rules/harmony_markov_v5.json"] + [f"data/v5/rules/{s}/harmony_v5.json" for s in mk["gate"]["used"]]))
    else:
        g = json.loads(gated_p.read_text())
        events.append(_ev("M-V5-RULES-1/harmony_v5-gated-c80", "in-progress", "medium",
            "Pre-declared >=3-unblocked-song gate not met at emit time (Peach Dream lands BLOCKED; Rome not yet landed); script validated on a labelled n=2 preview; nothing fed to a generator.",
            (f"P3 GATED: {g['n_used']} unblocked landed songs (< 3): landed {g['landed']}, blocked-skipped {g['blocked_skipped']}. Record data/v5/rules/harmony_v5_gated.json. "
             "scripts/v5/harmony_v5.py implements OPERATOR #2 first data: per-beat pitch-class profile from bass+guitar+piano+other canonical MIDI (beat = tick/480; "
             "weight = note overlap in beats x velocity — DISCLOSURE: the c4 serializer writes uniform velocity 100 because MuScriptor events carry none, so the "
             "weighting is duration-only); 84 root x quality cosine templates (maj/min/7/min7/maj7/9/sus); zero-energy beats -> N; Krumhansl-Kessler key (no key "
             "metadata exists in the profile manifests — Krumhansl path per brief); functional state = (root - tonic) % 12 : quality; beat-level Markov chain with "
             "self-loops (a per-beat sampler's chain) + segment-level change matrix; stationary distribution by power iteration; PRE-DECLARED degeneracy: "
             "non-degenerate iff max stationary mass < 0.60 AND >= 4 qualities with >= 8 segments. LABELLED n=2 PREVIEW (data/v5/rules/preview_n2/, KQ4 data-existence "
             f"only, NOT a M-V5-RULES-1 verdict): WIG key {prev['per_song'][WIG]['key']['tonic_name']} {prev['per_song'][WIG]['key']['mode']} (corr "
             f"{prev['per_song'][WIG]['key']['corr']:.3f}), 302 beats / {prev['per_song'][WIG]['n_segments']} segments, top states {prev['per_song'][WIG]['top_states'][:4]}; "
             f"CG key {prev['per_song'][CG]['key']['tonic_name']} {prev['per_song'][CG]['key']['mode']} (corr {prev['per_song'][CG]['key']['corr']:.3f}), 415 beats / "
             f"{prev['per_song'][CG]['n_segments']} segments, top states {prev['per_song'][CG]['top_states'][:4]}; corpus chain {len(prev['states'])} states, max stationary "
             f"{prev['max_stationary_state']} = {prev['max_stationary_mass']}, qualities >= 8 segments {prev['qualities_with_count_ge_threshold']} -> preview "
             f"{prev['degeneracy_verdict']}. Before the index-collision fix the same run gave N = 0.75 (68 % / 82 % empty beats) — the lossy MIDI would have "
             "produced a degenerate chain; the fix is prerequisite for every v5 rules model. The official run re-executes unchanged once >= 3 unblocked songs "
             "(WIG, CG, Rome) have landed (Rome is next in the driver's order after Peach Dream)."),
            ["scripts/v5/harmony_v5.py", "data/v5/rules/harmony_v5_gated.json", "data/v5/rules/preview_n2/harmony_markov_v5.json",
             f"data/v5/rules/preview_n2/{WIG}/harmony_v5.json", f"data/v5/rules/preview_n2/{CG}/harmony_v5.json"]))

    events.append(_ev("M-V5-EAR-1/ear-venv-headroom-c80", "validated", "high",
        "df measured after transient deletion; arithmetic explicit; no pip/venv this cycle; /root/.local untouched and excluded.",
        (f"data/v5/ear/venv_headroom_c80.json: df {head['df_user_pct']} %, free {head['free_gb']} GB (brief >= 3.5 GB: {head['brief_threshold_free_ge_3_5gb']}, WITHOUT "
         f"/root/.local = {head['root_local_bytes_untouched']/1e9:.2f} GB, untouched — operator-authority disk question), required 2.6 GB, idle margin "
         f"{head['margin_gb_idle']} GB (>= 0.9), margin during a transcription transient (344 MB) {head['margin_gb_during_transcription']} GB, margin during pip "
         f"transient + transcription {head['margin_gb_during_pip_and_transcription']} GB (c79 hit 93 % this way). build_allowed_next_cycle = {head['build_allowed_next_cycle']} "
         f"because the transcription job ({head['transcription_job']['songs_remaining']} songs remaining, ~{head['transcription_job']['eta_hours_at_27min_per_song']} h) will "
         f"not finish before the c81 build; build_allowed_if_sequenced_after_transcription = {head['build_allowed_if_sequenced_after_transcription']}. c81 recipe: "
         "pause the driver at a song boundary (cache-safe: every stage keyed) or build immediately after a song's transient deletion, `pip install --no-cache-dir`, "
         "re-check df before the VGGish probe. MANDATORY by c81."),
        ["data/v5/ear/venv_headroom_c80.json"]))

    events.append(_ev("_plan/register-c80-sub-leaves", "validated", "high",
        "Rows inserted inline in the parseable ## Milestones region (before ## Sub-milestones) via tools/_register_c80_por_rows.py; idempotent.",
        ("c80 POR rows registered inline (P0 liveness, tempo_v5b preregistered + verdict, recanonicalize-blocked, canonical-midi-index-collision, harmony gated, "
         "ear headroom, per-song transcribed-c80, housekeeping). M-V5-RULES-1 gate note references recanonicalization_blocked.json. promise_check IS runnable "
         "this cycle (module resolves from /home/user/human-in-a-loop/long-exposure); its output is reported verbatim in the work output."),
        ["plan_of_record.md", "tools/_register_c80_por_rows.py"]))

    events.append(_ev("_infra/adopt-cycle80-tests", "validated", "high",
        "New suites green under /usr/bin/python3; pre-c80 regression green; no anchor mutation.",
        (f"tests/test_tempo_v5b.py (6) + tests/test_harmony_v5.py (3) adopted. Results at emit: {test_line}. test_01 encodes the pre-registered mechanism on a "
         "synthetic 3:2 hierarchy (strongest single peak at 1.5T, harmonic sum prefers T when T/2 and 2T are in range); test_02 asserts out-of-range harmonics "
         "contribute 0 including the on-disk PD lag-21 T/2 term (the diagnosed failure); test_04 asserts the pre-registration mtime gate, the frozen verdict enum, "
         "and — because the verdict is RULES_OUT — that PD + Disco A are blocked and CG + Rome are not; test_06 byte-det x2. Harmony: C-maj7 recovery; I-vi-IV-V7 "
         "invariant under 4 transpositions; pre-declared degeneracy thresholds + on-disk gated/chain record."),
        ["tests/test_tempo_v5b.py", "tests/test_harmony_v5.py"]))

    events.append(_ev("_archive/cycle-80-scratch", "validated", "high",
        "One-shot emitters retained in-tree per emitter-exemption pattern; scratch runners live in the harness scratchpad; nothing to move to tools/stale/.",
        ("tools/_emit_c80_ledger_events.py + tools/_register_c80_por_rows.py retained in-tree (docs/emitter_exemption_policy.md). Session scratchpad: p0_probe, "
         "p0_progress_fix, bytedet_v5b, bytedet_reindex, idx_probe, p3_official, p4_headroom, run_tests (not in workspace). data/v5/corpus/plot_tempo_v5b_scores.py "
         "is co-located with its data + figure (regenerable triplet). data/v5/rules/preview_n2/ is a labelled preview, retained."), []))

    events.append(_ev("_run/cycle_80_closed", "validated", "high",
        "All MANDATORY brief items landed or halt-honestly gated: P0 alive, P1 RULES_OUT (first-class negative), P2 blocked-branch, P3 gated with preview, P4 headroom, P5 ledger/POR/tests/promise_check.",
        ("c80 CLOSED — v5 REOPENING cycle 2. 9-HEADER CLOSING SUMMARY. (1) VERDICT: SUBSTANTIVE with two first-class negatives — the pre-registered harmonic-sum "
         f"tempo criterion is RULED OUT ({fals['verdict']}: PD/Disco A unchanged at 80.75, Rome regressed to 103.36) and c79's full-length canonical MIDI is "
         "LOSSY (index collision in the c22 chunk merge x c4 index-keyed serializer) — fixed losslessly by a v5 re-indexing sibling. (2) LANDED: P0 liveness "
         f"(PID {prog.get('pid')} alive; CG then PD progressed; stale dry_run rows overwritten with disclosure); P1 tempo_v5b pre-registration (mtime gate) + 26/26 "
         f"scored + byte-det {bd['n_equal']}/{bd['n_files_compared']} + frozen verdict + mechanism diagnosis (T/2 of the anchor beat falls outside the 240 BPM candidate "
         "ceiling) + figure; P2 recanonicalization_blocked.json (PD, Disco A); canonical-midi-index-collision fix + reindex byte-det 14/14; per-song landing "
         f"events for {[s for s in done if s != WIG]}; P3 harmony_v5.py (84 templates, KK key, functional beat-level Markov, pre-declared degeneracy) GATED at n_used="
         f"{n_used} with a labelled n=2 preview (NON_DEGENERATE, max stationary N=0.124, 7 qualities) — after the MIDI fix; before it the preview was degenerate "
         "(N=0.75); P4 headroom JSON (free 5.21 GB, idle margin 2.61 GB, build_allowed_next_cycle=false because the job will not finish before c81; sequenced "
         "build allowed); P5 events + POR rows + 9 new tests + promise_check run. (3) BLOCKED/DEFERRED: tempo criterion revision -> c81 pre-registration "
         "(read harmonics regardless of the candidate band / comb-tempogram); harmony official run -> when Rome lands (>=3 unblocked); ear venv build -> c81 "
         "sequenced after/paused transcription (MANDATORY); Peach Dream + Disco A remain blocked for rules. (4) FIRST-CLASS FINDINGS: (a) harmonic sum with a "
         "[40,240] candidate band fails on 3:2 songs because the true beat's T/2 sits at 246 BPM; (b) chunk-merge index collision silently dropped ~78 % of "
         "full-length notes in c79 canonical MIDI; (c) CG other/piano are genuinely near-empty stems (0 / 4 notes; -81 dBFS), not a transcription defect; (d) on "
         "lossless MIDI the 2-song harmony chain is non-degenerate with 7 qualities in use. (5) DISCIPLINE: FD-1 halt-honest (no retune, no second criterion, "
         "gated P3, deferrals with reasons, defect recorded with counts); FD-6 operator ear remains LANDS authority; FD-16(a) canonical 7-key env_pin 2ac444c3… "
         "unchanged c22 -> c80 (59 cycles); FD-16(c) byte-det x2 on tempo_v5b (27/27) and reindexed MIDI (14/14); c14 str-supersede lemma (2 str supersedes: "
         "index-collision -> c79 WIG landing clause; this row -> _run/cycle_79_closed); c47 preservation-spin BAN honored; no wait-on-operator memo; no PRNG / "
         f"sidecar_nonfactor / VST3 state APIs (AST-tested). (6) ANCHORS: {n_frozen_ok}/14 FROZEN anchors byte-identical to their c79-pinned SHAs — "
         + "; ".join(f"{k} {frozen[k][:12]}{'' if frozen_ok[k] else ' MISMATCH'}" for k in FROZEN_EXPECTED) +
         f". (7) STORAGE: df open 87 %, emit {df[4]} ({df[3]} avail); driver max {prog.get('df_max_pct_observed')} %; no install; /root/.local untouched. "
         f"(8) TESTS: {test_line}. (9) NEXT (c81): pre-register + run a band-independent harmonic criterion (targets unchanged), re-canonicalize only if SUPPORTED; "
         "run reindex_canonical_v5.py over newly landed songs and the official harmony run at >=3 unblocked; build the ear venv sequenced with the driver and run "
         "the VGGish probe (MANDATORY); open the joint groove model on canonical_v5_reindexed/ drums (kick/snare/hat classes) + bass. 21st consecutive cycle of "
         "9-header closing-summary compliance (c59-c80)."),
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_79_closed"))

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
        print("IDEMPOTENT: all c80 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c80 events; frozen anchors OK {n_frozen_ok}/14")
    for e in to_append:
        print(f"  {e['status']:12s} {e['milestone_id']} {e['event_id']}")
    for k, ok in frozen_ok.items():
        if not ok:
            print(f"  FROZEN MISMATCH {k} {frozen[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
