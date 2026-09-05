#!/usr/bin/env python3
"""Check internal href/src links resolve.

Every href / src in every rendered HTML file must resolve to a file that
exists on disk (or, for #anchor, be an in-page reference). This catches
broken links from renamed species slugs, missing images, or path typos.
"""
from __future__ import annotations
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


class Ext(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs: list[tuple[str, str]] = []  # (attr, value)
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d and d["id"]:
            self.ids.add(d["id"])
        for a in ("src", "href"):
            if a in d and d[a]:
                self.hrefs.append((a, d[a]))


def resolve(html_path: Path, link: str) -> tuple[str, Path | None, str | None]:
    """Return (kind, target_path, fragment)."""
    if link.startswith("mailto:"):
        return ("mailto", None, None)
    if link.startswith("http://") or link.startswith("https://") or link.startswith("//"):
        return ("external", None, None)
    frag_stripped, frag = urldefrag(link)
    if not frag_stripped:
        # in-page anchor
        return ("anchor", html_path, frag or None)
    target = (html_path.parent / unquote(frag_stripped)).resolve()
    return ("file", target, frag or None)


def main() -> int:
    if not SITE.exists():
        print("check_links: site/ missing", file=sys.stderr)
        return 2
    html_files = list(sorted(SITE.rglob("*.html")))
    # First pass: gather anchor ids in each HTML file.
    ids_by_file: dict[Path, set[str]] = {}
    parsers: dict[Path, Ext] = {}
    for hp in html_files:
        p = Ext()
        p.feed(hp.read_text())
        p.close()
        ids_by_file[hp] = p.ids
        parsers[hp] = p

    errs = []
    for hp in html_files:
        for attr, link in parsers[hp].hrefs:
            kind, target, frag = resolve(hp, link)
            if kind in ("mailto", "external"):
                # external caught by lint_site; ignored here.
                continue
            if kind == "anchor":
                if frag and frag not in ids_by_file[hp]:
                    errs.append(f"{hp.relative_to(ROOT)}: anchor #{frag} not found in same page")
                continue
            # kind == "file"
            if not target.exists():
                errs.append(f"{hp.relative_to(ROOT)}: {attr}={link} -> missing {target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}")
                continue
            if frag:
                if target.suffix.lower() == ".html":
                    if frag not in ids_by_file.get(target, set()):
                        errs.append(f"{hp.relative_to(ROOT)}: {attr}={link} -> anchor #{frag} missing in {target.name}")
    if errs:
        print(f"check_links: {len(errs)} broken links")
        for e in errs:
            print(f"  {e}")
        return 1
    print(f"check_links: OK — {len(html_files)} pages, all internal links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
