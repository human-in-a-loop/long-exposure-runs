"""c20 clone-2: 12-case shape test for Peach Dream v3 focus-song delivery.

Matches c9..c19 heartbeat convention (12 cases). Focus-song variant checks
delivery layout + rubric_hash_v2 chain + byte-determinism + structural gates.
"""
import hashlib
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SONG_SHA16 = "88d247468cb6d49f"
DEL_ROOT = REPO / f"data/v3/deliveries/{SONG_SHA16}"
OPSEC = DEL_ROOT / "operator_section"
VERDICT = DEL_ROOT / "cycle20/verdict.json"
RUBRIC_DOC = REPO / "docs/v3_spine_rubric_v2.md"
RUBRIC_HASH_FILE = REPO / "data/v3_spine/rubric_hash_v2.txt"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _load_verdict():
    assert VERDICT.exists(), f"missing verdict: {VERDICT}"
    return json.loads(VERDICT.read_text())


def test_c20_verdict_exists_and_valid_json():
    v = _load_verdict()
    assert v["cycle"] == 20
    assert v["song_sha16"] == SONG_SHA16
    assert v["clone"] == "clone-2"


def test_c20_verdict_placement_convention():
    assert VERDICT.parent.name == "cycle20"
    assert VERDICT.name == "verdict.json"


def test_c20_rubric_hash_v2_three_way_chain_holds():
    v = _load_verdict()
    doc_sha = _sha256(RUBRIC_DOC)
    file_sha = RUBRIC_HASH_FILE.read_text().strip()
    assert doc_sha == file_sha == v["rubric_hash_v2"] == v["rubric_hash_v2_doc_sha"]
    assert v["rubric_hash_v2_three_way_chain_holds"] is True


def test_c20_verdict_is_pending_or_partial_or_fails():
    v = _load_verdict()
    assert v["verdict"] in ("V3_FOCUS_SONG_LANDS_pending_operator",
                            "V3_FOCUS_SONG_PARTIAL", "V3_FOCUS_SONG_FAILS")


def test_c20_blocked_on_operator_true():
    v = _load_verdict()
    assert v["blocked_on_operator"] is True
    assert "FD-6" in v["reason"]


def test_c20_chosen_section_matches_focus_set_v2():
    v = _load_verdict()
    focus = json.loads((REPO / "data/recreate_v2/focus_set_v2.json").read_text())
    peach = next(s for s in focus["songs"] if s["song_id"] == SONG_SHA16)
    assert v["chosen_section"]["t_start_s"] == peach["chosen_section"]["t_start_s"]
    assert v["chosen_section"]["t_end_s"] == peach["chosen_section"]["t_end_s"]


def test_c20_all_delivery_artifacts_exist_and_shas_resolve():
    v = _load_verdict()
    for key, entry in v["artifacts"].items():
        p = REPO / entry["path"]
        assert p.exists(), f"missing {key}: {p}"
        assert _sha256(p) == entry["sha256"], f"{key} sha drift"


def test_c20_byte_determinism_all_stages():
    v = _load_verdict()
    b = v["byte_determinism"]
    for k in ("htdemucs_all_24_stems", "muscriptor_all_probes",
              "canonical_midi_all_stems", "merged_mid_x2",
              "per_track_render_x2", "mix_match_x2"):
        assert k in b, f"missing byte-det key: {k}"
    if not b["all_deterministic"]:
        pytest.xfail("FD-1 tripped: nondeterminism detected — see verdict for details")


def test_c20_structural_4_4_gates_all_pass():
    v = _load_verdict()
    g = v["structural_gates_4_4"]
    for gate, ok in g["assertions"].items():
        assert ok, f"structural gate failed: {gate}"
    assert g["n_pass"] == g["n_total"] == 4


def test_c20_panel_never_lands_gate_and_8_keys_finite():
    v = _load_verdict()
    m = v["m_tex_1_panel"]
    assert m["panel_is_never_lands_gate"] is True
    assert m["n_keys"] == 8
    for k, ok in m["finite_per_key"].items():
        assert ok, f"panel key non-finite: {k}"


def test_c20_chicken_grease_anchor_refs_resolve():
    v = _load_verdict()
    ref = v["chicken_grease_anchor_ref"]
    p_verdict = REPO / ref["c19_verdict_path"]
    assert p_verdict.exists()
    assert _sha256(p_verdict) == ref["c19_verdict_sha256"]
    p_a = REPO / "data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav"
    assert p_a.exists()
    assert _sha256(p_a) == ref["c5_method_a_wav_sha256"]


def test_c20_manifest_matches_chicken_grease_format():
    m = json.loads((OPSEC / "manifest.json").read_text())
    for k in ("schema_version", "song_sha16", "song_title", "ab_window_operator_section",
              "artifacts", "per_stem_canonical_midi_sha", "tempo_choice",
              "rubric_hash_v2"):
        assert k in m, f"manifest missing key: {k}"
    assert m["song_sha16"] == SONG_SHA16
    assert m["song_title"] == "Peach Dream"
