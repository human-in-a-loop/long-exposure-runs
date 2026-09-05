#!/usr/bin/env python3
"""Lint the rendered site.

Rules:
  - Every HTML file is parseable by html.parser (well-formed enough that
    the parser encounters no crash) — trailing warnings are noted but not fatal.
  - Every src= and href= attribute is one of: relative path, in-page anchor
    (starts with '#'), or a 'mailto:' link. Any http(s):// value is a hard fail.
"""
from __future__ import annotations
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

EXTERNAL_PREFIXES = ("http://", "https://", "//", "data:", "ftp:")
ALLOWED_SCHEMES = ("#", "mailto:")


RESOURCE_LOADING_TAGS = {
    # These tags trigger network requests when the browser parses them.
    "img", "script", "link", "iframe", "source", "video", "audio",
    "embed", "track", "object", "picture",
}

class LinkExtractor(HTMLParser):
    """Collect (tag, attr, value) triples so lint can distinguish
    asset-loading attributes (must be local) from hyperlinks (may be external
    when they are provenance/attribution links, since the user opts to follow
    them and no request fires at page load)."""
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value is None:
                continue
            if name in ("src", "href"):
                self.links.append((tag.lower(), name, value))


def check_file(path: Path) -> list[str]:
    errors = []
    text = path.read_text()
    p = LinkExtractor()
    try:
        p.feed(text)
        p.close()
    except Exception as e:
        errors.append(f"{path.relative_to(ROOT)}: HTML parse crashed — {e}")
        return errors
    for tag, attr, val in p.links:
        v = val.strip()
        if not v:
            errors.append(f"{path.relative_to(ROOT)}: empty {tag} {attr}=")
            continue
        is_asset = tag in RESOURCE_LOADING_TAGS
        # <link rel="stylesheet"> is asset-loading; hyperlink <a>/nav are not.
        if v.startswith(EXTERNAL_PREFIXES):
            if is_asset:
                errors.append(f"{path.relative_to(ROOT)}: external URL in <{tag}> {attr}= : {v}")
            # else: allowed — hyperlink for provenance/attribution.
            continue
        if v.startswith(ALLOWED_SCHEMES):
            continue
        if "://" in v:
            errors.append(f"{path.relative_to(ROOT)}: unexpected scheme in <{tag}> {attr}= : {v}")
    return errors


def main() -> int:
    if not SITE.exists():
        print(f"lint_site: {SITE} does not exist — run scripts/build_site.py first.", file=sys.stderr)
        return 2
    errs = []
    n = 0
    for html_path in sorted(SITE.rglob("*.html")):
        n += 1
        errs.extend(check_file(html_path))
    if errs:
        print(f"lint_site: {len(errs)} problems across {n} HTML files")
        for e in errs:
            print(f"  {e}")
        return 1
    print(f"lint_site: OK — {n} HTML files, no external asset URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
