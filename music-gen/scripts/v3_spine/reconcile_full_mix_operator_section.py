#!/usr/bin/env python3
"""c5 Track B: full-mix vs merged reconciliation on the operator-section."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import mido

SEC = Path("data/v3_spine/31a164f845f8e27e/operator_section")


def count_notes(p: Path):
    mf = mido.MidiFile(p)
    total = 0
    pc = Counter()
    parts = Counter()
    for tr in mf.tracks:
        for m in tr:
            if m.type == "note_on":
                total += 1
                pc[m.note % 12] += 1
                parts[m.channel] += 1
    return total, pc, parts


def main():
    full = SEC / "canonical_midi" / "full_mix.mid"
    merged = SEC / "merged.mid"
    fc, fpc, fpar = count_notes(full)
    mc, mpc, mpar = count_notes(merged)
    all_pcs = set(fpc) | set(mpc)
    delta = {int(p): fpc.get(p, 0) - mpc.get(p, 0) for p in sorted(all_pcs)}
    only_fm = sorted(set(fpar) - set(mpar))
    only_m = sorted(set(mpar) - set(fpar))
    findings = []
    if only_fm:
        findings.append({
            "kind": "channels_in_full_mix_only",
            "channels": only_fm,
            "note_counts_by_channel": {ch: fpar[ch] for ch in only_fm},
        })
    out = SEC / "full_mix_reconciliation_operator_section.json"
    payload = {
        "cycle": 5,
        "section": "operator_section",
        "full_mix_note_count": fc,
        "merged_note_count": mc,
        "per_pitch_class_delta_full_minus_merged": delta,
        "parts_present_in_full_mix_absent_in_merged": only_fm,
        "parts_present_in_merged_absent_in_full_mix": only_m,
        "full_mix_only_findings": findings,
        "reconciliation_policy": "per_stem_favor_default_per_operator_directive_point_4",
        "auto_merge_this_cycle": False,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"full={fc} merged={mc} findings={len(findings)}")


if __name__ == "__main__":
    main()
