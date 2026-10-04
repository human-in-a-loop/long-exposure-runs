#!/usr/bin/python3
"""v6 Phase 0 — thin wrapper around scripts/v5/velocity_v5.py (READ-ONLY import) for the 29-song corpus.

created: 2026-10-04
milestone: M-V6-DATA-0/velocity-v6-wrapper

Neutralises two hard-coded v5 assumptions WITHOUT editing scripts/v5:
  * velocity_v5.py:61 FOCUS = the five v5 focus songs (two absent here) and :253 `for sha16 in FOCUS` in build_profiles,
    :367 `args.songs or FOCUS` in main  ->  FOCUS is replaced (module global, looked up at call time) by every eligible
    song that has landed (transcription_manifest.json + muscriptor_full/ present, not tempo-/content-blocked);
  * velocity_v5.py:309-310 R1 = "drums + bass spread >= 6 dB on >= 4/5 songs" (literal 4 inside build_profiles) ->
    the v6 rule ">= 80 % of N songs" (ceil(0.8 N)) is evaluated here on the same per-song statistics and recorded
    under R1.drums_bass_pass_ge_80pct / R1.route_2_fallback_stems; the v5 keys are kept for byte-compat of readers.
Everything else (separation via htdemucs subprocess, 50 ms RMS, midrank mapping, sibling velocity MIDI, ladders) is
velocity_v5's own code. Progress log: data/v5/logs/velocity_v6.progress.json.
Discipline: /usr/bin/python3 guard; env pins (velocity_v5 sets them at import); no PRNG.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import FOCUS_ORDER, interpreter_guard, pin_env, read_json  # noqa: E402

pin_env()
interpreter_guard()
from scripts.v5 import velocity_v5 as V  # noqa: E402  READ-ONLY (module constants patched in-process only)
from scripts.v5.content_blocked import load_content_blocked  # noqa: E402

R1_MIN_FRAC = 0.8


def landed_eligible(corpus: Path, eligible_from: Path) -> list[str]:
    used = list(read_json(eligible_from)["gate"]["used"])
    blocked_p = corpus / "recanonicalization_blocked.json"
    blocked = set()
    if blocked_p.exists():
        d = read_json(blocked_p)
        blocked = set(d.get("blocked_songs", {})) - set(d.get("unblocked_c86", {}))
    content = load_content_blocked(corpus)
    out = []
    for s in used:
        if s in blocked or s in content:
            continue
        if (corpus / s / "transcription_manifest.json").exists() and (corpus / s / "muscriptor_full" / "drums.json").exists() \
                and (corpus / s / "canonical_v5_reindexed" / "drums.reindexed.json").exists():
            out.append(s)
    return out


def patch_r1(prof: dict, n_songs: int, min_frac: float = R1_MIN_FRAC) -> dict:
    need = int(math.ceil(min_frac * n_songs)) if n_songs else 0
    per_stem = prof["R1"]["songs_passing_per_stem"]
    verdict = {stem: (per_stem[stem] >= need and n_songs > 0) for stem in ("drums", "bass")}
    prof["R1"].update({
        "rule_v6": f"drums + bass spread >= {V.R1_MIN_SPREAD_DB} dB on >= {int(min_frac * 100)} % of N={n_songs} songs (ceil = {need})",
        "n_songs": n_songs, "min_songs_required": need, "drums_bass_pass_ge_80pct": verdict,
        "route_2_fallback_stems": [stem for stem in ("drums", "bass") if not verdict[stem]],
        "v5_rule_superseded": "drums_bass_pass_ge_4_of_5 is the v5 literal (velocity_v5.py:309-310); v6 verdict = drums_bass_pass_ge_80pct"})
    prof["wrapper"] = {"script": "scripts/v6/velocity_v6.py", "songs": list(V.FOCUS), "n_songs": n_songs, "r1_min_frac": min_frac}
    return prof


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 wrapper: velocity_v5 Route-1 extraction + profiles over every landed eligible song")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--eligible-from", default="data/v5/rules/eligible_c86.json")
    ap.add_argument("--songs", nargs="*", default=None, help="subset (default: every landed eligible song)")
    ap.add_argument("--x2-song", default=FOCUS_ORDER[0], help="song separated twice in-cycle (default WIG); 'none' to skip")
    ap.add_argument("--profiles-out", default="data/v5/rules/velocity_profiles_v5.json")
    ap.add_argument("--profiles-only", action="store_true")
    ap.add_argument("--groove", default="data/v5/rules/groove_v5_v2_full.json")
    ap.add_argument("--r1-min-frac", type=float, default=R1_MIN_FRAC)
    ap.add_argument("--skip-done", action="store_true", help="skip songs whose velocity_v5/velocities.json already exists")
    args = ap.parse_args(argv)
    os.chdir(_WS)
    corpus = Path(args.corpus_dir)
    songs = landed_eligible(corpus, Path(args.eligible_from))
    if args.songs:
        songs = [s for s in songs if s in set(args.songs)]
    if not songs:
        raise SystemExit("velocity_v6: no landed eligible song (transcription_manifest.json + muscriptor_full/ + canonical_v5_reindexed/ needed)")
    V.FOCUS = list(songs)  # build_profiles / main look FOCUS up as a module global at call time
    man = read_json("data/v5/corpus/corpus_manifest.json")
    meta = {s["sha16"]: s for s in man["songs"]}
    log_p = Path("data/v5/logs/velocity_v6.progress.json")
    log_p.parent.mkdir(parents=True, exist_ok=True)
    log = read_json(log_p) if log_p.exists() else {"schema_version": 1, "wrapper": "scripts/v6/velocity_v6.py", "per_song": {}}
    log["started"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log["songs"] = songs
    if not args.profiles_only:
        for s in songs:
            if args.skip_done and (corpus / s / "velocity_v5" / "velocities.json").exists():
                print(f"{s} skip (velocities.json present)")
                continue
            rec = V.process_song(s, meta[s], corpus, x2=(s == args.x2_song))
            log["per_song"][s] = rec
            sep = rec["separation"]
            print(f"{s} {str(rec['title'])[:24]:24s} sep {sep['wall_s']}s df peak {rec['df_pct_peak']}%; "
                  + "; ".join(f"{st} n={v['n']} spread={v['spread_db']}dB" for st, v in rec["stems"].items()), flush=True)
            log_p.write_text(json.dumps(log, sort_keys=True, indent=1) + "\n")
    missing = [s for s in songs if not (corpus / s / "velocity_v5" / "velocities.json").exists()]
    if missing:
        raise SystemExit(f"velocity_v6: velocities.json missing for {missing}; run without --profiles-only")
    groove = read_json(args.groove) if Path(args.groove).exists() else {}
    prof = V.build_profiles(log.get("per_song", {}), corpus, groove)
    prof = patch_r1(prof, len(songs), args.r1_min_frac)
    Path(args.profiles_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.profiles_out).write_text(json.dumps(prof, sort_keys=True, indent=1) + "\n")
    print(f"profiles -> {args.profiles_out}; N={len(songs)}; R1 v6 {prof['R1']['drums_bass_pass_ge_80pct']} (per stem {prof['R1']['songs_passing_per_stem']}); "
          f"route-2 fallback {prof['R1']['route_2_fallback_stems']}; R2 {prof['R2']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
