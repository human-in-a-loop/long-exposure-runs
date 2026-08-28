#!/usr/bin/env python3
"""Negative-fixture tests for the sharded-manifest build.

Covers three failure classes the sharding scheme must catch:
  1. Duplicate image id across image-manifest shards → build errors.
  2. Shard filename iteration order does not affect rendered HTML bytes.
  3. A citation token that references an unknown shard letter → build errors.

Run with:
    python3 tests/test_build_merge.py
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"


def run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def make_workspace(tmp: Path) -> None:
    """Copy the minimum needed to run build_site.py in isolation."""
    (tmp / "scripts").mkdir()
    for f in ("build_site.py",):
        shutil.copy(SCRIPTS / f, tmp / "scripts" / f)
    (tmp / "data" / "species").mkdir(parents=True)
    (tmp / "data" / "references").mkdir(parents=True)
    (tmp / "site" / "species").mkdir(parents=True)
    (tmp / "site" / "assets" / "photos").mkdir(parents=True)
    (tmp / "site" / "assets" / "diagrams").mkdir(parents=True)
    (tmp / "data" / "glossary.yaml").write_text("[]\n")


SPECIES_ONE = """\
slug: fake-species-one
scientific_name: Fakea unus
authority: Test
family: Testaceae
common_names: {hawaiian: [uno], english: [fake one]}
status: indigenous
coastal_zones: [strand]
tier: common
occurrence_notes: hypothetical
how_to_identify:
  growth_form: shrub
  leaves: green
  flowers: white
  size: small
  zone_hint: strand
  clinchers: [c1, c2]
  look_alikes:
    - species: nothing
      how_to_distinguish: n/a
ecology: hypothetical
citations: ["A:1"]
images: []
diagrams:
  - file: fake.svg
    caption: fake
  - file: fake.svg
    caption: fake
"""


def _write_base(tmp: Path) -> None:
    """Empty REFERENCES.md; one species; one SVG."""
    (tmp / "REFERENCES.md").write_text("# References\n")
    (tmp / "data" / "species" / "one.yaml").write_text(SPECIES_ONE)
    (tmp / "site" / "assets" / "diagrams" / "fake.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    (tmp / "data" / "images.json").write_text("[]\n")


def test_duplicate_image_id_across_shards(tmp: Path) -> tuple[bool, str]:
    make_workspace(tmp)
    _write_base(tmp)
    (tmp / "data" / "references" / "branch-a.md").write_text("[1] fake ref\n")
    entry = {
        "id": "dup-1", "url": "https://x/y.jpg",
        "author": "x", "license": "CC-BY-3.0",
        "license_url": "https://x", "source": "x",
        "source_page": "https://x", "caption": "x"
    }
    (tmp / "data" / "images.branch-a.json").write_text(json.dumps([entry]))
    (tmp / "data" / "images.branch-b.json").write_text(json.dumps([entry]))
    rc, out, err = run([sys.executable, "scripts/build_site.py"], tmp)
    combined = out + err
    if rc == 0:
        return False, f"expected non-zero exit; got 0. output:\n{combined}"
    if "duplicate image id 'dup-1'" not in combined:
        return False, f"did not report duplicate id. output:\n{combined}"
    return True, "duplicate image id across shards rejected"


def test_shard_order_deterministic(tmp: Path) -> tuple[bool, str]:
    make_workspace(tmp)
    _write_base(tmp)
    # Multiple shards, each with entries. Different filesystem creation order
    # must not change rendered HTML.
    (tmp / "data" / "references" / "branch-a.md").write_text("[1] first-a\n[2] second-a\n")
    (tmp / "data" / "references" / "branch-b.md").write_text("[1] first-b\n")
    (tmp / "data" / "references" / "branch-c.md").write_text("[1] first-c\n[2] second-c\n")
    (tmp / "data" / "images.branch-a.json").write_text("[]\n")
    (tmp / "data" / "images.branch-b.json").write_text("[]\n")
    (tmp / "data" / "images.branch-c.json").write_text("[]\n")

    rc, _, err = run([sys.executable, "scripts/build_site.py"], tmp)
    if rc != 0:
        return False, f"build failed on first pass: {err}"
    ref1_hash = hashlib.sha256((tmp / "site" / "references.html").read_bytes()).hexdigest()
    map1 = (tmp / "data" / "references.map.json").read_text()

    # Recreate the shard files in reverse order (fs mtime order flips).
    # Since the loader must sort by lexicographic filename, output stays same.
    for name in ("branch-c.md", "branch-b.md", "branch-a.md"):
        p = tmp / "data" / "references" / name
        text = p.read_text()
        p.unlink()
        p.write_text(text)

    rc, _, err = run([sys.executable, "scripts/build_site.py"], tmp)
    if rc != 0:
        return False, f"build failed on second pass: {err}"
    ref2_hash = hashlib.sha256((tmp / "site" / "references.html").read_bytes()).hexdigest()
    map2 = (tmp / "data" / "references.map.json").read_text()

    if ref1_hash != ref2_hash:
        return False, f"references.html changed with shard file recreation order"
    if map1 != map2:
        return False, f"references.map.json changed with shard file recreation order"
    # Also check the citation token in the species page: species cites "A:1" which
    # should map to global 16 (base has 0 refs + a[0]=16).
    # Actually with our base REFERENCES.md being empty, A:1 becomes global 1.
    parsed = json.loads(map2)
    if parsed.get("A:1") != 1:
        return False, f"unexpected token map: {parsed}"
    if parsed.get("C:2") != 5:
        return False, f"C:2 should be global 5, got: {parsed}"
    return True, "shard ordering deterministic; token map stable"


def test_unresolved_citation_token(tmp: Path) -> tuple[bool, str]:
    make_workspace(tmp)
    _write_base(tmp)
    # No branch-a.md exists — species cites "A:1" which cannot resolve.
    (tmp / "data" / "images.branch-a.json").write_text("[]\n")
    rc, out, err = run([sys.executable, "scripts/build_site.py"], tmp)
    combined = out + err
    if rc == 0:
        return False, f"expected non-zero exit; got 0. output:\n{combined}"
    if "unresolved token 'A:1'" not in combined:
        return False, f"did not report unresolved token. output:\n{combined}"
    return True, "unresolved citation token rejected"


def main() -> int:
    tests = [
        ("duplicate image id across shards", test_duplicate_image_id_across_shards),
        ("shard iteration order deterministic", test_shard_order_deterministic),
        ("unresolved citation token", test_unresolved_citation_token),
    ]
    any_fail = 0
    for name, fn in tests:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            ok, msg = fn(tmp)
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] {name} — {msg}")
            if not ok:
                any_fail = 1
    print("\ntest_build_merge: " + ("ALL PASSED" if any_fail == 0 else "SOME FAILED"))
    return any_fail


if __name__ == "__main__":
    sys.exit(main())
