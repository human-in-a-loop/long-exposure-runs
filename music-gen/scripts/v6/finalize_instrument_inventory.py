#!/usr/bin/python3
"""Phase 4 (instrument realism) — final pass over INVENTORY.json: attach render results, determinism
checks and caveats, prune silent/error entries, then write SUMMARY.md.

created: 2026-10-04
milestone: M-V6-INSTRUMENTS-1

Order of operations for a full rebuild:
  build_instrument_inventory.py            # sfz/sf2 entries (+ .ram.sfz wrappers)
  render_patch_test.py --all               # smoke-render sfz + sf2
  render_vst_test.py                       # register + render Surge XT / Dexed entries
  finalize_instrument_inventory.py         # this file
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_patch_test import INVENTORY, RENDERS, main as render_main  # noqa: E402

NOTES = [
    "- **Determinism**: `sfizz_render` and `fluidsynth` renders are byte-identical across runs *when the sfz is loaded through the "
    "generated `*.ram.sfz` wrapper* (`<control> hint_ram_based=1`). Without it, sfizz streams long one-shot tails from disk in a "
    "background thread and 1 of 3 renders of the Salamander Drumkit differed (max |diff| 0.008, 9.5% of samples, starting at 1.67 s). "
    "Surge XT and Dexed via DawDreamer are **not** bit-deterministic (both differed between two identical renders); treat the "
    "`dawdreamer` backend as audition-only or freeze its output once per song.",
    "- **Not sourced**: Karoryfer (Meatbass, Black and Green) — the freebies page routes through a shop/checkout flow, no direct asset "
    "URLs; sfzinstruments GitHub repos (SalamanderDrumkit, karoryfer.*, jlearman.*) — github.com HTML/codeload/API all return 403 "
    "through the proxy, and `add_repo` has no access to that org (the Salamander Drumkit was taken from archive.org instead); "
    "VSCO-2 Community Edition — vis.versilstudios.com fails TLS through the proxy and the set is ~3 GB; Virtual Playing Orchestra — skipped (size); "
    "Timbres of Heaven / Arachno — hosts not probed after the budget was met, and both have redistribution-restricted licenses; "
    "HuggingFace mirrors (`projectlosangeles/SFZ-Instruments` 12.5 GB, `soundfonts4u`) are re-uploads tagged CC-BY-NC-SA by the uploader, so they were skipped.",
    "- **GeneralUser GS**: schristiancollins.com serves a JS-only page (no direct asset path), so the official 2.0.2 release zip was taken from "
    "its archive.org mirror; the sf2 INFO chunk reads 'GeneralUser GS 2.0.2 / S. Christian Collins' and `documentation/LICENSE.txt` is included.",
    "- **Dexed**: 1.0.1 ships only its own default cartridge (no Yamaha ROM1A 'E.PIANO 1'/'BASS 1'); its electric_piano entries are "
    "decaying FM keys chosen by envelope analysis, not a Rhodes clone. The FreePats FM Piano 1/2 (CC0, sampled DX7-style) are the better e-piano picks.",
    "- **Realism caveats**: FreePats synth pads/leads/strings/brass are single-velocity-layer GM-style synth samples (useful for variety, not "
    "'realistic' horns); real horn sections only exist in the GM sf2 banks (GeneralUser GS / MuseScore_General 'Brass Section'). "
    "Muted/palm-muted electric guitar exists only as GM program 28 in the sf2 banks (the FreePats DI Strat can be processed with pedalboard instead). "
    "Upright bass only as GM program 32. Brushed kit: GeneralUser GS / MuseScore_General 'Brush' (128:40) plus AVL Blonde Bop HR.",
    "- **Licenses**: everything is CC0 / CC-BY / CC-BY-SA / MIT / GPL-with-sample-exception / GeneralUser GS License v2.0 — all fine for a private, "
    "never-released research project. CC-BY-SA items (Salamander Drumkit, AVL kits) and GPL-exception items would need attribution/share-alike only on release.",
    "- Preinstalled banks (FluidR3_GM, AVL sf2 kits, Surge XT, Dexed) are listed with absolute paths and `preinstalled: true`; they count 0 MB toward downloads.",
]


def main() -> int:
    # 1. prune silent/error entries using the render summary (no re-render)
    render_main(["--prune-from-summary"])
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    summ = json.load(open(RENDERS / "_render_summary.json", encoding="utf-8"))
    # 2. attach render metrics per entry
    for lib in inv["libraries"]:
        for inst in lib["instruments"]:
            r = summ.get(f"{lib['slug']}::{inst['name']}")
            if r:
                inst["render"] = {k: r.get(k) for k in ("wav", "rms_dbfs", "peak_dbfs", "duration_sec", "sha256", "status")}
    # 3. determinism results
    det_path = RENDERS / "_determinism_sfz.json"
    inv["determinism_checks"] = {
        "sfz_ram_wrapper": json.load(open(det_path)) if det_path.exists() else None,
        "sf2": {"generaluser_gs::Grand Piano [0:0]": True, "fluidsynth": "byte-identical on repeat"},
        "dawdreamer": {"surge_xt": False, "dexed": False},
        "note": "see summary_notes[0]",
    }
    inv["summary_notes"] = NOTES
    counts = {}
    for lib in inv["libraries"]:
        for inst in lib["instruments"]:
            counts[inst["role"]] = counts.get(inst["role"], 0) + 1
    inv["role_counts"] = dict(sorted(counts.items()))
    inv["disk_used_mb"] = float(subprocess.run(["du", "-sm", str(INVENTORY.parent)], capture_output=True, text=True).stdout.split()[0])
    with open(INVENTORY, "w", encoding="utf-8") as fh:
        json.dump(inv, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("role counts:", inv["role_counts"], "| rejected:", len(inv["rejected"]), "| disk MB:", inv["disk_used_mb"])
    # 4. SUMMARY.md
    from instrument_summary import main as summary_main
    return summary_main()


if __name__ == "__main__":
    sys.exit(main())
