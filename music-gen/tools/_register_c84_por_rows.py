#!/usr/bin/python3
"""c84 one-shot POR registration: insert c84 sub-leaf rows (+ ONE outage line) inline in the `## Milestones` parseable region
(before `## Sub-milestones`). Idempotent; re-runnable (adds only missing rows). Retained in-tree per c14+ emitter-exemption pattern."""
import json, os, re
from pathlib import Path
os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")
LEDGER = Path("promise_ledger.jsonl")
P = "M-V5-CORPUS-1"
C = Path("data/v5/corpus")


def j(p):
    return json.loads(Path(p).read_text())


def main() -> int:
    launch = j("data/v5/logs/transcribe_full_c84.launch.json"); live = Path("data/v5/logs/c84_p0_liveness.txt").read_text().strip()
    cg = j(C / "content_blocked.json"); hb = j(C / "hook_at_birth_c84.json")
    h = j("data/v5/rules/harmony_markov_v5_full.json"); g = j("data/v5/rules/groove_v5_v2_full.json"); roll = j("data/v5/gen/iteration_01/iteration_rollup.json")
    sc_p = Path("data/v5/gen/gen_v5_iter01_ear_scores_c84.json"); sc = j(sc_p) if sc_p.exists() else {}
    stall = j("data/v5/gen/stall_counter.json")
    landed = sorted(p.parent.name for p in C.glob("*/transcription_manifest.json"))
    side = sorted(p.parent.name for p in C.glob("*/canonical_v5_reindexed_sha256.json"))
    b = cg["blocked_songs"].get("ae1b65eaf1560951", {})
    pt = g["per_table"]
    rows = [
     ("_infra/c100-c127-lost-to-outage", "G1", "c100–c127 lost to outage (rate limit + researcher context overflow; engine dead 2026-09-07 03:32Z → 2026-09-09 20:40Z); last real work c98/c99 = on-disk c82/c83; resumed at c84 (harness c128). ONE line, no memo.", "Line present.", "—"),
     (f"{P}/transcription-liveness-c84", "G4", f"c84 P0.1: {live}", "Liveness file exists; old PID absent; df < 90 %.", f"{P}/transcription-liveness-c83"),
     (f"{P}/driver-restart-c84", "G4", f"c84 P0.3: pinned c79 command relaunched via READ-ONLY launch_detached (new PID {launch['new_pid']}, {launch['launched_utc']}) after verifying driver sha {launch['driver_sha256_at_launch'][:12]}… + hook sha {launch['reindex_hook_sha256_at_launch'][:12]}… unchanged and that build_env_pin_manifest() under the driver's pinned env reproduces the stage-cache key {launch['stage_cache_env_pin_key'][:12]}… (computed WITHOUT the pins it reads 6386e0cc… — disclosed, not drift). 0e1e8f20592db366 resumed with cache hits on decode/htdemucs/6 muscriptor probes (full_mix ran); `_transient/` consumed by the driver. cc0693b4a24f64b2 follows.", "Launch JSON with new PID + resume song + cache hits; df < 90 %.", f"{P}/full-length-transcription-launched-c79"),
     (f"{P}/content-gate-preregistered-c84", "G4", "c84 P0.2: `content_gate_prereg_c84.json` BEFORE output — R1 NON_MUSIC_CONTENT := n_note_on(full_mix)==0 AND sum(drums,bass,guitar,other,piano)==0; R2 title regex `commentary|interview|q&a|talk|podcast|lecture|spoken`; BLOCKED iff R1; expected exactly ae1b65eaf1560951.", "Prereg mtime < output mtime.", "—"),
     (f"{P}/content-gate-c84", "G4", f"c84 P0.2: `scripts/v5/content_gate_v5.py` → `content_blocked.json` (separate file; tempo-blocked file byte-identical): blocked {sorted(cg['blocked_songs'])} (expectation match {cg['matches_expectation']}); tally {cg['verdict_tally']}. ae1b65eaf1560951 '{b.get('title')}': {b.get('verdict')}, note counts {b.get('note_counts')}, hook-at-birth Δ {b.get('hook_at_birth_delta_s')} s. Additive `ContentBlockedError` refusal (scripts/v5/content_blocked.py) in harmony_v5 / groove_v5 / groove_v5_v2, fixture-tested (refuses before MISSING_REINDEX).", "content_blocked.json = exactly the pre-registered hit; refusal fires in all three rules scripts.", f"{P}/content-gate-preregistered-c84"),
    ]
    existing_ledger = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            existing_ledger.add(json.loads(line).get("milestone_id"))
    for s, v in hb["per_song"].items():
        if any(re.fullmatch(rf"{P}/{s}-reindexed-c8[0-3]", m or "") for m in existing_ledger):
            continue
        tm = j(C / s / "transcription_manifest.json")
        extra = f" CONTENT VERDICT {b.get('verdict')} (content-blocked for rules; vocals {tm['note_counts']['vocals']['n_note_on']} starts, instruments + full_mix 0)." if s == "ae1b65eaf1560951" else ""
        rows.append((f"{P}/{s}-reindexed-c84", "G4", f"c84 per-song lossless record: {tm.get('title')} ({s}, bpm_v5 {tm['bpm_v5']}): landed under PID 10247 (hook live at birth) after c83 close — sidecar Δ {v.get('sidecar_minus_manifest_s')} s; hook_at_birth={v['hook_at_birth']}; paired {v.get('paired_total')} / unpaired {v.get('unpaired_total')}; MIDI note_on == JSON starts {v.get('note_on_equals_starts_all')}; zero catch-up.{extra}", "Sidecar SHAs match disk; note_on == starts; hook-at-birth evidence.", f"{P}/hook-at-birth-verification-c84"))
    rows += [
     (f"{P}/hook-at-birth-verification-c84", "G4", f"c84 P0.4: `hook_at_birth_c84.py` (baseline = 9 songs known at c83 close) verified {len(hb['new_landings_since_c83'])} post-c83 landings all hook_at_birth={hb['all_new_hook_at_birth']}; `reindex_landed()` no-op {hb['catch_up_is_noop']}. Invariant (d): {hb['invariant_d_disclosure']}.", "Every post-c83 landing has a hook-at-birth sidecar; zero catch-ups; per-song rows only for songs without an existing row.", f"{P}/hook-at-birth-verification-c83"),
     ("M-V5-RULES-1/harmony-full-corpus-preregistered-c84", "G4", "c84 P1: `harmony_prereg_c84.json` BEFORE output — eligible = landed ∧ sidecar ∧ ¬tempo-blocked ∧ ¬content-blocked; c80 degeneracy rule + threshold 12 unchanged; enum HARMONY_NONDEGENERATE / HARMONY_DEGENERATE.", "Prereg mtime < chain mtime.", "M-V5-RULES-1/harmony_v5-first-data-c82"),
     ("M-V5-RULES-1/harmony-full-corpus-c84", "G4", f"c84 P1 **{h['degeneracy_verdict']}** (HARMONY_NONDEGENERATE) on n={h['gate']['n_used']} eligible songs (tempo-blocked skipped {h['gate']['blocked_skipped']}, content-blocked skipped {h['gate']['content_blocked_skipped']}): {len(h['states'])} states; max stationary {h['max_stationary_state']}={h['max_stationary_mass']} (c82 n=3 0.0956); qualities ≥ 8 segs {h['qualities_with_count_ge_threshold']}. Per-song excluded-beat fraction mean {round(sum(v['excluded_beat_fraction'] for v in h['per_song'].values()) / len(h['per_song']), 4)} — the c82 breadth finding persists at full corpus; not retuned. `harmony_markov_v5_full.json` byte-det x2; c82 `harmony_markov_v5.json` byte-identical. Figure `fig_harmony_full_c84.png` + `plot_harmony_full_c84.py`.", "Enum from the prereg; byte-det x2; figure + plot script on disk.", "M-V5-RULES-1/harmony-full-corpus-preregistered-c84"),
     ("M-V5-RULES-1/groove-v2-full-corpus-preregistered-c84", "G4", "c84 P2: `groove_prereg_c84.json` BEFORE output — SHA-256 fold of 3 held out; GENERALIZES iff singleton < 0.5 ∧ |Δbackbeat|,|Δlock| ≤ 0.15; alpha 0.5 + 8th-note kick alphabet held constant.", "Prereg mtime < model mtime.", "M-V5-RULES-1/groove_v5-v2-heldout-c82"),
     ("M-V5-RULES-1/groove-v2-full-corpus-c84", "G4", f"c84 P2 **{g['verdict']}**: {g['gate']['n_eligible']} eligible, held out {g['fold']['heldout']}, train {g['n_train_songs']} songs / {g['n_train_bars']} bars. Held-out backbeat Δ {g['validation']['backbeat_ratio']['abs_diff']} + lock Δ {g['validation']['bass_kick_lock']['abs_diff']} within 0.15, but singleton {g['singleton_context_fraction']} ≥ 0.5. FIRST-CLASS: the small-n mechanism holds for snare|kick8 ({pt['snare_given_kick']['singleton_fraction']}) and bass|kick8 ({pt['bass_given_kick']['singleton_fraction']}) but hat|kick8,snare16 stays {pt['hat_given_kick_snare']['singleton_fraction']} ({pt['hat_given_kick_snare']['n_contexts']} contexts / {pt['hat_given_kick_snare']['n_pairs']} bars) — context granularity, not n; next axis pre-registered for c85, not changed (FD-1). Byte-det x2. Figure `fig_groove_v2_full_c84.png` + `plot_groove_v2_full_c84.py`. Does not block P3.", "Enum from the prereg; byte-det x2; figure + plot script on disk.", "M-V5-RULES-1/groove-v2-full-corpus-preregistered-c84"),
     ("M-V5-GEN-1/iteration-01-c84", "G5", f"c84 P3 groove-first iteration 1: `scripts/v5/generate_v5.py` — A A B A (4 bars each, A repeated literally), drums+bass from the c84 groove conditionals, chords from the c84 harmony chain, keys/melody chord tones on the grid, SHA-256 inverse-CDF only; donor tempo + pinned sf2 profiles (GM shims for keys/melody + CG drums, disclosed); 5 renders under `data/v5/gen/iteration_01/` each REPLAY_PROOF_HOLDS (byte-det x2 in fresh mkdtemp); per-track WAVs deleted after mix. Informational ear scores (venv, c76 v2): ≥6 {sc.get('n_gen_ge_6')}/{sc.get('n_gen_renders')}; NO passer declared (FD-6, c76 L119). Best samples → `data/v4/generated/v5_iter_01/`. stall {stall['iterations']}/{stall['budget']}.", "5 renders + replay proofs on disk; scores recorded; stall 1/12; top-5 audio rule honoured.", "M-V5-GEN-1"),
     ("_plan/register-c84-sub-leaves", "G1", f"c84 POR registration row: c84 sub-leaves + ONE outage line inserted inline via `tools/_register_c84_por_rows.py` (idempotent). M-V5-CORPUS-1: {len(landed)}/26 landed, {len(side)}/26 sidecar at registration; content gate landed; M-V5-RULES-1 full corpus harmony {h['degeneracy_verdict']} / groove {g['verdict']}; M-V5-GEN-1 iteration 1 landed (informational scores).", "Rows added.", "—"),
     ("_infra/adopt-cycle84-tests", "G1", "c84 test-adoption: `tests/test_c84_landing.py` (8) new; adopted suite re-run under /usr/bin/python3 (counts in the ledger event / work output; ADOPTED suite, not tests/ as a whole).", "New tests green + regression green.", "—"),
     ("_archive/cycle-84-scratch", "G1", "c84 scratch archival: emitter + registrar retained in-tree per emitter-exemption pattern and listed as artifacts of this event (L1); scratchpad runners not in workspace; plot scripts co-located with data + figures.", "No workspace scratch to archive.", "—"),
     ("_run/cycle_84_closed", "G1", "c84 CLOSED — v5 REOPENING cycle 6 (outage recovery by execution). See ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c84 POR rows present"); return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    sys.exit(main()) if False else main()
