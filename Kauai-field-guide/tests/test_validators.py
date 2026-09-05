#!/usr/bin/env python3
"""Negative-fixture tests for the validators.

Each fixture is a known-bad case that MUST be rejected. Run with:
    python3 tests/test_validators.py
"""
from __future__ import annotations
import json
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


def make_workspace(tmp: Path):
    """Copy scripts + references + a minimal site skeleton into tmp."""
    (tmp / "scripts").mkdir()
    for f in ("lint_site.py", "check_coverage.py", "check_links.py", "_licenses.py"):
        shutil.copy(SCRIPTS / f, tmp / "scripts" / f)
    shutil.copy(REPO / "REFERENCES.md", tmp / "REFERENCES.md")
    (tmp / "data" / "species").mkdir(parents=True)
    (tmp / "site" / "species").mkdir(parents=True)
    (tmp / "site" / "assets" / "photos").mkdir(parents=True)
    (tmp / "site" / "assets" / "diagrams").mkdir(parents=True)


BAD_LICENSE_IMG_LOCK = {
    "bad-1": {
        "id": "bad-1", "url": "https://x/y.jpg", "path": "assets/photos/bad.jpg",
        "bytes": 1, "width": 10, "height": 10, "sha256_12": "abc",
        "author": "", "license": "All-Rights-Reserved", "license_url": "",
        "source": "", "source_page": "", "caption": ""
    }
}

MISSING_ID_YAML = """\
slug: test-missing-idblock
scientific_name: Fakea imaginaria
authority: Test
family: Testaceae
common_names:
  hawaiian: [test]
  english: [fake plant]
status: indigenous
coastal_zones: [strand]
tier: common
occurrence_notes: hypothetical
ecology: hypothetical
citations: [1]
images:
  - id: nope
    role: habit
diagrams:
  - file: nope.svg
    caption: fake
how_to_identify:
  growth_form: shrub
  leaves: green
  size: small
  zone_hint: hypothetical
  clinchers: [only-one]
"""

EXTERNAL_URL_HTML = """<!DOCTYPE html><html><head><title>t</title></head>
<body><img src="https://external.example.com/photo.jpg"></body></html>
"""

EMPTY_LOOK_ALIKES_YAML = """\
slug: test-empty-lookalikes
scientific_name: Fakea nolookalikes
authority: Test
family: Testaceae
common_names:
  hawaiian: [test]
  english: [fake plant]
status: indigenous
coastal_zones: [strand]
tier: common
occurrence_notes: hypothetical
ecology: hypothetical
citations: [1]
images: []
diagrams:
  - file: fake1.svg
    caption: fake
  - file: fake2.svg
    caption: fake
how_to_identify:
  growth_form: shrub
  leaves: green
  flowers: white
  size: small
  zone_hint: strand
  clinchers: [one, two]
  look_alikes: []
"""


def test_coverage_rejects_bad(tmp: Path) -> tuple[bool, str]:
    make_workspace(tmp)
    (tmp / "data" / "species" / "bad.yaml").write_text(MISSING_ID_YAML)
    (tmp / "data" / "images.lock.json").write_text(json.dumps(BAD_LICENSE_IMG_LOCK))
    rc, out, err = run([sys.executable, "scripts/check_coverage.py"], tmp)
    if rc == 0:
        return False, "expected non-zero exit; got 0. output:\n" + out + err
    checks = [
        "citation [1]" not in out and "REFERENCES" not in out,  # unrelated, just noise
        "clinchers must be 2-4" in out,
        "id 'nope' not in data/images.lock.json" in out or "id 'nope'" in out,
    ]
    if not checks[1]:
        return False, "coverage did not flag clinchers count. output:\n" + out
    if not checks[2]:
        return False, "coverage did not flag unknown image id. output:\n" + out
    return True, "coverage rejected bad fixture"


def test_lint_rejects_external(tmp: Path) -> tuple[bool, str]:
    make_workspace(tmp)
    (tmp / "site" / "index.html").write_text(EXTERNAL_URL_HTML)
    rc, out, err = run([sys.executable, "scripts/lint_site.py"], tmp)
    if rc == 0:
        return False, "expected non-zero exit; got 0. output:\n" + out + err
    if "external URL" not in out or "src=" not in out:
        return False, "lint did not flag external URL. output:\n" + out
    return True, "lint rejected external URL"


def test_coverage_rejects_empty_look_alikes(tmp: Path) -> tuple[bool, str]:
    """After the cycle-2 tightening, an empty look_alikes list must fail."""
    make_workspace(tmp)
    (tmp / "data" / "species" / "empty-la.yaml").write_text(EMPTY_LOOK_ALIKES_YAML)
    (tmp / "data" / "images.lock.json").write_text("{}")
    # Create the two diagram files it references so we isolate the look_alikes failure.
    for fn in ("fake1.svg", "fake2.svg"):
        (tmp / "site" / "assets" / "diagrams" / fn).write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    rc, out, err = run([sys.executable, "scripts/check_coverage.py"], tmp)
    if rc == 0:
        return False, "expected non-zero exit; got 0. output:\n" + out + err
    if "look_alikes must have >=1 entry" not in out:
        return False, "coverage did not flag empty look_alikes. output:\n" + out
    return True, "coverage rejected empty look_alikes"


NC_LICENSE_YAML = """\
slug: test-nc-license
scientific_name: Fakea nonecommercialis
authority: Test
family: Testaceae
common_names:
  hawaiian: [test]
  english: [fake plant]
status: indigenous
coastal_zones: [strand]
tier: common
occurrence_notes: hypothetical
ecology: hypothetical
citations: [1]
images:
  - id: nc-1
    role: habit
    diagnostic_pointer: fake
  - id: nc-2
    role: leaf
    diagnostic_pointer: fake
diagrams: []
how_to_identify:
  growth_form: shrub
  leaves: green
  flowers: white
  size: small
  zone_hint: strand
  clinchers: [one, two]
  look_alikes:
    - species: nothing
      how_to_distinguish: nothing
"""

NC_LICENSE_IMG_LOCK = {
    "nc-1": {
        "id": "nc-1", "url": "https://x/y.jpg", "path": "assets/photos/nc1.jpg",
        "bytes": 1, "width": 10, "height": 10, "sha256_12": "abc",
        "author": "someone", "license": "CC-BY-NC-4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
        "source": "somewhere", "source_page": "https://example/nc1", "caption": "x"
    },
    "nc-2": {
        "id": "nc-2", "url": "https://x/y2.jpg", "path": "assets/photos/nc2.jpg",
        "bytes": 1, "width": 10, "height": 10, "sha256_12": "def",
        "author": "someone", "license": "CC-BY-NC-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "source": "somewhere", "source_page": "https://example/nc2", "caption": "y"
    },
}


def test_coverage_rejects_nc_license(tmp: Path) -> tuple[bool, str]:
    """After cycle-3 allow-list extension: CC-BY-NC-* must still be rejected.

    Pins that the CC-BY-2.0/2.5 broadening did not open the door to
    non-commercial licenses.
    """
    make_workspace(tmp)
    (tmp / "data" / "species" / "nc.yaml").write_text(NC_LICENSE_YAML)
    (tmp / "data" / "images.lock.json").write_text(json.dumps(NC_LICENSE_IMG_LOCK))
    # Create photo file stubs so the on-disk check doesn't trigger first.
    (tmp / "site" / "assets" / "photos" / "nc1.jpg").write_bytes(b"stub")
    (tmp / "site" / "assets" / "photos" / "nc2.jpg").write_bytes(b"stub")
    rc, out, err = run([sys.executable, "scripts/check_coverage.py"], tmp)
    if rc == 0:
        return False, "expected non-zero exit; got 0. output:\n" + out + err
    if "CC-BY-NC-4.0" not in out or "not in allow-list" not in out:
        return False, "coverage did not flag CC-BY-NC-4.0 as out-of-allow-list. output:\n" + out
    if "CC-BY-NC-SA-4.0" not in out:
        return False, "coverage did not flag CC-BY-NC-SA-4.0. output:\n" + out
    return True, "coverage rejected CC-BY-NC-* licenses"


def test_links_rejects_missing(tmp: Path) -> tuple[bool, str]:
    make_workspace(tmp)
    (tmp / "site" / "index.html").write_text(
        '<!DOCTYPE html><html><head><title>t</title></head>'
        '<body><a href="species/does-not-exist.html">x</a></body></html>'
    )
    rc, out, err = run([sys.executable, "scripts/check_links.py"], tmp)
    if rc == 0:
        return False, "expected non-zero exit; got 0. output:\n" + out + err
    if "does-not-exist" not in out:
        return False, "links check did not flag missing target. output:\n" + out
    return True, "check_links rejected missing target"


def main() -> int:
    tests = [
        ("coverage rejects bad species+image", test_coverage_rejects_bad),
        ("coverage rejects empty look_alikes", test_coverage_rejects_empty_look_alikes),
        ("coverage rejects CC-BY-NC-* licenses", test_coverage_rejects_nc_license),
        ("lint_site rejects external URL", test_lint_rejects_external),
        ("check_links rejects missing target", test_links_rejects_missing),
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
    print("\ntest_validators: " + ("ALL PASSED" if any_fail == 0 else "SOME FAILED"))
    return any_fail


if __name__ == "__main__":
    sys.exit(main())
