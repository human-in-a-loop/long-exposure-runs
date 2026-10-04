#!/usr/bin/python3
"""v6 Phase 3 — microtiming_report_v6: render data/v6/rules/microtiming_v6_README.md (tables) from microtiming_v6.json.

created: 2026-10-04
milestone: M-V6-GEN-3/humanization

  /usr/bin/python3 scripts/v6/microtiming_report_v6.py [data/v6/rules/microtiming_v6.json]
"""
from __future__ import annotations

import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.gen.common import WS, read_json  # noqa: E402
from scripts.v6.gen import microtiming_model as M  # noqa: E402


def f(x, nd=1) -> str:
    return "-" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def table(head: list, rows: list) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def slot_table(pool: dict, key: str, nd: int = 1, scale: float = 1.0) -> str:
    rows = []
    for s in M.STREAMS:
        v = pool["streams"][s][key]
        rows.append([s] + [f(None if x is None else x * scale, nd) for x in v])
    return table(["stream"] + [str(i) for i in range(16)], rows)


def pool_section(name: str, pool: dict) -> str:
    sw = pool["swing_ratios_drums"]
    lines = [f"### {name}", "",
             f"songs: {pool['n_songs']} ({', '.join(pool['songs']) if pool['songs'] else '-'}); grid confidence tally: {pool.get('grid_confidence_tally')}", "",
             f"Swing ratio across songs (drums, odd-8th vs even-8th): min {f(sw.get('0.0'), 3)} / Q1 {f(sw.get('0.25'), 3)} / median {f(sw.get('0.5'), 3)} / Q3 {f(sw.get('0.75'), 3)} / max {f(sw.get('1.0'), 3)} (IQR {f(sw.get('iqr'), 3)}, n={sw.get('n')})",
             "", "Per-stream swing (offset of odd-8th slots 2/6/10/14 in ms, ratio):", "",
             table(["stream", "offset_ms", "offset_f16", "ratio", "n_odd", "n_even", "n_assigned", "rejected", "reject_rate"],
                   [[s, f(pool["streams"][s]["swing"]["offset_ms"], 2), f(pool["streams"][s]["swing"]["offset_f16"], 4), f(pool["streams"][s]["swing"]["ratio"], 3),
                     pool["streams"][s]["swing"]["n_odd"], pool["streams"][s]["swing"]["n_even"], pool["streams"][s]["n_assigned"], pool["streams"][s]["n_rejected"],
                     f(pool["streams"][s]["reject_rate"], 3)] for s in M.STREAMS]),
             "", "Per-slot mean deviation (ms, + = late):", "", slot_table(pool, "slot_mean_ms"), "", "Per-slot std of the deviation (ms):", "", slot_table(pool, "slot_std_ms"),
             "", "Per-slot onset counts:", "", slot_table(pool, "slot_n", 0),
             "", f"Bass vs kick lag at coincident slots (ms, + = bass late): mean {f(pool['bass_kick_lag_ms']['mean'], 2)}, std {f(pool['bass_kick_lag_ms']['std'], 2)}, n={pool['bass_kick_lag_ms']['n']}",
             "", "Velocity by slot (dB relative to the stream mean):", "", slot_table(pool, "vel_by_slot_db"),
             "", "Velocity by beat class and hypermeter (dB rel.):", "",
             table(["stream", "downbeat", "backbeat", "beat3", "offbeat", "bar%4=0", "1", "2", "3", "bar%8=0", "1", "2", "3", "4", "5", "6", "7"],
                   [[s] + [f(pool["streams"][s]["vel_by_beat_class_db"][c], 2) for c in M.BEAT_CLASSES] + [f(x, 2) for x in pool["streams"][s]["vel_by_bar_mod4_db"]]
                    + [f(x, 2) for x in pool["streams"][s]["vel_by_bar_mod8_db"]] for s in M.STREAMS]),
             "", f"Fill density (drum onsets in the last beat of boundary bars / other bars): mod4 ratio {f(pool['fill_density']['mod4']['ratio'], 3)}, mod8 ratio {f(pool['fill_density']['mod8']['ratio'], 3)}",
             f"Bass duration proxy (decay-to-20 dB / IOI): mean {f(pool['bass_duration']['mean_frac'], 3)}, quantiles {pool['bass_duration']['quantiles']}, by class {pool['bass_duration']['by_class']}", ""]
    return "\n".join(lines)


def render_readme(mt: dict) -> str:
    out = ["# microtiming_v6 — performance model learned from the corpus stems", "",
           f"generator: `{mt['generator']}`; songs: {mt['n_songs']}; params: `{mt['params']}`", "",
           "Deviations are measured from the smoothed beat grid (known bpm forced into librosa.beat.beat_track, tightness "
           f"{mt['params']['tightness']}, local linear smoothing over +/-{mt['params']['beat_smoothing_halfwidth']} beats); onsets with |dev| > 0.4 x 16th are rejected. "
           "Slot = 16th index in the bar (0 = downbeat; 4/12 = backbeats; 2/6/10/14 = odd 8ths). Velocity = dB of the 30 ms RMS after the onset, relative to the stream mean.", "",
           "## Per-song grid fit, rejected onsets and swing", "",
           table(["sha16", "band", "title", "bpm", "conf", "contrast", "beat_hit", "tempo_ratio", "phase_margin", "n_bars", "swing_hat", "swing_drums", "lag_ms", "kick/snare/hat/bass onsets", "rejected", "reject_rate"],
                 [[s, e["band"], (e.get("title") or "")[:28], f(e["grid"]["bpm"]), e["grid"]["confidence"], f(e["grid"].get("beat_contrast"), 3), f(e["grid"].get("beat_hit_frac"), 3),
                   f(e["grid"].get("tempo_ratio"), 4), f(e["grid"]["phase_margin"], 3), e["grid"]["n_bars"], f(e["swing"]["hat"]["ratio"], 3), f(e["swing"]["drums"]["ratio"], 3),
                   f(e["bass_kick_lag"]["mean_ms"], 1), "/".join(str(e["streams"][k]["n_assigned"]) for k in M.STREAMS),
                   sum(e["streams"][k]["n_rejected"] for k in M.STREAMS),
                   f(sum(e["streams"][k]["n_rejected"] for k in M.STREAMS) / max(1, sum(e["streams"][k]["n_detected"] for k in M.STREAMS)), 3)]
                  for s, e in sorted(mt["per_song"].items())]), "", "## Pooled models", ""]
    out.append(pool_section("all songs", mt["pooled"]["all"]))
    for k in sorted(mt["pooled"]):
        if k.startswith("band_"):
            out.append(pool_section(k, mt["pooled"][k]))
    for t, p in sorted(mt["pooled"]["near_tempo"].items(), key=lambda kv: float(kv[0])):
        out.append(pool_section(f"near_tempo {t} bpm (+/-15 %)", p))
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else WS / "data/v6/rules/microtiming_v6.json"
    dst = src.with_name(src.stem + "_README.md")
    dst.write_text(render_readme(read_json(src)), encoding="utf-8")
    print(f"wrote {dst}")
