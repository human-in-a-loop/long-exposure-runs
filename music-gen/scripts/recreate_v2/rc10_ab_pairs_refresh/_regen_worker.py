"""Venv-side worker: regenerate other_vocals winner MIDIs (5 songs × 2 stems).

Invoked via subprocess by regenerate_other_vocals_winners.py.
Uses c53 helpers from scripts.recreate_v2.rc10_other_vocals.run_rc10 verbatim.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# c48 env-var flags default OFF
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

WS = Path("/home/user/long-exposure-runs/music-gen")
sys.path.insert(0, str(WS))

from scripts.recreate_v2.rc10_other_vocals.run_rc10 import (  # noqa: E402
    _bp_predict,
    _chroma_chord_track,
    _extract_window,
    _load_rc5_bpm,
    _postprocess,
)


def _load_focus() -> list[dict]:
    return json.loads((WS / "data/recreate_v2/focus_set_v2.json").read_text())["songs"]


def _load_winner_type() -> dict:
    return json.loads((WS / "data/rc10_impl/other_vocals/winner_per_stem_type.json").read_text())


def _regen_song(song: dict, work_root: Path) -> dict:
    """Regenerate winner MIDIs for one song (vocals + other_residual)."""
    import soundfile as sf

    sha16 = song["audio_sha16"]
    section = song["chosen_section"]
    t0, t1 = float(section["t_start_s"]), float(section["t_end_s"])
    bpm = _load_rc5_bpm(sha16)

    base_dir = WS / f"data/recreate_v2/baseline/{sha16}/rc9_6stem"
    vocals_full = base_dir / "vocals.wav"
    other_full = base_dir / "other.wav"

    song_work = work_root / sha16
    song_work.mkdir(parents=True, exist_ok=True)

    stem_dur = sf.info(str(vocals_full)).duration
    vocals_win = song_work / "vocals_window.wav"
    other_win = song_work / "other_window.wav"
    if t1 <= stem_dur + 0.01:
        _extract_window(vocals_full, vocals_win, t0, t1)
        _extract_window(other_full, other_win, t0, t1)
        section_source = "chosen_section"
    else:
        _extract_window(vocals_full, vocals_win, 0.0, stem_dur)
        _extract_window(other_full, other_win, 0.0, stem_dur)
        section_source = f"baseline_full_0..{stem_dur:.2f}s (chosen_section {t0:.1f}..{t1:.1f}s out of range)"

    out_dir_vocals = WS / f"data/rc10_impl/other_vocals/per_song/{sha16}/vocals"
    out_dir_other = WS / f"data/rc10_impl/other_vocals/per_song/{sha16}/other_residual"
    out_dir_vocals.mkdir(parents=True, exist_ok=True)
    out_dir_other.mkdir(parents=True, exist_ok=True)

    # vocals winner: v_a postprocessed (basic-pitch defaults + D4)
    v_raw = song_work / "vocals_va_raw.mid"
    v_pp = song_work / "vocals_va_pp.mid"
    _bp_predict(vocals_win, v_raw, tuned=False)
    _postprocess(v_raw, v_pp, vocals_win, bpm, "vocals")
    vocals_winner = out_dir_vocals / "winner.mid"
    import shutil

    shutil.copy(v_pp, vocals_winner)

    # other_residual winner: o_b raw (chroma_cqt chord track, no postprocessing)
    o_raw = song_work / "other_ob_raw.mid"
    _chroma_chord_track(other_win, o_raw, bpm)
    other_winner = out_dir_other / "winner.mid"
    shutil.copy(o_raw, other_winner)

    return {
        "sha16": sha16,
        "section_source": section_source,
        "bpm": bpm,
        "vocals_winner_path": str(vocals_winner.relative_to(WS)),
        "other_residual_winner_path": str(other_winner.relative_to(WS)),
    }


def main() -> int:
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="rc10_regen_", dir=str(WS / "tmp/rc10_ab_refresh")))
    (WS / "tmp/rc10_ab_refresh").mkdir(parents=True, exist_ok=True)

    winner_type = _load_winner_type()
    assert winner_type["vocals"]["candidate"] == "v_a" and winner_type["vocals"]["postprocessed"] is True, (
        winner_type
    )
    assert (
        winner_type["other_residual"]["candidate"] == "o_b"
        and winner_type["other_residual"]["postprocessed"] is False
    ), winner_type

    songs = _load_focus()
    results = []
    for song in songs:
        r = _regen_song(song, tmp)
        results.append(r)
        print(f"[regen] {r['sha16']} vocals+other_residual", flush=True)
    manifest = {
        "winner_per_stem_type_source": "data/rc10_impl/other_vocals/winner_per_stem_type.json",
        "winner_per_stem_type": winner_type,
        "songs": results,
    }
    out = WS / "data/rc10_ab_pairs_refresh/other_vocals_regen_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"[regen] manifest → {out.relative_to(WS)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
