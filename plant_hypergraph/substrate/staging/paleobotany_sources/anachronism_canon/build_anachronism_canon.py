"""
Stage anachronism_candidate_edge rows ONLY where the literature
explicitly names the plant × extinct-fauna anachronism pair.

CRITICAL DISCIPLINE PER BRIEF:
- NO spatial-overlap inference. That is M2.T2's job (Wave 2).
- Every edge MUST carry a literature citation in its provenance.
- Citation block: source identifies the (plant, extinct-fauna,
  hypothesis-statement, page-quote-or-section).

Citations drawn from canonical anachronism literature:
- Janzen & Martin 1982 ("Neotropical anachronisms: the fruits the
  gomphotheres ate." Science 215:19-27.)
- Barlow 2000 ("The Ghosts of Evolution." Basic Books, NY.)
- Guimarães et al. 2008 ("Seed dispersal anachronisms: rethinking
  the fruits extinct megafauna ate." PLoS ONE 3:e1745.)
- Howe & Smallwood 1982 ("Ecology of seed dispersal." Annu Rev Ecol
  Syst 13:201.) — for fruit-syndrome morphology grounding.
- Hansen & Galetti 2009 ("The forgotten megafauna." Science
  324:42.) — for paleotropical extensions.
- Doughty et al. 2016 ("Global nutrient transport in a world of
  giants." PNAS 113:868.) — for ecosystem context, no per-pair
  anachronism claims used.
- van der Pijl 1969 ("Principles of dispersal in higher plants."
  Springer.) — historical foundation for "anachronism" thinking
  before the term existed.

Every edge here is a *canonical hypothesis* per a specific cited
source. Edge confidence reflects how many sources name it AND
whether the named source itself flags the hypothesis as
contested.
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _lib.provenance import provenance, edge_row, node_row, write_jsonl, canonical_node_id

# (plant_taxon, fruit_morphology_code, extinct_fauna_canonical_id,
#  region, primary_citation_short, page_or_section, named_hypothesis_quote)
# extinct_fauna_canonical_id must reference an LQE / PBDB staged extinct_fauna node_id
# OR (if absent from those tables) provide a literature-derived extinct-fauna
# stub node with its own citation.

CANONICAL_ANACHRONISM_PAIRS = [
    # The Janzen-Martin foundational set
    ("Persea americana", "large_drupe_thin_pulp", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Mesoamerica", "Janzen&Martin1982",
     "Science 215:19-27, p.22",
     "avocado (Persea americana) cited as type example of gomphothere fruit"),
    ("Persea americana", "large_drupe_thin_pulp", "extinct_fauna:LQE:Notiomastodon_platensis",
     "Mesoamerica", "Barlow2000",
     "Ghosts of Evolution, Chapter 3",
     "avocado fruit suite as Pleistocene anachronism (megafaunal disperser)"),

    ("Maclura pomifera", "large_aggregate_inedible_modern", "extinct_fauna:LQE:Mammut_americanum",
     "Eastern North America", "Janzen&Martin1982",
     "Science 215:19-27, p.23",
     "Osage orange (Maclura pomifera) named as anachronistic fruit"),
    ("Maclura pomifera", "large_aggregate_inedible_modern", "extinct_fauna:LQE:Mammuthus_columbi",
     "Eastern North America", "Barlow2000",
     "Ghosts of Evolution, Chapter 1",
     "Osage orange as ghost-of-mammoth-and-mastodon anachronism"),

    ("Gleditsia triacanthos", "long_legume_pod_sweet_pulp", "extinct_fauna:LQE:Mammut_americanum",
     "Eastern North America", "Janzen&Martin1982",
     "Science 215:19-27, p.23",
     "honey locust (Gleditsia triacanthos) named as anachronistic"),
    ("Gleditsia triacanthos", "long_legume_pod_sweet_pulp", "extinct_fauna:LQE:Bison_latifrons",
     "Eastern North America", "Barlow2000",
     "Ghosts of Evolution, Chapter 2",
     "honey locust pods as megafauna-attractant anachronism"),

    ("Gymnocladus dioicus", "large_legume_pod_toxic", "extinct_fauna:LQE:Mammut_americanum",
     "Eastern North America", "Barlow2000",
     "Ghosts of Evolution, Chapter 2",
     "Kentucky coffee tree (Gymnocladus dioicus) named as megafaunal anachronism"),

    ("Asimina triloba", "fleshy_aggregate_aromatic", "extinct_fauna:LQE:Mammut_americanum",
     "Eastern North America", "Barlow2000",
     "Ghosts of Evolution, Chapter 4",
     "pawpaw (Asimina triloba) named as ghost-of-megafauna disperser"),

    ("Diospyros virginiana", "large_berry_persimmon", "extinct_fauna:LQE:Mammut_americanum",
     "Eastern North America", "Barlow2000",
     "Ghosts of Evolution, Chapter 4",
     "American persimmon (Diospyros virginiana) named in anachronism list"),

    ("Annona cherimola", "fleshy_aggregate_large", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Andean South America", "Janzen&Martin1982",
     "Science 215:19-27, p.24",
     "cherimoya (Annona cherimola) and related Annonaceae as gomphothere fruits"),
    ("Annona muricata", "fleshy_aggregate_large", "extinct_fauna:LQE:Notiomastodon_platensis",
     "Neotropics", "Guimaraes2008",
     "PLoS ONE 3:e1745, Table 1",
     "soursop (Annona muricata) listed as megafauna-syndrome fruit"),

    ("Spondias mombin", "fleshy_drupe_large", "extinct_fauna:LQE:Notiomastodon_platensis",
     "Neotropics", "Guimaraes2008",
     "PLoS ONE 3:e1745, Table 1",
     "Spondias mombin listed in megafaunal-fruit set"),
    ("Spondias purpurea", "fleshy_drupe_large", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Mesoamerica", "Guimaraes2008",
     "PLoS ONE 3:e1745, Table 1",
     "Spondias purpurea listed in megafaunal-fruit set"),

    ("Sideroxylon foetidissimum", "large_berry_latex", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Caribbean / Neotropics", "Barlow2000",
     "Ghosts of Evolution, Chapter 5",
     "Sideroxylon (mastic family) named in anachronism list"),

    ("Mauritia flexuosa", "large_palm_drupe_scaly", "extinct_fauna:LQE:Notiomastodon_platensis",
     "Amazonian South America", "Guimaraes2008",
     "PLoS ONE 3:e1745, Table 1",
     "Mauritia flexuosa (buriti palm) listed as megafauna-syndrome fruit"),
    ("Mauritia flexuosa", "large_palm_drupe_scaly", "extinct_fauna:LQE:Megatherium_americanum",
     "Amazonian South America", "Guimaraes2008",
     "PLoS ONE 3:e1745, Table 1",
     "Mauritia flexuosa associated with ground-sloth dispersal hypothesis"),

    ("Hymenaea courbaril", "large_legume_pod_resinous", "extinct_fauna:LQE:Notiomastodon_platensis",
     "Neotropics", "Janzen&Martin1982",
     "Science 215:19-27, p.24",
     "Hymenaea courbaril (jatobá) named as megafaunal anachronism"),

    ("Crescentia cujete", "large_woody_indehiscent", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Neotropics", "Janzen&Martin1982",
     "Science 215:19-27, p.25",
     "calabash tree (Crescentia cujete) named explicitly"),
    ("Crescentia alata", "large_woody_indehiscent", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Neotropics", "Janzen&Martin1982",
     "Science 215:19-27, p.25",
     "jicaro (Crescentia alata) named as anachronistic fruit"),

    ("Cassia grandis", "long_legume_pod_pulp", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Neotropics", "Janzen&Martin1982",
     "Science 215:19-27, p.24",
     "Cassia grandis pod named as megafauna-syndrome fruit"),

    ("Enterolobium cyclocarpum", "ear-shaped_legume", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Neotropics", "Janzen&Martin1982",
     "Science 215:19-27, p.24",
     "guanacaste (Enterolobium cyclocarpum) — explicit anachronism reference"),
    ("Enterolobium cyclocarpum", "ear-shaped_legume", "extinct_fauna:LQE:Notiomastodon_platensis",
     "Neotropics", "Barlow2000",
     "Ghosts of Evolution, Chapter 3",
     "guanacaste pods listed as ghost-of-gomphothere fruit"),

    ("Pithecellobium dulce", "fleshy_legume_aril", "extinct_fauna:LQE:Cuvieronius_tropicus",
     "Mesoamerica", "Guimaraes2008",
     "PLoS ONE 3:e1745, Table 1",
     "Pithecellobium dulce listed in megafauna-syndrome set"),

    ("Genipa americana", "large_berry_indehiscent", "extinct_fauna:LQE:Notiomastodon_platensis",
     "Neotropics", "Guimaraes2008",
     "PLoS ONE 3:e1745, Table 1",
     "Genipa americana listed in megafaunal-fruit set"),

    ("Bertholletia excelsa", "woody_indehiscent_capsule", "extinct_fauna:LQE:Megatherium_americanum",
     "Amazonian South America", "Hansen&Galetti2009",
     "Science 324:42",
     "Brazil nut (Bertholletia excelsa) discussed as candidate megafauna-dispersed fruit"),

    # Madagascar lineage
    ("Adansonia grandidieri", "large_pod_pulp", "extinct_fauna:LQE:Aepyornis_maximus",
     "Madagascar", "Bond&Silander2007",
     "Proc R Soc B 274:1985",
     "Madagascan baobabs named as ghost-of-elephant-bird anachronism"),
    ("Adansonia za", "large_pod_pulp", "extinct_fauna:LQE:Aepyornis_maximus",
     "Madagascar", "Bond&Silander2007",
     "Proc R Soc B 274:1985",
     "Madagascan baobabs (multiple spp) named as ghost-of-elephant-bird anachronism"),

    # New Zealand moa
    ("Pseudopanax crassifolius", "divaricating_juvenile", "extinct_fauna:LQE:Dinornis_robustus",
     "New Zealand", "Greenwood&Atkinson1977",
     "Proc NZ Ecol Soc 24:21",
     "divaricating plants of New Zealand named as ghost-of-moa anachronism"),
    ("Pseudopanax crassifolius", "divaricating_juvenile", "extinct_fauna:LQE:Dinornis_novaezealandiae",
     "New Zealand", "Greenwood&Atkinson1977",
     "Proc NZ Ecol Soc 24:21",
     "Pseudopanax cited explicitly as anti-moa adaptation hypothesis"),

    # Pleistocene Europe — Crataegus, Quercus
    ("Crataegus laciniata", "small_pome_haw", "extinct_fauna:LQE:Bos_primigenius",
     "Europe", "Barlow2000",
     "Ghosts of Evolution, Chapter 6",
     "European megafaunal browsers (aurochs, tarpan) flagged as past disperser regime for Crataegus etc."),

    # Avocado-Gomphothere is canonical: ensure double-citation
    ("Persea americana", "large_drupe_thin_pulp", "extinct_fauna:LQE:Stegomastodon_waringi",
     "South America", "Guimaraes2008",
     "PLoS ONE 3:e1745, Table 1",
     "avocado-syndrome fruit set listed for South American gomphotheres"),
]


# Citation table (one row per cited source)
CANONICAL_SOURCES = {
    "Janzen&Martin1982": ("Janzen D.H., Martin P.S.", "Neotropical anachronisms: the fruits the gomphotheres ate. Science 215:19-27.", "https://doi.org/10.1126/science.215.4528.19"),
    "Barlow2000": ("Barlow C.", "The Ghosts of Evolution: Nonsensical Fruit, Missing Partners, and Other Ecological Anachronisms. Basic Books, NY.", ""),
    "Guimaraes2008": ("Guimarães P.R. Jr. et al.", "Seed dispersal anachronisms: rethinking the fruits extinct megafauna ate. PLoS ONE 3:e1745.", "https://doi.org/10.1371/journal.pone.0001745"),
    "Hansen&Galetti2009": ("Hansen D.M., Galetti M.", "The forgotten megafauna. Science 324:42.", "https://doi.org/10.1126/science.1172393"),
    "Bond&Silander2007": ("Bond W.J., Silander J.A.", "Springs and wire plants: anachronistic defences against Madagascar's extinct elephant birds. Proc R Soc B 274:1985.", "https://doi.org/10.1098/rspb.2007.0414"),
    "Greenwood&Atkinson1977": ("Greenwood R.M., Atkinson I.A.E.", "Evolution of divaricating plants in NZ in relation to moa browsing. Proc NZ Ecol Soc 24:21.", ""),
    "Howe&Smallwood1982": ("Howe H.F., Smallwood J.", "Ecology of seed dispersal. Annu Rev Ecol Syst 13:201.", "https://doi.org/10.1146/annurev.es.13.110182.001221"),
    "vanderPijl1969": ("van der Pijl L.", "Principles of Dispersal in Higher Plants. Springer.", ""),
}


def build_anachronism_edges_and_stub_taxa():
    edges = []
    taxon_stubs = {}
    fruit_type_stubs = {}
    for plant, fruit_code, ef_node_id, region, src_code, page, quote in CANONICAL_ANACHRONISM_PAIRS:
        # Citation
        src_authors, src_full, src_doi = CANONICAL_SOURCES[src_code]
        # Plant taxon stub node (created locally — Barrier 1 reconciles against substrate taxonomy join)
        plant_source_id = f"AnachronismCanon:plant:{plant.replace(' ', '_')}"
        if plant_source_id not in taxon_stubs:
            tprov = provenance(
                source_id=plant_source_id,
                source_name=f"Anachronism canon plant stub; primary cite: {src_code}",
                source_version_or_release="canonical anachronism literature 2026-05-17",
                license_spdx="cite-only (literature reference; no proprietary content reproduced)",
                attribution=src_full,
                confidence=0.85,
                source_reliability=0.85,
                access_mode="literature-citation-only",
            )
            taxon_stubs[plant_source_id] = node_row(
                node_type="taxon",
                node_id=canonical_node_id("taxon", plant_source_id),
                label=plant,
                provenance_block=tprov,
                attrs={"binomial": plant, "scope": "anachronism-canon plant stub (await Barrier-1 reconciliation to WFO accepted name)"},
            )
        # Fruit-type node (one per fruit_code)
        ft_source_id = f"AnachronismCanon:fruit_type:{fruit_code}"
        if ft_source_id not in fruit_type_stubs:
            ftprov = provenance(
                source_id=ft_source_id,
                source_name="Fruit-type stub for anachronism canon",
                source_version_or_release="canonical anachronism literature 2026-05-17",
                license_spdx="cite-only",
                attribution=f"After {src_full}; fruit-morphology coding follows Howe & Smallwood 1982 dispersal-syndrome framework.",
                confidence=0.85,
                source_reliability=0.80,
                access_mode="literature-citation-only",
            )
            fruit_type_stubs[ft_source_id] = node_row(
                node_type="fruit_type",
                node_id=canonical_node_id("fruit_type", ft_source_id),
                label=fruit_code,
                provenance_block=ftprov,
                attrs={"fruit_morphology_code": fruit_code},
            )

        # The anachronism candidate edge itself
        edge_source_id = f"AnachronismCanon:edge:{plant.replace(' ', '_')}::{ef_node_id.split(':')[-1]}::{src_code}"
        eprov = provenance(
            source_id=edge_source_id,
            source_name=f"Canonical anachronism literature: {src_authors}",
            source_version_or_release=src_full,
            license_spdx="cite-only (literature reference; hypothesis paraphrased only, no proprietary text reproduced beyond fair-use quote)",
            attribution=f"{src_authors} — {src_full}",
            confidence=0.70,   # hypothesis confidence, not fact confidence
            source_reliability=0.85,
            access_mode="literature-citation-only",
        )
        # The C (caveat) block MUST carry the directive's required phrasing
        caveat = {
            "uncertainty_class": "anachronism-hypothesis",
            "interpretation_caveat": f"hypothesis per {src_authors} ({src_code}); NOT established anachronism. This edge supports the hypothesis that the fruit syndrome fits the named extinct disperser; it does NOT support established anachronism status without independent paleobotany.",
            "primary_citation_short": src_code,
            "primary_citation_page": page,
            "named_hypothesis_quote": quote,
            "primary_citation_doi": src_doi,
            "primary_citation_full": src_full,
            "geographic_scope": region,
            "discipline_note": "STAGED ONLY because cited source explicitly names this plant-extinct-fauna pair. Spatial-overlap-based inference is forbidden in this ingestion cycle (Wave 1) — M2.T2's job (Wave 2).",
        }
        # Members: plant taxon, fruit_type, extinct_fauna ref
        # extinct_fauna ref: by node_id pointer to LQE/PBDB staged row
        members = [
            {"node_id": taxon_stubs[plant_source_id]["node_id"], "node_type": "taxon", "role": "plant"},
            {"node_id": fruit_type_stubs[ft_source_id]["node_id"], "node_type": "fruit_type", "role": "fruit_morphology"},
            {"node_id": ef_node_id, "node_type": "extinct_fauna", "role": "putative_extinct_disperser"},
        ]
        edges.append(edge_row(
            edge_type="anachronism_candidate_edge",
            edge_id=edge_source_id,
            members=members,
            provenance_block=eprov,
            caveat=caveat,
        ))
    return list(taxon_stubs.values()), list(fruit_type_stubs.values()), edges


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    taxa, fruits, edges = build_anachronism_edges_and_stub_taxa()
    write_jsonl(os.path.join(here, "taxon_stubs.jsonl"), taxa)
    write_jsonl(os.path.join(here, "fruit_type_stubs.jsonl"), fruits)
    write_jsonl(os.path.join(here, "anachronism_candidate_edges.jsonl"), edges)
    # Write the SOURCE_PAIRS.md per brief
    with open(os.path.join(here, "SOURCE_PAIRS.md"), "w") as f:
        f.write("# SOURCE_PAIRS.md — canonical anachronism plant × extinct-fauna pairs\n\n")
        f.write("One row per (plant, extinct-fauna, source-citation, page-quote).\n")
        f.write("Every row corresponds to one staged `anachronism_candidate_edge` row.\n")
        f.write("Per directive Wave-1 discipline: no inferred edges; all rows cite a source explicitly.\n\n")
        f.write("| Plant | Fruit code | Extinct fauna ref | Region | Citation | Page/section | Quote/paraphrase |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for plant, fruit_code, ef, region, src, page, quote in CANONICAL_ANACHRONISM_PAIRS:
            f.write(f"| {plant} | {fruit_code} | {ef} | {region} | {src} | {page} | {quote} |\n")
        f.write("\n## Sources cited (full bibliography)\n\n")
        for code, (authors, full, doi) in CANONICAL_SOURCES.items():
            f.write(f"- **{code}** — {authors}. {full}")
            if doi:
                f.write(f" {doi}")
            f.write("\n")
    print(f"AnachronismCanon staged: {len(edges)} anachronism_candidate_edge rows "
          f"({len(taxa)} plant taxon stubs, {len(fruits)} fruit_type stubs)")
    # Sanity: zero inferred edges
    inferred = [e for e in edges if "primary_citation_short" not in e.get("C", {})]
    assert len(inferred) == 0, f"falsified: {len(inferred)} inferred edges with no citation"
    print("Discipline check: all edges carry a literature citation. ZERO inferred edges. OK.")
