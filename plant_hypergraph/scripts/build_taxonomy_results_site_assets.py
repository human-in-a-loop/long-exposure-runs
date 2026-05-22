# created: 2026-05-18T00:00:00+00:00
# cycle: 34
# run_id: run-phytograph-taxonomy-results-site
# agent: worker
# milestone: _plan/taxonomy-results-site
"""Build public data and figure assets for the taxonomy results site."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS_TSV = ROOT / "data/reopen/final_free_tier_track_status.tsv"
SITE = ROOT / "taxonomy_results_site"
DATA = SITE / "data"
TABLES = DATA / "evidence_tables"
FIGURES = SITE / "assets/figures"


TRACK_LABELS = {
    "Track 1": "Reticulation and polyploidy",
    "Track 2": "Ecological anachronisms",
    "Track 3": "Convergent traits",
    "Track 4": "Crop wild relatives and climate",
    "Track 5": "Chemodiversity",
    "Track 6": "Botanical model benchmark",
}

TRACK_SLUGS = {
    "Track 1": "track1",
    "Track 2": "track2",
    "Track 3": "track3",
    "Track 4": "track4",
    "Track 5": "track5",
    "Track 6": "track6",
}

STATUS_LABELS = {
    "sidecar_readiness_uncontrolled": "sidecar evidence only",
    "H2_remains_not_supported_or_data_limited": "not supported or data-limited",
    "confound_limited": "confound-limited",
    "still_data_limited": "data-limited",
    "H5_remains_source_biased": "source-biased",
    "environment_limited_untested": "untested under local/open constraints",
}

STATUS_CLASSES = {
    "sidecar_readiness_uncontrolled": "status-caution",
    "H2_remains_not_supported_or_data_limited": "status-negative",
    "confound_limited": "status-caution",
    "still_data_limited": "status-limited",
    "H5_remains_source_biased": "status-bias",
    "environment_limited_untested": "status-limited",
}

PUBLIC_BASIS = {
    "Track 1": "namespace reconciliation and source-control review",
    "Track 2": "ghost-interaction evidence and control closure",
    "Track 3": "trait and confound matrix review",
    "Track 4": "occurrence and climate-readiness review",
    "Track 5": "non-Duke temporal chemistry review and source ablation",
    "Track 6": "local/open benchmark feasibility review",
}

PUBLIC_COUNTS = {
    "Track 6": "0 approved local/open model pairings; 0 executed responses; 0 scored responses",
}

PUBLIC_BLOCKERS = {
    "Track 6": "No approved local/open model and response set was available under the study constraints",
}

PUBLIC_FUTURE = {
    "Track 6": "Approved local/open model weights and documented response rows with scorer diagnostics",
}

TRACK_SUMMARIES = {
    "Track 1": {
        "plain_question": "Where do plant histories depart from a simple branching tree?",
        "field_focus": "Reticulation evidence, chromosome/ploidy rows, hybridization rows, accepted-key projection.",
        "public_result": "Evidence was visible in sidecar records, but controlled accepted-name recovery did not support a promoted reticulation result.",
        "evidence_type": "reticulation evidence",
        "validation_use": "accepted-key projection and matched controls",
        "rejection_reason": "Sidecar records did not clear controlled accepted-key recovery.",
    },
    "Track 2": {
        "plain_question": "Can lost animal-plant partnerships be detected from plant evidence?",
        "field_focus": "Canonical anachronism held-outs, modern dispersal-failure evidence, living-disperser controls.",
        "public_result": "No canonical held-out case passed the validation criteria with the available accepted-name evidence.",
        "evidence_type": "anachronism support",
        "validation_use": "held-out recovery and control checks",
        "rejection_reason": "Modern-failure and source-class support were insufficient.",
    },
    "Track 3": {
        "plain_question": "Can repeated plant traits be separated from family size and sampling density?",
        "field_focus": "Trait carriers, family-size controls, sampling-density controls, projection-loss gates.",
        "public_result": "Trait signals remained inseparable from confounders, so convergence claims were not promoted.",
        "evidence_type": "trait carrier matrix",
        "validation_use": "convergence controls",
        "rejection_reason": "No trait was controlled-ready.",
    },
    "Track 4": {
        "plain_question": "Can crop relatives be ranked for climate substitution from local evidence?",
        "field_focus": "Crop-wild-relative rows, occurrence records, climate summaries, expert comparator rows.",
        "public_result": "Occurrences were recovered, but numeric climate summaries and comparator rows were absent.",
        "evidence_type": "crop and occurrence evidence",
        "validation_use": "climate-substitution validation",
        "rejection_reason": "No numeric BIOCLIM vectors or validation-allowed comparators.",
    },
    "Track 5": {
        "plain_question": "Can under-screened plants be prioritized for chemistry from source-backed evidence?",
        "field_focus": "Compound-class rows, dated chemistry evidence, source-ablation checks.",
        "public_result": "The evidence remained dominated by one source family, so chemistry predictions were not promoted.",
        "evidence_type": "phytochemistry evidence",
        "validation_use": "temporal holdout and source ablation",
        "rejection_reason": "Non-Duke dated strata were insufficient.",
    },
    "Track 6": {
        "plain_question": "Can botanical reasoning questions be scored against audited local responses?",
        "field_focus": "Question bank, scoring rubric, response rows, scorer diagnostics.",
        "public_result": "The benchmark scaffold exists, but no audited local/open response set was available for scoring.",
        "evidence_type": "benchmark response evidence",
        "validation_use": "scored local/open response rows",
        "rejection_reason": "No audited response rows were produced.",
    },
}


def read_status_rows() -> list[dict[str, str]]:
    with STATUS_TSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_counts(text: str) -> list[tuple[str, str]]:
    parts = [part.strip() for part in text.split(";") if part.strip()]
    parsed: list[tuple[str, str]] = []
    for part in parts:
        tokens = part.split(" ", 1)
        if tokens and any(ch.isdigit() for ch in tokens[0]):
            parsed.append((tokens[0], tokens[1] if len(tokens) > 1 else "count"))
        else:
            parsed.append(("not quantified", part))
    return parsed


def build_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    tracks = []
    for row in rows:
        track = row["track"]
        summary = TRACK_SUMMARIES[track]
        tracks.append(
            {
                "track": track,
                "slug": TRACK_SLUGS[track],
                "label": TRACK_LABELS[track],
                "status_code": row["final_free_tier_status"],
                "status_label": STATUS_LABELS[row["final_free_tier_status"]],
                "status_class": STATUS_CLASSES[row["final_free_tier_status"]],
                "plain_question": summary["plain_question"],
                "field_focus": summary["field_focus"],
                "public_result": summary["public_result"],
                "validated_branch_basis": PUBLIC_BASIS.get(track, row["validated_branch_basis"]),
                "key_counts": PUBLIC_COUNTS.get(track, row["key_counts"]),
                "counts": [
                    {"value": value, "label": label}
                    for value, label in parse_counts(PUBLIC_COUNTS.get(track, row["key_counts"]))
                ],
                "blocker": PUBLIC_BLOCKERS.get(track, row["blocker"]),
                "future_data_required": PUBLIC_FUTURE.get(track, row["future_data_required"]),
                "claim_boundary": row["claim_boundary"],
                "evidence_type": summary["evidence_type"],
                "validation_use": summary["validation_use"],
                "rejection_reason": summary["rejection_reason"],
            }
        )
    return {
        "title": "PhytoGraph taxonomy results review",
        "updated": "2026-05-18",
        "study_boundary": (
            "No cross-track prediction or speculation entries were promoted beyond table headers, "
            "because the required validation predicates were not met."
        ),
        "substrate": {
            "taxa_indexed": 60000,
            "schema": "typed plant-evidence hypergraph",
            "accepted_name_policy": "accepted names are operational join keys; synonym and source conflicts remain visible",
            "evidence_policy": "observed evidence, inferred fields, predicted fields, and missing data are separated",
        },
        "routes": [
            "Start Here",
            "Choose a Track",
            "What Was Found",
            "Why Claims Were Not Promoted",
            "Evidence Explorer",
            "Methods for Taxonomists",
            "Limitations",
            "What Evidence Would Change the Conclusion",
        ],
        "tracks": tracks,
        "source_notes": [
            "Final synthesis report",
            "Audit report",
            "Falsification and ablation report",
            "Research contribution ledger",
            "Final local-evidence track status table",
            "Track-local reports and evidence tables",
        ],
    }


def write_track_tables(summary: dict[str, object]) -> None:
    for track in summary["tracks"]:
        payload = [
            {
                "track": track["track"],
                "theme": track["label"],
                "source": track["validated_branch_basis"],
                "accepted_name_status": "accepted-key evidence reviewed; unresolved joins retained as limitations",
                "evidence_type": track["evidence_type"],
                "key_counts": track["key_counts"],
                "validation_use": track["validation_use"],
                "status": track["status_label"],
                "rejection_reason": track["rejection_reason"],
                "claim_boundary": track["claim_boundary"],
                "future_evidence_predicate": track["future_data_required"],
            }
        ]
        write_json(TABLES / f"{track['slug']}.json", payload)


def svg_page(width: int, height: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">\n'
        "<defs>\n"
        "<style><![CDATA[\n"
        "text{font-family:Inter,Arial,sans-serif;fill:#17201b} .title{font-size:26px;font-weight:800}"
        ".label{font-size:15px;font-weight:700}.small{font-size:12px}.tiny{font-size:10px}"
        ".muted{fill:#5f6f67}.box{fill:#f7faf8;stroke:#b8c8bf;stroke-width:1.2}.green{fill:#dff2df;stroke:#6aa56a}"
        ".amber{fill:#fff1cf;stroke:#c28b23}.red{fill:#ffe0dd;stroke:#c75b4e}.blue{fill:#dfeefd;stroke:#5b89c7}"
        ".violet{fill:#eee4ff;stroke:#8b70bf}.gray{fill:#edf0ef;stroke:#8c9892}.line{stroke:#698075;stroke-width:2;fill:none}"
        "]]></style>\n</defs>\n"
        f"{body}\n</svg>\n"
    )


def campaign_hypergraph(summary: dict[str, object]) -> str:
    centers = [(170, 180), (370, 110), (570, 180), (170, 350), (370, 420), (570, 350)]
    colors = ["blue", "amber", "violet", "green", "red", "gray"]
    body = ['<rect width="760" height="520" fill="#fbfdfb"/>', '<text x="36" y="46" class="title">Typed plant-evidence hypergraph</text>']
    body.append('<circle cx="370" cy="260" r="78" fill="#e8f5ec" stroke="#477b59" stroke-width="2"/>')
    body.append('<text x="318" y="250" class="label">Shared</text><text x="300" y="272" class="label">plant evidence</text>')
    for idx, track in enumerate(summary["tracks"]):
        x, y = centers[idx]
        body.append(f'<path d="M370 260 L{x} {y}" class="line"/>')
        body.append(f'<rect x="{x-95}" y="{y-42}" width="190" height="84" rx="8" class="{colors[idx]}"/>')
        body.append(f'<text x="{x-78}" y="{y-10}" class="label">{esc(track["track"])}</text>')
        body.append(f'<text x="{x-78}" y="{y+14}" class="small">{esc(track["label"])}</text>')
    body.append('<text x="36" y="492" class="small muted">Each theme attaches typed evidence to the same accepted-name substrate; unsupported claims remain unpromoted.</text>')
    return svg_page(760, 520, "\n".join(body))


def track_status(summary: dict[str, object]) -> str:
    body = ['<rect width="900" height="520" fill="#fbfdfb"/>', '<text x="34" y="42" class="title">Final status by biological theme</text>']
    color_map = {
        "status-caution": "amber",
        "status-negative": "red",
        "status-limited": "gray",
        "status-bias": "violet",
    }
    y = 82
    for track in summary["tracks"]:
        color = color_map[track["status_class"]]
        body.append(f'<rect x="36" y="{y}" width="828" height="58" rx="7" class="{color}"/>')
        body.append(f'<text x="54" y="{y+24}" class="label">{esc(track["track"])} · {esc(track["label"])}</text>')
        body.append(f'<text x="54" y="{y+46}" class="small">{esc(track["status_label"])} — {esc(track["claim_boundary"])}</text>')
        y += 68
    return svg_page(900, 520, "\n".join(body))


def evidence_recovered(summary: dict[str, object]) -> str:
    rows = [
        ("Track 1", 22, 2, "event taxa vs WFO projected"),
        ("Track 2", 31, 0, "candidates vs held-outs passing"),
        ("Track 3", 3069, 0, "trait rows vs controlled-ready traits"),
        ("Track 4", 3358, 0, "occurrences vs numeric climate vectors"),
        ("Track 5", 1, 0, "source stratum vs validation-ready stratum"),
        ("Track 6", 0, 0, "responses vs scored responses"),
    ]
    body = ['<rect width="900" height="500" fill="#fbfdfb"/>', '<text x="34" y="42" class="title">Evidence recovered versus promotion-ready evidence</text>']
    y = 90
    max_val = 3358
    for track, recovered, ready, note in rows:
        rec_w = max(3, int(610 * recovered / max_val))
        ready_w = max(3 if ready else 0, int(610 * ready / max_val))
        body.append(f'<text x="36" y="{y+14}" class="label">{track}</text>')
        body.append(f'<rect x="142" y="{y}" width="610" height="20" rx="3" fill="#edf0ef"/>')
        body.append(f'<rect x="142" y="{y}" width="{rec_w}" height="20" rx="3" fill="#79a887"/>')
        if ready_w:
            body.append(f'<rect x="142" y="{y+26}" width="{ready_w}" height="14" rx="3" fill="#2f6d4a"/>')
        body.append(f'<text x="768" y="{y+15}" class="small">{recovered} / {ready} · {esc(note)}</text>')
        y += 62
    body.append('<text x="36" y="470" class="small muted">Upper bars show local evidence recovered; lower promotion-ready bars remain zero where validation predicates failed.</text>')
    return svg_page(900, 500, "\n".join(body))


def accepted_key_joins(summary: dict[str, object]) -> str:
    rows = [
        ("Taxonomy substrate", "60,000 taxa indexed", "usable as review surface", "green"),
        ("Reticulation", "2 accepted-name projections", "sidecar signal uncontrolled", "amber"),
        ("Ghost interaction", "0 of 8 held-outs passed", "modern-failure support missing", "red"),
        ("Domestication", "0 comparator rows", "climate validation blocked", "gray"),
    ]
    body = ['<rect width="820" height="430" fill="#fbfdfb"/>', '<text x="34" y="44" class="title">Accepted-name joins and blockers</text>']
    x = 58
    for label, metric, note, color in rows:
        body.append(f'<rect x="{x}" y="104" width="162" height="130" rx="9" class="{color}"/>')
        body.append(f'<text x="{x+16}" y="135" class="label">{esc(label)}</text>')
        body.append(f'<text x="{x+16}" y="166" class="small">{esc(metric)}</text>')
        body.append(f'<text x="{x+16}" y="196" class="tiny">{esc(note)}</text>')
        if x < 560:
            body.append(f'<path d="M{x+162} 170 L{x+202} 170" class="line"/>')
        x += 202
    body.append('<text x="52" y="316" class="label">Interpretation</text>')
    body.append('<text x="52" y="342" class="small muted">The site exposes accepted-name joins as evidence gates, not as hidden cleanup.</text>')
    body.append('<text x="52" y="365" class="small muted">When a join or control fails, the biological claim stays below promotion threshold.</text>')
    return svg_page(820, 430, "\n".join(body))


def source_bias(summary: dict[str, object]) -> str:
    body = ['<rect width="820" height="430" fill="#fbfdfb"/>', '<text x="34" y="44" class="title">Source dominance and source-density caution</text>']
    body.append('<rect x="70" y="98" width="290" height="220" rx="9" class="violet"/>')
    body.append('<text x="92" y="132" class="label">Track 5</text>')
    body.append('<text x="92" y="164" class="small">Full predictor rows existed only with</text>')
    body.append('<text x="92" y="186" class="small">the dominant chemistry source present.</text>')
    body.append('<rect x="420" y="98" width="290" height="220" rx="9" class="amber"/>')
    body.append('<text x="442" y="132" class="label">Cross-track caution</text>')
    body.append('<text x="442" y="164" class="small">Source density can mimic biological</text>')
    body.append('<text x="442" y="186" class="small">signal unless ablations preserve it.</text>')
    body.append('<path d="M210 338 C300 374 474 374 565 338" class="line"/>')
    body.append('<text x="214" y="390" class="small muted">Negative source-ablation outcomes are scientific results: they prevent overclaiming.</text>')
    return svg_page(820, 430, "\n".join(body))


def bioclim(summary: dict[str, object]) -> str:
    body = ['<rect width="820" height="430" fill="#fbfdfb"/>', '<text x="34" y="44" class="title">Occurrence and BIOCLIM readiness</text>']
    rows = [("post-filter occurrence records", 3358, "#79a887"), ("numeric BIOCLIM vectors", 0, "#c75b4e"), ("validation-allowed comparator rows", 0, "#c75b4e")]
    y = 105
    for label, value, color in rows:
        width = 600 if value else 3
        body.append(f'<text x="70" y="{y+18}" class="label">{esc(label)}</text>')
        body.append(f'<rect x="330" y="{y}" width="360" height="24" rx="4" fill="#edf0ef"/>')
        body.append(f'<rect x="330" y="{y}" width="{min(width, 360)}" height="24" rx="4" fill="{color}"/>')
        body.append(f'<text x="710" y="{y+18}" class="label">{value}</text>')
        y += 70
    body.append('<text x="70" y="350" class="small muted">Occurrences alone did not support climate-substitution recommendations without numeric climate vectors and comparators.</text>')
    return svg_page(820, 430, "\n".join(body))


def validation_outcomes(summary: dict[str, object]) -> str:
    labels = ["supported", "not supported", "data-limited", "source-biased", "untested"]
    values = [0, 1, 3, 1, 1]
    colors = ["#2f6d4a", "#c75b4e", "#8c9892", "#8b70bf", "#c28b23"]
    body = ['<rect width="760" height="430" fill="#fbfdfb"/>', '<text x="34" y="44" class="title">Validation outcomes across themes</text>']
    x = 80
    for label, value, color in zip(labels, values, colors):
        h = 34 + value * 44
        body.append(f'<rect x="{x}" y="{310-h}" width="86" height="{h}" rx="5" fill="{color}"/>')
        body.append(f'<text x="{x+32}" y="{300-h}" class="label">{value}</text>')
        body.append(f'<text x="{x-12}" y="338" class="small">{esc(label)}</text>')
        x += 128
    body.append('<text x="54" y="392" class="small muted">The study promoted no cross-track predictions; closure statuses preserve negative, limited, and biased outcomes.</text>')
    return svg_page(760, 430, "\n".join(body))


def future_predicates(summary: dict[str, object]) -> str:
    body = ['<rect width="980" height="560" fill="#fbfdfb"/>', '<text x="34" y="44" class="title">Evidence that would change the conclusion</text>']
    y = 84
    for track in summary["tracks"]:
        body.append(f'<rect x="40" y="{y}" width="900" height="62" rx="7" class="box"/>')
        body.append(f'<text x="58" y="{y+24}" class="label">{esc(track["track"])} · {esc(track["label"])}</text>')
        body.append(f'<text x="58" y="{y+48}" class="small">{esc(track["future_data_required"])}</text>')
        y += 74
    return svg_page(980, 560, "\n".join(body))


FIGURE_BUILDERS = {
    "campaign_hypergraph_map.svg": campaign_hypergraph,
    "track_status_overview.svg": track_status,
    "evidence_recovered_vs_rejected.svg": evidence_recovered,
    "accepted_key_joins.svg": accepted_key_joins,
    "source_bias_summary.svg": source_bias,
    "occurrence_bioclim_readiness.svg": bioclim,
    "validation_outcomes.svg": validation_outcomes,
    "future_evidence_predicates.svg": future_predicates,
}


def main() -> None:
    rows = read_status_rows()
    summary = build_summary(rows)
    DATA.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    write_json(DATA / "site_summary.json", summary)
    write_track_tables(summary)
    for name, builder in FIGURE_BUILDERS.items():
        (FIGURES / name).write_text(builder(summary), encoding="utf-8")
    print(f"wrote {DATA / 'site_summary.json'}")
    print(f"wrote {len(summary['tracks'])} evidence tables")
    print(f"wrote {len(FIGURE_BUILDERS)} figures")


if __name__ == "__main__":
    main()
