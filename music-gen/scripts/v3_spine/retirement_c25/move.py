#!/usr/bin/python3
"""c25 one-off driver retirement — move mechanism.

Consumes ``data/v3/recreate_v3/retirement_catalog_c22.json`` verbatim,
moves 37 per-song v3-spine driver scripts from ``scripts/v3_spine/`` to
``tools/stale/oneoff_v3_drivers_retired_c25/<basename>`` via
``os.rename`` (content-preserving) + ``os.utime`` (mtime-advancing per
c38 lesson). SHA-256 preserved byte-identically. Idempotent — second
run detects targets already-at-destination and records
``action: already_moved``.

Discipline:
- Interpreter guard ``/usr/bin/python3`` (see shebang + assertion).
- Zero PRNG, zero ``sidecar_nonfactor``, zero VST3 state APIs
  (get_state / save_state / save_preset / load_state / set_state).
- Env pins set BEFORE any non-trivial import.
"""
from __future__ import annotations

import os
import sys

# Env pins — set before any observed import (matches c22/c24 doctrine).
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

# Interpreter guard — the v3-spine invariant.
assert sys.executable == "/usr/bin/python3", (
    f"c25 retirement requires /usr/bin/python3; got {sys.executable}"
)

import hashlib
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
CATALOG = ROOT / "data" / "v3" / "recreate_v3" / "retirement_catalog_c22.json"
OUT_DIR = ROOT / "data" / "v3" / "retirement" / "c25"
STALE_DIR = ROOT / "tools" / "stale" / "oneoff_v3_drivers_retired_c25"


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_catalog() -> list[str]:
    """Flatten the catalog's `candidates` dict into the 37-element list."""
    cat = json.loads(CATALOG.read_text())
    targets: list[str] = []
    for _key, group in sorted(cat["candidates"].items()):
        targets.extend(group)
    assert len(targets) == 37, f"catalog gate broken: expected 37 got {len(targets)}"
    return targets


def move_all() -> dict:
    """Move (or verify already-moved) each of the 37 cataloged targets.

    Returns the moves manifest dict (also written to
    ``data/v3/retirement/c25/moves.jsonl`` line-per-target).
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STALE_DIR.mkdir(parents=True, exist_ok=True)

    targets = _load_catalog()
    now = float(os.environ["SOURCE_DATE_EPOCH"])
    # Use SOURCE_DATE_EPOCH as the target mtime so byte-determinism of
    # timestamps holds across runs. c38 lesson: the point of the touch
    # is to break "file-mtime-order" tests keyed to the pre-move value.
    moves = []
    for rel in targets:
        basename = pathlib.Path(rel).name
        src = ROOT / rel
        dst = STALE_DIR / basename

        if not src.exists() and dst.exists():
            # Second-run idempotent branch.
            action = "already_moved"
            sha = _sha256(dst)
            mtime_pre = None
            mtime_post = dst.stat().st_mtime
        elif src.exists():
            sha = _sha256(src)
            mtime_pre = src.stat().st_mtime
            os.rename(str(src), str(dst))
            os.utime(str(dst), (now, now))
            post_sha = _sha256(dst)
            assert post_sha == sha, (
                f"SHA drift on rename: {basename} pre={sha} post={post_sha}"
            )
            action = "renamed"
            mtime_post = dst.stat().st_mtime
        else:
            action = "missing_source"
            sha = None
            mtime_pre = None
            mtime_post = None

        moves.append({
            "basename": basename,
            "src": rel,
            "dst": str(dst.relative_to(ROOT)),
            "sha256": sha,
            "mtime_pre": mtime_pre,
            "mtime_post": mtime_post,
            "action": action,
        })

    # Write moves.jsonl (line-per-move) and moves manifest sha over
    # the determinism-only triples.
    jsonl_path = OUT_DIR / "moves.jsonl"
    with open(jsonl_path, "w") as f:
        for row in moves:
            f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    det_triples = [
        {"basename": r["basename"], "sha256": r["sha256"],
         "action_class": ("moved" if r["action"] in ("renamed", "already_moved")
                          else r["action"])}
        for r in moves
    ]
    det_bytes = json.dumps(det_triples, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    det_sha = hashlib.sha256(det_bytes).hexdigest()
    (OUT_DIR / "moves_determinism_sha.txt").write_text(det_sha)

    return {"moves": moves, "determinism_sha": det_sha}


def snapshot_preserved(label: str) -> dict:
    """Snapshot ≥25 SHA-256 anchors of the preserved set + external refs.

    Writes to ``data/v3/retirement/c25/anchor_preservation_<label>.json``.
    """
    entries: list[tuple[str, str | None]] = []

    # Named preserved anchors.
    named = [
        "scripts/v3_spine/recreate_v3.py",
        "scripts/v3_spine/recreate_v3_checkpointed.py",
        "scripts/v3_spine/stage_cache.py",
        "scripts/v3_spine/launch_detached.py",
        "scripts/v3_spine/midi_from_json_events.py",
        "scripts/palette_render/render_stem.py",
        "docs/v3_spine_oneoff_driver_retirement_c25_rubric.md",
        "data/v3/retirement/c25/rubric_hash.txt",
        "data/v3/rules/rules_artifact.jsonl",
        "data/v3/reproduce/c23/31a164f845f8e27e/reproduce_report.json",
        "data/v3/reproduce/c23/51e433ade2a845e1/reproduce_report.json",
    ]
    for rel in named:
        p = ROOT / rel
        entries.append((rel, _sha256(p) if p.exists() else None))

    # v3_pipeline/* directory (glob).
    vp_dir = ROOT / "scripts" / "v3_spine" / "v3_pipeline"
    for p in sorted(vp_dir.glob("*.py")):
        entries.append((str(p.relative_to(ROOT)), _sha256(p)))

    # torch213_reproduce_probe_c*.py (glob).
    for p in sorted((ROOT / "scripts" / "v3_spine").glob(
            "torch213_reproduce_probe_c*.py")):
        entries.append((str(p.relative_to(ROOT)), _sha256(p)))

    # anchor_preservation_c*.py (glob).
    for p in sorted((ROOT / "scripts" / "v3_spine").glob(
            "anchor_preservation_c*.py")):
        entries.append((str(p.relative_to(ROOT)), _sha256(p)))

    # verdict_c*.py (glob).
    for p in sorted((ROOT / "scripts" / "v3_spine").glob("verdict_c*.py")):
        entries.append((str(p.relative_to(ROOT)), _sha256(p)))

    # *_ledger.py under scripts/ EXCEPT peach_dream_c20_ledger.py
    # (which is a cataloged move target).
    for p in sorted((ROOT / "scripts").rglob("*_ledger.py")):
        if p.name == "peach_dream_c20_ledger.py":
            continue
        entries.append((str(p.relative_to(ROOT)), _sha256(p)))

    # De-dup preserving order.
    seen: set[str] = set()
    unique: list[dict] = []
    for path, sha in entries:
        if path in seen:
            continue
        seen.add(path)
        unique.append({"path": path, "sha256": sha})

    out = {
        "label": label,
        "n_entries": len(unique),
        "entries": unique,
    }
    (OUT_DIR / f"anchor_preservation_{label}.json").write_text(
        json.dumps(out, sort_keys=True, indent=2))
    return out


def grep_zero_verification() -> dict:
    """Grep-zero import scan for the 37 moved module paths.

    Scans ``scripts/``, ``tools/`` (excl. ``tools/stale/``), ``tests/``,
    ``data/``, ``docs/`` for import-statement patterns resolving the
    moved modules. Literal-string references in .md/.json/.jsonl are
    counted but classified as ``literal_string`` — they do NOT gate
    LANDS. Only real Python imports do.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = _load_catalog()
    module_stems = [pathlib.Path(t).stem for t in targets]  # 37 stems

    scan_roots = ["scripts", "tools", "tests", "data", "docs"]
    scanned = 0
    py_matches: list[dict] = []
    literal_matches: list[dict] = []

    def _skip(rel: str) -> bool:
        return rel.startswith("tools/stale/") or "/__pycache__/" in rel

    for root in scan_roots:
        rpath = ROOT / root
        if not rpath.exists():
            continue
        for p in rpath.rglob("*"):
            if not p.is_file():
                continue
            rel = str(p.relative_to(ROOT))
            if _skip(rel):
                continue
            if p.suffix not in {".py", ".md", ".json", ".jsonl", ".txt", ".tsv"}:
                continue
            scanned += 1
            try:
                text = p.read_text(errors="replace")
            except (OSError, UnicodeDecodeError):
                continue
            for stem in module_stems:
                # Python import statements — the LANDS gate.
                py_patterns = [
                    f"from scripts.v3_spine.{stem} import",
                    f"import scripts.v3_spine.{stem}",
                    f"from scripts.v3_spine import {stem}",
                ]
                for pat in py_patterns:
                    if pat in text:
                        py_matches.append({
                            "path": rel,
                            "pattern": pat,
                            "stem": stem,
                        })
                # Literal-string references — reported not gated.
                lit_pat = f"scripts/v3_spine/{stem}.py"
                if lit_pat in text and p.suffix != ".py":
                    literal_matches.append({
                        "path": rel,
                        "pattern": lit_pat,
                        "stem": stem,
                    })

    out = {
        "scanned_files": scanned,
        "scanned_roots": scan_roots,
        "excluded": ["tools/stale/", "**/__pycache__/**"],
        "python_import_matches": py_matches,
        "literal_string_matches_non_py": literal_matches,
        "zero_broken_imports": len(py_matches) == 0,
    }
    (OUT_DIR / "grep_zero_verification.json").write_text(
        json.dumps(out, sort_keys=True, indent=2))
    return out


def byte_determinism_verify(rerun_cmd: list[str] | None = None) -> dict:
    """Two-fresh-subprocess-run byte-determinism ×2 check.

    First invocation is assumed to be the currently-running one (moves
    already performed); this function re-invokes the move script once
    more as a fresh subprocess and records the determinism SHA equality
    of ``moves.jsonl`` (over the determinism-only triple, timestamp-
    excluded).
    """
    import subprocess
    first_sha = (OUT_DIR / "moves_determinism_sha.txt").read_text().strip()
    if rerun_cmd is None:
        rerun_cmd = ["/usr/bin/python3", "-m",
                     "scripts.v3_spine.retirement_c25.move", "--run"]
    subprocess.run(rerun_cmd, cwd=str(ROOT), check=True,
                   env={**os.environ, "PYTHONPATH": str(ROOT)})
    second_sha = (OUT_DIR / "moves_determinism_sha.txt").read_text().strip()
    out = {
        "first_run_determinism_sha": first_sha,
        "second_run_determinism_sha": second_sha,
        "byte_determinism_holds": first_sha == second_sha,
    }
    (OUT_DIR / "byte_determinism.json").write_text(
        json.dumps(out, sort_keys=True, indent=2))
    return out


def main() -> None:
    move_all()


if __name__ == "__main__":
    main()
