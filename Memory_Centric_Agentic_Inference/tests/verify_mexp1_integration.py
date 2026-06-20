# created: 2026-05-11T21:20:00Z
# cycle: 15
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-EXP-1

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPERIMENTS = ROOT / "memory-centric-agentic" / "experiments"


def read_csv(name):
    with (DATA / name).open(newline="") as f:
        return list(csv.DictReader(f))


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL {message}")
    print(f"PASS {message}")


def main():
    specs = read_csv("measurement_experiment_specs.csv")
    fields = read_csv("measurement_required_fields.csv")
    thresholds = read_csv("measurement_thresholds.csv")
    claims = read_csv("measurement_claim_update_matrix.csv")
    probes = read_csv("measurement_synthetic_probe_results.csv")

    for artifact in [
        "trajectory_reuse_measurement_plan.md",
        "provenance_overhead_measurement_plan.md",
        "cache_durable_risk_measurement_plan.md",
    ]:
        require((EXPERIMENTS / artifact).exists(), f"{artifact} exists")

    spec_ids = {row["experiment_id"] for row in specs}
    threshold_ids = {row["threshold_id"] for row in thresholds}
    constants = {
        name: {row["deferred_constant"] for row in rows}
        for name, rows in [
            ("specs", specs),
            ("fields", fields),
            ("thresholds", thresholds),
            ("claims", claims),
            ("probes", probes),
        ]
    }

    require({"DC-003", "DC-004", "DC-005", "DC-006"}.issubset(constants["specs"]), "all deferred constants represented in specs")
    require({"DC-003", "DC-004", "DC-005", "DC-006"}.issubset(constants["thresholds"]), "all deferred constants represented in thresholds")

    require(all(f"TRJ-{i:03d}" in " ".join(spec_ids) for i in range(1, 8)), "TRJ-001 through TRJ-007 present")
    require(all(f"CDR-SEM-{i:03d}" in spec_ids for i in range(1, 7)), "CDR-SEM-001 through CDR-SEM-006 present")
    require(all(f"CDR-DUR-{i:03d}" in spec_ids for i in range(1, 6)), "CDR-DUR-001 through CDR-DUR-005 present")
    require(all(f"EXP-PROV-" in exp for exp in [
        "EXP-PROV-MICRO-001",
        "EXP-PROV-REPLAY-002",
        "EXP-PROV-ISOLATION-003",
        "EXP-PROV-LINEAGE-004",
        "EXP-PROV-VERIFIER-005",
        "EXP-PROV-RETENTION-006",
        "EXP-PROV-POINTER-007",
    ] if exp in spec_ids), "EXP-PROV-* rows parse")
    require({
        "EXP-PROV-MICRO-001",
        "EXP-PROV-REPLAY-002",
        "EXP-PROV-ISOLATION-003",
        "EXP-PROV-LINEAGE-004",
        "EXP-PROV-VERIFIER-005",
        "EXP-PROV-RETENTION-006",
        "EXP-PROV-POINTER-007",
    }.issubset(spec_ids), "EXP-PROV-001 through EXP-PROV-007 present")

    require({"T-PROV-B-001", "T-PROV-C-002", "T-PROV-UNSAFE-003", "T-PROV-POINTER-004"}.issubset(threshold_ids), "DC-006 thresholds present")
    require(any("validation_queue_wait" in row["field"] for row in fields if row["deferred_constant"] == "DC-006"), "DC-006 validation timing fields present")
    require(any(row["deferred_constant"] == "DC-006" and row["claim_id"] == "CL-009" for row in claims), "DC-006 safety claim update present")
    require(any(row["deferred_constant"] == "DC-006" and row["evidence_status"] == "synthetic_mechanism_probe" for row in probes), "DC-006 synthetic probes present")

    for name, rows in [
        ("specs", specs),
        ("fields", fields),
        ("thresholds", thresholds),
        ("claims", claims),
        ("probes", probes),
    ]:
        require(all("placeholder" not in str(row).lower() and "replace_me" not in str(row).lower() for row in rows), f"{name} has no placeholder tokens")


if __name__ == "__main__":
    main()
