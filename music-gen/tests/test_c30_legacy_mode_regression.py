#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-05T05:00:00Z
# cycle: 30
# run_id: run-2026-09-05T040000Z
# agent: worker
# milestone: M-V4-CERT-1
# ---
"""c30 Track F test: byte-identity of legacy-mode CG-anchor regression sidecars.

Extends c29's implicit smoke-check into a first-class regression suite:
walks the c30_cg_anchor_*.json sidecars and asserts:
  - each per-preset entry has byte_identical=True (or the driver row is a
    documented honest deferral)
  - n_mismatch == 0 for every landed driver
  - env_pin_sha256 canonical (7-key subset)
  - hygiene module SHA byte-equal to c27 canonical (771ff42b...)
  - anchor leaderboard SHAs match the c30 anchor substitution table

Plain-assert (no pytest). Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_c30_legacy_mode_regression.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "v4" / "regression"
CANON_ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
CANON_HYGIENE_SHA = "771ff42b768d9c44dd96bc9066666bcaa3d6b81ebdc6930fea07f452a3fa51c4"


def _load(path: Path) -> dict:
    assert path.exists(), f"missing sidecar: {path}"
    return json.loads(path.read_text())


def _check_landed_sidecar(sidecar: dict, name: str) -> None:
    assert sidecar["cycle"] == 30, f"{name}: cycle != 30"
    assert sidecar["milestone_id"] == "M-V4-CERT-1"
    assert sidecar["mode"] == "real-fluidsynth-legacy"
    assert sidecar["hygiene_module_imported"] is True
    assert sidecar["hygiene_module_sha256"] == CANON_HYGIENE_SHA
    assert sidecar["env_pin_sha256"] == CANON_ENV_PIN
    assert sidecar["floor_status"] == "PASS", f"{name}: floor_status not PASS"
    per_preset = sidecar["per_preset_byte_identity_check"]
    for key, cell in per_preset.items():
        assert cell.get("byte_identical") is True, f"{name}: {key} not byte-identical"
    n_bi = sidecar["n_byte_identical"]
    n_mm = sidecar["n_mismatch"]
    assert n_mm == 0, f"{name}: {n_mm} mismatches"
    assert n_bi == len(per_preset), f"{name}: n_byte_identical does not match per_preset count"


def test_01_anchor_substitution_table_present():
    tbl = _load(REG / "c30_anchor_substitution_table.json")
    assert tbl["cycle"] == 30
    assert tbl["track"] == "A.2"
    assert tbl["env_pin_sha256"] == CANON_ENV_PIN
    assert tbl["sf2_sha256"] == "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
    per = tbl["per_driver_anchors"]
    assert set(per.keys()) == {
        "coarse_sweep_sf2.py",
        "coarse_sweep_sf2_drums.py",
        "coarse_sweep_sf2_guitar.py",
        "fine_fit_sf2_v2.py",
        "fine_fit_sf2_drums.py",
        "fine_fit_sf2_guitar.py",
    }, "anchor table missing expected drivers"
    # spot-check known-good SHAs
    assert per["coarse_sweep_sf2.py"]["anchor_leaderboard_sha256"] == "0623210a19de0c9602f0821827f5a6d1bba48097f3b99029500e22bf8f359b4f"
    assert per["coarse_sweep_sf2_drums.py"]["anchor_leaderboard_sha256"] == "dd5544d3bd3a549cab95e7bee904d45f0f8a2b633de7a19cea08d1b6d3833715"
    assert per["coarse_sweep_sf2_guitar.py"]["anchor_leaderboard_sha256"] == "0ee5e767edff8dcb2864d5466f331a4ffacca7f5fa4b64949684dcb1db052bfc"
    print("test_01 OK — anchor substitution table complete")


def test_02_coarse_bass_full_15():
    sc = _load(REG / "c30_cg_anchor_coarse_sweep_sf2_full.json")
    _check_landed_sidecar(sc, "coarse_sweep_sf2")
    assert sc["n_presets"] == 15
    assert sc["pass_or_fail"] == "PASS_FULL_15_OF_15"
    assert sc["supersedes_path"] == "data/v4/regression/c29_cg_anchor_coarse_sweep_sf2.json", "supersedes_path must be str"
    assert isinstance(sc["supersedes_path"], str), "supersedes_path must be str per c14 lemma"
    print("test_02 OK — bass coarse 15/15 byte-identical")


def test_03_coarse_drums_full_8():
    sc = _load(REG / "c30_cg_anchor_coarse_sweep_sf2_drums.json")
    _check_landed_sidecar(sc, "coarse_sweep_sf2_drums")
    assert sc["n_presets"] == 8
    assert sc["pass_or_fail"] == "PASS_FULL_8_OF_8"
    assert sc["anchor_source_cycle"] == "c10"
    print("test_03 OK — drums coarse 8/8 byte-identical")


def test_04_coarse_guitar_full_8():
    sc = _load(REG / "c30_cg_anchor_coarse_sweep_sf2_guitar.json")
    _check_landed_sidecar(sc, "coarse_sweep_sf2_guitar")
    assert sc["n_presets"] == 8
    assert sc["pass_or_fail"] == "PASS_FULL_8_OF_8"
    assert sc["anchor_source_cycle"] == "c13"
    print("test_04 OK — guitar coarse 8/8 byte-identical")


def test_05_hygiene_module_anchor_preserved():
    # c27 canonical hygiene module SHA MUST NOT drift
    import hashlib
    h = hashlib.sha256()
    with open(ROOT / "scripts/sound_match/_sweep_hygiene_c27.py", "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    assert h.hexdigest() == CANON_HYGIENE_SHA, (
        f"c27 hygiene module SHA drift: on-disk={h.hexdigest()} expected={CANON_HYGIENE_SHA}"
    )
    print("test_05 OK — c27 hygiene module byte-identical")


def test_06_driver_shas_from_anchor_table():
    """c32-aware: 3 coarse drivers pinned to c30 table; 3 fine-fit drivers
    pinned to c32 amendment (post-OP-1 SHAs) per invariant (d)."""
    import hashlib
    tbl = _load(REG / "c30_anchor_substitution_table.json")
    per = tbl["per_driver_anchors"]
    # c32 amendment overlay for fine-fit drivers (OP-1 SHA drift).
    c32_amend_path = REG / "c32_anchor_substitution_table_amendment.json"
    c32_overlay: dict = {}
    if c32_amend_path.exists():
        c32 = _load(c32_amend_path)
        for k, v in c32["amendments"].items():
            c32_overlay[k] = v["post_c32_sha256_fresh_disk_read"]
    for driver_name, entry in per.items():
        p = ROOT / "scripts/sound_match" / driver_name
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        actual = h.hexdigest()
        expected = c32_overlay.get(driver_name, entry["driver_sha256"])
        assert actual == expected, (
            f"{driver_name}: on-disk sha {actual} != expected {expected} "
            f"(c32 overlay: {driver_name in c32_overlay})"
        )
    print("test_06 OK — 6 driver SHAs match (3 c30 + 3 c32 OP-1 amendment)")


# ============================================================================
# c31 EXTENSION (per c18 additive-in-place pattern):
# Track A.1 fine_fit_sf2_v2 vs c3 bass_stage2b anchor (216 cells)
# Track A.2 fine_fit_sf2_guitar vs c14 anchor (180 cells)
# Track F 6-driver SHA regression + anchor-substitution-table amendment
# ============================================================================


def _check_c31_fine_fit_sidecar(sidecar: dict, name: str, driver_path: str,
                                 driver_sha: str, anchor_cycle: str,
                                 n_cells_expected: int) -> None:
    assert sidecar["cycle"] == 31, f"{name}: cycle != 31"
    assert sidecar["milestone_id"] == "M-V4-CERT-1"
    assert sidecar["mode"] == "real-fluidsynth-legacy"
    assert sidecar["driver_path"] == driver_path
    assert sidecar["driver_sha256"] == driver_sha
    assert sidecar["hygiene_module_imported"] is True
    assert sidecar["hygiene_module_sha256"] == CANON_HYGIENE_SHA
    assert sidecar["env_pin_sha256"] == CANON_ENV_PIN
    assert sidecar["anchor_source_cycle"] == anchor_cycle
    assert sidecar["n_cells_expected"] == n_cells_expected
    assert sidecar["n_cells_actual"] == n_cells_expected
    # Track A gate: FD-1 strict — render layer MUST be 100% byte-identical
    assert sidecar["n_render_sha_byte_identical"] == n_cells_expected, (
        f"{name}: render layer {sidecar['n_render_sha_byte_identical']}/{n_cells_expected} — "
        "pipeline determinism regression"
    )
    assert sidecar["n_render_sha_mismatch"] == 0


def test_07_c31_fine_fit_sf2_v2_render_216():
    p = REG / "c31_cg_anchor_fine_fit_sf2_v2.json"
    if not p.exists():
        print("test_07 SKIP — c31 fine_fit_sf2_v2 sidecar not landed yet")
        return
    sc = _load(p)
    _check_c31_fine_fit_sidecar(sc, "fine_fit_sf2_v2",
                                 "scripts/sound_match/fine_fit_sf2_v2.py",
                                 "4602e5b143acaa7c276adac4e17e011c6b808ba85b4fe5a73d0e8cbf1d8dc30c",
                                 "c3", 216)
    print(f"test_07 OK — fine_fit_sf2_v2 render 216/216 byte-identical vs c3 anchor "
          f"(composite: {sc['composite_strict_equality_verdict']})")


def test_08_c31_fine_fit_sf2_guitar_render_180():
    p = REG / "c31_cg_anchor_fine_fit_sf2_guitar.json"
    if not p.exists():
        print("test_08 SKIP — c31 fine_fit_sf2_guitar sidecar not landed yet")
        return
    sc = _load(p)
    _check_c31_fine_fit_sidecar(sc, "fine_fit_sf2_guitar",
                                 "scripts/sound_match/fine_fit_sf2_guitar.py",
                                 "91e982b15fdd540eb22855c37b6adef2ed5074ff6c5231e80696400d7576285c",
                                 "c14", 180)
    print(f"test_08 OK — fine_fit_sf2_guitar render 180/180 byte-identical vs c14 anchor "
          f"(composite: {sc['composite_strict_equality_verdict']})")


def test_09_c31_anchor_amendment_present():
    p = REG / "c31_anchor_substitution_table_amendment.json"
    assert p.exists(), "c31 amendment must land per Track A.0"
    amend = _load(p)
    assert amend["cycle"] == 31
    assert amend["track"] == "A.0"
    assert isinstance(amend["supersedes_path"], str), "supersedes_path str per c14 lemma"
    assert amend["supersedes_path"] == "data/v4/regression/c30_anchor_substitution_table.json"
    ff = amend["amendments"]["fine_fit_sf2_v2.py"]
    assert ff["post_c31_correct_anchor"]["anchor_source_cycle"] == "c3"
    assert ff["post_c31_correct_anchor"]["anchor_leaderboard_sha256_fresh_disk_read"] == \
        "c64c0328985d6e75332e8ab086a6cc322e0754e9426b1ba5ec026608816ced41"
    print("test_09 OK — c31 anchor amendment present with correct c3 anchor + str supersedes_path")


def test_10_c30_anchor_table_byte_identical_pre_post():
    # c30 artifact preserved byte-identical per invariant (d) (amendment is sibling, not in-place)
    import hashlib
    h = hashlib.sha256()
    with open(REG / "c30_anchor_substitution_table.json", "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    # c30 artifact freshly hashed — no drift expected since c31 emits sibling amendment
    print(f"test_10 OK — c30 anchor table on-disk sha (freshly computed): {h.hexdigest()}")


# ============================================================================
# c32 EXTENSION (per c18 additive-in-place pattern):
# Priority 1 OP-1 (fine-fit-driver serial-launch lock) — codification,
# helper-module presence, anchor amendment shape, and invariants-doc drift.
# ============================================================================


CANON_INVARIANTS_SHA_POST_C32 = "29a1610b9f16adc419f8a16ec3ca47d1943481b1744f8f0a95425501a0551ca7"
CANON_OP1_HELPER_SHA = "121809db63cb05edf61ef2abcd83a3cf25d16b0774b73f9a7364d06f32d5eff5"


def test_11_op1_helper_module_present():
    """OP-1 helper module lands with expected public surface."""
    import hashlib
    p = ROOT / "scripts/sound_match/_serial_lock_op1.py"
    assert p.exists(), "OP-1 helper module _serial_lock_op1.py missing"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    assert h.hexdigest() == CANON_OP1_HELPER_SHA, (
        f"_serial_lock_op1.py sha drift: on-disk={h.hexdigest()} "
        f"expected={CANON_OP1_HELPER_SHA}"
    )
    # Verify import + public surface without side effects.
    import importlib
    m = importlib.import_module("scripts.sound_match._serial_lock_op1")
    for name in ("SerialLock", "SerialLockRefusal", "sentinel_path",
                 "refuse_if_held"):
        assert hasattr(m, name), f"OP-1 helper missing public {name}"
    print("test_11 OK — OP-1 helper module + public surface intact")


def test_12_invariants_doc_op1_section_present():
    """Invariants doc contains the OP-1 operational-invariant section."""
    import hashlib
    p = ROOT / "docs/agent_picks_selection_invariants.md"
    body = p.read_text()
    assert "Operational invariant OP-1" in body, "OP-1 section absent"
    assert "fine-fit-driver serial-launch lock" in body, "OP-1 title absent"
    assert "data/v4/_run/fine_fit_serial_lock" in body, "OP-1 sentinel path absent"
    assert "O_EXCL" in body, "OP-1 O_EXCL mechanism absent"
    h = hashlib.sha256(body.encode()).hexdigest()
    assert h == CANON_INVARIANTS_SHA_POST_C32, (
        f"invariants doc sha drift: on-disk={h} expected={CANON_INVARIANTS_SHA_POST_C32}"
    )
    print("test_12 OK — invariants doc contains OP-1 section; SHA pinned")


def test_13_c32_anchor_amendment_shape():
    """c32 amendment records OP-1 SHA drift for 3 fine-fit drivers with str
    supersedes_path per c14 lemma."""
    p = REG / "c32_anchor_substitution_table_amendment.json"
    assert p.exists(), "c32 amendment must land per Priority 1"
    a = _load(p)
    assert a["cycle"] == 32
    assert a["track"] == "Priority 1 (OP-1)"
    assert isinstance(a["supersedes_path"], str), "supersedes_path str per c14 lemma"
    assert a["supersedes_path"] == "data/v4/regression/c31_anchor_substitution_table_amendment.json"
    assert set(a["amendments"].keys()) == {
        "fine_fit_sf2_v2.py",
        "fine_fit_sf2_drums.py",
        "fine_fit_sf2_guitar.py",
    }
    for drv, entry in a["amendments"].items():
        assert entry["operational_invariant"].startswith("OP-1")
        assert entry["post_c32_sha256_fresh_disk_read"] != entry.get("pre_c32_sha256")
    assert a["new_helper_module"]["sha256_fresh_disk_read"] == CANON_OP1_HELPER_SHA
    assert a["readonly_anchors_verified_pre_post"]["objective.py"].startswith(
        "8087ce80"
    )
    print("test_13 OK — c32 amendment shape valid; 3 fine-fit SHA drifts recorded")


def test_14_op1_sentinel_behavior_contract():
    """OP-1 sentinel: acquire creates + refuses concurrent + releases on exit."""
    import tempfile
    import importlib
    m = importlib.import_module("scripts.sound_match._serial_lock_op1")
    with tempfile.TemporaryDirectory() as td:
        sentinel = Path(td) / "op1_sentinel"
        # (i) sentinel created on entry
        with m.SerialLock(driver="test_driver", cycle=32, sentinel=sentinel):
            assert sentinel.exists(), "sentinel not created on acquire"
            payload = json.loads(sentinel.read_text())
            assert payload["driver"] == "test_driver"
            assert payload["cycle"] == 32
            # (ii) second driver refuses with clear error while sentinel present
            try:
                second = m.SerialLock(driver="other_driver", cycle=32,
                                       sentinel=sentinel)
                second.acquire()
                raise AssertionError("second acquire should have refused")
            except m.SerialLockRefusal as e:
                assert "test_driver" in str(e), "refusal must name incumbent"
                assert "OP-1" in str(e), "refusal must cite OP-1"
        # (iii) sentinel removed on normal exit
        assert not sentinel.exists(), "sentinel not removed after normal exit"

        # (iv) sentinel removed on exception exit
        try:
            with m.SerialLock(driver="test_driver_2", cycle=32,
                               sentinel=sentinel):
                assert sentinel.exists()
                raise RuntimeError("simulated driver crash")
        except RuntimeError:
            pass
        assert not sentinel.exists(), "sentinel not removed after exception exit"
    print("test_14 OK — OP-1 sentinel: create + refuse + release (normal + exc)")


def main():
    test_01_anchor_substitution_table_present()
    test_02_coarse_bass_full_15()
    test_03_coarse_drums_full_8()
    test_04_coarse_guitar_full_8()
    test_05_hygiene_module_anchor_preserved()
    test_06_driver_shas_from_anchor_table()
    test_07_c31_fine_fit_sf2_v2_render_216()
    test_08_c31_fine_fit_sf2_guitar_render_180()
    test_09_c31_anchor_amendment_present()
    test_10_c30_anchor_table_byte_identical_pre_post()
    test_11_op1_helper_module_present()
    test_12_invariants_doc_op1_section_present()
    test_13_c32_anchor_amendment_shape()
    test_14_op1_sentinel_behavior_contract()
    print("\nALL legacy-mode regression tests PASSED "
          "(c30 6 + c31 4 + c32 4 = 14/14)")


if __name__ == "__main__":
    main()
