# created: 2026-05-11T19:40:00Z
# cycle: 15
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-EXP-1

"""Verify DC-005 trajectory-reuse artifacts are ready for conductor merge."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "data" / "dc005_merge_verification_results.csv"

CSV_ARTIFACTS = {
    "experiment_specs": ROOT / "data" / "measurement_experiment_specs.csv",
    "required_fields": ROOT / "data" / "measurement_required_fields.csv",
    "thresholds": ROOT / "data" / "measurement_thresholds.csv",
    "claim_update_matrix": ROOT / "data" / "measurement_claim_update_matrix.csv",
    "synthetic_probe_results": ROOT / "data" / "measurement_synthetic_probe_results.csv",
}

REQUIRED_TRJ_IDS = {
    "TRJ-001",
    "TRJ-002",
    "TRJ-003",
    "TRJ-004",
    "TRJ-005",
    "TRJ-006",
    "TRJ-007",
}

REQUIRED_THRESHOLDS = {
    "C_to_B_trajectory_reuse",
    "C_to_A_trajectory_reuse",
    "p_survive_min",
    "p_verifier_reuse_min",
}

REQUIRED_FIELDS = {
    "trajectory_node_id",
    "replay_authorization_scope",
    "verifier_evidence_hash",
    "retention_hold_state",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f"missing artifact: {path.relative_to(ROOT)}")
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    if not fieldnames:
        raise ValueError(f"empty or headerless CSV: {path.relative_to(ROOT)}")
    if not rows:
        raise ValueError(f"CSV has no data rows: {path.relative_to(ROOT)}")
    return fieldnames, rows


def add_result(
    results: list[dict[str, str]],
    check_id: str,
    artifact: str,
    expected: str,
    observed: str,
    passed: bool,
) -> None:
    results.append(
        {
            "check_id": check_id,
            "artifact": artifact,
            "expected": expected,
            "observed": observed,
            "status": "PASS" if passed else "FAIL",
        }
    )


def split_field_tokens(rows: list[dict[str, str]]) -> set[str]:
    tokens: set[str] = set()
    for row in rows:
        for token in row.get("field", "").split(";"):
            token = token.strip()
            if token:
                tokens.add(token)
    return tokens


def main() -> int:
    results: list[dict[str, str]] = []
    loaded: dict[str, list[dict[str, str]]] = {}

    for name, path in CSV_ARTIFACTS.items():
        try:
            fieldnames, rows = read_csv(path)
            loaded[name] = rows
            add_result(
                results,
                f"{name}_parseable",
                str(path.relative_to(ROOT)),
                "exists with header and at least one data row",
                f"{len(rows)} rows; columns={';'.join(fieldnames)}",
                True,
            )
        except Exception as exc:  # precise message is emitted in observed.
            add_result(
                results,
                f"{name}_parseable",
                str(path.relative_to(ROOT)),
                "exists with header and at least one data row",
                str(exc),
                False,
            )

    specs = loaded.get("experiment_specs", [])
    trj_seen = {row.get("experiment_id", "").split("-")[0] + "-" + row.get("experiment_id", "").split("-")[1] for row in specs if row.get("experiment_id", "").startswith("TRJ-")}
    missing_trj = sorted(REQUIRED_TRJ_IDS - trj_seen)
    add_result(
        results,
        "required_trj_ids",
        "data/measurement_experiment_specs.csv",
        ";".join(sorted(REQUIRED_TRJ_IDS)),
        "missing=" + (";".join(missing_trj) if missing_trj else "none"),
        not missing_trj,
    )

    thresholds = {row.get("threshold_id", "") for row in loaded.get("thresholds", [])}
    missing_thresholds = sorted(REQUIRED_THRESHOLDS - thresholds)
    add_result(
        results,
        "required_thresholds",
        "data/measurement_thresholds.csv",
        ";".join(sorted(REQUIRED_THRESHOLDS)),
        "missing=" + (";".join(missing_thresholds) if missing_thresholds else "none"),
        not missing_thresholds,
    )

    field_tokens = split_field_tokens(loaded.get("required_fields", []))
    missing_fields = sorted(REQUIRED_FIELDS - field_tokens)
    add_result(
        results,
        "required_fields",
        "data/measurement_required_fields.csv",
        ";".join(sorted(REQUIRED_FIELDS)),
        "missing=" + (";".join(missing_fields) if missing_fields else "none"),
        not missing_fields,
    )

    dc006_rows: list[str] = []
    for name, rows in loaded.items():
        for row_num, row in enumerate(rows, start=2):
            if row.get("deferred_constant") != "DC-006":
                continue
            experiment_id = row.get("experiment_id", "")
            threshold_id = row.get("threshold_id", "")
            if experiment_id.startswith("TRJ-") or threshold_id in REQUIRED_THRESHOLDS:
                dc006_rows.append(f"{CSV_ARTIFACTS[name].relative_to(ROOT)}:{row_num}")
    add_result(
        results,
        "no_dc006_measurement_rows",
        "data/measurement_*.csv",
        "no deferred_constant=DC-006 rows reuse DC-005 TRJ experiment IDs or thresholds",
        "violations=" + (";".join(dc006_rows) if dc006_rows else "none"),
        not dc006_rows,
    )

    authorization_gate_rows = [
        row
        for row in loaded.get("required_fields", [])
        if "authorization_gate_not_overhead_measurement" in row.get("scope_boundary", "")
    ]
    add_result(
        results,
        "authorization_gate_boundary",
        "data/measurement_required_fields.csv",
        "authorization/provenance fields are validity gates, not overhead magnitude rows",
        f"{len(authorization_gate_rows)} matching scope-boundary rows",
        len(authorization_gate_rows) >= 1,
    )

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check_id", "artifact", "expected", "observed", "status"],
        )
        writer.writeheader()
        writer.writerows(results)

    failed = [result for result in results if result["status"] != "PASS"]
    for result in results:
        print(
            f"{result['status']} {result['check_id']} "
            f"artifact={result['artifact']} observed={result['observed']}"
        )
    print(f"wrote {RESULTS_PATH.relative_to(ROOT)}")

    if failed:
        print(f"FAIL {len(failed)} DC-005 merge-readiness checks failed", file=sys.stderr)
        return 1
    print(f"PASS {len(results)} DC-005 merge-readiness checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
