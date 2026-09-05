#!/usr/bin/env python3
"""Second-pass check that no resource-loading tag in any rendered HTML file
points at an external URL. This is the file:// offline guarantee.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

RESOURCE_PAT = re.compile(
    r'<(?P<tag>img|script|link|iframe|source|video|audio|embed|track|object|picture)\b[^>]*?\s(?:src|href)=[\"\']([^\"\']+)[\"\']',
    re.I,
)

def main() -> int:
    issues = 0
    n_files = 0
    for p in sorted(SITE.rglob("*.html")):
        n_files += 1
        text = p.read_text()
        for m in RESOURCE_PAT.finditer(text):
            url = m.group(2)
            if url.startswith(("http://", "https://", "//")):
                print(f"EXT {p.relative_to(ROOT)} <{m.group('tag')}> -> {url}")
                issues += 1
    if issues == 0:
        print(f"check_offline: OK — {n_files} HTML files, no external asset URLs (safe for file://)")
        return 0
    print(f"check_offline: {issues} external asset URLs found")
    return 1


if __name__ == "__main__":
    sys.exit(main())
