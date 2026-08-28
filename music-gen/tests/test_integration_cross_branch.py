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


print()
print(f"result: {'PASS' if fail == 0 else 'FAIL'} ({fail} failures)")
sys.exit(1 if fail else 0)
