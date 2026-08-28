"""Two-front-door harvester.

Both `local_folder()` and `youtube_playlist()` end at the same seam:
they hand a *decoded WAV path* to the chunker + provenance writer.
The resulting manifests have identical shape — downstream code can only
distinguish local vs. YouTube by inspecting `source_type`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from scripts.ingest.chunker import chunk
from scripts.ingest.provenance import write_manifest

SR_TARGET = 22050
EGRESS_LOG = Path("data/ingestion/egress_status.jsonl")
_AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _decode_to_wav(src: Path, dst_wav: Path) -> None:
    """Decode any source (any container / channel count / sr) to a
    canonical mono 22050 Hz 16-bit PCM WAV via ffmpeg. WAV inputs are
    still transcoded for parity: source_id is a function of the decoded
    canonical form, not the on-disk container."""
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(src),
        "-ac", "1", "-ar", str(SR_TARGET),
        "-c:a", "pcm_s16le",
        str(dst_wav),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _emit(source_type: str, source_ref: str, decoded_wav: Path,
          out_clip_dir: Path, out_manifest_dir: Path) -> Path:
    """Chunk one decoded WAV and write its manifest. Returns the
    manifest path."""
    result = chunk(decoded_wav, out_clip_dir,
                   source_type=source_type, source_ref=source_ref)
    manifest = out_manifest_dir / f"{Path(source_ref).stem or result.source_id}.manifest.jsonl"
    write_manifest(result, source_type=source_type,
                   source_ref=source_ref, manifest_path=manifest)
    return manifest


def local_folder(path: Path, clip_dir: Path, manifest_dir: Path
                 ) -> list[Path]:
    """Enumerate audio files under `path` and ingest each."""
    path = Path(path)
    manifests: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="ingest_local_") as td:
        td_p = Path(td)
        for src in sorted(path.rglob("*")):
            if src.is_file() and src.suffix.lower() in _AUDIO_EXTS:
                decoded = td_p / (src.stem + ".wav")
                _decode_to_wav(src, decoded)
                manifests.append(_emit(
                    "local", str(src.resolve()),
                    decoded, clip_dir, manifest_dir,
                ))
    return manifests


def _log_egress(record: dict) -> None:
    EGRESS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with EGRESS_LOG.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def youtube_playlist(playlist_url: str, clip_dir: Path, manifest_dir: Path,
                     *, runner=subprocess.run) -> list[Path]:
    """Download a YouTube playlist to a temp dir via yt-dlp, then
    hand each downloaded file to the same decode+chunk seam as
    `local_folder`. Logs any egress failure and returns []."""
    manifests: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="ingest_yt_") as td:
        td_p = Path(td)
        cmd = [
            "yt-dlp", "-f", "bestaudio", "-x", "--audio-format", "wav",
            "--no-warnings", "--restrict-filenames",
            "--extractor-args", "youtube:player_client=tv_embedded",
            "-o", str(td_p / "%(id)s.%(ext)s"),
            playlist_url,
        ]
        try:
            proc = runner(cmd, capture_output=True, text=True, timeout=1800)
            rc = proc.returncode
            if rc != 0:
                _log_egress(dict(
                    ts=_now_iso(), event="youtube_playlist_failed",
                    playlist_url=playlist_url, returncode=rc,
                    stderr_tail=(proc.stderr or "")[-400:],
                ))
                return []
        except Exception as exc:
            _log_egress(dict(
                ts=_now_iso(), event="youtube_playlist_exception",
                playlist_url=playlist_url, error=f"{type(exc).__name__}: {exc}",
            ))
            return []
        for src in sorted(td_p.rglob("*")):
            if src.is_file() and src.suffix.lower() in _AUDIO_EXTS:
                decoded = td_p / (src.stem + "_dec.wav")
                _decode_to_wav(src, decoded)
                yt_ref = f"https://youtube.com/watch?v={src.stem}"
                manifests.append(_emit(
                    "youtube", yt_ref, decoded, clip_dir, manifest_dir,
                ))
    return manifests
