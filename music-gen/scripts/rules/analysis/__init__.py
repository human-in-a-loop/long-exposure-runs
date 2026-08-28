# ---
# created: 2026-08-28T11:30:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 855d4c2e9945)
# milestone: M-GEN-1/collision-floor-investigation
# ---
"""M-GEN-1 collision floor structural investigation package.

Analysis-only. Consumes the frozen 76-row rules ledger and cycle-13
batch-v2 collision matrix. Attributes each collision pair to its
dominant rule_type contributor, extracts structural fingerprints,
computes pairwise structural distances, produces cluster verdict,
and proposes rule_sub_type intervention (or hash-geometric verdict).
"""
