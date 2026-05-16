# created: 2026-05-16T06:10:00Z
# cycle: 19
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M8-quotient-family-bridge

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_quotient_family_bridge_table.py"
CSV_PATH = ROOT / "data/extension_candidates/quotient_family_bridge_table.csv"


def load_builder():
    spec = importlib.util.spec_from_file_location("bridge_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_rows():
    if not CSV_PATH.exists():
        builder = load_builder()
        assert builder.main() == 0
    with CSV_PATH.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_all_required_bridge_statuses_appear():
    rows = load_rows()
    statuses = {row["bridge_status"] for row in rows}
    required = {"covered", "partially_covered", "heuristic_only", "not_covered"}
    assert required <= statuses


def test_supporting_artifact_paths_exist():
    for row in load_rows():
        assert (ROOT / row["supporting_artifact"]).exists(), row["supporting_artifact"]


def test_table_includes_theorem_1_and_theorem_2_objects():
    sources = {row["source"] for row in load_rows()}
    assert "Theorem 1 variance" in sources
    assert "Theorem 2 fourth moment" in sources


def test_positive_partial_and_negative_classifications():
    statuses = [row["bridge_status"] for row in load_rows()]
    assert "covered" in statuses
    assert "partially_covered" in statuses
    assert ("not_covered" in statuses) or ("heuristic_only" in statuses)


def test_manifest_has_required_columns():
    rows = load_rows()
    required = set(load_builder().FIELDNAMES)
    assert rows
    assert required <= set(rows[0])


if __name__ == "__main__":
    test_all_required_bridge_statuses_appear()
    test_supporting_artifact_paths_exist()
    test_table_includes_theorem_1_and_theorem_2_objects()
    test_positive_partial_and_negative_classifications()
    test_manifest_has_required_columns()
    print("all quotient-family bridge table tests passed")
