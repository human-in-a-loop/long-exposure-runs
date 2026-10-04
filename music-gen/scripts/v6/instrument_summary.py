#!/usr/bin/python3
"""Phase 4 (instrument realism) — write workspace/instruments/SUMMARY.md from INVENTORY.json + renders.

created: 2026-10-04
milestone: M-V6-INSTRUMENTS-1
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_patch_test import INSTR_ROOT, INVENTORY, RENDERS  # noqa: E402

ROLE_ORDER = ["piano", "electric_piano", "organ", "electric_bass", "acoustic_bass", "synth_bass", "electric_guitar",
              "acoustic_guitar", "drums", "pad", "strings_pad", "lead", "brass", "percussion"]

# default patch pool per role: (slug, instrument-name prefix) in priority order; only kept if present in the inventory
POOL = {
    "piano": [("salamander_grand_piano", "Salamander Grand Piano V3"), ("upright_piano_kw", "Upright Piano KW"),
              ("generaluser_gs", "Grand Piano"), ("old_piano_fb", "Old Piano FB")],
    "electric_piano": [("fm_piano1", "FM Piano 1"), ("generaluser_gs", "Electric Piano 1"), ("musescore_general", "Tine Electric Piano"),
                       ("surge_xt", "Surge XT: Soft Suitcase"), ("surge_xt", "Surge XT: DX EP"), ("fm_piano2", "FM Piano 2")],
    "organ": [("drawbar_organ_emulation", "Drawbar Organ"), ("percussive_organ_emulation", "Percussive Organ"),
              ("rock_organ_emulation", "Rock Organ"), ("generaluser_gs", "Drawbar Organ")],
    "electric_bass": [("finger_bass_yr", "Finger Bass YR"), ("picked_bass_yr", "Picked Bass YR"),
                      ("generaluser_gs", "Finger Bass"), ("generaluser_gs", "Pick Bass"), ("musescore_general", "Fingered Bass")],
    "acoustic_bass": [("generaluser_gs", "Acoustic Bass"), ("musescore_general", "Acoustic Bass"), ("freepats_gm", "Acoustic Bass")],
    "synth_bass": [("lately_bass", "Lately Bass"), ("synth_bass_1", "Synth Bass 1"), ("surge_xt", "Surge XT: Fingered"),
                   ("dexed", "Dexed: Thunder")],
    "electric_guitar": [("eguitar_fsbs_clean", "EGuitar FSBS clean"), ("eguitar_fsbs_jazz", "EGuitar FSBS jazz"),
                        ("eguitar_fsbs_direct", "EGuitar FSBS direct"), ("generaluser_gs", "Muted Guitar"),
                        ("musescore_general", "Palm Muted Guitar"), ("generaluser_gs", "Clean Guitar")],
    "acoustic_guitar": [("spanish_classical_guitar", "Spanish Classical Guitar"), ("fss_steel_string_guitar", "FSS Steel String"),
                        ("generaluser_gs", "Nylon Guitar"), ("generaluser_gs", "Steel Guitar")],
    "drums": [("salamander_drumkit", "Salamander Drumkit"), ("muldjord_kit", "Muldjord Kit"), ("avl_drumkits_sf2", "AVL Black Pearl"),
              ("avl_drumkits_sf2", "AVL Blonde Bop HR"), ("generaluser_gs", "Brush"), ("generaluser_gs", "Room"),
              ("musescore_general", "Jazz [128"), ("generaluser_gs", "Standard 1")],
    "pad": [("new_age_pad", "New Age Pad"), ("synth_pad_bowed", "Synth Pad Bowed"), ("synth_pad_choir", "Synth Pad Choir"),
            ("surge_xt", "Surge XT: Pad 1"), ("surge_xt", "Surge XT: MKS-70"), ("dexed", "Dexed: Slow3D"), ("generaluser_gs", "Warm Pad")],
    "strings_pad": [("synth_strings_1", "Synth Strings 1"), ("synth_strings_2", "Synth Strings 2"), ("generaluser_gs", "Strings"),
                    ("musescore_general", "Strings"), ("surge_xt", "Surge XT: Subtle Comb")],
    "lead": [("synth_square", "Synth Square"), ("synth_fifths", "Synth Fifths"), ("synth_calliope", "Synth Calliope"),
             ("surge_xt", "Surge XT: Classic Lead 1"), ("surge_xt", "Surge XT: Crisp PWM"), ("dexed", "Dexed: SAW EM UP")],
    "brass": [("generaluser_gs", "Brass Section"), ("musescore_general", "Brass Section"), ("synth_brass_1", "Synth Brass 1"),
              ("synth_brass_2", "Synth Brass 2")],
    "percussion": [("world_percussion", "World Percussion")],
}


def du_mb(path: Path) -> float:
    out = subprocess.run(["du", "-sm", str(path)], capture_output=True, text=True).stdout
    return float(out.split()[0]) if out else 0.0


def main() -> int:
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    summ_path = RENDERS / "_render_summary.json"
    summ = json.load(open(summ_path)) if summ_path.exists() else {}
    by_role: dict[str, list] = defaultdict(list)
    lib_by_slug = {l["slug"]: l for l in inv["libraries"]}
    for lib in inv["libraries"]:
        for inst in lib["instruments"]:
            r = summ.get(f"{lib['slug']}::{inst['name']}", {})
            by_role[inst["role"]].append((lib, inst, r))
    lines = ["# Instrument sources — Phase 4 (instrument realism)", "",
             f"Inventory: `{INVENTORY.relative_to(INSTR_ROOT.parent.parent)}` — {len(inv['libraries'])} libraries, "
             f"{sum(len(l['instruments']) for l in inv['libraries'])} playable entries, {len(inv.get('rejected', []))} rejected.", "",
             f"Disk used by `workspace/instruments/` (incl. `_renders/`): **{du_mb(INSTR_ROOT) / 1024:.2f} GB** "
             f"(downloaded libraries {inv.get('total_downloaded_mb', 0) / 1000:.2f} GB; renders {du_mb(RENDERS):.0f} MB).", "",
             "Backends: `sfizz_render 1.2.3` (.sfz), `fluidsynth 2.3.4` (.sf2), `dawdreamer 0.9.0` (Surge XT 1.3.4 / Dexed 1.0.1 VST3).",
             "Test render: 4 bars @ 100 BPM, 3 velocity tiers, role register (see `scripts/v6/render_patch_test.py`).", "",
             "## Role -> available options", "", "| role | n | library | instrument | backend | license | RMS dBFS |", "|---|---|---|---|---|---|---|"]
    for role in ROLE_ORDER + sorted(set(by_role) - set(ROLE_ORDER)):
        rows = by_role.get(role, [])
        if not rows:
            lines.append(f"| {role} | 0 | — | — | — | — | — |")
            continue
        for k, (lib, inst, r) in enumerate(rows):
            lines.append(f"| {role if k == 0 else ''} | {len(rows) if k == 0 else ''} | {lib['slug']} | {inst['name']} | "
                         f"{inst.get('backend') or lib['format']} | {lib['license']['id']} | {r.get('rms_dbfs', '')} |")
    lines += ["", "## Libraries", "", "| slug | format | size MB | license | source |", "|---|---|---|---|---|"]
    for lib in inv["libraries"]:
        lines.append(f"| {lib['slug']} | {lib['format']} | {lib['size_mb']} | [{lib['license']['id']}]({lib['license']['url']}) | {lib['source_url']} |")
    lines += ["", "## Rejected entries (silent or render error)", ""]
    if inv.get("rejected"):
        lines += ["| slug | instrument | role | reason | detail |", "|---|---|---|---|---|"]
        for r in inv["rejected"]:
            lines.append(f"| {r['slug']} | {r['instrument']} | {r['role']} | {r['reason']} | {str(r.get('detail', ''))[:120]} |")
    else:
        lines.append("none")
    lines += ["", "## Recommended default patch pool per role", "",
              "Priority order; the generator should sample from these per song (first two are the realistic 'A/B' pair).", ""]
    for role in ROLE_ORDER:
        picks = []
        for slug, prefix in POOL.get(role, []):
            lib = lib_by_slug.get(slug)
            if not lib:
                continue
            for inst in lib["instruments"]:
                if inst["name"].startswith(prefix):
                    picks.append(f"`{slug}` / {inst['name']} ({inst.get('backend') or lib['format']})")
                    break
        lines.append(f"- **{role}**: " + ("; ".join(picks) if picks else "_no option sourced_"))
    lines += ["", "## Not sourced / caveats", ""]
    lines += inv.get("summary_notes", [])
    (INSTR_ROOT / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {INSTR_ROOT / 'SUMMARY.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
