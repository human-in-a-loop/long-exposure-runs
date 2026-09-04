#!/usr/bin/env -S /usr/bin/python3
"""c18 ledger emitter. Appends 8 events via long_exposure.tools.ledger_append.

Events (order matters; named substantive first, then housekeeping):
  1. _infra/adopt-cycle18-full-render-tests           Track 1 tests
  2. _infra/bass-gain-narrative-clarification-c18     Track 1 doc
  3. M-V4-PROFILES-1/rome-opened                      Track 2
  4. _infra/pinned-profile-schema-rationale-c18       Track 3
  5. _infra/cg-ab-mix-lufs-diagnostic-c18             Track 4
  6. _plan/register-c18-showcase-tests-rome-schema-rationale-sub-leaves
                                                      Track 5 POR row
  7. _archive/cycle-18-scratch                        housekeeping
  8. _infra/adopt-cycle18-tests                       housekeeping
  9. _run/cycle_18_closed                             cycle rollup
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")


def _derive_event_id(body: dict) -> str:
    canon = json.dumps(
        {k: v for k, v in body.items() if k not in ("event_id", "ts")},
        sort_keys=True,
        separators=(",", ":"),
    )
    return str(uuid.uuid5(_NAMESPACE, canon))

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

WORKSPACE = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
CYCLE = 18
TS = "2026-09-04T04:35:00Z"


def _sha(rel: str) -> str:
    return hashlib.sha256((WORKSPACE / rel).read_bytes()).hexdigest()


def _sha16(rel: str) -> str:
    return _sha(rel)[:16]


def _append(event: dict) -> None:
    payload = json.dumps(event, sort_keys=True)
    r = subprocess.run(
        [
            "/usr/bin/python3",
            "-m",
            "long_exposure.tools.ledger_append",
            "--workspace",
            str(WORKSPACE),
            "--event",
            payload,
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print("ERR:", r.stderr, file=sys.stderr)
        raise SystemExit(2)
    print("APPENDED", event["milestone_id"], r.stdout.strip())


def confidence(level: str, rationale: str, assessor: str = "worker") -> dict:
    return {"level": level, "rationale": rationale, "assessor": assessor}


def base(milestone_id: str, status: str, narrative: str, artifacts: list[str],
         conf_level: str = "high", rationale: str = "on-disk artifacts verified") -> dict:
    body = {
        "milestone_id": milestone_id,
        "ts": TS,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "agent": "worker",
        "status": status,
        "confidence": confidence(conf_level, rationale),
        "narrative": narrative,
        "artifacts": artifacts,
    }
    body["event_id"] = _derive_event_id(body)
    return body


def main() -> int:
    # 1) Track 1 — tests file
    _append(base(
        "_infra/adopt-cycle18-full-render-tests",
        "validated",
        "c18 Track 1: authored tests/test_deliver_cg_ab_v4_full_render.py "
        "(sha {sha}) with 12 regression cases (≥8 gate). 12/12 PASS: SHA "
        "regression on cg_ab_mix.wav 6e13e007…f9484b; per-cell provenance "
        "manifest schema; bass gain formula (line 244-248 gain=ref_rms/ren_rms "
        "capped [0.05, 4.0]); bass gain amplification semantics (on-disk "
        "2.688385 > 1.0 — guards against c17 'attenuation' narrative drift); "
        "OPT3 htdemucs stem-substitution routing for drums (34492c03…) + "
        "guitar (e4ff08ea…); discipline guards (AST + call-pattern regex; "
        "docstring self-mentions excluded); replay-proof anchor regression + "
        "REPLAY_PROOF_HOLDS verdict; manifest schema shape; piano+other "
        "null_no_synthesis; vocals htdemucs_hybrid_overlay; env_pin canonical "
        "7-key subset with env_pin_sha256 2ac444c3…. Invariant (d) disclosure: "
        "test 05/06 assert on-disk `render_family` + `source_sha256` fields "
        "(c18 brief used shorthand `source`/`sha256`).".format(
            sha=_sha16("tests/test_deliver_cg_ab_v4_full_render.py")
        ),
        artifacts=[
            "tests/test_deliver_cg_ab_v4_full_render.py",
        ],
    ))

    # 2) Track 1 — clarification doc
    _append(base(
        "_infra/bass-gain-narrative-clarification-c18",
        "validated",
        "c18 Track 1: authored docs/sound_match/cg_ab_bass_gain_clarification_c18.md "
        "(sha {sha}) to close c17 auditor MODERATE #1 (narrative-vs-artifact "
        "drift). Corrects the c17 report's 'attenuation, gain 0.093' phrasing "
        "to 'amplification, gain 2.688385 > 1.0' with formula cited from "
        "scripts/sound_match/deliver_cg_ab_v4.py lines 244-248 (gain = ref_rms "
        "/ ren_rms capped [0.05, 4.0]). c17 report is READ-ONLY per FD-1 + "
        "invariant (d); this note supplements, does not rewrite. Semantics "
        "test-anchored in tests/test_deliver_cg_ab_v4_full_render.py::test_04.".format(
            sha=_sha16("docs/sound_match/cg_ab_bass_gain_clarification_c18.md")
        ),
        artifacts=[
            "docs/sound_match/cg_ab_bass_gain_clarification_c18.md",
        ],
    ))

    # 3) Track 2 — Rome opened
    stem_sha = _sha16("data/v4/profiles/51e433ade2a845e1/stem_manifest.json")
    _append(base(
        "M-V4-PROFILES-1/rome-opened",
        "in-progress",
        "c18 Track 2: emitted Rome (sha16 51e433ade2a845e1) v4 stem_manifest.json "
        "(sha {sha}) with 6 htdemucs 6-stem SHAs from "
        "data/v3_spine/51e433ade2a845e1/operator_section/rc9_6stem/ on the "
        "operator D1-chosen section t=62.740..92.740s per focus_set_v2.json. "
        "Byte-parallel to c17 WIG shape at data/v4/profiles/252eb21ce7df7328/"
        "stem_manifest.json. Explicit `blocked_on: _manager/M-V4-METRIC-"
        "SEMANTICS-c16` + note_metric_semantics_carryover — candidate "
        "acceptance under Rome's profile suite awaits Track 2 operator "
        "resolution. NO stage-1 sweeps launched. env_pin_sha256 pinned to "
        "canonical 2ac444c3….".format(sha=stem_sha),
        conf_level="medium",
        rationale="skeleton only; blocked on metric-semantics operator resolution",
        artifacts=[
            "data/v4/profiles/51e433ade2a845e1/stem_manifest.json",
            "scripts/sound_match/_emit_c18_rome_manifest.py",
        ],
    ))

    # 4) Track 3 — schema rationale doc
    _append(base(
        "_infra/pinned-profile-schema-rationale-c18",
        "validated",
        "c18 Track 3: authored docs/pinned_profile_schema_v1_rationale.md "
        "(sha {sha}) to close c17 auditor MODERATE #2 (imprecise 'fabricated "
        "invariant' wording). Companion doc records: invariant (e) codified "
        "at c16 (canonical acceptance_fork shape = c14 4-nested-key + str "
        "supersedes_path per c14 lemma); invariant (d) disclosure norm applied "
        "to c9 bass (operator_authority), c14 drums (canonical), c15 guitar "
        "(3-nested-key, retroactively disclosed). Schema is invariant (e)-"
        "compliant AND invariant (d)-disclosure-compliant; validates all "
        "three on-disk anchors as first-class per FD-1 honesty principle. "
        "Explicit correction: the c17 'fabricated invariant' phrasing was "
        "imprecise; the schema reflects on-disk reality per invariant (d), "
        "does not fabricate. Schema JSON docstring NOT modified this cycle "
        "to preserve c17 anchor sha 8f61d9391a5a3bcf… byte-identical; the "
        "cross-link lives in the rationale doc.".format(
            sha=_sha16("docs/pinned_profile_schema_v1_rationale.md")
        ),
        artifacts=[
            "docs/pinned_profile_schema_v1_rationale.md",
        ],
    ))

    # 5) Track 4 — LUFS diagnostic
    lufs_sha = _sha16("data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.lufs_diagnostic.json")
    _append(base(
        "_infra/cg-ab-mix-lufs-diagnostic-c18",
        "validated",
        "c18 Track 4 (OPTIONAL): pyloudnorm probe SUCCEEDED. Authored "
        "scripts/sound_match/measure_cg_ab_mix_lufs.py (sha {sha_scr}) and "
        "wrote diagnostic sidecar at data/v4/deliveries/31a164f845f8e27e/"
        "cg_ab_mix.lufs_diagnostic.json (sha {sha_out}). LUFS-I measurements: "
        "cg_ab_mix=-15.32, stem_bass=-18.48, stem_drums=-13.69, stem_guitar="
        "-27.86, stem_vocals=-23.97, stem_piano=-inf (silence-floor), "
        "stem_other=-69.74. DIAGNOSTIC ONLY: does not mutate audio bytes; "
        "cg_ab_mix.wav sha 6e13e0075c5d8116… byte-identical pre==post "
        "(asserted in-script). env_pin_sha256 canonical 2ac444c3…".format(
            sha_scr=_sha16("scripts/sound_match/measure_cg_ab_mix_lufs.py"),
            sha_out=lufs_sha,
        ),
        artifacts=[
            "scripts/sound_match/measure_cg_ab_mix_lufs.py",
            "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.lufs_diagnostic.json",
        ],
    ))

    # 6) Track 5 — POR registration row
    _append(base(
        "_plan/register-c18-showcase-tests-rome-schema-rationale-sub-leaves",
        "validated",
        "c18 plan-of-record row registering the 5 new c18 milestone_ids "
        "landed this cycle + 3 housekeeping rows + campaign_state.md refresh. "
        "New rows: _infra/adopt-cycle18-full-render-tests, "
        "_infra/bass-gain-narrative-clarification-c18, "
        "M-V4-PROFILES-1/rome-opened, "
        "_infra/pinned-profile-schema-rationale-c18, "
        "_infra/cg-ab-mix-lufs-diagnostic-c18, "
        "_archive/cycle-18-scratch, _infra/adopt-cycle18-tests, "
        "_run/cycle_18_closed. Closes promise_check drift.",
        artifacts=[
            "docs/campaign_state.md",
        ],
    ))

    # 7) housekeeping — archive scratch
    _append(base(
        "_archive/cycle-18-scratch",
        "validated",
        "c18 scratch archival housekeeping. One-shot Rome manifest emitter "
        "scripts/sound_match/_emit_c18_rome_manifest.py + this ledger emitter "
        "scripts/sound_match/_emit_c18_ledger_events.py retained in-tree for "
        "provenance per c14/c15/c16/c17 pattern; no workspace scratch to "
        "archive to tools/stale/ this cycle.",
        artifacts=[
            "scripts/sound_match/_emit_c18_rome_manifest.py",
            "scripts/sound_match/_emit_c18_ledger_events.py",
        ],
    ))

    # 8) housekeeping — adopt-tests roll-up
    _append(base(
        "_infra/adopt-cycle18-tests",
        "validated",
        "c18 test-adoption housekeeping. Carries the one new c18 test file: "
        "tests/test_deliver_cg_ab_v4_full_render.py (12/12 PASS). Total "
        "pinned-profile + full-render regression cases green cross-cycle: "
        "c16 28 + c17 6 (schema) + c18 12 (full-render) = 46 (exceeds "
        "brief target ≥42).",
        artifacts=[
            "tests/test_deliver_cg_ab_v4_full_render.py",
        ],
    ))

    # 9) cycle closed
    _append(base(
        "_run/cycle_18_closed",
        "validated",
        "c18 CLOSED. Five tracks landed: (1) PRIMARY full-render test debt "
        "fillin (12/12 PASS) + bass-gain narrative clarification "
        "(amplification 2.688385 > 1.0 test-anchored); (2) SECONDARY Rome "
        "stem_manifest.json skeleton opened byte-parallel to WIG (still "
        "blocked_on M-V4-METRIC-SEMANTICS-c16); (3) MINOR schema wording "
        "correction via pinned_profile_schema_v1_rationale.md companion; "
        "(4) OPTIONAL LUFS-I diagnostic sidecar (pyloudnorm PROBE OK, "
        "cg_ab_mix.wav LUFS-I=-15.32); (5) POR + campaign_state.md refresh "
        "+ housekeeping. M-V4-SHOWCASE-1 status: LANDS_pending_operator "
        "(rendered + regression-tested); cg_ab_mix.wav SHA 6e13e007…f9484b "
        "byte-identical pre==post. Track 2 escalation _manager/M-V4-METRIC-"
        "SEMANTICS-c16 carried forward unchanged (blocked_on_operator=true); "
        "c18 does not adjudicate it. No wait-on-operator memo emitted "
        "(BANNED per operator directive 2026-09-03 part 2). Operator ear "
        "remains LANDS authority post-hoc per FD-6.",
        artifacts=[],
    ))

    return 0


if __name__ == "__main__":
    sys.exit(main())
