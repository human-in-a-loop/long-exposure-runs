#!/usr/bin/python3
"""v6 Phase 0 — bootstrap every hand-written input the v5 rule extractors / generator REQUIRE (idempotent).

created: 2026-10-04
milestone: M-V6-DATA-0/bootstrap-v5-inputs

After the container wipe of data/, the v5 scripts crash on missing operator-authored files that no producer script
writes. This script creates them with the exact keys each consumer reads (file:line cites in FILES below), and is safe
to re-run:
  * PREREG files (mtime-gated by their consumers: "prereg must pre-date every output") are written ONLY if absent
    (or --force), so re-running bootstrap after a rules run never trips PREREG_AFTER_OUTPUT;
  * derived / mirror files are rewritten only when their content changes (atomic; sorted keys);
  * eligible lists = harmony chain gate (data/v5/rules/harmony_markov_v5_full.json) when it exists, else every
    manifest song (narrowed later by the content gate + landing); --only eligible refreshes just those;
  * donor_profile_map.json for N = 29 donors (gen_v6_song_01..29, manifest priority order, focus first) with
    bass + drums FluidR3_GM sf2 SHIM profiles under data/v4/profiles/<sha16>/ (bank 0 program 33 fingered bass;
    drums bank 128 program 0; 44100 Hz; gain 0.8; real on-disk sf2 sha256, asserted against the pinned value).
Discipline: /usr/bin/python3 guard (suppressible); env pins; no PRNG; nothing under scripts/v5 touched.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import (  # noqa: E402
    ENV_PIN_SHA256, FOCUS, FOCUS_ABSENT, FOCUS_ORDER, SF2_PATH, SF2_SHA256_PINNED, WS, canonical_json,
    ensure_tempo_overrides_file, interpreter_guard, load_tempo_overrides, pin_env, read_json, sha256_file,
    write_text_atomic)

pin_env()
interpreter_guard()

SCHEMA_VERSION = 1
BUDGET = 12
# profile_writer._NAMESPACE_PROFILE (scripts/sound_match/profile_writer.py) — same uuid5 scheme so ids are comparable.
_NAMESPACE_PROFILE = uuid.UUID("2f4b6c7d-8e9a-4b1c-a2d3-e4f556677889")
BASS_PROGRAM, BASS_NAME = 33, "Fingered Bass"
DRUMS_BANK, DRUMS_PROGRAM, DRUMS_NAME = 128, 0, "Standard Kit"
SAMPLE_RATE, GAIN = 44100, 0.8

# consumer -> why the file must exist (documentation for the operator; mirrors the code survey)
FILES = {
    "data/v5/corpus/recanonicalization_blocked.json": "groove_v5_full_c84.py:49 harmony_v5.py tempo_blocked_effective form_plan_v5.py:224 generate_v5.py:410 (blocked_songs{sha16:{anchor_bpm}}, unblocked_c86)",
    "data/v5/corpus/content_gate_prereg_c84.json": "content_gate_v5.py:87,93,108-111 (rules, expected.blocked; mtime must precede content_blocked.json)",
    "data/v5/corpus/tempo_f4_operator_resolution_c86.json": "recanonicalize_tempo_v5.py:146-151 (adopted_bpm{sha16:bpm}, authority, guidance{path,sha256}, supersedes{path,sha256})",
    "data/v5/corpus/tempo_overrides_c86.json": "harmony_v5/groove_v5_v2/comping_v5 --tempo-overrides, velocity_v5.py:131-135, generate_v5.py:408 (FLAT {sha16: bpm})",
    "data/v5/rules/eligible_c84.json": "bass_pitch_v5.py:323 melody_vomm_v5.py:267 (gate.used)",
    "data/v5/rules/eligible_c86.json": "comping_v5.py:267,290 (gate.used, gate.late_landed_deferred)",
    "data/v5/rules/harmony_prereg_c84.json": "generate_v5.py:875,925 (sha-pinned)",
    "data/v5/rules/groove_prereg_c84.json": "groove_v5_full_c84.py:78,120 (exists; mtime < output), generate_v5.py:876,925 (sha-pinned)",
    "data/v5/rules/comping_prereg_c87.json": "comping_v5.py:265-268 (thresholds == THRESHOLDS, enum == ENUM; mtime < output)",
    "data/v5/gen/form_prereg_c85.json": "form_plan_v5.py:54,219,320 (mtime < output; sha), generate_v5.py:731",
    "data/v5/gen/f2_prereg_c86.json": "bass_pitch_v5.py:64,355 melody_vomm_v5.py:66,317 velocity_v5.py:335 generate_v5.py:912 (sha-pinned)",
    "data/v5/gen/f3_prereg_c88.json": "generate_v5.py:902 (sha-pinned, --f3)",
    "data/v5/gen/f5_prereg_c89.json": "generate_v5.py --f5-prereg (sha-pinned; --f5 not used in v6 iteration 1)",
    "data/v5/gen/stall_counter.json": "generate_v5.py:1084-1085 (iterations, budget, history)",
    "data/v5/logs/": "velocity_v5.py:367 writes velocity_v5_c86.progress.json without mkdir",
    "data/v4/gen/donor_profile_map.json": "generate_v5.py:853,938 (songs[].generated_song_id/donor_song_sha16/donor_song_name/donor_bass_profile_relpath/donor_drums_profile_relpath)",
    "data/v4/profiles/<sha16>/{bass,drums}.json": "generate_v5.py:638-642,652-656 + scripts/sound_match/replay.py:51-62 (family sf2, identity.sf2_path/sf2_sha256/bank/program, params.sample_rate/gain)",
}
# scripts/v5/comping_v5.py:68-69 — asserted verbatim at :265-268
COMPING_THRESHOLDS = {"min_songs": 8, "min_bars_with_onsets_per_song": 16, "pooled_max_slot_mass_lt": 0.5, "chord_window_ms": 30}
COMPING_ENUM = ["COMPING_NON_DEGENERATE", "COMPING_DEGENERATE"]


class Bootstrap:
    def __init__(self, ws: Path, force: bool = False, only: set | None = None):
        self.ws = ws
        self.force = force
        self.only = only
        self.report: list[tuple[str, str]] = []
        self.manifest = read_json(ws / "data/v5/corpus/corpus_manifest.json")
        self.songs = sorted([s for s in self.manifest["songs"] if s.get("in_v5_corpus")], key=lambda s: s["v5_priority_rank"])
        self.sha16s = [s["sha16"] for s in self.songs]
        self.by_sha = {s["sha16"]: s for s in self.songs}

    # ------------------------------------------------------------------------------------------------ primitives
    def _want(self, group: str) -> bool:
        return self.only is None or group in self.only

    def _rel(self, p: Path) -> str:
        return str(p.relative_to(self.ws))

    def write_prereg(self, rel: str, obj: dict) -> None:
        """mtime-gated file: only if absent or --force."""
        p = self.ws / rel
        existed = p.exists()
        if existed and not self.force:
            self.report.append((rel, "kept (prereg; mtime-gated)"))
            return
        write_text_atomic(p, canonical_json(obj))
        self.report.append((rel, "rewritten (--force)" if existed else "created"))

    def write_derived(self, rel: str, obj, flat: bool = False) -> None:
        p = self.ws / rel
        existed = p.exists()
        txt = (json.dumps(obj, sort_keys=True, indent=2) + "\n") if flat else canonical_json(obj)
        changed = write_text_atomic(p, txt)
        self.report.append((rel, "created" if not existed else ("updated" if changed else "unchanged")))

    def sha_or_none(self, rel: str):
        p = self.ws / rel
        return sha256_file(p) if p.exists() else None

    def base(self, consumer: str, **extra) -> dict:
        d = {"schema_version": SCHEMA_VERSION, "env_pin_sha256": ENV_PIN_SHA256, "generator": "scripts/v6/bootstrap_v5_inputs.py",
             "milestone": "M-V6-DATA-0/bootstrap-v5-inputs", "agent": "worker", "consumer": consumer,
             "corpus": {"n_songs": len(self.sha16s), "manifest_sha256": sha256_file(self.ws / "data/v5/corpus/corpus_manifest.json")}}
        d.update(extra)
        return d

    # ------------------------------------------------------------------------------------------------ groups
    def corpus_files(self) -> None:
        if not self._want("corpus"):
            return
        ensure_tempo_overrides_file(self.ws / "data/v6/corpus/tempo_overrides_v6.json")
        self.report.append(("data/v6/corpus/tempo_overrides_v6.json", "present"))
        overrides = load_tempo_overrides(self.ws / "data/v6/corpus/tempo_overrides_v6.json")
        # 1. empty tempo block (schema keys read by groove/harmony/form_plan/generate)
        self.write_derived("data/v5/corpus/recanonicalization_blocked.json",
                           self.base(FILES["data/v5/corpus/recanonicalization_blocked.json"], blocked_songs={}, unblocked_c86={},
                                     note="v6: no tempo-blocked songs; the v6 estimator + overrides serve every song's bpm_v5 directly"))
        # 2. content-gate prereg (mtime-gated)
        self.write_prereg("data/v5/corpus/content_gate_prereg_c84.json",
                          self.base(FILES["data/v5/corpus/content_gate_prereg_c84.json"], cycle="v6-0", written_before_any_output=True,
                                    rules={"R1_content": "n_note_on(full_mix) == 0 AND sum(n_note_on over drums,bass,guitar,other,piano) == 0 from transcription_manifest.json note_counts -> BLOCKED",
                                           "R2_title": "re.search(r'commentary|interview|q&a|talk|podcast|lecture|spoken', title, re.I) -> corroboration only"},
                                    expected={"blocked": [], "note": "v6 corpus: every receipt is a music upload; expected zero R1 firings (recorded, not retuned)"}))
        # 3. operator resolution (adopted tempi = the v6 overrides)
        # authority for Disco A 120.272335 = the c86 F4-close operator addendum when the repo carries it, else the v6 overrides file
        c86_guidance = "docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt"
        guidance_rel = c86_guidance if (self.ws / c86_guidance).exists() else "data/v6/corpus/tempo_overrides_v6.json"
        supersedes_rel = "data/v6/corpus/tempo_v6_summary.tsv"
        self.write_derived("data/v5/corpus/tempo_f4_operator_resolution_c86.json",
                           self.base(FILES["data/v5/corpus/tempo_f4_operator_resolution_c86.json"],
                                     adopted_bpm={k: float(v) for k, v in sorted(overrides.items())},
                                     adopted_names={k: (FOCUS.get(k, {}).get("name") or self.by_sha.get(k, {}).get("title")) for k in sorted(overrides)},
                                     authority="OPERATOR",
                                     guidance={"path": guidance_rel, "sha256": self.sha_or_none(guidance_rel),
                                               "note": "Disco A 120.272335 = F4 close (c86) operator addendum; the v6 override table data/v6/corpus/tempo_overrides_v6.json mirrors it",
                                               "overrides_v6_path": "data/v6/corpus/tempo_overrides_v6.json",
                                               "overrides_v6_sha256": self.sha_or_none("data/v6/corpus/tempo_overrides_v6.json")},
                                     supersedes={"path": supersedes_rel, "sha256": self.sha_or_none(supersedes_rel),
                                                 "note": "the v6 estimator table; the overridden songs' bpm_v6_estimate is superseded by adopted_bpm"}))
        # 4. flat {sha16: bpm} mirror of the v6 overrides (consumers json.loads(...).items() -> float)
        self.write_derived("data/v5/corpus/tempo_overrides_c86.json", {k: float(v) for k, v in sorted(overrides.items())}, flat=True)

    def eligible_files(self) -> None:
        if not self._want("eligible"):
            return
        chain_p = self.ws / "data/v5/rules/harmony_markov_v5_full.json"
        if chain_p.exists():
            gate = dict(read_json(chain_p)["gate"])
            src = {"kind": "harmony_chain_gate", "path": self._rel(chain_p), "sha256": sha256_file(chain_p)}
        else:
            landed = [s for s in self.sha16s if (self.ws / "data/v5/corpus" / s / "transcription_manifest.json").exists()]
            gate = {"n_landed": len(landed), "landed": landed, "n_blocked_skipped": 0, "blocked_skipped": [], "n_content_blocked_skipped": 0,
                    "content_blocked_skipped": [], "content_gate_present": False, "n_used": len(self.sha16s), "used": list(self.sha16s), "min_songs": 3}
            src = {"kind": "manifest_all_songs_pre_transcription", "path": "data/v5/corpus/corpus_manifest.json",
                   "note": "placeholder until harmony_v5.py runs; re-run `bootstrap_v5_inputs.py --only eligible` afterwards (run_pipeline_v6.sh does)"}
        gate.setdefault("late_landed_deferred", [])
        for rel, consumer in (("data/v5/rules/eligible_c84.json", FILES["data/v5/rules/eligible_c84.json"]),
                              ("data/v5/rules/eligible_c86.json", FILES["data/v5/rules/eligible_c86.json"])):
            self.write_derived(rel, self.base(consumer, gate=gate, source=src))

    def rules_preregs(self) -> None:
        if not self._want("preregs"):
            return
        self.write_prereg("data/v5/rules/harmony_prereg_c84.json",
                          self.base(FILES["data/v5/rules/harmony_prereg_c84.json"], cycle="v6-0", written_before_any_output=True,
                                    script="scripts/v5/harmony_v5.py", out_name="harmony_markov_v5_full.json", per_song_subdir="per_song_c84",
                                    pre_declared={"degeneracy": {"max_stationary_mass_lt": 0.60, "min_distinct_qualities": 4, "min_quality_segment_count": 8},
                                                  "min_songs": 3, "exclude_max_simultaneous_starts": 12, "midi_dir_preference": ["canonical_v5c_reindexed", "canonical_v5_reindexed"]},
                                    corpus_rule="landed AND NOT tempo-blocked AND NOT content-blocked, manifest priority order (29-song v6 corpus)"))
        self.write_prereg("data/v5/rules/groove_prereg_c84.json",
                          self.base(FILES["data/v5/rules/groove_prereg_c84.json"], cycle="v6-0", written_before_any_output=True,
                                    script="scripts/v5/groove_v5_full_c84.py", out="data/v5/rules/groove_v5_v2_full.json",
                                    pre_declared={"eligible": "landed AND sidecar AND NOT tempo-blocked AND NOT content-blocked",
                                                  "heldout_fold": "3 eligible sha16 with the lowest sha256('groove_fold_c84|<sha16>')", "n_heldout": 3,
                                                  "alpha": 0.5, "tol": 0.15, "singleton_max": 0.5, "min_distinct": 3, "n_sample": 64,
                                                  "enum": ["GROOVE_V2_GENERALIZES", "GROOVE_V2_OVERFITS", "GROOVE_V2_DEGENERATE"]}))
        self.write_prereg("data/v5/rules/comping_prereg_c87.json",
                          self.base(FILES["data/v5/rules/comping_prereg_c87.json"], cycle="v6-0", written_before_any_output=True,
                                    script="scripts/v5/comping_v5.py", thresholds=dict(COMPING_THRESHOLDS), enum=list(COMPING_ENUM),
                                    rule="COMPING_NON_DEGENERATE iff n_songs_with_ge_16_pooled_bars >= 8 AND pooled_max_slot_mass < 0.5",
                                    held_constant={"eligible": {"path": "data/v5/rules/eligible_c86.json"}, "tempo_overrides": {"path": "data/v5/corpus/tempo_overrides_c86.json"}}))

    def gen_preregs(self) -> None:
        if not self._want("preregs"):
            return
        self.write_prereg("data/v5/gen/form_prereg_c85.json",
                          self.base(FILES["data/v5/gen/form_prereg_c85.json"], cycle="v6-0", written_before_any_output=True,
                                    script="scripts/v5/form_plan_v5.py (via scripts/v6/form_plan_v6.py: FOCUS_ELIGIBLE = focus songs present in the chain)",
                                    pre_declared={"bars_per_block": 8, "similarity_threshold": 0.85, "length_clip": [4, 8], "pcp_duration_cap_beats": 1.0,
                                                  "linkage": "single, deterministic", "fallback_template": ["A", "A", "B", "A", "B", "C", "A", "A"],
                                                  "R1": "each eligible focus song recovers >= 3 labels AND a literal repeat"},
                                    generator_constants={"F1_BARS_PER_SECTION": 8, "F1_MIN_SEGMENTS": 8, "F1_N_CANDIDATES": 8, "F1_INTRO_BASS_ONLY_Q": 0.33,
                                                         "F1_MIN_DURATION_S": 90.0, "F1_MIN_BARS": 32, "F1_MIN_LABELS": 3,
                                                         "enum": ["FORM_PLAN_LANDS", "FORM_PLAN_PARTIAL", "FORM_PLAN_FAILS"]},
                                    focus_eligible_v6=list(FOCUS_ORDER), focus_absent=dict(FOCUS_ABSENT)))
        self.write_prereg("data/v5/gen/f2_prereg_c86.json",
                          self.base(FILES["data/v5/gen/f2_prereg_c86.json"], cycle="v6-0", written_before_any_output=True,
                                    bass_pitch_model={"script": "scripts/v5/bass_pitch_v5.py", "class_order": ["root", "fifth", "octave", "third", "approach", "other"],
                                                      "alpha": 0.5, "n_check": 2000, "tol": 0.15, "conditional_key": "<slot>|<chg>"},
                                    melody_vomm={"script": "scripts/v5/melody_vomm_v5.py", "max_order": 3, "ioi_buckets": [1, 2, 3, 4, 6, 8, 12],
                                                 "singleton_threshold_order3": 0.5, "enum": ["GENERALIZES", "MEMORIZES"]},
                                    velocity_extraction_route_1={"script": "scripts/v5/velocity_v5.py (via scripts/v6/velocity_v6.py)", "window_s": 0.050,
                                                                 "mapping": "midrank p5->40 p95->110", "songs": "every landed eligible song (v6; the v5 FOCUS five is replaced)",
                                                                 "R1": "drums + bass spread >= 6 dB on >= 80 % of songs (v6 generalisation of the v5 >= 4/5 rule)"},
                                    velocity_profiles={"quantile_levels": [0, 10, 25, 50, 75, 90, 100], "route_2_fallback": "pre-declared ladders in velocity_v5.ROUTE2"},
                                    generator={"F2_MELODY_REGISTER": [67, 84], "F2_RMS_RATIO_MIN": 1.5, "F2_RMS_FRAME_S": 0.05, "enum": ["F2_LANDS", "F2_PARTIAL", "F2_FAILS"],
                                               "n_songs": "N donors (v6: 29); LANDS iff every clause holds on all N (scripts/v6/generate_v6.py recomputes the v5 '5 of 5' enums for N)"}))
        self.write_prereg("data/v5/gen/f3_prereg_c88.json",
                          self.base(FILES["data/v5/gen/f3_prereg_c88.json"], cycle="v6-0", written_before_any_output=True,
                                    comping_statistics={"script": "scripts/v5/comping_v5.py", "prereg": "data/v5/rules/comping_prereg_c87.json", "gate": "COMPING_NON_DEGENERATE"},
                                    generator={"parts": ["guitar", "piano", "other"], "gm_shims": {"guitar": 27, "piano": 0, "other": 89},
                                               "register_low": {"guitar": 52, "piano": 60, "other": 48}, "n_note_on_min": 32, "audibility_floor_dbfs": -60.0,
                                               "enum": ["F3_LANDS", "F3_PARTIAL", "F3_FAILS"]}))
        self.write_prereg("data/v5/gen/f5_prereg_c89.json",
                          self.base(FILES["data/v5/gen/f5_prereg_c89.json"], cycle="v6-0", written_before_any_output=True,
                                    status="NOT USED in v6 iteration 1 (--f5 off); present only so the sha-pin path resolves",
                                    note="scripts/v5/interpolate_v5.py:46 NAMES still maps CG/PD which are absent from the v6 corpus; pass sha16 donors if --f5 is ever used"))

    def gen_state(self) -> None:
        if not self._want("gen"):
            return
        p = self.ws / "data/v5/gen/stall_counter.json"
        if p.exists() and not self.force:
            self.report.append(("data/v5/gen/stall_counter.json", "kept (history preserved)"))
        else:
            write_text_atomic(p, json.dumps({"iterations": 0, "budget": BUDGET, "history": [],
                                             "note": "v6 phase-0 reset (generate_v5.py appends one history entry per iteration)"}, indent=2) + "\n")
            self.report.append(("data/v5/gen/stall_counter.json", "created/reset"))
        for d in ("data/v5/logs", "data/v5/rules", "data/v5/gen", "data/v6/logs"):
            (self.ws / d).mkdir(parents=True, exist_ok=True)
        self.report.append(("data/v5/logs/", "present"))

    def donor_map_and_profiles(self) -> None:
        if not self._want("donors"):
            return
        sf2 = Path(SF2_PATH)
        sf2_sha = sha256_file(sf2) if sf2.exists() else SF2_SHA256_PINNED
        if sf2.exists() and sf2_sha != SF2_SHA256_PINNED:
            raise RuntimeError(f"sf2 sha mismatch: on-disk {sf2_sha} != pinned {SF2_SHA256_PINNED}")
        if not sf2.exists():
            print(f"WARNING: {SF2_PATH} missing; profiles carry the pinned sha {SF2_SHA256_PINNED[:16]}... (replay will fail until installed)", file=sys.stderr)
        specs = []
        for i, s in enumerate(self.songs, 1):
            sha16 = s["sha16"]
            pdir = Path("data/v4/profiles") / sha16
            bass = self._profile(sha16, "bass", {"bank": 0, "program": BASS_PROGRAM, "preset_name": BASS_NAME}, {"sample_rate": SAMPLE_RATE, "gain": GAIN}, sf2_sha)
            drums = self._profile(sha16, "drums", {"bank": DRUMS_BANK, "program": DRUMS_PROGRAM, "preset_name": DRUMS_NAME},
                                  {"sample_rate": SAMPLE_RATE, "gain": GAIN, "midi_channel": 10}, sf2_sha)
            self.write_derived(str(pdir / "bass.json"), bass)
            self.write_derived(str(pdir / "drums.json"), drums)
            specs.append({"generated_song_id": f"gen_v6_song_{i:02d}", "donor_song_sha16": sha16,
                          "donor_song_name": FOCUS[sha16]["name"] if sha16 in FOCUS else s.get("title"),
                          "donor_band": s["band"], "donor_tier": s["v5_tier"], "donor_priority_rank": s["v5_priority_rank"],
                          "donor_bass_profile_relpath": str(pdir / "bass.json"), "donor_drums_profile_relpath": str(pdir / "drums.json"),
                          "profiles_are_shims": True})
        dm = self.base(FILES["data/v4/gen/donor_profile_map.json"], n_donors=len(specs), songs=specs,
                       profile_policy={"family": "sf2", "sf2_path": SF2_PATH, "sf2_sha256": sf2_sha,
                                       "bass": {"bank": 0, "program": BASS_PROGRAM, "preset": BASS_NAME}, "drums": {"bank": DRUMS_BANK, "program": DRUMS_PROGRAM, "preset": DRUMS_NAME},
                                       "sample_rate": SAMPLE_RATE, "gain": GAIN, "status": "SHIM placeholders so generate_v5.py renders; Phase 4 replaces with matched profiles"},
                       interpolation_demo={"enabled": False, "pairs": [],
                                           "note": "F5 (--f5) is not part of v6 iteration 1; interpolate_v5.NAMES references CG/PD (absent) — use sha16 donors if enabled"})
        self.write_derived("data/v4/gen/donor_profile_map.json", dm)

    def _profile(self, sha16: str, instrument: str, ident_extra: dict, params: dict, sf2_sha: str) -> dict:
        body = {"schema_v": "v4.0", "song_sha16": sha16, "instrument": instrument, "family": "sf2",
                "identity": {"sf2_path": SF2_PATH, "sf2_sha256": sf2_sha, **ident_extra},
                "params": dict(params), "deps_sha256": {"sf2_sha256": sf2_sha},
                "objective_scores": {"note": "shim: not searched, not scored"},
                "search_metadata": {"stage": "v6_phase0_shim", "cycle": "v6-0", "generator": "scripts/v6/bootstrap_v5_inputs.py"},
                "render_replayable": True,
                "provenance": {"shim": True, "sf2": {"path": SF2_PATH, "sha256": sf2_sha}, "env_pin_sha256_7key": ENV_PIN_SHA256,
                               "note": "placeholder so scripts/v5/generate_v5.py renders (bass: profile; drums: donor_drums_profile_relpath); Phase 4 replaces"}}
        canon = json.dumps({k: v for k, v in body.items() if k != "profile_id" and not k.startswith("render_sha256")},
                           sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        body["profile_id"] = str(uuid.uuid5(_NAMESPACE_PROFILE, canon))
        return body

    def run(self) -> list[tuple[str, str]]:
        self.corpus_files()
        self.rules_preregs()
        self.gen_preregs()
        self.gen_state()
        self.eligible_files()
        self.donor_map_and_profiles()
        return self.report


def required_paths(ws: Path, sha16s: list[str]) -> list[Path]:
    """Every file the v5 consumers need (used by the tests and the runbook check)."""
    fixed = [k for k in FILES if not k.endswith("/") and "<sha16>" not in k]
    out = [ws / f for f in fixed] + [ws / "data/v5/logs"]
    for s in sha16s:
        out += [ws / "data/v4/profiles" / s / "bass.json", ws / "data/v4/profiles" / s / "drums.json"]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="bootstrap the hand-written v5 inputs for the v6 corpus (idempotent)")
    ap.add_argument("--ws", default=str(WS), help="workspace root (tests redirect this)")
    ap.add_argument("--force", action="store_true", help="rewrite preregs / reset the stall counter (breaks PREREG mtime gates of existing outputs!)")
    ap.add_argument("--only", nargs="*", choices=("corpus", "preregs", "gen", "eligible", "donors"), default=None)
    ap.add_argument("--check", action="store_true", help="only report which required files are missing (exit 1 if any)")
    args = ap.parse_args(argv)
    ws = Path(args.ws).resolve()
    man = read_json(ws / "data/v5/corpus/corpus_manifest.json")
    sha16s = [s["sha16"] for s in man["songs"] if s.get("in_v5_corpus")]
    if args.check:
        missing = [p for p in required_paths(ws, sha16s) if not p.exists()]
        for p in missing:
            print(f"MISSING {p.relative_to(ws)}")
        print(f"check: {len(required_paths(ws, sha16s)) - len(missing)}/{len(required_paths(ws, sha16s))} required inputs present")
        return 1 if missing else 0
    b = Bootstrap(ws, force=args.force, only=set(args.only) if args.only else None)
    rep = b.run()
    tally: dict[str, int] = {}
    for rel, status in rep:
        tally[status.split(" ")[0]] = tally.get(status.split(" ")[0], 0) + 1
        if "profiles/" not in rel or status not in ("unchanged",):
            if "profiles/" in rel and status in ("created", "updated") and not rel.endswith("bass.json"):
                continue  # keep the printout short: one line per donor profile pair
            print(f"  {status:28s} {rel}")
    print(f"bootstrap: {dict(sorted(tally.items()))} ({len(rep)} entries) for {len(sha16s)} songs")
    missing = [p for p in required_paths(ws, sha16s) if not p.exists()]
    if missing:
        print(f"ERROR: still missing {[str(p.relative_to(ws)) for p in missing]}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
