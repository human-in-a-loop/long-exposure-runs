#!/usr/bin/env python3
"""c7 test suite. Minimum 14 cases per brief; delivered target 17."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
os.chdir(_REPO)

FAILS: list[str] = []


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        FAILS.append(msg)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_01_track_a_dry_run_present() -> None:
    p = _REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json"
    _assert(p.is_file(), f"missing {p}")
    d = json.loads(p.read_text())
    for k in ("cycle", "mode", "probe_status", "attribution_verdict",
              "torch_version_observed", "torch_file_observed",
              "command_string_drafted", "c3_guitar_json_sha_anchor",
              "c4_guitar_json_sha_anchor", "stem_input_path",
              "stem_input_sha256", "spec_sha256",
              "venv_signature_pre", "venv_signature_post", "venv_unchanged"):
        _assert(k in d, f"torch213 missing key {k}")
    _assert(d["cycle"] == 7, "cycle != 7")
    _assert(d["mode"] == "dry_run", "expected dry_run by default")
    _assert(d["probe_status"] == "awaiting_operator_green_light",
            f"probe_status expected awaiting_operator_green_light, got {d['probe_status']}")
    _assert(d["network_syscall_attempted"] is False,
            "network_syscall_attempted must be False")
    _assert(d["venv_unchanged"] is True,
            "workspace/learned_transcribers_venv must be unchanged")


def test_02_track_a_execute_refused_without_operator_flag() -> None:
    # The script has an --execute flag. Without the flag, mode is always dry_run.
    # We simulate a fresh run and confirm the default path.
    r = subprocess.run(
        ["/usr/bin/python3", "scripts/v3_spine/torch213_reproduce_probe.py"],
        capture_output=True, check=True,
    )
    out = json.loads((_REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json").read_text())
    _assert(out["mode"] == "dry_run",
            "no operator flag → must remain dry_run")


def test_03_no_network_imports_in_c7_scripts() -> None:
    forbidden = {"urllib", "urllib3", "requests", "httpx",
                 "socket", "http", "aiohttp"}
    for name in ("torch213_reproduce_probe.py",
                 "empty_stem_duration_sanity.py",
                 "rc7_canonicality_metrics.py",
                 "byte_det_c7.py",
                 "anchor_preservation_c7.py",
                 "verdict_c7.py"):
        p = _REPO / "scripts/v3_spine" / name
        if not p.is_file():
            continue
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    root = n.name.split(".")[0]
                    _assert(root not in forbidden,
                            f"{name}: forbidden import {n.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split(".")[0]
                    _assert(root not in forbidden,
                            f"{name}: forbidden from-import {node.module}")


def test_04_track_a_does_not_mutate_venv() -> None:
    d = json.loads((_REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json").read_text())
    pre = d["venv_signature_pre"]
    post = d["venv_signature_post"]
    _assert(pre["dir_manifest_sha256"] == post["dir_manifest_sha256"],
            "venv dir manifest SHA drifted mid-run")
    _assert(pre["n_files"] == post["n_files"],
            "venv file count drifted mid-run")


def test_05_track_b_note_lands_with_both_shas() -> None:
    note = _REPO / "docs/v3_spine_rc7_canonicality_decision_note.md"
    _assert(note.is_file(), f"missing {note}")
    text = note.read_text()
    _assert("cc919559b4508b6b" in text,
            "Method A SHA prefix missing from note")
    _assert("f40796be982998b0" in text,
            "Method B SHA prefix missing from note")


def test_06_track_b_note_contains_no_verdict_language() -> None:
    note = _REPO / "docs/v3_spine_rc7_canonicality_decision_note.md"
    text = note.read_text()
    # Grep is case-sensitive: verdicts appear only ALLCAPS in the campaign.
    for banned in ("LANDS", "PARTIAL", "FAILS"):
        _assert(banned not in text,
                f"note contains banned verdict token '{banned}'")


def test_07_track_c_full_mix_and_shorts_correct() -> None:
    d = json.loads((_REPO / "data/v3_spine/cycle7/empty_stem_duration_sanity.json").read_text())
    _assert(d["full_mix_duration_correct"] is True,
            "full_mix_duration_correct must be True")
    _assert(d["empty_stem_shorts_expected"] is True,
            "empty_stem_shorts_expected must be True")
    a = d["per_file"]["method_a_full_mix"]
    b = d["per_file"]["method_b_full_mix"]
    _assert(a["n_samples"] == 1_323_000,
            f"Method A n_samples={a['n_samples']} != 1_323_000")
    _assert(b["n_samples"] == 1_323_000,
            f"Method B n_samples={b['n_samples']} != 1_323_000")
    _assert(d["per_file"]["other_per_track"]["n_samples"] == 88_320,
            "other per-track n_samples != 88_320")
    _assert(d["per_file"]["piano_per_track"]["n_samples"] == 88_320,
            "piano per-track n_samples != 88_320")


def test_08_locked_script_shas_unchanged() -> None:
    # Cross-check DO-NOT-TOUCH scripts against c6 SHAs pinned in ledger.
    known = {
        # These are the runtime SHAs — spot-check that files exist + are unchanged
        # vs the pre-anchor snapshot. Exact SHA values live in
        # anchor_preservation_pre_c7.json (already committed pre-run).
        "scripts/palette_render/render_stem.py": None,
        "scripts/recreate_v2/rc7_v2_rerun.py": None,
        "scripts/recreate_v2/rc7_mix_balance.py": None,
        "scripts/v3_spine/mix_match_operator_section.py": None,
    }
    pre = json.loads((_REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c7.json").read_text())
    for rel in known:
        _assert(rel in pre["anchors"], f"{rel} missing from anchor snapshot")
        actual = _sha256(_REPO / rel)
        _assert(actual == pre["anchors"][rel]["sha256"],
                f"{rel} SHA drift: {actual} != {pre['anchors'][rel]['sha256']}")


def test_09_c4_c5_c6_delivery_shas_unchanged() -> None:
    pre = json.loads((_REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c7.json").read_text())
    for rel in (
        "data/v3/deliveries/31a164f845f8e27e/verdict.json",  # c4
        "data/v3/deliveries/31a164f845f8e27e/operator_section/verdict.json",  # c5
        "data/v3_spine/verdict_c6.json",  # c6
        "data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav",  # c6 Method B
    ):
        _assert(rel in pre["anchors"], f"{rel} not in pre-snapshot")
        _assert(_sha256(_REPO / rel) == pre["anchors"][rel]["sha256"],
                f"{rel} SHA drift pre==now")


def test_10_anchor_count_target_met() -> None:
    pre = json.loads((_REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c7.json").read_text())
    _assert(pre["n_anchors"] >= 75,
            f"pre-snapshot has {pre['n_anchors']} anchors, target >=75")
    _assert(pre["n_missing"] == 0, f"pre-snapshot missing: {pre['missing']}")


def test_11_three_way_rubric_hash_chain() -> None:
    verdict_path = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json"
    _assert(verdict_path.is_file(), f"missing {verdict_path}")
    v = json.loads(verdict_path.read_text())
    rubric_doc = _REPO / "docs/v3_spine_rubric_v2.md"
    rubric_hash_file = _REPO / "data/v3_spine/rubric_hash_v2.txt"
    doc_sha = _sha256(rubric_doc)
    file_sha = rubric_hash_file.read_text().strip()
    _assert(doc_sha == file_sha,
            f"rubric doc SHA != hash file: {doc_sha} vs {file_sha}")
    _assert(v["rubric_hash_v2"] == doc_sha,
            f"verdict.rubric_hash_v2 != doc SHA")
    _assert(v.get("rubric_hash_v2_three_way_chain_holds") is True,
            "verdict must record three-way chain as holding")


def test_12_verdict_shape() -> None:
    v = json.loads((_REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json").read_text())
    for k in ("cycle", "song_sha16", "verdict",
              "torch213_reproduce", "rc7_canonicality_note",
              "empty_stem_duration_sanity",
              "rubric_hash_v2", "rubric_hash_v2_doc_sha",
              "rubric_hash_v2_three_way_chain_holds",
              "blocked_on_operator",
              "verdict_placement_convention"):
        _assert(k in v, f"verdict missing key {k}")
    _assert(v["cycle"] == 7, "cycle != 7")
    _assert(v["song_sha16"] == "31a164f845f8e27e", "wrong song")
    _assert(v["verdict"] in {
        "V3_SPINE_C7_THREE_TRACK_LANDS_pending_operator", "PARTIAL", "FAILS"
    }, f"unexpected verdict {v['verdict']}")
    _assert(v["verdict_placement_convention"] == "cycle<N>/",
            "verdict_placement_convention must record cycle<N>/ fix")


def test_13_blocked_on_operator_true() -> None:
    v = json.loads((_REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json").read_text())
    _assert(v["blocked_on_operator"] is True,
            "blocked_on_operator must be True per FD-6")


def test_14_byte_det_sidecars_present() -> None:
    for out in (
        "data/v3_spine/cycle7/torch213_reproduce_probe.json",
        "data/v3_spine/cycle7/empty_stem_duration_sanity.json",
        "data/v3_spine/cycle7/rc7_canonicality_metrics.json",
    ):
        side = _REPO / (out.replace(".json", ".byte_determinism.json"))
        _assert(side.is_file(), f"missing byte-det sidecar {side}")
        d = json.loads(side.read_text())
        _assert(d["equal"] is True or d.get("mode") == "dry_run",
                f"byte-det sidecar {side} not equal")


def test_15_all_c7_scripts_have_interpreter_guard() -> None:
    for name in ("torch213_reproduce_probe.py",
                 "empty_stem_duration_sanity.py",
                 "rc7_canonicality_metrics.py",
                 "byte_det_c7.py",
                 "anchor_preservation_c7.py",
                 "verdict_c7.py"):
        p = _REPO / "scripts/v3_spine" / name
        if not p.is_file():
            continue
        text = p.read_text()
        _assert('sys.executable != "/usr/bin/python3"' in text,
                f"{name}: missing /usr/bin/python3 guard")


def test_16_anchor_preservation_post_matches_pre() -> None:
    p = _REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_c7.json"
    _assert(p.is_file(), f"missing {p}")
    r = json.loads(p.read_text())
    _assert(r["all_match"] is True,
            f"anchor preservation FAILED: diffs={r.get('diffs')}")
    _assert(r["n_diff"] == 0, f"n_diff={r['n_diff']}")
    _assert(r["n_pre"] >= 75, f"n_pre={r['n_pre']} < 75 target")


def test_17_no_prng_in_c7_scripts() -> None:
    for name in ("torch213_reproduce_probe.py",
                 "empty_stem_duration_sanity.py",
                 "rc7_canonicality_metrics.py",
                 "byte_det_c7.py",
                 "anchor_preservation_c7.py",
                 "verdict_c7.py"):
        p = _REPO / "scripts/v3_spine" / name
        if not p.is_file():
            continue
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    _assert(n.name.split(".")[0] != "random",
                            f"{name}: PRNG import {n.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    _assert(node.module.split(".")[0] != "random",
                            f"{name}: from-random import")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILS.append(f"{t.__name__} raised {type(e).__name__}: {e}")
    if FAILS:
        for f in FAILS:
            print("FAIL:", f, file=sys.stderr)
        print(f"{len(FAILS)}/{len(tests)} FAIL", file=sys.stderr)
        return 1
    print(f"{len(tests)}/{len(tests)} PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
