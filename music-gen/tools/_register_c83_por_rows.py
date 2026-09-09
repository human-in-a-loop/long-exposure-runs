#!/usr/bin/python3
"""c83 one-shot POR registration: insert c83 sub-leaf rows inline in the `## Milestones` parseable region
(before `## Sub-milestones`). Idempotent; re-runnable (adds only missing rows). Retained in-tree per c14+ emitter-exemption pattern."""
import json, os, sys
from pathlib import Path
os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")
P = "M-V5-CORPUS-1"
C = Path("data/v5/corpus")


def j(p):
    return json.loads(Path(p).read_text())


def main() -> int:
    rc = j("data/v5/ear/env_pin_ear_venv_c82_amended.json"); pr = j("data/v5/ear/ear_probe_c83.json")
    u = j(C / "unpaired_starts_c83.json"); t = j("data/v5/gen/gen_render_ear_scores_c83.json")
    live = Path("data/v5/logs/c83_p0_liveness.txt").read_text().strip().replace("\n", " | ")
    landed = sorted(p.parent.name for p in C.glob("*/canonical_v5_reindexed_sha256.json"))
    nm = u["named_cells_from_brief"]
    rows = [
     (f"{P}/transcription-liveness-c83", "G4", f"c83 S1 P0: {live}. Driver untouched; no restart; no install; df never ≥ 90 %.", "Liveness file exists; PID alive; df < 90 %; no FROZEN path modified.", f"{P}/transcription-liveness-c82"),
     ("M-V5-EAR-1/ear-venv-receipt-amended-c83", "G3", f"c83 S2 P0 (closes c82 F2): `data/v5/ear/env_pin_ear_venv_c82_amended.json` pins the AMENDED venv (c79 command + `pip install -r ear_venv_pip_freeze_c82_amended.txt`; librosa pin {rc['librosa_pin']}; freeze sha {rc['pip_freeze_sha256'][:12]}… recomputed; versions by venv subprocess {rc['versions_from_venv_subprocess']}; main-env freeze unchanged {rc['main_env_unchanged']}); str-supersedes the c82 receipt. Read-only re-probe `ear_probe_c83.json` x2: **{pr['status']}** (run1==run2 {pr['run1_eq_run2']}). Adopts the two c82 orphan logs (F3). F5 (`ear_probe_c82.json` without `agent`) disclosed, file byte-identical. test_ear_venv_c81 test_04 additive (4/4).", "Amended receipt on disk with str supersede; probe enum recorded; test green; main-env sha unchanged.", "M-V5-EAR-1/ear-venv-built-c82"),
     (f"{P}/unpaired-starts-characterization-c83", "G4", f"c83 S4 (M-3, characterization, no fix): prereg BEFORE output; {u['n_songs']} songs x 7 stems; tally {u['tally_all_cells']}. Named cells: " + "; ".join(f"{k} {v['n_unpaired']}/{v['n_starts']} → {v['label']}" for k, v in nm.items()) + ". FIRST-CLASS FINDING: the large-unpaired cells (Molasses other/vocals, Desire other) are neither H1 (final-chunk share 0) nor H2 (per-chunk rate CV 1.6–2.2): unpaired starts sit inside the 2 densest 25 s chunks of each stem (density-burst class). Labelled MIXED by the pre-declared rule; no retune. Byte-det x2. Figure `fig_unpaired_starts_c83.png`. c84 candidate: chunk-window-constrained pairing OR per-chunk MuScriptor caching (not implemented).", "Prereg mtime < output mtime; per-(song,stem) hypothesis table; no reindex output modified; byte-det x2.", f"{P}/reindex-fidelity-c82"),
     ("M-V5-GEN-1/gen-renders-ear-scored-informational-c83", "G5", f"c83 S5 INFORMATIONAL: `scripts/v5/score_gen_batch_v5.py` scored the 15 gen renders + interpolation demo through the amended venv (READ-ONLY c74 extractor + c76 v2 calibration on fresh exemplar signatures). ≥ 6: {t['n_gen_ge_6']}/15 (CG-donor + PD-donor songs); scores 5.72–6.25 sit inside the band-4 context range {t['band4_v2_context']} → non-discriminative under the c76 L119 proof. 16 sibling `ear_score_v5.json`; manifests + WAVs byte-identical; table byte-det x2. NOT a passer declaration; FD-6 governs; M-V5-GEN-1 stays gated on M-V5-RULES-1.", "16 sibling score files; x2 byte-det; manifests/WAVs byte-identical; informational framing explicit.", "M-V5-GEN-1"),
     ("_infra/harmony-gated-record-tombstone-c83", "G1", "c83 S6 F4: `harmony_v5_gated.json` superseded by `harmony_markov_v5.json` (str supersede); gated file byte-identical; `data/v5/rules/README_c83.md` one-liner.", "README present; gated file unchanged.", "—"),
    ]
    hb_p = C / "hook_at_birth_c83.json"
    if hb_p.exists():
        hb = j(hb_p)
        for s, v in hb["per_song"].items():
            tm = j(C / s / "transcription_manifest.json")
            rows.append((f"{P}/{s}-reindexed-c83", "G4", f"c83 per-song lossless record: {tm.get('title')} ({s}, bpm_v5 {tm['bpm_v5']}): landed under the restarted driver (PID 10247) with the hook live at birth — sidecar Δ {v.get('sidecar_minus_manifest_s')} s after the manifest; hook_at_birth={v['hook_at_birth']}; paired {v.get('paired_total')} / unpaired {v.get('unpaired_total')}; MIDI note_on == JSON starts {v.get('note_on_equals_starts_all')}; zero catch-up.", "Sidecar SHAs match disk; note_on == starts; hook-at-birth evidence.", f"{P}/hook-at-birth-verification-c83"))
        rows.append((f"{P}/hook-at-birth-verification-c83", "G4", f"c83 S3: {hb['n_landed_total']}/26 landed; post-restart landings {hb['new_landings']}; all hook_at_birth={hb['all_new_hook_at_birth']}; `reindex_landed()` no-op {hb['catch_up_is_noop']}. Invariant (d): {hb['invariant_d_disclosure']}.", "Every new landing has a matching sidecar with hook-at-birth evidence; zero catch-ups.", f"{P}/reindex-hygiene-c81"))
    else:
        rows.append((f"{P}/hook-at-birth-verification-c83", "G4", "c83 S3: no post-restart landing on disk at registration (song 9 in flight); verifier `scripts/v5/hook_at_birth_c83.py` on disk; per-song rows append when a landing occurs.", "Verifier on disk.", f"{P}/reindex-hygiene-c81"))
    v5d_p = C / "tempo_v5d_falsification.json"
    if v5d_p.exists():
        v5d = j(v5d_p)
        rows.append((f"{P}/tempo_v5d-preregistered-c83", "G4", f"c83 S7: `tempo_v5d_preregistration.json` BEFORE any output — {v5d.get('criterion_summary', 'see file')}.", "Prereg mtime precedes every tempo_v5d.json; 26/26; byte-det x2.", f"{P}/tempo-mechanism-verdict-c82"))
        rows.append((f"{P}/tempo_v5d-verdict-c83", "G4", v5d.get("por_narrative", f"c83 S7 verdict {v5d['verdict']}"), "Verdict ∈ frozen enum; no retune; no recanonicalization this cycle.", f"{P}/tempo_v5d-preregistered-c83"))
    else:
        rows.append((f"{P}/tempo_v5d-deferred-c83", "G4", "c83 S7: TEMPO_V5D_DEFERRED_WALL_BUDGET — optional refined-lag criterion not attempted; blocked file untouched; PD + Disco A remain out of rules.", "Deferral enum recorded.", f"{P}/tempo-mechanism-verdict-c82"))
    rows += [
     ("_plan/register-c83-sub-leaves", "G1", f"c83 POR registration row: c83 sub-leaves inserted inline in the `## Milestones` parseable region via `tools/_register_c83_por_rows.py` (idempotent). M-V5-CORPUS-1: {len(landed)}/26 landed, all lossless + sidecar ({landed}); M-V5-EAR-1: amended receipt landed (F2 closed); M-V5-GEN-1: informational scores only, gated on M-V5-RULES-1; PD + Disco A remain tempo-blocked. Test counts refer to the adopted suite.", "Rows added.", "—"),
     ("_infra/adopt-cycle83-tests", "G1", "c83 test-adoption: `tests/test_c83_landing.py` (7) new + `tests/test_ear_venv_c81.py` test_04 additive; adopted suite re-run under /usr/bin/python3 (counts in the ledger event / work output; ADOPTED suite, not tests/ as a whole).", "New tests green + regression green.", "—"),
     ("_archive/cycle-83-scratch", "G1", "c83 scratch archival: emitter + registrar retained in-tree per emitter-exemption pattern; scratchpad runners not in workspace; plot script co-located with its data + figure.", "No workspace scratch to archive.", "—"),
     ("_run/cycle_83_closed", "G1", "c83 CLOSED — v5 REOPENING cycle 5. See ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c83 POR rows present"); return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
