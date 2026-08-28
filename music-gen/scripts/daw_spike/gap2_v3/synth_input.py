#!/usr/bin/env python3
"""Synthesize a deterministic 10.0 s bass input WAV for GAP-2 v3 renders.

Emits data/daw_spike/gap2_v3/input_10s.wav @ 44.1 kHz stereo. Uses
fluidsynth with FluidR3_GM.sf2 (SHA-256 pinned) to render 4 whole-note
bass notes at 120 BPM.

Interpreter-guarded /usr/bin/python3. Single-thread BLAS pins. Any
downstream reader must verify the output SHA-256 for byte-determinism.
"""
import hashlib
import os
import pathlib
import struct
import subprocess
import sys
import tempfile

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('PYTHONHASHSEED', '0')

assert sys.executable == '/usr/bin/python3', sys.executable

ROOT = pathlib.Path('/home/user/long-exposure-runs/music-gen')
SF2 = pathlib.Path('/usr/share/sounds/sf2/FluidR3_GM.sf2')
SF2_SHA_PREFIX = '74594e8f'  # pinned per M-SEP-1/ground-truth
OUT_WAV = ROOT / 'data/daw_spike/gap2_v3/input_10s.wav'


def _write_midi(path: pathlib.Path) -> None:
    # Minimal SMF type-0: 4 whole-note bass tones (F2, A2, C3, E3) at 120 BPM,
    # each 2.5 s to hit 10.0 s total. Ticks per quarter = 480; whole = 1920.
    tpq = 480
    tempo_us = 500000  # 120 BPM
    notes = [41, 45, 48, 52]  # F2 A2 C3 E3
    events = bytearray()
    def vlq(v: int) -> bytes:
        buf = [v & 0x7f]
        v >>= 7
        while v:
            buf.append(0x80 | (v & 0x7f))
            v >>= 7
        return bytes(reversed(buf))
    # Tempo meta
    events += vlq(0) + b'\xff\x51\x03' + tempo_us.to_bytes(3, 'big')
    # Program change to bass (channel 0, program 32 = Acoustic Bass)
    events += vlq(0) + b'\xc0' + bytes([32])
    for n in notes:
        events += vlq(0) + bytes([0x90, n, 96])
        events += vlq(tpq * 4) + bytes([0x80, n, 0])  # whole note = 4 quarters
    # End of track
    events += vlq(0) + b'\xff\x2f\x00'
    track = b'MTrk' + len(events).to_bytes(4, 'big') + bytes(events)
    header = b'MThd' + (6).to_bytes(4, 'big') + (0).to_bytes(2, 'big') + (1).to_bytes(2, 'big') + tpq.to_bytes(2, 'big')
    path.write_bytes(header + track)


def _canonicalize_wav(path: pathlib.Path) -> None:
    """Strip any non-essential chunks; keep 'fmt ' and 'data' only.

    fluidsynth may embed timestamped LIST/bext metadata that breaks byte
    determinism. This function rewrites the file with a canonical
    RIFF/fmt/data layout preserving PCM bytes exactly.
    """
    raw = path.read_bytes()
    assert raw[:4] == b'RIFF' and raw[8:12] == b'WAVE', 'not a WAVE'
    pos = 12
    fmt = None
    data = None
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        csz = struct.unpack('<I', raw[pos + 4:pos + 8])[0]
        body = raw[pos + 8:pos + 8 + csz]
        if cid == b'fmt ':
            fmt = body
        elif cid == b'data':
            data = body
        pos += 8 + csz + (csz & 1)
    if fmt is None or data is None:
        raise RuntimeError('missing fmt or data chunk in fluidsynth WAV')
    body = b'WAVE' + b'fmt ' + len(fmt).to_bytes(4, 'little') + fmt + b'data' + len(data).to_bytes(4, 'little') + data
    out = b'RIFF' + len(body).to_bytes(4, 'little') + body
    path.write_bytes(out)


def main() -> None:
    if not SF2.exists():
        raise SystemExit(f'SF2 missing: {SF2}')
    sha = hashlib.sha256(SF2.read_bytes()).hexdigest()
    assert sha.startswith(SF2_SHA_PREFIX), f'SF2 SHA drift: {sha}'
    OUT_WAV.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        mid = pathlib.Path(td) / 'in.mid'
        _write_midi(mid)
        cmd = [
            'fluidsynth', '-ni', '-a', 'file', '-F', str(OUT_WAV), '-r', '44100',
            '-g', '0.5',  # gain
            '-T', 'wav',
            str(SF2), str(mid),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    _canonicalize_wav(OUT_WAV)
    # Trim/pad to EXACTLY 441000 samples (10.0 s @ 44.1 kHz) for
    # perfect alignment with the reference/automation length.
    import soundfile as _sf
    x, sr = _sf.read(str(OUT_WAV), always_2d=True)
    assert sr == 44100, sr
    target = 441000
    if x.shape[0] > target:
        x = x[:target]
    elif x.shape[0] < target:
        import numpy as _np
        pad = _np.zeros((target - x.shape[0], x.shape[1]), dtype=x.dtype)
        x = _np.concatenate([x, pad], axis=0)
    _sf.write(str(OUT_WAV), x, sr, subtype='PCM_16')
    out_sha = hashlib.sha256(OUT_WAV.read_bytes()).hexdigest()
    print(f'OK input_10s.wav sha256={out_sha} shape={x.shape}')


if __name__ == '__main__':
    main()
