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

print()
print(f"result: {'PASS' if fail == 0 else 'FAIL'} ({fail} failures)")
sys.exit(1 if fail else 0)
