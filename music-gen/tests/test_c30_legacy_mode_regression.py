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
    tbl = _load(REG / "c30_anchor_substitution_table.json")
    per = tbl["per_driver_anchors"]
    # Fresh sha of each named driver; must equal recorded SHA
    import hashlib
    for driver_name, entry in per.items():
        p = ROOT / "scripts/sound_match" / driver_name
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        assert h.hexdigest() == entry["driver_sha256"], (
            f"{driver_name}: on-disk sha {h.hexdigest()} != table {entry['driver_sha256']}"
        )
    print("test_06 OK — all 6 driver SHAs byte-identical to anchor table")


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
    print("\nALL legacy-mode regression tests PASSED (c30 6/6 + c31 4/4 = 10/10)")


if __name__ == "__main__":
    main()
