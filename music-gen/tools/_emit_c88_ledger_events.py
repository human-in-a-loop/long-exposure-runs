#!/usr/bin/python3
"""c88 (= harness c132, offset 44) one-shot ledger emitter — v5 REOPENING cycle 10: F3 `--f3` wired (default off) + iteration 4 on the n=23
chain with the adopted PD / Disco A tempos; F4 POR row amended; disk prune; n=25 deferral; tests; POR; close.

created: 2026-09-10T06:35:00Z
cycle: 88
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _archive/cycle-88-scratch

Every event carries `agent`; event_id = UUID5(NAMESPACE_URL, canonical JSON minus event_id/ts); idempotent on (milestone_id, cycle == 88);
supersedes_path str|None (c14 lemma). FAILS CLOSED (MissingArtifact) on every hard-read path. df via `df -P` (driver semantics).
Retained in-tree per docs/emitter_exemption_policy.md.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 88
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
NAMES = {"252eb21ce7df7328": "WIG", "31a164f845f8e27e": "CG", "51e433ade2a845e1": "Rome", "88d247468cb6d49f": "PD", "cdd2717e52820ff6": "Disco A"}
TEST_RESULTS = Path("data/v5/logs/test_results_c88.json")


class MissingArtifact(FileNotFoundError):
    pass


def _sha(p) -> str:
    p = Path(p)
    if not p.exists():
        raise MissingArtifact(str(p))
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _j(p):
    p = Path(p)
    if not p.exists():
        raise MissingArtifact(str(p))
    return json.loads(p.read_text())


def _df():
    row = subprocess.run(["df", "-P", "."], capture_output=True, text=True, check=True).stdout.splitlines()[-1].split()
    return int(row[4].rstrip("%")), round(int(row[3]) * 1024 / 1e9, 3)


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _ev(milestone_id, status, level, rationale, narrative, artifacts, supersedes_path=None):
    body = {"agent": "worker", "artifacts": artifacts, "confidence": {"assessor": "worker", "level": level, "rationale": rationale},
            "cycle": CYCLE, "env_pin_sha256": ENV_PIN, "milestone_id": milestone_id, "narrative": narrative,
            "run_id": RUN_ID, "status": status, "supersedes_path": supersedes_path, "ts": TS}
    body["event_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, _canonical({k: v for k, v in body.items() if k not in ("event_id", "ts")})))
    return body


def main() -> int:
    roll = _j("data/v5/gen/iteration_04/iteration_rollup.json")
    bd = _j("data/v5/gen/byte_determinism_c88.json")
    ent = bd["entries"]
    stall = _j("data/v5/gen/stall_counter.json")
    sc = _j("data/v5/gen/gen_v5_iter04_ear_scores_c88.json")
    lm = _j("data/v4/generated/v5_iter_04/listening_manifest.json")
    launch = _j("data/v5/logs/gen_iter04_c88.launch.json")
    prereg = _j("data/v5/gen/f3_prereg_c88.json")
    prune = _j("data/v5/logs/c88_prune.json")
    tests = _j(TEST_RESULTS)
    df_now, avail_now = _df()
    f3 = roll["f3"]
    it4 = ent["iteration_04_renders"]
    fo3, fo2 = ent["iteration_03_flag_off_replay"], ent["iteration_02_flag_off_replay"]
    post = bd["post_edit_script_sha256"]["generate_v5"]
    assert post == _sha("scripts/v5/generate_v5.py") == roll["generator_hash"], "generator image drifted after the render"
    pre = bd["turn_start_pins"]["generate_v5_pre_edit"]["sha256"]
    final = bd["f3_enum_final"]
    it4_wavs = [f"data/v5/gen/iteration_04/{s['generated_song_id']}_donor_{s['donor']}/ab_mix.wav" for s in roll["songs"]]
    it4_art = it4_wavs + [w.replace("ab_mix.wav", "ab_mix.manifest.json") for w in it4_wavs] + [w.replace("ab_mix.wav", "ab_mix.replay_proof.json") for w in it4_wavs]
    listening = [r["dest"] + "/ab_mix.wav" for r in lm["samples"]] + ["data/v4/generated/v5_iter_04/listening_manifest.json"]
    parts = {NAMES[s["donor"]]: {p: (v["n_note_on"], v["raw_render_rms_dbfs"], v["program"]) for p, v in _j(f"data/v5/gen/iteration_04/{s['generated_song_id']}_donor_{s['donor']}/ab_mix.manifest.json")["f3"]["parts"].items()} for s in roll["songs"]}
    tempos = {NAMES[s["donor"]]: (s["tempo_bpm"], s["tempo_source"]) for s in roll["songs"]}
    n_tests_pass = sum(v["n_pass_lines"] for v in tests.values())
    por_rows = [l for l in Path("plan_of_record.md").read_text().splitlines() if l.startswith("| M-V5-GEN-1/F4-tempo-fix | G5 |")]
    assert len(por_rows) == 1 and "c86 RESOLVED" in por_rows[0]
    events = []

    events.append(_ev("_plan/guidance-continuation-c88", "validated", "high", "on-disk guidance directory scanned at turn start; no file newer than the c131 guidance.",
        "c88 (= harness c132, offset 44): no new operator guidance file landed; the c131 guidance `docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt` "
        f"(sha16 {_sha('docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt')[:16]}) continues to govern — F2 done (F2_PARTIAL stands, RMS-variance ≥ 1.5 on 0/5, drums < 1.0; no retune), this cycle is F3; "
        f"the backlog guidance (sha16 {_sha('docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt')[:16]}) sets one feature per cycle. No c87 audit report on disk at turn start (reports/cycles has 128-130); the c87 MODERATE named in the brief (F4 POR row) is fixed below.",
        ["docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt", "docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt"]))

    events.append(_ev("_infra/disk-prune-c88", "validated", "high", "df read with `df -P` before and after; prune record on disk.",
        f"c88 P0a disk prune: df {prune['df_before']['used_pct']} % ({prune['df_before']['avail_gb']} GB avail) at open — at the 85 % prune threshold; pruned ONLY regenerable transients: the c85–c87 ×2 render tempdirs under /tmp "
        f"({prune['pruned_mb']} MB: flag-off iteration 1/2 sets, the uniform-velocity twin, score run2, profiles run2 — all reproducible from the commands pinned in byte_determinism_c86.json); nothing under data/v4/**, data/v5/corpus/** canonical dirs or profiles; "
        f"no `_transient/` dirs and no stale per-track WAVs under data/v5; the 48 MB c84 groove-model copy under iteration_01/ left in place (never delete workspace artifacts; disclosed). df after {prune['df_after']['used_pct']} % ({prune['df_after']['avail_gb']} GB); "
        f"at emit {df_now} % ({avail_now} GB); never ≥ 90 %.", ["data/v5/logs/c88_prune.json"]))

    events.append(_ev("_plan/f4-tempo-fix-por-row-amended-c88", "validated", "high", "row amended by the idempotent registrar (`--f4-amend`), c85 wording preserved verbatim; test_c88_landing::test_08 asserts the clause + the untouched c85 verdict anchor.",
        "c88 P0b (closes the c87 auditor MODERATE): the POR row `M-V5-GEN-1/F4-tempo-fix` still described the c85 F4_HALF_DOUBLE_AMBIGUOUS / MUST-NOT-CONSUME state; an ADDITIVE `c86 RESOLVED` clause was appended via `tools/_register_c88_por_rows.py --f4-amend` "
        "(operator adopted PD 122.197271 / Disco A 120.272335 under the guidance addendum sha16 8677bb0cd3f240a0; blocked file amended eb78cfc0ce57dc9f…, pre 2fbabc07… kept as stale/; canonical_v5c_reindexed ×2; n=23 rules consumed from iteration 4; F4 CLOSED per the c87 validated/high ledger row; "
        f"see `M-V5-CORPUS-1/tempo-f4-operator-resolved-c86`). The c85 verdict file `data/v5/corpus/tempo_f4_verdict_c85.json` (sha {_sha('data/v5/corpus/tempo_f4_verdict_c85.json')[:16]}…) is untouched and is the superseded path.",
        ["plan_of_record.md", "tools/_register_c88_por_rows.py"], supersedes_path="data/v5/corpus/tempo_f4_verdict_c85.json"))

    events.append(_ev("M-V5-GEN-1/f3-preregistered-c88", "validated", "high", "prereg mtime precedes every iteration-4 output (test_c88_landing::test_01); prereg sha pinned in the rollup and every manifest.",
        f"c88 P0d: `data/v5/gen/f3_prereg_c88.json` (sha {_sha('data/v5/gen/f3_prereg_c88.json')[:16]}…) written BEFORE any F3 output: part definitions (per-bar IOI walk sampled by SHA-256 inverse-CDF from the corpus 16th-IOI histogram — NOT the structureless slot histogram, disclosed; "
        "round(chord_size_mean) chord tones capped at 6 over the chain state on the form plan; register_low guitar 52 / piano 60 / other 48; `other` = pad per the corpus sustain 8.95 beats; parts follow the KEYS mute mask of the F1 arrangement), program policy (donor pinned `<part>.json` if present — only CG guitar.json prog 28 exists — "
        f"else GM shims 27 / 0 / 89, listed per song: {sum(1 for s in prereg['program_policy']['per_song'].values() for p in s['parts'].values() if p['source'] == 'gm_shim')}/15 cells shims), velocities via the F2 keys-by-slot ladder, SHA-256 inverse-CDF only, per-song clauses (≥ 32 note_on per part, −60 dB audibility floor on the normalised track, replay ×2) + iteration clause (F3-off reproduces iteration 3), "
        "frozen enum F3_LANDS / F3_PARTIAL / F3_FAILS, held-constant list (harmony n=23, groove n=23, form plan, velocity profiles, bass model, VOMM, env pin, donors, SF2).", ["data/v5/gen/f3_prereg_c88.json"]))

    events.append(_ev("_infra/f3-wiring-and-tempo-overrides-c88", "validated", "high", "pre/post SHAs pinned; flag-off reproduction under the post-edit image recorded ×5 for iteration 3 and ×5 for iteration 2; argparse guard tested.",
        f"c88 P0e: `scripts/v5/generate_v5.py` edited ADDITIVELY (pre {pre[:16]}… → post {post[:16]}…): `--f3` default OFF consuming the READ-ONLY c87 builder `scripts/v5/comping_gen_v5.py` ({_sha('scripts/v5/comping_gen_v5.py')[:16]}…, untouched), sub-flag `--comping-model` rejected without `--f3` (argparse error, mirrors the c87 F2 fix), "
        "independent `--tempo-overrides <json>` (donor_tempo consults it first; None on every flag-off run), pin-path args `--harmony-prereg` / `--groove-prereg` (c84 defaults). Flag-off under the post-edit image: "
        f"iteration 3 {fo3['n_equal']}/5 (tempdir {fo3['tempdir']}, {fo3['wall_s']} s) and iteration 2 {fo2['n_equal']}/5 (tempdir {fo2['tempdir']}). `/usr/bin/python3` guard + `created:` stamps present; no PRNG.",
        ["scripts/v5/generate_v5.py", "data/v5/gen/byte_determinism_c88.json", "data/v5/logs/flagoff_c88.log"]))

    events.append(_ev("M-V5-GEN-1/iteration-04-c88", "validated", "high", "5/5 REPLAY_PROOF_HOLDS in fresh tempdirs under the post-edit image; F3-off reproduces iteration 3 5/5; enum from the prereg; scores informational only (FD-6).",
        f"c88 iteration 4 RENDERED (detached at turn start, PID {launch['pid']}, `{launch['log']}`): `{launch['generate_command']}` under generator sha {post[:16]}… on the n=23 chain (harmony {roll['rules_sha256']['harmony_chain'][:8]}… NON_DEGENERATE, "
        f"groove {roll['rules_sha256']['groove_model'][:8]}… GROOVE_V2_OVERFITS disclosed) with the adopted tempos {tempos} (PD / Disco A donor tempo switched from the frozen anchor to the adopted value from this iteration — closes the donor_tempo frozen-anchor minor item). "
        f"{it4['n_equal']}/5 REPLAY_PROOF_HOLDS; forms {[''.join(s['form']) for s in roll['songs']]}; durations {[s['duration_s'] for s in roll['songs']]} s. F3 parts per song {{donor: {{part: (note_on, raw render dBFS, program)}}}} = {parts}; "
        f"per-song clauses (≥ 32 note_on + audible + replay) {f3['n_songs_all_per_song_clauses']}/5; F3-off clause {fo3['n_equal']}/5 → **{final}**. Informational ear scores (venv c76 v2; FD-6, no passer): ≥ 6 {sc['n_gen_ge_6']}/5, "
        f"{[round(v['ear_score_v2'], 3) for v in sc['scores'].values()]}, table ×2 {ent['iteration_04_ear_scores_table']['equal']}. Listening copies → data/v4/generated/v5_iter_04/ ({len(lm['samples'])} songs, SHA-verified). "
        f"Stall {stall['iterations']}/{stall['budget']} with the F6 entry (feature '{stall['history'][-1]['feature']}', seed 3, rules/form/donor/comping/tempo SHAs). Figure `iteration_04/fig_iter04_parts_c88.png` via `plot_iter04_parts_c88.py --out` (reference lines = the prereg clauses).",
        it4_art + listening + ["data/v5/gen/iteration_04/iteration_rollup.json", "data/v5/gen/byte_determinism_c88.json", "data/v5/gen/stall_counter.json", "data/v5/gen/gen_v5_iter04_ear_scores_c88.json",
                               "data/v5/gen/iteration_04/fig_iter04_parts_c88.png", "data/v5/gen/iteration_04/plot_iter04_parts_c88.py", "data/v5/logs/gen_iter04_c88.launch.json", "data/v5/logs/gen_iter04_c88.log",
                               "data/v5/logs/generate_v5_iter04_c88.log"]))

    f3_status, f3_level = ("validated", "high") if final == "F3_LANDS" else ("in-progress", "medium")
    events.append(_ev("M-V5-GEN-1/F3-guitar-piano-other", f3_status, f3_level, f"enum {final} from the pre-registered clauses; recorded, not retuned (FD-1).",
        f"c88 F3 GUITAR / PIANO / OTHER: `--f3` wired (default off) and iteration 4 rendered → **{final}** (parts ≥ 32 note_on + audible + replay ×2 on {f3['n_songs_all_per_song_clauses']}/5 songs; F3-off reproduces iteration 3 {fo3['n_equal']}/5). "
        f"Comping from the c87 statistics (COMPING_NON_DEGENERATE; IOI walk, slot histogram unused — structureless, disclosed); programs: CG guitar via the pinned `guitar.json` (prog 28), every other (song, part) cell a GM shim (27 / 0 / 89; disclosed, not profiled); velocities from the F2 keys-by-slot ladder. "
        f"Supersedes the c87 in-progress record of this milestone (enum F3_FLAG_WIRING_DEFERRED_c88 → resolved).",
        ["scripts/v5/generate_v5.py", "scripts/v5/comping_gen_v5.py", "data/v5/rules/comping_v5.json", "data/v5/gen/f3_prereg_c88.json", "data/v5/gen/iteration_04/iteration_rollup.json", "tests/test_c88_landing.py"]))

    events.append(_ev("_infra/n25-follow-up-deferred-c88", "validated", "high", "one deferral line per the brief's P4 allowance; nothing consumed from it.",
        "c88 P4 (optional) DEFERRED: the n=25 sibling artifacts (eligible_c88 = n=23 ∪ {0e1e8f20592db366, cc0693b4a24f64b2}; harmony / groove / comping re-run, byte-det ×2, NOT consumed by iteration 4) roll to the F5 cycle (c89) — P1–P3 absorbed the wall budget.", []))

    events.append(_ev("_plan/register-c88-sub-leaves", "validated", "high", "rows inserted inline in the parseable region by tools/_register_c88_por_rows.py (idempotent, fail-closed); F4 row amended by the same tool.",
        f"c88 POR registration: F4 row amended (`--f4-amend`) + c88 sub-leaves inserted before `## Sub-milestones`. POR started at sha {bd['turn_start_pins']['plan_of_record_at_open']['sha256'][:16]}… (c87 close). F3 row `M-V5-GEN-1/F3-guitar-piano-other` (c85) reused — no duplicate row.",
        ["plan_of_record.md", "tools/_register_c88_por_rows.py"]))

    events.append(_ev("_infra/adopt-cycle88-tests", "validated", "high", "adopted suite re-run under /usr/bin/python3; counts from data/v5/logs/test_results_c88.json (ADOPTED suite, not tests/ as a whole).",
        f"c88 test-adoption: `tests/test_c88_landing.py` ({tests.get('tests/test_c88_landing.py', {}).get('n_pass_lines', '?')}/10) new — prereg mtime gate, argparse default-off + sub-flag rejection, parts present 5/5 + program policy, F3-off reproduces iteration 3 + 2, manifests carry n=23 SHAs + adopted tempos, byte-det ×2 with the post-edit sha, AST discipline scan, POR F4 clause, stall 4/12 + listening + figure, iteration 1–3 + READ-ONLY pins byte-identical. "
        f"Re-pins (commented in place as c88 re-pins, disclosed): `test_c85_landing::test_06`, `test_c86_landing::test_05`, `test_c87_landing::test_05` pinned stall `iterations == 3` — the counter advances by design (4/12), so they now assert ≥ 3 and index the iteration-3 history entry explicitly; iteration-3 anchors unchanged. "
        f"Adopted suite {len(tests)} files / {n_tests_pass} PASS lines; all rc=0: {all(v['rc'] == 0 for v in tests.values())}.",
        ["tests/test_c88_landing.py", "tests/test_c85_landing.py", "tests/test_c86_landing.py", "tests/test_c87_landing.py", "data/v5/logs/test_results_c88.json"]))

    events.append(_ev("_archive/cycle-88-scratch", "validated", "high", "one-shot emitter + registrar retained in-tree per emitter-exemption policy and listed as artifacts.",
        "c88 scratch archival: `tools/_emit_c88_ledger_events.py` + `tools/_register_c88_por_rows.py` retained in-tree; pipeline runners (p0_prune_pins_c88, p0_prereg_c88, smoke_f3_c88, run_iter04_c88, launch_iter04_c88, flagoff_c88, bytedet_c88, run_tests_c88) live in the session scratchpad only "
        "(their commands and outputs are pinned in byte_determinism_c88.json + the launch JSON). The smoke + flag-off ×2 tempdirs under /tmp are reclaimable.", ["tools/_emit_c88_ledger_events.py", "tools/_register_c88_por_rows.py"]))

    events.append(_ev("_run/cycle_88_closed", "validated", "high", "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        f"c88 CLOSED — v5 REOPENING cycle 10 (= harness c132, offset 44 disclosed, not reconciled): F3 `--f3` wired default-off + iteration 4 rendered on the n=23 chain with the adopted PD / Disco A tempos → **{final}**; F3-off reproduces iteration 3 {fo3['n_equal']}/5 and iteration 2 {fo2['n_equal']}/5; "
        "F4 POR row amended (c87 MODERATE closed); n=25 follow-up deferred to c89. Disclosures (one line each): F2_PARTIAL stands (RMS ≥ 1.5 on 0/5, drums < 1.0), no retune; comping slot histogram structureless, IOI structured (builder uses IOI); melody VOMM MEMORIZES (0.72); bass model 52.7 % null-chord skips; "
        "groove n=23 OVERFITS (0.637); cross-cycle stem mismatch ACCEPTED; n=25 late landers deferred (P4); GM shims on 14/15 (song, part) cells (only CG guitar pinned); PD / Disco A donor tempo switched to the adopted values from iteration 4; df 86 % → 85 % after a 377 MB /tmp prune (never ≥ 90 %); "
        f"cycle counter c88 on disk vs c132 harness. env_pin {ENV_PIN[:8]}…922ca unchanged. df at emit {df_now} % ({avail_now} GB). Next (c89): F5 interpolation demo (own prereg; seed 4; CG ↔ PD t=0.5 blending groove + harmony), n=25 sibling artifacts, comping slot-histogram diagnostic.",
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_87_closed"))

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
        assert e["agent"] == "worker" and isinstance(e["supersedes_path"], (str, type(None)))
        for a in e["artifacts"]:
            if not Path(a).exists():
                raise MissingArtifact(f"{e['milestone_id']}: {a}")
    existing = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("cycle") == CYCLE:
                existing.add(row.get("milestone_id"))
    to_append = [e for e in events if e["milestone_id"] not in existing]
    if "--dry-run" in sys.argv:
        print(f"DRY RUN: {len(events)} events validated; would append {[e['milestone_id'] for e in to_append]}")
        return 0
    if not to_append:
        print("IDEMPOTENT: all c88 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c88 events")
    for e in to_append:
        print(f"  {e['status']:12s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
