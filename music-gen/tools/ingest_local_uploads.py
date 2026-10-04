#!/usr/bin/env python3
"""Ingest user-uploaded audio into corpus/ratings/<band>/ with harvester naming + receipts.

Matches each upload to corpus/ratings/ratings_manifest.tsv by fuzzy title match (token Jaccard),
cross-checks the upload's leading "<N>." against the manifest playlist position, copies the file to
corpus/ratings/<band>/<NNN>__<video_id>__<title>.<ext>, and appends a receipt line (sha256, duration,
format) to corpus/ratings/ingest_receipts.jsonl. Idempotent: files whose sha256 is already receipted
are skipped. Audio bytes stay gitignored; only the receipts are tracked.

Usage: python3 tools/ingest_local_uploads.py <upload_dir> [--min-score 0.5] [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RATINGS = ROOT / "corpus" / "ratings"
MANIFEST = RATINGS / "ratings_manifest.tsv"
RECEIPTS = RATINGS / "ingest_receipts.jsonl"
AUDIO_EXT = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus", ".aac"}
STOP = {"official", "video", "audio", "live", "feat", "ft", "the", "a", "and", "lyric", "lyrics",
        "hd", "hq", "mv", "music", "visualizer", "remastered", "version", "of", "in"}


def norm_tokens(s: str) -> set[str]:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"['’]", "", s)
    toks = re.findall(r"[a-z0-9]+", s)
    return {t for t in toks if t not in STOP and len(t) > 1}


def upload_title(name: str) -> tuple[int | None, str]:
    stem = Path(name).stem
    stem = re.sub(r"^[0-9a-f]{8}-", "", stem)  # upload-tool uuid prefix
    m = re.match(r"^(\d+)\.[_ ]*(.*)$", stem)
    if m:
        return int(m.group(1)), m.group(2)
    return None, stem


def probe(path: Path) -> dict:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=sample_rate,channels,codec_name",
         "-select_streams", "a:0", "-of", "json", str(path)]).decode()
    j = json.loads(out)
    st = (j.get("streams") or [{}])[0]
    return {"duration_s": round(float(j["format"]["duration"]), 2), "sample_rate": int(st.get("sample_rate", 0)),
            "channels": int(st.get("channels", 0)), "codec": st.get("codec_name")}


def load_manifest() -> list[dict]:
    rows = list(csv.DictReader(MANIFEST.open(), delimiter="\t"))
    pos: dict[str, int] = {}
    for r in rows:
        pos[r["rating"]] = pos.get(r["rating"], 0) + 1
        r["position"] = pos[r["rating"]]
        r["_tok"] = norm_tokens(r["title"])
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("upload_dir")
    ap.add_argument("--min-score", type=float, default=0.5)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    rows = load_manifest()
    seen = set()
    if RECEIPTS.exists():
        seen = {json.loads(l)["sha256"] for l in RECEIPTS.open() if l.strip()}

    results = []
    for f in sorted(Path(a.upload_dir).iterdir()):
        if f.suffix.lower() not in AUDIO_EXT:
            continue
        sha = hashlib.sha256(f.read_bytes()).hexdigest()
        num, title = upload_title(f.name)
        tok = norm_tokens(title)
        scored = []
        for r in rows:
            inter = len(tok & r["_tok"])
            if not inter:
                continue
            j = inter / len(tok | r["_tok"])
            # containment helps short titles like "Disco A" vs longer manifest strings
            c = inter / max(1, min(len(tok), len(r["_tok"])))
            s = max(j, 0.85 * c) + (0.15 if num is not None and r["position"] == num else 0.0)
            scored.append((s, r))
        scored.sort(key=lambda x: -x[0])
        if not scored or scored[0][0] < a.min_score:
            results.append({"file": f.name, "status": "UNMATCHED", "upload_title": title,
                            "best": scored[0][1]["title"] if scored else None,
                            "best_score": round(scored[0][0], 3) if scored else 0})
            continue
        s, r = scored[0]
        ambiguous = len(scored) > 1 and scored[1][0] > s - 0.1 and scored[1][1]["video_id"] != r["video_id"]
        meta = probe(f)
        dur_delta = round(meta["duration_s"] - float(r["duration_s"] or 0), 2) if r["duration_s"] else None
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", r["title"])[:80].strip("_")
        dst = RATINGS / r["rating"] / f"{r['position']:03d}__{r['video_id']}__{safe}{f.suffix.lower()}"
        rec = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "sha256": sha, "sha16": sha[:16],
               "band": int(r["rating"]), "position": r["position"], "video_id": r["video_id"], "title": r["title"],
               "manifest_duration_s": float(r["duration_s"]) if r["duration_s"] else None, "duration_delta_s": dur_delta,
               "upload_number": num, "upload_number_matches_position": num == r["position"] if num is not None else None,
               "match_score": round(s, 3), "ambiguous": ambiguous, "path": str(dst.relative_to(ROOT)),
               "source": "local_upload", **meta}
        status = "DUPLICATE" if sha in seen else "INGESTED"
        if status == "INGESTED" and not a.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            with RECEIPTS.open("a") as fh:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
            seen.add(sha)
        elif status == "DUPLICATE" and not dst.exists() and not a.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            status = "DUPLICATE_RESTORED"
        results.append({"file": f.name, "status": status, **rec})

    for x in results:
        if x["status"] == "UNMATCHED":
            print(f"UNMATCHED  {x['file']}  best={x['best']!r} score={x['best_score']}")
        else:
            flags = []
            if x["ambiguous"]:
                flags.append("AMBIGUOUS")
            if x["upload_number_matches_position"] is False:
                flags.append(f"num{x['upload_number']}!=pos{x['position']}")
            if x["duration_delta_s"] is not None and abs(x["duration_delta_s"]) > 3:
                flags.append(f"dur_delta={x['duration_delta_s']}s")
            print(f"{x['status']:18s} band{x['band']} #{x['position']:03d} {x['title'][:48]:48s} "
                  f"{x['duration_s']:7.1f}s sha16={x['sha16']} score={x['match_score']} {' '.join(flags)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
