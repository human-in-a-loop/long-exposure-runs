#!/usr/bin/env python3
"""Download, verify, and downscale images for the field guide.

Reads data/images.json — one entry per intended image, with mandatory
license metadata. Refuses to download any entry whose license is not in
the allow-list, or whose author / license_url / source / source_page fields
are missing.

Writes:
  site/assets/photos/<sha256[:12]>.<ext>  — downscaled image
  data/images.lock.json                    — verified manifest, keyed by image id

Idempotent — skips images already downloaded (matched by URL) unless --force.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from PIL import Image

# Ensure ROOT/scripts/ is on sys.path for the shared _licenses import when
# fetch_images.py is invoked as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _licenses import ALLOWED_LICENSES  # single source of truth

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MANIFEST = DATA / "images.json"
LOCK = DATA / "images.lock.json"
PHOTOS_DIR = ROOT / "site" / "assets" / "photos"
REQUIRED = ("id", "url", "author", "license", "license_url", "source", "source_page", "caption")
MAX_LONG_EDGE = 1200
TARGET_MIN_KB = 150
TARGET_MAX_KB = 400
JPEG_QUALITIES = [82, 75, 68]
UA = "kauai-field-guide/1.0 (educational field guide; contact via project)"


def validate_entry(entry: dict) -> list[str]:
    errs = []
    for f in REQUIRED:
        if not entry.get(f):
            errs.append(f"entry missing '{f}'")
    if entry.get("license") and entry["license"] not in ALLOWED_LICENSES:
        errs.append(f"license '{entry['license']}' not in allow-list {sorted(ALLOWED_LICENSES)}")
    return errs


def to_thumb_url(url: str, width: int = 1280) -> str:
    """Rewrite an upload.wikimedia.org 'original' URL into a thumbnail URL of
    the given width. Wikimedia explicitly asks bulk clients to use thumbnails.
    Non-upload.wikimedia URLs are returned unchanged."""
    prefix = "https://upload.wikimedia.org/wikipedia/commons/"
    if not url.startswith(prefix):
        return url
    tail = url[len(prefix):]
    # tail = 'a/ab/Filename.jpg' possibly with '?utm_...' — strip query
    tail = tail.split("?")[0]
    parts = tail.split("/")
    if len(parts) != 3:
        return url
    a, ab, fname = parts
    return f"{prefix}thumb/{a}/{ab}/{fname}/{width}px-{fname}"


def download(url: str, retries: int = 4) -> bytes:
    """Prefer a thumbnail URL; fall back to original if the thumb 404s."""
    urls = []
    thumb = to_thumb_url(url, 1280)
    if thumb != url:
        urls.append(thumb)
    urls.append(url)  # last-resort original
    last = None
    for u in urls:
        for attempt in range(retries):
            try:
                req = Request(u, headers={"User-Agent": UA})
                with urlopen(req, timeout=30) as r:
                    return r.read()
            except HTTPError as e:
                last = e
                if e.code == 429:
                    time.sleep(15 * (attempt + 1))
                elif e.code in (400, 404):
                    break  # try next url
                else:
                    time.sleep(3 * (attempt + 1))
            except URLError as e:
                last = e
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"download failed for {url}: {last}")


def downscale_jpeg(raw: bytes, max_edge: int, quality: int) -> tuple[bytes, int, int]:
    img = Image.open(io.BytesIO(raw))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    w, h = img.size
    scale = min(1.0, max_edge / max(w, h))
    if scale < 1.0:
        new = (int(w * scale), int(h * scale))
        img = img.resize(new, Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=quality, optimize=True, progressive=True)
    return out.getvalue(), img.size[0], img.size[1]


def choose_encoding(raw: bytes) -> tuple[bytes, int, int]:
    """Iterate max-edge + quality until the file lands in the target band."""
    for edge in (MAX_LONG_EDGE, 1000, 900):
        for q in JPEG_QUALITIES:
            data, w, h = downscale_jpeg(raw, edge, q)
            kb = len(data) / 1024
            if kb <= TARGET_MAX_KB:
                return data, w, h
    # last resort: aggressive
    return downscale_jpeg(raw, 800, 65)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not MANIFEST.exists():
        print("fetch_images: data/images.json not found", file=sys.stderr)
        return 2
    entries = json.loads(MANIFEST.read_text())
    if not isinstance(entries, list):
        print("fetch_images: images.json must be a JSON array", file=sys.stderr)
        return 2
    # Merge in shard manifests (data/images.branch-*.json). Duplicate ids across
    # base + shards are a hard error — the build preflight also catches this
    # but we want fetch to refuse to download conflicting entries.
    seen_ids: dict[str, str] = {e.get("id"): "images.json" for e in entries if e.get("id")}
    for shard in sorted(DATA.glob("images.branch-*.json")):
        try:
            shard_entries = json.loads(shard.read_text())
        except Exception as e:
            print(f"fetch_images: cannot parse {shard.name}: {e}", file=sys.stderr)
            return 2
        if not isinstance(shard_entries, list):
            print(f"fetch_images: {shard.name} must be a JSON array", file=sys.stderr)
            return 2
        for e in shard_entries:
            iid = e.get("id")
            if iid and iid in seen_ids:
                print(f"fetch_images: duplicate image id '{iid}' in {shard.name} and {seen_ids[iid]}", file=sys.stderr)
                return 2
            if iid:
                seen_ids[iid] = shard.name
            entries.append(e)

    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    lock: dict[str, dict] = {}
    if LOCK.exists() and not args.force:
        lock = json.loads(LOCK.read_text())

    n_ok, n_skip, n_fail = 0, 0, 0
    for entry in entries:
        errs = validate_entry(entry)
        if errs:
            print(f"REJECT {entry.get('id','<?>')}: {'; '.join(errs)}")
            n_fail += 1
            continue
        iid = entry["id"]
        if iid in lock and not args.force:
            # Confirm file still exists.
            on_disk = ROOT / "site" / lock[iid]["path"]
            if on_disk.exists() and lock[iid].get("url") == entry["url"]:
                n_skip += 1
                continue
        try:
            time.sleep(1.5)  # gentle client-side rate limit
            raw = download(entry["url"])
            data, w, h = choose_encoding(raw)
            sha = hashlib.sha256(data).hexdigest()[:12]
            fname = f"{sha}.jpg"
            (PHOTOS_DIR / fname).write_bytes(data)
            rel = f"assets/photos/{fname}"
            lock[iid] = {
                "id": iid,
                "url": entry["url"],
                "path": rel,
                "bytes": len(data),
                "width": w,
                "height": h,
                "sha256_12": sha,
                "author": entry["author"],
                "license": entry["license"],
                "license_url": entry["license_url"],
                "source": entry["source"],
                "source_page": entry["source_page"],
                "caption": entry["caption"],
            }
            print(f"OK  {iid}: {w}x{h} {len(data)//1024}KB -> {rel}")
            n_ok += 1
        except Exception as e:
            print(f"FAIL {iid}: {e}")
            n_fail += 1

    LOCK.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
    print(f"\nfetch_images: {n_ok} downloaded, {n_skip} skipped, {n_fail} failed. Lock has {len(lock)} entries.")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
