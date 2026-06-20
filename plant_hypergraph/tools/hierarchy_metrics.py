# created: 2026-05-17T01:15:00Z
# cycle: 2
# run_id: run-2026-05-17T004540Z
# agent: worker
# milestone: M4
"""Small hierarchy-aware metrics for the synthetic plant benchmark.

The functions are intentionally light and operate on CSV-loaded row dicts so
they can be reused before the project commits to pandas/networkx.
"""

from __future__ import annotations

import csv
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable


def load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def name_maps(names_rows: Iterable[dict[str, str]]) -> tuple[dict[str, str], dict[str, str]]:
    by_id: dict[str, str] = {}
    by_string: dict[str, str] = {}
    for row in names_rows:
        accepted = row["accepted_taxon_id"]
        by_id[row["name_id"]] = accepted
        by_string[row["name_string"]] = accepted
    return by_id, by_string


def normalize_label(label: str, names_rows: Iterable[dict[str, str]] | None = None) -> str:
    """Map a taxon id, name id, or name string to an accepted taxon id."""
    if label.startswith("taxon:") or names_rows is None:
        return label
    by_id, by_string = name_maps(names_rows)
    return by_id.get(label, by_string.get(label, label))


def flat_exact_match(predictions: Iterable[str], targets: Iterable[str]) -> float:
    pairs = list(zip(predictions, targets))
    if not pairs:
        return 0.0
    return sum(pred == target for pred, target in pairs) / len(pairs)


def synonym_normalized_exact_match(
    predictions: Iterable[str],
    targets: Iterable[str],
    names_rows: Iterable[dict[str, str]],
) -> float:
    names = list(names_rows)
    pairs = [(normalize_label(pred, names), normalize_label(target, names)) for pred, target in zip(predictions, targets)]
    if not pairs:
        return 0.0
    return sum(pred == target for pred, target in pairs) / len(pairs)


def parent_map(taxa_rows: Iterable[dict[str, str]]) -> dict[str, str]:
    return {row["taxon_id"]: row["parent_taxon_id"] for row in taxa_rows if row.get("parent_taxon_id")}


def ancestor_chain(taxon_id: str, parents: dict[str, str]) -> list[str]:
    chain = [taxon_id]
    seen = {taxon_id}
    cur = taxon_id
    while cur in parents and parents[cur] and parents[cur] not in seen:
        cur = parents[cur]
        chain.append(cur)
        seen.add(cur)
    return chain


def hierarchy_distance(
    prediction: str,
    target: str,
    taxa_rows: Iterable[dict[str, str]],
    names_rows: Iterable[dict[str, str]] | None = None,
) -> int:
    """Return shortest ancestor-path distance after optional synonym normalization.

    Exact accepted-taxon matches score 0. Wrong species in the same genus is 2
    in a normal family/genus/species tree; wrong genus in the same family is 4.
    Missing-rank species bridge directly to family because the benchmark parent
    map records the observed hierarchy, not an imputed genus.
    """
    taxa = list(taxa_rows)
    pred = normalize_label(prediction, names_rows)
    tgt = normalize_label(target, names_rows)
    if pred == tgt:
        return 0
    parents = parent_map(taxa)
    pred_chain = ancestor_chain(pred, parents)
    tgt_chain = ancestor_chain(tgt, parents)
    pred_pos = {node: idx for idx, node in enumerate(pred_chain)}
    distances = [pred_pos[node] + j for j, node in enumerate(tgt_chain) if node in pred_pos]
    return min(distances) if distances else len(pred_chain) + len(tgt_chain)


def mean_hierarchical_distance_error(
    predictions: Iterable[str],
    targets: Iterable[str],
    taxa_rows: Iterable[dict[str, str]],
    names_rows: Iterable[dict[str, str]] | None = None,
) -> float:
    pairs = list(zip(predictions, targets))
    if not pairs:
        return 0.0
    taxa = list(taxa_rows)
    names = list(names_rows) if names_rows is not None else None
    return sum(hierarchy_distance(pred, tgt, taxa, names) for pred, tgt in pairs) / len(pairs)


def taxon_lookup(taxa_rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["taxon_id"]: row for row in taxa_rows}


def hierarchy_coherence_violation_rate(
    predictions: Iterable[dict[str, str]],
    taxa_rows: Iterable[dict[str, str]],
    allow_missing_rank_bridge: bool = True,
) -> float:
    """Count multi-rank predictions whose family/genus/species cannot coexist."""
    rows = list(predictions)
    if not rows:
        return 0.0
    taxa = taxon_lookup(taxa_rows)
    violations = 0
    for pred in rows:
        family = pred.get("family_id", "")
        genus = pred.get("genus_id", "")
        species = pred.get("species_id", "")
        bad = False
        if genus:
            bad = bad or genus not in taxa or taxa[genus].get("family_id") != family
        if species:
            if species not in taxa:
                bad = True
            else:
                sp = taxa[species]
                expected_family = sp.get("family_id", "")
                expected_genus = sp.get("genus_id", "")
                if family and expected_family != family:
                    bad = True
                if genus and expected_genus != genus:
                    bad = True
                if not genus and expected_genus and not allow_missing_rank_bridge:
                    bad = True
                if genus == "" and expected_genus == "" and allow_missing_rank_bridge:
                    bad = bad or False
        violations += int(bad)
    return violations / len(rows)


def reticulate_parent_map(hyperedge_rows: Iterable[dict[str, str]]) -> dict[str, set[str]]:
    edge_roles: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in hyperedge_rows:
        if row.get("edge_family") != "reticulate_or_hybrid_signal":
            continue
        if float(row.get("edge_weight", "1") or 0) <= 0:
            continue
        edge_roles[row["edge_id"]][row["role"]].add(row["node_id"])
    result: dict[str, set[str]] = defaultdict(set)
    for roles in edge_roles.values():
        for child in roles.get("reticulate_child", set()):
            result[child].update(roles.get("source_lineage", set()))
    return dict(result)


def descendants_by_ancestor(taxa_rows: Iterable[dict[str, str]]) -> dict[str, set[str]]:
    parents = parent_map(taxa_rows)
    children: dict[str, set[str]] = defaultdict(set)
    for child, parent in parents.items():
        children[parent].add(child)
    desc: dict[str, set[str]] = defaultdict(set)
    for ancestor in set(children):
        queue: deque[str] = deque(children[ancestor])
        while queue:
            node = queue.popleft()
            desc[ancestor].add(node)
            queue.extend(children.get(node, set()))
    return dict(desc)


def reticulate_near_miss_score(
    prediction: str,
    target: str,
    taxa_rows: Iterable[dict[str, str]],
    hyperedge_rows: Iterable[dict[str, str]],
    names_rows: Iterable[dict[str, str]] | None = None,
) -> float:
    """Score exact reticulate target matches as 1 and source-lineage near misses as 0.5."""
    taxa = list(taxa_rows)
    pred = normalize_label(prediction, names_rows)
    tgt = normalize_label(target, names_rows)
    if pred == tgt:
        return 1.0
    parents = reticulate_parent_map(hyperedge_rows)
    source_lineages = parents.get(tgt, set())
    if pred in source_lineages:
        return 0.5
    descendants = descendants_by_ancestor(taxa)
    if any(pred in descendants.get(source, set()) for source in source_lineages):
        return 0.5
    return 0.0


def mean_reticulate_near_miss_score(
    predictions: Iterable[str],
    targets: Iterable[str],
    taxa_rows: Iterable[dict[str, str]],
    hyperedge_rows: Iterable[dict[str, str]],
    names_rows: Iterable[dict[str, str]] | None = None,
) -> float:
    pairs = list(zip(predictions, targets))
    if not pairs:
        return 0.0
    taxa = list(taxa_rows)
    edges = list(hyperedge_rows)
    names = list(names_rows) if names_rows is not None else None
    return sum(reticulate_near_miss_score(pred, tgt, taxa, edges, names) for pred, tgt in pairs) / len(pairs)
