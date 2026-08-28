# M-INGEST-1/egress-ready-automation
#
# State-machine harness that watches data/ingestion/egress_status.jsonl for
# two consecutive fresh media_ok=true rows and, on trigger, chains the
# rated-audio pipeline: harvest -> chunker -> classifier -> ready-flag.
#
# See docs/egress_ready_automation.md for full contract, non-goals, and
# the six-scenario matrix.
#
# created: 2026-08-28
# cycle: 8
# run_id: run-2026-08-28T040704Z
# agent: worker (fork 3a908edcb241 clone 2)
# milestone: M-INGEST-1/egress-ready-automation
