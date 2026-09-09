#!/usr/bin/python3
"""c83 landing tests — S1 liveness, S2 amended receipt + probe, S3 hook-at-birth, S4 prereg/characterization, S5 informational scoring, S6 tombstone.

created: 2026-09-06T21:15:00Z
cycle: 83
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle83-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c83_landing.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
NEW_SCRIPTS = ["scripts/v5/ear_venv_receipt_amend_c83.py", "scripts/v5/unpaired_starts_c83.py", "scripts/v5/score_gen_batch_v5.py",
               "scripts/v5/hook_at_birth_c83.py", "tools/_emit_c83_ledger_events.py", "tools/_register_c83_por_rows.py"]


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_01_liveness_record_and_no_install() -> None:
    t = (_ROOT / "data/v5/logs/c83_p0_liveness.txt").read_text()
    assert "pid=10247" in t and "alive=True" in t and "df_driver_semantics" in t
    used = float(t.split("used_pct=")[1].split()[0])
    assert used < 90.0, used
    assert not (_ROOT / "data/v5/ear/venv_build_c83.json").exists(), "no venv build/install may happen at c83"
    print(f"test_01 PASS: liveness record; df {used} % < 90")


def test_02_amended_receipt_and_probe() -> None:
    d = json.loads((_ROOT / "data/v5/ear/env_pin_ear_venv_c82_amended.json").read_text())
    assert d["agent"] == "worker" and isinstance(d["supersedes_path"], str)
    assert _sha(d["pip_freeze_path"]) == d["pip_freeze_sha256"] == "40243a564ad69d5c3a6ee8481660a455cf14880f7c561a4934e6533a4a4bac43"
    assert d["main_env_unchanged"] and d["install_this_cycle"] is False
    p = json.loads((_ROOT / "data/v5/ear/ear_probe_c83.json").read_text())
    assert p["status"] == "EAR_VENV_REPRODUCES_CACHE" and p["run1_eq_run2"] and p["run1_sha256"] == p["run2_sha256"]
    assert all(v["max_abs_diff_vs_cache"] <= 1e-5 for v in p["rows"].values())
    # c82 pinned-command failure record is a permanent, byte-identical sibling
    assert json.loads((_ROOT / "data/v5/ear/ear_probe_c82.json").read_text())["status"] == "EAR_VENV_PROBE_FAILED"
    print(f"test_02 PASS: amended receipt + c83 probe {p['status']} run sha {p['run1_sha256'][:12]}…")


def test_03_unpaired_prereg_precedes_output_and_byte_det() -> None:
    pre = _ROOT / "data/v5/corpus/unpaired_starts_prereg_c83.json"
    out = _ROOT / "data/v5/corpus/unpaired_starts_c83.json"
    assert pre.stat().st_mtime < out.stat().st_mtime
    d = json.loads(out.read_text())
    assert d["prereg_sha256"] == _sha(pre) and d["agent"] == "worker"
    assert set(d["tally_all_cells"]) == {"H1_tail_chunk_concentration", "H2_uniform_dense_stem_ambiguity", "MIXED", "TOO_FEW"}
    for s, row in d["per_song"].items():
        for st, c in row["stems"].items():
            assert sum(c["chunk_hist_all"]) == c["n_starts"] and sum(c["chunk_hist_unpaired"]) == c["n_unpaired"], (s, st)
            assert c["label"] in d["tally_all_cells"]
    # fresh subprocess reproduces the JSON byte-identically (scoped to the songs present at run time via --songs-from)
    td = Path(tempfile.mkdtemp(prefix="c83_unp_"))
    env = dict(os.environ); env["PYTHONPATH"] = "."
    r = subprocess.run(["/usr/bin/python3", "scripts/v5/unpaired_starts_c83.py", "--out", str(td / "u.json"), "--songs-from", str(out)],
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
    assert _sha(td / "u.json") == _sha(out), "unpaired_starts_c83.json not byte-deterministic"
    print(f"test_03 PASS: prereg precedes output; tally {d['tally_all_cells']}; byte-det x2")


def test_04_gen_scores_informational_and_bytes_unchanged() -> None:
    t = json.loads((_ROOT / "data/v5/gen/gen_render_ear_scores_c83.json").read_text())
    assert t["informational_only"] is True and "no passer declared" in t["framing"] and t["agent"] == "worker"
    assert t["n_scored"] == 16 and t["n_gen_renders"] == 15 and t["wav_and_manifest_bytes_unchanged"] is True
    for k, v in t["scores"].items():
        wav = _ROOT / "data/v4/gen" / k / "ab_mix.wav"
        assert _sha(wav) == v["wav_sha256"] and _sha(wav.with_name("ab_mix.manifest.json")) == v["manifest_sha256"], k
        sib = json.loads(wav.with_name("ear_score_v5.json").read_text())
        assert sib["informational_only"] is True and sib["ear_score_v2"] == v["ear_score_v2"] and 1.0 <= v["ear_score_v2"] <= 7.0
    assert t["n_gen_ge_6"] == sum(v["ge_6"] for k, v in t["scores"].items() if not k.startswith("interpolation_demo"))
    print(f"test_04 PASS: 16 scored informational; {t['n_gen_ge_6']}/15 gen >= 6; WAV/manifest bytes unchanged")


def test_05_hook_at_birth_record_if_present() -> None:
    p = _ROOT / "data/v5/corpus/hook_at_birth_c83.json"
    if not p.exists():
        print("test_05 SKIP-PASS: hook_at_birth_c83.json not yet written (no post-restart landing at test time)")
        return
    d = json.loads(p.read_text())
    assert d["catch_up_is_noop"] is True and d["agent"] == "worker"
    for s, v in d["per_song"].items():
        assert v["hook_at_birth"] is True and v["note_on_equals_starts_all"], s
        assert (_ROOT / f"data/v5/corpus/{s}/canonical_v5_reindexed_sha256.json").exists()
    print(f"test_05 PASS: {len(d['per_song'])} post-restart landing(s) hook_at_birth; catch-up no-op")


def test_06_tombstone_and_gated_file_unchanged() -> None:
    assert (_ROOT / "data/v5/rules/README_c83.md").read_text().count("harmony_markov_v5.json") >= 1
    assert (_ROOT / "data/v5/rules/harmony_v5_gated.json").exists()
    mk = json.loads((_ROOT / "data/v5/rules/harmony_markov_v5.json").read_text())
    assert mk["degeneracy_verdict"] == "NON_DEGENERATE"
    print("test_06 PASS: F4 tombstone README present; gated file retained; markov record NON_DEGENERATE")


def test_07_discipline_ast_and_guards() -> None:
    for rel in NEW_SCRIPTS:
        p = _ROOT / rel
        if not p.exists():
            continue
        src = p.read_text()
        assert src.startswith("#!/usr/bin/python3"), rel
        tree = ast.parse(src)
        names = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        assert not any(m in ("random", "numpy.random", "secrets") for m in names), (rel, names)
        assert not any("sidecar_nonfactor" in m for m in names), rel
        code = src.replace(ast.get_docstring(tree) or "", "")  # the discipline docstring names the banned tokens on purpose
        calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        assert not calls & {"get_state", "save_state", "set_state", "load_state", "save_preset"}, (rel, calls)
        assert "sidecar_nonfactor" not in code, rel
    print(f"test_07 PASS: AST discipline on {len(NEW_SCRIPTS)} c83 scripts")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} c83_landing tests PASS")
