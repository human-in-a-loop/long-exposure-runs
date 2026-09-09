#!/usr/bin/python3
"""c85 F4 — operator adjudication of the two tempo-blocked focus songs (Peach Dream, Disco A) under the pre-registered
half/double-time check. NOT a fifth unaided tempo criterion (v5/v5b/v5c/v5d all RULES_OUT; the tempo axis is STOPPED).

created: 2026-09-09T22:05:10Z
cycle: 85
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo-f4-preregistered-c85

Authority: docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt item F4 (sha cf7296cf…). Prereg (written FIRST,
mtime-gated): data/v5/corpus/tempo_f4_prereg_c85.json. Inputs READ-ONLY: data/v5/corpus/<sha16>/{tempo_v5d.json,
tempo_mechanism_c82.json, transcription_manifest.json}. No autocorrelation is recomputed; the adopted candidate is the on-disk
tempo_v5d winner and the candidate set is the on-disk c82 refined list. Three sub-checks per song (see prereg operational
definitions): half/double (T/2 and 2T candidates both STRICTLY lower s_ref), drum onsets per beat in [0.5, 4], adopted bpm within
±2 of the c22 anchor. Verdict enum: F4_RESOLVED / F4_HALF_DOUBLE_AMBIGUOUS / F4_FAILS. FD-1: nothing is retuned on failure.
Writes tempo_f4_verdict_c85.json (--out-dir for the x2 byte-det run). data/v5/corpus/recanonicalization_blocked.json is never
touched. Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
PREREG = "data/v5/corpus/tempo_f4_prereg_c85.json"
BLOCKED = "data/v5/corpus/recanonicalization_blocked.json"
BLOCKED_SHA_PREFIX = "2fbabc07849dbe23"
GUIDANCE = "docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt"
GUIDANCE_SHA = "cf7296cfcf70c27757e5dda55edd758cc3cbc3d854c253f3d726603c05b283b7"
SCOPE = {"88d247468cb6d49f": {"title": "Peach Dream", "anchor_bpm": 123.046875},
         "cdd2717e52820ff6": {"title": "Disco A", "anchor_bpm": 120.18531976744185}}
LAG_TOL = 0.15          # relative distance of a candidate's lag_ref from T/2 or 2T
ONSETS_BAND = (0.5, 4.0)
ANCHOR_TOL_BPM = 2.0
ENUM = ("F4_RESOLVED", "F4_HALF_DOUBLE_AMBIGUOUS", "F4_FAILS")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _nearest(cands: list[dict], target_lag: float, tol: float = LAG_TOL) -> dict | None:
    """Candidate whose lag_ref is nearest to target_lag, accepted only within tol (relative); ties -> lower lag_ref (deterministic)."""
    best = None
    for c in sorted(cands, key=lambda c: (abs(c["lag_ref"] - target_lag), c["lag_ref"])):
        if abs(c["lag_ref"] - target_lag) / target_lag <= tol:
            best = c
        break
    return best


def half_double_check(cands: list[dict], adopted: dict, tol: float = LAG_TOL) -> dict:
    """Pre-registered sub-check: the T/2 and 2T candidates must BOTH have s_ref STRICTLY lower than the adopted s_ref.
    An absent candidate (none within tol of T/2 or 2T) FAILS the sub-check (cannot be established)."""
    T, s_adopt = float(adopted["lag_ref"]), float(adopted["s_ref"])
    out = {"adopted": {"lag_ref": T, "bpm_ref": adopted.get("bpm_ref"), "s_ref": s_adopt}, "lag_tol_rel": tol}
    for name, target in (("half", T / 2.0), ("double", 2.0 * T)):
        c = _nearest(cands, target, tol)
        if c is None:
            out[name] = {"target_lag": round(target, 6), "candidate": None, "scores_lower": False, "reason": "no candidate within tol"}
        else:
            out[name] = {"target_lag": round(target, 6), "candidate": {"lag_ref": c["lag_ref"], "bpm_ref": c.get("bpm_ref"), "s_ref": c["s_ref"]},
                         "rel_lag_error": round(abs(c["lag_ref"] - target) / target, 6),
                         "s_ref_minus_adopted": round(float(c["s_ref"]) - s_adopt, 6), "scores_lower": bool(float(c["s_ref"]) < s_adopt)}
    out["passes"] = bool(out["half"]["scores_lower"] and out["double"]["scores_lower"])
    return out


def adjudicate_song(sha16: str, corpus: Path) -> dict:
    d = corpus / sha16
    v5d_p, c82_p, tm_p = d / "tempo_v5d.json", d / "tempo_mechanism_c82.json", d / "transcription_manifest.json"
    v5d, c82, tm = (json.loads(p.read_text()) for p in (v5d_p, c82_p, tm_p))
    adopted = v5d["winner"]
    assert adopted["bpm_ref"] == v5d["bpm_v5d"], (sha16, "winner != bpm_v5d")
    cands = c82["candidates"]
    assert any(c["lag_ref"] == adopted["lag_ref"] and c["s_ref"] == adopted["s_ref"] for c in cands), (sha16, "adopted not in c82 candidate set")
    bpm = float(adopted["bpm_ref"])
    hd = half_double_check(cands, adopted)
    n_drum = int(tm["note_counts"]["drums"]["n_note_on"])
    dur = float(tm["duration_s"])
    n_beats = dur * bpm / 60.0
    opb = n_drum / n_beats
    onsets = {"drums_n_note_on": n_drum, "duration_s": dur, "n_beats_at_adopted_bpm": round(n_beats, 6), "onsets_per_beat": round(opb, 6),
              "band": list(ONSETS_BAND), "passes": bool(ONSETS_BAND[0] <= opb <= ONSETS_BAND[1])}
    anchor = SCOPE[sha16]["anchor_bpm"]
    assert c82["anchor_bpm"] == anchor, (sha16, "anchor mismatch vs c82 record")
    anc = {"c22_anchor_bpm": anchor, "adopted_bpm": bpm, "delta_bpm": round(bpm - anchor, 6), "abs_delta_bpm": round(abs(bpm - anchor), 6),
           "tol_bpm": ANCHOR_TOL_BPM, "passes": bool(abs(bpm - anchor) <= ANCHOR_TOL_BPM)}
    return {"sha16": sha16, "title": SCOPE[sha16]["title"], "adopted_bpm": bpm, "adopted_lag_ref": adopted["lag_ref"], "adopted_s_ref": adopted["s_ref"],
            "bpm_v5_on_disk": v5d["bpm_v5"], "bpm_v5c_on_disk": v5d["bpm_v5c"], "bpm_v5d_on_disk": v5d["bpm_v5d"],
            "pick_band_bpm": v5d["pick_band_bpm"], "n_candidates": len(cands),
            "candidates": [{k: c[k] for k in ("lag_int", "lag_ref", "bpm_ref", "s_ref", "ac_T", "ac_half", "ac_double", "in_pick_band")} for c in cands],
            "half_double": hd, "onsets_per_beat": onsets, "anchor": anc,
            "all_three_pass": bool(hd["passes"] and onsets["passes"] and anc["passes"]),
            "inputs": {"tempo_v5d": {"path": str(v5d_p), "sha256": _sha(v5d_p)}, "tempo_mechanism_c82": {"path": str(c82_p), "sha256": _sha(c82_p)},
                       "transcription_manifest": {"path": str(tm_p), "sha256": _sha(tm_p)}}}


def verdict_of(songs: list[dict]) -> str:
    if all(s["all_three_pass"] for s in songs):
        return "F4_RESOLVED"
    if any(not s["half_double"]["passes"] for s in songs):
        return "F4_HALF_DOUBLE_AMBIGUOUS"
    return "F4_FAILS"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="c85 F4 tempo adjudication (operator authority; pre-registered)")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--prereg", default=PREREG)
    ap.add_argument("--out-dir", default="data/v5/corpus", help="byte-det x2: fresh mkdtemp")
    ap.add_argument("--out-name", default="tempo_f4_verdict_c85.json")
    a = ap.parse_args(argv)
    os.chdir(_WS)
    prereg_p = Path(a.prereg)
    prereg = json.loads(prereg_p.read_text())
    assert prereg["scope"] == list(SCOPE) and prereg["verdict_enum"] == list(ENUM), "prereg scope/enum mismatch"
    assert prereg["authority"]["sha256"] == GUIDANCE_SHA == _sha(Path(GUIDANCE)), "guidance sha mismatch"
    assert prereg_p.stat().st_mtime < time.time(), "prereg must predate the output"
    blocked_p = Path(BLOCKED)
    blocked_sha = _sha(blocked_p)
    assert blocked_sha.startswith(BLOCKED_SHA_PREFIX), "blocked file changed — refuse to adjudicate"
    corpus = Path(a.corpus_dir)
    songs = [adjudicate_song(s, corpus) for s in SCOPE]
    verdict = verdict_of(songs)
    assert verdict in ENUM
    resolved = verdict == "F4_RESOLVED"
    fails = [f"{s['title']}: " + ", ".join(k for k, ok in (("half/double", s["half_double"]["passes"]), ("onsets", s["onsets_per_beat"]["passes"]),
                                                            ("anchor", s["anchor"]["passes"])) if not ok) for s in songs if not s["all_three_pass"]]
    narrative = (f"c85 F4 operator adjudication (authority {GUIDANCE} sha {GUIDANCE_SHA[:16]}…, prereg {a.prereg} sha {_sha(prereg_p)[:16]}…) of the "
                 f"two tempo-blocked focus songs under the pre-registered half/double-time check applied to the READ-ONLY c83 tempo_v5d winner "
                 f"and c82 refined candidate set. " +
                 " ".join(f"{s['title']} ({s['sha16']}): adopted lag_ref {s['adopted_lag_ref']} = {s['adopted_bpm']:.6f} BPM (s_ref {s['adopted_s_ref']}); "
                          f"T/2 candidate lag {s['half_double']['half']['candidate'] and s['half_double']['half']['candidate']['lag_ref']} s_ref "
                          f"{s['half_double']['half']['candidate'] and s['half_double']['half']['candidate']['s_ref']} lower={s['half_double']['half']['scores_lower']}; "
                          f"2T candidate lag {s['half_double']['double']['candidate'] and s['half_double']['double']['candidate']['lag_ref']} s_ref "
                          f"{s['half_double']['double']['candidate'] and s['half_double']['double']['candidate']['s_ref']} lower={s['half_double']['double']['scores_lower']}; "
                          f"drum onsets/beat {s['onsets_per_beat']['onsets_per_beat']} pass={s['onsets_per_beat']['passes']}; anchor delta "
                          f"{s['anchor']['delta_bpm']} BPM pass={s['anchor']['passes']}." for s in songs) +
                 f" VERDICT {verdict}" + (": both songs pass all three sub-checks." if resolved else f" (failing: {'; '.join(fails)}). FD-1: nothing retuned. "
                 f"Both songs stay MUST-NOT-CONSUME for rules extraction; {BLOCKED} untouched (sha {blocked_sha[:16]}…); no recanonicalization written."))
    out = {"schema_version": 1, "cycle": 85, "agent": "worker", "run_id": "run-2026-09-06T000000Z", "milestone": prereg["milestone"],
           "kind": "operator_adjudication_not_a_tempo_criterion", "env_pin_sha256": ENV_PIN_SHA256,
           "authority": {"path": GUIDANCE, "sha256": GUIDANCE_SHA}, "prereg_path": a.prereg, "prereg_sha256": _sha(prereg_p),
           "adopted_mechanism": prereg["adopted_mechanism"], "check_verbatim": prereg["check_verbatim_from_c85_brief"],
           "thresholds": {"lag_tol_rel": LAG_TOL, "onsets_band": list(ONSETS_BAND), "anchor_tol_bpm": ANCHOR_TOL_BPM, "score_lower": "strict <"},
           "verdict": verdict, "verdict_enum": list(ENUM), "resolved": resolved,
           "per_song": {s["sha16"]: s for s in songs},
           "table": [{"sha16": s["sha16"], "title": s["title"], "adopted_lag_ref": s["adopted_lag_ref"], "adopted_bpm": s["adopted_bpm"], "adopted_s_ref": s["adopted_s_ref"],
                      "half_lag_ref": (s["half_double"]["half"]["candidate"] or {}).get("lag_ref"), "half_bpm_ref": (s["half_double"]["half"]["candidate"] or {}).get("bpm_ref"),
                      "half_s_ref": (s["half_double"]["half"]["candidate"] or {}).get("s_ref"), "half_scores_lower": s["half_double"]["half"]["scores_lower"],
                      "double_lag_ref": (s["half_double"]["double"]["candidate"] or {}).get("lag_ref"), "double_bpm_ref": (s["half_double"]["double"]["candidate"] or {}).get("bpm_ref"),
                      "double_s_ref": (s["half_double"]["double"]["candidate"] or {}).get("s_ref"), "double_scores_lower": s["half_double"]["double"]["scores_lower"],
                      "half_double_pass": s["half_double"]["passes"], "onsets_per_beat": s["onsets_per_beat"]["onsets_per_beat"], "onsets_pass": s["onsets_per_beat"]["passes"],
                      "anchor_delta_bpm": s["anchor"]["delta_bpm"], "anchor_pass": s["anchor"]["passes"], "all_three_pass": s["all_three_pass"]} for s in songs],
           "recanonicalization_blocked_path": BLOCKED, "recanonicalization_blocked_sha256": blocked_sha, "blocked_file_touched": False,
           "consequence": ("F4_RESOLVED: recanonicalize_tempo_v5.py may run (lead decides on the rules re-run)" if resolved else
                           "NOT RESOLVED: both songs stay MUST-NOT-CONSUME; blocked file byte-identical; nothing else written (FD-1)"),
           "known_property_not_a_rescue_clause": prereg["known_property_not_a_rescue_clause"], "fd1": prereg["fd1"],
           "ledger_narrative": narrative}
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_p = out_dir / a.out_name
    out_p.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    assert prereg_p.stat().st_mtime < out_p.stat().st_mtime, "PREREG_AFTER_OUTPUT"
    assert _sha(blocked_p) == blocked_sha
    print(f"VERDICT {verdict}")
    for r in out["table"]:
        print(f"  {r['title']:12s} T={r['adopted_lag_ref']} bpm={r['adopted_bpm']:.6f} s={r['adopted_s_ref']} | T/2 lag={r['half_lag_ref']} s={r['half_s_ref']} lower={r['half_scores_lower']} "
              f"| 2T lag={r['double_lag_ref']} s={r['double_s_ref']} lower={r['double_scores_lower']} | onsets/beat={r['onsets_per_beat']} ok={r['onsets_pass']} "
              f"| anchor d={r['anchor_delta_bpm']} ok={r['anchor_pass']}")
    print(f"  wrote {out_p} sha256 {_sha(out_p)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
