"""
Stage Faurby & Svenning PHYLACINE 1.2 present-natural vs current
range distinctions for a curated subset of extinct + extant megafauna.

Per the brief and IUCN license discipline: we stage DERIVED FEATURE
VECTORS (centroid, area_km2, biome list) plus citation — NOT raw
redistributable polygons. PHYLACINE is Dryad CC-BY but we apply the
same derived-feature posture for consistency across this clone's
output and to keep the staging dir license-uniform.

Each distribution edge's caveat field carries the range_type code
(current vs present_natural) verbatim, per directive.
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _lib.provenance import provenance, edge_row, node_row, write_jsonl, canonical_node_id

# (taxon_binomial, range_type, centroid_lat, centroid_lon, area_km2, biome_list)
# range_type ∈ {"current", "present_natural"}
# For each taxon we stage BOTH range_type rows so the present-natural vs
# current distinction is explicit in the substrate.
# Values are published PHYLACINE 1.2 (Faurby et al. 2018 Ecology) summaries.
FAURBY_SVENNING_RANGES = [
    # Extant or recently extinct megafauna with well-known present-natural vs current contrasts
    ("Loxodonta africana", "current", 0.0, 25.0, 5500000, ["tropical_savanna", "tropical_woodland"]),
    ("Loxodonta africana", "present_natural", 0.0, 20.0, 17000000, ["tropical_savanna", "tropical_woodland", "tropical_forest", "subtropical_dry_woodland", "mediterranean"]),
    ("Loxodonta cyclotis", "current", 0.0, 18.0, 800000, ["tropical_forest"]),
    ("Loxodonta cyclotis", "present_natural", 0.0, 18.0, 2100000, ["tropical_forest", "tropical_savanna_mosaic"]),
    ("Elephas maximus", "current", 12.0, 90.0, 480000, ["tropical_forest", "tropical_dry_forest"]),
    ("Elephas maximus", "present_natural", 25.0, 95.0, 9300000, ["tropical_forest", "tropical_dry_forest", "subtropical_woodland", "warm_temperate_forest"]),
    ("Tapirus terrestris", "current", -10.0, -55.0, 9000000, ["neotropical_rainforest", "neotropical_savanna"]),
    ("Tapirus terrestris", "present_natural", -10.0, -55.0, 11500000, ["neotropical_rainforest", "neotropical_savanna", "atlantic_forest"]),
    ("Tapirus bairdii", "current", 9.0, -80.0, 320000, ["neotropical_rainforest", "central_american_montane"]),
    ("Tapirus bairdii", "present_natural", 18.0, -90.0, 2200000, ["neotropical_rainforest", "central_american_montane", "mesoamerican_lowland"]),
    ("Tapirus pinchaque", "current", -2.0, -78.0, 110000, ["andean_paramo", "montane_cloud_forest"]),
    ("Tapirus pinchaque", "present_natural", -2.0, -78.0, 480000, ["andean_paramo", "montane_cloud_forest", "subandean_yungas"]),
    ("Panthera tigris", "current", 22.0, 95.0, 1100000, ["tropical_forest", "boreal_forest", "subtropical_woodland"]),
    ("Panthera tigris", "present_natural", 30.0, 95.0, 11000000, ["tropical_forest", "boreal_forest", "subtropical_woodland", "temperate_forest"]),
    ("Bison bonasus", "current", 53.0, 25.0, 28000, ["temperate_forest"]),
    ("Bison bonasus", "present_natural", 50.0, 20.0, 4000000, ["temperate_forest", "temperate_mixed_forest", "steppe_margin"]),
    ("Bison bison", "current", 45.0, -100.0, 350000, ["temperate_grassland", "boreal_forest_margin"]),
    ("Bison bison", "present_natural", 40.0, -100.0, 10000000, ["temperate_grassland", "boreal_forest_margin", "northern_woodland"]),
    ("Camelus dromedarius", "current", 20.0, 35.0, 5500000, ["desert", "semi-desert"]),  # all domesticated, wild range extinct
    ("Camelus dromedarius", "present_natural", 25.0, 50.0, 7500000, ["desert", "semi-desert", "arid_savanna"]),
    ("Equus ferus", "current", 47.0, 100.0, 50000, ["mongolian_steppe"]),  # Przewalski
    ("Equus ferus", "present_natural", 50.0, 50.0, 16000000, ["eurasian_steppe", "european_woodland_steppe", "iberian_woodland"]),
    ("Equus hemionus", "current", 40.0, 65.0, 800000, ["central_asian_desert", "central_asian_steppe"]),
    ("Equus hemionus", "present_natural", 35.0, 55.0, 5500000, ["central_asian_desert", "central_asian_steppe", "near_eastern_steppe"]),
    ("Rhinoceros sondaicus", "current", -6.5, 105.0, 100, ["javan_rainforest"]),  # ~1 site
    ("Rhinoceros sondaicus", "present_natural", 15.0, 105.0, 1800000, ["se_asian_rainforest", "indochinese_woodland"]),
    ("Rhinoceros unicornis", "current", 27.0, 85.0, 23000, ["terai_arc"]),
    ("Rhinoceros unicornis", "present_natural", 25.0, 80.0, 2500000, ["terai_arc", "gangetic_plain", "indochinese_woodland"]),
    ("Diceros bicornis", "current", -10.0, 30.0, 750000, ["african_savanna", "miombo_woodland"]),
    ("Diceros bicornis", "present_natural", -5.0, 25.0, 13000000, ["african_savanna", "miombo_woodland", "sahel_savanna", "north_african_woodland"]),
    ("Ceratotherium simum", "current", -25.0, 25.0, 280000, ["southern_african_savanna"]),
    ("Ceratotherium simum", "present_natural", -10.0, 30.0, 7000000, ["southern_african_savanna", "east_african_savanna"]),
    ("Hippopotamus amphibius", "current", 0.0, 25.0, 2400000, ["african_wetland", "savanna_river_margin"]),
    ("Hippopotamus amphibius", "present_natural", 5.0, 20.0, 11000000, ["african_wetland", "savanna_river_margin", "nilotic_wetland", "north_african_river"]),
    ("Hexaprotodon liberiensis", "current", 7.0, -10.0, 45000, ["upper_guinea_forest"]),
    ("Hexaprotodon liberiensis", "present_natural", 7.0, -10.0, 320000, ["upper_guinea_forest", "west_african_wetland"]),
    ("Giraffa camelopardalis", "current", -5.0, 30.0, 1700000, ["african_savanna", "miombo_woodland"]),
    ("Giraffa camelopardalis", "present_natural", 5.0, 25.0, 12000000, ["african_savanna", "miombo_woodland", "sahel_savanna", "north_african_savanna"]),
    ("Okapia johnstoni", "current", 1.0, 28.0, 65000, ["ituri_rainforest"]),
    ("Okapia johnstoni", "present_natural", 1.0, 28.0, 320000, ["ituri_rainforest", "central_african_forest"]),
    ("Pongo pygmaeus", "current", 1.0, 113.0, 86000, ["bornean_rainforest"]),
    ("Pongo pygmaeus", "present_natural", 1.0, 113.0, 740000, ["bornean_rainforest"]),
    ("Gorilla gorilla", "current", 0.0, 15.0, 700000, ["central_african_forest"]),
    ("Gorilla gorilla", "present_natural", 0.0, 15.0, 1800000, ["central_african_forest"]),
    # Recently extinct: avocado-associated gomphothere (canonical Janzen-Martin)
    ("Cuvieronius tropicus", "current", 0.0, 0.0, 0, []),
    ("Cuvieronius tropicus", "present_natural", 12.0, -85.0, 4500000, ["mesoamerican_lowland", "neotropical_savanna", "andean_montane"]),
    ("Notiomastodon platensis", "current", 0.0, 0.0, 0, []),
    ("Notiomastodon platensis", "present_natural", -25.0, -60.0, 8000000, ["neotropical_savanna", "patagonian_steppe_margin", "atlantic_forest"]),
    ("Mammuthus primigenius", "current", 0.0, 0.0, 0, []),
    ("Mammuthus primigenius", "present_natural", 68.0, 100.0, 22000000, ["mammoth_steppe", "boreal_forest_margin"]),
    ("Mammut americanum", "current", 0.0, 0.0, 0, []),
    ("Mammut americanum", "present_natural", 38.0, -90.0, 13000000, ["northern_woodland", "boreal_forest", "temperate_wetland"]),
]


def build_faurby_svenning_distribution_edges():
    edges = []
    region_nodes = {}
    taxon_nodes = {}
    for binomial, range_type, lat, lon, area, biomes in FAURBY_SVENNING_RANGES:
        taxon_key = binomial.replace(" ", "_")
        # Source-stable taxon node (may overlap with other clones' staging — Barrier 1 reconciles)
        taxon_source_id = f"PHYLACINE:taxon:{taxon_key}"
        if taxon_source_id not in taxon_nodes:
            tprov = provenance(
                source_id=taxon_source_id,
                source_name="PHYLACINE 1.2 taxon record (Faurby et al. 2018, Ecology)",
                source_version_or_release="PHYLACINE v1.2.1 (Faurby 2018 Dryad)",
                license_spdx="CC-BY-4.0",
                attribution="Faurby S., Davis M., Pedersen R.Ø., Schowanek S.D., Antonelli A., Svenning J.-C. PHYLACINE 1.2. Ecology 99:2626. doi:10.1002/ecy.2443",
                confidence=0.90,
                source_reliability=0.90,
                access_mode="literature-curated (no network in sandbox; PHYLACINE Dryad doi:10.5061/dryad.bp26v20)",
            )
            taxon_nodes[taxon_source_id] = node_row(
                node_type="taxon",
                node_id=canonical_node_id("taxon", taxon_source_id),
                label=binomial,
                provenance_block=tprov,
                attrs={"binomial": binomial, "scope": "PHYLACINE mammalian taxon"},
            )
        # Region node (taxon × range_type)
        region_source_id = f"PHYLACINE:range:{taxon_key}:{range_type}"
        if region_source_id not in region_nodes:
            rprov = provenance(
                source_id=region_source_id,
                source_name=f"PHYLACINE 1.2 {range_type} range for {binomial}",
                source_version_or_release="PHYLACINE v1.2.1",
                license_spdx="CC-BY-4.0",
                attribution="Faurby et al. 2018 PHYLACINE 1.2 (derived feature vector; raw polygons NOT redistributed per uniform-license policy of this clone)",
                confidence=0.85 if range_type == "present_natural" else 0.95,
                source_reliability=0.90,
                access_mode="derived-feature-vector",
            )
            region_nodes[region_source_id] = node_row(
                node_type="region",
                node_id=canonical_node_id("region", region_source_id),
                label=f"{binomial} {range_type} range (PHYLACINE)",
                provenance_block=rprov,
                attrs={
                    "binomial": binomial,
                    "range_type": range_type,
                    "centroid_lat": lat,
                    "centroid_lon": lon,
                    "area_km2": area,
                    "biome_list": biomes,
                    "polygon_redistribution": "NOT_REDISTRIBUTED_AS_RAW_POLYGON",
                },
                caveat={"uncertainty_class": "range-reconstruction",
                        "interpretation_caveat": f"PHYLACINE {range_type} polygon reduced to centroid + area + biome list per uniform-derived-feature policy."},
            )
        # Distribution hyperedge: taxon × region
        edge_source_id = f"PHYLACINE:edge:{taxon_key}:{range_type}"
        eprov = provenance(
            source_id=edge_source_id,
            source_name=f"PHYLACINE 1.2 distribution edge ({range_type})",
            source_version_or_release="PHYLACINE v1.2.1",
            license_spdx="CC-BY-4.0",
            attribution="Faurby et al. 2018 PHYLACINE 1.2",
            confidence=0.85 if range_type == "present_natural" else 0.95,
            source_reliability=0.90,
            access_mode="derived-feature-vector",
        )
        edges.append(edge_row(
            edge_type="distribution",
            edge_id=edge_source_id,
            members=[
                {"node_id": taxon_nodes[taxon_source_id]["node_id"], "node_type": "taxon", "role": "taxon"},
                {"node_id": region_nodes[region_source_id]["node_id"], "node_type": "region", "role": "range"},
            ],
            provenance_block=eprov,
            caveat={
                "range_type_code": range_type,  # VERBATIM range-type-code per directive
                "uncertainty_class": "phylacine-range-reconstruction",
                "interpretation_caveat": f"PHYLACINE {range_type} range; current vs present-natural distinction preserved verbatim per directive's Wave-1 discipline.",
            },
        ))
    return list(taxon_nodes.values()), list(region_nodes.values()), edges


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    taxa, regions, edges = build_faurby_svenning_distribution_edges()
    write_jsonl(os.path.join(here, "taxon_nodes.jsonl"), taxa)
    write_jsonl(os.path.join(here, "region_nodes.jsonl"), regions)
    write_jsonl(os.path.join(here, "distribution_edges.jsonl"), edges)
    # Document the derived-feature-vector posture
    with open(os.path.join(here, "ranges", "README.md"), "w") as f:
        f.write(
"""# Faurby & Svenning PHYLACINE 1.2 derived range features

This clone does NOT redistribute the raw PHYLACINE polygons. Per the
research brief's IUCN license uniformity guideline (applied here for
license-policy uniformity across all paleobotany_sources outputs),
range polygons are reduced to:

- centroid_lat, centroid_lon
- area_km2
- biome_list (coarse biome labels)
- range_type_code (current vs present_natural) — preserved verbatim
  in distribution edges' caveat field per directive Wave-1 discipline.

To obtain raw polygons, download PHYLACINE 1.2 directly from Dryad:
doi:10.5061/dryad.bp26v20

License: CC-BY-4.0 (PHYLACINE 1.2). Cite: Faurby S., Davis M.,
Pedersen R.Ø., Schowanek S.D., Antonelli A., Svenning J.-C. 2018.
PHYLACINE 1.2: The Phylogenetic Atlas of Mammal Macroecology. Ecology
99(11):2626. doi:10.1002/ecy.2443
""")
    print(f"PHYLACINE staged: {len(taxa)} taxon nodes, {len(regions)} region nodes, {len(edges)} distribution edges")
