#!/usr/bin/python3
"""v6 Phase 4 tests — backends: sfz (sfizz_render via the .ram.sfz wrapper) and sf2 (fluidsynth) stems are byte-identical
across two renders; bank/program forcing works (bank-128 kit on channel 9, bank-0 AVL kit on channel 0 both sound); the
dawdreamer path is frozen by (midi, patch) sha (exercised with a stub so the test does not need the VST).

Run: /usr/bin/python3 -m pytest tests/test_v6_render_backends.py -q
"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

import numpy as np  # noqa: E402

from scripts.v6.gen.render_v6 import backends, midi_io, select  # noqa: E402

POOL = select.load_pool()


def _rms_db(p: Path) -> float:
    import soundfile as sf
    x, _ = sf.read(str(p), dtype="float32", always_2d=True)
    return float(20 * np.log10(np.sqrt((x.astype(np.float64) ** 2).mean()) + 1e-12))


def _notes(drums: bool):
    if drums:
        return [{"pitch": p, "velocity": 100, "start_s": 0.25 * i, "end_s": 0.25 * i + 0.1} for i, p in enumerate((36, 42, 38, 42, 36, 46, 38, 49))]
    return [{"pitch": p, "velocity": v, "start_s": 0.5 * i, "end_s": 0.5 * i + 0.45} for i, (p, v) in enumerate(((40, 60), (43, 90), (45, 120), (47, 80)))]


def test_01_sfz_and_sf2_byte_determinism() -> None:
    cases = [("finger_bass_yr__Finger_Bass_YR", False), ("fluidr3_gm__Rhodes_EP_0_4", False), ("musescore_general__Standard_128_0", True), ("avl_drumkits_sf2__AVL_Black_Pearl_4pc", True),
             ("salamander_drumkit__Salamander_Drumkit_OH_mics", True)]
    with tempfile.TemporaryDirectory() as td:
        for pid, drums in cases:
            patch = POOL["patches"][pid]
            ch = backends.midi_channel_for(patch, "drums" if drums else "bass")
            assert ch == (9 if (patch["backend"] == "sf2" and patch.get("bank") == 128) else 0), (pid, ch)
            mid = Path(td) / f"{pid}.mid"
            midi_io.write_midi(_notes(drums), mid, 120.0, channel=ch, program=patch.get("program") if patch["backend"] == "sf2" else None,
                               bank=patch.get("bank") if patch["backend"] == "sf2" else None, song_len_s=3.0)
            shas = []
            for k in range(2):
                m = backends.render_stem(mid, patch, Path(td) / f"{pid}_{k}.wav")
                shas.append(m["wav_sha256"])
                assert m["backend"] == patch["backend"] and m["deterministic"] and m["midi_sha256"] == hashlib.sha256(mid.read_bytes()).hexdigest()
            assert shas[0] == shas[1], pid
            level = _rms_db(Path(td) / f"{pid}_0.wav")
            assert level > -60.0, (pid, level)
            print(f"  {pid}: identical sha {shas[0][:12]} rms {level:.1f} dBFS ({m['wall_s']}s)")
    print("test_01 PASS: sfz + sf2 renders byte-identical twice; bank-128 kit (ch 9) and bank-0 AVL kit (ch 0) both audible")


def test_02_dawdreamer_frozen_cache_contract(monkeypatch=None) -> None:
    """The frozen path copies a cached render keyed by sha256(midi bytes | patch identity) without touching dawdreamer."""
    with tempfile.TemporaryDirectory() as td:
        mid = Path(td) / "x.mid"
        midi_io.write_midi(_notes(False), mid, 120.0, song_len_s=2.0)
        patch = {"id": "surge_xt__Surge_XT_Pad_1", "backend": "dawdreamer", "plugin": "/usr/lib/vst3/Surge XT.vst3", "preset": "/usr/share/surge-xt/patches_factory/Pads/Pad 1.fxp",
                 "path": "/usr/share/surge-xt/patches_factory/Pads/Pad 1.fxp", "deterministic": False}
        key = backends.frozen_key(mid, patch)
        assert key == backends.frozen_key(mid, dict(patch, name="renamed")) and key != backends.frozen_key(mid, dict(patch, preset="/other.fxp"))
        frozen_dir = Path(td) / "frozen"
        frozen_dir.mkdir()
        import soundfile as sf
        fake = np.zeros((4410, 2), np.float32)
        fake[100, :] = 0.5
        sf.write(str(frozen_dir / f"{key}.wav"), fake, 44100)
        out = Path(td) / "out.wav"
        m = backends.render_stem(mid, patch, out, frozen_dir=frozen_dir)
        assert m["frozen"] and not m["rendered_now"] and m["frozen_key"] == key and not m["deterministic"]
        assert out.read_bytes() == (frozen_dir / f"{key}.wav").read_bytes()
    assert POOL["audition"]["pad"] and all(POOL["patches"][i]["backend"] == "dawdreamer" for i in POOL["audition"]["pad"])
    print("test_02 PASS: dawdreamer renders are frozen by (midi, patch) sha and replayed byte-identically")


if __name__ == "__main__":
    test_01_sfz_and_sf2_byte_determinism()
    test_02_dawdreamer_frozen_cache_contract()
