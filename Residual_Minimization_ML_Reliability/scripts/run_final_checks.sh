#!/usr/bin/env bash
# created: 2026-05-14T04:20:00Z
# cycle: 3
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-5

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

.sciml-venv/bin/python scripts/triage_residual_sequences.py
.sciml-venv/bin/python scripts/collocation_certificate_scaling.py
.sciml-venv/bin/python -m pytest tests/test_triage_scaling.py tests/test_collocation_certificate.py -q
