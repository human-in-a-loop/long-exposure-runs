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
_rules_root = WS / "scripts" / "rules"
_pat_sidecar_import = _re.compile(
    r"^\s*(?:from\s+\S*\bsidecar_nonfactor\b|import\s+\S*\bsidecar_nonfactor\b)",
    _re.MULTILINE,
)
if _rules_root.is_dir():
    for _p in _rules_root.rglob("*.py"):
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
    _examples_root = WS / "scripts" / "rules" / "schema" / "examples"
    for _rt in _rule_types:
        _files = sorted((_examples_root / _rt).glob("*.json"))
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
_trans_root = WS / "scripts" / "transcribe"
if _trans_root.is_dir():
    for _p in _trans_root.rglob("*.py"):
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

print()
print(f"result: {'PASS' if fail == 0 else 'FAIL'} ({fail} failures)")
sys.exit(1 if fail else 0)
