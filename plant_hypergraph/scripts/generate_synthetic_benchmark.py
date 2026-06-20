# created: 2026-05-17T01:15:00Z
# cycle: 2
# run_id: run-2026-05-17T004540Z
# agent: worker
# milestone: M3
"""Generate a deterministic synthetic plant-taxonomy hypergraph benchmark."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


REQUIRED_EDGE_FAMILIES = [
    "taxonomic_parentage",
    "synonym_cluster",
    "trait_syndrome",
    "regional_checklist_context",
    "occurrence_provenance",
    "reticulate_or_hybrid_signal",
    "missing_rank_bridge",
]


def stable_fraction(seed: int, *parts: object) -> float:
    text = "|".join([str(seed), *[str(p) for p in parts]])
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def add_incidence(
    rows: list[dict[str, object]],
    edge_id: str,
    family: str,
    members: list[tuple[str, str, str, float]],
    edge_weight: float = 1.0,
    provenance: str = "synthetic_generator_v0.1",
) -> None:
    for node_id, node_type, role, role_weight in members:
        rows.append(
            {
                "edge_id": edge_id,
                "edge_family": family,
                "node_id": node_id,
                "node_type": node_type,
                "role": role,
                "role_weight": f"{role_weight:.3f}",
                "edge_weight": f"{edge_weight:.3f}",
                "provenance": provenance,
                "is_synthetic": "true",
            }
        )


def split_for_group(seed: int, group_id: str) -> str:
    x = stable_fraction(seed, "split", group_id)
    if x < 0.60:
        return "train"
    if x < 0.80:
        return "validation"
    return "test"


def build_taxa(args: argparse.Namespace) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    taxa: list[dict[str, object]] = []
    species_rows: list[dict[str, object]] = []
    for f_idx in range(args.n_families):
        family_id = f"taxon:F{f_idx+1:02d}"
        family_name = f"Synthaceae {f_idx+1}"
        taxa.append(
            {
                "taxon_id": family_id,
                "accepted_name": family_name,
                "rank": "family",
                "parent_taxon_id": "",
                "family_id": family_id,
                "genus_id": "",
                "is_synthetic": "true",
                "source_layer": "taxonomy",
            }
        )
        for g_local in range(args.genera_per_family):
            g_global = f_idx * args.genera_per_family + g_local + 1
            genus_id = f"taxon:G{g_global:03d}"
            genus_name = f"Genus{g_global:03d}"
            taxa.append(
                {
                    "taxon_id": genus_id,
                    "accepted_name": genus_name,
                    "rank": "genus",
                    "parent_taxon_id": family_id,
                    "family_id": family_id,
                    "genus_id": genus_id,
                    "is_synthetic": "true",
                    "source_layer": "taxonomy",
                }
            )
            for s_local in range(args.species_per_genus):
                s_global = (g_global - 1) * args.species_per_genus + s_local + 1
                species_id = f"taxon:S{s_global:04d}"
                missing_genus = stable_fraction(args.seed, "missing", species_id) < args.missing_rank_rate
                accepted_name = f"{genus_name} species{s_local+1:02d}"
                row = {
                    "taxon_id": species_id,
                    "accepted_name": accepted_name,
                    "rank": "species",
                    "parent_taxon_id": family_id if missing_genus else genus_id,
                    "family_id": family_id,
                    "genus_id": "" if missing_genus else genus_id,
                    "is_synthetic": "true",
                    "source_layer": "taxonomy",
                }
                taxa.append(row)
                species_rows.append(row)
    return taxa, species_rows


def build_names(args: argparse.Namespace, taxa: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for taxon in taxa:
        taxon_id = str(taxon["taxon_id"])
        group_id = f"cluster:{taxon_id}"
        rows.append(
            {
                "name_id": f"name:{taxon_id}:accepted",
                "name_string": taxon["accepted_name"],
                "accepted_taxon_id": taxon_id,
                "name_status": "accepted",
                "source_layer": "nomenclature",
                "leakage_group_id": group_id,
            }
        )
        if taxon["rank"] == "species" and stable_fraction(args.seed, "syn", taxon_id) < args.synonym_rate:
            base = str(taxon["accepted_name"])
            rows.append(
                {
                    "name_id": f"name:{taxon_id}:synonym",
                    "name_string": base.replace("species", "synonym"),
                    "accepted_taxon_id": taxon_id,
                    "name_status": "synonym",
                    "source_layer": "nomenclature",
                    "leakage_group_id": group_id,
                }
            )
            rows.append(
                {
                    "name_id": f"name:{taxon_id}:renamed",
                    "name_string": f"Oldname {taxon_id.split(':')[-1]}",
                    "accepted_taxon_id": taxon_id,
                    "name_status": "renamed_label",
                    "source_layer": "dataset_label_hierarchy",
                    "leakage_group_id": group_id,
                }
            )
        if taxon["rank"] == "species" and stable_fraction(args.seed, "noisy-name", taxon_id) < max(args.occurrence_noise_rate, 0.05):
            rows.append(
                {
                    "name_id": f"name:{taxon_id}:verbatim_noise",
                    "name_string": f"{taxon['accepted_name']} cf.",
                    "accepted_taxon_id": taxon_id,
                    "name_status": "noisy_verbatim",
                    "source_layer": "occurrence_evidence",
                    "leakage_group_id": group_id,
                }
            )
    return rows


def build_hyperedges(
    args: argparse.Namespace,
    taxa: list[dict[str, object]],
    species_rows: list[dict[str, object]],
    names: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, list[str]], set[str]]:
    rows: list[dict[str, object]] = []
    reticulate_parents: dict[str, list[str]] = {}
    convergence_species: set[str] = set()
    taxa_by_id = {str(t["taxon_id"]): t for t in taxa}

    for taxon in taxa:
        child = str(taxon["taxon_id"])
        parent = str(taxon["parent_taxon_id"])
        if parent:
            add_incidence(
                rows,
                f"edge:tax_parent:{child}",
                "taxonomic_parentage",
                [
                    (child, "taxon", "child_taxon", 1.0),
                    (parent, "taxon", "parent_taxon", 1.0),
                    (f"rank:{taxon['rank']}", "rank", "child_rank", 1.0),
                    ("source:synthetic_taxonomy", "source", "source", 1.0),
                ],
                edge_weight=1.0,
                provenance="synthetic_taxonomy",
            )
        if taxon["rank"] == "species" and not taxon["genus_id"]:
            add_incidence(
                rows,
                f"edge:missing_bridge:{child}",
                "missing_rank_bridge",
                [
                    (child, "taxon", "lower_rank_taxon", 1.0),
                    (str(taxon["family_id"]), "taxon", "higher_rank_ancestor", 1.0),
                    ("rank:genus", "rank", "missing_rank", 1.0),
                    ("source:synthetic_taxonomy", "source", "source", 1.0),
                ],
                edge_weight=0.9,
                provenance="synthetic_missing_rank",
            )

    names_by_taxon: dict[str, list[dict[str, object]]] = defaultdict(list)
    for name in names:
        names_by_taxon[str(name["accepted_taxon_id"])].append(name)
    for taxon_id, group_names in sorted(names_by_taxon.items()):
        members = [(taxon_id, "taxon", "accepted_taxon", 1.0), ("source:synthetic_names", "source", "source", 1.0)]
        for name in group_names:
            role = "accepted_name" if name["name_status"] == "accepted" else "synonym_or_label"
            members.append((str(name["name_id"]), "name_string", role, 1.0))
        add_incidence(rows, f"edge:synonym_cluster:{taxon_id}", "synonym_cluster", members, 1.0, "synthetic_nomenclature")

    species_by_genus: dict[str, list[dict[str, object]]] = defaultdict(list)
    species_by_family: dict[str, list[dict[str, object]]] = defaultdict(list)
    for sp in species_rows:
        species_by_family[str(sp["family_id"])].append(sp)
        if sp["genus_id"]:
            species_by_genus[str(sp["genus_id"])].append(sp)

    for genus_id, genus_species in sorted(species_by_genus.items()):
        members = [(f"trait:local:{genus_id}", "trait", "local_trait_state", 1.0), ("source:synthetic_traits", "source", "source", 1.0)]
        members.extend((str(sp["taxon_id"]), "taxon", "taxon_with_trait", 1.0) for sp in genus_species[: max(2, len(genus_species) // 2)])
        add_incidence(rows, f"edge:trait_local:{genus_id}", "trait_syndrome", members, 0.5, "synthetic_local_trait")

    candidate_species = list(species_rows)
    random.Random(args.seed).shuffle(candidate_species)
    n_convergent = max(0, int(round(len(species_rows) * args.trait_convergence_rate)))
    for idx in range(n_convergent):
        a = candidate_species[idx % len(candidate_species)]
        distant = [sp for sp in candidate_species if sp["family_id"] != a["family_id"]]
        if not distant:
            continue
        b = distant[idx % len(distant)]
        convergence_species.update([str(a["taxon_id"]), str(b["taxon_id"])])
        add_incidence(
            rows,
            f"edge:trait_convergence:{idx+1:03d}",
            "trait_syndrome",
            [
                (str(a["taxon_id"]), "taxon", "convergent_taxon", 1.0),
                (str(b["taxon_id"]), "taxon", "convergent_taxon", 1.0),
                (f"trait:convergent:{idx+1:03d}", "trait", "shared_convergent_trait", 1.0),
                ("source:synthetic_traits", "source", "source", 1.0),
            ],
            edge_weight=0.4,
            provenance="synthetic_trait_convergence_trap",
        )

    for family_id, family_species in sorted(species_by_family.items()):
        region = f"region:{family_id.split(':')[-1]}"
        members = [(family_id, "taxon", "regional_family_context", 1.0), (region, "region", "checklist_region", 1.0), ("source:synthetic_checklist", "source", "source", 1.0)]
        for sp in family_species[: min(4, len(family_species))]:
            members.append((str(sp["taxon_id"]), "taxon", "regionally_listed_taxon", 1.0))
        add_incidence(rows, f"edge:regional:{family_id}", "regional_checklist_context", members, 0.6, "synthetic_regional_checklist")

    for idx, sp in enumerate(species_rows, 1):
        expected_region = f"region:{str(sp['family_id']).split(':')[-1]}"
        noisy = stable_fraction(args.seed, "occ-noise", sp["taxon_id"]) < args.occurrence_noise_rate
        region = "region:implausible" if noisy else expected_region
        add_incidence(
            rows,
            f"edge:occurrence:{idx:04d}",
            "occurrence_provenance",
            [
                (f"occ:{idx:04d}", "occurrence_record", "occurrence_record", 1.0),
                (str(sp["taxon_id"]), "taxon", "recorded_taxon", 1.0),
                (region, "region", "recorded_region", 1.0),
                (f"observation:{idx:04d}", "specimen_or_observation", "observation", 1.0),
                ("source:synthetic_occurrence", "source", "source", 1.0),
            ],
            edge_weight=0.5 if not noisy else 0.2,
            provenance="synthetic_occurrence_noise" if noisy else "synthetic_occurrence",
        )

    n_reticulate = max(0, int(round(len(species_rows) * args.reticulation_rate)))
    for idx, child in enumerate(candidate_species[:n_reticulate], 1):
        parent_a = str(child["genus_id"] or child["family_id"])
        other_families = [sp for sp in species_rows if sp["family_id"] != child["family_id"] and sp["genus_id"]]
        if not other_families:
            continue
        parent_b = str(other_families[idx % len(other_families)]["genus_id"])
        child_id = str(child["taxon_id"])
        reticulate_parents[child_id] = [parent_a, parent_b]
        add_incidence(
            rows,
            f"edge:reticulate:{idx:03d}",
            "reticulate_or_hybrid_signal",
            [
                (child_id, "taxon", "reticulate_child", 1.0),
                (parent_a, "taxon", "source_lineage", 1.0),
                (parent_b, "taxon", "source_lineage", 1.0),
                (f"phylo:synthetic_network:{idx:03d}", "phylogeny_node", "synthetic_network_evidence", 1.0),
                ("source:synthetic_reticulation", "source", "source", 1.0),
            ],
            edge_weight=1.0,
            provenance="synthetic_reticulation_oracle",
        )

    # Deterministic row order makes CSV output stable.
    rows.sort(key=lambda r: (str(r["edge_id"]), str(r["node_id"]), str(r["role"])))
    return rows, reticulate_parents, convergence_species


def build_examples(
    args: argparse.Namespace,
    species_rows: list[dict[str, object]],
    names: list[dict[str, object]],
    reticulate_parents: dict[str, list[str]],
    convergence_species: set[str],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    names_by_taxon: dict[str, list[dict[str, object]]] = defaultdict(list)
    for name in names:
        names_by_taxon[str(name["accepted_taxon_id"])].append(name)
    rows: list[dict[str, object]] = []
    split_rows: list[dict[str, object]] = []
    example_idx = 1
    seen_groups: set[str] = set()
    for sp in species_rows:
        taxon_id = str(sp["taxon_id"])
        group_id = f"cluster:{taxon_id}"
        split = split_for_group(args.seed, group_id)
        if group_id not in seen_groups:
            split_rows.append({"leakage_group_id": group_id, "accepted_taxon_id": taxon_id, "split": split})
            seen_groups.add(group_id)
        case_types = ["strict_hierarchy"]
        if not sp["genus_id"]:
            case_types.append("missing_rank")
        if taxon_id in reticulate_parents:
            case_types.append("reticulate")
        if taxon_id in convergence_species:
            case_types.append("trait_convergence")
        noisy_occ = stable_fraction(args.seed, "occ-noise", taxon_id) < args.occurrence_noise_rate
        if noisy_occ:
            case_types.append("noisy_occurrence")
        name_candidates = names_by_taxon[taxon_id]
        selected_names = [n for n in name_candidates if n["name_status"] in {"accepted", "synonym", "renamed_label", "noisy_verbatim"}]
        for name in selected_names[:3]:
            if name["name_status"] in {"synonym", "renamed_label"}:
                case = "synonym_or_rename"
            elif "reticulate" in case_types:
                case = "reticulate"
            elif "missing_rank" in case_types:
                case = "missing_rank"
            elif "trait_convergence" in case_types:
                case = "trait_convergence"
            elif "noisy_occurrence" in case_types:
                case = "noisy_occurrence"
            else:
                case = "strict_hierarchy"
            if name["name_status"] == "accepted" and case == "strict_hierarchy" and stable_fraction(args.seed, "downsample", taxon_id) > 0.55:
                continue
            observed = {
                "name_id": name["name_id"],
                "region_id": "region:implausible" if noisy_occ else f"region:{str(sp['family_id']).split(':')[-1]}",
                "trait_flags": sorted([ct for ct in case_types if ct in {"trait_convergence", "reticulate"}]),
            }
            rows.append(
                {
                    "example_id": f"ex:{example_idx:04d}",
                    "observed_features_json": json.dumps(observed, sort_keys=True, separators=(",", ":")),
                    "noisy_label": name["name_string"],
                    "target_accepted_taxon_id": taxon_id,
                    "target_rank_path": f"{sp['family_id']}|{sp['genus_id']}|{taxon_id}",
                    "case_type": case,
                    "split": split,
                    "leakage_group_id": group_id,
                }
            )
            example_idx += 1
    rows.sort(key=lambda r: str(r["example_id"]))
    split_rows.sort(key=lambda r: str(r["leakage_group_id"]))
    return rows, split_rows


def plot_composition(examples_path: Path, out_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    counts: Counter[tuple[str, str]] = Counter()
    with examples_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            counts[(row["case_type"], row["split"])] += 1
    case_types = sorted({case for case, _ in counts})
    splits = ["train", "validation", "test"]
    colors = {"train": "#3b7a57", "validation": "#4f6fad", "test": "#b45f4d"}
    fig, ax = plt.subplots(figsize=(9, 4.8))
    left = [0] * len(case_types)
    y_positions = list(range(len(case_types)))
    for split in splits:
        values = [counts[(case, split)] for case in case_types]
        ax.barh(y_positions, values, left=left, label=split, color=colors[split])
        left = [l + v for l, v in zip(left, values)]
    ax.set_yticks(y_positions)
    ax.set_yticklabels(case_types)
    ax.set_xlabel("labeled examples")
    ax.set_title("Synthetic benchmark composition by case type and split")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def generate(args: argparse.Namespace) -> dict[str, str]:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    taxa, species_rows = build_taxa(args)
    names = build_names(args, taxa)
    hyperedges, reticulate_parents, convergence_species = build_hyperedges(args, taxa, species_rows, names)
    examples, splits = build_examples(args, species_rows, names, reticulate_parents, convergence_species)

    paths = {
        "taxa": out_dir / "taxa.csv",
        "names": out_dir / "names.csv",
        "hyperedges": out_dir / "hyperedges.csv",
        "examples": out_dir / "examples.csv",
        "splits": out_dir / "splits.csv",
        "composition": out_dir / "composition.png",
        "metadata": out_dir / "metadata.json",
    }
    write_csv(paths["taxa"], ["taxon_id", "accepted_name", "rank", "parent_taxon_id", "family_id", "genus_id", "is_synthetic", "source_layer"], taxa)
    write_csv(paths["names"], ["name_id", "name_string", "accepted_taxon_id", "name_status", "source_layer", "leakage_group_id"], names)
    write_csv(paths["hyperedges"], ["edge_id", "edge_family", "node_id", "node_type", "role", "role_weight", "edge_weight", "provenance", "is_synthetic"], hyperedges)
    write_csv(paths["examples"], ["example_id", "observed_features_json", "noisy_label", "target_accepted_taxon_id", "target_rank_path", "case_type", "split", "leakage_group_id"], examples)
    write_csv(paths["splits"], ["leakage_group_id", "accepted_taxon_id", "split"], splits)
    plot_composition(paths["examples"], paths["composition"])

    hashes = {path.name: sha256_file(path) for key, path in paths.items() if key != "metadata"}
    metadata = {
        "schema_version": "synthetic_benchmark_v0.1",
        "created": "2026-05-17T01:15:00Z",
        "generator": "scripts/generate_synthetic_benchmark.py",
        "seed": args.seed,
        "parameters": {
            "n_families": args.n_families,
            "genera_per_family": args.genera_per_family,
            "species_per_genus": args.species_per_genus,
            "synonym_rate": args.synonym_rate,
            "missing_rank_rate": args.missing_rank_rate,
            "reticulation_rate": args.reticulation_rate,
            "trait_convergence_rate": args.trait_convergence_rate,
            "occurrence_noise_rate": args.occurrence_noise_rate,
        },
        "counts": {
            "taxa": len(taxa),
            "species": len(species_rows),
            "names": len(names),
            "hyperedge_incidence_rows": len(hyperedges),
            "examples": len(examples),
            "reticulate_cases": len(reticulate_parents),
            "trait_convergence_taxa": len(convergence_species),
        },
        "required_edge_families": REQUIRED_EDGE_FAMILIES,
        "synthetic_status_disclaimer": "All traits, geography, occurrence noise, missing ranks, and reticulate/hybrid-like signals are synthetic benchmark mechanisms and do not imply biological novelty.",
        "file_hashes_sha256": hashes,
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=20260517)
    p.add_argument("--out-dir", default="data/synthetic_benchmark/v0.1/")
    p.add_argument("--n-families", type=int, default=4)
    p.add_argument("--genera-per-family", type=int, default=3)
    p.add_argument("--species-per-genus", type=int, default=5)
    p.add_argument("--synonym-rate", type=float, default=0.45)
    p.add_argument("--missing-rank-rate", type=float, default=0.18)
    p.add_argument("--reticulation-rate", type=float, default=0.12)
    p.add_argument("--trait-convergence-rate", type=float, default=0.16)
    p.add_argument("--occurrence-noise-rate", type=float, default=0.12)
    return p


def main() -> None:
    args = parser().parse_args()
    outputs = generate(args)
    print(json.dumps(outputs, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
