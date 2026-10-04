#!/usr/bin/python3
"""v6 Phase 2 — harmony: phrase chord sequences from the v5 Markov chain CONDITIONED on ending at the cadence's target states.

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

Chord slots: harmonic rhythm hr in {1, 2, 4} per bar -> slots at beats [0] / [0, 2] / [0, 1, 2, 3]. Per phrase of T slots:
  transition matrices per slot: P_t = the segment-level (change-only, zero-diagonal) matrix, except at the first slot of a
  bar whose hr == 1 where repeats across bars are allowed with the data's hold probability
  (P_t(s|s) = p_self(beat-level) ** 4, rest of the mass on the change row);
  backward messages: beta_{T-1}(s) = 1[s in FINAL], beta_{T-2}(s) = 1[s in PENULT] * sum_s' P_{T-1}(s'|s) beta_{T-1}(s'),
  beta_t(s) = sum_s' P_{t+1}(s'|s) beta_{t+1}(s') (with 'N' masked out of the last two slots);
  forward sampling: s_0 ~ pi0(s) beta_0(s), s_t ~ P_t(s|s_{t-1}) beta_t(s), each by SHA-256 inverse-CDF (draw_from).
Cadence targets (relative roots, key mode from the chain): authentic V -> I, half (any non-V) -> V, plagal IV -> I,
deceptive V -> vi (major) / VI (minor); every set is intersected with the chain's states and falls back to the root alone.
If the target is unreachable (all beta_0 zero) the phrase is sampled unconditioned and `conditioning_ok` is False.
The realized cadence (classified from the last two chords) is recorded next to the planned one for the validators.
"""
from __future__ import annotations

from scripts.v6.gen.common import draw_from, hold_prob, seg_matrix, state_root, state_quality

_SETS_MAJOR = {"I": (0, ("maj", "maj7", "sus", "9")), "V": (7, ("maj", "7", "9", "sus")), "IV": (5, ("maj", "maj7", "sus")), "vi": (9, ("min", "min7"))}
_SETS_MINOR = {"I": (0, ("min", "min7")), "V": (7, ("maj", "7", "9", "min", "min7")), "IV": (5, ("min", "min7", "maj")), "vi": (8, ("maj", "maj7"))}


def function_set(states: list, fn: str, mode: str) -> set:
    root, quals = (_SETS_MINOR if str(mode).lower() == "minor" else _SETS_MAJOR)[fn]
    s = {st for st in states if state_root(st) == root and state_quality(st) in quals}
    if not s:
        s = {st for st in states if state_root(st) == root}
    return s


def cadence_targets(cadence: str, states: list, mode: str) -> tuple[set, set]:
    """(penultimate set, final set) for a cadence type over the chain's states."""
    I, V, IV, vi = (function_set(states, f, mode) for f in ("I", "V", "IV", "vi"))
    if cadence == "authentic":
        return V, I
    if cadence == "half":
        return {s for s in states if s not in V and s != "N"}, V
    if cadence == "plagal":
        return IV, I
    if cadence == "deceptive":
        return V, vi
    raise ValueError(cadence)


def classify_cadence(penult: str | None, final: str, states: list, mode: str) -> str:
    I, V, IV, vi = (function_set(states, f, mode) for f in ("I", "V", "IV", "vi"))
    if penult in V and final in I:
        return "authentic"
    if penult in IV and final in I:
        return "plagal"
    if penult in V and final in vi:
        return "deceptive"
    if final in V and penult not in V:
        return "half"
    return "none"


def phrase_slots(hr: list, start_bar: int) -> list:
    """[(bar, beat, repeat_allowed)] for the bars of a phrase (hr = chords per bar for each bar)."""
    out = []
    for i, h in enumerate(hr):
        beats = {1: (0,), 2: (0, 2), 4: (0, 1, 2, 3)}[int(h)]
        for b in beats:
            out.append((start_bar + i, b, bool(h == 1)))
    return out


def slot_matrix(chain: dict, P_seg: dict, repeat_allowed: bool) -> dict:
    if not repeat_allowed:
        return P_seg
    P = {}
    for s, row in P_seg.items():
        h = hold_prob(chain, s)
        P[s] = {t: (1.0 - h) * p for t, p in row.items()}
        P[s][s] = h
    return P


def backward_messages(mats: list, states: list, penult: set, final: set) -> list:
    """beta[t][s] for t = 0..T-1 given per-slot matrices mats[t] (mats[0] unused). 'N' masked out of the last two slots."""
    T = len(mats)
    beta = [dict() for _ in range(T)]
    for s in states:
        beta[T - 1][s] = 1.0 if (s in final and s != "N") else 0.0
    for t in range(T - 2, -1, -1):
        for s in states:
            v = sum(mats[t + 1][s].get(sp, 0.0) * beta[t + 1][sp] for sp in states)
            if t == T - 2 and (s not in penult or s == "N"):
                v = 0.0
            beta[t][s] = v
    return beta


def sample_phrase_chords(chain: dict, slots: list, cadence: str, mode: str, tag: str, prev_state: str | None = None) -> dict:
    """slots = [(bar, beat, repeat_allowed)]; returns the chord per slot, the backward messages' reachability and the realized cadence."""
    states = chain["states"]
    P_seg = seg_matrix(chain)
    mats = [slot_matrix(chain, P_seg, rep) for (_b, _bt, rep) in slots]
    penult, final = cadence_targets(cadence, states, mode)
    beta = backward_messages(mats, states, penult, final)
    pi0 = mats[0][prev_state] if prev_state is not None and prev_state in mats[0] else chain["stationary_distribution"]
    w0 = {s: float(pi0.get(s, 0.0)) * beta[0][s] for s in states}
    ok = sum(w0.values()) > 0.0
    if not ok:  # unreachable target: unconditioned fallback (recorded)
        beta = [{s: 1.0 for s in states} for _ in slots]
        w0 = {s: float(pi0.get(s, 0.0)) for s in states}
    seq = [draw_from(w0, f"{tag}|chord0")]
    for t in range(1, len(slots)):
        row = mats[t][seq[-1]]
        w = {s: row.get(s, 0.0) * beta[t][s] for s in states}
        if sum(w.values()) <= 0.0:
            w = {s: row.get(s, 0.0) for s in states}
        seq.append(draw_from(w, f"{tag}|chord{t}|from={seq[-1]}"))
    realized = classify_cadence(seq[-2] if len(seq) > 1 else prev_state, seq[-1], states, mode)
    return {"chords": seq, "slots": [{"bar": b, "beat": bt, "state": s, "repeat_allowed": rep} for (b, bt, rep), s in zip(slots, seq)],
            "cadence_planned": cadence, "cadence_realized": realized, "cadence_ok": realized == cadence, "conditioning_ok": ok,
            "targets": {"penultimate": sorted(penult), "final": sorted(final)}, "beta0_mass": round(sum(w0.values()), 9)}


def beat_chords(slot_records: list, n_bars: int, start_bar: int = 0) -> list:
    """Per-bar per-beat chord states from chord slots (held until the next slot)."""
    out = [[None] * 4 for _ in range(n_bars)]
    cur = None
    by_pos = {(r["bar"] - start_bar, r["beat"]): r["state"] for r in slot_records}
    for b in range(n_bars):
        for bt in range(4):
            cur = by_pos.get((b, bt), cur)
            out[b][bt] = cur if cur is not None else "N"
    return out


def label_harmony(chain: dict, label_plan: dict, mode: str, tag: str) -> dict:
    """All phrases of one section label, chained (each phrase conditions its first chord on the previous phrase's last)."""
    hr = label_plan["harmonic_rhythm"]
    phrases, prev, all_slots = [], None, []
    for ph in label_plan["phrases"]:
        sl = phrase_slots(hr[ph["start_bar"]: ph["start_bar"] + ph["n_bars"]], ph["start_bar"])
        r = sample_phrase_chords(chain, sl, ph["cadence"], mode, f"{tag}|harmony|{ph['index']}", prev)
        r["phrase_index"] = ph["index"]
        phrases.append(r)
        all_slots += r["slots"]
        prev = r["chords"][-1]
    n_bars = len(hr)
    return {"phrases": phrases, "slots": all_slots, "beat_chords": beat_chords(all_slots, n_bars), "harmonic_rhythm": list(hr), "n_bars": n_bars}
