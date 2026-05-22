import unittest

from tools import hierarchy_metrics as hm


TAXA = [
    {"taxon_id": "taxon:F1", "rank": "family", "parent_taxon_id": "", "family_id": "taxon:F1", "genus_id": ""},
    {"taxon_id": "taxon:F2", "rank": "family", "parent_taxon_id": "", "family_id": "taxon:F2", "genus_id": ""},
    {"taxon_id": "taxon:G1", "rank": "genus", "parent_taxon_id": "taxon:F1", "family_id": "taxon:F1", "genus_id": "taxon:G1"},
    {"taxon_id": "taxon:G2", "rank": "genus", "parent_taxon_id": "taxon:F1", "family_id": "taxon:F1", "genus_id": "taxon:G2"},
    {"taxon_id": "taxon:G3", "rank": "genus", "parent_taxon_id": "taxon:F2", "family_id": "taxon:F2", "genus_id": "taxon:G3"},
    {"taxon_id": "taxon:S1", "rank": "species", "parent_taxon_id": "taxon:G1", "family_id": "taxon:F1", "genus_id": "taxon:G1"},
    {"taxon_id": "taxon:S2", "rank": "species", "parent_taxon_id": "taxon:G1", "family_id": "taxon:F1", "genus_id": "taxon:G1"},
    {"taxon_id": "taxon:S3", "rank": "species", "parent_taxon_id": "taxon:G2", "family_id": "taxon:F1", "genus_id": "taxon:G2"},
    {"taxon_id": "taxon:S4", "rank": "species", "parent_taxon_id": "taxon:F2", "family_id": "taxon:F2", "genus_id": ""},
]

NAMES = [
    {"name_id": "name:S1:accepted", "name_string": "Genus1 species1", "accepted_taxon_id": "taxon:S1"},
    {"name_id": "name:S1:syn", "name_string": "Old species1", "accepted_taxon_id": "taxon:S1"},
    {"name_id": "name:S2:accepted", "name_string": "Genus1 species2", "accepted_taxon_id": "taxon:S2"},
]

RETICULATE_EDGES = [
    {"edge_id": "edge:r1", "edge_family": "reticulate_or_hybrid_signal", "node_id": "taxon:S1", "role": "reticulate_child", "edge_weight": "1"},
    {"edge_id": "edge:r1", "edge_family": "reticulate_or_hybrid_signal", "node_id": "taxon:G1", "role": "source_lineage", "edge_weight": "1"},
    {"edge_id": "edge:r1", "edge_family": "reticulate_or_hybrid_signal", "node_id": "taxon:G3", "role": "source_lineage", "edge_weight": "1"},
    {"edge_id": "edge:t1", "edge_family": "trait_syndrome", "node_id": "taxon:G2", "role": "convergent_taxon", "edge_weight": "1"},
]


class HierarchyMetricTests(unittest.TestCase):
    def test_synonym_normalized_match_differs_from_flat(self):
        self.assertEqual(hm.flat_exact_match(["Old species1"], ["taxon:S1"]), 0.0)
        self.assertEqual(hm.synonym_normalized_exact_match(["Old species1"], ["taxon:S1"], NAMES), 1.0)
        self.assertEqual(hm.synonym_normalized_exact_match(["Genus1 species2"], ["taxon:S1"], NAMES), 0.0)

    def test_hierarchy_distance_distinguishes_near_misses(self):
        self.assertEqual(hm.hierarchy_distance("taxon:S1", "taxon:S1", TAXA), 0)
        self.assertEqual(hm.hierarchy_distance("taxon:S2", "taxon:S1", TAXA), 2)
        self.assertEqual(hm.hierarchy_distance("taxon:S3", "taxon:S1", TAXA), 4)

    def test_missing_rank_bridge_shortens_observed_path(self):
        self.assertEqual(hm.hierarchy_distance("taxon:F2", "taxon:S4", TAXA), 1)
        self.assertGreater(hm.hierarchy_distance("taxon:G1", "taxon:S4", TAXA), 1)

    def test_hierarchy_coherence_violation_rate(self):
        predictions = [
            {"family_id": "taxon:F1", "genus_id": "taxon:G1", "species_id": "taxon:S1"},
            {"family_id": "taxon:F2", "genus_id": "taxon:G1", "species_id": "taxon:S1"},
            {"family_id": "taxon:F2", "genus_id": "", "species_id": "taxon:S4"},
        ]
        self.assertAlmostEqual(hm.hierarchy_coherence_violation_rate(predictions, TAXA), 1 / 3)
        self.assertAlmostEqual(hm.hierarchy_coherence_violation_rate([predictions[-1]], TAXA, allow_missing_rank_bridge=False), 0.0)

    def test_reticulate_near_miss_credits_only_source_lineage(self):
        self.assertEqual(hm.reticulate_near_miss_score("taxon:S1", "taxon:S1", TAXA, RETICULATE_EDGES), 1.0)
        self.assertEqual(hm.reticulate_near_miss_score("taxon:G3", "taxon:S1", TAXA, RETICULATE_EDGES), 0.5)
        self.assertEqual(hm.reticulate_near_miss_score("taxon:S3", "taxon:S1", TAXA, RETICULATE_EDGES), 0.0)


if __name__ == "__main__":
    unittest.main()
