"""Generate scorecard TSV + MD from verdict.json (RC10 Branch C)."""
from __future__ import annotations

import json
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
V = json.loads((WS / "data/rc10_impl/other_vocals/verdict.json").read_text())

tsv_rows = [
    "song_id\tstem\tcandidate\tvariant\tprimary_metric\tsecondary_metric\tpass"
]

for song in V["per_song"]:
    sid = song["song_id"]
    for cid, res in song["vocals"].items():
        if "error" in res:
            tsv_rows.append(f"{sid}\tvocals\t{cid}\terror\tNA\tNA\tFALSE")
            continue
        for tag in ("raw", "pp"):
            r = res[tag]
            tsv_rows.append(
                f"{sid}\tvocals\t{cid}\t{tag}"
                f"\t{r['f0_agreement_pct']:.2f}%"
                f"\tcov={r['voiced_time_coverage_ratio']:.3f}"
                f"\t{'TRUE' if r['pass'] else 'FALSE'}"
            )
    for cid, res in song["other_residual"].items():
        if "error" in res:
            tsv_rows.append(f"{sid}\tother_residual\t{cid}\terror\tNA\tNA\tFALSE")
            continue
        for tag in ("raw", "pp"):
            r = res[tag]
            tsv_rows.append(
                f"{sid}\tother_residual\t{cid}\t{tag}"
                f"\tcos={r['mean_chroma_cosine']:.3f}"
                f"\tdens_ratio={r.get('density_ratio_vs_baseline','NA')}"
                f"\t{'TRUE' if r.get('pass') else 'FALSE'}"
            )

tsv = "\n".join(tsv_rows) + "\n"
(WS / "data/rc10_impl/other_vocals/scorecard.tsv").write_text(tsv)

# Markdown scorecard
lines = [
    "# RC10 Branch C Scorecard (c53 clone-2)",
    "",
    f"**Verdict:** `{V['verdict']}`   ",
    f"**Vocals winner:** {V['vocals_winner']}   ",
    f"**Other-residual winner:** {V['other_residual_winner']}   ",
    f"**Pass counts:** vocals {V['vocals_pass_count']}/5, other-residual {V['other_residual_pass_count']}/5.",
    "",
    "## Vocals — per song / candidate / variant",
    "",
    "| song | candidate | variant | f0_agreement | coverage_ratio | PASS |",
    "|------|-----------|---------|--------------|----------------|------|",
]
for song in V["per_song"]:
    sid = song["song_id"]
    for cid, res in song["vocals"].items():
        if "error" in res:
            lines.append(f"| `{sid}` | {cid} | error | NA | NA | ❌ |")
            continue
        for tag in ("raw", "pp"):
            r = res[tag]
            lines.append(
                f"| `{sid}` | {cid} | {tag} | "
                f"{r['f0_agreement_pct']:.2f}% | "
                f"{r['voiced_time_coverage_ratio']:.3f} | "
                f"{'✅' if r['pass'] else '❌'} |"
            )
lines += [
    "",
    "## Other-residual — per song / candidate / variant",
    "",
    "| song | candidate | variant | chroma_cosine | density_ratio | PASS |",
    "|------|-----------|---------|---------------|---------------|------|",
]
for song in V["per_song"]:
    sid = song["song_id"]
    for cid, res in song["other_residual"].items():
        if "error" in res:
            lines.append(f"| `{sid}` | {cid} | error | NA | NA | ❌ |")
            continue
        for tag in ("raw", "pp"):
            r = res[tag]
            lines.append(
                f"| `{sid}` | {cid} | {tag} | "
                f"{r['mean_chroma_cosine']:.3f} | "
                f"{r.get('density_ratio_vs_baseline','NA')} | "
                f"{'✅' if r.get('pass') else '❌'} |"
            )
lines.append("")
lines.append(
    "PASS gates per rubric §D2 — vocals: f0_agreement_pct ≥ 60% AND coverage_ratio ∈ [0.5, 2.0]; "
    "other-residual: mean_chroma_cosine ≥ 0.55 AND density_ratio ∈ [0.5, 2.0]."
)
(WS / "docs/rc10_other_vocals_scorecard.md").write_text("\n".join(lines) + "\n")
print("wrote scorecard.tsv and scorecard.md")
