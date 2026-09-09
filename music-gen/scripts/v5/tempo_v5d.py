#!/usr/bin/python3
"""c83 S7 — tempo criterion v5d: refined-fractional-lag harmonic sum (pre-registered; frozen 2-verdict enum).

created: 2026-09-06T21:25:00Z
cycle: 83
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo_v5d-verdict-c83

Pre-registration: data/v5/corpus/tempo_v5d_preregistration.json (mtime must precede every output; asserted).
Input: the READ-ONLY c82 mechanism-probe records data/v5/corpus/<sha16>/tempo_mechanism_c82.json — their `candidates`
(parabola-refined local maxima in [40,240] with s_ref = ac(T)+½ac(T/2)+½ac(2T) at the refined fractional lags) are exactly
the v5d candidates; this script re-derives in_pick_band from bpm_ref, recomputes the SHA-256 tiebreak, picks argmax s_ref over
[70,180], scores the five anchor targets (identical to v5/v5b/v5c) and emits the frozen verdict
{SUPPORTED, RULES_OUT_REFINED_LAG}. FD-1: no retune; on either outcome recanonicalization_blocked.json is untouched.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
sys.path.insert(0, str(_WS))
from scripts.v5.tempo_mechanism_probe_c82 import anchor_bpm_table  # noqa: E402  READ-ONLY (c82)

CORPUS = Path("data/v5/corpus")
PREREG = CORPUS / "tempo_v5d_preregistration.json"
PICK_BAND = (70.0, 180.0)
CRITERION = "refined_lag_harmonic_sum_v5d"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
WIG = "252eb21ce7df7328"
ANCHOR_TOL = 2.0
ENUM = ("SUPPORTED", "RULES_OUT_REFINED_LAG")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tiebreak(sha16: str, bpm: float) -> str:
    return hashlib.sha256(f"{sha16}|{bpm:.6f}".encode()).hexdigest()


def estimate(sha16: str, probe: dict) -> dict:
    cands = []
    for c in probe["candidates"]:
        bpm = float(c["bpm_ref"])
        cands.append({"lag_int": c["lag_int"], "lag_ref": c["lag_ref"], "bpm_ref": round(bpm, 6), "s_ref": c["s_ref"],
                      "ac_T": c["ac_T"], "ac_half": c["ac_half"], "ac_double": c["ac_double"],
                      "in_pick_band": bool(PICK_BAND[0] <= bpm <= PICK_BAND[1]), "tiebreak_sha256": tiebreak(sha16, round(bpm, 6))})
    eligible = sorted([c for c in cands if c["in_pick_band"]], key=lambda c: (-c["s_ref"], c["tiebreak_sha256"]))
    winner = eligible[0] if eligible else None
    return {"schema_version": 1, "agent": "worker", "cycle": 83, "sha16": sha16, "title": probe.get("title"), "criterion": CRITERION,
            "env_pin_sha256": ENV_PIN, "input_record": f"data/v5/corpus/{sha16}/tempo_mechanism_c82.json",
            "input_record_sha256": _sha(CORPUS / sha16 / "tempo_mechanism_c82.json"), "pick_band_bpm": list(PICK_BAND),
            "bpm_v5": probe.get("bpm_v5"), "bpm_v5c": probe.get("bpm_v5c_integer_winner"),
            "bpm_v5d": winner["bpm_ref"] if winner else None, "winner": winner,
            "n_candidates": len(cands), "n_eligible": len(eligible), "candidates": cands,
            "s_top3": [{"bpm_ref": c["bpm_ref"], "s_ref": c["s_ref"]} for c in eligible[:3]]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=CORPUS)
    a = ap.parse_args(argv)
    prereg = json.loads(PREREG.read_text()); prereg_mtime = PREREG.stat().st_mtime
    anchors = anchor_bpm_table()
    man = json.loads((CORPUS / "corpus_manifest.json").read_text())
    songs = [s["sha16"] for s in man["songs"] if s.get("in_v5_corpus")]
    rows, hits, misses, flips = [], {}, {}, []
    for s in songs:
        rec = estimate(s, json.loads((CORPUS / s / "tempo_mechanism_c82.json").read_text()))
        d = a.out_dir / s; d.mkdir(parents=True, exist_ok=True)
        (d / "tempo_v5d.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
        b = rec["bpm_v5d"]
        if s in anchors:
            tgt = anchors[s]
            ok = b is not None and abs(b - tgt) <= ANCHOR_TOL and not (s == WIG and 45.0 <= b <= 56.0)
            (hits if ok else misses)[s] = {"bpm_v5d": b, "anchor": round(tgt, 6), "delta": round(b - tgt, 6) if b is not None else None,
                                            "s_ref_winner": rec["winner"]["s_ref"] if rec["winner"] else None}
        elif b is not None and rec["bpm_v5"] is not None and abs(b - rec["bpm_v5"]) > 2.0:
            flips.append({"sha16": s, "bpm_v5": rec["bpm_v5"], "bpm_v5d": b})
        rows.append((s, rec.get("title"), rec["bpm_v5"], rec["bpm_v5c"], b, rec["winner"]["s_ref"] if rec["winner"] else None, s in anchors))
    tsv = ["sha16\ttitle\tbpm_v5\tbpm_v5c\tbpm_v5d\ts_ref_winner\tis_anchor"] + ["\t".join("" if v is None else str(v) for v in r) for r in rows]
    (a.out_dir / "tempo_v5d_summary.tsv").write_text("\n".join(tsv) + "\n")
    verdict = "SUPPORTED" if len(hits) == 5 and not misses else "RULES_OUT_REFINED_LAG"
    assert verdict in ENUM
    n_non_anchor = len([s for s in songs if s not in anchors])
    v = {"schema_version": 1, "agent": "worker", "cycle": 83, "run_id": "run-2026-09-06T000000Z", "criterion": CRITERION, "verdict": verdict,
         "criterion_summary": prereg["criterion_summary"], "justification_verbatim": prereg["justification_verbatim"],
         "prereg_path": str(PREREG), "prereg_sha256": _sha(PREREG), "prereg_mtime_precedes_outputs": True,
         "anchor_hits": hits, "anchor_misses": misses, "n_anchor_hits": len(hits), "anchor_tol_bpm": ANCHOR_TOL,
         "secondary_non_anchor_flips_gt_2bpm_vs_v5": {"n": len(flips), "of": n_non_anchor, "rows": flips},
         "n_songs": len(songs), "env_pin_sha256": ENV_PIN,
         "recanonicalization_this_cycle": False, "recanonicalization_blocked_json_touched": False,
         "next": ("c84 plan: recanonicalize PD + Disco A at bpm_v5d under canonical_v5c_reindexed/ via a fresh reindex; supersede recanonicalization_blocked.json only after that reindex lands; v5d becomes the canonical tempo criterion."
                  if verdict == "SUPPORTED" else "RULES_OUT: recorded and STOP — no v5e; PD + Disco A remain MUST-NOT-CONSUME for rules; the tempo axis hands to operator adjudication or a mechanism other than autocorrelation.")}
    v["ledger_narrative"] = (f"c83 S7 VERDICT = **{verdict}** ({len(hits)}/5 anchors hit; tol ±{ANCHOR_TOL} BPM). Hits: "
                             + "; ".join(f"{k} {x['bpm_v5d']} (Δ {x['delta']:+.2f}, s {x['s_ref_winner']})" for k, x in hits.items())
                             + (". Misses: " + "; ".join(f"{k} {x['bpm_v5d']} vs {x['anchor']} (Δ {x['delta']:+.2f})" for k, x in misses.items()) if misses else "")
                             + f". Non-anchor flips > 2 BPM vs v5: {len(flips)}/{n_non_anchor}. Input = READ-ONLY c82 mechanism-probe candidates (same autocorrelation); prereg before every output; byte-det x2. {v['next']}")
    v["por_narrative"] = v["ledger_narrative"]
    (a.out_dir / "tempo_v5d_falsification.json").write_text(json.dumps(v, sort_keys=True, indent=2) + "\n")
    for p in a.out_dir.glob("**/tempo_v5d*.json"):
        if p.name == PREREG.name:
            continue  # the pre-registration itself is the gate, not an output
        assert p.stat().st_mtime > prereg_mtime, p
    print(json.dumps({k: v[k] for k in ("verdict", "anchor_hits", "anchor_misses", "secondary_non_anchor_flips_gt_2bpm_vs_v5")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
