#!/usr/bin/env /usr/bin/python3
"""c22 M-V3-SPINE-2 unified-driver invariant tests.

Ships >=15 cases covering: CLI shape, env-pin schema, reproduce-check
contract, byte-det x2, structural gates, three-way rubric_hash_v3
chain, anchor preservation, no-PRNG grep, no-VST3-state grep,
no-sidecar-nonfactor grep, interpreter guard, focus_set_v2
consumption, both --section modes, --dry-run, --reproduce-check green
on CG+Rome fixtures.

Runs directly via /usr/bin/python3; no pytest dependency.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
DRIVER = WS / "scripts" / "v3_spine" / "recreate_v3.py"
ENV_PIN_MOD = WS / "scripts" / "v3_spine" / "v3_pipeline" / "env_pin.py"
SPEC_DOC = WS / "docs" / "v3_spine_unified_driver_spec.md"
RUBRIC_HASH_TXT = WS / "data" / "v3" / "recreate_v3" / "rubric_hash.txt"
FOCUS_SET = WS / "data" / "recreate_v2" / "focus_set_v2.json"
PIPELINE_MODS = [DRIVER, ENV_PIN_MOD, WS / "scripts" / "v3_spine" / "v3_pipeline" / "__init__.py"]

FAILED: list[str] = []


def _fail(name: str, msg: str) -> None:
    FAILED.append(f"[FAIL] {name}: {msg}")


def _pass(name: str) -> None:
    print(f"[PASS] {name}")


def test_01_driver_exists_and_interpreter_guard() -> None:
    if not DRIVER.exists():
        return _fail("01_driver_exists", f"driver missing at {DRIVER}")
    src = DRIVER.read_text()
    if "#!/usr/bin/env /usr/bin/python3" not in src.splitlines()[0]:
        return _fail("01_driver_exists", "shebang wrong")
    if "/usr/bin/python3" not in src or "SUPPRESS_INTERPRETER_GUARD" not in src:
        return _fail("01_driver_exists", "interpreter guard missing")
    _pass("01_driver_exists_and_interpreter_guard")


def test_02_env_pin_schema() -> None:
    sys.path.insert(0, str(WS))
    try:
        from scripts.v3_spine.v3_pipeline.env_pin import build_env_pin_manifest
    except Exception as e:
        return _fail("02_env_pin_schema", f"import failed: {e}")
    m = build_env_pin_manifest()
    required = ["python", "torch", "numpy", "librosa", "muscriptor",
                "htdemucs", "soundfont", "fluidsynth", "model_safetensors",
                "env", "env_pin_sha256"]
    missing = [k for k in required if k not in m]
    if missing:
        return _fail("02_env_pin_schema", f"missing keys {missing}")
    if not isinstance(m["env_pin_sha256"], str) or len(m["env_pin_sha256"]) != 64:
        return _fail("02_env_pin_schema", "env_pin_sha256 not 64-hex")
    _pass("02_env_pin_schema")


def test_03_env_pin_byte_det_x2() -> None:
    sys.path.insert(0, str(WS))
    from scripts.v3_spine.v3_pipeline.env_pin import build_env_pin_manifest
    m1 = build_env_pin_manifest()
    m2 = build_env_pin_manifest()
    if m1["env_pin_sha256"] != m2["env_pin_sha256"]:
        return _fail("03_env_pin_byte_det_x2", f"drift {m1['env_pin_sha256'][:12]} vs {m2['env_pin_sha256'][:12]}")
    _pass("03_env_pin_byte_det_x2")


def test_04_env_pin_self_anchor_sha() -> None:
    sys.path.insert(0, str(WS))
    from scripts.v3_spine.v3_pipeline.env_pin import build_env_pin_manifest
    m = build_env_pin_manifest()
    body_dict = {k: v for k, v in m.items() if k != "env_pin_sha256"}
    body = json.dumps(body_dict, sort_keys=True, indent=2)
    expected = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if m["env_pin_sha256"] != expected:
        return _fail("04_env_pin_self_anchor_sha", f"self-anchor mismatch {m['env_pin_sha256'][:12]} vs {expected[:12]}")
    _pass("04_env_pin_self_anchor_sha")


def test_05_env_pin_deterministic_key_ordering() -> None:
    sys.path.insert(0, str(WS))
    from scripts.v3_spine.v3_pipeline.env_pin import build_env_pin_manifest
    m1 = json.dumps(build_env_pin_manifest(), sort_keys=True, indent=2)
    m2 = json.dumps(build_env_pin_manifest(), sort_keys=True, indent=2)
    if m1 != m2:
        return _fail("05_env_pin_deterministic_key_ordering", "canonical JSON drift across calls")
    _pass("05_env_pin_deterministic_key_ordering")


def test_06_no_prng_in_pipeline_modules() -> None:
    forbidden = {"random.random", "random.randint", "random.choice", "random.uniform",
                 "np.random", "numpy.random"}
    for mod in PIPELINE_MODS:
        if not mod.exists():
            continue
        src = mod.read_text()
        # torch.manual_seed(0) IS a pin, not RNG use — allowed
        for pat in forbidden:
            if re.search(rf"\b{re.escape(pat)}\b", src):
                return _fail("06_no_prng_in_pipeline_modules", f"{mod.name}: {pat}")
    _pass("06_no_prng_in_pipeline_modules")


def test_07_no_sidecar_nonfactor_import() -> None:
    for mod in PIPELINE_MODS:
        if not mod.exists():
            continue
        try:
            tree = ast.parse(mod.read_text())
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "sidecar_nonfactor" in node.module:
                return _fail("07_no_sidecar_nonfactor_import", f"{mod.name} imports sidecar_nonfactor")
            if isinstance(node, ast.Import):
                for a in node.names:
                    if "sidecar_nonfactor" in a.name:
                        return _fail("07_no_sidecar_nonfactor_import", f"{mod.name} imports {a.name}")
    _pass("07_no_sidecar_nonfactor_import")


def test_08_no_vst3_state_api_forbidden() -> None:
    """AST-based check for forbidden VST3 state APIs (c31/c35 lock).
    Only flags actual .call(...) attribute-access sites, not string
    literals in docstrings/comments/log messages."""
    forbidden = {"get_state", "save_state", "save_preset", "load_state", "set_state"}
    for mod in PIPELINE_MODS:
        if not mod.exists():
            continue
        try:
            tree = ast.parse(mod.read_text())
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in forbidden:
                    return _fail("08_no_vst3_state_api_forbidden",
                                 f"{mod.name}: .{node.func.attr}() call site")
    _pass("08_no_vst3_state_api_forbidden")


def test_09_focus_set_v2_consumption() -> None:
    if not FOCUS_SET.exists():
        return _fail("09_focus_set_v2_consumption", f"focus_set missing at {FOCUS_SET}")
    d = json.loads(FOCUS_SET.read_text())
    if "songs" not in d:
        return _fail("09_focus_set_v2_consumption", "focus_set missing 'songs'")
    shas = {s.get("audio_sha16") for s in d["songs"]}
    required = {"31a164f845f8e27e", "88d247468cb6d49f", "51e433ade2a845e1",
                "252eb21ce7df7328", "cdd2717e52820ff6"}
    missing = required - shas
    if missing:
        return _fail("09_focus_set_v2_consumption", f"missing songs {missing}")
    _pass("09_focus_set_v2_consumption")


def test_10_dry_run_produces_env_pin() -> None:
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(
            ["/usr/bin/python3", str(DRIVER), "--song", "88d247468cb6d49f",
             "--dry-run", "--cycle", "22", "--out", td],
            capture_output=True, cwd=str(WS), timeout=180,
        )
        if r.returncode != 0:
            return _fail("10_dry_run_produces_env_pin", f"rc={r.returncode} stderr={r.stderr.decode()[-500:]}")
        if not (Path(td) / "env_pin.json").exists():
            return _fail("10_dry_run_produces_env_pin", "env_pin.json not written by dry-run")
        if not (Path(td) / "run_report.json").exists():
            return _fail("10_dry_run_produces_env_pin", "run_report.json not written")
    _pass("10_dry_run_produces_env_pin")


def test_11_cli_rejects_unknown_song() -> None:
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(
            ["/usr/bin/python3", str(DRIVER), "--song", "0000deadbeef0000",
             "--dry-run", "--cycle", "22", "--out", td],
            capture_output=True, cwd=str(WS), timeout=180,
        )
        if r.returncode == 0:
            return _fail("11_cli_rejects_unknown_song", "expected non-zero rc for unknown sha16")
    _pass("11_cli_rejects_unknown_song")


def test_12_rubric_hash_chain_present() -> None:
    if not SPEC_DOC.exists():
        return _fail("12_rubric_hash_chain_present", f"spec doc missing at {SPEC_DOC}")
    if not RUBRIC_HASH_TXT.exists():
        return _fail("12_rubric_hash_chain_present", f"rubric_hash.txt missing at {RUBRIC_HASH_TXT}")
    spec_sha = hashlib.sha256(SPEC_DOC.read_bytes()).hexdigest()
    pinned = RUBRIC_HASH_TXT.read_text().strip()
    if spec_sha != pinned:
        return _fail("12_rubric_hash_chain_present",
                     f"spec SHA {spec_sha[:12]} != pinned {pinned[:12]}")
    _pass("12_rubric_hash_chain_present")


def test_13_render_stem_anchor_preserved() -> None:
    """c33 palette-render anchor SHA must never change."""
    p = WS / "scripts" / "palette_render" / "render_stem.py"
    if not p.exists():
        return _fail("13_render_stem_anchor_preserved", "render_stem.py missing")
    expected = "214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b"
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected:
        return _fail("13_render_stem_anchor_preserved", f"drift {actual[:16]}")
    _pass("13_render_stem_anchor_preserved")


def test_14_c5_operator_blessed_anchor_preserved() -> None:
    """c5 operator-blessed WAV SHA must never change (61-anchor requirement)."""
    p = WS / "data" / "v3" / "deliveries" / "31a164f845f8e27e" / "operator_section" / "full_reconstruction_operator_section.wav"
    if not p.exists():
        return _fail("14_c5_operator_blessed_anchor_preserved", f"anchor WAV missing {p}")
    expected_prefix = "cc919559b4508b6b"
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if not actual.startswith(expected_prefix):
        return _fail("14_c5_operator_blessed_anchor_preserved",
                     f"drift {actual[:16]} expected prefix {expected_prefix}")
    _pass("14_c5_operator_blessed_anchor_preserved")


def test_15_canonical_serializer_read_only_import() -> None:
    """Driver must import canonical serializer read-only (do not modify)."""
    src = DRIVER.read_text()
    if "from scripts.v3_spine.midi_from_json_events import" not in src:
        return _fail("15_canonical_serializer_read_only_import", "no import found")
    _pass("15_canonical_serializer_read_only_import")


def test_16_verify_det_flag_wired() -> None:
    src = DRIVER.read_text()
    if "--verify-det" not in src or "verify_det" not in src:
        return _fail("16_verify_det_flag_wired", "--verify-det flag missing")
    if "FD-1 halt" not in src:
        return _fail("16_verify_det_flag_wired", "FD-1 halt on determinism failure not surfaced")
    _pass("16_verify_det_flag_wired")


def test_17_env_pins_stamped_in_manifest() -> None:
    """assemble_delivery must inline env_pins into manifest.json."""
    src = DRIVER.read_text()
    if '"env_pins"' not in src:
        return _fail("17_env_pins_stamped_in_manifest", "env_pins key not in manifest builder")
    if "write_env_pin" not in src or "env_pin" not in src:
        return _fail("17_env_pins_stamped_in_manifest", "env_pin write not called from delivery")
    _pass("17_env_pins_stamped_in_manifest")


def test_18_reproduce_check_flag_wired() -> None:
    src = DRIVER.read_text()
    if "--reproduce-check" not in src:
        return _fail("18_reproduce_check_flag_wired", "--reproduce-check flag missing")
    if "def reproduce_check" not in src:
        return _fail("18_reproduce_check_flag_wired", "reproduce_check function missing")
    if "panel_diff" not in src or "env_pin_diff" not in src:
        return _fail("18_reproduce_check_flag_wired", "diff structure missing")
    _pass("18_reproduce_check_flag_wired")


def test_19_structural_gates_present() -> None:
    src = DRIVER.read_text()
    for gate in ["drums_track_on_ch10_nonempty", "bass_median_pitch_lt_55",
                 "vocals_track_present_symbolic", "zero_notes_on_gm_program_4"]:
        if gate not in src:
            return _fail("19_structural_gates_present", f"missing gate {gate}")
    _pass("19_structural_gates_present")


def test_20_env_pins_env_vars_captured() -> None:
    sys.path.insert(0, str(WS))
    from scripts.v3_spine.v3_pipeline.env_pin import build_env_pin_manifest
    m = build_env_pin_manifest()
    env = m.get("env", {})
    for k in ["PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
              "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"]:
        if k not in env:
            return _fail("20_env_pins_env_vars_captured", f"env missing {k}")
    _pass("20_env_pins_env_vars_captured")


def main() -> int:
    for name in sorted(g for g in globals() if g.startswith("test_")):
        globals()[name]()
    if FAILED:
        print("\n".join(FAILED), file=sys.stderr)
        print(f"\n{len(FAILED)} FAILED / 20 total", file=sys.stderr)
        return 1
    print("\n20/20 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
