# created: 2026-05-11T14:36:00Z
# cycle: 7
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRACE-1

"""Validate synthetic trace v2 and its deliberate invalid fixtures."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_COLUMNS = [
    "trace_id", "run_id", "workload_class", "time_step", "event_type", "object_id",
    "object_class", "size_units", "tier", "parent_object_id", "trajectory_node_id",
    "branch_id", "provenance_id", "reuse_distance", "reuse_probability_hint",
    "correctness_sensitive", "recompute_cost_hint", "loss_cost_hint", "durability_horizon",
    "verifier_id", "merge_state", "source_version", "invalidation_signal", "evidence_label",
]

VALID_EVENT_TYPES = {
    "run_start", "object_create", "object_access", "object_update", "object_place",
    "object_migrate", "object_evict", "object_recompute", "branch_fork", "branch_discard",
    "branch_merge", "verifier_start", "verifier_result", "tool_call_start", "tool_call_result",
    "workspace_write", "workspace_compact", "semantic_cache_lookup", "semantic_cache_insert",
    "run_end",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        fields = ["check_name", "status", "detail", "evidence_label"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def nonempty(row: dict[str, str], field: str) -> bool:
    return str(row.get(field, "")).strip() != ""


def validate_rows(rows: list[dict[str, str]], label: str) -> tuple[list[dict[str, object]], list[str]]:
    results: list[dict[str, object]] = []
    errors: list[str] = []

    columns = set(rows[0].keys()) if rows else set()
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing_cols:
        errors.append(f"missing_columns:{','.join(missing_cols)}")
    results.append({"check_name": f"{label}:required_columns", "status": "fail" if missing_cols else "pass", "detail": ";".join(missing_cols) or "all required columns present", "evidence_label": "synthetic"})

    births: dict[str, int] = {}
    deaths: dict[str, int] = {}
    branches: set[str] = set()
    verifiers: dict[str, int] = {}
    last_time_by_run: defaultdict[str, int] = defaultdict(lambda: -1)
    event_type_seen = set()

    for i, row in enumerate(rows, start=2):
        event_type = row.get("event_type", "")
        event_type_seen.add(event_type)
        run_id = row.get("run_id", "")
        try:
            t = int(row.get("time_step", ""))
        except ValueError:
            errors.append(f"row_{i}:bad_time_step")
            continue
        if t < last_time_by_run[run_id]:
            errors.append(f"row_{i}:nonmonotone_time")
        last_time_by_run[run_id] = max(last_time_by_run[run_id], t)
        if event_type not in VALID_EVENT_TYPES:
            errors.append(f"row_{i}:bad_event_type:{event_type}")

        oid = row.get("object_id", "")
        if event_type == "object_create":
            if not oid or not nonempty(row, "object_class") or not nonempty(row, "size_units"):
                errors.append(f"row_{i}:bad_object_create")
            births[oid] = t
        elif event_type in {"object_access", "object_update", "object_place", "object_migrate", "object_evict", "object_recompute", "tool_call_result", "workspace_write", "workspace_compact", "semantic_cache_lookup", "semantic_cache_insert"}:
            if oid and oid not in births:
                errors.append(f"row_{i}:object_event_before_birth:{event_type}:{oid}")
            if oid and oid in deaths and event_type != "object_evict" and t >= deaths[oid]:
                errors.append(f"row_{i}:object_event_after_evict:{event_type}:{oid}")
        if event_type == "object_evict" and oid:
            if oid not in births:
                errors.append(f"row_{i}:evict_before_birth:{oid}")
            elif t < births[oid]:
                errors.append(f"row_{i}:evict_time_before_birth:{oid}")
            deaths[oid] = t

        branch_id = row.get("branch_id", "")
        if event_type == "branch_fork":
            if not branch_id:
                errors.append(f"row_{i}:branch_fork_missing_branch_id")
            branches.add(branch_id)
        if event_type in {"branch_merge", "branch_discard"}:
            if branch_id not in branches:
                errors.append(f"row_{i}:branch_close_without_fork:{branch_id}")
            if row.get("merge_state", "") not in {"merged", "discarded"}:
                errors.append(f"row_{i}:bad_branch_merge_state")

        verifier_id = row.get("verifier_id", "")
        if event_type == "verifier_start":
            if not verifier_id:
                errors.append(f"row_{i}:verifier_start_missing_id")
            verifiers[verifier_id] = t
        if event_type == "verifier_result":
            if verifier_id not in verifiers:
                errors.append(f"row_{i}:verifier_result_without_start:{verifier_id}")
            elif t < verifiers[verifier_id]:
                errors.append(f"row_{i}:verifier_result_before_start:{verifier_id}")

        if event_type == "workspace_write":
            horizon = int(row.get("durability_horizon") or "0")
            if horizon <= 0:
                errors.append(f"row_{i}:workspace_write_missing_durability_horizon")
            if not nonempty(row, "provenance_id"):
                errors.append(f"row_{i}:workspace_write_missing_provenance")
        if event_type in {"semantic_cache_lookup", "semantic_cache_insert"}:
            if not nonempty(row, "provenance_id"):
                errors.append(f"row_{i}:semantic_cache_missing_provenance")
            if not nonempty(row, "invalidation_signal"):
                errors.append(f"row_{i}:semantic_cache_missing_invalidation_signal")

    represented = sorted(event_type_seen & VALID_EVENT_TYPES)
    results.append({"check_name": f"{label}:event_type_count", "status": "pass" if len(represented) >= 15 else "fail", "detail": str(len(represented)), "evidence_label": "synthetic"})
    results.append({"check_name": f"{label}:event_order_and_references", "status": "pass" if not errors else "fail", "detail": "no critical violations" if not errors else " | ".join(errors[:20]), "evidence_label": "synthetic"})
    return results, errors


def boundary_checks(events: list[dict[str, str]]) -> list[dict[str, object]]:
    summary = read_csv(DATA / "trace_workload_summary.csv")
    dag = {r["workload_class"]: r for r in read_csv(DATA / "trace_branch_dag_metrics.csv")}
    life = read_csv(DATA / "trace_object_lifetimes.csv")
    results = []

    control_ok = all(int(float(dag[w]["max_dag_width"])) == 0 for w in ["single-turn chat control", "batch summarization/offline inference control"])
    results.append({"check_name": "controls_dag_collapsed", "status": "pass" if control_ok else "fail", "detail": str({w: dag[w]["max_dag_width"] for w in dag if "control" in w}), "evidence_label": "synthetic"})

    rag_classes = {r["object_class"] for r in life if r["workload_class"] == "RAG"}
    rag_ok = {"retrieved context", "semantic cache entry"} <= rag_classes and int(float(dag["RAG"]["max_dag_width"])) == 0
    results.append({"check_name": "rag_reuse_without_trajectory", "status": "pass" if rag_ok else "fail", "detail": "; ".join(sorted(rag_classes)), "evidence_label": "synthetic"})

    agentic = ["code-agent loop", "verification-heavy", "multi-agent branch/merge"]
    agentic_ok = True
    details = {}
    for workload in agentic:
        classes = {r["object_class"] for r in life if r["workload_class"] == workload}
        share = next(float(r["non_kv_object_size_share"]) for r in summary if r["workload_class"] == workload)
        ok = bool({"tool output", "verifier state", "trajectory log"} & classes) and share > 0.1
        details[workload] = f"classes={len(classes)} share={share}"
        agentic_ok = agentic_ok and ok
    results.append({"check_name": "agentic_non_kv_state_present", "status": "pass" if agentic_ok else "fail", "detail": " | ".join(f"{k}:{v}" for k, v in details.items()), "evidence_label": "synthetic"})

    return results


def main() -> None:
    events_path = DATA / "agentic_trace_events_v2.csv"
    invalid_path = DATA / "trace_invalid_cases.csv"
    events = read_csv(events_path)
    invalid = read_csv(invalid_path)

    rows, errors = validate_rows(events, "positive_trace")
    invalid_rows, invalid_errors = validate_rows(invalid, "invalid_fixtures")
    intended = len(invalid_errors) >= 5
    invalid_rows.append({"check_name": "invalid_fixtures:intended_failures", "status": "pass" if intended else "fail", "detail": " | ".join(invalid_errors[:20]), "evidence_label": "synthetic"})
    rows.extend(boundary_checks(events))
    rows.extend(invalid_rows)
    write_csv(DATA / "trace_schema_validation.csv", rows)

    critical_errors = errors + ([] if intended else ["invalid fixtures did not fail"])
    print(f"positive_events={len(events)}")
    print(f"positive_errors={len(errors)}")
    print(f"invalid_fixture_errors={len(invalid_errors)}")
    for err in invalid_errors[:10]:
        print(f"invalid_fixture_error {err}")
    if critical_errors:
        print("CRITICAL " + " | ".join(critical_errors[:20]), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
