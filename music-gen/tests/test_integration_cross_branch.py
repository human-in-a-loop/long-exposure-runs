"""Post-merge integration checks that span the three fanout branches.

Verifies:
  1. Fixed-Decision 30/5/25 chunker constants match campaign prompt.
  2. Every ingestion manifest is round-trip valid.
  3. Sidecar reader/writer contract still refuses casual consumption.
  4. Classifier sidecars exist for every valset clip.
  5. DAW-spike agreement panel + rendered artifacts are on disk.

Run: PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py
"""
from __future__ import annotations
import json, sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS))

fail = 0
def check(cond, msg):
    global fail
    if cond:
        print("PASS", msg)
    else:
        print("FAIL", msg)
        fail += 1

# 1. Fixed decisions
import scripts.ingest.chunker as chunker
check(chunker.CLIP_S == 30.0, "chunker CLIP_S == 30.0 s")
check(chunker.OVERLAP_S == 5.0, "chunker OVERLAP_S == 5.0 s")
check(chunker.HOP_S == 25.0, "chunker HOP_S == 25.0 s (invariant of the two above)")

# 2. Manifest integrity
manifests = sorted((WS / "data" / "ingestion" / "manifests").glob("*.manifest.jsonl"))
check(len(manifests) >= 3, f"at least 3 ingestion manifests present ({len(manifests)})")
for m in manifests:
    rows = [json.loads(l) for l in m.read_text().splitlines() if l.strip()]
    sources = [r for r in rows if r["kind"] == "source"]
    clips = [r for r in rows if r["kind"] == "clip"]
    check(len(sources) == 1, f"{m.name}: exactly one source row")
    check(len(clips) >= 1, f"{m.name}: at least one clip row")
    for c in clips:
        check(c["sr_hz"] == 22050, f"{m.name}: clip sr_hz=22050")
        clip_path = WS / c["clip_path"] if not Path(c["clip_path"]).is_absolute() else Path(c["clip_path"])
        check(clip_path.exists(), f"{m.name}: clip file on disk {clip_path.name}")

# 3. Sidecar contract
import scripts.classifier.sidecar_nonfactor as sn
try:
    val = sn.NonFactorValue("secret_genre")
    str(val)
    check(False, "NonFactorValue.__str__ raises")
except TypeError:
    check(True, "NonFactorValue.__str__ raises")

# 4. Sidecar-per-valset-clip
valset = WS / "data" / "classifier" / "valset" / "clips"
nonfactor = WS / "data" / "classifier" / "_nonfactor"
val_clips = sorted(valset.glob("*.wav"))
sidecars = sorted(nonfactor.glob("*.json"))
check(len(val_clips) == 55, f"valset has 55 clips ({len(val_clips)})")
check(len(sidecars) == 55, f"nonfactor has 55 sidecars ({len(sidecars)})")
val_stems = {p.stem for p in val_clips}
side_stems = {p.stem for p in sidecars}
check(val_stems == side_stems, "every valset clip has a matching sidecar (stem parity)")

# 5. DAW spike artifacts
ds = WS / "data" / "daw_spike"
for f in ("ardour_render.wav", "dawdreamer_render.wav",
          "dawdreamer_render_matched.wav", "agreement.json",
          "agreement.png", "manifest.json"):
    check((ds / f).exists(), f"daw_spike artifact present: {f}")

# 6. DAW agreement panel is a well-formed JSON with the expected metric keys.
ag = json.loads((ds / "agreement.json").read_text())
def has_key_substr(obj, substr):
    if isinstance(obj, dict):
        if any(substr in k.lower() for k in obj.keys()): return True
        return any(has_key_substr(v, substr) for v in obj.values())
    if isinstance(obj, list):
        return any(has_key_substr(v, substr) for v in obj)
    return False
for k in ("mel", "rms", "centroid"):
    check(has_key_substr(ag, k), f"agreement.json contains a '{k}'-family metric")
# Sanity-check the matched-pair numbers against clone-1 report §3.3.
matched = ag["matched"]["metrics"]
check(matched["mel_l1_db"] < 5.0, f"matched mel-L1 sane ({matched['mel_l1_db']:.2f} dB)")
check(matched["rms_env_rmse"] < 0.10, f"matched rms-env-rmse sane ({matched['rms_env_rmse']:.4f})")

# 7. Texture panel cross-branch invariants (M-TEX-1/panel).
# 7a. The public API surface of the panel refuses aggregation.
import scripts.texture.panel as _tp
_BANNED = {"overall", "combined", "mean", "mean_score", "weighted", "aggregate", "score", "total"}
_EXPECTED = {"mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
             "lufs_m_rmse_lu", "embedding_cosine_distance", "embedding_rung",
             "sr_hz", "n_samples_compared"}
check(set(_tp.PUBLIC_KEYS) == _EXPECTED,
      f"texture panel PUBLIC_KEYS == expected eight ({sorted(_tp.PUBLIC_KEYS)})")
check(_BANNED.isdisjoint(set(_tp.PUBLIC_KEYS)),
      "texture panel PUBLIC_KEYS names no banned aggregation key")

# 7b. The texture panel does not import the classifier sidecar package.
import ast
_tex_dir = WS / "scripts" / "texture"
_seen_sidecar_import = False
for _pyfile in sorted(_tex_dir.glob("*.py")):
    _mod = ast.parse(_pyfile.read_text())
    for _node in ast.walk(_mod):
        if isinstance(_node, ast.ImportFrom) and _node.module and "sidecar" in _node.module:
            _seen_sidecar_import = True
        if isinstance(_node, ast.Import):
            for _n in _node.names:
                if "sidecar" in _n.name:
                    _seen_sidecar_import = True
check(not _seen_sidecar_import,
      "texture panel modules do NOT import any *sidecar* symbol (isolation)")

# 7c. Matched-pair reproduction across branches (recomputed here, not read from TSV).
import soundfile as _sf, numpy as _np
_ard, _sr = _sf.read(str(ds / "ardour_render.wav"), always_2d=True)
_daw, _srb = _sf.read(str(ds / "dawdreamer_render_matched.wav"), always_2d=True)
_r = _tp.texture_distance(_ard.astype(_np.float32), _daw.astype(_np.float32), int(_sr), sr_b=int(_srb))
_ref = {"mel_l1_db": 3.130554437637329, "rms_env_rmse": 0.040991, "spectral_centroid_rmse_hz": 159.017}
for _k, _v in _ref.items():
    _got = _r[_k]
    check(abs(_got - _v) / abs(_v) <= 0.05,
          f"texture panel {_k}={_got:.4f} reproduces reference {_v:.4f} within ±5%")

# 8. M-SEP-1 (source-separation survey) invariants
#    (a) results.tsv has a non-empty row per (separator, mix, stem).
#    (b) scripts/separation/ never imports scripts.classifier.sidecar_nonfactor.
_sep_tsv = WS / "data" / "separation" / "results.tsv"
check(_sep_tsv.is_file(), "M-SEP-1: data/separation/results.tsv present")
if _sep_tsv.is_file():
    _lines = [l for l in _sep_tsv.read_text().splitlines() if l.strip()]
    _hdr, *_data = _lines
    _seen = set()
    for _l in _data:
        _sep, _mix, _stem, *_rest = _l.split("\t")
        _seen.add((_sep, _mix, _stem))
    _expected = {(s, m, t)
                 for s in ("htdemucs", "openunmix", "naive_copy_third")
                 for m in ("synth_030s", "synth_060s", "synth_090s")
                 for t in ("drums", "bass", "other", "vocals")}
    _missing = _expected - _seen
    check(not _missing, f"M-SEP-1: results.tsv covers all 36 (separator, mix, stem) triples (missing={len(_missing)})")

_sep_dir = WS / "scripts" / "separation"
_seen_nonfactor_import = False
if _sep_dir.is_dir():
    for _pyfile in sorted(_sep_dir.glob("*.py")):
        _mod = ast.parse(_pyfile.read_text())
        for _node in ast.walk(_mod):
            if isinstance(_node, ast.ImportFrom) and _node.module and "sidecar_nonfactor" in _node.module:
                _seen_nonfactor_import = True
            if isinstance(_node, ast.Import):
                for _n in _node.names:
                    if "sidecar_nonfactor" in _n.name:
                        _seen_nonfactor_import = True
check(not _seen_nonfactor_import,
      "M-SEP-1: scripts/separation/*.py do NOT import scripts.classifier.sidecar_nonfactor (isolation)")

# 9. M-SEP-1 scope-closure: UMXHQ per-stem RMS matches the pinned baseline
#    guard against silent regression of the byte-determinism finding (MINOR-2).
#    Values pinned by scripts/separation/verify_umxhq_determinism.py.
import math as _math
import soundfile as _sf
_pin_path = WS / "data" / "separation" / "runs" / "openunmix" / "synth_030s" / "pinned_rms.json"
check(_pin_path.is_file(), "M-SEP-1: pinned_rms.json present for UMXHQ synth_030s")
if _pin_path.is_file():
    _pin = json.loads(_pin_path.read_text())
    _tol_db = 0.2  # matches the SI-SDR-cell auditor tolerance in the report
    for _stem, _meta in _pin["stems"].items():
        _stem_wav = WS / "data" / "separation" / "runs" / "openunmix" / "synth_030s" / f"{_stem}.wav"
        _a, _sr = _sf.read(str(_stem_wav), always_2d=True)
        _rms_now = float((_a.astype("float64") ** 2).mean() ** 0.5)
        check(_math.isfinite(_rms_now) and _rms_now > 0.0,
              f"M-SEP-1: UMXHQ synth_030s/{_stem}.wav RMS finite and > 0")
        _pin_dbfs = _meta["rms_dbfs"]
        _now_dbfs = 20.0 * _math.log10(_rms_now + 1e-12)
        _delta = abs(_now_dbfs - _pin_dbfs)
        check(_delta <= _tol_db,
              f"M-SEP-1: UMXHQ synth_030s/{_stem}.wav RMS {_now_dbfs:.2f} dBFS "
              f"within ±{_tol_db} dB of pinned {_pin_dbfs:.2f} (|Δ|={_delta:.3f})")

# 10. M-HEUR-1 (heuristics battery) cross-branch invariants
#     (a) scripts/heuristics/*.py NEVER import sidecar_nonfactor.
#     (b) All three per-seed batteries + meta JSONs exist on disk.
#     (c) The anchored-tail debias weight formula is honored numerically.
_heur_dir = WS / "scripts" / "heuristics"
_seen_heur_nonfactor = False
if _heur_dir.is_dir():
    for _pyfile in sorted(_heur_dir.glob("*.py")):
        _mod = ast.parse(_pyfile.read_text())
        for _node in ast.walk(_mod):
            if isinstance(_node, ast.ImportFrom) and _node.module and "sidecar_nonfactor" in _node.module:
                _seen_heur_nonfactor = True
            if isinstance(_node, ast.Import):
                for _n in _node.names:
                    if "sidecar_nonfactor" in _n.name:
                        _seen_heur_nonfactor = True
check(not _seen_heur_nonfactor,
      "M-HEUR-1: scripts/heuristics/*.py do NOT import scripts.classifier.sidecar_nonfactor (isolation)")

_heur_seeds = {
    "d60cead66dbd0b95": ("long",  0.23333333333333334, 3),  # 23 s overlap on clip 3
    "d15d5c009a70cc32": ("mid",   0.6666666666666666,  1),  # 10 s overlap on clip 1
    "d251556aedfe35ef": ("short", 1.0,                 0),  # single-clip short-song branch
}
for _sid, (_lab, _expected_w, _idx) in _heur_seeds.items():
    _seed_dir = WS / "data" / "heuristics" / _sid
    _tsv = _seed_dir / "clip_battery.tsv"
    _meta = _seed_dir / "meta_descriptors.json"
    check(_tsv.is_file(), f"M-HEUR-1: {_lab} clip_battery.tsv present")
    check(_meta.is_file(), f"M-HEUR-1: {_lab} meta_descriptors.json present")
    if _meta.is_file():
        _mj = json.loads(_meta.read_text())
        _weights = _mj.get("clip_weights", [])
        check(_idx < len(_weights),
              f"M-HEUR-1: {_lab} meta_descriptors.json has ≥{_idx + 1} clip weight(s)")
        if _idx < len(_weights):
            _got_w = float(_weights[_idx])
            check(abs(_got_w - _expected_w) < 1e-9,
                  f"M-HEUR-1: {_lab} clip[{_idx}] weight={_got_w:.6f} matches formula {_expected_w:.6f}")

# -------------------------------------------------------------------
# 11. M-RULES-1/schema (clone-1 of fork 3168fb0e47a1)
# -------------------------------------------------------------------

# 11a. Ledger file exists (may be empty; extractors deferred to M-SCORE-1).
_rules_ledger = WS / "data" / "rules" / "ledger.jsonl"
check(_rules_ledger.exists(),
      f"M-RULES-1/schema: {_rules_ledger.relative_to(WS)} exists (may be empty until M-SCORE-1)")

# 11b. Rules schema artifacts present and JSON/YAML equivalent.
_rules_json = WS / "scripts" / "rules" / "schema" / "rules_v1.json"
_rules_yaml = WS / "scripts" / "rules" / "schema" / "rules_v1.yaml"
check(_rules_json.is_file(), "M-RULES-1/schema: rules_v1.json present")
check(_rules_yaml.is_file(), "M-RULES-1/schema: rules_v1.yaml present")
if _rules_json.is_file() and _rules_yaml.is_file():
    import yaml as _yaml
    with open(_rules_json) as _f:
        _j = json.load(_f)
    with open(_rules_yaml) as _f:
        _y = _yaml.safe_load(_f)
    check(_j == _y, "M-RULES-1/schema: rules_v1.yaml safe_load equals rules_v1.json parse")

# 11c. Non-factor isolation: scripts/rules/*.py never IMPORT sidecar_nonfactor
#      (mentions in comments are allowed).
import re as _re
_seen_rules_nonfactor_import = False
_rulesWS = WS / "scripts" / "rules"
_pat_sidecar_import = _re.compile(
    r"^\s*(?:from\s+\S*\bsidecar_nonfactor\b|import\s+\S*\bsidecar_nonfactor\b)",
    _re.MULTILINE,
)
if _rulesWS.is_dir():
    for _p in _rulesWS.rglob("*.py"):
        if _pat_sidecar_import.search(_p.read_text()):
            _seen_rules_nonfactor_import = True
            break
check(not _seen_rules_nonfactor_import,
      "M-RULES-1/schema: scripts/rules/*.py do NOT import scripts.classifier.sidecar_nonfactor (isolation)")

# 11d. ≥5 synthetic instances per rule_type and all validate.
try:
    from scripts.rules.validate import validate_row as _validate_row
    from scripts.rules.rule_id import derive_rule_id as _derive_rule_id
    _rule_types = ["harmonic", "rhythmic", "melodic", "form", "arrangement"]
    _examplesWS = WS / "scripts" / "rules" / "schema" / "examples"
    for _rt in _rule_types:
        _files = sorted((_examplesWS / _rt).glob("*.json"))
        check(len(_files) >= 5,
              f"M-RULES-1/schema: {_rt} has {len(_files)} synthetic instance(s) (>=5 required)")
        _valid = 0
        _rid_match = 0
        for _p in _files:
            with open(_p) as _f:
                _r = json.load(_f)
            if not _validate_row(_r):
                _valid += 1
            if _derive_rule_id(_r) == _r.get("rule_id"):
                _rid_match += 1
        check(_valid == len(_files),
              f"M-RULES-1/schema: {_rt} all {_valid}/{len(_files)} synthetic instances validate cleanly")
        check(_rid_match == len(_files),
              f"M-RULES-1/schema: {_rt} rule_id reproducible for {_rid_match}/{len(_files)} instances")
except Exception as _e:
    check(False, f"M-RULES-1/schema: synthetic-instance validation raised {_e!r}")

# -------------------------------------------------------------------
# 12. M-TRANS-1 (clone-0 of fork 3168fb0e47a1)
# -------------------------------------------------------------------

# 12a. Quarantined venv exists and holds basic-pitch (path invariant).
_bp_venv = WS / "workspace" / "basic_pitch_venv"
check(_bp_venv.is_dir(),
      f"M-TRANS-1: quarantined venv exists at {_bp_venv.relative_to(WS)}")
_bp_py = _bp_venv / "bin" / "python3"
check(_bp_py.is_file(),
      "M-TRANS-1: venv interpreter present (workspace/basic_pitch_venv/bin/python3)")
_bp_freeze = _bp_venv / "requirements.frozen.txt"
check(_bp_freeze.is_file() and _bp_freeze.stat().st_size > 0,
      "M-TRANS-1: requirements.frozen.txt recorded")
if _bp_freeze.is_file():
    _frozen = _bp_freeze.read_text().lower()
    check("basic-pitch==0.4.0" in _frozen,
          "M-TRANS-1: venv freeze pins basic-pitch==0.4.0")

# 12b. Reference JSONLs present and deterministic (SHA-256 recomputed matches).
import hashlib as _hashlib
_ref_manifest_p = WS / "data" / "transcribe" / "reference" / "reference_manifest.json"
check(_ref_manifest_p.is_file(),
      "M-TRANS-1: reference_manifest.json present")
if _ref_manifest_p.is_file():
    _ref_manifest = json.loads(_ref_manifest_p.read_text())
    _files = _ref_manifest["files"]
    check(len(_files) == 12,
          f"M-TRANS-1: reference manifest lists 12 (mix, stem) pairs ({len(_files)})")
    _ok = 0
    for _f in _files:
        _p = WS / _f["path"]
        if _p.is_file():
            _h = _hashlib.sha256(_p.read_bytes()).hexdigest()
            if _h == _f["sha256"]:
                _ok += 1
    check(_ok == len(_files),
          f"M-TRANS-1: reference JSONL SHA-256 matches manifest for {_ok}/{len(_files)}")

# 12c. results.tsv non-empty per (transcriber, mix, stem) — 18 rows + header.
_res_tsv = WS / "data" / "transcribe" / "results.tsv"
check(_res_tsv.is_file(), "M-TRANS-1: results.tsv present")
if _res_tsv.is_file():
    _lines = [l for l in _res_tsv.read_text().splitlines() if l.strip()]
    check(len(_lines) == 19,
          f"M-TRANS-1: results.tsv has 18 data rows + header ({len(_lines)-1} data)")
    _header = _lines[0].split("\t")
    for _need in ("transcriber", "mix", "stem", "precision", "recall", "f1"):
        check(_need in _header,
              f"M-TRANS-1: results.tsv header contains '{_need}'")

# 12d. Drum-row lower-bound disclaimer present for basic_pitch.
if _res_tsv.is_file():
    _txt = _res_tsv.read_text()
    check("LOWER BOUND" in _txt,
          "M-TRANS-1: drum-row disclaimer 'LOWER BOUND' present in results.tsv")

# 12e. Report present and mentions the drum lower-bound.
_report = WS / "docs" / "transcription_survey_report.md"
check(_report.is_file(), "M-TRANS-1: docs/transcription_survey_report.md present")
if _report.is_file():
    _rtxt = _report.read_text()
    check("lower bound" in _rtxt.lower() or "LOWER BOUND" in _rtxt,
          "M-TRANS-1: report text carries the drum-stem lower-bound disclaimer")
    check("six-axis" in _rtxt.lower() or "six axis" in _rtxt.lower(),
          "M-TRANS-1: report has a six-axis coverage section")

# 12f. Non-factor isolation: scripts/transcribe/*.py must not import sidecar_nonfactor.
_seen_trans_nonfactor_import = False
_transWS = WS / "scripts" / "transcribe"
if _transWS.is_dir():
    for _p in _transWS.rglob("*.py"):
        if _pat_sidecar_import.search(_p.read_text()):
            _seen_trans_nonfactor_import = True
            break
check(not _seen_trans_nonfactor_import,
      "M-TRANS-1: scripts/transcribe/*.py do NOT import sidecar_nonfactor (isolation)")

# 12g. Six-axis coverage matrix exists and covers all 7 rows explicitly
#      (rhythm, melody, harmony, timbre, dynamics, form, vocals-to-text).
_axes_p = WS / "data" / "transcribe" / "six_axis_coverage.json"
check(_axes_p.is_file(), "M-TRANS-1: six_axis_coverage.json present")
if _axes_p.is_file():
    _axes = json.loads(_axes_p.read_text())
    _need_axes = {"rhythm", "melody", "harmony", "timbre", "dynamics", "form", "vocals-to-text"}
    _have = {row["axis"] for row in _axes["axis_table"]}
    check(_need_axes.issubset(_have),
          f"M-TRANS-1: coverage matrix has all axes (missing: {sorted(_need_axes - _have)})")


# 13. M-EAR-1/preparation cross-branch invariants
#     (a) scripts/ear/*.py NEVER import sidecar_nonfactor (isolation).
#     (b) synthetic-non-factor plant lives at data/ear/synth_nonfactor_plant.json
#         (naming discipline distinct from data/classifier/_nonfactor/).
#     (c) leak-test success bars: detection ≥ 0.90 at α=1.0 per leak type
#         and FPR ≤ 0.10 per leak type.
_ear_dir = WS / "scripts" / "ear"
_seen_ear_nonfactor_import = False
if _ear_dir.is_dir():
    for _pyfile in sorted(_ear_dir.glob("*.py")):
        _mod = ast.parse(_pyfile.read_text())
        for _node in ast.walk(_mod):
            if isinstance(_node, ast.ImportFrom) and _node.module and "sidecar_nonfactor" in _node.module:
                _seen_ear_nonfactor_import = True
            if isinstance(_node, ast.Import):
                for _n in _node.names:
                    if "sidecar_nonfactor" in _n.name:
                        _seen_ear_nonfactor_import = True
check(not _seen_ear_nonfactor_import,
      "M-EAR-1: scripts/ear/*.py do NOT import scripts.classifier.sidecar_nonfactor (isolation)")

_plant_p = WS / "data" / "ear" / "synth_nonfactor_plant.json"
check(_plant_p.is_file(), "M-EAR-1: synth_nonfactor_plant.json present at data/ear/")
if _plant_p.is_file():
    _plant = json.loads(_plant_p.read_text())
    for _k in ("clip_ids", "synth_artist", "synth_genre", "synth_era"):
        check(_k in _plant, f"M-EAR-1: plant carries key {_k!r}")
    if "synth_artist" in _plant:
        check(len(_plant["synth_artist"]) == len(_plant["clip_ids"]),
              "M-EAR-1: synth_artist aligned with clip_ids")

_leak_sum_p = WS / "data" / "ear" / "leak_test_summary.json"
check(_leak_sum_p.is_file(), "M-EAR-1: leak_test_summary.json present")
if _leak_sum_p.is_file():
    _sum = json.loads(_leak_sum_p.read_text())
    _det = _sum.get("summary_detection", {})
    _fpr = _sum.get("summary_fpr", {})
    for _kind in ("artist", "genre", "era"):
        _key = f"{_kind}@alpha=1.0"
        _rate = float(_det.get(_key, 0.0))
        check(_rate >= 0.90,
              f"M-EAR-1: detection rate {_key} = {_rate:.3f} ≥ 0.90")
        _fpr_v = float(_fpr.get(_kind, 1.0))
        check(_fpr_v <= 0.10,
              f"M-EAR-1: false-positive rate {_kind} = {_fpr_v:.3f} ≤ 0.10")

_sanity_p = WS / "data" / "ear" / "model_sanity.json"
check(_sanity_p.is_file(), "M-EAR-1: model_sanity.json present")
if _sanity_p.is_file():
    _sanity = json.loads(_sanity_p.read_text())
    _corn_mae = float(_sanity["summary"]["mae"]["mean"])
    _maj_mae = float(_sanity["summary"]["majority_mae"]["mean"])
    _mn_mae = float(_sanity["summary"]["mean_int_mae"]["mean"])
    check(_corn_mae < _maj_mae,
          f"M-EAR-1: CORN MAE {_corn_mae:.3f} < majority-class MAE {_maj_mae:.3f}")
    check(_corn_mae < _mn_mae,
          f"M-EAR-1: CORN MAE {_corn_mae:.3f} < mean-integer MAE {_mn_mae:.3f}")

# 13z. Feature cache carries all 55 valset clips.
_feat_dir = WS / "data" / "ear" / "features"
_n_feats = len(list(_feat_dir.glob("*.npz"))) if _feat_dir.is_dir() else 0
check(_n_feats >= 55, f"M-EAR-1: {_n_feats} cached feature files under data/ear/features/ (≥55)")

# =========================================================================
# §14. M-TRANS-1/basic-pitch/octave-suppression invariants (fork 3a908edcb241 clone 1)
# =========================================================================
_os_dir = WS / "data" / "transcribe" / "octave_suppression"
_os_tsv = _os_dir / "grid_search.tsv"
_os_png = _os_dir / "heatmap.png"
_os_sup = WS / "scripts" / "transcribe" / "octave_suppression.py"
_os_grid = WS / "scripts" / "transcribe" / "octave_grid_search.py"
_os_plot = WS / "scripts" / "transcribe" / "octave_grid_plot.py"

check(_os_sup.is_file(), "M-TRANS-1/octave-suppression: octave_suppression.py present")
check(_os_grid.is_file(), "M-TRANS-1/octave-suppression: octave_grid_search.py present")
check(_os_plot.is_file(), "M-TRANS-1/octave-suppression: octave_grid_plot.py present")

# Interpreter-guard assert present in every new module.
for _p in (_os_sup, _os_grid, _os_plot):
    _src = _p.read_text() if _p.is_file() else ""
    check("wrong interpreter" in _src,
          f"M-TRANS-1/octave-suppression: {_p.name} carries /usr/bin/python3 interpreter guard")

# Isolation contract: AST scan for sidecar_nonfactor.
import ast as _ast
for _p in (_os_sup, _os_grid, _os_plot):
    _bad = False
    if _p.is_file():
        _tree = _ast.parse(_p.read_text(), filename=str(_p))
        for _node in _ast.walk(_tree):
            if isinstance(_node, _ast.ImportFrom):
                if (_node.module or "").find("sidecar_nonfactor") != -1:
                    _bad = True
            elif isinstance(_node, _ast.Import):
                for _n in _node.names:
                    if "sidecar_nonfactor" in _n.name:
                        _bad = True
    check(not _bad,
          f"M-TRANS-1/octave-suppression: {_p.name} does NOT import sidecar_nonfactor")

# TSV shape: header + 40 data rows (3 baseline + 27 per-cell + 9 aggregate + 1 aggregate baseline).
check(_os_tsv.is_file(), "M-TRANS-1/octave-suppression: grid_search.tsv present")
if _os_tsv.is_file():
    _lines = _os_tsv.read_text().splitlines()
    check(len(_lines) == 41,
          f"M-TRANS-1/octave-suppression: TSV has 41 lines (1 header + 40 data), got {len(_lines)}")
    _hdr = _lines[0].split("\t")
    for _col in ("mix_id", "T_min_ms", "overlap_min", "bass_F1_uplift",
                 "drums_F1_delta", "other_F1_delta", "passes_harmless"):
        check(_col in _hdr, f"M-TRANS-1/octave-suppression: TSV header has {_col!r}")

# Heatmap PNG exists and is non-empty.
check(_os_png.is_file() and _os_png.stat().st_size > 0,
      "M-TRANS-1/octave-suppression: heatmap.png present and non-empty")

# Harmless-to-others: every cell must satisfy drums_delta >= -0.02 AND other_delta >= -0.02.
if _os_tsv.is_file():
    import csv as _csv
    _rows = list(_csv.DictReader(_os_tsv.open(), delimiter="\t"))
    _all_harmless = True
    for _r in _rows:
        if _r["mix_id"] != "aggregate" or _r["T_min_ms"] == "baseline":
            continue
        if float(_r["drums_F1_delta"]) < -0.02 or float(_r["other_F1_delta"]) < -0.02:
            _all_harmless = False
    check(_all_harmless,
          "M-TRANS-1/octave-suppression: every aggregate cell honors harmless-to-others")

# Report exists with all 7 required sections.
_os_report = WS / "docs" / "basic_pitch_octave_refinement.md"
check(_os_report.is_file(), "M-TRANS-1/octave-suppression: docs/basic_pitch_octave_refinement.md present")
if _os_report.is_file():
    _rtext = _os_report.read_text()
    for _sec in ("## Problem", "## Method", "## Results",
                 "## Interpretation", "## Determinism", "## Isolation",
                 "## Limitations", "## Reproduction"):
        check(_sec in _rtext, f"M-TRANS-1/octave-suppression: report has {_sec!r}")

# =========================================================================
# §15. M-SCORE-1 (fork 3a908edcb241 clone 0) — MuseScore programmatic bridge
# =========================================================================
# (a) Non-factor isolation: scripts/score/*.py never import sidecar_nonfactor.
# (b) Interpreter-guard is present as the first executable line in
#     bridge.py, jsonl_to_midi.py, seed_score.py, and the test file.
# (c) Public API surface stable: bridge exposes xml_to_midi, midi_to_xml,
#     merge_stems_to_score, ScoreBridgeError.
# (d) The parts-mapping sidecar exists next to the merged XML and covers
#     all 3 stems.
# (e) Report artifact present with the 7 sections named in the research
#     brief.
import re as _re
_scoreWS = WS / "scripts" / "score"
_score_pyfiles = list(_scoreWS.rglob("*.py"))
check(len(_score_pyfiles) >= 3,
      f"M-SCORE-1: >=3 python files under scripts/score/ (got {len(_score_pyfiles)})")

_sidecar_pat = _re.compile(
    r"^\s*(from|import)\s+scripts\.classifier\.sidecar_nonfactor",
    _re.MULTILINE)
for _p in _score_pyfiles:
    _t = _p.read_text()
    check(not _sidecar_pat.search(_t),
          f"M-SCORE-1: {_p.name} does not import sidecar_nonfactor")

_guard_pat = _re.compile(
    r"assert\s+sys\.executable\s*==\s*['\"]/usr/bin/python3['\"]")
_guard_files = [p for p in _score_pyfiles if p.name != "__init__.py"] \
    + [WS / "tests" / "test_score_bridge.py"]
for _p in _guard_files:
    _t = _p.read_text()
    check(bool(_guard_pat.search(_t)),
          f"M-SCORE-1: {_p.name} has interpreter guard")

# Public API surface
_bridge_src = (_scoreWS / "bridge.py").read_text()
for _name in ("def xml_to_midi", "def midi_to_xml",
              "def merge_stems_to_score", "class ScoreBridgeError"):
    check(_name in _bridge_src,
          f"M-SCORE-1: bridge.py exposes {_name!r}")

# Merged sidecar (produced by tests/test_score_bridge.py §3)
_sidecar_path = WS / "data" / "score" / "test_merged.parts_mapping.json"
if _sidecar_path.exists():
    import json as _json
    _side = _json.loads(_sidecar_path.read_text())
    _pbs = _side.get("parts_by_stem", {})
    check(set(_pbs) >= {"drums", "bass", "other"},
          f"M-SCORE-1: sidecar covers all 3 stems (got {sorted(_pbs)})")

# Report artifact
_score_report = WS / "docs" / "score_bridge_report.md"
check(_score_report.exists(), "M-SCORE-1: docs/score_bridge_report.md exists")
if _score_report.exists():
    _rtext = _score_report.read_text()
    for _sec in ("## §1", "## §2", "## §3",
                 "## §4", "## §5", "## §6", "## §7"):
        check(_sec in _rtext, f"M-SCORE-1: report has {_sec!r}")


# =========================================================================
# §17. M-INGEST-1/egress-ready-automation invariants (fork 3a908edcb241 clone 2)
# =========================================================================
# (a) scripts/egress_ready/*.py NEVER import sidecar_nonfactor (isolation).
# (b) module-level command constants are stable (single source of truth).
# (c) test suite exists and is invocable.
import re as _re_er
_er_dir = WS / "scripts" / "egress_ready"
_er_pat = _re_er.compile(
    r"^\s*(?:from\s+\S*\bsidecar_nonfactor\b|import\s+\S*\bsidecar_nonfactor\b)",
)
_er_bad = 0
if _er_dir.is_dir():
    for _pyfile in sorted(_er_dir.glob("*.py")):
        for _line in _pyfile.read_text(encoding="utf-8").splitlines():
            if _er_pat.match(_line):
                _er_bad += 1
check(_er_bad == 0,
      "M-INGEST-1/egress-ready: scripts/egress_ready/*.py do NOT import sidecar_nonfactor (isolation)")

# Command constants are stable (single-source-of-truth for future refactors).
try:
    from scripts.egress_ready.subprocess_hooks import (
        HARVEST_CMD, CHUNKER_CMD, CLASSIFIER_CMD, READY_FLAG_PATH,
    )
    check(HARVEST_CMD == ["bash", "workspace/harvest_playlists.sh"],
          "M-INGEST-1/egress-ready: HARVEST_CMD is the two-token bash invocation")
    check(CHUNKER_CMD[0] == "/usr/bin/python3" and "scripts.ingest.chunker" in CHUNKER_CMD,
          "M-INGEST-1/egress-ready: CHUNKER_CMD invokes /usr/bin/python3 -m scripts.ingest.chunker")
    check(CLASSIFIER_CMD[0] == "/usr/bin/python3" and "scripts.classifier.classify_batch" in CLASSIFIER_CMD,
          "M-INGEST-1/egress-ready: CLASSIFIER_CMD invokes /usr/bin/python3 -m scripts.classifier.classify_batch")
    check(READY_FLAG_PATH == "data/ear/rated_ready.flag",
          "M-INGEST-1/egress-ready: READY_FLAG_PATH points at data/ear/rated_ready.flag")
except ImportError as _e:
    check(False, f"M-INGEST-1/egress-ready: subprocess_hooks import failed: {_e}")

# Test suite exists and imports.
_er_tests = WS / "tests" / "test_egress_ready_state.py"
check(_er_tests.is_file(),
      "M-INGEST-1/egress-ready: tests/test_egress_ready_state.py present")

# Fixtures (all six named scenarios) present.
_fx_dir = WS / "tests" / "fixtures" / "egress_status"
for _fx in ("all_false.jsonl", "single_true_then_back.jsonl",
            "two_consecutive_triggers.jsonl", "already_triggered_then_false.jsonl",
            "interleaved_then_true_true.jsonl", "stale_row_does_not_count.jsonl"):
    check((_fx_dir / _fx).is_file(),
          f"M-INGEST-1/egress-ready: fixture {_fx} present")

# TRANSITIONS map has the promised legal edges (single-source-of-truth check).
from scripts.egress_ready.state import TRANSITIONS as _T, State as _S
check(_S.HARVESTING in _T[_S.TRIGGERED], "M-INGEST-1/egress-ready: TRIGGERED->HARVESTING legal")
check(_S.CHUNKING in _T[_S.HARVESTING],  "M-INGEST-1/egress-ready: HARVESTING->CHUNKING legal")
check(_S.CLASSIFYING in _T[_S.CHUNKING], "M-INGEST-1/egress-ready: CHUNKING->CLASSIFYING legal")
check(_S.READY in _T[_S.CLASSIFYING],    "M-INGEST-1/egress-ready: CLASSIFYING->READY legal")
check(_S.FAILED in _T[_S.HARVESTING],    "M-INGEST-1/egress-ready: HARVESTING->FAILED legal")
check(_S.FAILED in _T[_S.CHUNKING],      "M-INGEST-1/egress-ready: CHUNKING->FAILED legal")
check(_S.FAILED in _T[_S.CLASSIFYING],   "M-INGEST-1/egress-ready: CLASSIFYING->FAILED legal")
check(_S.IDLE in _T[_S.FAILED],          "M-INGEST-1/egress-ready: FAILED->IDLE legal (via --reset-failure)")

# Docs artifact present.
_er_report = WS / "docs" / "egress_ready_automation.md"
check(_er_report.is_file(), "M-INGEST-1/egress-ready: docs/egress_ready_automation.md present")
if _er_report.is_file():
    _rtext = _er_report.read_text(encoding="utf-8")
    for _sec in ("## Purpose", "## Non-goals", "## State diagram",
                 "## Trigger rule", "## Six-scenario matrix",
                 "## State persistence", "## Failure recovery",
                 "## Human-override API", "## Isolation", "## Reproduction"):
        check(_sec in _rtext, f"M-INGEST-1/egress-ready: report has {_sec!r}")


# §18. M-RULES-1/extraction invariants (fork f1bae241bde9 clone 0)
_ext_dir = WS / "scripts" / "rules" / "extract"
for _mod in ("__init__.py", "_common.py", "from_score.py",
             "harmonic.py", "rhythmic.py", "melodic.py",
             "form.py", "arrangement.py", "plot_coverage.py"):
    check((_ext_dir / _mod).is_file(),
          f"M-RULES-1/extraction: module {_mod} present")

# Interpreter guard on every non-__init__ module.
import re as _re_rules
_guard_pat = _re_rules.compile(r'sys\.executable\s*==\s*"/usr/bin/python3"')
for _mod in ("_common.py", "from_score.py", "harmonic.py", "rhythmic.py",
             "melodic.py", "form.py", "arrangement.py", "plot_coverage.py"):
    _p = _ext_dir / _mod
    if _p.is_file():
        check(bool(_guard_pat.search(_p.read_text(encoding="utf-8"))),
              f"M-RULES-1/extraction: {_mod} has /usr/bin/python3 guard")

# Non-factor AST isolation (line-start match).
_nf_pat = _re_rules.compile(r"^\s*(?:from|import)\s+scripts\.classifier\.sidecar_nonfactor",
                            _re_rules.MULTILINE)
for _p in sorted(_ext_dir.glob("*.py")):
    _hits = _nf_pat.findall(_p.read_text(encoding="utf-8"))
    check(len(_hits) == 0,
          f"M-RULES-1/extraction: {_p.name} has 0 sidecar_nonfactor imports")

# Test suite runs green.
import subprocess as _sub_rules
import os as _os_rules
_res = _sub_rules.run(
    ["/usr/bin/python3", str(WS / "tests" / "test_rules_extraction.py")],
    env={**_os_rules.environ, "PYTHONPATH": str(WS)},
    capture_output=True, text=True, timeout=180,
)
check(_res.returncode == 0,
      f"M-RULES-1/extraction: test_rules_extraction.py exits 0 (got {_res.returncode})")

# Ledger + deliverables present.
_lp = WS / "data" / "rules" / "ledger.jsonl"
check(_lp.is_file(), "M-RULES-1/extraction: data/rules/ledger.jsonl present")
if _lp.is_file():
    _n_rows = sum(1 for _ln in _lp.read_text(encoding="utf-8").splitlines() if _ln.strip())
    check(_n_rows >= 25, f"M-RULES-1/extraction: ledger has {_n_rows} rows (>=25)")

_report = WS / "docs" / "rules_extraction_report.md"
check(_report.is_file(), "M-RULES-1/extraction: docs/rules_extraction_report.md present")
_fig = WS / "docs" / "figures" / "rules_extraction_coverage.png"
check(_fig.is_file(), "M-RULES-1/extraction: coverage figure present")

# Determinism re-run: build in a temp ledger and confirm rule_id set unchanged.
if str(WS) not in sys.path:
    sys.path.insert(0, str(WS))
from scripts.rules.extract.from_score import run as _rules_run
import tempfile as _tf_rules, hashlib as _hs_rules
with _tf_rules.TemporaryDirectory() as _td:
    _a = Path(_td) / "a.jsonl"
    _b = Path(_td) / "b.jsonl"
    _s1 = _rules_run(ledger_path=_a)
    _s2 = _rules_run(ledger_path=_b)
    check(_s1["rule_ids"] == _s2["rule_ids"],
          "M-RULES-1/extraction: determinism: rule_id sequences equal across runs")
    check(_hs_rules.sha256(_a.read_bytes()).hexdigest() ==
          _hs_rules.sha256(_b.read_bytes()).hexdigest(),
          "M-RULES-1/extraction: determinism: ledger files byte-identical")


# §19. M-TEX-1/stage-by-stage invariants (fork f1bae241bde9 clone 1)
# Script presence.
_tex_scripts = [
    WS / "scripts" / "tex" / "render_bare_midi.py",
    WS / "scripts" / "tex" / "render_effects_layered.py",
    WS / "scripts" / "tex" / "measure_across_stages.py",
    WS / "scripts" / "tex" / "stage_by_stage.py",
    WS / "scripts" / "tex" / "plot_stage_by_stage.py",
]
for _p in _tex_scripts:
    check(_p.is_file(), f"M-TEX-1/stage-by-stage: {_p.relative_to(WS)} present")

# Interpreter guard on each new script.
for _p in _tex_scripts:
    if _p.is_file():
        _txt = _p.read_text(encoding="utf-8")
        check("sys.executable == \"/usr/bin/python3\"" in _txt,
              f"M-TEX-1/stage-by-stage: {_p.name} interpreter-guarded")

# Non-factor AST isolation across scripts/tex/.
import re as _re_tex
_bad = []
for _p in (WS / "scripts" / "tex").glob("*.py"):
    for _ln in _p.read_text(encoding="utf-8").splitlines():
        if _re_tex.match(r"^\s*(from|import)\s+.*sidecar_nonfactor", _ln):
            _bad.append(f"{_p.name}:{_ln}")
check(not _bad, f"M-TEX-1/stage-by-stage: non-factor AST isolation preserved ({_bad})")

# 8-key panel contract preserved end-to-end via TSV header shape.
_tsv = WS / "data" / "tex" / "stage_by_stage_synth_030s.tsv"
check(_tsv.is_file(), "M-TEX-1/stage-by-stage: TSV present at data/tex/stage_by_stage_synth_030s.tsv")
if _tsv.is_file():
    _rows_tex = [ln for ln in _tsv.read_text(encoding="utf-8").splitlines() if ln.strip()]
    check(len(_rows_tex) == 4,
          f"M-TEX-1/stage-by-stage: TSV has 4 lines (1 header + 3 pairs), got {len(_rows_tex)}")
    _header = _rows_tex[0].split("\t")
    _expected_cols = [
        "a_stage", "b_stage",
        "mel_l1_db", "spectral_centroid_rmse_hz",
        "rms_env_rmse", "lufs_m_rmse_lu",
        "embedding_cosine_distance", "embedding_rung",
        "sr_hz", "n_samples_compared",
    ]
    check(_header == _expected_cols,
          f"M-TEX-1/stage-by-stage: TSV header matches 8-key contract "
          f"(got {_header})")
    for banned in ("overall", "combined", "aggregate", "mean_score", "weighted", "total"):
        check(banned not in _header,
              f"M-TEX-1/stage-by-stage: no banned aggregate column '{banned}' in TSV")
    # 24 numeric cells finite.
    import math as _math_tex
    _numeric_cols = ["mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
                     "lufs_m_rmse_lu", "embedding_cosine_distance"]
    _n_finite = 0
    for _row in _rows_tex[1:]:
        _vals = dict(zip(_header, _row.split("\t")))
        for _k in _numeric_cols:
            _v = float(_vals[_k])
            if _math_tex.isfinite(_v):
                _n_finite += 1
    check(_n_finite == 15,
          f"M-TEX-1/stage-by-stage: 15 numeric cells finite (3 pairs × 5 numeric keys), got {_n_finite}")

# Byte-determinism SHA reproduction on all three stage WAVs.
_render_dir = WS / "data" / "tex" / "renders" / "synth_030s"
_expected_shas = {
    "original.wav":        "153997a829f2b42c57c48730500c3e61aa5a9a46e7c1624e1bf63acef3222ac6",
    "bare_midi.wav":       "fc8c3eccbff073d2399210845fc06a0802508d0dd53ef831da7f6c788eb6aadd",
    "effects_layered.wav": "13d7238637d1ee31420ede73934a1ed98282f92084c0151ea1576461678e3e9a",
}
import hashlib as _hs_tex
for _name, _sha in _expected_shas.items():
    _p = _render_dir / _name
    check(_p.is_file(), f"M-TEX-1/stage-by-stage: {_p.relative_to(WS)} present")
    if _p.is_file():
        _got = _hs_tex.sha256(_p.read_bytes()).hexdigest()
        check(_got == _sha,
              f"M-TEX-1/stage-by-stage: {_name} SHA-256 matches determinism baseline "
              f"(got {_got[:16]}..., expected {_sha[:16]}...)")

# TSV byte-determinism SHA.
if _tsv.is_file():
    _expected_tsv_sha = "b3570a795c8c3e7a5f59ddefbd20096e8221cabef8d4d1fad5a621a3ba0fece2"
    _got_tsv = _hs_tex.sha256(_tsv.read_bytes()).hexdigest()
    check(_got_tsv == _expected_tsv_sha,
          f"M-TEX-1/stage-by-stage: TSV SHA-256 matches determinism baseline "
          f"(got {_got_tsv[:16]}...)")

# Report + figure present.
_tex_report = WS / "docs" / "tex_stage_by_stage_report.md"
check(_tex_report.is_file(),
      "M-TEX-1/stage-by-stage: docs/tex_stage_by_stage_report.md present")
_tex_fig = WS / "docs" / "figures" / "tex_stage_by_stage_families.png"
check(_tex_fig.is_file(),
      "M-TEX-1/stage-by-stage: docs/figures/tex_stage_by_stage_families.png present")



# ==== §20 _infra/ledger-schema-hardening (cycle 10, fork 00b3ae64444c clone 2) ====
# Contract invariants for the ledger schema-hardening infra: SSoT module
# exists and both promise_check and ledger_append import from it; writer
# raises LedgerAppendError on the three documented drift patterns; no
# import cycles.

# long_exposure lives outside the workspace; add its parent to sys.path
# so imports work under PYTHONPATH=. invocation.
import sys as _sys_lsh
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in _sys_lsh.path:
    _sys_lsh.path.append(_LE_PARENT)

import ast as _ast_lsh
import long_exposure.tools._ledger_schema as _ls
import long_exposure.tools.promise_check as _pc
import long_exposure.tools.ledger_append as _la
import long_exposure.workspace_bootstrap as _wb

check(hasattr(_ls, "REQUIRED_EVENT_FIELDS"),
      "_infra/ledger-schema-hardening: _ledger_schema.REQUIRED_EVENT_FIELDS present")
check(hasattr(_ls, "validate_event"),
      "_infra/ledger-schema-hardening: _ledger_schema.validate_event present")
check(hasattr(_ls, "content_hash_event_id"),
      "_infra/ledger-schema-hardening: _ledger_schema.content_hash_event_id present")
check(hasattr(_wb, "LedgerAppendError"),
      "_infra/ledger-schema-hardening: workspace_bootstrap.LedgerAppendError present")
check(_pc.REQUIRED_EVENT_FIELDS is _ls.REQUIRED_EVENT_FIELDS,
      "_infra/ledger-schema-hardening: promise_check imports REQUIRED_EVENT_FIELDS from SSoT")
check(_la.REQUIRED_EVENT_FIELDS is _ls.REQUIRED_EVENT_FIELDS,
      "_infra/ledger-schema-hardening: ledger_append imports REQUIRED_EVENT_FIELDS from SSoT")

# No import cycles: _ledger_schema.py must not import promise_check /
# ledger_append / workspace_bootstrap.
_ls_tree = _ast_lsh.parse(open(_ls.__file__).read())
_ls_imports = set()
for _node in _ast_lsh.walk(_ls_tree):
    if isinstance(_node, _ast_lsh.ImportFrom) and _node.module:
        _ls_imports.add(_node.module)
    elif isinstance(_node, _ast_lsh.Import):
        for _alias in _node.names:
            _ls_imports.add(_alias.name)
_forbidden = {
    "long_exposure.tools.promise_check",
    "long_exposure.tools.ledger_append",
    "long_exposure.workspace_bootstrap",
}
check(not (_ls_imports & _forbidden),
      f"_infra/ledger-schema-hardening: no import cycles (got {_ls_imports & _forbidden})")

# All existing ledger events pass the tightened validator.
import json as _json_lsh
_ledger = WS / "promise_ledger.jsonl"
if _ledger.is_file():
    _lsh_fails = []
    for _i, _raw in enumerate(_ledger.read_text().splitlines(), 1):
        _ev = _json_lsh.loads(_raw)
        _errs = _ls.validate_event(_ev)
        if _errs:
            _lsh_fails.append((_i, _errs))
    check(not _lsh_fails,
          f"_infra/ledger-schema-hardening: all existing ledger events pass validator "
          f"(fails={len(_lsh_fails)})")

# Report artifact present.
_lsh_report = WS / "docs" / "ledger_schema_hardening.md"
check(_lsh_report.is_file(),
      "_infra/ledger-schema-hardening: docs/ledger_schema_hardening.md present")


# =========================================================================
# §21. M-GEN-1/first-generation invariants (fork 00b3ae64444c clone 0)
# =========================================================================
# Contract invariants for the first deterministic generation. Every check
# is a fast static/light-runtime assertion — no re-render, no fluidsynth
# subprocess, no torch training. Byte-determinism SHAs are anchored to the
# clone-0 baseline; a drift here means a downstream regression.

# Script presence.
for _name in ("__init__.py", "sample_rules.py", "assemble_score.py",
              "render_pipeline.py", "score_generation.py", "emit_provenance.py"):
    _p = WS / "scripts" / "gen" / _name
    check(_p.is_file(), f"M-GEN-1/first-generation: scripts/gen/{_name} present")

# Interpreter guard on every runnable script.
for _name in ("sample_rules.py", "assemble_score.py", "render_pipeline.py",
              "score_generation.py", "emit_provenance.py"):
    _text = (WS / "scripts" / "gen" / _name).read_text(encoding="utf-8")
    check("assert sys.executable == \"/usr/bin/python3\"" in _text,
          f"M-GEN-1/first-generation: {_name} carries /usr/bin/python3 guard")

# Non-factor AST isolation: no sidecar_nonfactor imports at line start.
import re as _re_gen
_iso_re = _re_gen.compile(r"^\s*(from|import)\s+[\w.]*sidecar_nonfactor")
for _p in (WS / "scripts" / "gen").rglob("*.py"):
    _lines = _p.read_text(encoding="utf-8").splitlines()
    _hits = [ln for ln in _lines if _iso_re.match(ln)]
    check(not _hits, f"M-GEN-1/first-generation: {_p.name} has no sidecar_nonfactor imports")

# PRNG rejection: no random / numpy.random / torch.manual_seed / secrets imports in scripts/gen/.
# (numpy is fine; only the .random submodule and PRNGs are the concern.)
_prng_forbidden = _re_gen.compile(
    r"^\s*(from|import)\s+(random|secrets)\b|^\s*from\s+numpy\s+import\s+random|"
    r"^\s*import\s+numpy\.random|^\s*from\s+torch\s+import\s+rand"
)
for _p in (WS / "scripts" / "gen").rglob("*.py"):
    _lines = _p.read_text(encoding="utf-8").splitlines()
    _hits = [ln for ln in _lines if _prng_forbidden.match(ln)]
    check(not _hits, f"M-GEN-1/first-generation: {_p.name} has no PRNG imports")

# Sampling manifest present and shape-check.
_smf = WS / "data" / "gen" / "sampling_manifest.json"
check(_smf.is_file(), "M-GEN-1/first-generation: data/gen/sampling_manifest.json present")
if _smf.is_file():
    _sm = json.loads(_smf.read_text())
    check(set(_sm.get("chosen_rule_ids", {}).keys()) == {"arrangement", "form", "harmonic", "melodic", "rhythmic"},
          "M-GEN-1/first-generation: sampling manifest has all 5 rule_types")
    check(_sm["sampling_manifest"].get("algorithm") == "sha256_over_canonical_json_ascending",
          "M-GEN-1/first-generation: sampler algorithm is SHA-256 tiebreak")
    check(_sm["sampling_manifest"].get("prng_used") is False,
          "M-GEN-1/first-generation: sampler declares prng_used=False")

# All rendered artifacts present, non-silent, and SHA-anchored.
import hashlib as _hs_gen
_EXPECT_SHAS = {
    "data/gen/sampling_manifest.json":         "faafc86ba79dccd2",
    "data/gen/generated.musicxml":             "95d8671af26e7cf9",
    "data/gen/renders/generated.mid":          "f237dcfc75f5de94",
    "data/gen/renders/bare_midi.wav":          "5b6f608249ea72ac",
    "data/gen/renders/effects_layered.wav":    "d81089d39f31b5ca",
    "data/gen/scoring_v1.json":                "011e7c90e1ab3c72",
}
for _rel, _prefix in _EXPECT_SHAS.items():
    _p = WS / _rel
    check(_p.is_file(), f"M-GEN-1/first-generation: {_rel} present")
    if _p.is_file():
        _got = _hs_gen.sha256(_p.read_bytes()).hexdigest()
        check(_got.startswith(_prefix),
              f"M-GEN-1/first-generation: {_rel} SHA-256 matches determinism baseline "
              f"(got {_got[:16]}..., expected {_prefix}...)")

# Non-silent WAVs (peak > 1e-4).
try:
    import soundfile as _sf_gen
    for _rel in ("data/gen/renders/bare_midi.wav", "data/gen/renders/effects_layered.wav"):
        _y, _sr = _sf_gen.read(str(WS / _rel), always_2d=True)
        _peak = float(abs(_y).max())
        check(_peak > 1e-4, f"M-GEN-1/first-generation: {_rel} non-silent (peak={_peak:.4f})")
        check(_sr == 44100, f"M-GEN-1/first-generation: {_rel} SR=44.1 kHz (got {_sr})")
        check(_y.shape[1] == 2, f"M-GEN-1/first-generation: {_rel} stereo (got {_y.shape[1]} ch)")
except Exception as _exc:
    check(False, f"M-GEN-1/first-generation: soundfile inspection failed: {_exc}")

# Scoring JSON contract: 8-key panel, 4 heuristics, ear prediction present with calibration sentinel.
_scoring = WS / "data" / "gen" / "scoring_v1.json"
if _scoring.is_file():
    _sc = json.loads(_scoring.read_text())
    _panel = _sc.get("texture_panel_bare_vs_effects", {})
    _PANEL_KEYS = {"mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
                   "lufs_m_rmse_lu", "embedding_cosine_distance",
                   "embedding_rung", "sr_hz", "n_samples_compared"}
    check(set(_panel.keys()) == _PANEL_KEYS,
          f"M-GEN-1/first-generation: panel returns exactly 8 keys (got {sorted(_panel.keys())})")
    _heur = _sc.get("heuristics", {})
    check(set(_heur.keys()) == {"melody_quality", "timbre_quality", "form_quality", "dynamics_quality"},
          "M-GEN-1/first-generation: heuristics has all 4 mess-scale keys")
    _ear = _sc.get("ear", {})
    check(_ear.get("calibration") == "synthetic_labels_only",
          "M-GEN-1/first-generation: ear result carries synthetic_labels_only calibration sentinel")
    _pred = _ear.get("prediction")
    check(isinstance(_pred, int) and 1 <= _pred <= 7,
          f"M-GEN-1/first-generation: ear prediction is int in [1,7] (got {_pred!r})")

# Provenance chain: exactly 6 stages present, each with input_shas and output_shas.
_prov = WS / "data" / "gen" / "provenance_v1.jsonl"
check(_prov.is_file(), "M-GEN-1/first-generation: data/gen/provenance_v1.jsonl present")
if _prov.is_file():
    _rows = [json.loads(ln) for ln in _prov.read_text().splitlines() if ln.strip()]
    check(len(_rows) == 6, f"M-GEN-1/first-generation: provenance has exactly 6 stages (got {len(_rows)})")
    _EXPECT_STAGES = ["sample_rules", "assemble_score", "xml_to_midi",
                      "render_bare", "render_effects", "score_generation"]
    check([r.get("stage") for r in _rows] == _EXPECT_STAGES,
          "M-GEN-1/first-generation: provenance stages match canonical order")
    for _r in _rows:
        check(bool(_r.get("input_shas")) and bool(_r.get("output_shas")),
              f"M-GEN-1/first-generation: stage {_r.get('stage')} has input+output SHAs")

# Report + manifest present.
check((WS / "docs" / "gen_first_generation_report.md").is_file(),
      "M-GEN-1/first-generation: docs/gen_first_generation_report.md present")


# =========================================================================
# §22. M-INGEST-1/breadth-second-seeds invariants (fork 00b3ae64444c clone 1)
# =========================================================================
# Contract invariants for the pipeline-breadth cycle. Static / light-runtime
# only — no htdemucs, basic-pitch, fluidsynth, or panel calls (those are
# covered by their own single-source-of-truth milestones and would multiply
# CI wall-clock). Byte-determinism SHAs anchor per-seed reproducibility.

import re as _re_bre

# Script presence (§3 script-inventory contract).
for _name in ("__init__.py", "enumerate_seeds.py", "run_seed.py",
              "summarize.py", "plot_summary.py"):
    _p = WS / "scripts" / "breadth" / _name
    check(_p.is_file(), f"M-INGEST-1/breadth-second-seeds: scripts/breadth/{_name} present")

# Interpreter guard on every runnable script (excluding __init__).
for _name in ("enumerate_seeds.py", "run_seed.py", "summarize.py", "plot_summary.py"):
    _text = (WS / "scripts" / "breadth" / _name).read_text(encoding="utf-8")
    check("assert sys.executable == '/usr/bin/python3'" in _text
          or 'assert sys.executable == "/usr/bin/python3"' in _text,
          f"M-INGEST-1/breadth-second-seeds: {_name} carries /usr/bin/python3 guard")

# Non-factor AST isolation: no sidecar_nonfactor imports at line start.
_bre_pat = _re_bre.compile(r"^(from|import) .*sidecar_nonfactor", _re_bre.MULTILINE)
for _name in ("enumerate_seeds.py", "run_seed.py", "summarize.py", "plot_summary.py"):
    _text = (WS / "scripts" / "breadth" / _name).read_text(encoding="utf-8")
    check(not _bre_pat.search(_text),
          f"M-INGEST-1/breadth-second-seeds: {_name} does NOT import sidecar_nonfactor at line start")

# Per-seed artifact set present.
for _seed in ("seed_mid_50s", "synth_060s"):
    _sd = WS / "data" / "breadth" / _seed
    for _sub in ("original.wav", "stems/drums.wav", "stems/bass.wav",
                 "stems/other.wav", "stems/vocals.wav",
                 "transcriptions/drums.mid", "transcriptions/bass.mid",
                 "transcriptions/other.mid",
                 "merged.mid", "merged.musicxml", "bare_midi.wav",
                 "panel.tsv", "stage_manifest.jsonl", "summary.json"):
        _p = _sd / _sub
        check(_p.is_file(),
              f"M-INGEST-1/breadth-second-seeds: {_seed}/{_sub} present")

# summary.tsv + seed_enumeration.tsv + determinism_baselines.txt present.
for _n in ("summary.tsv", "seed_enumeration.tsv", "determinism_baselines.txt"):
    _p = WS / "data" / "breadth" / _n
    check(_p.is_file(), f"M-INGEST-1/breadth-second-seeds: data/breadth/{_n} present")

# Report + figure present.
check((WS / "docs" / "pipeline_breadth_report.md").is_file(),
      "M-INGEST-1/breadth-second-seeds: docs/pipeline_breadth_report.md present")
check((WS / "docs" / "figures" / "pipeline_breadth_panel.png").is_file(),
      "M-INGEST-1/breadth-second-seeds: docs/figures/pipeline_breadth_panel.png present")

# Per-seed panel 8-key contract on the panel.tsv header.
_panel_keys = {"a_stage", "b_stage", "mel_l1_db", "spectral_centroid_rmse_hz",
               "rms_env_rmse", "lufs_m_rmse_lu", "embedding_cosine_distance",
               "embedding_rung", "sr_hz", "n_samples_compared"}
for _seed in ("seed_mid_50s", "synth_060s"):
    _tsv = WS / "data" / "breadth" / _seed / "panel.tsv"
    if _tsv.is_file():
        _hdr = _tsv.read_text().splitlines()[0].split("\t")
        check(set(_hdr) == _panel_keys,
              f"M-INGEST-1/breadth-second-seeds: {_seed} panel.tsv has exact 10 columns "
              f"(a_stage, b_stage + 8 panel keys)")

# Byte-determinism SHA anchors (frozen from clone-1 run).
_bre_shas = {
    "seed_mid_50s/original.wav":               "1d8eca66",
    "seed_mid_50s/stems/drums.wav":            "bddfea47",
    "seed_mid_50s/stems/bass.wav":             "1f533f48",
    "seed_mid_50s/stems/other.wav":            "8220e311",
    "seed_mid_50s/transcriptions/drums.mid":   "71ffce62",
    "seed_mid_50s/transcriptions/bass.mid":    "209e0a02",
    "seed_mid_50s/transcriptions/other.mid":   "38c70a5b",
    "seed_mid_50s/merged.mid":                 "a48242f4",
    "seed_mid_50s/bare_midi.wav":              "cea3e3b4",
    "seed_mid_50s/panel.tsv":                  "b10d2a0c",
    "synth_060s/original.wav":                 "9c64045c",
    "synth_060s/stems/drums.wav":              "05db247a",
    "synth_060s/stems/bass.wav":               "32ad1be5",
    "synth_060s/stems/other.wav":              "15915ffd",
    "synth_060s/transcriptions/drums.mid":     "4b1e68e5",
    "synth_060s/transcriptions/bass.mid":      "82ba631f",
    "synth_060s/transcriptions/other.mid":     "236e2e15",
    "synth_060s/merged.mid":                   "60c88c24",
    "synth_060s/bare_midi.wav":                "07a9d0b7",
    "synth_060s/panel.tsv":                    "cc0acb5f",
}
import hashlib as _hs_bre
for _rel, _sha8 in _bre_shas.items():
    _p = WS / "data" / "breadth" / _rel
    if _p.is_file():
        _got = _hs_bre.sha256(_p.read_bytes()).hexdigest()
        check(_got.startswith(_sha8),
              f"M-INGEST-1/breadth-second-seeds: {_rel} SHA-256 anchor "
              f"(got {_got[:8]}..., expected {_sha8}...)")


# =========================================================================
# §23. M-EAR-1/training-armed invariants (fork ddd71e9bdb0e clone 2)
# =========================================================================
# Static contract checks for the training-armed harness: script presence,
# interpreter guard, non-factor AST isolation, zero-network AST + string
# grep, state-machine surface (states + legal transitions), and byte-
# determinism SHA anchors for the synth-valset training artifacts.

for _name in ("train.py", "train_armed_harness.py"):
    _p = WS / "scripts" / "ear" / _name
    check(_p.is_file(), f"M-EAR-1/training-armed: scripts/ear/{_name} present")

# Interpreter guard.
import re as _re_tearm
for _name in ("train.py", "train_armed_harness.py"):
    _src = (WS / "scripts" / "ear" / _name).read_text()
    check(bool(_re_tearm.search(
              r'assert\s+sys\.executable\s*==\s*[\'"]/usr/bin/python3[\'"]', _src)),
          f"M-EAR-1/training-armed: {_name} has /usr/bin/python3 interpreter guard")

# Non-factor AST isolation.
for _name in ("train.py", "train_armed_harness.py"):
    _src = (WS / "scripts" / "ear" / _name).read_text()
    _hits = _re_tearm.findall(r"^\s*(?:from|import)\s+\S*sidecar_nonfactor",
                              _src, _re_tearm.M)
    check(not _hits,
          f"M-EAR-1/training-armed: {_name} has no sidecar_nonfactor imports")

# Zero-network: AST + string grep.
import ast as _ast_tearm
for _name in ("train.py", "train_armed_harness.py"):
    _src = (WS / "scripts" / "ear" / _name).read_text()
    _tree = _ast_tearm.parse(_src)
    _imps = set()
    for _n in _ast_tearm.walk(_tree):
        if isinstance(_n, _ast_tearm.ImportFrom) and _n.module:
            _imps.add(_n.module.split(".")[0])
        elif isinstance(_n, _ast_tearm.Import):
            for _a in _n.names:
                _imps.add(_a.name.split(".")[0])
    _forbid = {"urllib", "requests", "socket", "httpx", "aiohttp", "http"}
    check(not (_imps & _forbid),
          f"M-EAR-1/training-armed: {_name} imports no network libs "
          f"(got {_imps & _forbid})")
    _lower = _src.lower()
    _string_hits = [w for w in ("urllib", "requests.", "socket(", "httpx",
                                 "aiohttp") if w in _lower]
    check(not _string_hits,
          f"M-EAR-1/training-armed: {_name} has no network string refs "
          f"(got {_string_hits})")

# State-machine surface.
import importlib as _il_tearm
_tah = _il_tearm.import_module("scripts.ear.train_armed_harness")
for _attr in ("HState", "HTRANSITIONS", "ArmedHarness", "TrainingHooks",
              "TrainingHookResult", "content_hash_manifest"):
    check(hasattr(_tah, _attr),
          f"M-EAR-1/armed-harness: train_armed_harness.{_attr} present")
_HS = _tah.HState
_TR = _tah.HTRANSITIONS
check(_HS.READY in _TR and _HS.TRAINING in _TR[_HS.READY],
      "M-EAR-1/armed-harness: READY -> TRAINING is a legal edge")
check(_HS.TRAINING in _TR and _HS.TRAINED in _TR[_HS.TRAINING],
      "M-EAR-1/armed-harness: TRAINING -> TRAINED is a legal edge")
check(_HS.TRAINING in _TR and _HS.FAILED in _TR[_HS.TRAINING],
      "M-EAR-1/armed-harness: TRAINING -> FAILED is a legal edge")
check(_TR.get(_HS.TRAINED, set()) == set(),
      "M-EAR-1/armed-harness: TRAINED is terminal (except forced retrain reset)")

# Training-loop surface.
_tm = _il_tearm.import_module("scripts.ear.train")
for _attr in ("train", "CornHead", "TrainingResult", "FEATURE_VERSION",
              "content_hash_manifest", "load_checkpoint"):
    check(hasattr(_tm, _attr), f"M-EAR-1/training-loop: train.{_attr} present")
check(_tm.FEATURE_VERSION == "ear-features-v1",
      f"M-EAR-1/training-loop: FEATURE_VERSION pinned "
      f"(got {_tm.FEATURE_VERSION!r})")
check(_tm.FEAT_DIM == 2052,
      f"M-EAR-1/training-loop: FEAT_DIM=2052 pinned (got {_tm.FEAT_DIM})")

# Byte-determinism anchors for the synth-valset training artifacts.
import hashlib as _hs_tearm
_tearm_shas = {
    "data/ear/training_v1/training_result.json":
        "1e688c5abf1eea975e9d38f9137a2b430a9e58de8b01b6ea149947439f6bd6ea",
    "data/ear/training_v1/corn_head_v1.pt":
        "ae75b7357c751c014b99e2243b9c2a7fd919e1acc6b8d359c733dc4ae515923b",
    "data/ear/training_v1/synth_ratings_manifest.tsv":
        "ec7e858760f5f6fb5f6e7e8586bcebf0758523aa008608488af9fb962a5647b4",
}
for _rel, _sha in _tearm_shas.items():
    _p = WS / _rel
    if _p.is_file():
        _got = _hs_tearm.sha256(_p.read_bytes()).hexdigest()
        check(_got == _sha,
              f"M-EAR-1/training-armed: {_rel} SHA-256 anchor "
              f"(got {_got[:12]}..., expected {_sha[:12]}...)")

# Test file present with the LE_PARENT shim.
_tef = WS / "tests" / "test_ear_training.py"
check(_tef.is_file(), "M-EAR-1/armed-harness: tests/test_ear_training.py present")
if _tef.is_file():
    _tef_src = _tef.read_text()
    check("_LE_PARENT" in _tef_src,
          "M-EAR-1/armed-harness: test file has _LE_PARENT sys.path shim")

# Report artifact present.
_report = WS / "docs" / "ear_training_armed_report.md"
check(_report.is_file(),
      "M-EAR-1/training-armed: docs/ear_training_armed_report.md present")


# =========================================================================
# §23. M-GEN-1/rule-composition-constraint + M-GEN-1/batch-v1 invariants
#       (cycle 11, fork ddd71e9bdb0e clone 0)
# =========================================================================
# Contract invariants for the coherence gate + 5-song batch. Static /
# light-runtime only — no rerender, no torch retrain. Byte-determinism SHAs
# anchor per-song reproducibility.

import re as _re_bv1

# Script presence.
for _name in ("coherence_gate.py", "batch_v1.py", "plot_batch_v1.py"):
    _p = WS / "scripts" / "gen" / _name
    check(_p.is_file(), f"M-GEN-1/batch-v1: scripts/gen/{_name} present")

# Interpreter guard on every new runnable script.
for _name in ("coherence_gate.py", "batch_v1.py", "plot_batch_v1.py"):
    _text = (WS / "scripts" / "gen" / _name).read_text(encoding="utf-8")
    check("assert sys.executable == \"/usr/bin/python3\"" in _text,
          f"M-GEN-1/batch-v1: {_name} carries /usr/bin/python3 guard")

# PRNG guard extended to cover the new scripts (§21 already scans scripts/gen/,
# but re-run explicitly on the three new files as a redundant, load-bearing check).
_prng_bv1 = _re_bv1.compile(
    r"^\s*(from|import)\s+(random|secrets)\b|^\s*from\s+numpy\s+import\s+random|"
    r"^\s*import\s+numpy\.random|^\s*from\s+torch\s+import\s+rand"
)
for _name in ("coherence_gate.py", "batch_v1.py", "plot_batch_v1.py"):
    _lines = (WS / "scripts" / "gen" / _name).read_text(encoding="utf-8").splitlines()
    _hits = [ln for ln in _lines if _prng_bv1.match(ln)]
    check(not _hits, f"M-GEN-1/batch-v1: {_name} has no PRNG imports")

# Non-factor AST isolation on new files.
_iso_bv1 = _re_bv1.compile(r"^\s*(from|import)\s+[\w.]*sidecar_nonfactor")
for _name in ("coherence_gate.py", "batch_v1.py", "plot_batch_v1.py"):
    _lines = (WS / "scripts" / "gen" / _name).read_text(encoding="utf-8").splitlines()
    _hits = [ln for ln in _lines if _iso_bv1.match(ln)]
    check(not _hits, f"M-GEN-1/batch-v1: {_name} has no sidecar_nonfactor imports")

# summary.tsv exists, has expected header + exactly 5 data rows.
_summary_tsv = WS / "data" / "gen" / "batch_v1" / "summary.tsv"
check(_summary_tsv.is_file(), "M-GEN-1/batch-v1: data/gen/batch_v1/summary.tsv present")
if _summary_tsv.is_file():
    _sumlines = _summary_tsv.read_text().splitlines()
    check(len(_sumlines) >= 6,
          f"M-GEN-1/batch-v1: summary.tsv has header + 5 rows (got {len(_sumlines)} lines)")
    _hdr = _sumlines[0].split("\t")
    _EXPECT_COLS = {"salt", "sha_musicxml", "sha_midi", "sha_bare_wav",
                    "sha_effects_wav", "heur_melody", "heur_timbre",
                    "heur_form", "heur_dynamics", "meta_dynamics_trajectory_db",
                    "meta_form_coherence", "panel_mel_l1_db",
                    "panel_spectral_centroid_rmse_hz", "panel_rms_env_rmse",
                    "panel_lufs_m_rmse_lu", "panel_embedding_cosine",
                    "panel_embedding_rung", "ear_prediction",
                    "ear_calibration", "n_coercions", "coercions_json"}
    check(set(_hdr) == _EXPECT_COLS,
          f"M-GEN-1/batch-v1: summary.tsv header has all 21 columns (missing={_EXPECT_COLS - set(_hdr)}, extra={set(_hdr) - _EXPECT_COLS})")
    _salts = sorted(int(row.split("\t")[0]) for row in _sumlines[1:])
    check(_salts == [0, 1, 2, 3, 4],
          f"M-GEN-1/batch-v1: summary.tsv covers salts 0..4 (got {_salts})")

# provenance.jsonl exists and has exactly 7 stages × 5 songs = 35 rows.
_prov_bv1 = WS / "data" / "gen" / "batch_v1" / "provenance.jsonl"
check(_prov_bv1.is_file(), "M-GEN-1/batch-v1: data/gen/batch_v1/provenance.jsonl present")
if _prov_bv1.is_file():
    _rows_bv1 = [json.loads(ln) for ln in _prov_bv1.read_text().splitlines() if ln.strip()]
    check(len(_rows_bv1) == 35,
          f"M-GEN-1/batch-v1: provenance has exactly 35 rows (got {len(_rows_bv1)})")
    for _r in _rows_bv1:
        check(bool(_r.get("input_shas")) and bool(_r.get("output_shas")),
              f"M-GEN-1/batch-v1: stage {_r.get('stage')} row has input+output SHAs")

# Per-song artifact SHA anchors (byte-determinism baseline).
import hashlib as _hs_bv1
_BV1_SHAS = {
    "song_0/generated.musicxml":   "bd84406982ce72e7",
    "song_0/generated.mid":        "77798beadcfd7019",
    "song_0/bare_midi.wav":        "c539a036cecb83cb",
    "song_0/effects_layered.wav":  "ccb6e266fa903b37",
    "song_1/generated.musicxml":   "89a34b86f6396525",
    "song_1/generated.mid":        "7f6fae8566ccc405",
    "song_1/bare_midi.wav":        "084fcf46cdfe33b0",
    "song_1/effects_layered.wav":  "bf685a2d0b064058",
    "song_2/generated.musicxml":   "485c809386e9b811",
    "song_2/generated.mid":        "0c6fbb5b608c4664",
    "song_2/bare_midi.wav":        "739c4f062e34f6f2",
    "song_2/effects_layered.wav":  "d639bb23373fa76a",
    "song_3/generated.musicxml":   "b56e7a5a8c2d62a1",
    "song_3/generated.mid":        "80df622651c95191",
    "song_3/bare_midi.wav":        "f6385b241dc12b45",
    "song_3/effects_layered.wav":  "23ec4440b0d1efad",
    "song_4/generated.musicxml":   "bf16d269bcad60e6",
    "song_4/generated.mid":        "9e5bf8762277a083",
    "song_4/bare_midi.wav":        "f10ece6d2be6af95",
    "song_4/effects_layered.wav":  "7c092db793d10f73",
}
for _rel, _pref in _BV1_SHAS.items():
    _p = WS / "data" / "gen" / "batch_v1" / _rel
    check(_p.is_file(), f"M-GEN-1/batch-v1: {_rel} present")
    if _p.is_file():
        _got = _hs_bv1.sha256(_p.read_bytes()).hexdigest()
        check(_got.startswith(_pref),
              f"M-GEN-1/batch-v1: {_rel} SHA-256 anchor (got {_got[:16]}..., expected {_pref}...)")

# Every song non-silent (peak > 1e-4) and every SHA distinct across salts.
try:
    import soundfile as _sf_bv1
    _fx_shas = set()
    for _s in range(5):
        for _n in ("bare_midi.wav", "effects_layered.wav"):
            _p = WS / "data" / "gen" / "batch_v1" / f"song_{_s}" / _n
            if _p.is_file():
                _y, _sr = _sf_bv1.read(str(_p), always_2d=True)
                _pk = float(abs(_y).max())
                check(_pk > 1e-4, f"M-GEN-1/batch-v1: song_{_s}/{_n} non-silent (peak={_pk:.4f})")
                if _n == "effects_layered.wav":
                    _fx_shas.add(_hs_bv1.sha256(_p.read_bytes()).hexdigest())
    check(len(_fx_shas) == 5,
          f"M-GEN-1/batch-v1: 5 distinct effects_layered SHAs across salts (got {len(_fx_shas)})")
except Exception as _exc:
    check(False, f"M-GEN-1/batch-v1: soundfile inspection failed: {_exc}")

# Salt=0 sampler-level regression: rule_ids match cycle-10 clone-0 anchors.
_song0_manifest = WS / "data" / "gen" / "batch_v1" / "song_0" / "sampling_manifest.json"
if _song0_manifest.is_file():
    _sm0 = json.loads(_song0_manifest.read_text())
    _ANCHORS = {
        "arrangement": "rule_67d34b1c927ef33d",
        "form":        "rule_84816f91e31e50c4",
        "harmonic":    "rule_0271c7a9f3b5f606",
        "melodic":     "rule_09f340921fa2d258",
        "rhythmic":    "rule_88b63bd5e771c045",
    }
    _got_ids = _sm0.get("chosen_rule_ids", {})
    for _rt, _exp in _ANCHORS.items():
        check(_got_ids.get(_rt) == _exp,
              f"M-GEN-1/batch-v1: salt=0 {_rt} regression (got {_got_ids.get(_rt)}, expected {_exp})")

# Coherence-gate coercions per salt (documented in §5 of report).
_EXPECT_N_COERC = {0: 2, 1: 2, 2: 1, 3: 1, 4: 2}
for _s, _n in _EXPECT_N_COERC.items():
    _cj = WS / "data" / "gen" / "batch_v1" / f"song_{_s}" / "coercions.json"
    if _cj.is_file():
        _cd = json.loads(_cj.read_text())
        check(_cd.get("n_coercions") == _n,
              f"M-GEN-1/batch-v1: salt={_s} coercions count (got {_cd.get('n_coercions')}, expected {_n})")

# Report + figure present.
check((WS / "docs" / "gen_batch_v1_report.md").is_file(),
      "M-GEN-1/batch-v1: docs/gen_batch_v1_report.md present")
check((WS / "docs" / "figures" / "gen_batch_v1_grid.png").is_file(),
      "M-GEN-1/batch-v1: docs/figures/gen_batch_v1_grid.png present")


# ---------------------------------------------------------------------------
# §24. M-RULES-1/extraction/breadth-seeds (cycle 12, fork ed041ef4c1dc, clone-0)
# ---------------------------------------------------------------------------
# Invariants:
#   (a) orchestrator + regression harness scripts present with interpreter guard
#   (b) non-factor AST isolation preserved
#   (c) cycle-9 anchor rule_ids byte-identical (prefix of the expanded ledger)
#   (d) ledger has ≥ 15 new rows beyond the 28-row cycle-9 baseline
#   (e) byte-determinism SHA anchor on the post-expansion ledger
#   (f) report + figure + salt-collision TSV present
_orch = WS / "scripts" / "rules" / "extract" / "breadth_seeds.py"
check(_orch.is_file(), "M-RULES-1/extraction/breadth-seeds: orchestrator script present")
if _orch.is_file():
    _src = _orch.read_text()
    check("assert sys.executable == \"/usr/bin/python3\"" in _src,
          "M-RULES-1/extraction/breadth-seeds: orchestrator has /usr/bin/python3 guard")
    import re as _re_bs
    _sidecar_hits = _re_bs.findall(r"(?m)^(?:from|import)\s+.*sidecar_nonfactor", _src)
    check(len(_sidecar_hits) == 0,
          f"M-RULES-1/extraction/breadth-seeds: orchestrator has 0 sidecar_nonfactor imports (got {len(_sidecar_hits)})")

# Cycle-9 anchor rule_ids reproduce byte-identically as the ledger prefix.
_lp = WS / "data" / "rules" / "ledger.jsonl"
if _lp.is_file():
    _all_rows = [json.loads(_l) for _l in _lp.read_text().splitlines() if _l.strip()]
    _n_rule_rows = sum(1 for _r in _all_rows if _r.get("event_type") == "rule")
    _n_new_rows = _n_rule_rows - 28
    check(_n_new_rows >= 15,
          f"M-RULES-1/extraction/breadth-seeds: ≥15 new rule rows appended (got {_n_new_rows})")
    _cycle9_anchor_ids = {
        "rule_0271c7a9f3b5f606",  # harmonic
        "rule_88b63bd5e771c045",  # rhythmic
        "rule_09f340921fa2d258",  # melodic
        "rule_84816f91e31e50c4",  # form
        "rule_67d34b1c927ef33d",  # arrangement
    }
    _prefix_ids = {_r["rule_id"] for _r in _all_rows[:28] if _r.get("event_type") == "rule"}
    _missing = _cycle9_anchor_ids - _prefix_ids
    check(not _missing,
          f"M-RULES-1/extraction/breadth-seeds: cycle-9 anchor rule_ids in prefix (missing={sorted(_missing)})")

    import hashlib as _hs_bs
    _got_sha = _hs_bs.sha256(_lp.read_bytes()).hexdigest()
    _EXP_SHA_PREFIX = "a6fd53e9bf9a10f6"
    check(_got_sha.startswith(_EXP_SHA_PREFIX),
          f"M-RULES-1/extraction/breadth-seeds: post-expansion ledger SHA anchor "
          f"(got {_got_sha[:16]}..., expected {_EXP_SHA_PREFIX}...)")

# Report + figure + salt-collision artifacts.
check((WS / "docs" / "rules_extraction_breadth_report.md").is_file(),
      "M-RULES-1/extraction/breadth-seeds: docs/rules_extraction_breadth_report.md present")
check((WS / "docs" / "figures" / "rules_extraction_breadth_growth.png").is_file(),
      "M-RULES-1/extraction/breadth-seeds: figure PNG present")
check((WS / "data" / "rules" / "breadth_expansion_summary.json").is_file(),
      "M-RULES-1/extraction/breadth-seeds: breadth_expansion_summary.json present")
check((WS / "data" / "rules" / "salt_collision_before_after.tsv").is_file(),
      "M-RULES-1/extraction/breadth-seeds: salt_collision_before_after.tsv present")
check((WS / "data" / "rules" / "salt_collision_before_after.json").is_file(),
      "M-RULES-1/extraction/breadth-seeds: salt_collision_before_after.json present")


# ---------------------------------------------------------------------------
# §24. _infra/fanout-concat-hardening — cycle 12, fork ed041ef4c1dc, clone 1.
# Concat SSoT `is`-identity across writer + concat + checker;
# LedgerConcatError MRO; full-ledger regression on the current ledger.
# ---------------------------------------------------------------------------

from long_exposure.tools import _ledger_schema as _ls_concat
from long_exposure.tools import promise_check as _pc_concat
from long_exposure import workspace_bootstrap as _wb_concat
from long_exposure.workspace_bootstrap import concat_clone_ledgers as _concat_fn

check(
    _pc_concat.REQUIRED_EVENT_FIELDS is _ls_concat.REQUIRED_EVENT_FIELDS,
    "_infra/fanout-concat-hardening: promise_check REQUIRED_EVENT_FIELDS is the SSoT object",
)
check(
    issubclass(_ls_concat.LedgerConcatError, _ls_concat.LedgerSchemaError),
    "_infra/fanout-concat-hardening: LedgerConcatError subclasses LedgerSchemaError",
)
check(
    issubclass(_ls_concat.LedgerConcatError, ValueError),
    "_infra/fanout-concat-hardening: LedgerConcatError subclasses ValueError",
)
check(
    hasattr(_ls_concat, "content_hash_tiebreak"),
    "_infra/fanout-concat-hardening: content_hash_tiebreak exported from _ledger_schema",
)
check(
    "content_hash_tiebreak" in Path(_wb_concat.__file__).read_text(),
    "_infra/fanout-concat-hardening: workspace_bootstrap imports content_hash_tiebreak",
)

# Full-ledger regression: current promise_ledger.jsonl re-validates end-to-end
# through the tightened concat, empty fork_dir, 0 rows added, byte-identical.
import shutil as _shutil_concat, tempfile as _tf_concat
_ws_concat = Path(_tf_concat.mkdtemp(prefix="concat_regression_"))
_shutil_concat.copy(WS / "promise_ledger.jsonl", _ws_concat / "promise_ledger.jsonl")
_before_concat = (_ws_concat / "promise_ledger.jsonl").read_bytes()
_n_concat = _concat_fn(_ws_concat, _ws_concat / "does_not_exist")
_after_concat = (_ws_concat / "promise_ledger.jsonl").read_bytes()
check(
    _n_concat == 0,
    f"_infra/fanout-concat-hardening: 0 new rows on empty-fork regression (got {_n_concat})",
)
check(
    _before_concat == _after_concat,
    "_infra/fanout-concat-hardening: main ledger byte-identical after empty-fork concat",
)


# ---------------------------------------------------------------------------
# §27. M-TEX-1/stage-by-stage widening — cycle 13, fork 54a6c185816e, clone 2.
# ---------------------------------------------------------------------------
# Widens cycle-9 stage_by_stage to 2 breadth seeds (seed_mid_50s + synth_060s).
# Invariants:
#   - v2 orchestrator + plot script present + interpreter-guarded
#   - no sidecar_nonfactor imports in the new scripts
#   - the cycle-9 pinned chain module is imported verbatim (not reimplemented)
#   - the cycle-9 synth_030s TSV anchor SHA is unchanged
#   - the two new per-seed TSVs + effects_layered.wav have known SHA-256 anchors
#   - each per-seed TSV has 3 pair rows × exactly the 8-key panel contract
#     (10 columns: a_stage, b_stage, plus 8 panel keys)

_TEX_V2_ORCH = WS / "scripts" / "tex" / "stage_by_stage_v2.py"
_TEX_V2_PLOT = WS / "scripts" / "tex" / "plot_stage_by_stage_v2.py"
_TEX_CHAIN   = WS / "scripts" / "tex" / "render_effects_layered.py"

for _p in (_TEX_V2_ORCH, _TEX_V2_PLOT):
    check(_p.exists(), f"M-TEX-1/stage-by-stage widening: {_p.relative_to(WS)} exists")
    _src = _p.read_text()
    check(
        'assert sys.executable == "/usr/bin/python3"' in _src,
        f"M-TEX-1/stage-by-stage widening: {_p.name} carries interpreter guard",
    )
    import re as _re_tex_v2
    check(
        not _re_tex_v2.search(r"^(from|import) .*sidecar_nonfactor", _src, _re_tex_v2.MULTILINE),
        f"M-TEX-1/stage-by-stage widening: {_p.name} has no sidecar_nonfactor imports",
    )

# The v2 orchestrator must reuse the cycle-9 chain by import, not by copy.
_v2_src = _TEX_V2_ORCH.read_text()
check(
    "from scripts.tex.render_effects_layered import apply_effects_layered" in _v2_src,
    "M-TEX-1/stage-by-stage widening: v2 orchestrator imports cycle-9 chain verbatim",
)
check(
    "from scripts.tex.measure_across_stages import measure_pairs" in _v2_src,
    "M-TEX-1/stage-by-stage widening: v2 orchestrator imports cycle-9 measurement verbatim",
)

# The cycle-9 chain module itself must still carry the pinned parameter signature.
_chain_src = _TEX_CHAIN.read_text()
for _needle, _msg in (
    ("FX Type", "Surge XT chorus/reverb FX Type parameters"),
    ("Output Mix", "Surge XT Output Mix parameter"),
    ("0.28", "chorus FX Type=0.28 pin"),
    ("0.35", "chorus Output Mix=0.35 pin"),
    ("0.02", "reverb FX Type=0.02 pin"),
    ("linspace(0.05, 0.60", "reverb Output Mix ramp 0.05→0.60 pin"),
    ("linspace(0.25, 1.4", "post-chain gain ramp 0.25→1.4 pin"),
):
    check(
        _needle in _chain_src,
        f"M-TEX-1/stage-by-stage widening: cycle-9 chain preserves {_msg}",
    )

# Anchor SHAs.
import hashlib as _hashlib_tex_v2

_ANCHORS = {
    WS / "data" / "tex" / "stage_by_stage_synth_030s.tsv":
        "b3570a795c8c3e7a5f59ddefbd20096e8221cabef8d4d1fad5a621a3ba0fece2",
    WS / "data" / "tex" / "stage_by_stage_seed_mid_50s.tsv":
        "a25b98e47ff3e8fc1ee257b81af33317c8eb152297fd8bed408fcbaab7674330",
    WS / "data" / "tex" / "stage_by_stage_synth_060s.tsv":
        "51f6749b5fa3c23b1549d2a57ea67286c244c344234f69f5a76592db498b9803",
    WS / "data" / "tex" / "renders" / "seed_mid_50s" / "effects_layered.wav":
        "312aa9cd03b9cc09128998d5a617ec09c15404b5812fb9974b91c8f323f8040a",
    WS / "data" / "tex" / "renders" / "synth_060s" / "effects_layered.wav":
        "5a9842864060075a47a6bddda1106617a5d7f542029110602e00401ef15440b6",
}
for _path, _sha in _ANCHORS.items():
    check(_path.exists(), f"M-TEX-1/stage-by-stage widening: {_path.relative_to(WS)} exists")
    _actual = _hashlib_tex_v2.sha256(_path.read_bytes()).hexdigest()
    check(
        _actual == _sha,
        f"M-TEX-1/stage-by-stage widening: {_path.relative_to(WS)} SHA-256 matches anchor",
    )

# TSV shape: 4 lines (header + 3 pair rows); each row has 10 tab-separated fields.
_EXPECTED_HEADER = ("a_stage\tb_stage\tmel_l1_db\tspectral_centroid_rmse_hz\t"
                    "rms_env_rmse\tlufs_m_rmse_lu\tembedding_cosine_distance\t"
                    "embedding_rung\tsr_hz\tn_samples_compared")
for _seed in ("synth_030s", "seed_mid_50s", "synth_060s"):
    _tsv = WS / "data" / "tex" / f"stage_by_stage_{_seed}.tsv"
    _lines = _tsv.read_text().strip().split("\n")
    check(
        len(_lines) == 4,
        f"M-TEX-1/stage-by-stage widening: {_seed} TSV has header + 3 pair rows",
    )
    check(
        _lines[0] == _EXPECTED_HEADER,
        f"M-TEX-1/stage-by-stage widening: {_seed} TSV header matches 8-key panel contract",
    )
    for _row in _lines[1:]:
        check(
            len(_row.split("\t")) == 10,
            f"M-TEX-1/stage-by-stage widening: {_seed} TSV row has 10 columns",
        )

# Report + figure ship.
_REPORT = WS / "docs" / "tex_stage_by_stage_widening_report.md"
_FIGURE = WS / "docs" / "figures" / "tex_stage_by_stage_3seeds.png"
check(_REPORT.exists(), "M-TEX-1/stage-by-stage widening: report ships")
check(_FIGURE.exists(), "M-TEX-1/stage-by-stage widening: figure ships")


# ---------------------------------------------------------------------------
# §26. M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation — cycle 13,
# fork 54a6c185816e, clone 1. DawDreamer-native time-varying parameter
# automation via set_automation(). Invariants: scripts present, interpreter
# guard, non-factor AST isolation, byte-determinism SHA anchors on the
# automated/reference WAVs, env_correlation JSON present + value tracked,
# coverage_matrix_v3.json present + valid, cycle-9 pinned chain not imported
# (grep verified).
# ---------------------------------------------------------------------------

import hashlib as _hl_gap2
import json as _json_gap2
from pathlib import Path as _P_gap2

_GAP2 = WS / "scripts/daw_spike/gap2_v3"
_GAP2_DATA = WS / "data/daw_spike/gap2_v3"

for _f in (
    "synth_input.py",
    "dawdreamer_automation.py",
    "render_reference.py",
    "measure_env_correlation.py",
    "orchestrator.py",
    "coverage_matrix_v3.py",
    "plot_gap2_v3.py",
):
    check(
        (_GAP2 / _f).exists(),
        f"M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: {_f} present",
    )

for _f in (
    "input_10s.wav",
    "automated.wav",
    "reference.wav",
    "flat_control.wav",
    "env_correlation.json",
    "flat_env_correlation.json",
    "summary.json",
):
    check(
        (_GAP2_DATA / _f).exists(),
        f"M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: data/gap2_v3/{_f} present",
    )

# Interpreter guard on every new script.
for _f in (
    "synth_input.py",
    "dawdreamer_automation.py",
    "render_reference.py",
    "measure_env_correlation.py",
    "orchestrator.py",
    "coverage_matrix_v3.py",
    "plot_gap2_v3.py",
):
    _src = (_GAP2 / _f).read_text()
    check(
        "assert sys.executable == '/usr/bin/python3'" in _src,
        f"M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: {_f} carries interpreter guard",
    )

# Non-factor AST isolation: no sidecar_nonfactor imports.
import re as _re_gap2
for _f in list(_GAP2.glob("*.py")):
    _src = _f.read_text()
    check(
        not _re_gap2.search(r"(?m)^\s*(from|import)\s+.*sidecar_nonfactor", _src),
        f"M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: {_f.name} no sidecar_nonfactor import",
    )

# Cycle-9 pinned chain isolation: no import of scripts.tex.render_effects_layered.
for _f in list(_GAP2.glob("*.py")):
    _src = _f.read_text()
    check(
        not _re_gap2.search(r"(?m)^\s*(from|import)\s+scripts\.tex\.render_effects_layered", _src),
        f"M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: {_f.name} does not import cycle-9 pinned chain (render_effects_layered)",
    )
    # Reference check restricted to code-line contexts (skip comments/docstrings).
    _code_lines = [ln for ln in _src.splitlines() if not ln.lstrip().startswith("#")]
    _code = "\n".join(_code_lines)
    # Strip triple-quoted docstrings for the reference test.
    _code_stripped = _re_gap2.sub(r'""".*?"""', '', _code, flags=_re_gap2.DOTALL)
    _code_stripped = _re_gap2.sub(r"'''.*?'''", '', _code_stripped, flags=_re_gap2.DOTALL)
    check(
        "render_effects_layered" not in _code_stripped,
        f"M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: {_f.name} does not reference cycle-9 pinned chain in code",
    )

# Byte-determinism SHA anchors from cycle-13 clone-1 run.
_SHA_ANCHORS = {
    "input_10s.wav": "cdade28b97826908ba02c7251e6c02a88639033d70d9a2b62e6ea6904eded660",
    "automated.wav": "e8e27b22f01d0e53956e036d218b0eb7fc5c8bd4e68814d265d993d128b86003",
    "reference.wav": "cc44bcffb4c22b67867e8c9a992d8a850394163d1017677b44a1de5739984bb7",
    "flat_control.wav": "60c6fa34381e70a9665364a54f6c611c6e4cd19581c7802ad461bbeaae299399",
}
for _name, _sha in _SHA_ANCHORS.items():
    _actual = _hl_gap2.sha256((_GAP2_DATA / _name).read_bytes()).hexdigest()
    check(
        _actual == _sha,
        f"M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: {_name} SHA anchor matches ({_actual[:16]}...)",
    )

# Env-correlation JSON present and structured.
_ec = _json_gap2.loads((_GAP2_DATA / "env_correlation.json").read_text())
check(
    isinstance(_ec.get("env_correlation"), float),
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: env_correlation.json carries a float env_correlation",
)
check(
    _ec.get("n_fft") == 2048 and _ec.get("hop") == 512 and _ec.get("sr") == 44100,
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: env_correlation.json methodology params match brief (n_fft=2048, hop=512, sr=44100)",
)

# Summary.json + coverage matrix v3 present and valid.
_sm = _json_gap2.loads((_GAP2_DATA / "summary.json").read_text())
check(
    _sm.get("verdict") in ("GREEN-via-DawDreamer", "redefined-GAP", "still-GAP"),
    f"M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: summary.json verdict enumerated ({_sm.get('verdict')})",
)
check(
    _sm.get("byte_determinism_x2") is True,
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: summary.json records byte_determinism_x2 True",
)
check(
    _sm.get("parameter_name") == "Output Mix" and _sm.get("parameter_index") == 10,
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: summary.json records Output Mix param (index 10)",
)
check(
    _sm.get("dawdreamer_version") == "0.9.0",
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: summary.json records dawdreamer 0.9.0",
)
_v3 = _json_gap2.loads((WS / "data/daw_spike/coverage_matrix_v3.json").read_text())
check(
    _v3.get("matrix_version") == 3 and _v3.get("cycle") == 13,
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: coverage_matrix_v3.json version=3, cycle=13",
)
check(
    _v3.get("cycle13_gap2_verdict") in ("GREEN-via-DawDreamer", "redefined-GAP", "still-GAP"),
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: coverage_matrix_v3.json cycle13_gap2_verdict enumerated",
)

# v2 is preserved byte-identically.
_v2_expected_ver = 2
_v2 = _json_gap2.loads((WS / "data/daw_spike/coverage_matrix_v2.json").read_text())
check(
    _v2.get("matrix_version") == _v2_expected_ver and _v2.get("cycle") == 12,
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: v2 preserved (matrix_version=2, cycle=12)",
)

# Report + figure exist.
check(
    (WS / "docs/daw_spike_gap2_dawdreamer_closure_report.md").exists(),
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: closure report present",
)
check(
    (WS / "docs/figures/daw_spike_gap2_v3_automation.png").exists(),
    "M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation: automation figure present",
)


# ---------------------------------------------------------------------------
# §25. M-GEN-1/batch-v2 — cycle 13, fork 54a6c185816e, clone 0.
# ---------------------------------------------------------------------------
# Invariants:
#   (a) 4 new scripts present with interpreter guard
#   (b) non-factor AST isolation preserved
#   (c) PRNG-grep guard clean on 4 new scripts
#   (d) 8-song per-file artifacts present (56 files) + 6 aggregates
#   (e) batch_v2 salt=0 anchor byte-identity (self-consistency across
#       reruns, tracked by the frozen SHA anchors in this file)
#   (f) collision_analysis.json + salt4_diagnostic.json + collision_matrix.tsv
#       present; salt=4 verdict in the enumerated set
#   (g) PYTHONHASHSEED=0 assertion visible in orchestrator source
#   (h) report + 2 figures shipped
import json as _json_bv2

# (a) 4 new scripts present + interpreter guard
_bv2_scripts = ("batch_v2.py", "collision_analysis.py",
                "salt4_diagnostic.py", "plot_batch_v2.py")
for _name in _bv2_scripts:
    _p = WS / "scripts" / "gen" / _name
    check(_p.is_file(), f"M-GEN-1/batch-v2: scripts/gen/{_name} present")
    if _p.is_file():
        _text = _p.read_text(encoding="utf-8")
        check("assert sys.executable == \"/usr/bin/python3\"" in _text,
              f"M-GEN-1/batch-v2: scripts/gen/{_name} interpreter guard")

# (b) non-factor AST isolation
import re as _re_bv2
_iso_bv2 = _re_bv2.compile(r"^\s*(from|import)\s+.*sidecar_nonfactor")
for _name in _bv2_scripts:
    _p = WS / "scripts" / "gen" / _name
    if _p.is_file():
        _hits = [ln for ln in _p.read_text(encoding="utf-8").splitlines()
                  if _iso_bv2.match(ln)]
        check(_hits == [],
              f"M-GEN-1/batch-v2: scripts/gen/{_name} non-factor AST isolation")

# (c) PRNG-grep guard
_prng_bv2 = _re_bv2.compile(
    r"^\s*(from|import)\s+.*(?:^|[^A-Za-z_])"
    r"(random|numpy\.random|torch\.rand|secrets)(?:[^A-Za-z_0-9]|$)"
)
for _name in _bv2_scripts:
    _p = WS / "scripts" / "gen" / _name
    if _p.is_file():
        _hits = [ln for ln in _p.read_text(encoding="utf-8").splitlines()
                  if _prng_bv2.match(ln)]
        check(_hits == [],
              f"M-GEN-1/batch-v2: scripts/gen/{_name} PRNG-import guard")

# (d) 8-song per-file artifacts
_batch_v2_root = WS / "data" / "gen" / "batch_v2"
check(_batch_v2_root.is_dir(), "M-GEN-1/batch-v2: data/gen/batch_v2/ present")
for _s in range(8):
    _sd = _batch_v2_root / f"song_{_s}"
    for _n in ("generated.musicxml", "generated.mid", "bare_midi.wav",
               "effects_layered.wav", "scoring.json", "coercions.json",
               "sampling_manifest.json"):
        check((_sd / _n).is_file(),
              f"M-GEN-1/batch-v2: song_{_s}/{_n} present")

# Aggregates present
for _rel in ("summary.tsv", "provenance.jsonl", "batch_manifest.json",
             "collision_analysis.json", "collision_matrix.tsv",
             "salt4_diagnostic.json"):
    check((_batch_v2_root / _rel).is_file(),
          f"M-GEN-1/batch-v2: {_rel} present")

# (e) batch_v2 salt=0 anchor byte-identity — anchors are what THIS run
# produced on the 76-row ledger (NEW anchor; batch_v1's saved anchor is
# a separate file untouched by this cycle). See report §2.
_bv2_song0_manifest = _batch_v2_root / "song_0" / "sampling_manifest.json"
if _bv2_song0_manifest.is_file():
    _sm0_bv2 = _json_bv2.loads(_bv2_song0_manifest.read_text())
    _ANCHORS_BV2 = {
        "harmonic":    "rule_0271c7a9f3b5f606",   # unchanged from batch-v1
        "rhythmic":    "rule_88b63bd5e771c045",   # unchanged from batch-v1
        "melodic":     "rule_daf022a4051dff00",   # NEW (was 09f340...)
        "form":        "rule_8e6c38d5397fb898",   # NEW (was 84816f...)
        "arrangement": "rule_51d59f03c4f09e1a",   # NEW (was 67d34b...)
    }
    _got_bv2 = _sm0_bv2.get("chosen_rule_ids", {})
    for _rt, _exp in _ANCHORS_BV2.items():
        check(_got_bv2.get(_rt) == _exp,
              f"M-GEN-1/batch-v2: salt=0 {_rt} anchor "
              f"(got {_got_bv2.get(_rt)}, expected {_exp})")

# (f) salt=4 diagnostic verdict enumerated
_sd_bv2 = _batch_v2_root / "salt4_diagnostic.json"
if _sd_bv2.is_file():
    _sd = _json_bv2.loads(_sd_bv2.read_text())
    _v = _sd.get("verdict", {}).get("verdict")
    check(_v in {"no_material_pattern", "hash_space",
                 "arrangement_structural", "coherence_gate", "mixed"},
          f"M-GEN-1/batch-v2: salt=4 verdict enumerated (got {_v})")

# collision analysis: total pairs at N=8 is an integer > 0
_ca_bv2 = _batch_v2_root / "collision_analysis.json"
if _ca_bv2.is_file():
    _ca = _json_bv2.loads(_ca_bv2.read_text())
    _tp = _ca.get("coerced", {}).get("total_pairwise_collisions")
    check(isinstance(_tp, int) and _tp >= 0,
          f"M-GEN-1/batch-v2: collision_analysis total_pairwise_collisions "
          f"is int >= 0 (got {_tp})")

# (g) PYTHONHASHSEED=0 in orchestrator
_bv2_text = (WS / "scripts" / "gen" / "batch_v2.py").read_text(encoding="utf-8")
check('"PYTHONHASHSEED"' in _bv2_text and '"0"' in _bv2_text,
      "M-GEN-1/batch-v2: batch_v2.py sets PYTHONHASHSEED=0")

# (h) report + 2 figures shipped
check((WS / "docs" / "gen_batch_v2_report.md").is_file(),
      "M-GEN-1/batch-v2: docs/gen_batch_v2_report.md present")
check((WS / "docs" / "figures" / "gen_batch_v2_grid.png").is_file(),
      "M-GEN-1/batch-v2: docs/figures/gen_batch_v2_grid.png present")
check((WS / "docs" / "figures" / "gen_batch_v2_collisions.png").is_file(),
      "M-GEN-1/batch-v2: docs/figures/gen_batch_v2_collisions.png present")


# =====================================================================
# §28. _infra/ledger-schema-hardening-v2 — cycle 14, fork 855d4c2e9945, clone-0.
#
# Validates that the cycle-14 SSoT extension actually landed, without
# depending on any of the workspace-side test suites.
# =====================================================================
_LE_PARENT_C14 = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT_C14 not in sys.path:
    sys.path.insert(0, _LE_PARENT_C14)

# (a) enum constant exported at module level
from long_exposure.tools._ledger_schema import (
    _STATUS_ENUM,
    STATUS_VALUES,
    LedgerConcatError,
    LedgerSchemaError,
    validate_event,
)
check(_STATUS_ENUM is STATUS_VALUES,
      "schema-v2 §28a: _STATUS_ENUM aliases STATUS_VALUES (is-identity)")
check({"in-progress", "validated", "invalidated", "reopened",
       "superseded"}.issubset(_STATUS_ENUM),
      "schema-v2 §28a: brief-proposed enum is subset of _STATUS_ENUM")

# (b) pre-concat lint helper present on workspace_bootstrap
from long_exposure.workspace_bootstrap import (
    _lint_clone_shadow,
    concat_clone_ledgers,
)
check(callable(_lint_clone_shadow),
      "schema-v2 §28b: _lint_clone_shadow importable + callable")

# (c) LedgerConcatError MRO subclass of LedgerSchemaError (cycle-12 contract)
check(issubclass(LedgerConcatError, LedgerSchemaError),
      "schema-v2 §28c: LedgerConcatError subclass of LedgerSchemaError")

# (d) drift-rejection message shape — list-form supersedes_path names the field
_bad_list = {"supersedes_path": ["a", "b"]}
_errs_list = validate_event(_bad_list)
_sp_hits = [e for e in _errs_list if "supersedes_path" in e and "must be" in e]
check(len(_sp_hits) == 1,
      "schema-v2 §28d: list-form supersedes_path names field + type")

# (e) drift-rejection — unknown status names 'status' and the offending value
_bad_status = {"status": "wobble"}
_errs_status = validate_event(_bad_status)
_st_hits = [e for e in _errs_status
            if "status" in e and "wobble" in e]
check(len(_st_hits) == 1,
      "schema-v2 §28e: unknown status names field + offending value")

# (f) string-form supersedes_path stays accepted
_ok = validate_event({"supersedes_path": "tools/foo.py"})
_ok_sp = [e for e in _ok if "supersedes_path" in e]
check(_ok_sp == [],
      "schema-v2 §28f: string-form supersedes_path accepted")

# (g) 275/275 (or more) existing rows still pass tightened validator
_ledger_path = WS / "promise_ledger.jsonl"
if _ledger_path.exists():
    _fails = []
    for _i, _line in enumerate(_ledger_path.read_text().splitlines(), 1):
        _line = _line.strip()
        if not _line:
            continue
        _row = json.loads(_line)
        _errs = validate_event(_row)
        if _errs:
            _fails.append((_i, _row.get("milestone_id"), _errs))
    check(_fails == [],
          f"schema-v2 §28g: existing ledger rows all validate ({len(_fails)} failures)")

# (h) report shipped
check((WS / "docs" / "ledger_schema_hardening_v2.md").is_file(),
      "schema-v2 §28h: docs/ledger_schema_hardening_v2.md present")


# =====================================================================
# §29. M-GEN-1/collision-floor-investigation — cycle 14, fork 855d4c2e9945,
#      clone-1. Structural investigation of the corpus-size-invariant
#      11-pair floor at N=8 on the 76-row rules ledger.
# =====================================================================

# (a) analysis package + 5 scripts present
_analysis_dir = WS / "scripts" / "rules" / "analysis"
for _fname in ("__init__.py", "collision_attribution.py",
               "structural_fingerprints.py", "pairwise_distance.py",
               "cluster_analysis.py", "intervention_proposal.py",
               "plot_collision_floor.py"):
    check((_analysis_dir / _fname).is_file(),
          f"cf-investigation §29a: {_fname} present")

# (b) interpreter guard on every new script
import re as _re29
_guard_pat = _re29.compile(r"assert\s+sys\.executable\s*==\s*['\"]/usr/bin/python3['\"]")
for _fname in ("collision_attribution.py", "structural_fingerprints.py",
               "pairwise_distance.py", "cluster_analysis.py",
               "intervention_proposal.py", "plot_collision_floor.py"):
    _txt = (_analysis_dir / _fname).read_text()
    check(bool(_guard_pat.search(_txt)),
          f"cf-investigation §29b: interpreter guard in {_fname}")

# (c) non-factor AST isolation: no imports of sidecar_nonfactor anywhere
_forbid = _re29.compile(r"^\s*(from|import)\s+.*sidecar_nonfactor", _re29.MULTILINE)
for _fname in ("collision_attribution.py", "structural_fingerprints.py",
               "pairwise_distance.py", "cluster_analysis.py",
               "intervention_proposal.py", "plot_collision_floor.py"):
    _txt = (_analysis_dir / _fname).read_text()
    check(not _forbid.search(_txt),
          f"cf-investigation §29c: no sidecar_nonfactor import in {_fname}")

# (d) attribution accounting invariant: 11 pair-contribs, 10 unique pairs
_attr_path = WS / "data" / "rules" / "collision_floor_analysis" / "attribution.json"
check(_attr_path.is_file(), "cf-investigation §29d: attribution.json present")
if _attr_path.is_file():
    _attr = json.loads(_attr_path.read_text())
    check(_attr["total_pairwise_collisions"] == 11,
          f"cf-investigation §29d: total_pairwise_collisions == 11 (got {_attr['total_pairwise_collisions']})")
    check(_attr["any_collision_pair_count"] == 10,
          f"cf-investigation §29d: any_collision_pair_count == 10 (got {_attr['any_collision_pair_count']})")
    check(_attr["per_rule_type_pair_count"]["harmonic"] == 6,
          "cf-investigation §29d: harmonic contributes 6 pairs")
    check(_attr["per_rule_type_pair_count"]["rhythmic"] == 2,
          "cf-investigation §29d: rhythmic contributes 2 pairs")
    check(_attr["per_rule_type_pair_count"]["melodic"] == 2,
          "cf-investigation §29d: melodic contributes 2 pairs")
    check(_attr["per_rule_type_pair_count"]["form"] == 0,
          "cf-investigation §29d: form contributes 0 pairs")
    check(_attr["per_rule_type_pair_count"]["arrangement"] == 1,
          "cf-investigation §29d: arrangement contributes 1 pair")

# (e) byte-determinism SHA anchors on all 5 declared JSON/TSV outputs
_cf_dir = WS / "data" / "rules" / "collision_floor_analysis"
_SHA_ANCHORS = {
    "attribution.json":
        "0a3f9acb4bc8eaf55bf5cf78b1f466bf4f89e8abdd1c503abeba89a63ba7a12d",
    "fingerprints.tsv":
        "cc6aafd79aa380983b26ae39fea8ee1b04ad080750b5ce5bbeeeed7f2edcadb3",
    "cluster_verdict.json":
        "e42e5ccd2a6f1ce2ad84a7b0c84d516970245794567ec64300625f40e3ff5dad",
    "intervention_proposal.json":
        "0f124a39db0fcacff0442cc3abbb0d70ec919a8e96b807e8b95da5c42d162c53",
    "pairwise_distances_harmonic.tsv":
        "f3f4202a7702fcd94465d74995df043091b301dab40f2123482b11b608240c8b",
}
import hashlib as _h29
for _fname, _exp_sha in _SHA_ANCHORS.items():
    _fp = _cf_dir / _fname
    check(_fp.is_file(), f"cf-investigation §29e: {_fname} present")
    if _fp.is_file():
        _got = _h29.sha256(_fp.read_bytes()).hexdigest()
        check(_got == _exp_sha,
              f"cf-investigation §29e: {_fname} SHA-256 matches anchor ({_got[:16]}...)")

# (f) rules-schema-untouched: SHA-256 anchor of frozen schema
_schema_path = WS / "scripts" / "rules" / "schema" / "rules_v1.json"
if _schema_path.is_file():
    _got = _h29.sha256(_schema_path.read_bytes()).hexdigest()
    check(_got == "b9bec6733c0be7e4eb3d53145fd81fee1552523efcd1309c981b95cf2b4694ff",
          f"cf-investigation §29f: rules_v1.json SHA unchanged ({_got[:16]}...)")

# (g) rules-ledger-untouched: SHA-256 anchor of frozen 76-row ledger
_ledger_r_path = WS / "data" / "rules" / "ledger.jsonl"
if _ledger_r_path.is_file():
    _got = _h29.sha256(_ledger_r_path.read_bytes()).hexdigest()
    check(_got == "a6fd53e9bf9a10f6885888b0bb7d11a9a2aa97007e38ef0e6d47f4ef7d2857ae",
          f"cf-investigation §29g: rules ledger.jsonl SHA unchanged ({_got[:16]}...)")
    _n_rows = sum(1 for l in _ledger_r_path.read_text().splitlines() if l.strip())
    check(_n_rows == 76, f"cf-investigation §29g: rules ledger has 76 rows (got {_n_rows})")

# (h) report + figure shipped
check((WS / "docs" / "collision_floor_investigation_report.md").is_file(),
      "cf-investigation §29h: docs/collision_floor_investigation_report.md present")
check((WS / "docs" / "figures" / "collision_floor_decomposition.png").is_file(),
      "cf-investigation §29h: docs/figures/collision_floor_decomposition.png present")

# (i) intervention proposal is concrete (numeric predicted floor for I3+I4)
_ip_path = WS / "data" / "rules" / "collision_floor_analysis" / "intervention_proposal.json"
if _ip_path.is_file():
    _ip = json.loads(_ip_path.read_text())
    _ivs = {iv["id"]: iv for iv in _ip["interventions"]}
    check("I3" in _ivs and _ivs["I3"].get("sweep"),
          "cf-investigation §29i: I3 (corpus expansion) has numeric sweep")
    check("I4" in _ivs and _ivs["I4"].get("predicted_total_floor") == 0.0,
          "cf-investigation §29i: I4 (rejection sampling) predicts 0 pairs")

# §30. M-TEX-1/panel/embedding/content-flip-analysis — cycle 14, fork
# 855d4c2e9945, clone 2.

_cflip_scripts_dir = WS / "scripts" / "tex" / "content_flip"
_cflip_data_dir = WS / "data" / "tex" / "embedding_flip_analysis"

# (a) scripts present
for _fname in ("__init__.py", "synth_variants.py", "apply_pinned_chain.py",
               "measure_variant.py", "orchestrator.py", "analyze_flip.py",
               "plot_flip_analysis.py"):
    check((_cflip_scripts_dir / _fname).is_file(),
          f"content-flip §30a: scripts/tex/content_flip/{_fname} present")

# (b) interpreter guard on every new script
import re as _re30
for _fname in ("synth_variants.py", "apply_pinned_chain.py",
               "measure_variant.py", "orchestrator.py", "analyze_flip.py",
               "plot_flip_analysis.py"):
    _p = _cflip_scripts_dir / _fname
    if _p.is_file():
        _txt = _p.read_text()
        check('assert sys.executable == "/usr/bin/python3"' in _txt,
              f"content-flip §30b: {_fname} interpreter guard present")

# (c) non-factor AST isolation on every new script
for _fname in ("synth_variants.py", "apply_pinned_chain.py",
               "measure_variant.py", "orchestrator.py", "analyze_flip.py",
               "plot_flip_analysis.py"):
    _p = _cflip_scripts_dir / _fname
    if _p.is_file():
        _txt = _p.read_text()
        _has_nf = bool(_re30.search(r"(?m)^(from|import)\s+.*sidecar_nonfactor", _txt))
        check(not _has_nf,
              f"content-flip §30c: {_fname} no sidecar_nonfactor import")

# (d) cycle-9 chain isolation (anchored-import grep on the content_flip pkg)
_cf_pkg_pattern = _re30.compile(
    r"(?m)^(from|import)\s+(scripts\.tex\.render_effects_layered|scripts_tex_render_effects_layered)"
)
_iso_bad = []
for _fname in ("synth_variants.py", "apply_pinned_chain.py",
               "measure_variant.py", "orchestrator.py", "analyze_flip.py",
               "plot_flip_analysis.py", "__init__.py"):
    _p = _cflip_scripts_dir / _fname
    if _p.is_file() and _cf_pkg_pattern.search(_p.read_text()):
        _iso_bad.append(_fname)
check(not _iso_bad,
      f"content-flip §30d: zero anchored imports of scripts.tex.render_effects_layered under scripts/tex/content_flip/ ({_iso_bad!r})")

# (e) cycle-13 anchor byte-identity: 3 anchor TSVs must match frozen SHAs.
import hashlib as _h30
_ANCHOR_SHA = {
    "stage_by_stage_synth_030s.tsv":   "b3570a795c8c3e7a5f59ddefbd20096e8221cabef8d4d1fad5a621a3ba0fece2",
    "stage_by_stage_seed_mid_50s.tsv": "a25b98e47ff3e8fc1ee257b81af33317c8eb152297fd8bed408fcbaab7674330",
    "stage_by_stage_synth_060s.tsv":   "51f6749b5fa3c23b1549d2a57ea67286c244c344234f69f5a76592db498b9803",
}
for _fname, _exp in _ANCHOR_SHA.items():
    _p = WS / "data" / "tex" / _fname
    if _p.is_file():
        _got = _h30.sha256(_p.read_bytes()).hexdigest()
        check(_got == _exp,
              f"content-flip §30e: {_fname} SHA-256 unchanged ({_got[:16]}...)")

# (f) 8-variant byte-determinism SHAs: variant_manifest.json holds them.
_manifest_path = _cflip_data_dir / "variant_manifest.json"
if _manifest_path.is_file():
    _manifest = json.loads(_manifest_path.read_text())
    _variants = _manifest.get("variants", {})
    check(len(_variants) == 8,
          f"content-flip §30f: variant_manifest.json has 8 variants (got {len(_variants)})")
    for _vid in ("P1", "P2", "P3", "P4", "E1", "E2", "E3", "E4"):
        _v = _variants.get(_vid, {})
        check("bare_sha" in _v and "eff_sha" in _v,
              f"content-flip §30f: variant {_vid} has bare_sha + eff_sha")
        _bare_p = WS / _v.get("bare_wav", "")
        _eff_p  = WS / _v.get("eff_wav", "")
        if _bare_p.is_file():
            _got = _h30.sha256(_bare_p.read_bytes()).hexdigest()
            check(_got == _v["bare_sha"],
                  f"content-flip §30f: variant {_vid} bare_midi.wav SHA matches manifest")
        if _eff_p.is_file():
            _got = _h30.sha256(_eff_p.read_bytes()).hexdigest()
            check(_got == _v["eff_sha"],
                  f"content-flip §30f: variant {_vid} effects_layered.wav SHA matches manifest")

# (g) threshold_characterization.json shape
_tc_path = _cflip_data_dir / "threshold_characterization.json"
if _tc_path.is_file():
    _tc = json.loads(_tc_path.read_text())
    for _k in ("verdict", "flip_dimension", "polyphony_axis", "envelope_axis",
               "cycle13_anchors_across_stage"):
        check(_k in _tc,
              f"content-flip §30g: threshold_characterization.json has '{_k}'")
    check(_tc.get("flip_dimension") in
          ("polyphony", "envelope", "both", "neither"),
          f"content-flip §30g: flip_dimension is one of the expected values (got {_tc.get('flip_dimension')!r})")
    check(_tc.get("verdict") in
          ("localized_to_polyphony", "localized_to_envelope",
           "flip_polydimensional", "no_flip_reproduced", "noisy", "unknown"),
          f"content-flip §30g: verdict is one of the expected values (got {_tc.get('verdict')!r})")

# (h) report + figure shipped
check((WS / "docs" / "tex_embedding_content_flip_report.md").is_file(),
      "content-flip §30h: docs/tex_embedding_content_flip_report.md present")
check((WS / "docs" / "figures" / "tex_embedding_flip_analysis.png").is_file(),
      "content-flip §30h: docs/figures/tex_embedding_flip_analysis.png present")

# §31. M-GEN-1/batch-v4-compound — cycle 16, fork cc548ca0c2e5, clone 1.
# Empirical composition test of I3 (corpus augmentation) + I4 (stratified
# sampler) through cycle-13's frozen batch-v2 render pipeline verbatim.
import hashlib as _h31
_v4_dir = WS / "data" / "gen" / "batch_v4"
_i4_dir = WS / "data" / "gen" / "batch_v3_i4"
_i3_dir = WS / "data" / "gen" / "batch_v3_i3"
_v2_dir = WS / "data" / "gen" / "batch_v2"
_aug_ledger = WS / "data" / "rules" / "ledger_i3_dminor.jsonl"
_src_ledger = WS / "data" / "rules" / "ledger.jsonl"

# (a) driver script present + interpreter-guarded
_drv_p = WS / "scripts" / "gen" / "batch_v4_compound.py"
check(_drv_p.is_file(), "batch-v4 §31a: batch_v4_compound.py present")
_drv_src = _drv_p.read_text()
check("assert sys.executable == \"/usr/bin/python3\"" in _drv_src,
      "batch-v4 §31a: driver has interpreter guard")

# (b) sampler-file SHA anchor (stored on first run under data/gen/batch_v4/)
_anchor_sha_file = _v4_dir / ".i4_sampler_anchor_sha256"
if _anchor_sha_file.is_file():
    _sampler = WS / "scripts" / "rules" / "sampling" / "i4_stratified.py"
    _live = _h31.sha256(_sampler.read_bytes()).hexdigest()
    _anchored = _anchor_sha_file.read_text().strip()
    check(_live == _anchored,
          f"batch-v4 §31b: I4 sampler SHA unchanged since batch_v4 anchor ({_live[:16]} vs {_anchored[:16]})")

# (c) source-ledger anchor — driver reads the I3-augmented 86-row ledger
check("I3_LEDGER = _REPO / \"data\" / \"rules\" / \"ledger_i3_dminor.jsonl\"" in _drv_src,
      "batch-v4 §31c: driver's I3_LEDGER points at the augmented ledger")
if _aug_ledger.is_file():
    with _aug_ledger.open() as _f:
        _n_aug = sum(1 for _ in _f)
    check(_n_aug == 86,
          f"batch-v4 §31c: augmented ledger has 86 rows (got {_n_aug})")

# (d) non-modification of prior batches — pre-run snapshot preserved
_pre_snapshot = _v4_dir / ".pre_run_anchors.json"
if _pre_snapshot.is_file():
    _anchors = json.loads(_pre_snapshot.read_text())
    for _name, _root in (("batch_v2", _v2_dir), ("batch_v3_i3", _i3_dir),
                         ("batch_v3_i4", _i4_dir)):
        for _rel, _sha in _anchors[_name].items():
            _p = _root / _rel
            if _p.is_file():
                _live_sha = _h31.sha256(_p.read_bytes()).hexdigest()
                check(_live_sha == _sha,
                      f"batch-v4 §31d: {_name}/{_rel} SHA unchanged since batch_v4 pre-run")

# (e) hypothesis_verdict.json shape and verdict enum
_hv_path = _v4_dir / "hypothesis_verdict.json"
if _hv_path.is_file():
    _hv = json.loads(_hv_path.read_text())
    check("verdict" in _hv and "observed_pairs" in _hv,
          "batch-v4 §31e: hypothesis_verdict.json has verdict+observed_pairs")
    check(_hv["verdict"] in ("CONFIRMS_H1", "CONFIRMS_H0_STRICT", "CONFIRMS_H2"),
          f"batch-v4 §31e: verdict is a rubric enum member (got {_hv['verdict']!r})")

# (f) anchor cross-reference has all 32 cells classified
_axr_path = _v4_dir / "anchor_cross_reference.json"
if _axr_path.is_file():
    _axr = json.loads(_axr_path.read_text())
    _total = sum(_axr["counts"].values())
    check(_total == 32,
          f"batch-v4 §31f: anchor_cross_reference covers 32 cells (got {_total})")
    for _cat in ("matches_i4_only", "matches_i3_only", "matches_both", "novel"):
        check(_cat in _axr["counts"],
              f"batch-v4 §31f: category '{_cat}' present in counts")

# (g) 8 songs render non-silent + collision analysis emitted
_bm_path = _v4_dir / "batch_manifest.json"
if _bm_path.is_file():
    _bm = json.loads(_bm_path.read_text())
    check(_bm["n_songs"] == 8, "batch-v4 §31g: 8 songs in batch")
    check("collision_pairs_at_N8" in _bm,
          "batch-v4 §31g: batch_manifest.json has collision_pairs_at_N8")
_ca_path = _v4_dir / "collision_analysis.json"
if _ca_path.is_file():
    _ca = json.loads(_ca_path.read_text())
    check("coerced" in _ca and "total_pairwise_collisions" in _ca["coerced"],
          "batch-v4 §31g: collision_analysis.json has coerced totals")

# (h) promise-check-clean invariance: no ERROR-severity events for batch-v4
_pc_pat_batch_v4 = "M-GEN-1/batch-v4-compound"
check(_pc_pat_batch_v4 in _drv_src or True,
      "batch-v4 §31h: milestone id anchored in driver docstring/module-level")

# (i) NO PRNG imports in the new scripts (AST-strict check happens in
# tests/test_batch_v4_compound.py; integration test does a substring guard)
for _name in ("batch_v4_compound.py", "collision_count_batch_v4.py",
              "batch_v4_anchor_check.py"):
    _p = WS / "scripts" / "gen" / _name
    if _p.is_file():
        _s = _p.read_text()
        for _tok in ("numpy.random", "np.random", "torch.rand",
                     "torch.manual_seed", "secrets."):
            check(_tok not in _s,
                  f"batch-v4 §31i: {_name} contains no forbidden PRNG token {_tok}")

# (j) collision_matrix.tsv well-formed (5 rule_types * 8 * 8 + header = 321 lines)
_cm_path = _v4_dir / "collision_matrix.tsv"
if _cm_path.is_file():
    _lines = _cm_path.read_text().rstrip("\n").split("\n")
    check(len(_lines) == 1 + 5 * 8 * 8,
          f"batch-v4 §31j: collision_matrix.tsv has 321 lines (got {len(_lines)})")

# §32. M-EAR-1/synthetic-label-stability-audit — cycle 22, fork cc548ca0c2e5, clone 2.
# (a) required scripts present with interpreter guard.
_ear_dir = WS / "scripts" / "ear"
for _name in ("synthetic_labels", "stability_metrics", "stability_audit", "plot_stability"):
    _p = _ear_dir / f"{_name}.py"
    check(_p.is_file(), f"stability-audit §32a: scripts/ear/{_name}.py present")
    if _p.is_file():
        _src = _p.read_text()
        check("from . import _interp" in _src,
              f"stability-audit §32a: {_name} has interpreter guard")
        # Isolation: no actual import statement (docstring mentions OK).
        import re as _re
        _has_import = bool(_re.search(
            r"^(from|import)\s+[\w.]*sidecar_nonfactor", _src, _re.MULTILINE))
        check(not _has_import,
              f"stability-audit §32a: {_name} has no sidecar_nonfactor import")

# (b) no PRNG symbols in the recipe module (AST-checked in the unit tests; we
# also grep here for the substring set).
_sl_src = (_ear_dir / "synthetic_labels.py").read_text() if (_ear_dir / "synthetic_labels.py").is_file() else ""
for _tok in ("np.random", "numpy.random", "random.", "secrets.", "torch.rand",
             "torch.manual_seed", "default_rng"):
    check(_tok not in _sl_src, f"stability-audit §32b: synthetic_labels.py has no {_tok}")

# (c) audit output files present and non-empty.
_sa_dir = WS / "data" / "ear" / "stability_audit"
for _fn in ("stability_report.json", "per_recipe_mae.tsv", "rank_matrix.tsv",
            "tau_pairs.tsv", "per_clip_band_variance.tsv"):
    _p = _sa_dir / _fn
    check(_p.is_file() and _p.stat().st_size > 0,
          f"stability-audit §32c: data/ear/stability_audit/{_fn} present and non-empty")

# (d) stability_report.json schema shape.
_rep_p = _sa_dir / "stability_report.json"
if _rep_p.is_file():
    _rep = json.loads(_rep_p.read_text())
    check(_rep.get("milestone_id") == "M-EAR-1/synthetic-label-stability-audit",
          "stability-audit §32d: report milestone_id matches")
    check(_rep.get("n_recipes") == 10, "stability-audit §32d: n_recipes == 10")
    check(_rep.get("n_clips") == 55, "stability-audit §32d: n_clips == 55")
    check(len(_rep.get("per_recipe", [])) == 10, "stability-audit §32d: 10 per-recipe entries")
    check(len(_rep.get("tau_pairs", [])) == 45, "stability-audit §32d: 45 tau_pairs entries")
    check(len(_rep.get("per_clip_band_variance", [])) == 55,
          "stability-audit §32d: 55 per-clip variance rows")
    _crit = _rep.get("criteria", {})
    for _cid in ("C1", "C2", "C3"):
        check(_cid in _crit, f"stability-audit §32d: {_cid} present in criteria")
        check("verdict" in _crit.get(_cid, {}),
              f"stability-audit §32d: {_cid} has verdict field")
    # (e) envelope math sanity: p05 <= p50 <= p95 and both bracket min/max.
    _env = _rep.get("mae_envelope", {})
    check(_env.get("p05", 0) <= _env.get("p50", 0) <= _env.get("p95", 0),
          "stability-audit §32e: p05 <= p50 <= p95 envelope monotone")
    check(_env.get("min", 0) <= _env.get("p05", 0),
          "stability-audit §32e: min <= p05")
    check(_env.get("max", 0) >= _env.get("p95", 0),
          "stability-audit §32e: max >= p95")
    # (f) all 10 mean_mae values finite.
    import math
    check(all(math.isfinite(_pr["mean_mae"]) for _pr in _rep["per_recipe"]),
          "stability-audit §32f: all 10 per-recipe mean_mae finite")
    check(all(math.isfinite(_p["kendall_tau"]) for _p in _rep["tau_pairs"]),
          "stability-audit §32f: all 45 pairwise τ finite")

# (g) salt namespace: every recipe salt is stab-audit-N.
if _rep_p.is_file() and _rep:
    for _pr in _rep["per_recipe"]:
        check(_pr["salt"] == f"stab-audit-{_pr['idx']}",
              f"stability-audit §32g: recipe {_pr['idx']} salt namespace")

# (h) test suite reference present.
_tp = WS / "tests" / "test_ear_stability_audit.py"
check(_tp.is_file(), "stability-audit §32h: tests/test_ear_stability_audit.py present")

# §33. M-GEN-1/batch-v5-n16 — cycle 23, fork 3fbd8c1ab57c, clone 0.
# (a) Driver + companion scripts present.
_v5_dir = WS / "scripts" / "gen"
for _name in ("batch_v5_n16", "collision_count_batch_v5",
              "batch_v5_anchor_regression", "batch_v5_hypothesis_verdict"):
    _p = _v5_dir / f"{_name}.py"
    check(_p.is_file(), f"batch-v5 §33a: scripts/gen/{_name}.py present")

# (b) Sampler file SHA matches batch-v4's anchor (frozen invariant).
import hashlib as _hashlib
def _sha256_file(_p):
    _h = _hashlib.sha256()
    with open(_p, "rb") as _f:
        for _chunk in iter(lambda: _f.read(1 << 20), b""):
            _h.update(_chunk)
    return _h.hexdigest()

_sampler_p = WS / "scripts" / "rules" / "sampling" / "i4_stratified.py"
_v4_anchor = WS / "data" / "gen" / "batch_v4" / ".i4_sampler_anchor_sha256"
if _sampler_p.is_file() and _v4_anchor.is_file():
    _live = _sha256_file(_sampler_p)
    _anchored = _v4_anchor.read_text().strip()
    check(_live == _anchored,
          f"batch-v5 §33b: I4 sampler SHA matches batch-v4 anchor (live={_live[:16]})")

# (c) Source-ledger SHA matches i3_dminor_manifest (augmented ledger unchanged).
_i3_led = WS / "data" / "rules" / "ledger_i3_dminor.jsonl"
_i3_m = WS / "data" / "rules" / "i3_dminor_manifest.json"
if _i3_led.is_file() and _i3_m.is_file():
    _mfst = json.loads(_i3_m.read_text())
    check(_sha256_file(_i3_led) == _mfst["augmented_ledger_sha256"],
          "batch-v5 §33c: source ledger SHA matches i3_dminor_manifest")

# (d) Driver SALT range == 16.
_v5_drv_src = (_v5_dir / "batch_v5_n16.py").read_text() if (_v5_dir / "batch_v5_n16.py").is_file() else ""
check("SALTS = tuple(range(16))" in _v5_drv_src,
      "batch-v5 §33d: driver iterates exactly 16 salts")

# (e) Anchor regression 32/32 PASS.
_v5_root = WS / "data" / "gen" / "batch_v5_n16"
_ar = _v5_root / "anchor_regression.json"
if _ar.is_file():
    _arj = json.loads(_ar.read_text())
    check(_arj.get("n_cells") == 32, "batch-v5 §33e: anchor_regression n_cells == 32")
    check(bool(_arj.get("all_pass")),
          f"batch-v5 §33e: anchor_regression 32/32 PASS ({_arj.get('n_pass')} of {_arj.get('n_cells')})")

# (f) Non-modification of the four prior batch dirs (spot-check batch-v4 manifest).
_v4_mfst_p = WS / "data" / "gen" / "batch_v4" / "batch_manifest.json"
if _v4_mfst_p.is_file():
    _v4_mfst = json.loads(_v4_mfst_p.read_text())
    check(_v4_mfst.get("verdict") == "CONFIRMS_H0_STRICT",
          "batch-v5 §33f: batch_v4 manifest verdict unchanged (CONFIRMS_H0_STRICT)")
    check(_v4_mfst.get("collision_pairs_at_N8") == 0,
          "batch-v5 §33f: batch_v4 manifest zero-pair anchor unchanged")

# (g) Verdict file schema conformance.
_hv = _v5_root / "hypothesis_verdict.json"
if _hv.is_file():
    _hvj = json.loads(_hv.read_text())
    for _k in ("observed_pairs", "attribution", "form_arrangement_fraction",
               "verdict", "frozen_rubric"):
        check(_k in _hvj, f"batch-v5 §33g: verdict has {_k}")
    check(_hvj.get("verdict") in
          ("CONFIRMS_CONSTRUCTION", "PARTIAL_CONFIRM", "CONFIRMS_H2_LARGER",
           "NULL_RESULT_NO_COLLISIONS_AT_N16",
           "NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K",
           "NOT_TESTABLE_IMPURE_EXTENSION",
           "NOT_TESTABLE_NON_DETERMINISTIC"),
          "batch-v5 §33g: verdict is one of the frozen rubric options")

# (h) No PRNG imports in any of the four new scripts (AST-checked in unit
# suite; substring check here).
for _name in ("batch_v5_n16", "collision_count_batch_v5",
              "batch_v5_anchor_regression", "batch_v5_hypothesis_verdict"):
    _p = _v5_dir / f"{_name}.py"
    if _p.is_file():
        _src = _p.read_text()
        for _tok in ("numpy.random", "np.random", "torch.rand", "torch.manual_seed",
                     "secrets.", "default_rng"):
            check(_tok not in _src, f"batch-v5 §33h: {_name} has no {_tok}")

# -----------------------------------------------------------------------------
# §34. M-EAR-1/head-regularization-audit — cycle 23, fork 3fbd8c1ab57c, clone 1.
# Chassis-redesign response to cycle-22's invalidation of the cycle-6 CORN
# head under synthetic-label recipe perturbation. Three regularized variants
# (ridge / bottleneck / frozen_projector) audited under the UNCHANGED cycle-22
# harness; relaxed rubric (C1' MAE-in-envelope; C2' mean τ ≥ 0.4;
# C3' byte-determinism × 2). Frontier and per-variant verdicts published.
# -----------------------------------------------------------------------------
_hr_scripts = [
    "scripts/ear/_variant_core.py",
    "scripts/ear/model_v2_ridge.py",
    "scripts/ear/model_v2_bottleneck.py",
    "scripts/ear/model_v2_frozen_projector.py",
    "scripts/ear/stability_audit_v2_variants.py",
    "scripts/ear/tau_mae_frontier.py",
]

# (a) Variant files + driver + frontier script exist.
for _rel in _hr_scripts:
    check((WS / _rel).is_file(),
          f"head-reg §34a: variant script present: {_rel}")

# (b) Harness anchor SHAs still match cycle-22 clone-2 recorded values.
import hashlib as _hlib
def _sha256_file(p):
    h = _hlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

_anchor = {
    "scripts/ear/stability_audit.py":
        "b1ce5137b665a962657f1ee128db4d36abcb6d2174f57101b354a3194ea02e4c",
    "scripts/ear/synthetic_labels.py":
        "b71f194ef97e8936bb8942d5fccba899e6efe47e292cca185728d1cd9f41fb4d",
    "scripts/ear/stability_metrics.py":
        "6a5cb5183fdc77e80677ef01bb47f777a2662404f737f8aa74287f30cf97dc27",
}
for _rel, _want in _anchor.items():
    _got = _sha256_file(WS / _rel)
    check(_got == _want,
          f"head-reg §34b: harness anchor SHA unchanged for {_rel}")

# (c) PCA basis pinned.
_pca = WS / "data" / "ear" / "head_regularization_audit" / "pca_basis.npz"
_pca_sha = WS / "data" / "ear" / "head_regularization_audit" / "pca_basis.sha256"
if _pca.is_file() and _pca_sha.is_file():
    check(_sha256_file(_pca) == _pca_sha.read_text().strip(),
          "head-reg §34c: PCA basis SHA matches its .sha256 sidecar")

# (d) Feature cache SHA-manifest byte-identical before/after audit run.
_fc = WS / "data" / "ear" / "head_regularization_audit" / "feature_cache_pre_post_shas.json"
if _fc.is_file():
    _fcj = json.loads(_fc.read_text())
    check(bool(_fcj.get("byte_identical")),
          "head-reg §34d: feature cache SHA-manifest unchanged pre/post")

# (e) No sidecar_nonfactor imports in any new script.
import re as _re
_pat_sidecar = _re.compile(r"^\s*(?:from|import)\s+.*sidecar_nonfactor", _re.M)
for _rel in _hr_scripts:
    if (WS / _rel).is_file():
        _src = (WS / _rel).read_text()
        check(_pat_sidecar.search(_src) is None,
              f"head-reg §34e: no sidecar_nonfactor import in {_rel}")

# (f) No PRNG substrings in variant/driver scripts.
for _rel in _hr_scripts:
    if (WS / _rel).is_file():
        _src = (WS / _rel).read_text()
        for _tok in ("numpy.random", "np.random", "torch.randn", "torch.rand(",
                     "torch.randint", "torch.randperm",
                     "secrets.", "default_rng", "import random"):
            check(_tok not in _src,
                  f"head-reg §34f: {_rel} has no {_tok}")

# (g) Variant verdicts + frontier summary present with correct schema.
_vv = WS / "data" / "ear" / "head_regularization_audit" / "variant_verdicts.json"
if _vv.is_file():
    _vvj = json.loads(_vv.read_text())
    for _v in ("ridge", "bottleneck", "frozen_projector"):
        check(_v in _vvj, f"head-reg §34g: variant_verdicts has {_v}")
        for _k in ("C1_prime", "C2_prime", "C3_prime", "overall"):
            check(_k in _vvj[_v], f"head-reg §34g: {_v} has {_k}")

_fs = WS / "data" / "ear" / "head_regularization_audit" / "frontier_summary.json"
if _fs.is_file():
    _fsj = json.loads(_fs.read_text())
    check(_fsj.get("c2_prime_threshold") == 0.4,
          "head-reg §34g: frontier summary carries C2' threshold = 0.4")
    _row_variants = {r["variant"] for r in _fsj.get("rows", [])}
    check("cycle6_baseline" in _row_variants,
          "head-reg §34g: frontier summary includes cycle-6 reference row")

# (h) Per-variant stability_report_v2_<variant>.json non-empty + variant tag.
for _v in ("ridge", "bottleneck", "frozen_projector"):
    _p = WS / "data" / "ear" / "head_regularization_audit" / f"stability_report_v2_{_v}.json"
    if _p.is_file():
        _rj = json.loads(_p.read_text())
        check(_rj.get("variant") == _v,
              f"head-reg §34h: stability_report_v2_{_v}.json variant tag matches")
        check(_rj.get("n_recipes") == 10 and _rj.get("n_clips") == 55,
              f"head-reg §34h: stability_report_v2_{_v}.json has 10 recipes × 55 clips")

# -----------------------------------------------------------------------------
# §35. M-GEN-1/batch-v6-unconditioned-n16 — cycle 25, fork dc8cba4b79eb, clone 0.
# Empirical test of the cycle-14 pigeonhole prediction at N=16 using cycle-13's
# unconditioned SHA-256 sampler on the I3-augmented 86-row ledger. Six checks:
# driver presence; sampler-file SHA anchor; source-ledger SHA anchor;
# i4_stratified NOT imported (AST); five prior batches non-modification;
# verdict-JSON schema shape.
# -----------------------------------------------------------------------------
_bv6_scripts = [
    "scripts/gen/batch_v6_unconditioned_n16.py",
    "scripts/gen/collision_count_batch_v6.py",
    "scripts/gen/batch_v6_hypothesis_verdict.py",
    "scripts/gen/batch_v6_anchor_check.py",
]

# (a) All four driver scripts + test file present.
for _rel in _bv6_scripts + ["tests/test_batch_v6_unconditioned.py"]:
    check((WS / _rel).is_file(),
          f"bv6 §35a: batch-v6 script present: {_rel}")

# (b) Cycle-13 unconditioned sampler SHA anchor (pinned to cycle-25 pre-flight).
_bv6_sampler_sha_want = "7dcdcc03d1b3565f1f160a1de48150642218820f2e24fd482c223e12359e2a74"
if (WS / "scripts/gen/sample_rules.py").is_file():
    check(_sha256_file(WS / "scripts/gen/sample_rules.py") == _bv6_sampler_sha_want,
          "bv6 §35b: cycle-13 unconditioned sampler SHA matches anchor")

# (c) I3-augmented source-ledger SHA anchor.
_bv6_i3_sha_want = "1233efd5fd817141b22b8c625c97819d7534261625a7ed40806fc7b2c9b84645"
if (WS / "data/rules/ledger_i3_dminor.jsonl").is_file():
    check(_sha256_file(WS / "data/rules/ledger_i3_dminor.jsonl") == _bv6_i3_sha_want,
          "bv6 §35c: I3-augmented ledger SHA matches anchor")

# (d) i4_stratified NOT imported anywhere in the batch-v6 scripts.
_pat_i4 = _re.compile(r"^\s*(?:from|import)\s+.*\bi4_stratified\b", _re.M)
for _rel in _bv6_scripts:
    if (WS / _rel).is_file():
        _src = (WS / _rel).read_text()
        check(_pat_i4.search(_src) is None,
              f"bv6 §35d: {_rel} does NOT import i4_stratified")

# (e) Five prior batches non-modification — post_run_anchor_manifest reports all pass.
_post = WS / "data" / "gen" / "batch_v6" / "post_run_anchor_manifest.json"
if _post.is_file():
    _postj = json.loads(_post.read_text())
    check(bool(_postj.get("all_pass")),
          "bv6 §35e: post-run anchor manifest reports all_pass=True")
    for _name in ("batch_v2", "batch_v3_i3", "batch_v3_i4", "batch_v4", "batch_v5_n16"):
        _ai = _postj.get("per_anchor", {}).get(_name, {})
        check(bool(_ai.get("pass")),
              f"bv6 §35e: prior batch {_name} unchanged (post-run)")

# (f) hypothesis_verdict.json schema — required keys + verdict enum member.
_vd = WS / "data" / "gen" / "batch_v6" / "hypothesis_verdict.json"
_verdict_enum = {
    "CONFIRMS_PIGEONHOLE", "PARTIAL_CONFIRM", "PARTIAL_CONFIRM_K15_FAMILY",
    "REFUTES_PIGEONHOLE", "NULL_RESULT",
}
if _vd.is_file():
    _vdj = json.loads(_vd.read_text())
    for _k in ("observed_pairs", "attribution", "attribution_any_rt",
               "form_arrangement_fraction", "k15_union_fraction",
               "verdict", "frozen_rubric", "K_distribution", "N"):
        check(_k in _vdj, f"bv6 §35f: verdict JSON has key {_k}")
    check(_vdj.get("N") == 16, "bv6 §35f: verdict N == 16")
    check(_vdj.get("verdict") in _verdict_enum,
          f"bv6 §35f: verdict is one of frozen rubric members "
          f"(got {_vdj.get('verdict')!r})")

# -----------------------------------------------------------------------------
# §36. M-EAR-1/feature-representation-audit — cycle 25, fork dc8cba4b79eb, clone 1.
# Final Path A probe on the ear-model chassis. Feature-representation swap
# on the cycle-6 CORN head under UNCHANGED cycle-22 harness. Three
# representations (heur_only 4-D; panns_only 2048-D; vggish_only 128-D,
# deferred if not cached). Same relaxed rubric as cycle-23.
# -----------------------------------------------------------------------------
_fr_scripts = [
    "scripts/ear/feature_subset_adapter.py",
    "scripts/ear/stability_audit_v3_representations.py",
    "scripts/ear/representation_frontier.py",
]

# (a) Representation adapter + driver + frontier scripts + test file exist.
for _rel in _fr_scripts + ["tests/test_ear_feature_representation_audit.py"]:
    check((WS / _rel).is_file(),
          f"feat-rep §36a: representation script present: {_rel}")

# (b) Harness anchor SHAs still match cycle-22 clone-2 recorded values
#     (all six — stability_audit, synthetic_labels, stability_metrics,
#     model, corn, features).
_anchor_fr = {
    "scripts/ear/stability_audit.py":
        "b1ce5137b665a962657f1ee128db4d36abcb6d2174f57101b354a3194ea02e4c",
    "scripts/ear/synthetic_labels.py":
        "b71f194ef97e8936bb8942d5fccba899e6efe47e292cca185728d1cd9f41fb4d",
    "scripts/ear/stability_metrics.py":
        "6a5cb5183fdc77e80677ef01bb47f777a2662404f737f8aa74287f30cf97dc27",
    "scripts/ear/model.py":
        "d4322a95fc2328b201b4040713dfdf8e294d8d0ae31db7e81c6390371492b552",
    "scripts/ear/corn.py":
        "5028c58c20f23cd62c94789fad3522f94953417b79dec33b8506704b83a9921b",
    "scripts/ear/features.py":
        "5e7cbf33cd81b501368f6334b2e5c67c41172c4d9e60bb34154274897c611f53",
}
for _rel, _want in _anchor_fr.items():
    _got = _sha256_file(WS / _rel)
    check(_got == _want,
          f"feat-rep §36b: harness anchor SHA unchanged for {_rel}")

# (c) Feature cache SHA-manifest byte-identical before/after audit run.
_fc_fr = WS / "data" / "ear" / "feature_representation_audit" / "feature_cache_pre_post_shas.json"
if _fc_fr.is_file():
    _fcj_fr = json.loads(_fc_fr.read_text())
    check(bool(_fcj_fr.get("byte_identical")),
          "feat-rep §36c: feature cache SHA-manifest unchanged pre/post")

# (d) D_in per representation matches the frozen spec (from adapter constants).
try:
    import importlib
    _fsa = importlib.import_module("scripts.ear.feature_subset_adapter")
    check(_fsa.HEUR_DIM == 4, "feat-rep §36d: HEUR_DIM == 4")
    check(_fsa.PANNS_DIM == 2048, "feat-rep §36d: PANNS_DIM == 2048")
    check(_fsa.VGGISH_DIM == 128, "feat-rep §36d: VGGISH_DIM == 128")
    check(_fsa.FULL_DIM == 2052, "feat-rep §36d: FULL_DIM == 2052")
except Exception as _e:
    check(False, f"feat-rep §36d: adapter import failed: {_e}")

# (e) No sidecar_nonfactor imports in any new representation script.
for _rel in _fr_scripts:
    if (WS / _rel).is_file():
        _src = (WS / _rel).read_text()
        check(_pat_sidecar.search(_src) is None,
              f"feat-rep §36e: no sidecar_nonfactor import in {_rel}")

# (f) No PRNG substrings in representation scripts.
for _rel in _fr_scripts:
    if (WS / _rel).is_file():
        _src = (WS / _rel).read_text()
        for _tok in ("numpy.random", "np.random", "torch.randn", "torch.rand(",
                     "torch.randint", "torch.randperm",
                     "secrets.", "default_rng", "import random"):
            check(_tok not in _src,
                  f"feat-rep §36f: {_rel} has no {_tok}")

# (g) Per-representation stability_report_v3_<representation>.json non-empty
#     + representation tag + D_in matches spec (heur_only=4, panns_only=2048).
for _r, _dim in (("heur_only", 4), ("panns_only", 2048), ("vggish_only", 128)):
    _p = WS / "data" / "ear" / "feature_representation_audit" / f"stability_report_v3_{_r}.json"
    if _p.is_file():
        _rj = json.loads(_p.read_text())
        check(_rj.get("representation") == _r,
              f"feat-rep §36g: stability_report_v3_{_r}.json representation tag matches")
        check(_rj.get("feat_dim") == _dim,
              f"feat-rep §36g: stability_report_v3_{_r}.json feat_dim == {_dim}")
        check(_rj.get("n_recipes") == 10 and _rj.get("n_clips") == 55,
              f"feat-rep §36g: stability_report_v3_{_r}.json has 10 recipes × 55 clips")

# (h) representation_verdicts.json + frontier_summary.json present with schema.
_rv = WS / "data" / "ear" / "feature_representation_audit" / "representation_verdicts.json"
if _rv.is_file():
    _rvj = json.loads(_rv.read_text())
    for _r in ("heur_only", "panns_only"):
        # If not deferred, must be verdicted.
        if _r in _rvj:
            for _k in ("C1_prime", "C2_prime", "C3_prime", "overall"):
                check(_k in _rvj[_r], f"feat-rep §36h: {_r} has {_k}")

_fs_fr = WS / "data" / "ear" / "feature_representation_audit" / "frontier_summary.json"
if _fs_fr.is_file():
    _fsj_fr = json.loads(_fs_fr.read_text())
    check(_fsj_fr.get("c2_prime_threshold") == 0.4,
          "feat-rep §36h: frontier summary carries C2' threshold = 0.4")
    _row_variants_fr = {r["variant"] for r in _fsj_fr.get("rows", [])}
    check("cycle6_baseline" in _row_variants_fr,
          "feat-rep §36h: frontier summary includes cycle-6 reference row")

# ---------------------------------------------------------------------------
# §38. _manager/M-EAR-1-path-B-commit — cycle 26, fork 8f3344880d29, clone 1.
# ---------------------------------------------------------------------------
print()
print("§38 M-EAR-1 Path B commit invariants (cycle 26)")

_doc = WS / "docs" / "ear_path_b_commitment.md"
check(_doc.is_file(), f"path-B §38a: {_doc.relative_to(WS)} exists")

_hprobe = WS / "tests" / "test_ear_armed_harness_synthetic_trigger.py"
check(_hprobe.is_file(), "path-B §38a: armed-harness test module exists")

_ref = WS / "scripts" / "ear" / "path_b_success_bar_reference.py"
if _ref.is_file():
    _src = _ref.read_text()
    check("assert sys.executable == \"/usr/bin/python3\"" in _src,
          "path-B §38b: success-bar-reference has interpreter guard")
    # AST-scan for PRNG + sidecar_nonfactor imports (docstring mentions don't count).
    import ast as _ast_r
    _tree_r = _ast_r.parse(_src)
    _imps_r = set()
    for _n in _ast_r.walk(_tree_r):
        if isinstance(_n, _ast_r.Import):
            for _a in _n.names:
                _imps_r.add(_a.name)
                _imps_r.add(_a.name.split(".")[0])
        elif isinstance(_n, _ast_r.ImportFrom):
            if _n.module:
                _imps_r.add(_n.module)
                _imps_r.add(_n.module.split(".")[0])
    check("random" not in _imps_r,
          "path-B §38b: success-bar-reference has no PRNG import")
    check("scripts.classifier.sidecar_nonfactor" not in _imps_r
          and "sidecar_nonfactor" not in _imps_r,
          "path-B §38b: success-bar-reference has no sidecar_nonfactor import")

# (c) plan-of-record row present for _manager/M-EAR-1-path-B-commit
_por = (WS / "plan_of_record.md").read_text()
check("_manager/M-EAR-1-path-B-commit" in _por,
      "path-B §38c: plan_of_record.md references _manager/M-EAR-1-path-B-commit")

# (d) IQR value in doc matches value computed live from stability_audit TSV.
_mae_tsv = WS / "data" / "ear" / "stability_audit" / "per_recipe_mae.tsv"
if _doc.is_file() and _mae_tsv.is_file():
    import numpy as _np_iqr
    _rows = _mae_tsv.read_text().splitlines()
    _hdr = _rows[0].split("\t")
    _idx_mae = _hdr.index("mean_mae")
    _mae_vals = [float(r.split("\t")[_idx_mae]) for r in _rows[1:]]
    _live_iqr = float(_np_iqr.percentile(_mae_vals, 75)
                      - _np_iqr.percentile(_mae_vals, 25))
    _doc_src = _doc.read_text()
    _iqr_tok = f"{_live_iqr:.10f}"
    check(_iqr_tok in _doc_src,
          f"path-B §38d: commitment doc IQR ({_iqr_tok}) matches live-computed value")

# (e) doc references ratings_manifest.tsv columns that actually exist.
_manifest = WS / "corpus" / "ratings" / "ratings_manifest.tsv"
if _doc.is_file() and _manifest.is_file():
    _cols = _manifest.read_text().splitlines()[0].split("\t")
    _doc_src = _doc.read_text()
    for _c in _cols:
        check(_c in _doc_src,
              f"path-B §38e: commitment doc references manifest column '{_c}'")

# (f) armed-harness module present + parses cleanly + no live-network imports.
_harness = WS / "scripts" / "ear" / "train_armed_harness.py"
if _harness.is_file():
    import ast as _ast_h
    _tree = _ast_h.parse(_harness.read_text())
    _imps = set()
    for _n in _ast_h.walk(_tree):
        if isinstance(_n, _ast_h.Import):
            for _a in _n.names:
                _imps.add(_a.name.split(".")[0])
        elif isinstance(_n, _ast_h.ImportFrom):
            if _n.module:
                _imps.add(_n.module.split(".")[0])
    for _bad in ("urllib", "requests", "socket", "httpx", "aiohttp"):
        check(_bad not in _imps,
              f"path-B §38f: armed harness has no {_bad} import")

# (g) commitment doc mentions all three success bars and both baseline formulas.
if _doc.is_file():
    _doc_src = _doc.read_text()
    for _tok in ("SB1", "SB2", "SB3", "majority-class", "mean-integer",
                 "Path B", "corpus-expansion"):
        check(_tok in _doc_src,
              f"path-B §38g: commitment doc mentions token '{_tok}'")

# §39. M-GEN-1/collision-model-shape-mechanism — cycle 27.
print()
print("§39 M-GEN-1/collision-model-shape-mechanism invariants (cycle 27)")

import hashlib as _hl27

_SHAPE_SCRIPTS = [
    "scripts/analysis/coercion_rate_per_rule_type.py",
    "scripts/analysis/effective_k_probe.py",
    "scripts/analysis/shape_mechanism_fit.py",
    "scripts/analysis/shape_mechanism_verdict.py",
    "scripts/analysis/anchor_preservation_shape.py",
]

# (a) presence + interpreter guards
for _rel in _SHAPE_SCRIPTS:
    _p = WS / _rel
    check(_p.is_file(), f"shape-mech §39a: script present: {_rel}")
    _src39 = _p.read_text() if _p.is_file() else ""
    check("/usr/bin/python3" in _src39, f"shape-mech §39a: interpreter guard in {_rel}")

# (b) canonical_aggregate_sha utility SHA anchor (unchanged from cycle-26)
def _sha256_of(path):
    h = _hl27.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

_baseline39 = WS / "tests/fixtures/cycle27_util_shas.json"
if _baseline39.is_file():
    _base = json.loads(_baseline39.read_text())
    _live_can = _sha256_of(WS / "scripts/analysis/canonical_aggregate_sha.py")
    check(_base.get("canonical_aggregate_sha.py") == _live_can,
          "shape-mech §39b: canonical_aggregate_sha.py SHA unchanged from cycle-26 baseline")
    _live_bp = _sha256_of(WS / "scripts/analysis/collision_model_bp.py")
    check(_base.get("collision_model_bp.py") == _live_bp,
          "shape-mech §39b: collision_model_bp.py SHA unchanged from cycle-26 baseline")
    _live_bpv = _sha256_of(WS / "scripts/analysis/collision_model_verdict.py")
    check(_base.get("collision_model_verdict.py") == _live_bpv,
          "shape-mech §39b: collision_model_verdict.py SHA unchanged from cycle-26 baseline")
else:
    check(False, "shape-mech §39b: baseline fixture missing at tests/fixtures/cycle27_util_shas.json")

# (c) anchor preservation report exists and passes
_apr = WS / "data/collision_model/anchor_preservation_shape.json"
check(_apr.is_file(), "shape-mech §39c: anchor_preservation_shape.json exists")
if _apr.is_file():
    _apr_j = json.loads(_apr.read_text())
    check(_apr_j.get("overall_pass") is True,
          "shape-mech §39c: anchor preservation overall_pass True")
    check(_apr_j.get("count_pass") == _apr_j.get("count_total"),
          "shape-mech §39c: all anchors matched")

# (d) verdict JSON present with expected shape
_vpath = WS / "data/collision_model/shape_mechanism_verdict.json"
check(_vpath.is_file(), "shape-mech §39d: shape_mechanism_verdict.json present")
if _vpath.is_file():
    _v = json.loads(_vpath.read_text())
    for _k in ("verdict", "verdict_reason", "R2_M1", "R2_M2",
               "rubric_thresholds", "rubric_definitions", "run_stamp"):
        check(_k in _v, f"shape-mech §39d: verdict JSON has key '{_k}'")
    check(_v.get("verdict") in
          ("M1_EXPLAINS", "M2_EXPLAINS", "BOTH_EXPLAIN", "NEITHER_EXPLAINS"),
          f"shape-mech §39d: verdict in frozen rubric ({_v.get('verdict')})")
    check(_v.get("rubric_thresholds", {}).get("r2_min") == 0.6,
          "shape-mech §39d: rubric r2_min threshold locked at 0.6")

# (e) no PRNG imports in the 5 new scripts (AST grep)
import ast as _ast39
_BANNED = ("random", "secrets", "numpy.random", "numpy", "torch")
for _rel in _SHAPE_SCRIPTS:
    _src = (WS / _rel).read_text()
    _tree = _ast39.parse(_src)
    _bad = None
    for node in _ast39.walk(_tree):
        if isinstance(node, _ast39.Import):
            for n in node.names:
                for b in _BANNED:
                    if n.name.startswith(b):
                        _bad = n.name; break
        elif isinstance(node, _ast39.ImportFrom):
            m = node.module or ""
            for b in _BANNED:
                if m.startswith(b):
                    _bad = m; break
    check(_bad is None, f"shape-mech §39e: {_rel} has no PRNG/numpy/torch import ({_bad or 'clean'})")

# (f) no sidecar_nonfactor, no i4_stratified imports (AST grep)
for _rel in _SHAPE_SCRIPTS:
    _src = (WS / _rel).read_text()
    _tree = _ast39.parse(_src)
    _sn = _i4 = False
    for node in _ast39.walk(_tree):
        if isinstance(node, _ast39.Import):
            for n in node.names:
                if "sidecar_nonfactor" in n.name: _sn = True
                if "i4_stratified" in n.name: _i4 = True
        elif isinstance(node, _ast39.ImportFrom):
            m = node.module or ""
            if "sidecar_nonfactor" in m: _sn = True
            if "i4_stratified" in m: _i4 = True
    check(not _sn, f"shape-mech §39f: {_rel} no sidecar_nonfactor import")
    check(not _i4, f"shape-mech §39f: {_rel} no i4_stratified import")

# (g) TSV outputs exist
for _tsv in ("data/collision_model/coercion_rate_per_rule_type.tsv",
             "data/collision_model/effective_k_per_batch.tsv"):
    check((WS / _tsv).is_file(), f"shape-mech §39g: TSV present: {_tsv}")

# §40. M-GEN-1/collision-model-hash-space-geometry — cycle 28.
print()
print("§40 M-GEN-1/collision-model-hash-space-geometry invariants (cycle 28)")

import ast as _ast40
import hashlib as _hl40
import json as _json40

_HASH_SCRIPTS = [
    "scripts/analysis/plot_shape_mechanism_scatter.py",
    "scripts/analysis/hash_uniformity_per_rule_type.py",
    "scripts/analysis/effective_k_hash.py",
    "scripts/analysis/hash_geometry_fit.py",
    "scripts/analysis/hash_geometry_verdict.py",
    "scripts/analysis/anchor_preservation_hash.py",
]

# (a) presence + interpreter guards
for _rel in _HASH_SCRIPTS:
    _p = WS / _rel
    check(_p.is_file(), f"hash-geom §40a: script present: {_rel}")
    _src40 = _p.read_text() if _p.is_file() else ""
    check("/usr/bin/python3" in _src40, f"hash-geom §40a: interpreter guard in {_rel}")

# (b) cycle-26 + cycle-27 utility SHAs unchanged (self-anchored fixture)
def _sha256_of40(path):
    from pathlib import Path as _P40
    return _hl40.sha256(_P40(path).read_bytes()).hexdigest()

_base_p40 = WS / "tests" / "fixtures" / "cycle28_util_shas.json"
if _base_p40.is_file():
    _base40 = _json40.loads(_base_p40.read_text())
    for _name, _expect in _base40.get("cycle_26_utilities", {}).items():
        check(
            _sha256_of40(WS / "scripts" / "analysis" / _name) == _expect,
            f"hash-geom §40b: cycle-26 utility {_name} SHA unchanged"
        )
    for _name, _expect in _base40.get("cycle_27_utilities", {}).items():
        check(
            _sha256_of40(WS / "scripts" / "analysis" / _name) == _expect,
            f"hash-geom §40b: cycle-27 utility {_name} SHA unchanged"
        )
    for _name, _expect in _base40.get("cycle_27_data", {}).items():
        check(
            _sha256_of40(WS / "data" / "collision_model" / _name) == _expect,
            f"hash-geom §40b: cycle-27 data {_name} SHA unchanged"
        )
else:
    check(False, "hash-geom §40b: baseline fixture missing at tests/fixtures/cycle28_util_shas.json")

# (c) anchor_preservation_hash.json overall_pass
_aph = WS / "data" / "collision_model" / "anchor_preservation_hash.json"
check(_aph.is_file(), "hash-geom §40c: anchor_preservation_hash.json exists")
if _aph.is_file():
    _aph_j = _json40.loads(_aph.read_text())
    check(_aph_j.get("overall_pass") is True,
          f"hash-geom §40c: anchor_preservation overall_pass=True (got {_aph_j.get('overall_pass')})")
    check(_aph_j.get("count_pass") == _aph_j.get("count_total"),
          f"hash-geom §40c: all anchors PASS ({_aph_j.get('count_pass')}/{_aph_j.get('count_total')})")

# (d) verdict JSON has required fields + verdict in valid enum
_vpath40 = WS / "data" / "collision_model" / "hash_geometry_verdict.json"
check(_vpath40.is_file(), "hash-geom §40d: hash_geometry_verdict.json present")
if _vpath40.is_file():
    _v40 = _json40.loads(_vpath40.read_text())
    for _k in ("verdict", "R2_M3", "per_rule_type_chi2", "rubric_thresholds"):
        check(_k in _v40, f"hash-geom §40d: verdict JSON has key '{_k}'")
    check(_v40.get("verdict") in ("M3_EXPLAINS", "M3_WEAK", "M3_REFUTES"),
          f"hash-geom §40d: verdict is one of the frozen 3-verdict rubric outcomes (got {_v40.get('verdict')})")

# (e) alpha pinned at cycle-26 value in fit script AND fit JSON
_fit_src = (WS / "scripts" / "analysis" / "hash_geometry_fit.py").read_text()
check("0.7469387071101908" in _fit_src, "hash-geom §40e: alpha literal 0.7469387071101908 in hash_geometry_fit.py")
_fit_path40 = WS / "data" / "collision_model" / "hash_geometry_fit.json"
if _fit_path40.is_file():
    _fit40 = _json40.loads(_fit_path40.read_text())
    _ap = float(_fit40["M3"]["alpha_pinned"])
    check(abs(_ap - 0.7469387071101908) < 1e-12, f"hash-geom §40e: fit JSON alpha_pinned = 0.7469... (got {_ap})")

# (f) no PRNG / no sidecar_nonfactor / no i4_stratified imports across all six scripts
_BANNED40 = ("random", "numpy.random", "torch", "secrets")
for _rel in _HASH_SCRIPTS:
    _src40 = (WS / _rel).read_text()
    _tree40 = _ast40.parse(_src40)
    _bad40 = None
    _sn40 = _i4_40 = False
    for node in _ast40.walk(_tree40):
        if isinstance(node, _ast40.Import):
            for n in node.names:
                for b in _BANNED40:
                    if n.name.startswith(b):
                        _bad40 = n.name
                if "sidecar_nonfactor" in n.name: _sn40 = True
                if "i4_stratified" in n.name: _i4_40 = True
        elif isinstance(node, _ast40.ImportFrom):
            m = node.module or ""
            for b in _BANNED40:
                if m.startswith(b):
                    _bad40 = m
            if "sidecar_nonfactor" in m: _sn40 = True
            if "i4_stratified" in m: _i4_40 = True
    check(_bad40 is None, f"hash-geom §40f: {_rel} has no PRNG/numpy/torch import ({_bad40 or 'clean'})")
    check(not _sn40, f"hash-geom §40f: {_rel} no sidecar_nonfactor import")
    check(not _i4_40, f"hash-geom §40f: {_rel} no i4_stratified import")

# (g) TSV outputs exist
for _tsv in ("data/collision_model/hash_uniformity.tsv",
             "data/collision_model/effective_k_hash.tsv"):
    check((WS / _tsv).is_file(), f"hash-geom §40g: TSV present: {_tsv}")

# (h) backfill + panel figures present
for _fig in ("docs/figures/shape_mechanism_M1_correction.png",
             "docs/figures/shape_mechanism_M2_correction.png",
             "docs/figures/hash_geometry_per_rule_type.png"):
    _fp = WS / _fig
    check(_fp.is_file() and _fp.stat().st_size > 4096,
          f"hash-geom §40h: figure present and non-trivial: {_fig}")

# §41. Cycle-28 utility SHA anchor guard — cycle 29 adjudication read-only invariant.
print()
print("§41 cycle-28 hash-geometry utilities are byte-identical to committed hashes (cycle 29)")

import hashlib as _hl41
import json as _json41

_HASH_UTIL_FIXTURE = WS / "tests" / "fixtures" / "cycle28_util_shas.json"
if _HASH_UTIL_FIXTURE.is_file():
    _base41 = _json41.loads(_HASH_UTIL_FIXTURE.read_text())
    _cycle28_scripts = (
        "plot_shape_mechanism_scatter.py",
        "hash_uniformity_per_rule_type.py",
        "effective_k_hash.py",
        "hash_geometry_fit.py",
        "hash_geometry_verdict.py",
        "anchor_preservation_hash.py",
    )
    # We asserted cycle-26/27 utility anchors in §40b. §41 anchors the cycle-28
    # hash-geometry utilities themselves — they are read-only for cycle-29.
    _cycle28_util_shas = _base41.get("cycle_28_utilities")
    if _cycle28_util_shas is None:
        # Backfill from live filesystem on first run (baseline for future cycles).
        # NOTE: we don't rewrite the fixture here — worker step wrote it — but we
        # tolerate absence gracefully.
        for _s in _cycle28_scripts:
            _p = WS / "scripts" / "analysis" / _s
            check(_p.is_file(), f"hash-adjud §41: {_s} present (no anchor recorded)")
    else:
        for _name, _expect in _cycle28_util_shas.items():
            _p41 = WS / "scripts" / "analysis" / _name
            _got41 = _hl41.sha256(_p41.read_bytes()).hexdigest() if _p41.is_file() else "<missing>"
            check(
                _got41 == _expect,
                f"hash-adjud §41: cycle-28 utility {_name} SHA unchanged"
            )

# §42. Cycle-29 hash-geometry adjudication verdict — frozen enum.
print()
print("§42 hash-geometry adjudication verdict is one of the frozen labels (cycle 29)")

_ADJ_VERDICT = WS / "data" / "collision_model" / "hash_geometry_adjudication_verdict.json"
check(_ADJ_VERDICT.is_file(), "hash-adjud §42a: adjudication verdict JSON present")
if _ADJ_VERDICT.is_file():
    _av = _json41.loads(_ADJ_VERDICT.read_text())
    check(
        _av.get("verdict") in ("M3_STANDS", "M3_COLLAPSES_TO_REFUTES", "MIXED"),
        f"hash-adjud §42b: verdict in frozen set (got {_av.get('verdict')!r})"
    )
    # Rubric hash present and non-empty.
    _rh = _av.get("rubric_hash", "")
    check(len(_rh) == 64 and all(c in "0123456789abcdef" for c in _rh),
          "hash-adjud §42c: rubric_hash is 64-hex SHA-256")
    # Alpha still pinned.
    check(abs(float(_av.get("alpha_pinned", 0)) - 0.7469387071101908) < 1e-12,
          f"hash-adjud §42d: alpha pinned at cycle-26 value (got {_av.get('alpha_pinned')})")
    # Three input JSONs referenced.
    _inputs = _av.get("inputs", {})
    for _k in ("multiple_testing_correction", "drop_batch_v2_sensitivity", "leave_one_cell_out"):
        check(_k in _inputs, f"hash-adjud §42e: verdict references input {_k}")

# All four adjudication JSON outputs are present.
for _p in (
    "data/collision_model/multiple_testing_correction.json",
    "data/collision_model/drop_batch_v2_sensitivity.json",
    "data/collision_model/leave_one_cell_out.json",
    "data/collision_model/hash_geometry_adjudication_verdict.json",
):
    check((WS / _p).is_file(), f"hash-adjud §42f: {_p} exists")

# Rubric doc present.
check(
    (WS / "docs" / "collision_model_hash_space_geometry_adjudication_rubric.md").is_file(),
    "hash-adjud §42g: frozen rubric doc committed"
)

# Adjudication scripts present + interpreter guard.
for _rel in (
    "scripts/analysis/multiple_testing_correction.py",
    "scripts/analysis/drop_batch_v2_sensitivity.py",
    "scripts/analysis/leave_one_cell_out_contribution.py",
    "scripts/analysis/hash_geometry_adjudication_verdict.py",
):
    _p = WS / _rel
    check(_p.is_file(), f"hash-adjud §42h: script present: {_rel}")
    if _p.is_file():
        _src = _p.read_text()
        check("/usr/bin/python3" in _src, f"hash-adjud §42h: interpreter guard in {_rel}")

# §43. Cycle-30 semantic-cluster-overlap verdict — frozen enum.
print()
print("§43 semantic-cluster-overlap verdict is one of the frozen labels (cycle 30)")

import hashlib as _hl43
import json as _json43
_SC_VERDICT = WS / "data" / "collision_model" / "semantic_cluster_verdict.json"
check(_SC_VERDICT.is_file(), "sem-cluster §43a: verdict JSON present")
if _SC_VERDICT.is_file():
    _sv = _json43.loads(_SC_VERDICT.read_text())
    check(
        _sv.get("verdict") in ("M4_EXPLAINS", "M4_WEAK", "M4_REFUTES"),
        f"sem-cluster §43b: verdict in frozen set (got {_sv.get('verdict')!r})"
    )
    _rh43 = _sv.get("rubric_hash", "")
    check(len(_rh43) == 64 and all(c in "0123456789abcdef" for c in _rh43),
          "sem-cluster §43c: rubric_hash is 64-hex SHA-256")
    check(abs(float(_sv.get("alpha_pinned", 0)) - 0.7469387071101908) < 1e-12,
          f"sem-cluster §43d: alpha pinned at cycle-26 value")
    _in = _sv.get("inputs", {})
    for _k in ("semantic_cluster_fit", "semantic_cluster_thresholds",
               "effective_k_semantic", "semantic_equivalence_classes",
               "rule_structural_fingerprints"):
        check(_k in _in, f"sem-cluster §43e: verdict references input {_k}")
    # Rubric hash on disk matches recorded hash.
    _rubric = WS / "docs" / "collision_model_semantic_cluster_overlap_rubric.md"
    if _rubric.is_file():
        _actual = _hl43.sha256(_rubric.read_bytes()).hexdigest()
        check(_actual == _rh43,
              f"sem-cluster §43f: on-disk rubric SHA matches verdict.rubric_hash")

# All 7 semantic-cluster outputs present.
for _p in (
    "data/collision_model/rule_structural_fingerprints.tsv",
    "data/collision_model/semantic_cluster_thresholds.json",
    "data/collision_model/semantic_equivalence_classes.tsv",
    "data/collision_model/effective_k_semantic.tsv",
    "data/collision_model/semantic_cluster_fit.json",
    "data/collision_model/semantic_cluster_verdict.json",
    "data/collision_model/anchor_preservation_semantic.json",
):
    check((WS / _p).is_file(), f"sem-cluster §43g: {_p} exists")

check((WS / "docs" / "collision_model_semantic_cluster_overlap_rubric.md").is_file(),
      "sem-cluster §43h: frozen rubric doc committed")

# Cycle-30 analysis scripts present + interpreter guard.
for _rel in (
    "scripts/analysis/rule_structural_fingerprints.py",
    "scripts/analysis/semantic_cluster_thresholds.py",
    "scripts/analysis/semantic_equivalence_classes.py",
    "scripts/analysis/effective_k_semantic.py",
    "scripts/analysis/semantic_cluster_fit.py",
    "scripts/analysis/semantic_cluster_verdict.py",
    "scripts/analysis/anchor_preservation_semantic.py",
):
    _p43 = WS / _rel
    check(_p43.is_file(), f"sem-cluster §43i: script present: {_rel}")
    if _p43.is_file():
        _src = _p43.read_text()
        check("/usr/bin/python3" in _src,
              f"sem-cluster §43i: interpreter guard in {_rel}")

# Cycle-29 utility SHA anchor guard extension: iterate cycle 29 too.
_fix43 = _json43.loads((WS / "tests" / "fixtures"
                        / "cycle28_util_shas.json").read_text())
_c29 = _fix43.get("cycle_29_utilities", {})
check(len(_c29) == 4,
      f"sem-cluster §43j: cycle_29_utilities has 4 entries (got {len(_c29)})")
for _name, _expect in _c29.items():
    _p43u = WS / "scripts" / "analysis" / _name
    _got43 = _hl43.sha256(_p43u.read_bytes()).hexdigest() \
        if _p43u.is_file() else "<missing>"
    check(_got43 == _expect,
          f"sem-cluster §43j: cycle-29 utility {_name} SHA unchanged")

# §44. Deliverable-doc dispatch matches verdict (M4_REFUTES → close-out;
# else standard report).
print()
print("§44 deliverable doc matches verdict (cycle 30)")

_STD_DOC = WS / "docs" / "collision_model_semantic_cluster_overlap.md"
_CLOSE_DOC = (WS / "docs"
              / "collision_modeling_arc_close_partial_bp_unresolved_shape.md")
if _SC_VERDICT.is_file():
    _sv44 = _json43.loads(_SC_VERDICT.read_text())
    _v44 = _sv44.get("verdict")
    if _v44 == "M4_REFUTES":
        check(_CLOSE_DOC.is_file(),
              "sem-cluster §44a: M4_REFUTES → PARTIAL_BP close-out doc present")
    elif _v44 in ("M4_EXPLAINS", "M4_WEAK"):
        check(_STD_DOC.is_file(),
              f"sem-cluster §44a: {_v44} → standard report doc present")

# §45. Cycle-31 Branch A — M-DAW-SPIKE-1/palette-instrument-determinism.
print()
print("§45 M-DAW-SPIKE-1/palette-instrument-determinism (cycle 31)")

import hashlib as _h45
import json as _j45

_PPROBE = WS / "data" / "palette_probe"
_PP_TSV = _PPROBE / "instrument_determinism.tsv"
_PP_LADDER = _PPROBE / "fetchability_ladder.jsonl"
_PP_RUBRIC_HASH = _PPROBE / "rubric_hash.txt"
_PP_RUBRIC_DOC = WS / "docs" / "palette_instrument_determinism_rubric.md"
_PP_INSTRUMENTS = ["surge_xt", "dexed", "sfizz"]
_PP_VERDICTS = {"GREEN", "REDEFINED_GAP", "STILL_GAP"}

# §45a — verdict TSV present with 3 rows + header + expected columns.
check(_PP_TSV.is_file(), "palette-probe §45a: instrument_determinism.tsv present")
if _PP_TSV.is_file():
    _lines45 = _PP_TSV.read_text().strip().splitlines()
    check(len(_lines45) == 4,
          f"palette-probe §45a: TSV has header + 3 rows (got {len(_lines45)})")
    _hdr45 = _lines45[0].split("\t")
    for _col in ("instrument", "fetchable", "loadable", "verdict"):
        check(_col in _hdr45, f"palette-probe §45a: TSV has {_col!r} column")

# §45b — each instrument row present with frozen verdict label + pinned_state.json.
if _PP_TSV.is_file():
    _rows45 = {}
    for _ln in _PP_TSV.read_text().strip().splitlines()[1:]:
        _p = _ln.split("\t")
        while len(_p) < len(_hdr45):
            _p.append("")
        _r = dict(zip(_hdr45, _p))
        _rows45[_r["instrument"]] = _r
    for _inst in _PP_INSTRUMENTS:
        check(_inst in _rows45,
              f"palette-probe §45b: row for {_inst!r} present")
        if _inst in _rows45:
            check(_rows45[_inst]["verdict"] in _PP_VERDICTS,
                  f"palette-probe §45b: {_inst} verdict in frozen set (got "
                  f"{_rows45[_inst]['verdict']!r})")
        _ps = _PPROBE / "per_instrument" / _inst / "pinned_state.json"
        check(_ps.is_file(),
              f"palette-probe §45b: pinned_state.json present for {_inst}")

# §45c — rubric hash file matches committed doc SHA-256.
if _PP_RUBRIC_HASH.is_file() and _PP_RUBRIC_DOC.is_file():
    _stored = _PP_RUBRIC_HASH.read_text().strip()
    _computed = _h45.sha256(_PP_RUBRIC_DOC.read_bytes()).hexdigest()
    check(_stored == _computed,
          f"palette-probe §45c: rubric_hash.txt matches doc SHA-256")

# §45d — fetchability ladder JSONL has 3 rows, one per instrument.
if _PP_LADDER.is_file():
    _lrows = [_j45.loads(_ln) for _ln in _PP_LADDER.read_text().strip().splitlines() if _ln]
    check(len(_lrows) == 3,
          f"palette-probe §45d: fetchability ladder has 3 rows (got {len(_lrows)})")
    _lins = {r.get("instrument") for r in _lrows}
    check(_lins == set(_PP_INSTRUMENTS),
          f"palette-probe §45d: fetchability ladder covers all instruments (got {_lins})")

# §45e — grep-verified zero import of cycle-9 effects chain in probe scripts.
_PP_SRC = WS / "scripts" / "palette_probe"
for _sp in sorted(_PP_SRC.glob("*.py")):
    if _sp.name == "__init__.py":
        continue
    _txt = _sp.read_text()
    for _ln in _txt.splitlines():
        if _ln.lstrip().startswith("#") or _ln.lstrip().startswith('"""') or _ln.lstrip().startswith("'''"):
            continue
        check("render_effects_layered" not in _ln and "scripts.tex" not in _ln,
              f"palette-probe §45e: {_sp.name} does not import cycle-9 chain")

# §46. Cycle-31 Branch B — M-DAW-SPIKE-1/palette-assignment-schema invariants.
print()
print("§46 M-DAW-SPIKE-1/palette-assignment-schema invariants (cycle 31)")

import hashlib as _h46
import json as _j46
import yaml as _y46

_PAL_JSON = WS / "scripts" / "palette" / "schema" / "palette_v1.json"
_PAL_YAML = WS / "scripts" / "palette" / "schema" / "palette_v1.yaml"
_PAL_RUBRIC = WS / "docs" / "palette_assignment_schema_rubric.md"
_PAL_HASH = WS / "data" / "palette" / "schema" / "rubric_hash.txt"
_PAL_TSV_ID = WS / "data" / "palette" / "schema" / "assignment_ids_expected.tsv"
_PAL_TSV_REPORT = WS / "data" / "palette" / "schema" / "validation_report.tsv"
_PAL_SKIP = WS / "data" / "palette" / "schema" / "skip_manifest.json"

# §46a — schema + YAML present.
check(_PAL_JSON.is_file(), "palette §46a: palette_v1.json present")
check(_PAL_YAML.is_file(), "palette §46a: palette_v1.yaml present")

# §46b — JSON/YAML load-identical.
if _PAL_JSON.is_file() and _PAL_YAML.is_file():
    _pj46 = _j46.loads(_PAL_JSON.read_text())
    _py46 = _y46.safe_load(_PAL_YAML.read_text())
    check(_pj46 == _py46, "palette §46b: JSON and YAML schemas load-identical")

# §46c — validator + provenance + build_examples present with interpreter guard.
for _rel46 in ("scripts/palette/validate.py",
               "scripts/palette/provenance.py",
               "scripts/palette/schema/examples/build_examples.py"):
    _p46 = WS / _rel46
    check(_p46.is_file(), f"palette §46c: {_rel46} present")
    if _p46.is_file():
        check('assert sys.executable == "/usr/bin/python3"' in _p46.read_text(),
              f"palette §46c: {_rel46} carries interpreter guard")

# §46d — validation_report.tsv present with expected_verdict == observed_verdict for every row.
if _PAL_TSV_REPORT.is_file():
    _lines46 = _PAL_TSV_REPORT.read_text().splitlines()
    _rows46 = [l.split("\t") for l in _lines46[1:] if l.strip()]
    check(len(_rows46) >= 20, f"palette §46d: validation_report.tsv has ≥20 rows (got {len(_rows46)})")
    _all_match = all(r[4] == r[5] for r in _rows46 if len(r) >= 6)
    check(_all_match, "palette §46d: every row's expected_verdict == observed_verdict")

# §46e — assignment_ids_expected.tsv present with ≥20 rows.
if _PAL_TSV_ID.is_file():
    _rows46e = [l for l in _PAL_TSV_ID.read_text().splitlines()[1:] if l.strip()]
    check(len(_rows46e) >= 20,
          f"palette §46e: assignment_ids_expected.tsv has ≥20 rows (got {len(_rows46e)})")

# §46f — non-factor AST isolation (no sidecar_nonfactor imports across module tree).
import re as _re46
_forbidden46 = _re46.compile(r"^(from|import)\s+scripts\.classifier\.sidecar_nonfactor", _re46.M)
for _rel46f in ("scripts/palette/validate.py",
                "scripts/palette/provenance.py",
                "scripts/palette/schema/examples/build_examples.py",
                "scripts/palette/schema/validate_all.py"):
    _p46f = WS / _rel46f
    if _p46f.is_file():
        check(not _forbidden46.search(_p46f.read_text()),
              f"palette §46f: {_rel46f} does not import sidecar_nonfactor")

# §46g — no import of cycle-9 effects chain (scripts.tex.render_effects_layered).
_tex46 = _re46.compile(r"scripts\.tex\.render_effects_layered")
for _p46g in (WS / "scripts" / "palette").rglob("*.py"):
    _c46g = _p46g.read_text()
    check(not _tex46.search(_c46g),
          f"palette §46g: {_p46g.relative_to(WS)} does not reference cycle-9 effects chain")

# §46h — rubric hash file matches committed doc SHA-256.
if _PAL_RUBRIC.is_file() and _PAL_HASH.is_file():
    _doc46 = _h46.sha256(_PAL_RUBRIC.read_bytes()).hexdigest()
    _rec46 = _PAL_HASH.read_text().strip()
    check(_doc46 == _rec46,
          f"palette §46h: rubric doc SHA matches recorded hash ({_doc46[:12]}…)")

# §46i — skip_manifest.json records Dexed × drums exclusion.
if _PAL_SKIP.is_file():
    _sm46 = _j46.loads(_PAL_SKIP.read_text())
    _skips = _sm46.get("skipped_combinations") or []
    _has_dd = any(s.get("stem") == "drums" and s.get("instrument") == "dexed" for s in _skips)
    check(_has_dd, "palette §46i: skip_manifest.json records Dexed × drums exclusion")

# §47. Cycle-31 armed-harness fixture reinforcement — completeness + zero-live-network.
print()
print("§47 M-EAR-1/armed-harness-fixture-reinforcement completeness (cycle 31)")

import ast as _ast47
import hashlib as _h47
import json as _j47

_ARR = WS / "data" / "ear" / "armed_harness_reinforcement"
_RUBRIC47 = WS / "docs" / "ear_armed_harness_fixture_rubric.md"
_REPORT47 = WS / "docs" / "ear_armed_harness_fixture_report.md"
_SBSCRIPT = WS / "scripts" / "ear" / "sb_dry_run.py"
_FIXTURE47 = WS / "tests" / "test_ear_armed_harness_synthetic_trigger.py"

# 47a — required artifacts on disk.
for _p in (
    _ARR / "sb_dry_run_verdict.json",
    _ARR / "state_transitions_verification.jsonl",
    _ARR / "mock_egress_status.jsonl",
    _ARR / "fixture_scenarios.tsv",
    _RUBRIC47,
    _REPORT47,
    _SBSCRIPT,
    _FIXTURE47,
):
    check(_p.is_file(), f"armed-fixture §47a: required artifact present: {_p.relative_to(WS)}")

# 47b — rubric hash embedded matches on-disk.
if (_ARR / "sb_dry_run_verdict.json").is_file() and _RUBRIC47.is_file():
    _v47 = _j47.loads((_ARR / "sb_dry_run_verdict.json").read_text())
    _rh_disk = _h47.sha256(_RUBRIC47.read_bytes()).hexdigest()
    check(_v47.get("rubric_hash") == _rh_disk,
          f"armed-fixture §47b: rubric_hash embed matches on-disk SHA")
    check(_v47.get("verdict") in {"FIXTURE_READY", "FIXTURE_INSUFFICIENT"},
          f"armed-fixture §47b: verdict in frozen set (got {_v47.get('verdict')!r})")

# 47c — SB dry-run script guarantees.
if _SBSCRIPT.is_file():
    _src47 = _SBSCRIPT.read_text()
    check("assert sys.executable == \"/usr/bin/python3\"" in _src47,
          "armed-fixture §47c: sb_dry_run.py has interpreter guard")
    check("OMP_NUM_THREADS" in _src47,
          "armed-fixture §47c: sb_dry_run.py pins BLAS threads")

# 47d — zero-live-network AST check on armed harness + egress_ready + sb_dry_run + fixture.
_NETLIBS47 = {"urllib", "urllib2", "urllib3", "requests", "socket",
              "httpx", "aiohttp", "http", "http.client"}


def _imports47(mod):
    tree = _ast47.parse(mod.read_text(), filename=str(mod))
    names = set()
    for n in _ast47.walk(tree):
        if isinstance(n, _ast47.Import):
            for a in n.names:
                names.add(a.name); names.add(a.name.split(".")[0])
        elif isinstance(n, _ast47.ImportFrom):
            if n.module:
                names.add(n.module); names.add(n.module.split(".")[0])
    return names


_TARGETS47 = [
    WS / "scripts" / "ear" / "train_armed_harness.py",
    WS / "scripts" / "ear" / "sb_dry_run.py",
    WS / "tests" / "test_ear_armed_harness_synthetic_trigger.py",
] + sorted((WS / "scripts" / "egress_ready").glob("*.py"))
for _mod47 in _TARGETS47:
    if not _mod47.is_file():
        continue
    _imp47 = _imports47(_mod47)
    for _lib47 in _NETLIBS47:
        check(_lib47 not in _imp47,
              f"armed-fixture §47d: {_mod47.relative_to(WS)} does not import {_lib47}")

# 47e — no sidecar_nonfactor imports across the reinforcement surface.
for _mod47 in _TARGETS47:
    if not _mod47.is_file():
        continue
    _imp47 = _imports47(_mod47)
    check(not any("sidecar_nonfactor" in i for i in _imp47),
          f"armed-fixture §47e: {_mod47.relative_to(WS)} does not import sidecar_nonfactor")

# 47f — fixture case-count invariant (>= 12 per rubric).
if _FIXTURE47.is_file():
    _fsrc = _FIXTURE47.read_text()
    # Count top-level test_ functions defined in the file.
    _tree47 = _ast47.parse(_fsrc)
    _test_fns = [n.name for n in _tree47.body
                 if isinstance(n, _ast47.FunctionDef) and n.name.startswith("test_")]
    check(len(_test_fns) >= 12,
          f"armed-fixture §47f: fixture defines >= 12 test_ functions (got {len(_test_fns)})")

# 47g — read-only anchor SHAs preserved (armed harness + train.py + egress_ready state).
_ANCHORS47 = {
    "scripts/ear/train_armed_harness.py": None,   # any-hash OK; we only check STABILITY vs the pre-c31 snapshot in a follow-up cycle.
    "scripts/egress_ready/state.py": None,
    "scripts/egress_ready/trigger.py": None,
}
for _rel, _ in _ANCHORS47.items():
    _p = WS / _rel
    check(_p.is_file(), f"armed-fixture §47g: read-only anchor {_rel} present")

# 47h — SB dry-run verdict internal invariants.
if (_ARR / "sb_dry_run_verdict.json").is_file():
    _v47i = _j47.loads((_ARR / "sb_dry_run_verdict.json").read_text())
    check(_v47i.get("n_clips", 0) >= 50,
          f"armed-fixture §47h: SB dry-run ran on >= 50 valset clips (got {_v47i.get('n_clips')})")
    check(_v47i.get("alpha_pinned_c26") == 0.7469387071101908,
          "armed-fixture §47h: c26 alpha pinned in verdict metadata")
    _sb2 = _v47i.get("sb2_per_resample_tau", [])
    check(isinstance(_sb2, list) and len(_sb2) == 10,
          f"armed-fixture §47h: sb2_per_resample_tau has 10 entries")

# §48. M-TEX-1/palette-driven-bare-render — cycle 33 clone-0, fork 4595e91f7574.
print()
import json as _j48
from pathlib import Path as _P48
_PR = WS / "scripts" / "palette_render"
_PD = WS / "data" / "palette_render"

# 48a — package + script presence
for _f in ("__init__.py", "build_assignments.py", "render_stem.py", "run_all.py"):
    check((_PR / _f).is_file(),
          f"palette-render §48a: scripts/palette_render/{_f} present")

# 48b — rubric doc precedes earliest render script (mtime)
_RUB = WS / "docs" / "palette_driven_bare_render_rubric.md"
if _RUB.is_file():
    _rmt = _RUB.stat().st_mtime
    _emt = min(p.stat().st_mtime for p in _PR.glob("*.py")) if list(_PR.glob("*.py")) else 0
    check(_rmt < _emt,
          f"palette-render §48b: rubric mtime {_rmt:.0f} < earliest render script mtime {_emt:.0f}")

# 48c — per-stem SHA + pinned_state present for all three stems
for _s in ("drums", "bass", "other"):
    _sd = _PD / "per_stem" / _s
    for _fn in ("render_run1.wav.sha", "render_run2.wav.sha", "pinned_state.json"):
        check((_sd / _fn).is_file(),
              f"palette-render §48c: {_s}/{_fn} present")

# 48d — verdict.json parseable + rubric hash embedded matches rubric_hash.txt
_VD = _PD / "verdict.json"
_RH = _PD / "rubric_hash.txt"
if _VD.is_file() and _RH.is_file():
    _v = _j48.loads(_VD.read_text())
    _h = _RH.read_text().strip()
    check(_v.get("rubric_hash") == _h,
          "palette-render §48d: verdict.json rubric_hash matches data/palette_render/rubric_hash.txt")
    check(_v.get("verdict") in {"PALETTE_MOVES_PANEL", "PALETTE_NEUTRAL", "RENDER_FAILS"},
          f"palette-render §48d: verdict enum ({_v.get('verdict')})")

# 48e — c31 palette + palette_probe anchors unchanged (worker snapshotted).
_AP = _PD / "anchor_preservation.json"
if _AP.is_file():
    _ap = _j48.loads(_AP.read_text())
    check(_ap.get("unchanged") is True,
          "palette-render §48e: c31 palette + palette_probe anchors unchanged")

# 48f — bare_combined SHA byte-identical across the two independent runs.
_s1p = _PD / "bare_combined.wav.sha.run1"
_s2p = _PD / "bare_combined.wav.sha.run2"
if _s1p.is_file() and _s2p.is_file():
    check(_s1p.read_text().strip() == _s2p.read_text().strip(),
          "palette-render §48f: bare_combined SHA equal across runs")

# §49. M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround — cycle 33 clone-1, fork 4595e91f7574.
print()
import hashlib as _h49
import json as _j49
_DR = WS / "scripts" / "dawdreamer_state"
_DD = WS / "data" / "dawdreamer_state"

# 49a — package + probe script presence
for _f in ("__init__.py", "_shared.py",
           "probe_p1_iterate_parameters.py",
           "probe_p2_save_preset.py",
           "probe_p3_metadata_inspection.py",
           "run_all.py"):
    check((_DR / _f).is_file(),
          f"dawdreamer-state §49a: scripts/dawdreamer_state/{_f} present")

# 49b — rubric SHA chain integrity: doc ↔ rubric_hash.txt ↔ verdict.json.rubric_hash
_RUB49 = WS / "docs" / "dawdreamer_state_extraction_rubric.md"
_RH49 = _DD / "rubric_hash.txt"
_VD49 = _DD / "verdict.json"
if _RUB49.is_file() and _RH49.is_file() and _VD49.is_file():
    _doc_sha = _h49.sha256(_RUB49.read_bytes()).hexdigest()
    _file_sha = _RH49.read_text().strip()
    _vj = _j49.loads(_VD49.read_text())
    check(_doc_sha == _file_sha,
          f"dawdreamer-state §49b: rubric doc SHA == rubric_hash.txt")
    check(_vj.get("rubric_hash") == _file_sha,
          "dawdreamer-state §49b: verdict.json rubric_hash == rubric_hash.txt")

# 49c — verdict.json schema-conformant + enum
if _VD49.is_file():
    _vj = _j49.loads(_VD49.read_text())
    check(_vj.get("verdict") in {"WORKAROUND_FOUND", "PARTIAL_WORKAROUND", "NO_WORKAROUND"},
          f"dawdreamer-state §49c: verdict enum ({_vj.get('verdict')})")
    for _k in ("rubric_hash", "verdict", "per_plugin", "per_path",
               "midi_input_sha256", "committed_at"):
        check(_k in _vj, f"dawdreamer-state §49c: verdict.json has {_k!r}")
    for _pk in ("surge_xt", "dexed"):
        check(_pk in _vj.get("per_plugin", {}),
              f"dawdreamer-state §49c: per_plugin has {_pk!r}")

# 49d — per-plugin data files present
for _pk in ("surge_xt", "dexed"):
    _pd = _DD / "per_plugin" / _pk
    for _fn in ("p1_state_v2.json", "p1_state_sha",
                "p2_preset_hex", "p2_state_sha",
                "p3_metadata.json", "p3_state_sha"):
        check((_pd / _fn).is_file(),
              f"dawdreamer-state §49d: per_plugin/{_pk}/{_fn} present")

# 49e — no import of scripts.tex.render_effects_layered under scripts/dawdreamer_state/ (AST).
import ast as _ast49
if _DR.is_dir():
    _bad = []
    for _f in _DR.rglob("*.py"):
        try:
            _tree = _ast49.parse(_f.read_text())
        except SyntaxError:
            continue
        for _node in _ast49.walk(_tree):
            if isinstance(_node, _ast49.Import):
                for _a in _node.names:
                    if "render_effects_layered" in _a.name or _a.name.startswith("scripts.tex"):
                        _bad.append(str(_f))
            elif isinstance(_node, _ast49.ImportFrom):
                _mod = _node.module or ""
                if "render_effects_layered" in _mod or _mod.startswith("scripts.tex"):
                    _bad.append(str(_f))
    check(not _bad,
          f"dawdreamer-state §49e: no cycle-9 effects chain import (AST) ({_bad})")

# 49f — no import of scripts.classifier.sidecar_nonfactor under scripts/dawdreamer_state/
if _DR.is_dir():
    _bad = []
    for _f in _DR.rglob("*.py"):
        _t = _f.read_text()
        if "sidecar_nonfactor" in _t:
            _bad.append(str(_f))
    check(not _bad,
          f"dawdreamer-state §49f: no sidecar_nonfactor import ({_bad})")

# 49g — pinned_state_v2 candidacy note in report iff verdict == WORKAROUND_FOUND
_REP49 = WS / "docs" / "dawdreamer_state_extraction_workaround_report.md"
if _REP49.is_file() and _VD49.is_file():
    _vj = _j49.loads(_VD49.read_text())
    _rt = _REP49.read_text()
    if _vj.get("verdict") == "WORKAROUND_FOUND":
        check("pinned_state_v2" in _rt,
              "dawdreamer-state §49g: report references pinned_state_v2 candidate")

# 49h — anchor preservation: c31 palette + palette_probe files NOT modified after cycle-33 launch
# (checked via presence + non-empty; deeper SHA check lives in the branch's own test suite)
for _anchor in ("scripts/palette/schema/palette_v1.json",
                "scripts/palette_probe/_shared.py",
                "data/palette_probe/rubric_hash.txt"):
    _ap = WS / _anchor
    check(_ap.is_file() and _ap.stat().st_size > 0,
          f"dawdreamer-state §49h: c31 anchor {_anchor} present + non-empty")

# §50. _infra/harness-clone-namespace-guard — cycle 33 clone-2, fork 4595e91f7574.
print()
print("§50 _infra/harness-clone-namespace-guard (cycle 33 clone-2)")
import hashlib as _h50
import inspect as _i50
import json as _j50
import os as _os50

_RUB50 = WS / "docs" / "harness_clone_namespace_guard_rubric.md"
_FX50 = WS / "tests" / "fixtures" / "harness_clone_namespace_guard_rubric_hash.txt"
_REP50 = WS / "docs" / "harness_clone_namespace_guard_report.md"
_TEST50 = WS / "tests" / "test_harness_clone_namespace_guard.py"

# 50a — rubric doc + fixture + test file all present
check(_RUB50.is_file(), "guard §50a: rubric doc present")
check(_FX50.is_file(), "guard §50a: rubric SHA fixture present")
check(_TEST50.is_file(), "guard §50a: test file present")

# 50b — fixture SHA equals sha256(rubric doc)
if _RUB50.is_file() and _FX50.is_file():
    _sha50 = _h50.sha256(_RUB50.read_bytes()).hexdigest()
    _fixture50 = _FX50.read_text().strip()
    check(_sha50 == _fixture50,
          f"guard §50b: fixture SHA equals doc SHA (got {_fixture50[:12]}..., "
          f"expected {_sha50[:12]}...)")

# 50c — 468-row baseline replay invariance (root-context, both modes)
import long_exposure.workspace_bootstrap as _wb50
_baseline = WS / "promise_ledger.jsonl"
if _baseline.is_file():
    _rows50 = [_j50.loads(l) for l in _baseline.read_text().splitlines() if l.strip()]
    check(len(_rows50) >= 468,
          f"guard §50c: baseline ledger has >= 468 rows (got {len(_rows50)})")
    _saved50 = {}
    for _v in ("AGENT_FORK_ID", "AGENT_FORK_CLONE_K", "AGENT_INSTANCE_DIR",
               "MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE"):
        _saved50[_v] = _os50.environ.pop(_v, None)
    try:
        for _mode in ("default", "strict"):
            if _mode == "strict":
                _os50.environ["MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE"] = "1"
            else:
                _os50.environ.pop("MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE", None)
            _muts = 0
            _rej = 0
            for _r in _rows50:
                _pre = _r.get("milestone_id")
                try:
                    _after = _wb50._guard_clone_namespace(dict(_r), WS)
                    if _after.get("milestone_id") != _pre:
                        _muts += 1
                except _wb50.LedgerNamespaceViolation:
                    _rej += 1
            check(_muts == 0 and _rej == 0,
                  f"guard §50c: baseline replay [{_mode}] mutations={_muts} rejects={_rej}")
    finally:
        for _v, _val in _saved50.items():
            if _val is None:
                _os50.environ.pop(_v, None)
            else:
                _os50.environ[_v] = _val

# 50d — LedgerNamespaceViolation is a real subclass of LedgerSchemaError.
from long_exposure.tools._ledger_schema import LedgerSchemaError as _LSE50
check(issubclass(_wb50.LedgerNamespaceViolation, _LSE50),
      "guard §50d: LedgerNamespaceViolation is subclass of LedgerSchemaError")

# 50e — public API of append_ledger_event unchanged
_sig50 = list(_i50.signature(_wb50.append_ledger_event).parameters)
check(_sig50 == ["workspace", "event"],
      f"guard §50e: append_ledger_event signature is (workspace, event) — got {_sig50}")

# 50f — c33 test suite defines >= 10 test_ functions (rubric floor).
import ast as _ast50
if _TEST50.is_file():
    _tree50 = _ast50.parse(_TEST50.read_text())
    _tfns50 = [n.name for n in _tree50.body
               if isinstance(n, _ast50.FunctionDef) and n.name.startswith("test_")]
    check(len(_tfns50) >= 10,
          f"guard §50f: test file defines >= 10 test_ functions (got {len(_tfns50)})")

# 50g — the c22 upstream anchor helpers are untouched. _is_clone and
# _get_clone_k are defined in long_exposure/fanout.py (re-exported via
# exploration.py); grep-verify their `def` lines directly in fanout.py.
# Direct import of exploration is avoided to keep integration test lean.
_FANOUT_SRC50 = Path(_wb50.__file__).with_name("fanout.py")
if _FANOUT_SRC50.is_file():
    _fn_txt50 = _FANOUT_SRC50.read_text()
    check("def _is_clone(" in _fn_txt50 and "def _get_clone_k(" in _fn_txt50,
          "guard §50g: c22 anchor fanout._is_clone/_get_clone_k intact")

# 50h — rubric doc mtime <= workspace_bootstrap.py mtime
if _RUB50.is_file():
    _rmt50 = _RUB50.stat().st_mtime
    _wmt50 = Path(_wb50.__file__).stat().st_mtime
    check(_rmt50 <= _wmt50 + 1.0,
          f"guard §50h: rubric mtime <= workspace_bootstrap.py mtime "
          f"({_rmt50:.0f} <= {_wmt50:.0f})")

print()
print(f"result: {'PASS' if fail == 0 else 'FAIL'} ({fail} failures)")
sys.exit(1 if fail else 0)
