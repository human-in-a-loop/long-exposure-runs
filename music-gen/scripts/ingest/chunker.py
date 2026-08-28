"""30 s / 5 s-overlap chunker with a tail-anchored final clip.

Fixed decisions (module-level constants; do not parameterize):
    CLIP_S    = 30.0    # every clip is exactly this long, except a
                        # short-song single-clip fallback.
    OVERLAP_S = 5.0     # standard-case overlap between adjacent clips.
    HOP_S     = 25.0    # implied hop = CLIP_S - OVERLAP_S.

Tail-handling rule (adopted; see docs/provenance_schema.md):
    If the last hop-strided start does not reach the end of the source,
    append one additional "anchored" clip whose *end* equals the source
    end. Its overlap with the previous clip is >= 5 s by construction.
    This strengthens the "phrase whole in a neighbor" guarantee at the
    tail rather than weakening it.

Short-song rule:
    If the whole source is shorter than CLIP_S, emit exactly one clip
    that is the entire source, with `short_song=True` set in provenance.
    No zero-padding.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List

import numpy as np

from scripts.ingest.wavio import (
    encode_pcm16_bytes,
    read_pcm16_mono,
    write_pcm16_mono,
)

CLIP_S = 30.0
OVERLAP_S = 5.0
HOP_S = CLIP_S - OVERLAP_S    # 25.0
CHUNKER_VERSION = "ingest/0.1.0"


@dataclass(frozen=True)
class ClipSpec:
    index: int
    start_sample: int
    end_sample: int          # exclusive
    anchored_tail: bool
    short_song: bool
    sr_hz: int

    @property
    def t_start_s(self) -> float:
        return self.start_sample / self.sr_hz

    @property
    def t_end_s(self) -> float:
        return self.end_sample / self.sr_hz

    @property
    def n_samples(self) -> int:
        return self.end_sample - self.start_sample


def plan_clips(n_samples: int, sr_hz: int) -> List[ClipSpec]:
    """Return the deterministic list of clip boundaries for a source of
    length `n_samples` at `sr_hz`. Sample-accurate arithmetic only."""
    if n_samples <= 0:
        raise ValueError("empty source")
    clip_len = int(round(CLIP_S * sr_hz))
    hop_len = int(round(HOP_S * sr_hz))
    if n_samples < clip_len:
        # short-song single-clip fallback (no zero-pad).
        return [ClipSpec(
            index=0, start_sample=0, end_sample=n_samples,
            anchored_tail=False, short_song=True, sr_hz=sr_hz,
        )]
    starts: list[int] = []
    s = 0
    while s + clip_len <= n_samples:
        starts.append(s)
        s += hop_len
    # tail-anchored final clip: append iff the last standard clip did
    # not already end at n_samples.
    last_end = starts[-1] + clip_len
    anchored = False
    if last_end < n_samples:
        starts.append(n_samples - clip_len)
        anchored = True
    specs: list[ClipSpec] = []
    for i, st in enumerate(starts):
        is_anchored = anchored and (i == len(starts) - 1)
        specs.append(ClipSpec(
            index=i, start_sample=st, end_sample=st + clip_len,
            anchored_tail=is_anchored, short_song=False, sr_hz=sr_hz,
        ))
    return specs


@dataclass
class ChunkResult:
    source_id: str
    source_bytes_sha256: str
    sr_hz: int
    n_samples: int
    clips: List[dict]        # ready-to-serialize provenance rows


def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def chunk(source_wav: Path, out_dir: Path, source_type: str = "local",
          source_ref: str | None = None) -> ChunkResult:
    """Read `source_wav` (mono downmixed at read time), plan clips,
    write them to `out_dir/<source_id>/`, and return provenance rows.

    Determinism guarantees:
    - Input bytes -> input samples -> pcm16 bytes are pure functions.
    - source_id = sha256(pcm16(mono decoded samples))[:16]  -> content-
      addressed, container/channel-count invariant.
    - clip_id   = sha256(pcm16(clip samples))[:16]         -> content
      addressed; replay from source reproduces byte-identical clips.
    """
    source_wav = Path(source_wav)
    samples, sr_hz = read_pcm16_mono(source_wav)
    pcm_bytes = encode_pcm16_bytes(samples)
    src_sha = _sha256_hex(pcm_bytes)
    source_id = src_sha[:16]

    if source_ref is None:
        source_ref = str(source_wav.resolve())

    specs = plan_clips(len(samples), sr_hz)
    clip_dir = Path(out_dir) / source_id
    clip_dir.mkdir(parents=True, exist_ok=True)

    clip_rows: list[dict] = []
    for spec in specs:
        clip_samples = samples[spec.start_sample:spec.end_sample]
        clip_pcm = encode_pcm16_bytes(clip_samples)
        clip_sha = _sha256_hex(clip_pcm)
        clip_id = clip_sha[:16]
        clip_path = clip_dir / f"{source_id}__{spec.index:02d}.wav"
        write_pcm16_mono(clip_path, clip_samples, sr_hz)
        clip_rows.append(dict(
            kind="clip",
            schema_v=1,
            source_id=source_id,
            clip_index=spec.index,
            clip_id=clip_id,
            t_start_s=spec.t_start_s,
            t_end_s=spec.t_end_s,
            n_samples=spec.n_samples,
            sr_hz=sr_hz,
            clip_path=str(clip_path),
            clip_bytes_sha256=clip_sha,
            short_song=spec.short_song,
            anchored_tail=spec.anchored_tail,
        ))

    return ChunkResult(
        source_id=source_id,
        source_bytes_sha256=src_sha,
        sr_hz=sr_hz,
        n_samples=len(samples),
        clips=clip_rows,
    )
