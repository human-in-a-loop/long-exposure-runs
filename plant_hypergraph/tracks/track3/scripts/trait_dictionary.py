"""
Track 3 trait dictionary (frozen, source-grounded).

Maps the Barrier-1 substrate's trait/fruit_type/life_form node labels onto the
canonical Track 3 trait axis required by milestone M2.T3:

    c4_photosynthesis, cam_photosynthesis, succulence, fleshy_fruit, drupe,
    samara, capsule, achene, follicle, aril, elaiosome, myrmecochory,
    ant_domatia, carnivory, parasitism

Rules are LITERAL label matches against substrate node labels. No fuzzy match,
no LLM, no synonym expansion. Out-of-scope labels fall into the `_other`
bucket so nothing is silently dropped.

Provenance of the rule set:
- AusTraits 6.0.0 trait term hierarchy (Falster et al., AusTraits 6.0.0; the
  substrate's `trait`, `fruit_type`, `life_form` nodes were minted from
  AusTraits term IDs during M1.5 ingestion and retain source labels of the
  form `category:value`).
- Photosynthetic-pathway categories follow the AusTraits `photosynthetic_pathway`
  term, which maps onto Sage's C4 / CAM lineage classification (Sage 2004 and
  successors). Both C4 and CAM are reported as separate canonical traits.
- Succulence categories follow the AusTraits `plant_succulence` term, which
  is the textbook coding for Cactaceae- and Euphorbiaceae-style succulence
  in the convergence-sources staging.
- Fruit syndromes (drupe, samara, capsule, achene, follicle) match the
  AusTraits `fruit_type:*` enumerated values directly. `fleshy_fruit`
  uses the explicit `fruit_fleshiness:fleshy` and `diaspore_fleshiness:fleshy`
  coding, not a derived union, so the projection stays auditable.
- `aril` is a dispersal-appendage trait in AusTraits, mapped from
  `dispersal_appendage:aril`.
- `elaiosome` is mapped from `dispersal_appendage:elaiosome`.
- `myrmecochory` is mapped from `dispersal_syndrome:myrmecochory` (and,
  conservatively, `dispersers:ants`).
- `ant_domatia`, `carnivory`, `parasitism` have no matching node label
  in the substrate's `trait`/`fruit_type`/`life_form` inventory. They are
  declared in the dictionary so the coverage table reports them explicitly
  as `data_limited` with `n_retained_edges = 0`.

This file is consumed by build_track3_enrichment.py. It must remain pure
data; no I/O, no network, no provider SDK imports.
"""

from typing import Dict, List

# Canonical Track 3 trait axis (frozen order matches M2.T3 directive).
CANONICAL_TRAITS: List[str] = [
    "c4_photosynthesis",
    "cam_photosynthesis",
    "succulence",
    "fleshy_fruit",
    "drupe",
    "samara",
    "capsule",
    "achene",
    "follicle",
    "aril",
    "elaiosome",
    "myrmecochory",
    "ant_domatia",
    "carnivory",
    "parasitism",
]

# Label -> canonical trait. Labels are the substrate `nodes.label` values for
# `trait`, `fruit_type`, and `life_form` nodes minted under source_group
# `convergence_sources` (austraits_6_0_0).
LABEL_TO_TRAIT: Dict[str, str] = {
    # --- photosynthetic pathway (trait) ---
    "photosynthetic_pathway:c4": "c4_photosynthesis",
    "photosynthetic_pathway:c3-c4": "c4_photosynthesis",
    "photosynthetic_pathway:c4-cam": "c4_photosynthesis",
    "photosynthetic_pathway:cam": "cam_photosynthesis",
    "photosynthetic_pathway:c3-cam": "cam_photosynthesis",
    "photosynthetic_pathway:facultative_cam": "cam_photosynthesis",
    # NB: photosynthetic_pathway:c4-cam routes to c4_photosynthesis only;
    # the underlying taxon will also typically have a separate cam row
    # if AusTraits records the dual-pathway state explicitly.
    # --- succulence (life_form) ---
    "plant_succulence:succulent": "succulence",
    "plant_succulence:succulent_leaves": "succulence",
    "plant_succulence:succulent_stems": "succulence",
    # --- fruit syndromes (fruit_type) ---
    "fruit_fleshiness:fleshy": "fleshy_fruit",
    "diaspore_fleshiness:fleshy": "fleshy_fruit",
    "fruit_type:drupe": "drupe",
    "fruit_type:samara": "samara",
    "fruit_type:capsule": "capsule",
    "fruit_type:achene": "achene",
    "fruit_type:follicle": "follicle",
    # --- dispersal-appendage traits ---
    "dispersal_appendage:aril": "aril",
    "dispersal_appendage:elaiosome": "elaiosome",
    # --- myrmecochory (dispersal_syndrome / dispersers) ---
    "dispersal_syndrome:myrmecochory": "myrmecochory",
    "dispersers:ants": "myrmecochory",
}

# Traits required by M2.T3 floor that have NO matching substrate label.
# Declared so the coverage table reports them with zero retained edges
# and a `data_limited` flag rather than silently missing.
TRAITS_WITHOUT_SUBSTRATE_LABEL: List[str] = [
    "ant_domatia",
    "carnivory",
    "parasitism",
]

# Floor required by M1.5 / M2.T3 minimum-viable-scale criterion.
FLOOR_ACCEPTED_TAXA: int = 500

# Projection rule id (records which rule book produced an output row).
PROJECTION_RULE_ID: str = "track3-trait-dictionary-v1.0-austraits-6.0.0"


def trait_for_label(label: str) -> str:
    """Return canonical trait for a substrate label, or '_other' if unmapped.

    Pure function. No mutation, no I/O.
    """
    return LABEL_TO_TRAIT.get(label, "_other")
