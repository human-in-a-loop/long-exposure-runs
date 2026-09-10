#!/usr/bin/python3
"""c89 F5 — model-parameter interpolation between two donors (CG <-> PD, t = 0.5) for the v5 generator.
Imported ONLY under `generate_v5.py --f5`; never on the flag-off path. Pre-registered in data/v5/gen/f5_prereg_c89.json
(written before this file existed; the prereg governs).

created: 2026-09-10T03:20:00Z
cycle: 89
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F5-interpolation-demo

Semantics (verbatim from the prereg `blend_semantics`):
  * donor-conditioned distribution = the n=23 model construction applied to the donor's OWN lossless canonical MIDI
    (READ-ONLY imports: scripts.v5.groove_v5_v2.load_song/table, scripts.v5.harmony_v5.analyse_song). CG is served from
    canonical_v5_reindexed/ at bpm_v5; PD from canonical_v5c_reindexed/ at the adopted 122.197271 (asserted by the loaders).
  * groove: P_mix(o|c) = t*P_A(o|c) + (1-t)*P_B(o|c) over the UNION outcome vocabulary of each of the four tables
    (kick8 marginal, snare16|kick8, hat16|kick8+snare16, bass16|kick8); P_X(o|c) = the donor's alpha-smoothed row when
    c is seen in X, else uniform over the donor vocab (row_for convention); outcomes absent from a donor vocab get 0 from it;
    contexts seen in neither donor keep the generator's uniform-over-vocab convention (they are simply absent from `probs`).
  * harmony: over the n=23 chain's 81 functional states (donor states asserted subset): row_mix(s) = t*P_A(s,.) + (1-t)*P_B(s,.)
    with P_X(s,.) = donor X row-normalised segment transitions when n_X(s) > 0 else the n=23 segment row (backoff, counted);
    stored as segment_level_counts[s] = n_mix(s)*row_mix(s), n_mix(s) = t*n_A(s) + (1-t)*n_B(s) so generate_v5.seg_matrix
    recovers row_mix and the F1 contrast rule reads the blended support; pi_mix = t*pi_A + (1-t)*pi_B (donor segment-state
    frequencies); tonic/mode = donor A.
  * NO note-level mean; ONE sequence is sampled from the blended model by the generator's SHA-256 inverse-CDF draws.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; READ-ONLY inputs; no writes here.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v5 import groove_v5_v2 as G  # noqa: E402  READ-ONLY (load_song, table, row_for, ALPHA)
from scripts.v5.harmony_v5 import analyse_song  # noqa: E402  READ-ONLY

NAMES = {"CG": "31a164f845f8e27e", "WIG": "252eb21ce7df7328", "Rome": "51e433ade2a845e1", "PD": "88d247468cb6d49f", "DiscoA": "cdd2717e52820ff6"}
TABLES = ("kick_marginal", "snare_given_kick", "hat_given_kick_snare", "bass_given_kick")


def _sha_obj(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def resolve_donor(x: str) -> str:
    if x in NAMES:
        return NAMES[x]
    if len(x) == 16 and all(c in "0123456789abcdef" for c in x):
        return x
    raise ValueError(f"unknown donor {x!r}: use one of {sorted(NAMES)} or a sha16")


def donor_groove_tables(corpus: Path, sha16: str, tempo_overrides: dict | None) -> dict:
    """Per-donor conditional tables built by the n=23 construction on the donor's own bars (groove_v5_v2.load_song + table)."""
    r = G.load_song(Path(corpus), sha16, tempo_overrides or {})
    bars = r["bars"]
    tables = {"kick_marginal": G.table([("*", b["kick"]) for b in bars]),
              "snare_given_kick": G.table([(str(b["kick"]), b["snare"]) for b in bars]),
              "hat_given_kick_snare": G.table([(f"{b['kick']}|{b['snare']}", b["hat"]) for b in bars]),
              "bass_given_kick": G.table([(str(b["kick"]), b["bass"]) for b in bars])}
    return {"sha16": sha16, "title": r.get("title"), "bpm_v5": r["bpm_v5"], "phase_offset": r["phase"]["offset"], "n_bars": len(bars),
            "stats": r["stats"], "midi_dir": r.get("midi_dir", str(Path(corpus) / sha16 / "canonical_v5_reindexed")),
            "tempo_override_c86": r.get("tempo_override_c86"), "tables": tables}


def blend_groove_tables(TA: dict, TB: dict, t: float) -> dict:
    """t-weighted mixture of two donor table sets over the union vocabulary; returns a `model` dict consumable by generate_v5."""
    out = {}
    for name in TABLES:
        a, b = TA[name], TB[name]
        vocab = sorted(set(a["vocab"]) | set(b["vocab"]), key=int)
        ctxs = sorted(set(a["probs"]) | set(b["probs"]))
        probs, n_both, n_a_only, n_b_only = {}, 0, 0, 0
        for c in ctxs:
            ra, rb = G.row_for(a, c), G.row_for(b, c)  # unseen context -> uniform over that donor's vocab
            in_a, in_b = c in a["probs"], c in b["probs"]
            n_both += in_a and in_b
            n_a_only += in_a and not in_b
            n_b_only += in_b and not in_a
            probs[c] = {o: t * ra.get(o, 0.0) + (1.0 - t) * rb.get(o, 0.0) for o in vocab}
        out[name] = {"probs": probs, "vocab": vocab, "alpha": G.ALPHA, "n_contexts": len(ctxs),
                     "blend": {"t": t, "contexts_seen_in_both": n_both, "contexts_A_only": n_a_only, "contexts_B_only": n_b_only,
                               "vocab_A": len(a["vocab"]), "vocab_B": len(b["vocab"]), "vocab_union": len(vocab)}}
    return out


def donor_harmony(corpus: Path, sha16: str, tempo_overrides: dict | None) -> dict:
    r = analyse_song(sha16, Path(corpus), tempo_overrides or {})
    segs = [g["state"] for g in r["segments"]]
    return {"sha16": sha16, "title": r.get("title"), "bpm_v5": r["bpm_v5"], "key": r["key"], "n_beats": r["n_beats"], "n_segments": len(segs),
            "n_excluded_beats": r["exclusion_rule"]["n_excluded_beats"], "midi_dir": r["midi_dir"], "tempo_override_c86": r.get("tempo_override_c86"),
            "segments": segs, "distinct_states": sorted(set(segs))}


def _seg_rows(states: list, segs: list) -> tuple[dict, dict, dict]:
    idx = {s: i for i, s in enumerate(states)}
    n = {s: 0 for s in states}
    C = {s: [0.0] * len(states) for s in states}
    for a, b in zip(segs, segs[1:]):
        C[a][idx[b]] += 1.0
        n[a] += 1
    freq = {s: 0 for s in states}
    for s in segs:
        freq[s] += 1
    tot = float(len(segs)) or 1.0
    pi = {s: freq[s] / tot for s in states}
    P = {s: ([v / n[s] for v in C[s]] if n[s] else None) for s in states}
    return n, P, pi


def blend_harmony_chain(chain: dict, HA: dict, HB: dict, t: float, donor_a: str) -> dict:
    """Blended segment-level chain over the n=23 state set; shape consumable by generate_v5 (states, segment_level_counts,
    stationary_distribution, per_song[donor_a].key, degeneracy_verdict)."""
    states = list(chain["states"])
    for H in (HA, HB):
        missing = sorted(set(H["distinct_states"]) - set(states))
        if missing:
            raise ValueError(f"donor {H['sha16']} has states outside the n=23 chain: {missing}")
    nA, PA, piA = _seg_rows(states, HA["segments"])
    nB, PB, piB = _seg_rows(states, HB["segments"])
    corpus_rows = {}
    for i, s in enumerate(states):
        row = chain["segment_level_counts"][i]
        tot = float(sum(row))
        corpus_rows[s] = [v / tot for v in row] if tot else [1.0 / len(states)] * len(states)
    counts, backoff = [], {"A": [], "B": [], "both_unseen": []}
    for s in states:
        ra = PA[s] if PA[s] is not None else corpus_rows[s]
        rb = PB[s] if PB[s] is not None else corpus_rows[s]
        if PA[s] is None and nB[s] > 0:
            backoff["A"].append(s)
        if PB[s] is None and nA[s] > 0:
            backoff["B"].append(s)
        if PA[s] is None and PB[s] is None:
            backoff["both_unseen"].append(s)
        n_mix = t * nA[s] + (1.0 - t) * nB[s]
        counts.append([round(n_mix * (t * x + (1.0 - t) * y), 9) for x, y in zip(ra, rb)])
    pi = {s: round(t * piA[s] + (1.0 - t) * piB[s], 9) for s in states}
    return {"states": states, "segment_level_counts": counts, "stationary_distribution": pi,
            "per_song": {donor_a: {"key": HA["key"], "title": HA["title"]}},
            "degeneracy_verdict": "NON_DEGENERATE", "degeneracy_note": "F5 blend of two donor-conditioned rows of the NON_DEGENERATE n=23 chain (330b9d46…); not re-verdicted",
            "chain_definition": "F5 t-weighted mixture of donor segment-level rows (n=23 segment row as backoff for a state unseen in one donor); counts = n_mix(s) * row_mix(s)",
            "blend": {"t": t, "donor_A": HA["sha16"], "donor_B": HB["sha16"], "n_states": len(states),
                      "states_with_support_A": sum(1 for s in states if nA[s]), "states_with_support_B": sum(1 for s in states if nB[s]),
                      "states_with_blended_support": sum(1 for s in states if t * nA[s] + (1.0 - t) * nB[s] > 0),
                      "backoff_to_n23_row_for_A": backoff["A"], "backoff_to_n23_row_for_B": backoff["B"], "n_both_unseen_uniform": len(backoff["both_unseen"]),
                      "segments_A": HA["n_segments"], "segments_B": HB["n_segments"], "tonic_mode_source": f"donor A {donor_a} KK key"}}


def build_blend(corpus: Path, chain_n23: dict, groove_n23: dict, donor_a: str, donor_b: str, t: float, tempo_overrides: dict | None) -> dict:
    """Returns {"groove": <groove dict>, "chain": <chain dict>, "record": <JSON-able provenance>} for one blend weight t."""
    TA, TB = donor_groove_tables(corpus, donor_a, tempo_overrides), donor_groove_tables(corpus, donor_b, tempo_overrides)
    HA, HB = donor_harmony(corpus, donor_a, tempo_overrides), donor_harmony(corpus, donor_b, tempo_overrides)
    return build_blend_from(TA, TB, HA, HB, chain_n23, groove_n23, donor_a, donor_b, t)


def build_blend_from(TA: dict, TB: dict, HA: dict, HB: dict, chain_n23: dict, groove_n23: dict, donor_a: str, donor_b: str, t: float) -> dict:
    model = blend_groove_tables(TA["tables"], TB["tables"], t)
    chain = blend_harmony_chain(chain_n23, HA, HB, t, donor_a)
    groove = {"model": model, "verdict": f"F5_BLEND(t={t})", "blend": {"t": t, "donor_A": donor_a, "donor_B": donor_b,
              "per_table": {k: v["blend"] for k, v in model.items()}, "n23_tables_consulted": False, "n23_verdict_disclosed": groove_n23.get("verdict")}}
    record = {"t": t, "donor_A": {k: v for k, v in TA.items() if k != "tables"} | {"harmony": {k: v for k, v in HA.items() if k != "segments"}},
              "donor_B": {k: v for k, v in TB.items() if k != "tables"} | {"harmony": {k: v for k, v in HB.items() if k != "segments"}},
              "groove_blend": groove["blend"], "harmony_blend": chain["blend"],
              "blended_model_sha256": {"groove_model": _sha_obj(model), "harmony_chain": _sha_obj({k: chain[k] for k in ("states", "segment_level_counts", "stationary_distribution")})},
              "semantics": "prereg data/v5/gen/f5_prereg_c89.json blend_semantics (model-parameter mixture; no note-level mean; SHA-256 inverse-CDF sampling)"}
    return {"groove": groove, "chain": chain, "record": record}


def hamming_fraction(a: list, b: list) -> float | None:
    if not a or len(a) != len(b):
        return None
    return round(sum(1 for x, y in zip(a, b) if x != y) / len(a), 6)


if __name__ == "__main__":  # self-check on a synthetic pair (no corpus reads)
    ta = {n: G.table([("*", 1), ("*", 3)]) if n == "kick_marginal" else G.table([("1", 4), ("3", 8)]) for n in TABLES}
    tb = {n: G.table([("*", 2)]) if n == "kick_marginal" else G.table([("2", 16)]) for n in TABLES}
    m = blend_groove_tables(ta, tb, 0.5)
    assert abs(sum(m["kick_marginal"]["probs"]["*"].values()) - 1.0) < 1e-9
    print(json.dumps({k: v["blend"] for k, v in m.items()}))
