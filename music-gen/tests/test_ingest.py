"""Ingestion chassis tests (M-INGEST-1).

We avoid pytest (not installed in this workspace); this file exposes
``run_all()`` returning ``(passed, failed, details)`` and prints a
compact summary when invoked as ``python -m tests.test_ingest`` or
``python tests/test_ingest.py``.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Callable

from scripts.ingest import chunker, harvester, provenance, seed_gen
from scripts.ingest.chunker import CLIP_S, HOP_S, OVERLAP_S, chunk, plan_clips
from scripts.ingest.provenance import (
    read_manifest,
    validate_manifest,
    write_manifest,
)
from scripts.ingest.wavio import read_pcm16_mono, write_pcm16_mono

SEED_DIR = Path("data/ingestion/seed")
CLIP_DIR = Path("data/ingestion/clips")
MANIFEST_DIR = Path("data/ingestion/manifests")


# --------------------------- test helpers ---------------------------

def _ensure_seeds() -> None:
    if not (SEED_DIR / "seed_long_87s.wav").exists():
        seed_gen.generate_all(SEED_DIR)


def _chunk_one(name: str, tmp: Path) -> tuple[Path, Path]:
    src = SEED_DIR / name
    clip_root = tmp / "clips"
    man = tmp / "manifests" / f"{src.stem}.manifest.jsonl"
    res = chunk(src, clip_root, source_type="local",
                source_ref=str(src.resolve()))
    write_manifest(res, "local", str(src.resolve()), man)
    return src, man


# --------------------------- chunker tests --------------------------

def test_determinism_across_runs() -> None:
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
        _, ma = _chunk_one("seed_mid_50s.wav", Path(ta))
        _, mb = _chunk_one("seed_mid_50s.wav", Path(tb))
        _, ca = read_manifest(ma)
        _, cb = read_manifest(mb)
        assert len(ca) == len(cb) == 2
        for x, y in zip(ca, cb):
            assert x["clip_bytes_sha256"] == y["clip_bytes_sha256"], (x, y)


def test_overlap_invariant_standard() -> None:
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        _, m = _chunk_one("seed_mid_50s.wav", Path(t))
        src, clips = read_manifest(m)
        # standard: hop-strided clip 0 -> [0,30]; then anchored final at [20,50].
        assert clips[0]["t_start_s"] == 0.0
        assert abs(clips[0]["t_end_s"] - 30.0) < 1e-6
        # Overlap is 10s (anchored) here, but still >= 5.
        overlap = clips[0]["t_end_s"] - clips[1]["t_start_s"]
        assert overlap + 1e-6 >= OVERLAP_S


def test_tail_anchored_final_clip() -> None:
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        _, m = _chunk_one("seed_long_87s.wav", Path(t))
        src, clips = read_manifest(m)
        assert len(clips) == 4
        # standard middle overlaps == 5.0 exactly (sample-accurate).
        eps = 1.0 / src["sr_hz"]
        std_overlap = clips[1]["t_end_s"] - clips[2]["t_start_s"]
        assert abs(std_overlap - OVERLAP_S) < eps + 1e-9, std_overlap
        # final is anchored: ends at duration; overlap with prior > 5 s.
        last = clips[-1]
        prev = clips[-2]
        assert last["anchored_tail"] is True
        assert abs(last["t_end_s"] - src["duration_s"]) < eps
        anchored_overlap = prev["t_end_s"] - last["t_start_s"]
        assert anchored_overlap > OVERLAP_S


def test_short_song_single_clip() -> None:
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        _, m = _chunk_one("seed_short_22s.wav", Path(t))
        src, clips = read_manifest(m)
        assert len(clips) == 1
        assert clips[0]["short_song"] is True
        assert clips[0]["n_samples"] < int(round(CLIP_S * src["sr_hz"]))
        # spans the whole source.
        assert clips[0]["t_start_s"] == 0.0
        assert abs(clips[0]["t_end_s"] - src["duration_s"]) < 1e-6


def test_boundary_appears_in_two_clips() -> None:
    """A tone-change boundary in the 5 s overlap should appear in both
    the clip ending just after it AND the clip starting just before it.
    We check the 25 s mark, which is a boundary in seed_mid_50s."""
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        _, m = _chunk_one("seed_mid_50s.wav", Path(t))
        _, clips = read_manifest(m)
        boundary_s = 25.0
        for c in clips:
            assert c["t_start_s"] <= boundary_s <= c["t_end_s"], (
                f"boundary {boundary_s}s missing from clip idx={c['clip_index']}"
            )


# --------------------------- provenance tests -----------------------

def test_schema_required_fields_pass() -> None:
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        _, m = _chunk_one("seed_mid_50s.wav", Path(t))
        errs = validate_manifest(m)
        assert errs == [], errs


def test_schema_bad_manifest_fails() -> None:
    with tempfile.TemporaryDirectory() as t:
        m = Path(t) / "bad.manifest.jsonl"
        m.write_text(
            json.dumps({"kind": "source", "schema_v": 1, "source_id": "x",
                        "source_type": "local", "source_ref": "y",
                        "sr_hz": 22050, "n_samples": 1, "duration_s": 0.0,
                        "bytes_sha256": "z", "chunker_version": "v",
                        "tail_rule": "anchored", "ingest_ts": "now"}) + "\n"
            # missing every clip field
            + json.dumps({"kind": "clip", "schema_v": 1}) + "\n"
        )
        errs = validate_manifest(m, check_clip_files=False)
        assert any("missing field" in e for e in errs), errs


def test_replay_round_trip() -> None:
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        tp = Path(t)
        src, m = _chunk_one("seed_long_87s.wav", tp)
        # nuke the clip directory; replay should recreate identical bytes.
        clip_root = tp / "clips"
        shutil.rmtree(clip_root)
        mismatches = provenance.replay(m, src, clip_root)
        assert mismatches == [], mismatches


def test_append_only_no_duplicates() -> None:
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        _, m = _chunk_one("seed_mid_50s.wav", Path(t))
        # inject a duplicate clip row
        rows = m.read_text().splitlines()
        rows.append(rows[-1])
        m.write_text("\n".join(rows) + "\n")
        errs = validate_manifest(m)
        assert any("duplicate" in e for e in errs), errs


def test_container_invariance() -> None:
    """Copying the same seed WAV to a differently named file must give
    the same source_id: source_id is a function of decoded samples."""
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        tp = Path(t)
        srcA = SEED_DIR / "seed_short_22s.wav"
        srcB = tp / "renamed.wav"
        shutil.copyfile(srcA, srcB)
        a = chunk(srcA, tp / "a", source_type="local", source_ref=str(srcA))
        b = chunk(srcB, tp / "b", source_type="local", source_ref=str(srcB))
        assert a.source_id == b.source_id


# --------------------------- harvester tests ------------------------

def test_local_and_youtube_manifest_parity() -> None:
    """local_folder(seed) and youtube_playlist(mocked to drop the same
    seed) must produce structurally identical manifests once source_type
    and source_ref are normalized."""
    _ensure_seeds()
    with tempfile.TemporaryDirectory() as t:
        tp = Path(t)
        # local door
        local_in = tp / "local_in"
        local_in.mkdir()
        shutil.copyfile(SEED_DIR / "seed_short_22s.wav",
                        local_in / "seed_short_22s.wav")
        local_manifests = harvester.local_folder(
            local_in, tp / "clips_L", tp / "manifests_L",
        )
        assert len(local_manifests) == 1

        # youtube door with subprocess mocked
        def fake_runner(cmd, capture_output=True, text=True, timeout=None):
            # Simulate yt-dlp having downloaded a single file into -o dir.
            out_arg = cmd[cmd.index("-o") + 1]
            out_dir = Path(out_arg).parent
            out_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SEED_DIR / "seed_short_22s.wav",
                            out_dir / "FAKEVID11ID.wav")
            class R:
                returncode = 0
                stdout = ""
                stderr = ""
            return R()

        yt_manifests = harvester.youtube_playlist(
            "https://youtube.com/playlist?list=FAKEPL",
            tp / "clips_Y", tp / "manifests_Y",
            runner=fake_runner,
        )
        assert len(yt_manifests) == 1

        s_l, c_l = read_manifest(local_manifests[0])
        s_y, c_y = read_manifest(yt_manifests[0])
        # After normalizing the two known differences:
        for f in ("source_type", "source_ref", "ingest_ts"):
            s_l.pop(f, None); s_y.pop(f, None)
        assert s_l == s_y, (s_l, s_y)
        assert s_l["source_id"] == s_y.get("source_id", s_l["source_id"])
        # (source_id was popped via .pop above? no we popped only 3 keys)
        # clip rows should match on every field except clip_path
        for x, y in zip(c_l, c_y):
            x2 = {k: v for k, v in x.items() if k != "clip_path"}
            y2 = {k: v for k, v in y.items() if k != "clip_path"}
            assert x2 == y2, (x2, y2)


def test_youtube_egress_failure_logged_not_raised() -> None:
    with tempfile.TemporaryDirectory() as t:
        tp = Path(t)
        # point EGRESS_LOG at a temp file
        import scripts.ingest.harvester as H
        orig = H.EGRESS_LOG
        H.EGRESS_LOG = tp / "egress.jsonl"
        try:
            def fail_runner(cmd, capture_output=True, text=True, timeout=None):
                class R:
                    returncode = 1
                    stdout = ""
                    stderr = "proxy connect denied"
                return R()
            got = H.youtube_playlist("https://youtube.com/playlist?list=X",
                                     tp / "cY", tp / "mY", runner=fail_runner)
            assert got == []
            assert H.EGRESS_LOG.exists()
            rows = [json.loads(l) for l in H.EGRESS_LOG.read_text().splitlines() if l.strip()]
            assert rows and rows[-1]["event"] == "youtube_playlist_failed"
        finally:
            H.EGRESS_LOG = orig


# --------------------------- egress probe tests ---------------------

def test_egress_probe_returns_within_timeout() -> None:
    """Probe must return a dict within 20 s wall-clock even if the
    network is blackholed. Uses the real probe function; if the
    workspace has no network, both stages time out cleanly."""
    from scripts.ingest import egress_probe as E
    import time
    t0 = time.monotonic()
    rec = E.probe(timeout_s=8.0)
    dt = time.monotonic() - t0
    assert isinstance(rec, dict)
    for k in ("ts", "metadata_ok", "media_ok", "note"):
        assert k in rec, k
    assert dt < 20.0, f"probe took {dt:.1f}s"


def test_egress_probe_appends_status_line() -> None:
    from scripts.ingest import egress_probe as E
    log = E.EGRESS_LOG
    log.parent.mkdir(parents=True, exist_ok=True)
    before = sum(1 for _ in log.open()) if log.exists() else 0
    E.probe(timeout_s=8.0)
    after = sum(1 for _ in log.open())
    assert after == before + 1, (before, after)


# --------------------------- runner ---------------------------------

TESTS: list[Callable[[], None]] = [
    test_determinism_across_runs,
    test_overlap_invariant_standard,
    test_tail_anchored_final_clip,
    test_short_song_single_clip,
    test_boundary_appears_in_two_clips,
    test_schema_required_fields_pass,
    test_schema_bad_manifest_fails,
    test_replay_round_trip,
    test_append_only_no_duplicates,
    test_container_invariance,
    test_local_and_youtube_manifest_parity,
    test_youtube_egress_failure_logged_not_raised,
    test_egress_probe_returns_within_timeout,
    test_egress_probe_appends_status_line,
]


def run_all() -> tuple[int, int, list[tuple[str, str]]]:
    passed = failed = 0
    details: list[tuple[str, str]] = []
    for t in TESTS:
        try:
            t()
            passed += 1
            details.append((t.__name__, "PASS"))
            print(f"PASS {t.__name__}")
        except Exception as exc:
            failed += 1
            tb = traceback.format_exc(limit=3)
            details.append((t.__name__, f"FAIL: {exc}"))
            print(f"FAIL {t.__name__}: {exc}\n{tb}")
    return passed, failed, details


if __name__ == "__main__":
    p, f, _ = run_all()
    print(f"\n{p} passed, {f} failed")
    sys.exit(0 if f == 0 else 1)
