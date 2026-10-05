#!/usr/bin/python3
"""v6 Phase 5 — render-path memory regression: composing + rendering several songs in ONE process must not retain per-song
memory (iteration 03 was OOM-killed at 13 GB: struct.pack's format cache held every rendered mix, scripts/v6/gen/render.py).

Run: /usr/bin/python3 -m pytest tests/test_v6_render_memory.py -q      (~3 min: three 16-bar fixture renders)
"""
from __future__ import annotations

import gc
import os
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v6.gen.render import write_wav_int16  # noqa: E402

RSS_GROWTH_CAP_MB = 150


def _rss_mb() -> int:
    return int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0]) // 1024


def test_write_wav_int16_bytes_identical_to_struct_pack_form(tmp_path) -> None:
    rng = np.random.default_rng(0)
    x = (rng.standard_normal((22050, 2)) * 0.4).astype(np.float32)
    x[10], x[20] = 3.0, -3.0  # clipping path
    ai = np.round(np.clip(x, -1.0, 1.0) * 32767.0).astype(np.int16)
    legacy = struct.pack("<" + "h" * ai.size, *ai.reshape(-1).tolist())
    write_wav_int16(tmp_path / "a.wav", x, 22050)
    raw = (tmp_path / "a.wav").read_bytes()
    assert raw[44:] == legacy and raw[:4] == b"RIFF" and len(raw) == 44 + len(legacy)
    struct._clearcache()


def test_three_songs_one_process_rss_growth_under_cap() -> None:
    from scripts.v6.gen.compose_v6 import compose_song, write_song
    from scripts.v6.gen.fixtures import load_models
    if not (_ROOT / "data" / "v5" / "rules" / "harmony_markov_v5_full.json").exists():
        import pytest
        pytest.skip("rule files absent (data/ is gitignored)")
    models = load_models(_ROOT / "data" / "v5" / "rules", fixtures=False)
    hz = {"mt": None, "path": None, "sha256": None}
    rss = []
    with tempfile.TemporaryDirectory(prefix="v6_mem_") as td:
        for i in range(3):
            res = compose_song(models, f"gen_v6_song_{i + 1}", "fixture_b", 3, 112.0, 16, hz)
            man = write_song(res, Path(td) / f"s{i}", True, False, "v6", 1)
            assert man["render"]["renderer"] == "v6"
            del res, man
            gc.collect()
            rss.append(_rss_mb())
    growth = rss[2] - rss[1]
    assert growth < RSS_GROWTH_CAP_MB, f"RSS grew {growth} MB between song 2 and 3 (rss per song {rss})"
    print(f"PASS: RSS per song {rss} MB; growth song2->3 {growth} MB < {RSS_GROWTH_CAP_MB}")
