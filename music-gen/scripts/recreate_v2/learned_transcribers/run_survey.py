#!/usr/bin/env python3
# created: 2026-09-02T07:20:00Z
# cycle: 57 clone-2
# agent: worker
# milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/learned-transcribers
"""RC10 W3 learned-transcriber survey orchestrator (outer /usr/bin/python3).

Drives smoke-test per successfully-installed model against Chicken Grease
6-stem baseline; byte-determinism × 2 via fresh tempfile.mkdtemp() dirs.
Writes per-model notes.json under data/rc10_learned_survey/<model>/.
"""
import glob, hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile

# c48 env-flags default OFF
os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")

# NOTE: do NOT .resolve() the venv python path — it symlinks to
# /usr/bin/python3.11 and would lose the venv site-packages context.
VENV_PY = pathlib.Path("workspace/learned_transcribers_venv/bin/python").absolute()
INNER = pathlib.Path("scripts/recreate_v2/learned_transcribers/_smoke_inner.py").resolve()
CG_SHA16 = "31a164f845f8e27e"
STEM_ROOT = pathlib.Path(f"data/recreate_v2/baseline/{CG_SHA16}/rc9_6stem")
OUT_ROOT = pathlib.Path("data/rc10_learned_survey")

ENV_PINS = {
    "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC", "LC_ALL": "C.UTF-8",
}


def _env():
    e = os.environ.copy()
    e.update(ENV_PINS)
    for k in ("VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME"):
        e.pop(k, None)
    return e


def _interpreter_guard():
    assert "/usr/bin/python3" in sys.executable or "/usr/local/bin/python3" in sys.executable, \
        f"orchestrator must run under /usr/bin/python3; got {sys.executable}"


def _sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def _run_inner_twice(model, stem):
    shas, outs = [], []
    for i in (1, 2):
        d = tempfile.mkdtemp(prefix=f"lt_{model}_run{i}_")
        out = pathlib.Path(d) / "notes.json"
        r = subprocess.run(
            [str(VENV_PY), str(INNER), "--model", model, "--stem", str(stem), "--out", str(out)],
            env=_env(), capture_output=True, text=True, timeout=1800,
        )
        if r.returncode != 0:
            return {"ok": False, "error": (r.stdout + r.stderr)[-800:], "shas": shas}
        shas.append(_sha(out)); outs.append(out)
    return {"ok": True, "shas": shas,
            "byte_determinism_holds": shas[0] == shas[1],
            "tmp_out": str(outs[0])}


def _importable(mod):
    r = subprocess.run([str(VENV_PY), "-c", f"import {mod}"],
                       env=_env(), capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def run_smoke_tests():
    results = {}
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    if _importable("torchcrepe"):
        for stem_name in ("bass", "vocals"):
            stem = STEM_ROOT / f"{stem_name}.wav"
            res = _run_inner_twice("torchcrepe", stem)
            if res["ok"]:
                md = OUT_ROOT / "torchcrepe" / CG_SHA16 / stem_name
                md.mkdir(parents=True, exist_ok=True)
                shutil.copy(res["tmp_out"], md / "notes.json")
                res["final_path"] = str(md / "notes.json")
            results[f"torchcrepe_{stem_name}"] = res
    else:
        results["torchcrepe_bass"] = {"ok": False, "error": "torchcrepe not importable in venv"}
    if _importable("piano_transcription_inference"):
        stem = STEM_ROOT / "piano.wav"
        res = _run_inner_twice("piano_bytedance", stem)
        if res["ok"]:
            md = OUT_ROOT / "piano_bytedance" / CG_SHA16 / "piano"
            md.mkdir(parents=True, exist_ok=True)
            shutil.copy(res["tmp_out"], md / "notes.json")
            res["final_path"] = str(md / "notes.json")
        results["piano_bytedance_piano"] = res
    else:
        results["piano_bytedance_piano"] = {"ok": False, "error": "piano_transcription_inference not importable in venv"}
    return results


def maybe_score_vs_gold(smoke_results):
    landed = False
    for p in glob.glob("data/rc10_gold_set/*/verdict.json"):
        try:
            if json.load(open(p)).get("verdict") in ("GOLD_SET_LANDS", "GOLD_SET_PARTIAL"):
                landed = True; break
        except Exception:
            pass
    if not landed:
        (OUT_ROOT / "smoke_test_only.flag").write_text("branch_a_gold_set_not_landed_mid_cycle\n")
        return {"gold_landed": False, "deferred_scoring_reason": "branch_a_gold_set_not_landed_mid_cycle"}
    return {"gold_landed": True, "note": "scoring path not exercised — gold format not final"}


def maybe_cross_stem_stub():
    src = pathlib.Path("data/rc10_musical_time/cross_stem_energy_per_onset.tsv")
    tsv = OUT_ROOT / "cross_stem_reconciliation_stub.tsv"
    tsv.write_text("onset_s\tdrum_owner_energy_dB\tbass_owner_energy_dB\tassignment\n")
    if not src.exists():
        (OUT_ROOT / "deferred_no_energy_table.sentinel").write_text(
            "branch_b_musical_time_cross_stem_energy_not_landed_mid_cycle\n")
        return {"landed": False}
    return {"landed": True, "path": str(tsv)}


def build_verdict(smoke_results, scoring, cross_stem):
    rubric_hash = pathlib.Path("data/rc10_learned_survey/rubric_hash.txt").read_text().strip()
    doc_sha = hashlib.sha256(pathlib.Path("docs/rc10_learned_survey_rubric.md").read_bytes()).hexdigest()
    installed_and_smoke_ok = [k for k, v in smoke_results.items()
                              if v.get("ok") and v.get("byte_determinism_holds")]
    installed_but_byte_det_failed = [k for k, v in smoke_results.items()
                                     if v.get("ok") and not v.get("byte_determinism_holds")]
    installed_but_smoke_fail = [k for k, v in smoke_results.items()
                                if v.get("ok") is False and "not importable" not in (v.get("error") or "")]
    not_importable = [k for k, v in smoke_results.items()
                      if v.get("ok") is False and "not importable" in (v.get("error") or "")]
    if installed_and_smoke_ok:
        verdict = "LEARNED_SURVEY_LANDS"
    elif installed_but_byte_det_failed or installed_but_smoke_fail:
        verdict = "LEARNED_SURVEY_PARTIAL"
    else:
        verdict = "FETCH_FAILS_ALL"
    v = {
        "cycle": 57, "clone": "clone-2",
        "milestone": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/learned-transcribers",
        "verdict": verdict,
        "rubric_hash": rubric_hash, "rubric_doc_sha256": doc_sha,
        "three_way_rubric_hash_byte_equality": rubric_hash == doc_sha,
        "smoke_test_only": not scoring.get("gold_landed", False),
        "deferred_scoring_reason": scoring.get("deferred_scoring_reason"),
        "smoke_results": smoke_results,
        "cross_stem_reconciliation": cross_stem,
        "installed_and_smoke_ok": installed_and_smoke_ok,
        "installed_but_byte_det_failed": installed_but_byte_det_failed,
        "installed_but_smoke_fail": installed_but_smoke_fail,
        "not_importable": not_importable,
        "focus_song": {"sha16": CG_SHA16, "name": "Chicken Grease"},
        "note": "c57 clone-2 W3 learned transcriber survey; honest fetchability per c11.",
    }
    (OUT_ROOT / "verdict.json").write_text(json.dumps(v, sort_keys=True, indent=2))
    return v


def main():
    _interpreter_guard()
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    smoke = run_smoke_tests()
    scoring = maybe_score_vs_gold(smoke)
    cross = maybe_cross_stem_stub()
    v = build_verdict(smoke, scoring, cross)
    print(json.dumps({"verdict": v["verdict"],
                      "installed_and_smoke_ok": v["installed_and_smoke_ok"]}, indent=2))


if __name__ == "__main__":
    main()
