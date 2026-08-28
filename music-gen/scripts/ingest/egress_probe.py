"""Non-blocking egress reachability probe for the YouTube media CDN.

Two-stage check, both wrapped in hard timeouts:
    1. yt-dlp --get-url --skip-download   -> resolves *.googlevideo.com URL.
    2. curl --range 0-1023 that URL       -> proves the CDN answers bytes.

Never raises. Never spins. Appends one JSONL row per invocation to
`data/ingestion/egress_status.jsonl`. The target video is a short public
domain / Creative Commons clip so the probe stays cheap even on success.

Probe target: `jNQXAC9IVRw` ("Me at the zoo") — the first-ever YouTube
video, ~19 s, Creative Commons per YouTube metadata. Documented in
docs/ingestion_chassis_report.md.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

EGRESS_LOG = Path("data/ingestion/egress_status.jsonl")
PROBE_VIDEO_ID = "jNQXAC9IVRw"   # ~19 s CC-licensed test target
PROBE_URL = f"https://www.youtube.com/watch?v={PROBE_VIDEO_ID}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], timeout_s: float) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout_s)
        return p.returncode, (p.stdout or ""), (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout_s}s"
    except FileNotFoundError:
        return 127, "", f"missing binary: {cmd[0]}"
    except Exception as exc:
        return 1, "", f"{type(exc).__name__}: {exc}"


def probe(timeout_s: float = 15.0, video_id: str = PROBE_VIDEO_ID) -> dict:
    ts = _now_iso()
    yt_cmd = [
        "yt-dlp", "--skip-download", "--get-url",
        "--extractor-args", "youtube:player_client=tv_embedded",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    rc1, out1, err1 = _run(yt_cmd, timeout_s=min(timeout_s, 12.0))
    metadata_ok = (rc1 == 0 and "googlevideo.com" in out1)
    stream_url = ""
    if metadata_ok:
        for line in out1.splitlines():
            if "googlevideo.com" in line:
                stream_url = line.strip()
                break

    media_ok = False
    http_code: int | None = None
    bytes_downloaded: int = 0
    media_note = ""
    if stream_url:
        # Follow redirects (-L) and measure bytes actually received —
        # a 302 without following is not proof of media reachability.
        curl_cmd = [
            "curl", "-sSL", "-o", "/dev/null",
            "-w", "%{http_code} %{size_download}",
            "-m", "8", "--range", "0-1023",
            stream_url,
        ]
        rc2, out2, err2 = _run(curl_cmd, timeout_s=min(timeout_s, 12.0))
        m = re.match(r"(\d{3})\s+(\d+)", out2 or "")
        if m:
            http_code = int(m.group(1))
            bytes_downloaded = int(m.group(2))
        media_ok = (rc2 == 0 and http_code is not None
                    and 200 <= http_code < 300
                    and bytes_downloaded > 0)
        if not media_ok:
            media_note = (err2 or
                          f"http_code={http_code} bytes={bytes_downloaded}"
                          )[:200]
    else:
        media_note = (err1 or "no googlevideo URL")[:200]

    record = dict(
        ts=ts,
        video_id=video_id,
        metadata_ok=bool(metadata_ok),
        media_ok=bool(media_ok),
        http_code=http_code,
        bytes_downloaded=bytes_downloaded,
        note=media_note,
        stream_url_present=bool(stream_url),
    )
    EGRESS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with EGRESS_LOG.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
    return record


if __name__ == "__main__":
    print(json.dumps(probe(), sort_keys=True))
