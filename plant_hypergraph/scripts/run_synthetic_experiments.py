# created: 2026-05-17T02:25:00Z
# cycle: 4
# run_id: run-2026-05-17T004540Z
# agent: worker
# milestone: M6
"""Run deterministic M6 baseline and hypergraph experiments."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import generate_synthetic_benchmark as gen
from tools import baselines


ABLATIONS = [
    ("none", set(), False, False),
    ("remove_synonym", {"synonym_cluster"}, False, False),
    ("remove_trait", {"trait_syndrome"}, False, False),
    ("randomize_trait", set(), True, False),
    ("remove_occurrence_geography_context", {"occurrence_provenance", "regional_checklist_context"}, False, False),
    ("remove_reticulate", {"reticulate_or_hybrid_signal"}, False, False),
    ("remove_missing_rank_bridge", {"missing_rank_bridge"}, False, False),
    ("collapse_to_clique_expansion", set(), False, False),
    ("randomize_accepted_names", set(), False, True),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_strict_control(out_dir: Path, seed: int) -> Path:
    args = type(
        "Args",
        (),
        {
            "seed": seed,
            "out_dir": str(out_dir),
            "n_families": 4,
            "genera_per_family": 3,
            "species_per_genus": 5,
            "synonym_rate": 0,
            "missing_rank_rate": 0,
            "reticulation_rate": 0,
            "trait_convergence_rate": 0,
            "occurrence_noise_rate": 0,
        },
    )()
    gen.generate(args)
    return out_dir


def metric_float(row: dict[str, object], key: str) -> float:
    return float(row.get(key, 0) or 0)


def best_by_model(rows: list[dict[str, object]], ablation: str = "none") -> dict[str, dict[str, object]]:
    return {row["model"]: row for row in rows if row["ablation"] == ablation and row["case_type"] == "all"}


def write_figures(out_dir: Path, results: list[dict[str, object]], ablation_rows: list[dict[str, object]], case_rows: list[dict[str, object]], false_rows: list[dict[str, object]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    none = [row for row in results if row["ablation"] == "none" and row["case_type"] == "all"]
    models = [row["model"] for row in none]
    flat = [metric_float(row, "flat_exact_match") for row in none]
    syn = [metric_float(row, "synonym_normalized_exact_match") for row in none]
    dist = [metric_float(row, "mean_hierarchy_distance") for row in none]

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    x = range(len(models))
    ax1.bar([i - 0.18 for i in x], flat, width=0.36, label="flat exact", color="#4f7cac")
    ax1.bar([i + 0.18 for i in x], syn, width=0.36, label="synonym-normalized", color="#6aa56a")
    ax1.set_ylabel("accuracy")
    ax1.set_ylim(0, 1.05)
    ax2 = ax1.twinx()
    ax2.plot(list(x), dist, color="#9b3d3d", marker="o", label="hierarchy distance")
    ax2.set_ylabel("mean hierarchy distance")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(models, rotation=30, ha="right")
    ax1.set_title("Flat and hierarchy-aware metrics by model family")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right")
    ax1.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "metric_comparison.png", dpi=160)
    plt.close(fig)

    heat = defaultdict(dict)
    for row in ablation_rows:
        if row["model"] == "native_hypergraph":
            heat[row["ablation"]]["native_hypergraph"] = metric_float(row, "mean_hierarchy_distance_delta_vs_none")
    labels = [row["ablation"] for row in ablation_rows if row["model"] == "native_hypergraph"]
    values = [[heat[label].get("native_hypergraph", 0.0)] for label in labels]
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    im = ax.imshow(values, cmap="RdBu_r", aspect="auto")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xticks([0])
    ax.set_xticklabels(["delta distance"])
    ax.set_title("Ablation effect on native hypergraph")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(out_dir / "ablation_heatmap.png", dpi=160)
    plt.close(fig)

    case_types = sorted({row["case_type"] for row in case_rows if row["case_type"] != "all"})
    selected = ["tree_dag", "ordinary_graph", "clique_expansion", "native_hypergraph"]
    by_case = {(row["case_type"], row["model"]): metric_float(row, "synonym_normalized_exact_match") for row in case_rows}
    fig, ax = plt.subplots(figsize=(10, 5.5))
    width = 0.18
    for j, model in enumerate(selected):
        ax.bar([i + (j - 1.5) * width for i in range(len(case_types))], [by_case.get((case, model), 0) for case in case_types], width=width, label=model)
    ax.set_xticks(range(len(case_types)))
    ax.set_xticklabels(case_types, rotation=25, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("synonym-normalized exact match")
    ax.set_title("Model performance by case type")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "case_type_breakdown.png", dpi=160)
    plt.close(fig)

    families = sorted({row["edge_family"] for row in false_rows})
    counts = [sum(int(row["introduced_taxon_pairs"]) for row in false_rows if row["edge_family"] == fam) for fam in families]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(families, counts, color="#7d5a8c")
    ax.set_ylabel("introduced taxon pairs")
    ax.set_title("False pairwise similarities from clique expansion")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "clique_false_similarity.png", dpi=160)
    plt.close(fig)


def public_sample_check(public_sample_dir: Path) -> dict[str, object]:
    path = public_sample_dir / "hyperedges.csv"
    rows = baselines.load_csv(path)
    synthetic_values = sorted({row.get("is_synthetic", "") for row in rows})
    return {
        "path": str(path),
        "hyperedge_rows": len(rows),
        "edge_families": sorted({row["edge_family"] for row in rows}),
        "all_is_synthetic_false": synthetic_values == ["false"],
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    benchmark = baselines.load_benchmark(args.benchmark_dir)

    all_predictions: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    for name, remove, randomize_trait, randomize_names in ABLATIONS:
        preds, metrics = baselines.run_model_suite(
            benchmark,
            ablation=name,
            remove_families=remove,
            randomize_trait=randomize_trait,
            randomize_names=randomize_names,
            seed=args.seed,
        )
        all_predictions.extend(preds)
        results.extend(metrics)

    no_ablation_preds = [row for row in all_predictions if row["ablation"] == "none"]
    case_rows: list[dict[str, object]] = []
    case_types = sorted({row["case_type"] for row in benchmark["examples"]})
    for model in baselines.MODEL_FAMILIES:
        model_preds = [row for row in no_ablation_preds if row["model"] == model]
        for case_type in case_types:
            case_rows.append(
                baselines.evaluate_predictions(
                    model_preds,
                    benchmark["taxa"],
                    benchmark["names"],
                    benchmark["hyperedges"],
                    model,
                    "none",
                    case_type=case_type,
                )
            )

    none_by_model = best_by_model(results)
    ablation_rows: list[dict[str, object]] = []
    for row in results:
        base = none_by_model.get(row["model"])
        if not base:
            continue
        ablation_rows.append(
            {
                **row,
                "flat_exact_match_delta_vs_none": f"{metric_float(row, 'flat_exact_match') - metric_float(base, 'flat_exact_match'):.6f}",
                "synonym_normalized_exact_match_delta_vs_none": f"{metric_float(row, 'synonym_normalized_exact_match') - metric_float(base, 'synonym_normalized_exact_match'):.6f}",
                "mean_hierarchy_distance_delta_vs_none": f"{metric_float(row, 'mean_hierarchy_distance') - metric_float(base, 'mean_hierarchy_distance'):.6f}",
            }
        )

    false_rows = baselines.clique_false_similarity_rows(benchmark["hyperedges"])

    with tempfile.TemporaryDirectory() as tmp:
        strict_dir = make_strict_control(Path(tmp) / "strict_control", args.seed)
        strict_benchmark = baselines.load_benchmark(strict_dir)
        _, strict_results = baselines.run_model_suite(strict_benchmark, ablation="strict_negative_control", seed=args.seed)

    result_fields = ["ablation", "model", "split", "case_type", "n", "flat_exact_match", "synonym_normalized_exact_match", "mean_hierarchy_distance", "hierarchy_coherence_violation_rate", "mean_reticulate_near_miss"]
    baselines.write_csv(out_dir / "results.csv", result_fields, results)
    baselines.write_csv(out_dir / "predictions.csv", ["ablation", "example_id", "split", "case_type", "model", "prediction", "target"], all_predictions)
    baselines.write_csv(out_dir / "case_type_breakdown.csv", result_fields, case_rows)
    baselines.write_csv(out_dir / "ablation_results.csv", result_fields + ["flat_exact_match_delta_vs_none", "synonym_normalized_exact_match_delta_vs_none", "mean_hierarchy_distance_delta_vs_none"], ablation_rows)
    baselines.write_csv(out_dir / "clique_false_similarity.csv", ["edge_id", "edge_family", "taxon_members", "introduced_taxon_pairs", "provenance"], false_rows)
    baselines.write_csv(out_dir / "strict_negative_control.csv", result_fields, strict_results)
    write_figures(out_dir, results, ablation_rows, case_rows, false_rows)

    summary = {
        "created": "2026-05-17T02:25:00Z",
        "cycle": 4,
        "milestone": "M6",
        "seed": args.seed,
        "benchmark_dir": args.benchmark_dir,
        "public_sample_check": public_sample_check(Path(args.public_sample_dir)),
        "result_rows": len(results),
        "prediction_rows": len(all_predictions),
        "case_type_rows": len(case_rows),
        "ablation_rows": len(ablation_rows),
        "clique_false_similarity_rows": len(false_rows),
        "strict_negative_control_rows": len(strict_results),
        "key_findings": summarize_findings(results, case_rows, ablation_rows, strict_results),
    }
    write_json(out_dir / "summary.json", summary)
    stable_hash_files = {
        "results.csv",
        "ablation_results.csv",
        "case_type_breakdown.csv",
        "clique_false_similarity.csv",
        "strict_negative_control.csv",
    }
    hashes = {path.name: sha256_file(path) for path in sorted(out_dir.glob("*.csv")) if path.name in stable_hash_files}
    summary["file_hashes_sha256"] = hashes
    write_json(out_dir / "summary.json", summary)
    return summary


def summarize_findings(results: list[dict[str, object]], case_rows: list[dict[str, object]], ablation_rows: list[dict[str, object]], strict_results: list[dict[str, object]]) -> dict[str, object]:
    none = best_by_model(results)
    strict = {row["model"]: row for row in strict_results if row["case_type"] == "all"}
    reticulate = {row["model"]: row for row in case_rows if row["case_type"] == "reticulate"}
    missing = {row["model"]: row for row in case_rows if row["case_type"] == "missing_rank"}
    native_ab = {row["ablation"]: row for row in ablation_rows if row["model"] == "native_hypergraph"}
    return {
        "best_flat_model": min(none.values(), key=lambda r: (-metric_float(r, "flat_exact_match"), r["model"]))["model"],
        "best_hierarchy_distance_model": min(none.values(), key=lambda r: (metric_float(r, "mean_hierarchy_distance"), r["model"]))["model"],
        "native_reticulate_synonym_accuracy": reticulate.get("native_hypergraph", {}).get("synonym_normalized_exact_match", ""),
        "tree_reticulate_synonym_accuracy": reticulate.get("tree_dag", {}).get("synonym_normalized_exact_match", ""),
        "native_missing_rank_distance": missing.get("native_hypergraph", {}).get("mean_hierarchy_distance", ""),
        "tree_missing_rank_distance": missing.get("tree_dag", {}).get("mean_hierarchy_distance", ""),
        "native_remove_reticulate_distance_delta": native_ab.get("remove_reticulate", {}).get("mean_hierarchy_distance_delta_vs_none", ""),
        "native_random_trait_distance_delta": native_ab.get("randomize_trait", {}).get("mean_hierarchy_distance_delta_vs_none", ""),
        "strict_control_tree_distance": strict.get("tree_dag", {}).get("mean_hierarchy_distance", ""),
        "strict_control_native_distance": strict.get("native_hypergraph", {}).get("mean_hierarchy_distance", ""),
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--benchmark-dir", default="data/synthetic_benchmark/v0.1")
    p.add_argument("--public-sample-dir", default="data/public_taxonomy_sample/v0.1")
    p.add_argument("--out-dir", default="data/experiments/synthetic_v0.1")
    p.add_argument("--seed", type=int, default=20260517)
    p.add_argument("--ablation", default="all", choices=["all"])
    return p


def main() -> None:
    print(json.dumps(run(parser().parse_args()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
