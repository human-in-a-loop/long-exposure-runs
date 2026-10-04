#!/usr/bin/python3
"""v6 Phase 2 — bassline: groove-model rhythm, interval-class pitches weighted by the bass model x counterpoint vs melody/keys.

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

Per bar: onsets = the groove model's bass16 slots (as v5) with an onset FORCED at every chord slot (every change, plus the
bar-start slot of a repeated chord; roots must sound on every change: the forced onset's class is 'root' and its pitch is
root_line's, the deterministic root line the voicing DP and the melody skeleton were given). Per onset: candidate classes {root, fifth, octave, third, approach,
repeat} ('other' of the v5 model = repeat the previous pitch) with base weights = the bass_pitch_v5 conditional row
"<slot%4>|<chord_change>" (approach only on the last onset before a change: +/-1 or +/-2 semitones into the NEXT root),
each class realised as a pitch in REGISTER 28..50 nearest the previous bass note, then multiplied by counterpoint factors
vs the melody note sounding at that time: contrary motion x1.5, parallel perfect 5th/8ve with the melody (or with any keys
voice at a chord change) x0.3, same pitch class as the melody on a strong beat (slots 0 / 8) x0.7, |delta| <= 7 from the
previous note x1.3. The class is drawn by SHA-256 inverse-CDF over the final weights (draw_from).
"""
from __future__ import annotations

from scripts.v6.gen.common import SLOTS, draw_from, nearest_pitch, state_pcs, u

REGISTER = (28, 50)
FACTORS = {"contrary": 1.5, "parallel_perfect": 0.3, "same_pc_strong": 0.7, "near_prev": 1.3}
CLASSES = ("root", "fifth", "octave", "third", "approach", "repeat")


def bits(x: int, n: int = SLOTS) -> list:
    return [i for i in range(n) if int(x) >> i & 1]


def class_pitch(cls: str, root_pc: int, pcs: list, next_root_pc, prev, tag: str) -> int | None:
    lo, hi = REGISTER
    anchor = prev if prev is not None else 38
    if cls == "root":
        return nearest_pitch(root_pc, anchor, lo, hi)
    if cls == "fifth":
        return nearest_pitch((root_pc + 7) % 12, anchor, lo, hi)
    if cls == "octave":
        r = nearest_pitch(root_pc, anchor, lo, hi)
        return r + 12 if r is not None and r + 12 <= hi else (r - 12 if r is not None and r - 12 >= lo else None)
    if cls == "third":
        third = pcs[1] if len(pcs) > 1 else (root_pc + 4) % 12
        return nearest_pitch(third, anchor, lo, hi)
    if cls == "approach":
        if next_root_pc is None:
            return None
        tgt = nearest_pitch(next_root_pc, anchor, lo, hi)
        if tgt is None:
            return None
        opts = [tgt + d for d in (-1, -2, 1, 2) if lo <= tgt + d <= hi]
        return opts[int(u(f"{tag}|approach") * len(opts))] if opts else None
    if cls == "repeat":
        return prev
    return None


def root_line(states: list, tonic: int, anchor: int = 38) -> list:
    """Deterministic bass root per chord slot (nearest root placement to the previous root in REGISTER; None for 'N').
    Shared by the voicing DP and the melody skeleton so both can avoid parallel perfects against the bass that WILL sound
    on every chord change (bassline forces the same pitches there)."""
    out, prev = [], anchor
    for st in states:
        pcs = state_pcs(st, tonic)
        if not pcs:
            out.append(None)
            continue
        p = nearest_pitch(pcs[0], prev, *REGISTER)
        out.append(p)
        prev = p
    return out


def is_parallel_perfect(prev_low, prev_high, low, high) -> bool:
    if None in (prev_low, prev_high, low, high):
        return False
    ia, ib = (prev_high - prev_low) % 12, (high - low) % 12
    return ia == ib and ia in (0, 7) and (low - prev_low) != 0 and (high - prev_high) != 0 and (low - prev_low) * (high - prev_high) > 0


def sounding(notes: list, slot: int):
    """Pitch of the (melody) note sounding at `slot` from a slot-sorted list of {slot, pitch, dur16}, or None."""
    best = None
    for n in notes:
        if n["slot"] <= slot < n["slot"] + n["dur16"]:
            best = n["pitch"]
        elif n["slot"] > slot:
            break
    return best


def label_bass(bass_model: dict, groove_bars: list, beat_chords: list, melody_notes: list, voicings_by_slot: dict, tonic: int, tag: str, velocity_fn,
               forced_roots: dict | None = None) -> dict:
    """Bass notes over a label's bars: [{slot, pitch, dur16, cls, bar, factors}]. forced_roots {(bar, beat): pitch} from root_line."""
    forced_roots = forced_roots or {}
    n_bars = len(beat_chords)
    mel = sorted(melody_notes, key=lambda n: n["slot"])
    notes, prev, prev_mel, prev_keys = [], None, None, None
    forced_total, changes_total = 0, 0
    for b in range(n_bars):
        chords = beat_chords[b]
        change_slots = [bt * 4 for bt in range(4) if (bt == 0 and (b == 0 or chords[0] != beat_chords[b - 1][3])) or (bt > 0 and chords[bt] != chords[bt - 1])]
        changes_total += len(change_slots)
        # every chord SLOT (changes AND a repeated chord's bar-start slot) gets a root onset, so the bass sounding at any chord
        # slot is exactly bassline.root_line's pitch (what the voicing DP and the melody skeleton assumed)
        change_slots = sorted(set(change_slots) | {bt * 4 for bt in range(4) if (b, bt) in forced_roots})
        onsets = sorted(set(bits(groove_bars[b]["bass"])) | set(change_slots))
        forced_total += len(set(change_slots) - set(bits(groove_bars[b]["bass"])))
        for k, p in enumerate(onsets):
            st = chords[p // 4]
            pcs = state_pcs(st, tonic)
            root_pc = pcs[0] if pcs else tonic
            nxt_slot = onsets[k + 1] if k + 1 < len(onsets) else SLOTS
            # next chord root if a change happens at the next onset (within the bar) or at the next bar's downbeat
            nxt_state = chords[nxt_slot // 4] if nxt_slot < SLOTS else (beat_chords[b + 1][0] if b + 1 < n_bars else None)
            nxt_pcs = state_pcs(nxt_state, tonic) if nxt_state else None
            next_root = nxt_pcs[0] if nxt_pcs and nxt_pcs[0] != root_pc else None
            chg = next_root is not None
            abs_slot = b * SLOTS + p
            mel_pitch = sounding(mel, abs_slot)
            keys_v = None
            for bb in range(p // 4, -1, -1):
                if (b, bb) in voicings_by_slot:
                    keys_v = voicings_by_slot[(b, bb)]
                    break
            nxt_forced = forced_roots.get((b, nxt_slot // 4)) if nxt_slot < SLOTS else (forced_roots.get((b + 1, 0)) if b + 1 < n_bars else None)
            mel_next = sounding(mel, b * SLOTS + nxt_slot) if nxt_forced is not None else None
            if p in change_slots and (pcs is not None):
                pitch = forced_roots.get((b, p // 4)) or class_pitch("root", root_pc, pcs or [root_pc], next_root, prev, f"{tag}|bass|{b}|{p}")
                cls, factors = "root", {"forced_root_on_change": 1.0}
            else:
                row = bass_model.get("conditional", {}).get(f"{p % 4}|{int(chg)}") or bass_model["marginal"]
                base = dict(row["probs"])
                base["repeat"] = base.pop("other", 0.0)
                w, factors = {}, {}
                for cls_ in CLASSES:
                    if cls_ == "approach" and not chg:
                        continue
                    cand = class_pitch(cls_, root_pc, pcs or [root_pc], next_root, prev, f"{tag}|bass|{b}|{p}")
                    if cand is None:
                        continue
                    f = 1.0
                    if prev is not None and mel_pitch is not None and prev_mel is not None and (cand - prev) * (mel_pitch - prev_mel) < 0:
                        f *= FACTORS["contrary"]
                    if is_parallel_perfect(prev, prev_mel, cand, mel_pitch):
                        f *= FACTORS["parallel_perfect"]
                    if nxt_forced is not None and is_parallel_perfect(cand, mel_pitch, nxt_forced, mel_next):  # look-ahead into the forced root
                        f *= FACTORS["parallel_perfect"]
                    if keys_v and prev_keys and keys_v != prev_keys and any(is_parallel_perfect(prev, pk, cand, kk) for pk, kk in zip(prev_keys, keys_v)):
                        f *= FACTORS["parallel_perfect"]
                    if mel_pitch is not None and p % 8 == 0 and cand % 12 == mel_pitch % 12:
                        f *= FACTORS["same_pc_strong"]
                    if prev is not None and abs(cand - prev) <= 7:
                        f *= FACTORS["near_prev"]
                    w[cls_] = float(base.get(cls_, 0.0)) * f
                    factors[cls_] = round(f, 4)
                cls = draw_from(w, f"{tag}|bass|cls|{b}|{p}") if w else "root"
                pitch = class_pitch(cls, root_pc, pcs or [root_pc], next_root, prev, f"{tag}|bass|{b}|{p}")
            notes.append({"slot": abs_slot, "pitch": int(pitch), "dur16": int(nxt_slot - p), "cls": cls, "bar": b, "chord": st,
                          "on_change": p in change_slots, "factors": factors,
                          "velocity": velocity_fn(f"{tag}|bass|vel|{b}|{p}", p, p in {2 * j for j in bits(groove_bars[b]["kick"], 8)})})
            prev, prev_mel, prev_keys = int(pitch), mel_pitch if mel_pitch is not None else prev_mel, keys_v
    return {"notes": notes, "n_changes": changes_total, "n_forced_onsets": forced_total}
