#!/usr/bin/python3
"""v6 Phase 2 — planner: FormPlan -> PhrasePlan (cadence types) -> harmonic rhythm -> arrangement.

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

FormPlan: data/v5/rules/form_plan_v5.json when present (same draws as generate_v5.plan_form: n_sections from the length
distribution, labels from the corpus label chain if R1 passed else the fixed template, 8 bars per section), otherwise the
fixed A A B A at 8 bars/section (or --bars/8 sections of the template A A B A B C A A). Every label is planned ONCE and
repeated literally wherever it recurs (v5 convention; validators.section_repeat_integrity checks it).
PhrasePlan per label: 2 phrases of 4 bars (1 of 8 for ballads, bpm < BALLAD_BPM); each phrase draws a CADENCE from
P(cadence | position) — section-final phrases biased to authentic, section-internal to half.
Harmonic rhythm per bar in {1, 2, 4} chords/bar from a distribution learned from the per-song beat-level chord streams when
available (chord changes per bar), else the prior {1: 0.55, 2: 0.35, 4: 0.10}; the last bar of a phrase is restricted to
{1, 2} so the cadence chord starts no later than beat 3 (the melody's cadence note is held >= a half note). Phase 5: the LAST bar
of the label that ends the form is fixed to 1 chord, so the arrangement's held final bar (one sustained sonority = the bar's chord)
is the final cadence chord by construction and never the pre-cadence dominant (the hold used to truncate a 2-chord final bar).
Arrangement (v5 F1 conventions): intro = section 0 with keys+melody muted (drums too when "bass_only"), outro = last
section with melody muted and the final bar held, breakdown = drums muted for 4 bars in the first non-A section of the
middle half, fills in the last bar of every section (from the form plan's boundary_fill_pool or the fixture pool).
"""
from __future__ import annotations

from scripts.v6.gen.common import draw_from

BARS_PER_SECTION = 8
BALLAD_BPM = 85.0
FIXED_FORM = ("A", "A", "B", "A")
FALLBACK_TEMPLATE = ("A", "A", "B", "A", "B", "C", "A", "A")
CADENCES = ("authentic", "half", "plagal", "deceptive")
P_CADENCE = {"final": {"authentic": 0.60, "half": 0.10, "plagal": 0.20, "deceptive": 0.10},
             "internal": {"authentic": 0.20, "half": 0.55, "plagal": 0.15, "deceptive": 0.10}}
HR_PRIOR = {1: 0.55, 2: 0.35, 4: 0.10}
INTRO_BASS_ONLY_Q = 0.33
BREAKDOWN_BARS = 4


def canonicalize_labels(seq: list) -> list:
    seen: dict = {}
    out = []
    for lab in seq:
        if lab not in seen:
            seen[lab] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[len(seen)]
        out.append(seen[lab])
    return out


def plan_form(fp: dict | None, tag: str, n_bars: int | None = None) -> dict:
    """Section labels (8 bars each). fp = form_plan_v5.json dict or None."""
    if fp is not None:
        n_sec = int(draw_from({k: float(v) for k, v in fp["length_distribution"].items()}, f"{tag}|form|n_sections")) if n_bars is None \
            else max(1, n_bars // BARS_PER_SECTION)
        if fp.get("R1", {}).get("pass"):
            labs = [draw_from(fp["start_distribution"], f"{tag}|form|label0")]
            for i in range(1, n_sec):
                labs.append(draw_from(fp["transition_probs"][labs[-1]], f"{tag}|form|label{i}|from={labs[-1]}"))
            raw, source = labs, "corpus_label_markov"
        else:
            tpl = fp.get("R1", {}).get("fallback_template") or list(FALLBACK_TEMPLATE)
            raw, source = [tpl[i % len(tpl)] for i in range(n_sec)], "R1_FAILED_fixed_template"
        intro_q = fp.get("intro_density_quantile")
    else:
        n_sec = max(1, n_bars // BARS_PER_SECTION) if n_bars else len(FIXED_FORM)
        tpl = FIXED_FORM if n_sec <= len(FIXED_FORM) else FALLBACK_TEMPLATE
        raw, source = [tpl[i % len(tpl)] for i in range(n_sec)], "fixed_template_(no form_plan_v5.json)"
        intro_q = None
    labels = canonicalize_labels(raw)
    return {"n_sections": n_sec, "bars_per_section": BARS_PER_SECTION, "labels_raw": raw, "labels": labels, "label_source": source,
            "n_bars": n_sec * BARS_PER_SECTION, "intro_density_quantile": intro_q,
            "sections": [{"index": i, "label": lab, "start_bar": i * BARS_PER_SECTION, "n_bars": BARS_PER_SECTION} for i, lab in enumerate(labels)]}


def harmonic_rhythm_distribution(chord_streams: dict) -> tuple[dict, str]:
    """{1,2,4}: probability from chord changes per bar over the per-song beat-level streams; prior when empty."""
    counts = {1: 0, 2: 0, 4: 0}
    n = 0
    for sha in sorted(chord_streams):
        seq = [e["state"] for e in chord_streams[sha]["chord_stream"]]
        for b in range(0, len(seq) - 3, 4):
            bar = seq[b:b + 4]
            changes = sum(1 for i in range(1, 4) if bar[i] != bar[i - 1])
            counts[1 if changes == 0 else (2 if changes == 1 else 4)] += 1
            n += 1
    if n == 0:
        return dict(HR_PRIOR), "prior"
    return {k: round(v / n, 6) for k, v in counts.items()}, f"learned_from_{len(chord_streams)}_chord_streams_{n}_bars"


def plan_phrases(form: dict, tag: str, bpm: float, hr_dist: dict) -> dict:
    """Per LABEL: phrases (start_bar within the section, n_bars, position, cadence) + harmonic rhythm per bar."""
    ballad = bpm < BALLAD_BPM
    nb = form["bars_per_section"]
    phrase_len = nb if ballad else nb // 2
    out = {}
    final_label = form["labels"][-1]  # its last bar is the song's held final bar: exactly the cadence chord (see module doc)
    for lab in sorted(set(form["labels"])):
        phrases = []
        for k in range(nb // phrase_len):
            pos = "final" if k == nb // phrase_len - 1 else "internal"
            cad = draw_from(P_CADENCE[pos], f"{tag}|phrase|{lab}|{k}|cadence|{pos}")
            phrases.append({"index": k, "start_bar": k * phrase_len, "n_bars": phrase_len, "position": pos, "cadence": cad})
        hr = []
        for b in range(nb):
            last = (b % phrase_len) == phrase_len - 1
            if lab == final_label and b == nb - 1:
                hr.append(1)
                continue
            w = {str(k): float(v) for k, v in hr_dist.items() if not (last and int(k) == 4)}
            hr.append(int(draw_from(w, f"{tag}|hr|{lab}|bar{b}")))
        out[lab] = {"phrases": phrases, "harmonic_rhythm": hr, "phrase_len_bars": phrase_len, "final_bar_single_chord": lab == final_label}
    return {"ballad": ballad, "label_plans": out, "cadence_table": P_CADENCE, "harmonic_rhythm_distribution": hr_dist}


def arrangement(form: dict, tag: str, fill_pool: list) -> dict:
    labels, n, nb = form["labels"], form["n_sections"], form["bars_per_section"]
    arr = [{"mute": [], "fill": None, "hold": False} for _ in range(n * nb)]
    q = form.get("intro_density_quantile")
    intro_bass_only = (q is not None and q < INTRO_BASS_ONLY_Q) if q is not None else (draw_from({"bass_only": INTRO_BASS_ONLY_Q, "drums_and_bass": 1 - INTRO_BASS_ONLY_Q}, f"{tag}|intro") == "bass_only")
    if n > 1:
        for k in range(nb):
            arr[k]["mute"] = ["keys", "melody"] + (["drums"] if intro_bass_only else [])
        for k in range((n - 1) * nb, n * nb):
            arr[k]["mute"] = sorted(set(arr[k]["mute"]) | {"melody"})
    arr[n * nb - 1]["hold"] = True
    lo, hi = n // 4, -(-3 * n // 4)
    breakdown = next((i for i in range(n) if lo <= i < hi and labels[i] != "A"), None)
    if breakdown is not None:
        for k in range(breakdown * nb, breakdown * nb + BREAKDOWN_BARS):
            arr[k]["mute"] = sorted(set(arr[k]["mute"]) | {"drums"})
    fills = []
    for i in range(n):
        w = {f"{j:03d}": float(e["count"]) for j, e in enumerate(fill_pool)}
        e = fill_pool[int(draw_from(w, f"{tag}|fill|section{i}"))]
        arr[i * nb + nb - 1]["fill"] = {"snare": int(e["snare"]), "hat": int(e["hat"])}
        fills.append({"section": i, "snare": int(e["snare"]), "hat": int(e["hat"])})
    info = {"intro": {"section": 0, "mode": "bass_only" if intro_bass_only else "drums_and_bass", "intro_density_quantile": q},
            "outro": {"section": n - 1, "melody_muted": n > 1, "final_bar_held": True},
            "breakdown": {"section": breakdown, "drums_muted_bars": BREAKDOWN_BARS if breakdown is not None else 0, "middle_half": [lo, hi]},
            "fills": fills, "fill_pool_size": len(fill_pool)}
    return {"per_bar": arr, "info": info}


def build_plan(models: dict, tag: str, bpm: float, n_bars: int | None = None) -> dict:
    form = plan_form(models.get("form_plan"), tag, n_bars)
    hr_dist, hr_src = harmonic_rhythm_distribution(models.get("chord_streams") or {})
    ph = plan_phrases(form, tag, bpm, hr_dist)
    arr = arrangement(form, tag, models["fill_pool"])
    return {"form": form, "ballad": ph["ballad"], "label_plans": ph["label_plans"], "cadence_table": P_CADENCE,
            "harmonic_rhythm": {"distribution": hr_dist, "source": hr_src}, "arrangement": arr}
