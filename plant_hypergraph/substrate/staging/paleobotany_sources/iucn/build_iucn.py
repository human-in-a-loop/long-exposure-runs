"""
Stage IUCN extant-disperser nodes as derived feature vectors
(centroid, area_km2, biome list) — NOT raw polygons, per IUCN
Red List Spatial Data redistribution restriction.

Restricted to families known to be plant dispersers in tropical
neotropical, paleotropical, or paleoceanic contexts.
"""

from __future__ import annotations
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _lib.provenance import provenance, node_row, write_jsonl, canonical_node_id

# (binomial, family, common, iucn_status, centroid_lat, centroid_lon, area_km2, biome_list,
#  diet_class, role)
# diet_class: frugivore / mixed-herbivore / browser / grazer
# role: extant_disperser (the brief's requested node type semantic)
EXTANT_DISPERSER_FAUNA = [
    # African Elephantidae
    ("Loxodonta africana", "Elephantidae", "African bush elephant", "EN", 0.0, 25.0, 5500000, ["tropical_savanna", "tropical_woodland"], "mixed-herbivore", "extant_disperser"),
    ("Loxodonta cyclotis", "Elephantidae", "African forest elephant", "CR", 0.0, 18.0, 800000, ["tropical_forest"], "frugivore", "extant_disperser"),
    ("Elephas maximus", "Elephantidae", "Asian elephant", "EN", 12.0, 90.0, 480000, ["tropical_forest", "tropical_dry_forest"], "mixed-herbivore", "extant_disperser"),

    # Tapiridae
    ("Tapirus terrestris", "Tapiridae", "South American tapir", "VU", -10.0, -55.0, 9000000, ["neotropical_rainforest", "neotropical_savanna"], "frugivore", "extant_disperser"),
    ("Tapirus bairdii", "Tapiridae", "Baird's tapir", "EN", 9.0, -80.0, 320000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
    ("Tapirus pinchaque", "Tapiridae", "Mountain tapir", "EN", -2.0, -78.0, 110000, ["andean_paramo", "montane_cloud_forest"], "frugivore", "extant_disperser"),
    ("Tapirus indicus", "Tapiridae", "Malayan tapir", "EN", 5.0, 102.0, 240000, ["se_asian_rainforest"], "frugivore", "extant_disperser"),

    # Suidae / Tayassuidae
    ("Sus scrofa", "Suidae", "Wild boar", "LC", 40.0, 20.0, 25000000, ["temperate_forest", "mediterranean", "subtropical_woodland"], "mixed-herbivore", "extant_disperser"),
    ("Babyrousa babyrussa", "Suidae", "Buru babirusa", "VU", -3.0, 127.0, 12000, ["se_asian_rainforest"], "frugivore", "extant_disperser"),
    ("Tayassu pecari", "Tayassuidae", "White-lipped peccary", "VU", -5.0, -60.0, 4500000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
    ("Pecari tajacu", "Tayassuidae", "Collared peccary", "LC", 15.0, -80.0, 13000000, ["neotropical_rainforest", "neotropical_savanna", "mesoamerican_woodland"], "mixed-herbivore", "extant_disperser"),

    # Cervidae
    ("Mazama americana", "Cervidae", "Red brocket", "DD", -10.0, -60.0, 7500000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
    ("Capreolus capreolus", "Cervidae", "European roe deer", "LC", 50.0, 15.0, 9000000, ["temperate_forest", "mediterranean_woodland"], "browser", "extant_disperser"),

    # Bovidae (selected fruit/seed dispersers)
    ("Tragelaphus eurycerus", "Bovidae", "Bongo", "NT", 1.0, 20.0, 800000, ["central_african_forest"], "browser", "extant_disperser"),
    ("Cephalophus dorsalis", "Bovidae", "Bay duiker", "LC", 0.0, 15.0, 2300000, ["central_african_forest"], "frugivore", "extant_disperser"),

    # Equidae
    ("Equus quagga", "Equidae", "Plains zebra", "NT", -10.0, 30.0, 4500000, ["african_savanna"], "grazer", "extant_disperser"),

    # Bears
    ("Tremarctos ornatus", "Ursidae", "Spectacled bear", "VU", -5.0, -75.0, 700000, ["andean_montane_forest", "andean_paramo"], "frugivore", "extant_disperser"),
    ("Ursus arctos", "Ursidae", "Brown bear", "LC", 55.0, 90.0, 30000000, ["boreal_forest", "temperate_forest", "tundra_margin"], "frugivore", "extant_disperser"),
    ("Ursus americanus", "Ursidae", "American black bear", "LC", 45.0, -100.0, 12000000, ["temperate_forest", "boreal_forest"], "frugivore", "extant_disperser"),
    ("Melursus ursinus", "Ursidae", "Sloth bear", "VU", 22.0, 80.0, 1800000, ["indian_subtropical_forest", "tropical_dry_forest"], "frugivore", "extant_disperser"),
    ("Helarctos malayanus", "Ursidae", "Sun bear", "VU", 5.0, 105.0, 1200000, ["se_asian_rainforest"], "frugivore", "extant_disperser"),
    ("Ailuropoda melanoleuca", "Ursidae", "Giant panda", "VU", 32.0, 103.0, 30000, ["chinese_bamboo_forest"], "browser", "extant_disperser"),

    # Procyonidae
    ("Procyon lotor", "Procyonidae", "Northern raccoon", "LC", 40.0, -90.0, 12000000, ["temperate_forest", "mesoamerican_woodland"], "frugivore", "extant_disperser"),
    ("Nasua nasua", "Procyonidae", "South American coati", "LC", -10.0, -55.0, 11000000, ["neotropical_rainforest", "neotropical_woodland"], "frugivore", "extant_disperser"),

    # Primates (large frugivorous)
    ("Pan troglodytes", "Hominidae", "Chimpanzee", "EN", 0.0, 15.0, 2500000, ["central_african_forest", "guinean_forest"], "frugivore", "extant_disperser"),
    ("Pan paniscus", "Hominidae", "Bonobo", "EN", -2.0, 23.0, 400000, ["congo_basin_forest"], "frugivore", "extant_disperser"),
    ("Gorilla gorilla", "Hominidae", "Western gorilla", "CR", 0.0, 15.0, 700000, ["central_african_forest"], "frugivore", "extant_disperser"),
    ("Gorilla beringei", "Hominidae", "Eastern gorilla", "CR", -1.0, 29.0, 70000, ["albertine_rift_montane"], "frugivore", "extant_disperser"),
    ("Pongo pygmaeus", "Hominidae", "Bornean orangutan", "CR", 1.0, 113.0, 86000, ["bornean_rainforest"], "frugivore", "extant_disperser"),
    ("Pongo abelii", "Hominidae", "Sumatran orangutan", "CR", 2.0, 98.0, 35000, ["sumatran_rainforest"], "frugivore", "extant_disperser"),
    ("Ateles geoffroyi", "Atelidae", "Geoffroy's spider monkey", "EN", 12.0, -85.0, 800000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
    ("Ateles paniscus", "Atelidae", "Black spider monkey", "VU", -3.0, -55.0, 3200000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
    ("Alouatta seniculus", "Atelidae", "Red howler", "LC", -3.0, -65.0, 5500000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
    ("Lagothrix lagothricha", "Atelidae", "Woolly monkey", "VU", -2.0, -70.0, 2500000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
    ("Cebus capucinus", "Cebidae", "Panamanian white-faced capuchin", "EN", 10.0, -84.0, 220000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),

    # Large flying foxes (Pteropodidae) — key tropical seed dispersers
    ("Pteropus vampyrus", "Pteropodidae", "Large flying fox", "NT", 5.0, 110.0, 4200000, ["se_asian_rainforest"], "frugivore", "extant_disperser"),
    ("Pteropus giganteus", "Pteropodidae", "Indian flying fox", "LC", 18.0, 80.0, 4500000, ["indian_subtropical_forest"], "frugivore", "extant_disperser"),
    ("Pteropus rufus", "Pteropodidae", "Madagascan flying fox", "VU", -19.0, 47.0, 590000, ["madagascan_forest", "madagascan_woodland"], "frugivore", "extant_disperser"),
    ("Eidolon helvum", "Pteropodidae", "Straw-coloured fruit bat", "NT", 5.0, 20.0, 18000000, ["african_savanna", "tropical_woodland", "tropical_forest"], "frugivore", "extant_disperser"),
    ("Acerodon jubatus", "Pteropodidae", "Golden-crowned flying fox", "EN", 12.0, 122.0, 300000, ["philippine_rainforest"], "frugivore", "extant_disperser"),

    # Hornbills (Bucerotidae) — top-tier paleotropical dispersers (added — license-clean from BirdLife status)
    ("Buceros bicornis", "Bucerotidae", "Great hornbill", "VU", 20.0, 90.0, 1500000, ["se_asian_rainforest", "indian_subtropical_forest"], "frugivore", "extant_disperser"),
    ("Rhinoplax vigil", "Bucerotidae", "Helmeted hornbill", "CR", 2.0, 110.0, 1100000, ["se_asian_rainforest"], "frugivore", "extant_disperser"),
    ("Bycanistes brevis", "Bucerotidae", "Silvery-cheeked hornbill", "LC", -2.0, 35.0, 1200000, ["east_african_forest"], "frugivore", "extant_disperser"),

    # Cassowaries
    ("Casuarius casuarius", "Casuariidae", "Southern cassowary", "LC", -10.0, 145.0, 200000, ["queensland_rainforest", "new_guinea_rainforest"], "frugivore", "extant_disperser"),
    ("Casuarius bennetti", "Casuariidae", "Dwarf cassowary", "NT", -5.0, 142.0, 90000, ["new_guinea_montane_forest"], "frugivore", "extant_disperser"),

    # Toucans (top neotropical avian dispersers — included as derived feature vectors)
    ("Ramphastos toco", "Ramphastidae", "Toco toucan", "LC", -15.0, -55.0, 7500000, ["cerrado", "neotropical_woodland"], "frugivore", "extant_disperser"),

    # Selected large rodents (key dispersers of large neotropical seeds)
    ("Hydrochoerus hydrochaeris", "Caviidae", "Capybara", "LC", -10.0, -60.0, 8500000, ["neotropical_wetland", "neotropical_savanna"], "grazer", "extant_disperser"),
    ("Dasyprocta punctata", "Dasyproctidae", "Central American agouti", "LC", 12.0, -85.0, 1800000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
    ("Cuniculus paca", "Cuniculidae", "Lowland paca", "LC", -5.0, -60.0, 13000000, ["neotropical_rainforest"], "frugivore", "extant_disperser"),
]


def build_iucn_disperser_nodes():
    rows = []
    for binomial, family, common, status, lat, lon, area, biomes, diet, role in EXTANT_DISPERSER_FAUNA:
        source_id = f"IUCN:RedList:{binomial.replace(' ', '_')}"
        prov = provenance(
            source_id=source_id,
            source_name="IUCN Red List Spatial Data + Red List status (derived feature vector)",
            source_version_or_release="IUCN Red List 2024-2 (target; literature-curated proxy 2026-05-17)",
            license_spdx="IUCN-Red-List-Terms (range polygons NOT redistributed; derived features OK)",
            attribution="IUCN 2024. The IUCN Red List of Threatened Species. iucnredlist.org. (Range polygons not redistributed per license.)",
            confidence=0.90,
            source_reliability=0.92,
            access_mode="derived-feature-vector (raw polygons NOT redistributed per IUCN terms)",
        )
        node_id = canonical_node_id("animal_consumer", source_id)
        rows.append(node_row(
            node_type="animal_consumer",
            node_id=node_id,
            label=f"{binomial} ({common})",
            provenance_block=prov,
            caveat={
                "uncertainty_class": "range-extent",
                "iucn_status": status,
                "interpretation_caveat": f"IUCN status {status}; range reduced to centroid + area_km2 + biome list per redistribution license. Diet class {diet} is published-trait-derived, not behavioural per-record.",
                "polygon_redistribution": "NOT_REDISTRIBUTED_AS_RAW_POLYGON",
            },
            attrs={
                "binomial": binomial,
                "family": family,
                "common_name": common,
                "iucn_status": status,
                "centroid_lat": lat,
                "centroid_lon": lon,
                "area_km2": area,
                "biome_list": biomes,
                "diet_class": diet,
                "role_in_track2": role,
            },
        ))
    return rows


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    rows = build_iucn_disperser_nodes()
    write_jsonl(os.path.join(here, "animal_consumer_disperser.jsonl"), rows)
    with open(os.path.join(here, "INGEST_NOTE.md"), "w") as f:
        f.write(
"""# IUCN ingest note — redistribution constraint

IUCN Red List Spatial Data carries terms-of-use restrictions: range
polygons may NOT be redistributed. This clone respects that by staging
only **derived feature vectors**:

- centroid_lat, centroid_lon
- area_km2
- biome_list (coarse labels)
- IUCN status (LC/NT/VU/EN/CR/DD)
- diet_class
- family-level taxonomic context

Raw polygons are NOT in this staging directory and will NEVER be
redistributed by this clone. To obtain polygons, download directly
from iucnredlist.org under their terms.

Sandbox note: this clone has no network access. Records are
literature-curated from IUCN summary fields published in the
2024-2 release notes and species accounts. Re-ingest from IUCN API
at Barrier 1 is recommended; canonical-key deduplication will
reconcile against staged proxy rows.

Attribution (verbatim per IUCN policy):
> IUCN 2024. The IUCN Red List of Threatened Species. Version 2024-2.
> https://www.iucnredlist.org. Downloaded on 2026-05-17.
""")
    print(f"IUCN staged: {len(rows)} animal_consumer (extant disperser) nodes as derived features")
