#!/usr/bin/python3
"""c83 S4 (M-3, characterization only) — unpaired MuScriptor starts per landed song x stem.

created: 2026-09-06T20:50:00Z
cycle: 83
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/unpaired-starts-characterization-c83

Pre-registration: data/v5/corpus/unpaired_starts_prereg_c83.json (must predate every output; asserted).
Reads canonical_v5_reindexed/<stem>.reindexed.json READ-ONLY for every song with a sidecar; an unpaired start is a
start whose `index` has no end event with start_event_index == index. Emits per-(song, stem) unpaired fraction,
25 s chunk histograms (unpaired + all starts), final-chunk concentration, per-chunk unpaired rate, and the
pre-declared descriptive label H1 / H2 / MIXED / TOO_FEW. NO threshold is a pass/fail; nothing is modified.
Output: data/v5/corpus/unpaired_starts_c83.json (--out overrides for the byte-det x2 run).
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
CORPUS = Path("data/v5/corpus")
PREREG = CORPUS / "unpaired_starts_prereg_c83.json"
OUT_DEFAULT = CORPUS / "unpaired_starts_c83.json"
STEMS = ["bass", "drums", "guitar", "other", "piano", "vocals", "full_mix"]
CHUNK_S = 25.0
MIN_N = 20
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _cv(xs: list) -> float | None:
    if len(xs) < 2:
        return None
    m = sum(xs) / len(xs)
    if m == 0:
        return None
    var = sum((x - m) ** 2 for x in xs) / len(xs)
    return round(math.sqrt(var) / m, 4)


def characterize(sha16: str, stem: str, duration_s: float) -> dict:
    p = CORPUS / sha16 / "canonical_v5_reindexed" / f"{stem}.reindexed.json"
    ev = json.loads(p.read_text())
    starts = [e for e in ev if e["type"] == "start"]
    ended = {e["start_event_index"] for e in ev if e["type"] == "end"}
    n_chunks = max(1, math.ceil(duration_s / CHUNK_S))
    hist_all = [0] * n_chunks
    hist_unp = [0] * n_chunks
    n_unp = 0
    for s in starts:
        k = min(n_chunks - 1, int(s["start_time"] // CHUNK_S))
        hist_all[k] += 1
        if s["index"] not in ended:
            hist_unp[k] += 1
            n_unp += 1
    n = len(starts)
    rate = [(round(u / a, 4) if a else None) for u, a in zip(hist_unp, hist_all)]
    final_unp_frac = (hist_unp[-1] / n_unp) if n_unp else None
    final_all_share = (hist_all[-1] / n) if n else None
    rate_dense = [u / a for u, a in zip(hist_unp, hist_all) if a >= MIN_N]
    cv = _cv(rate_dense)
    if n_unp < MIN_N:
        label = "TOO_FEW"
    elif final_unp_frac >= 0.5 and final_unp_frac >= 2 * final_all_share:
        label = "H1_tail_chunk_concentration"
    elif final_unp_frac < 2 * final_all_share and cv is not None and cv < 1.0:
        label = "H2_uniform_dense_stem_ambiguity"
    else:
        label = "MIXED"
    return {
        "reindexed_json_sha256": _sha(p),
        "n_starts": n, "n_unpaired": n_unp,
        "unpaired_fraction": round(n_unp / n, 4) if n else None,
        "n_chunks": n_chunks,
        "chunk_hist_all": hist_all, "chunk_hist_unpaired": hist_unp,
        "per_chunk_unpaired_rate": rate,
        "final_chunk_unpaired_fraction": round(final_unp_frac, 4) if final_unp_frac is not None else None,
        "final_chunk_share_of_all_starts": round(final_all_share, 4) if final_all_share is not None else None,
        "per_chunk_rate_cv_over_dense_chunks": cv,
        "n_dense_chunks_ge_20_starts": len(rate_dense),
        "label": label,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--songs-from", type=Path, default=None,
                    help="byte-det re-run: take the song list from an existing output JSON (a landing between runs must not change the set)")
    a = ap.parse_args(argv)
    prereg = json.loads(PREREG.read_text())
    prereg_mtime = PREREG.stat().st_mtime
    songs = sorted(p.parent.name for p in CORPUS.glob("*/canonical_v5_reindexed_sha256.json"))
    if a.songs_from is not None:
        songs = json.loads(a.songs_from.read_text())["songs"]
    per_song = {}
    tally = {"H1_tail_chunk_concentration": 0, "H2_uniform_dense_stem_ambiguity": 0, "MIXED": 0, "TOO_FEW": 0}
    per_stem_tally = {s: dict(tally) for s in STEMS}
    manifest = json.loads((CORPUS / "corpus_manifest.json").read_text())
    titles = {r["sha16"]: r.get("title", r["sha16"]) for r in manifest.get("songs", [])} if isinstance(manifest, dict) else {}
    for s in songs:
        tm = json.loads((CORPUS / s / "transcription_manifest.json").read_text())
        row = {"title": titles.get(s, s), "duration_s": tm["duration_s"], "bpm_v5": tm["bpm_v5"], "stems": {}}
        for stem in STEMS:
            if not (CORPUS / s / "canonical_v5_reindexed" / f"{stem}.reindexed.json").exists():
                continue
            c = characterize(s, stem, tm["duration_s"])
            row["stems"][stem] = c
            tally[c["label"]] += 1
            per_stem_tally[stem][c["label"]] += 1
        per_song[s] = row
    named = {}
    for s, stem in (("a9587ccde1b333f5", "other"), ("a9587ccde1b333f5", "vocals"), ("2b0370d9d0162c98", "other"), ("2b0370d9d0162c98", "vocals"),
                    ("51e433ade2a845e1", "bass"), ("252eb21ce7df7328", "other")):
        if s in per_song and stem in per_song[s]["stems"]:
            c = per_song[s]["stems"][stem]
            named[f"{s}/{stem}"] = {k: c[k] for k in ("n_starts", "n_unpaired", "unpaired_fraction", "final_chunk_unpaired_fraction",
                                                       "final_chunk_share_of_all_starts", "per_chunk_rate_cv_over_dense_chunks", "label")}
    dominant = max(tally, key=lambda k: (tally[k], k)) if any(tally.values()) else None
    classified = {k: v for k, v in tally.items() if k != "TOO_FEW"}
    dominant_classified = max(classified, key=lambda k: (classified[k], k)) if any(classified.values()) else None
    rec = {
        "schema_version": 1, "agent": "worker", "cycle": 83, "run_id": "run-2026-09-06T000000Z",
        "milestone": "M-V5-CORPUS-1/unpaired-starts-characterization-c83", "env_pin_sha256": ENV_PIN,
        "prereg_path": str(PREREG), "prereg_sha256": _sha(PREREG), "prereg_mtime_precedes_output": True,
        "hypotheses": prereg["hypotheses_pre_declared"], "chunk_s": CHUNK_S, "min_n_unpaired_to_classify": MIN_N,
        "n_songs": len(songs), "songs": songs, "per_song": per_song,
        "tally_all_cells": tally, "tally_per_stem": per_stem_tally,
        "dominant_label_all_cells": dominant, "dominant_label_classified_cells": dominant_classified,
        "named_cells_from_brief": named,
        "c84_candidate_if_H2_dominates": prereg["c84_candidates_named_if_H2_dominates"],
        "nothing_modified": "canonical_v5_reindexed/ READ-ONLY; no pairing changed (FD-1)",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    assert a.out.stat().st_mtime > prereg_mtime, "prereg must predate output"
    print(json.dumps({"tally": tally, "per_stem": per_stem_tally, "dominant": dominant, "dominant_classified": dominant_classified, "named": named}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
