#!/usr/bin/python3
"""c81 P5 tests — reindex hygiene (harmony refuses the lossy dir; sidecar SHAs match disk; hook on a two-chunk fixture).

created: 2026-09-06T17:20:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle81-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_reindex_hygiene_c81.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v5 import harmony_v5 as H  # noqa: E402
from scripts.v5 import reindex_hook as RH  # noqa: E402
from scripts.v3_spine.midi_from_json_events import serialize  # noqa: E402  READ-ONLY
import mido  # noqa: E402

CORPUS = _ROOT / "data/v5/corpus"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _note_on(p: Path) -> int:
    return sum(1 for tr in mido.MidiFile(str(p)).tracks for m in tr if m.type == "note_on" and m.velocity > 0)


def _two_chunk_fixture() -> list:
    """Two 30 s chunks re-offset by the READ-ONLY merge but with COLLIDING chunk-local indices 0..2 (the c80 defect)."""
    ev = []
    for chunk, off in ((0, 0.0), (1, 25.0)):
        for i in range(3):
            st = off + 1.0 + i
            ev.append({"type": "start", "index": i, "start_time": st, "pitch": 60 + i, "instrument": "acoustic_piano"})
            ev.append({"type": "end", "start_event_index": i, "end_time": st + 0.5, "pitch": 60 + i, "instrument": "acoustic_piano"})
    return ev


def test_01_harmony_refuses_lossy_dir_and_preference_tuple_is_lossless_only() -> None:
    assert "canonical_midi_full" not in H.MIDI_DIR_PREFERENCE
    assert H.MIDI_DIR_PREFERENCE == ("canonical_v5c_reindexed", "canonical_v5_reindexed")
    src = (_ROOT / "scripts/v5/harmony_v5.py").read_text()
    assert 'for sub in ("canonical_v5b", "canonical_v5_reindexed", "canonical_midi_full")' not in src
    with tempfile.TemporaryDirectory(prefix="hyg_t01_") as td:
        d = Path(td) / "deadbeefdeadbeef"
        (d / "canonical_midi_full").mkdir(parents=True)
        raw = d / "raw.json"
        raw.write_text(json.dumps(_two_chunk_fixture()))
        for stem in H.HARMONY_STEMS:
            serialize(str(raw), str(d / "canonical_midi_full" / f"{stem}.mid"), 120.0, (4, 4))
        (d / "transcription_manifest.json").write_text(json.dumps({"bpm_v5": 120.0, "title": "fixture", "note_counts": {}}))
        try:
            H.analyse_song("deadbeefdeadbeef", Path(td))
            raise AssertionError("harmony_v5 must raise MISSING_REINDEX when only the lossy dir exists")
        except H.MissingReindexError as e:
            assert "MISSING_REINDEX" in str(e) and "deadbeefdeadbeef" in str(e)
    print("test_01 PASS: harmony_v5 raises MissingReindexError on a lossy-only song; preference tuple lossless-only")


def test_02_sidecar_shas_match_disk_for_every_landed_song() -> None:
    landed = sorted(p.parent for p in CORPUS.glob("*/transcription_manifest.json"))
    assert len(landed) >= 3
    for d in landed:
        side_p = d / RH.SIDECAR_NAME
        assert side_p.exists(), f"missing sidecar for {d.name}"
        side = json.loads(side_p.read_text())
        rd = d / RH.OUT_SUBDIR
        assert side["reindex_manifest_sha256"] == _sha(rd / "reindex_manifest.json")
        for p, s in side["midi_sha256"].items():
            assert s == _sha(rd / f"{p}.mid"), (d.name, p)
        assert len(side["midi_sha256"]) == 7
        # lossless by count: reindexed MIDI note_on == JSON starts per probe
        rm = json.loads((rd / "reindex_manifest.json").read_text())
        for p, st in rm["probes"].items():
            assert _note_on(rd / f"{p}.mid") == st["n_starts_in"], (d.name, p)
    print(f"test_02 PASS: sidecars match disk + reindexed MIDI note_on == JSON starts for {[d.name for d in landed]}")


def test_03_hook_reindexes_two_chunk_fixture_losslessly() -> None:
    with tempfile.TemporaryDirectory(prefix="hyg_t03_") as td:
        corpus = Path(td)
        sha16 = "feedfacefeedface"
        d = corpus / sha16
        (d / "muscriptor_full").mkdir(parents=True)
        (d / "canonical_midi_full").mkdir()
        for p in RH.PROBES:
            (d / "muscriptor_full" / f"{p}.json").write_text(json.dumps(_two_chunk_fixture() if p in ("piano", "other") else []))
        (d / "transcription_manifest.json").write_text(json.dumps({"bpm_v5": 120.0, "title": "fixture"}))
        # the READ-ONLY serializer on the raw JSON is lossy (3 of 6 starts survive) — the defect the hook fixes
        serialize(str(d / "muscriptor_full/piano.json"), str(d / "canonical_midi_full/piano.mid"), 120.0, (4, 4))
        assert _note_on(d / "canonical_midi_full/piano.mid") == 3
        rec = RH.post_canonicalize(sha16, corpus)
        assert rec["reindex"]["piano"] == {"n_starts_in": 6, "n_paired": 6, "n_unpaired_starts": 0}
        assert _note_on(d / RH.OUT_SUBDIR / "piano.mid") == 6
        assert (d / RH.SIDECAR_NAME).exists() and (d / RH.OUT_SUBDIR / "reindex_manifest.json").exists()
        side = json.loads((d / RH.SIDECAR_NAME).read_text())
        assert side["midi_sha256"]["piano"] == _sha(d / RH.OUT_SUBDIR / "piano.mid")
        # idempotent catch-up loop reports 'present' on the second pass
        assert RH.reindex_landed(corpus) == [(sha16, "present")]
    print("test_03 PASS: two-chunk fixture — lossy serializer keeps 3/6, hook recovers 6/6 + sidecar; catch-up idempotent")


def test_04_driver_calls_hook_after_manifest_and_ast_is_clean() -> None:
    src = (_ROOT / "scripts/v5/transcribe_full_length.py").read_text()
    assert "from scripts.v5 import reindex_hook as _reindex_hook" in src
    i_manifest = src.index('(work / "transcription_manifest.json").write_text')
    i_hook = src.index("_reindex_hook.post_canonicalize(sha16")
    assert i_manifest < i_hook, "hook must fire after the manifest is written (sidecar pins the on-disk manifest sha)"
    forbidden_mods = {"random", "secrets"}
    forbidden_names = {"sidecar_nonfactor", "get_state", "save_state", "save_preset", "load_state", "set_state"}
    for path in ("scripts/v5/reindex_hook.py", "scripts/v5/transcribe_full_length.py", "scripts/v5/harmony_v5.py"):
        tree = ast.parse((_ROOT / path).read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [x.name for x in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                for n in names:
                    assert n.split(".")[0] not in forbidden_mods, (path, n)
                    assert "sidecar_nonfactor" not in n
            if isinstance(node, ast.Attribute):
                assert node.attr not in forbidden_names, (path, node.attr)
    print("test_04 PASS: driver imports the hook and calls it after the manifest write; AST clean on 3 scripts")


def test_05_tempo_v5b_summary_c81_anchor_source() -> None:
    new = (CORPUS / "tempo_v5b_summary_c81.tsv").read_text().splitlines()
    old = (CORPUS / "tempo_v5b_summary.tsv").read_text().splitlines()
    hdr = new[0].split("\t")
    assert "anchor_source" in hdr and len(new) == len(old) == 27
    wig_new = dict(zip(hdr, next(l for l in new[1:] if l.startswith("252eb21ce7df7328")).split("\t")))
    assert abs(float(wig_new["anchor_bpm"]) - 99.384014) < 1e-6 and wig_new["anchor_source"].startswith("librosa_full_mix_c79")
    wig_old = next(l for l in old[1:] if l.startswith("252eb21ce7df7328")).split("\t")
    assert wig_old[4].startswith("50.17"), "c80 file must be left untouched"
    print("test_05 PASS: tempo_v5b_summary_c81.tsv carries anchor_source; WIG anchor 99.384 (librosa_full_mix_c79); c80 file untouched")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} reindex_hygiene_c81 tests PASS")
