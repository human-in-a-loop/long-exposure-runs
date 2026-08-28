#!/usr/bin/env python3
"""Query the Wikimedia Commons API for candidate images by species.

For each species search phrase, list up to N candidate files with:
  - filename
  - author (Artist field, HTML-stripped)
  - license short name and URL
  - description short
  - direct upload URL for the original
Useful for hand-curating data/images.json.
"""
from __future__ import annotations
import argparse
import html as _html
import json
import re
import sys
import time
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

API = "https://commons.wikimedia.org/w/api.php"
UA = "kauai-field-guide/1.0 (educational field guide)"

ALLOW = {"cc0", "public domain", "cc by 3.0", "cc by 4.0", "cc by-sa 3.0", "cc by-sa 4.0"}


def api(params: dict) -> dict:
    p = {"format": "json", "formatversion": "2"}
    p.update(params)
    url = API + "?" + urlencode(p)
    last = None
    for attempt in range(5):
        try:
            req = Request(url, headers={"User-Agent": UA})
            with urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"api failed: {last}")


def search(term: str, limit: int = 12) -> list[str]:
    for attempt in range(4):
        try:
            r = api({"action": "query", "list": "search", "srsearch": term,
                     "srnamespace": "6", "srlimit": str(limit)})
            return [row["title"] for row in r.get("query", {}).get("search", [])]
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return []


def info(titles: list[str]) -> list[dict]:
    if not titles:
        return []
    # imageinfo API accepts up to 50 titles per call.
    out = []
    for i in range(0, len(titles), 25):
        chunk = titles[i:i+25]
        r = api({
            "action": "query",
            "titles": "|".join(chunk),
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size|user",
            "iiurlwidth": "1200",
        })
        for pg in r.get("query", {}).get("pages", []):
            title = pg.get("title", "")
            ii = pg.get("imageinfo", [])
            if not ii:
                continue
            info0 = ii[0]
            meta = info0.get("extmetadata", {}) or {}
            def m(k):
                return (meta.get(k, {}) or {}).get("value", "") or ""
            artist_raw = m("Artist")
            artist = _html.unescape(re.sub("<[^>]+>", "", artist_raw)).strip()
            license_short = m("LicenseShortName").strip()
            license_url = m("LicenseUrl").strip()
            desc = re.sub("<[^>]+>", " ", m("ImageDescription")).strip()[:180]
            out.append({
                "title": title,
                "url": info0.get("url", ""),
                "width": info0.get("width", 0),
                "height": info0.get("height", 0),
                "author": artist,
                "license_short": license_short,
                "license_url": license_url,
                "description": desc,
                "source_page": f"https://commons.wikimedia.org/wiki/{quote(title.replace(' ', '_'))}",
            })
        time.sleep(0.3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("terms", nargs="+", help="Species search phrases, e.g. 'Scaevola taccada Starr'")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--allow-any", action="store_true", help="Print all licenses, not only allow-list ones.")
    args = ap.parse_args()
    for term in args.terms:
        print(f"\n=== {term} ===")
        titles = search(term, limit=args.limit)
        recs = info(titles)
        time.sleep(3.0)
        for r in recs:
            ls = r["license_short"].lower()
            if not args.allow_any and ls not in ALLOW:
                continue
            print(f"- {r['title']}")
            print(f"    url:     {r['url']}")
            print(f"    dims:    {r['width']}x{r['height']}")
            print(f"    author:  {r['author']}")
            print(f"    license: {r['license_short']} <{r['license_url']}>")
            print(f"    desc:    {r['description']}")


if __name__ == "__main__":
    main()
