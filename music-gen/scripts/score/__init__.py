# M-SCORE-1 — MuseScore programmatic bridge (round-trip + merged-full-song).
# See docs/score_bridge_report.md for design + contract.
#
# Non-factor isolation contract: this package MUST NOT import
# scripts.classifier.sidecar_nonfactor. Scores never carry genre / artist /
# era / country / language fields.
