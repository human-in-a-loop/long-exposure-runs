#!/usr/bin/python3
"""c86 one-shot POR registration: insert the c86 sub-leaf rows inline in the `## Milestones` parseable region (before `## Sub-milestones`).
Idempotent; re-runnable (adds only missing rows). Retained in-tree per c14+ emitter-exemption pattern.

created: 2026-09-10T00:30:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _plan/register-c86-sub-leaves
"""
import json
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")
NAMES = {"252eb21ce7df7328": "WIG", "31a164f845f8e27e": "CG", "51e433ade2a845e1": "Rome", "88d247468cb6d49f": "PD", "cdd2717e52820ff6": "Disco A"}


def j(p):
    return json.loads(Path(p).read_text())


def main() -> int:
    roll = j("data/v5/gen/iteration_03/iteration_rollup.json")
    prof = j("data/v5/rules/velocity_profiles_v5.json")
    bass = j("data/v5/rules/bass_pitch_v5.json")
    vomm = j("data/v5/rules/melody_vomm_v5.json")
    gate = j("data/v5/gen/f2_route_gate_c86.json")
    h23 = j("data/v5/rules/harmony_markov_v5_full_c86.json")
    g23 = j("data/v5/rules/groove_v5_v2_full_c86.json")
    stall = j("data/v5/gen/stall_counter.json")
    sc = j("data/v5/gen/gen_v5_iter03_ear_scores_c86.json")
    f2 = roll["f2"]
    r1, r2 = prof["R1"], prof["R2"]
    rms = {NAMES[s["donor"]]: s.get("rms_variance_test") for s in roll["songs"]}
    rows = [
     ("_plan/adopt-operator-guidance-2026-09-09-F2-and-F4-addendum", "G1", "c86 adoption of OPERATOR GUIDANCE 2026-09-09 F2 VELOCITY DECISION + F4 ADDENDUM (`docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt`, sha16 8677bb0cd3f240a0; both blocks quoted verbatim in the ledger event; the auditor-cited e9f67abb… is a commit-side sha, on-disk governs): F2 dynamics by Route 1 (stem audio) or Route 2 (rule accents), decided in the first 10 minutes, one ledger line; no infeasibility memo; F4 AMBIGUOUS overruled — adopt PD 122.197271 / Disco A 120.272335, unblock (adjudication recorded IN the blocked file), harmony at n=23 in the earliest cheap cycle, consume from the next iteration, F4 CLOSED.", "Guidance quoted verbatim in the ledger event; route + F4 rows below.", "—"),
     ("M-V5-GEN-1/F2-velocity-route-decided-c86", "G5", f"c86 F2 route decision (one line): **{gate['route']}** — df {gate['df_used_pct_driver_semantics']} % ≤ 85, htdemucs importable (torch {gate['torch_version']}), WIG full-song separation {gate['separation_wall_s']} s ≤ 300; guidance sha16 8677bb0cd3f240a0. Fresh stems ≠ c79 cache (6/6) → pre-registered in-cycle ×2 fallback.", "Gate JSON on disk; route recorded.", "M-V5-GEN-1/F2-bass-melody-dynamics"),
     ("M-V5-GEN-1/f2-preregistered-c86", "G5", "c86 P2: `data/v5/gen/f2_prereg_c86.json` BEFORE any F2 output — route gate, 50 ms onset RMS, midrank p5→40/p95→110 + degenerate guard, profile definitions, bass/VOMM specs, generator flags, clause (c) render test, enum, ladder R1/R2/R3, held-constant list.", "Prereg mtime < every F2 output (test_01).", "M-V5-GEN-1/F2-bass-melody-dynamics"),
     ("M-V5-GEN-1/velocity-extraction-c86", "G5", f"c86 Route 1 (`scripts/v5/velocity_v5.py`): 5 focus songs separated in pinned subprocesses (READ-ONLY recreate_v3._run_htdemucs_once), 50 ms onset RMS at every MuScriptor start, per-(song, stem) midrank velocities, score-and-delete. In-cycle ×2 on WIG HOLDS; cross-cycle vs the c79 cache FAILS on every song (decoded full.wav SHAs match) — first-class finding, not retuned. R1 drums {r1['songs_passing_per_stem']['drums']}/5, bass {r1['songs_passing_per_stem']['bass']}/5 → {r1['drums_bass_pass_ge_4_of_5']}; Route-2 fallback stems {r1['route_2_fallback_stems']}. Outputs `velocity_v5/velocities.json` + sibling `canonical_v5_velocity/<stem>.mid` per song (canonical_v5_reindexed never written — disclosed reading).", "velocities.json + sibling MIDI for 5 songs; anchors untouched; in-cycle ×2 on WIG.", "M-V5-GEN-1/f2-preregistered-c86"),
     ("M-V5-RULES-1/velocity-profiles-c86", "G4", f"c86 `data/v5/rules/velocity_profiles_v5.json` (byte-det ×2): drums per GM class × 16th slot, bass by kick-coincidence × slot, melody by phrase position, keys by slot; quantile ladders sampled by SHA-256 inverse-CDF. R2: backbeat−odd {r2['backbeat_minus_odd']} (≥+10 {r2['backbeat_ge_plus_10']}), hat odd<even {r2['hat_odd_lower_than_even']}, bass coincident>non {r2['bass_coincident_gt_non']}, slot std {r2['drums_slot_profile_std']} (structureless {r2['structureless_std_lt_5']}). Figure `fig_velocity_profiles_c86.png` + `plot_velocity_profiles_c86.py --out`.", "Byte-det ×2; R2 recorded; figure on disk.", "M-V5-GEN-1/velocity-extraction-c86"),
     ("M-V5-RULES-1/bass-pitch-model-c86", "G4", f"c86 `scripts/v5/bass_pitch_v5.py` → `bass_pitch_v5.json` (n=21; byte-det ×2): interval classes root/fifth/octave/third/approach/other conditioned on (slot-in-beat, chord change), α 0.5; marginal {bass['marginal']['probs']}; root-on-downbeat corpus {bass['sampling_check']['corpus_downbeat_root_pc_fraction']} vs sampled {bass['sampling_check']['sampled_root_pc_fraction']} (pass {bass['sampling_check']['pass']}); corpus register median {bass['register']['corpus']['median']} IQR [{bass['register']['corpus']['iqr_lo']}, {bass['register']['corpus']['iqr_hi']}]; {bass['n_skipped_null_chord_total']} onsets on null-chord beats skipped (disclosed).", "Byte-det ×2; sampling check recorded.", "M-V5-GEN-1/f2-preregistered-c86"),
     ("M-V5-RULES-1/melody-vomm-c86", "G4", f"c86 `scripts/v5/melody_vomm_v5.py` → `melody_vomm_v5.json` (n=21; byte-det ×2): tokens scale-degree|IOI-bucket from vocals + other synth_lead; order ≤ 3 with escape; order-3 singleton fraction {vomm['order_stats']['3']['singleton_context_fraction']} → **{vomm['verdict']}** (recorded, not tuned); c72 vomm_generator not reused (API mismatch, sibling VOMM).", "Byte-det ×2; verdict from the prereg.", "M-V5-GEN-1/f2-preregistered-c86"),
     ("M-V5-GEN-1/iteration-03-c86", "G5", f"c86 iteration 3 (seed 2, form plan ON, `--f2 --velocity-mode f2`, c84 n=21 rules by design): 5 renders under `data/v5/gen/iteration_03/` each REPLAY_PROOF_HOLDS under the post-edit generator sha; forms {[''.join(s['form']) for s in roll['songs']]}; durations {[s['duration_s'] for s in roll['songs']]} s; velocities present {f2['n_velocities_present']}/5; frame-RMS variance ratios F2/uniform {rms} (≥1.5 5/5: {f2['clauses']['rms_variance_5_of_5']}); flag-off replay reproduces iteration 2 5/5; informational scores ≥6 {sc['n_gen_ge_6']}/5 (FD-6, no passer); listening copies → `data/v4/generated/v5_iter_03/`; stall {stall['iterations']}/{stall['budget']}. Figure `fig_iter03_velocity_c86.png`.", "5 renders + proofs on disk; RMS test recorded; listening copies listed in the event artifacts.", "M-V5-GEN-1/F2-bass-melody-dynamics"),
     ("M-V5-CORPUS-1/tempo-f4-operator-resolved-c86", "G4", "c86 F4 operator adjudication recorded (`tempo_f4_operator_resolution_c86.json`; supersedes the c85 AMBIGUOUS verdict path): PD 122.197271 / Disco A 120.272335 adopted; `recanonicalization_blocked.json` amended IN PLACE with `unblocked_c86` (pre-amend bytes preserved as `stale/recanonicalization_blocked.c80_c85.json`, 2fbabc07…; `blocked_songs` kept as history + donor_tempo's frozen-anchor source); `scripts/v5/recanonicalize_tempo_v5.py` → `canonical_v5c_reindexed/` for both songs at the adopted BPM (READ-ONLY c80 reindex + c4 serializer; note_on == JSON starts on 14 probes; byte-det ×2; canonical_v5_reindexed untouched).", "Resolution JSON + amended blocked file + stale copy + v5c dirs ×2 on disk.", "M-V5-GEN-1/F4-tempo-fix"),
     ("M-V5-RULES-1/harmony-n23-c86", "G4", f"c86 harmony n=23 (`eligible_c86.json` = c84's 21 + PD + Disco A; `harmony_prereg_c86.json` before the run; rule unchanged; additive `--tempo-overrides` asserting the v5c dir): **{h23['degeneracy_verdict']}** — {len(h23['states'])} states, max stationary {h23['max_stationary_state']} {h23['max_stationary_mass']} (n=21 0.063915); PD {h23['per_song']['88d247468cb6d49f']['key']['tonic_name']} {h23['per_song']['88d247468cb6d49f']['key']['mode']} {h23['per_song']['88d247468cb6d49f']['n_segments']} segs, Disco A {h23['per_song']['cdd2717e52820ff6']['key']['tonic_name']} {h23['per_song']['cdd2717e52820ff6']['key']['mode']} {h23['per_song']['cdd2717e52820ff6']['n_segments']} segs; chain byte-det ×2 with the post-edit script sha; c84 chain reproduced byte-identically by the edited script. Groove n=23 (`groove_prereg_c86.json`): **{g23['verdict']}** singleton {g23['singleton_context_fraction']}. Disclosure: the brief's 26−1−0=23 is a slip (25 eligible); late landers 0e1e8f20592db366 / cc0693b4a24f64b2 deferred so n=23 is exactly the operator's set. Figure `fig_harmony_n23_vs_n21_c86.png`. Consumed from iteration 4.", "Enum from the prereg; byte-det ×2; c84 artifacts untouched; figure on disk.", "M-V5-CORPUS-1/tempo-f4-operator-resolved-c86"),
     ("_infra/cheap-fixes-M1-M2-c86", "G1", "c86 P0: `plot_tempo_f4_c85.py --out` REQUIRED (figure re-issued, sha pinned in byte_determinism_c85.json `c86_reissue`; disclosed auditor-regenerated copy); `--cycle` REQUIRED on score_gen_batch_v5.py + deliver_v5_listening.py; form_plan_v5.py post-write prereg assert; sibling serializer with velocity field. MINOR 7 deferred to the F5 cycle (own prereg). Byte-det files split by owner (gen/, corpus/, rules/…_f4, rules/…_f2models).", "Tests green; SHAs pinned.", "—"),
     ("_plan/register-c86-sub-leaves", "G1", "c86 POR registration row: c86 sub-leaves inserted inline via `tools/_register_c86_por_rows.py` (idempotent).", "Rows added.", "—"),
     ("_infra/adopt-cycle86-tests", "G1", "c86 test-adoption: `tests/test_c86_landing.py` (10) + `tests/test_c86_f4_close.py` (6) + `tests/test_c86_f2_models.py` (5) new; c84/c85 blocked-file pins re-pinned to the stale copy + amended schema (disclosed); adopted suite re-run under /usr/bin/python3 (counts in the work output).", "New tests green + regression green.", "—"),
     ("_archive/cycle-86-scratch", "G1", "c86 scratch archival: emitter + registrar + detached launcher retained in-tree per emitter-exemption pattern and listed as artifacts; scratchpad runners not in workspace; plot scripts co-located with data + figures.", "No workspace scratch to archive.", "—"),
     ("_run/cycle_86_closed", "G1", "c86 CLOSED — v5 REOPENING cycle 8 (feature cycle: F2 iteration 3 via Route 1 + F4 CLOSED + P0 fixes). See ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c86 POR rows present")
        return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    main()
