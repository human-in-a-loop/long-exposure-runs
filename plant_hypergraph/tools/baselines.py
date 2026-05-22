# created: 2026-05-17T02:20:00Z
# cycle: 4
# run_id: run-2026-05-17T004540Z
# agent: worker
# milestone: M6
"""Deterministic baselines for the synthetic plant-taxonomy benchmark."""

from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from tools import hierarchy_metrics as hm


MODEL_FAMILIES = [
    "label_frequency",
    "taxonomy_depth",
    "flat_lookup_or_centroid",
    "tree_dag",
    "ordinary_graph",
    "clique_expansion",
    "native_hypergraph",
]

DEFAULT_FAMILIES = {
    "taxonomic_parentage",
    "synonym_cluster",
    "trait_syndrome",
    "regional_checklist_context",
    "occurrence_provenance",
    "reticulate_or_hybrid_signal",
    "missing_rank_bridge",
}


def load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: str | Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def load_benchmark(benchmark_dir: str | Path) -> dict[str, list[dict[str, str]]]:
    base = Path(benchmark_dir)
    return {
        "taxa": load_csv(base / "taxa.csv"),
        "names": load_csv(base / "names.csv"),
        "hyperedges": load_csv(base / "hyperedges.csv"),
        "examples": load_csv(base / "examples.csv"),
        "splits": load_csv(base / "splits.csv"),
    }


def parse_features(example: dict[str, str]) -> dict[str, object]:
    return json.loads(example["observed_features_json"])


def species_rows(taxa_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in taxa_rows if row.get("rank") == "species"]


def taxon_by_id(taxa_rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["taxon_id"]: row for row in taxa_rows}


def name_to_accepted(names_rows: Iterable[dict[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in names_rows:
        result[row["name_id"]] = row["accepted_taxon_id"]
        result[row["name_string"]] = row["accepted_taxon_id"]
    return result


def accepted_name_by_taxon(taxa_rows: Iterable[dict[str, str]]) -> dict[str, str]:
    return {row["taxon_id"]: row["accepted_name"] for row in taxa_rows}


def filter_hyperedges(
    hyperedges: Iterable[dict[str, str]],
    remove_families: set[str] | None = None,
    randomize_trait: bool = False,
    seed: int = 20260517,
) -> list[dict[str, str]]:
    rows = [dict(row) for row in hyperedges if row.get("edge_family") not in (remove_families or set())]
    if not randomize_trait:
        return rows
    taxa = sorted({row["node_id"] for row in rows if row.get("node_type") == "taxon" and row["node_id"].startswith("taxon:S")})
    rng = random.Random(seed)
    shuffled = taxa[:]
    rng.shuffle(shuffled)
    mapping = dict(zip(taxa, shuffled))
    for row in rows:
        if row.get("edge_family") == "trait_syndrome" and row.get("node_id") in mapping:
            row["node_id"] = mapping[row["node_id"]]
    return rows


def randomized_name_rows(names_rows: Iterable[dict[str, str]], seed: int = 20260517) -> list[dict[str, str]]:
    rows = [dict(row) for row in names_rows]
    accepted = [row["accepted_taxon_id"] for row in rows]
    shuffled = accepted[:]
    random.Random(seed).shuffle(shuffled)
    for row, accepted_id in zip(rows, shuffled):
        row["accepted_taxon_id"] = accepted_id
        row["leakage_group_id"] = f"randomized:{accepted_id}"
    return rows


def allowed_rows_for_model(model: str, hyperedges: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    rows = list(hyperedges)
    if model == "tree_dag":
        return [row for row in rows if row["edge_family"] == "taxonomic_parentage"]
    if model == "ordinary_graph":
        return [row for row in rows if row["edge_family"] != "reticulate_or_hybrid_signal"]
    if model in {"clique_expansion", "native_hypergraph"}:
        return rows
    return []


def train_label_frequency(examples: Iterable[dict[str, str]]) -> str:
    rows = list(examples)
    counts = Counter(row["target_accepted_taxon_id"] for row in rows if row["split"] == "train")
    if not counts:
        counts = Counter(row["target_accepted_taxon_id"] for row in rows)
    return min(counts.items(), key=lambda item: (-item[1], item[0]))[0]


def accepted_name_lookup_model(train_rows: Iterable[dict[str, str]], names_rows: Iterable[dict[str, str]]) -> dict[str, str]:
    names = name_to_accepted(names_rows)
    result: dict[str, str] = {}
    for row in train_rows:
        features = parse_features(row)
        name_id = str(features.get("name_id", ""))
        if name_id in names:
            result[name_id] = names[name_id]
    return result


def family_candidate(
    example: dict[str, str],
    taxa_rows: Iterable[dict[str, str]],
    fallback: str,
) -> str:
    features = parse_features(example)
    region = str(features.get("region_id", ""))
    family_id = f"taxon:{region.split(':')[-1]}" if region.startswith("region:F") else ""
    candidates = sorted(row["taxon_id"] for row in species_rows(taxa_rows) if row.get("family_id") == family_id)
    return candidates[0] if candidates else fallback


def ancestor_taxa(taxon_id: str, taxa_rows: Iterable[dict[str, str]]) -> set[str]:
    parents = hm.parent_map(taxa_rows)
    return set(hm.ancestor_chain(taxon_id, parents))


def edge_groups(hyperedges: Iterable[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hyperedges:
        groups[row["edge_id"]].append(row)
    return dict(groups)


def pairwise_edges(hyperedges: Iterable[dict[str, str]], clique: bool = False) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    for edge_id, rows in edge_groups(hyperedges).items():
        members = [row for row in rows if row.get("node_type") != "source"]
        for i, left in enumerate(members):
            for right in members[i + 1 :]:
                if not clique and {left["node_type"], right["node_type"]} == {"trait"}:
                    continue
                pairs.append(
                    {
                        "edge_id": edge_id,
                        "edge_family": left["edge_family"],
                        "left": left["node_id"],
                        "right": right["node_id"],
                        "left_role": left["role"],
                        "right_role": right["role"],
                        "pair_type": f"{left['role']}--{right['role']}",
                        "weight": str(float(left.get("edge_weight", "1") or 1) * float(left.get("role_weight", "1") or 1) * float(right.get("role_weight", "1") or 1)),
                    }
                )
    return pairs


def pair_index(pair_rows: Iterable[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    index: dict[str, list[dict[str, str]]] = defaultdict(list)
    for pair in pair_rows:
        index[pair["left"]].append(pair)
        index[pair["right"]].append(pair)
    return dict(index)


def native_candidate_index(hyperedges: Iterable[dict[str, str]]) -> dict[str, list[list[dict[str, str]]]]:
    index: dict[str, list[list[dict[str, str]]]] = defaultdict(list)
    for rows in edge_groups(hyperedges).values():
        for row in rows:
            if row.get("node_type") == "taxon":
                index[row["node_id"]].append(rows)
    return dict(index)


def candidate_pool(taxa_rows: Iterable[dict[str, str]]) -> list[str]:
    return sorted(row["taxon_id"] for row in species_rows(taxa_rows))


def score_name(features: dict[str, object], candidate: str, names_rows: Iterable[dict[str, str]], visible_synonyms: bool) -> float:
    name_id = str(features.get("name_id", ""))
    for row in names_rows:
        if row["name_id"] == name_id and row["accepted_taxon_id"] == candidate:
            return 3.0 if visible_synonyms or row.get("name_status") == "accepted" else 0.0
    return 0.0


def score_region(features: dict[str, object], candidate: str, taxa: dict[str, dict[str, str]]) -> float:
    region = str(features.get("region_id", ""))
    family_id = taxa.get(candidate, {}).get("family_id", "")
    return 0.8 if region == f"region:{family_id.split(':')[-1]}" else -0.4 if region == "region:implausible" else 0.0


def score_tree(candidate: str, taxa: dict[str, dict[str, str]]) -> float:
    row = taxa.get(candidate, {})
    return 0.35 if row.get("genus_id") else 0.15


def score_graph(
    features: dict[str, object],
    candidate: str,
    indexed_pairs: dict[str, list[dict[str, str]]],
    ancestors: dict[str, set[str]],
) -> float:
    visible = {candidate, *ancestors.get(candidate, set()), str(features.get("region_id", ""))}
    visible.update(str(flag) for flag in features.get("trait_flags", []))
    score = 0.0
    seen: set[tuple[str, str, str]] = set()
    for node in visible:
        for pair in indexed_pairs.get(node, []):
            key = (pair["edge_id"], pair["left"], pair["right"])
            if key in seen:
                continue
            seen.add(key)
            other = pair["right"] if pair["left"] in visible else pair["left"]
            if other == candidate:
                score += 0.15 * float(pair["weight"])
            elif other in ancestors.get(candidate, set()):
                score += 0.05 * float(pair["weight"])
    return score


def score_native_hypergraph(
    features: dict[str, object],
    candidate: str,
    indexed_edges: dict[str, list[list[dict[str, str]]]],
    ancestors: dict[str, set[str]],
) -> float:
    candidate_context = {candidate, *ancestors.get(candidate, set()), str(features.get("region_id", ""))}
    trait_flags = set(str(flag) for flag in features.get("trait_flags", []))
    score = 0.0
    for rows in indexed_edges.get(candidate, []):
        family = rows[0]["edge_family"]
        by_node = {row["node_id"]: row for row in rows}
        if candidate not in by_node:
            continue
        edge_weight = float(rows[0].get("edge_weight", "1") or 1)
        roles = {row["role"] for row in rows}
        if family == "reticulate_or_hybrid_signal" and "reticulate" in trait_flags and by_node[candidate]["role"] == "reticulate_child":
            score += 2.5 * edge_weight
        elif family == "missing_rank_bridge" and by_node[candidate]["role"] == "lower_rank_taxon":
            score += 1.2 * edge_weight
        elif family == "regional_checklist_context" and candidate_context.intersection(by_node):
            score += 0.4 * edge_weight
        elif family == "occurrence_provenance" and str(features.get("region_id", "")) in by_node:
            score += 0.3 * edge_weight
        elif family == "trait_syndrome" and trait_flags and roles.intersection({"convergent_taxon", "taxon_with_trait"}):
            score += 0.25 * edge_weight
    return score


def predict_examples(
    model: str,
    examples: Iterable[dict[str, str]],
    taxa_rows: list[dict[str, str]],
    names_rows: list[dict[str, str]],
    hyperedges: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows = list(examples)
    train_rows = [row for row in rows if row["split"] == "train"]
    fallback = train_label_frequency(rows)
    lookup = accepted_name_lookup_model(train_rows, names_rows)
    taxa = taxon_by_id(taxa_rows)
    candidates = candidate_pool(taxa_rows)
    allowed_edges = allowed_rows_for_model(model, hyperedges)
    ordinary_pairs = pairwise_edges(allowed_edges, clique=False)
    clique_pairs = pairwise_edges(allowed_edges, clique=True)
    ordinary_pair_index = pair_index(ordinary_pairs)
    clique_pair_index = pair_index(clique_pairs)
    native_index = native_candidate_index(allowed_edges)
    ancestors = {candidate: ancestor_taxa(candidate, taxa_rows) for candidate in candidates}
    predictions: list[dict[str, str]] = []
    for row in rows:
        features = parse_features(row)
        if model == "label_frequency":
            pred = fallback
        elif model == "taxonomy_depth":
            pred = family_candidate(row, taxa_rows, fallback)
        elif model == "flat_lookup_or_centroid":
            pred = lookup.get(str(features.get("name_id", "")), family_candidate(row, taxa_rows, fallback))
        else:
            best = (float("-inf"), "")
            for candidate in candidates:
                score = 0.01 if candidate == fallback else 0.0
                if model in {"tree_dag", "ordinary_graph", "clique_expansion", "native_hypergraph"}:
                    score += score_name(features, candidate, names_rows, visible_synonyms=False)
                    score += score_region(features, candidate, taxa)
                    score += score_tree(candidate, taxa)
                if model == "ordinary_graph":
                    score += score_graph(features, candidate, ordinary_pair_index, ancestors)
                elif model == "clique_expansion":
                    score += score_graph(features, candidate, clique_pair_index, ancestors)
                elif model == "native_hypergraph":
                    score += score_native_hypergraph(features, candidate, native_index, ancestors)
                best = max(best, (score, candidate), key=lambda item: (item[0], -int(item[1].split("S")[-1]) if "S" in item[1] else 0))
            pred = best[1] or fallback
        predictions.append(
            {
                "example_id": row["example_id"],
                "split": row["split"],
                "case_type": row["case_type"],
                "model": model,
                "prediction": pred,
                "target": row["target_accepted_taxon_id"],
            }
        )
    return predictions


def coherence_rows(predictions: Iterable[dict[str, str]], taxa_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    taxa = taxon_by_id(taxa_rows)
    rows: list[dict[str, str]] = []
    for pred in predictions:
        taxon = taxa.get(pred["prediction"], {})
        rows.append({"family_id": taxon.get("family_id", ""), "genus_id": taxon.get("genus_id", ""), "species_id": pred["prediction"]})
    return rows


def evaluate_predictions(
    predictions: Iterable[dict[str, str]],
    taxa_rows: list[dict[str, str]],
    names_rows: list[dict[str, str]],
    hyperedges: list[dict[str, str]],
    model: str,
    ablation: str,
    split: str = "test",
    case_type: str = "all",
) -> dict[str, object]:
    rows = [row for row in predictions if row["split"] == split and (case_type == "all" or row["case_type"] == case_type)]
    preds = [row["prediction"] for row in rows]
    targets = [row["target"] for row in rows]
    return {
        "ablation": ablation,
        "model": model,
        "split": split,
        "case_type": case_type,
        "n": len(rows),
        "flat_exact_match": f"{hm.flat_exact_match(preds, targets):.6f}",
        "synonym_normalized_exact_match": f"{hm.synonym_normalized_exact_match(preds, targets, names_rows):.6f}",
        "mean_hierarchy_distance": f"{hm.mean_hierarchical_distance_error(preds, targets, taxa_rows, names_rows):.6f}",
        "hierarchy_coherence_violation_rate": f"{hm.hierarchy_coherence_violation_rate(coherence_rows(rows, taxa_rows), taxa_rows):.6f}",
        "mean_reticulate_near_miss": f"{hm.mean_reticulate_near_miss_score(preds, targets, taxa_rows, hyperedges, names_rows):.6f}",
    }


def run_model_suite(
    benchmark: dict[str, list[dict[str, str]]],
    ablation: str = "none",
    remove_families: set[str] | None = None,
    randomize_trait: bool = False,
    randomize_names: bool = False,
    seed: int = 20260517,
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    taxa_rows = benchmark["taxa"]
    names_rows = randomized_name_rows(benchmark["names"], seed) if randomize_names else benchmark["names"]
    hyperedges = filter_hyperedges(benchmark["hyperedges"], remove_families, randomize_trait, seed)
    all_predictions: list[dict[str, str]] = []
    metrics: list[dict[str, object]] = []
    for model in MODEL_FAMILIES:
        prediction_model = "clique_expansion" if ablation == "collapse_to_clique_expansion" and model == "native_hypergraph" else model
        predictions = predict_examples(prediction_model, benchmark["examples"], taxa_rows, names_rows, hyperedges)
        if prediction_model != model:
            predictions = [{**row, "model": model} for row in predictions]
        all_predictions.extend({**row, "ablation": ablation} for row in predictions)
        metrics.append(evaluate_predictions(predictions, taxa_rows, names_rows, hyperedges, model, ablation))
    return all_predictions, metrics


def clique_false_similarity_rows(hyperedges: Iterable[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for edge_id, members in edge_groups(hyperedges).items():
        if members[0]["edge_family"] not in {"trait_syndrome", "reticulate_or_hybrid_signal", "regional_checklist_context"}:
            continue
        taxon_members = [row for row in members if row.get("node_type") == "taxon"]
        pair_count = len(taxon_members) * (len(taxon_members) - 1) // 2
        if pair_count:
            rows.append(
                {
                    "edge_id": edge_id,
                    "edge_family": members[0]["edge_family"],
                    "taxon_members": len(taxon_members),
                    "introduced_taxon_pairs": pair_count,
                    "provenance": members[0].get("provenance", ""),
                }
            )
    return rows
