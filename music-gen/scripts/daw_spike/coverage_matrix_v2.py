#!/usr/bin/env python3
"""M-DAW-SPIKE-1 coverage matrix v2 — cycle-12 refresh.

Regenerates the 5-axis × 2-engine coverage matrix from cycle-1
(daw_spike_report.md §1) with the cycle-12 GAP-closure results
folded in:

  GAP-1 (Ardour MIDI import)            : redefined-GAP
  GAP-2 (Ardour VST3 plugin-param auto) : still-GAP (broader than VST3)

Writes:
  data/daw_spike/coverage_matrix_v2.json  (machine-readable)
  docs/figures/daw_spike_coverage_v2.png  (heatmap)
"""
import json
import sys
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

assert sys.executable == '/usr/bin/python3', sys.executable

ROOT = pathlib.Path("/home/user/long-exposure-runs/music-gen")
OUT_JSON = ROOT / "data/daw_spike/coverage_matrix_v2.json"
OUT_FIG  = ROOT / "docs/figures/daw_spike_coverage_v2.png"

# Fixed 4-color legend for status. The cycle-3 matrix used GREEN /
# PARTIAL / GAP. Cycle-12 adds "redefined-GAP" — the primary path
# still isn't reachable via the originally-documented mechanism, but
# an alternative documented fallback closes the axis end-to-end.
STATUS_COLORS = {
    "GREEN":         "#2ca02c",
    "PARTIAL":       "#d4a017",
    "GAP":           "#d62728",
    "redefined-GAP": "#1f77b4",
}
STATUS_TO_CODE = {"GREEN": 3, "PARTIAL": 2, "redefined-GAP": 1, "GAP": 0}

AXES = [
    {
        "axis": "session_build",
        "ardour_cycle3":     "GREEN",
        "dawdreamer_cycle3": "GREEN",
        "ardour_cycle12":    "GREEN",
        "dawdreamer_cycle12":"GREEN",
        "notes": "unchanged — Lua create_session + DawDreamer RenderEngine both live.",
    },
    {
        "axis": "midi_import",
        "ardour_cycle3":     "GAP",
        "dawdreamer_cycle3": "GREEN",
        "ardour_cycle12":    "redefined-GAP",
        "dawdreamer_cycle12":"GREEN",
        "notes": (
            "GAP-1 fallback #2 closes end-to-end via a DIFFERENT mechanism: "
            "pre-render MIDI via fluidsynth + hand-authored "
            "<Source>/<Region>/<Playlist> audio-region XML → Ardour renders "
            "the audio (env_correlation=1.000, peak_ratio_db=0.00 dB vs "
            "pre-rendered WAV). Primary Lua-driven MIDI-region binding "
            "remains absent — the axis IS reachable, but not via the primary "
            "path originally documented."
        ),
        "tolerance_metric": "env_correlation >= 0.5 AND peak_ratio_db >= -20 dB",
        "tolerance_result": {"env_correlation": 1.000, "peak_ratio_db": 0.00},
        "evidence": "data/daw_spike/gap1_midi_import_measurement.json",
    },
    {
        "axis": "instrument_and_effect_params",
        "ardour_cycle3":     "GREEN",
        "dawdreamer_cycle3": "GREEN",
        "ardour_cycle12":    "GREEN",
        "dawdreamer_cycle12":"GREEN",
        "notes": "unchanged — set_processor_param works cross-format (VST3, LV2, Lua).",
    },
    {
        "axis": "automation",
        "ardour_cycle3":     "PARTIAL",
        "dawdreamer_cycle3": "GREEN",
        "ardour_cycle12":    "PARTIAL",
        "dawdreamer_cycle12":"GREEN",
        "notes": (
            "GAP-2 fallback #2 (LV2 reverb — ACE Reverb / a-reverb.lv2) DID "
            "NOT close the automation-delivery half. Wet-mix automation "
            "authored 0.05→0.90 on the Blend param + XML state='Play' patch, "
            "render second/first RMS = 1.0000 (flat), vs cycle-1 track-Amp "
            "baseline 2.05 and DawDreamer reference 2.46. NEW FINDING: "
            "Ardour Lua-authored plugin_automation() fails to deliver on "
            "LV2 as well as VST3 — the gap is broader than cycle-1's "
            "VST3-scoped diagnosis. Track-Amp automation remains the only "
            "verified Ardour automation delivery path (unchanged from "
            "cycle-1 PARTIAL)."
        ),
        "tolerance_metric": "second/first RMS ratio >= 1.20 (locked at investigation-phase)",
        "tolerance_result": {"second_over_first_lv2": 1.0000},
        "evidence": "data/daw_spike/gap2_lv2_measurement.json",
    },
    {
        "axis": "render_offline",
        "ardour_cycle3":     "GREEN",
        "dawdreamer_cycle3": "GREEN",
        "ardour_cycle12":    "GREEN",
        "dawdreamer_cycle12":"GREEN",
        "notes": (
            "unchanged — ardour8-export headless + engine.render() both "
            "produce 8s @ 48 kHz stereo WAVs. Cycle-12 note: on sessions "
            "with hand-authored audio regions, ardour8-export can abort on "
            "cleanup (SIGABRT / double-free) after the render is already "
            "committed. Output WAV bytes remain valid."
        ),
    },
]


def status_transition(a3, a12, d3, d12):
    if a3 == a12 and d3 == d12:
        return "unchanged"
    return f"ardour {a3}->{a12}; dawdreamer {d3}->{d12}"


def emit_json():
    matrix = {
        "matrix_version": 2,
        "cycle": 12,
        "created_by": "M-DAW-SPIKE-1/gap-closure clone-2 of fork ed041ef4c1dc",
        "run_id": "run-2026-08-28T040704Z",
        "baseline_matrix": "docs/daw_spike_report.md §1 (cycle 1 / cycle 3)",
        "cycle3_baseline_counts": {"GREEN": 6, "PARTIAL": 1, "GAP": 2, "cells": 9},
        "cycle12_counts": None,   # filled below
        "axes": [],
        "gaps_closed_this_cycle": [],
        "gaps_still_open": [],
    }
    counts = {"GREEN": 0, "PARTIAL": 0, "GAP": 0, "redefined-GAP": 0}
    for a in AXES:
        row = {
            "axis": a["axis"],
            "ardour":     {"cycle3": a["ardour_cycle3"],
                           "cycle12": a["ardour_cycle12"]},
            "dawdreamer": {"cycle3": a["dawdreamer_cycle3"],
                           "cycle12": a["dawdreamer_cycle12"]},
            "transition": status_transition(a["ardour_cycle3"], a["ardour_cycle12"],
                                             a["dawdreamer_cycle3"], a["dawdreamer_cycle12"]),
            "notes": a["notes"],
        }
        if "tolerance_metric" in a:
            row["tolerance_metric"] = a["tolerance_metric"]
            row["tolerance_result"] = a["tolerance_result"]
            row["evidence"] = a["evidence"]
        matrix["axes"].append(row)
        counts[a["ardour_cycle12"]]   = counts.get(a["ardour_cycle12"], 0) + 1
        counts[a["dawdreamer_cycle12"]] = counts.get(a["dawdreamer_cycle12"], 0) + 1

    # Which cycle-3 GAPs closed?
    for a in AXES:
        if a["ardour_cycle3"] == "GAP":
            if a["ardour_cycle12"] == "GREEN":
                matrix["gaps_closed_this_cycle"].append(
                    {"axis": a["axis"], "engine": "ardour", "verdict": "GREEN"})
            elif a["ardour_cycle12"] == "redefined-GAP":
                matrix["gaps_closed_this_cycle"].append(
                    {"axis": a["axis"], "engine": "ardour", "verdict": "redefined-GAP"})
            else:
                matrix["gaps_still_open"].append(
                    {"axis": a["axis"], "engine": "ardour", "verdict": a["ardour_cycle12"]})
        if a["ardour_cycle3"] == "PARTIAL" and a["ardour_cycle12"] == "PARTIAL":
            matrix["gaps_still_open"].append(
                {"axis": a["axis"], "engine": "ardour",
                 "verdict": "PARTIAL (unchanged; fallback did NOT promote to GREEN)"})
    matrix["cycle12_counts"] = counts
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(matrix, indent=2))
    return matrix


def emit_figure(matrix):
    axes = [a["axis"] for a in AXES]
    ardour_cycle12 = [a["ardour_cycle12"] for a in AXES]
    dawdreamer_cycle12 = [a["dawdreamer_cycle12"] for a in AXES]

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    grid = np.zeros((len(axes), 2), dtype=int)
    for i, a in enumerate(AXES):
        grid[i, 0] = STATUS_TO_CODE[a["ardour_cycle12"]]
        grid[i, 1] = STATUS_TO_CODE[a["dawdreamer_cycle12"]]

    color_lookup = np.array([
        STATUS_COLORS["GAP"],
        STATUS_COLORS["redefined-GAP"],
        STATUS_COLORS["PARTIAL"],
        STATUS_COLORS["GREEN"],
    ])
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            ax.add_patch(plt.Rectangle((j, len(axes) - i - 1), 1, 1,
                                        facecolor=color_lookup[grid[i, j]],
                                        edgecolor="white", linewidth=2))
            label = ardour_cycle12[i] if j == 0 else dawdreamer_cycle12[i]
            ax.text(j + 0.5, len(axes) - i - 1 + 0.5, label,
                    ha="center", va="center", fontsize=9,
                    color="white", weight="bold")

    ax.set_xlim(0, 2); ax.set_ylim(0, len(axes))
    ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(["Ardour", "DawDreamer"], fontsize=11)
    ax.set_yticks([len(axes) - i - 0.5 for i in range(len(axes))])
    ax.set_yticklabels(axes, fontsize=10)
    ax.set_title("M-DAW-SPIKE-1 coverage matrix v2 (cycle 12)\n"
                 "cycle-3 baseline: 6 GREEN / 1 PARTIAL / 2 GAP → "
                 f"cycle-12: {matrix['cycle12_counts']['GREEN']} GREEN / "
                 f"{matrix['cycle12_counts']['PARTIAL']} PARTIAL / "
                 f"{matrix['cycle12_counts']['GAP']} GAP / "
                 f"{matrix['cycle12_counts']['redefined-GAP']} redefined-GAP",
                 fontsize=10)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    # Undo the invert since we build coordinates manually.
    ax.invert_yaxis()

    # Legend
    handles = [plt.Rectangle((0,0),1,1, facecolor=STATUS_COLORS[s])
               for s in ["GREEN","PARTIAL","redefined-GAP","GAP"]]
    ax.legend(handles, ["GREEN","PARTIAL","redefined-GAP","GAP"],
              loc="lower center", bbox_to_anchor=(0.5, -0.20),
              ncol=4, frameon=False, fontsize=9)

    plt.tight_layout()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_FIG, dpi=110, bbox_inches="tight")
    plt.close()


def main():
    matrix = emit_json()
    emit_figure(matrix)
    print(f"[OK] wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"[OK] wrote {OUT_FIG.relative_to(ROOT)}")
    print(json.dumps(matrix["cycle12_counts"], indent=2))


if __name__ == "__main__":
    main()
