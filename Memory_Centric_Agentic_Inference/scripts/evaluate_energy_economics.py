#!/usr/bin/env python3
# created: 2026-05-11T21:46:00Z
# cycle: 16
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ENERGY-1
"""Evaluate synthetic energy/economics and CXL contention sensitivity."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOC = ROOT / "memory-centric-agentic"

REQUIRED_INPUTS = [
    DATA / "calibration_deferred_constants.csv",
    DATA / "calibration_memory_tiers.csv",
    DATA / "cost_model_scenarios.csv",
    DATA / "queueing_reversal_thresholds.csv",
    DATA / "queueing_architecture_winners.csv",
    DATA / "runtime_workload_summary.csv",
    DATA / "synthesis_architecture_decision_matrix.csv",
    DATA / "synthesis_claims_register.csv",
    DATA / "measurement_thresholds.csv",
]

OPTION_LABELS = {
    "A": "A_conventional_request_model_kv_serving",
    "B": "B_memory_object_aware_runtime",
    "C": "C_trajectory_dag_memory_fabric",
}

ENERGY_SETTINGS = {
    "DC001_zero_energy": 0.0,
    "DC001_equal_tier_low": 0.015,
    "DC001_memory_gap_medium": 0.04,
    "DC001_memory_gap_high": 0.09,
}

DOLLAR_SETTINGS = {
    "dollar_zero": 0.0,
    "dollar_low": 0.01,
    "dollar_medium": 0.025,
    "dollar_high": 0.05,
}

CXL_SETTINGS = {
    "DC002_local_like_p50": 0.5,
    "DC002_moderate_p95": 2.0,
    "DC002_tail_p99": 8.0,
    "DC002_pathological_p99": 1_000.0,
}

OBJECTS_BY_OPTION = {
    "A": "model/KV hot path",
    "B": "retrieved context; prefix cache; semantic cache entry; tool output",
    "C": "branch state; verifier state; trajectory log; durable workspace",
}

SCENARIO_TO_WORKLOAD = {
    "single-turn chat control": "single-turn chat control",
    "batch summarization/offline inference control": "batch summarization/offline inference control",
    "RAG with retrieved-context reuse": "RAG",
    "code-agent loop with tool outputs and durable workspace": "code-agent loop",
    "verification-heavy agent": "verification-heavy",
    "multi-agent branch/merge run": "multi-agent branch/merge",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        lowered = {str(v).strip().lower() for v in row.values()}
        if "placeholder" in lowered or "replace_me" in lowered:
            raise ValueError(f"invalid placeholder token in {path}: {row}")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def fnum(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, "") or default)
    except ValueError:
        return default


def option_short(option: str) -> str:
    if option.startswith("A_"):
        return "A"
    if option.startswith("B_"):
        return "B"
    if option.startswith("C_"):
        return "C"
    return option[:1]


def load_inputs() -> dict[str, list[dict[str, str]]]:
    inputs = {path.name: read_csv(path) for path in REQUIRED_INPUTS}
    deferred_ids = {r["constant_id"] for r in inputs["calibration_deferred_constants.csv"]}
    missing = {"DC-001", "DC-002"} - deferred_ids
    if missing:
        raise ValueError(f"missing deferred constants: {sorted(missing)}")
    return inputs


def build_joined(inputs: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    cost = {SCENARIO_TO_WORKLOAD.get(r["scenario"], r["scenario"]): r for r in inputs["cost_model_scenarios.csv"]}
    runtime = {r["workload_class"]: r for r in inputs["runtime_workload_summary.csv"]}
    queue = {r["workload_class"]: r for r in inputs["queueing_architecture_winners.csv"]}
    out = []
    for syn in inputs["synthesis_architecture_decision_matrix.csv"]:
        wl = syn["workload_class"]
        if wl not in cost or wl not in runtime or wl not in queue:
            raise ValueError(f"missing joined input for workload {wl}")
        out.append({"syn": syn, "cost": cost[wl], "runtime": runtime[wl], "queue": queue[wl]})
    return out


def retained_value(item: dict[str, object], option: str) -> float:
    runtime = item["runtime"]
    syn = item["syn"]
    assert isinstance(runtime, dict) and isinstance(syn, dict)
    if option == "A":
        return 0.0
    if option == "B":
        return max(0.0, fnum(runtime, "option_b_net_value"))
    option_c = max(0.0, fnum(runtime, "option_c_net_value"))
    return max(option_c, max(0.0, fnum(syn, "visible_retained_value_proxy")) - 2.0)


def synthetic_net(
    item: dict[str, object],
    option: str,
    energy_scale: float,
    dollar_scale: float,
    cxl_penalty: float,
) -> tuple[float, float]:
    cost = item["cost"]
    runtime = item["runtime"]
    assert isinstance(cost, dict) and isinstance(runtime, dict)
    retained = retained_value(item, option)
    energy_proxy = fnum(cost, "energy_proxy_score")
    dollar_proxy = fnum(cost, "dollar_proxy_score")
    retained_bytes = fnum(runtime, "retained_size_units")
    moved_avoided = energy_proxy * {"A": 0.0, "B": 0.35, "C": 0.55}[option]
    residency_charge = retained_bytes * {"A": 0.0, "B": 0.003, "C": 0.0045}[option]
    validation_charge = {"A": 0.0, "B": 0.9, "C": 1.8}[option]
    contention_charge = cxl_penalty * {"A": 0.0, "B": 1.0, "C": 1.6}[option]
    net_energy = retained + moved_avoided * energy_scale - residency_charge * energy_scale - validation_charge - contention_charge
    net_dollar = retained + dollar_proxy * dollar_scale - residency_charge * dollar_scale - validation_charge - contention_charge
    return round(net_energy, 4), round(net_dollar, 4)


def decide(option: str, net_energy: float, net_dollar: float, has_non_kv_value: bool) -> str:
    if option == "A":
        return "keep_option_A"
    if not has_non_kv_value:
        return "collapse_to_A_no_non_kv_retained_value"
    if net_energy <= 0 and net_dollar <= 0:
        return "collapse_to_A_economics_nonpositive"
    if net_energy <= 0 or net_dollar <= 0:
        return "downgrade_claim_energy_or_dollar_not_both"
    return "support_under_synthetic_sensitivity"


def scenario_rows(joined: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for item in joined:
        syn = item["syn"]
        cost = item["cost"]
        runtime = item["runtime"]
        assert isinstance(syn, dict) and isinstance(cost, dict) and isinstance(runtime, dict)
        wl = syn["workload_class"]
        for option in ["A", "B", "C"]:
            has_value = option == "A" or retained_value(item, option) > 0
            for e_name, e_scale in ENERGY_SETTINGS.items():
                d_name = e_name.replace("DC001_", "dollar_linked_")
                d_scale = DOLLAR_SETTINGS["dollar_zero"] if e_scale == 0 else min(0.05, e_scale * 0.55)
                for c_name, c_penalty in CXL_SETTINGS.items():
                    net_e, net_d = synthetic_net(item, option, e_scale, d_scale, c_penalty)
                    rows.append(
                        {
                            "scenario_id": f"{wl}|{option}|{e_name}|{c_name}",
                            "workload_class": wl,
                            "architecture_option": OPTION_LABELS[option],
                            "bytes_moved_proxy": round(fnum(cost, "energy_proxy_score") * {"A": 0.0, "B": 0.35, "C": 0.55}[option], 4),
                            "bytes_retained_proxy": fnum(runtime, "retained_size_units") if option != "A" else 0.0,
                            "recompute_proxy": retained_value(item, option),
                            "energy_per_byte_setting": e_name,
                            "dollar_per_byte_setting": d_name,
                            "cxl_latency_setting": c_name,
                            "net_energy_proxy": net_e,
                            "net_dollar_proxy": net_d,
                            "decision": decide(option, net_e, net_d, has_value),
                            "evidence_label": "synthetic_sensitivity",
                        }
                    )
    return rows


def choose_option(item: dict[str, object], e_scale: float, d_scale: float, c_penalty: float) -> tuple[str, dict[str, tuple[float, float]]]:
    scores: dict[str, tuple[float, float]] = {}
    for opt in ["A", "B", "C"]:
        scores[opt] = synthetic_net(item, opt, e_scale, d_scale, c_penalty)
    viable = {}
    for opt, vals in scores.items():
        if opt != "A" and retained_value(item, opt) <= 0:
            viable[opt] = -1_000_000.0
        else:
            viable[opt] = min(vals)
    best = max(viable, key=lambda opt: viable[opt])
    if viable[best] <= 0:
        best = "A"
    return best, scores


def sensitivity_rows(joined: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for item in joined:
        syn = item["syn"]
        assert isinstance(syn, dict)
        before = option_short(syn["final_option"])
        for e_name, e_scale in ENERGY_SETTINGS.items():
            for c_name, c_penalty in CXL_SETTINGS.items():
                after, scores = choose_option(item, e_scale, min(0.05, e_scale * 0.55), c_penalty)
                if e_scale == 0.0 and after != "A":
                    collapse = "DC-001 zero removes energy/dollar evidence; retained-value-only claim is not economic support"
                elif c_penalty >= 8.0 and before in {"B", "C"} and after != before:
                    collapse = "DC-002 tail contention exceeds retained-value margin"
                elif after == before:
                    collapse = "no synthetic collapse under this sweep"
                else:
                    collapse = "synthetic net value changes option after energy/contention charges"
                updates = "CL-012 stays speculative; "
                if before in {"B", "C"}:
                    updates += "CL-004 contention sensitivity updated"
                if before == "C":
                    updates += "; CL-005 DAG/contention sensitivity updated"
                rows.append(
                    {
                        "workload_class": syn["workload_class"],
                        "baseline_option": syn["final_option"],
                        "tested_option": OPTION_LABELS[before],
                        "dc001_setting": e_name,
                        "dc002_setting": c_name,
                        "option_before": before,
                        "option_after": after,
                        "collapse_reason": collapse,
                        "claim_updates": updates,
                        "evidence_label": "synthetic_sensitivity",
                    }
                )
    return rows


def cxl_rows(joined: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    percentiles = [("p50", 0.5), ("p95", 2.0), ("p99", 8.0), ("p99_pathological", 1_000.0)]
    for item in joined:
        syn = item["syn"]
        runtime = item["runtime"]
        assert isinstance(syn, dict) and isinstance(runtime, dict)
        wl = syn["workload_class"]
        for opt, object_class in [("B", OBJECTS_BY_OPTION["B"]), ("C", OBJECTS_BY_OPTION["C"])]:
            margin = retained_value(item, opt)
            threshold = round(max(0.0, margin / (1.0 if opt == "B" else 1.6)), 4)
            for pct, setting in percentiles:
                decision = "warm_tier_helps" if margin > 0 and setting < threshold else "downgrade_warm_tier"
                rows.append(
                    {
                        "threshold_id": f"DC002-{wl}-{opt}-{pct}",
                        "workload_class": wl,
                        "object_class": object_class,
                        "placement_tier": "CXL_or_pooled_memory_warm_tier",
                        "latency_percentile": pct,
                        "contention_setting": setting,
                        "benefit_margin": round(margin, 4),
                        "collapse_threshold": threshold,
                        "decision": decision,
                        "evidence_label": "synthetic_sensitivity",
                    }
                )
    return rows


def claim_update_rows(inputs: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    claims = {r["claim_id"]: r for r in inputs["synthesis_claims_register.csv"]}
    selected = ["CL-001", "CL-002", "CL-003", "CL-004", "CL-005", "CL-009", "CL-012"]
    rows = []
    for cid in selected:
        claim = claims[cid]
        if cid == "CL-012":
            after = "speculative"
            update = "DC-001/DC-002 sensitivity narrows thresholds but does not calibrate economic value"
            trigger = "replace with measured per-tier byte energy, price, and CXL contention telemetry"
            evidence = "speculative"
        elif cid in {"CL-004", "CL-005"}:
            after = "simulated"
            update = "contention threshold rows expose where queue/tail latency reverses architecture choice"
            trigger = "measured metadata, DAG, pooled-memory p50/p95/p99 below reversal thresholds"
            evidence = "synthetic_sensitivity"
        elif cid == "CL-001":
            after = claim["claim_type"]
            update = "control rows remain Option A unless positive non-KV retained value is present"
            trigger = "control workload shows safe non-KV retained value with positive net energy and dollar"
            evidence = "derived"
        elif cid == "CL-009":
            after = claim["claim_type"]
            update = "unsafe reuse still forces zero positive value before economics are counted"
            trigger = "unsafe-pass rate is zero and validation overhead is measured"
            evidence = "validated_artifact"
        else:
            after = claim["claim_type"]
            update = "energy/contention sweeps add downgrade conditions to existing synthetic retained-value claim"
            trigger = "measured DC-001/DC-002 values keep net value positive under security gates"
            evidence = "synthetic_sensitivity"
        rows.append(
            {
                "claim_id": cid,
                "claim_before": claim["claim_type"],
                "claim_after": after,
                "dc001_effect": update,
                "dc002_effect": trigger,
                "decision": "calibration_ready" if cid != "CL-012" else "remain_speculative_until_measured",
                "evidence_label": evidence,
            }
        )
    return rows


def measurement_rows() -> list[dict[str, object]]:
    return [
        {
            "measurement_id": "DC001-BYTE-ENERGY-001",
            "quantity": "per-tier joules per byte moved and retained",
            "required_telemetry": "bytes by source tier, destination tier, object class, reuse decision, accelerator/host power counters, wall-clock interval",
            "aggregation_unit": "workload_class x object_class x placement_tier",
            "supports_if": "net measured energy saved exceeds measurement noise and validation/coordination energy",
            "falsifies_if": "energy delta is below noise or arithmetic/system overhead dominates byte-movement savings",
            "updates_claim_ids": "CL-012; CL-002; CL-003",
        },
        {
            "measurement_id": "DC001-DOLLAR-001",
            "quantity": "dollar cost per retained byte and moved byte",
            "required_telemetry": "tier occupancy time, transfer volume, capacity reservation, eviction/recompute events, billing or internal chargeback rates",
            "aggregation_unit": "tenant x workload_class x architecture_option",
            "supports_if": "saved recompute or transfer cost exceeds residency, capacity, and policy overhead",
            "falsifies_if": "warm retention increases capacity reservation without reducing recompute or latency cost",
            "updates_claim_ids": "CL-012",
        },
        {
            "measurement_id": "DC002-CXL-CONTENTION-001",
            "quantity": "CXL or pooled-memory p50/p95/p99 latency under contention",
            "required_telemetry": "per-object warm-tier hit latency, queue depth, tenant concurrency, migration wait, p50/p95/p99 by object size",
            "aggregation_unit": "placement_tier x latency_percentile x workload_class",
            "supports_if": "tail latency remains below retained-value time-equivalent margin",
            "falsifies_if": "p95 or p99 contention exceeds retained-value margin for reusable objects",
            "updates_claim_ids": "CL-004; CL-005; CL-012",
        },
        {
            "measurement_id": "SECURITY-GATE-ENERGY-001",
            "quantity": "authorized safe reuse rate before energy credit",
            "required_telemetry": "tenant scope, cache salt, provenance pointer, source version, replay authorization, verifier hash, unsafe-pass rate",
            "aggregation_unit": "reuse_attempt x object_class",
            "supports_if": "unsafe-pass rate is zero and retained objects pass freshness/provenance gates",
            "falsifies_if": "any unsafe or unauthorized reuse is needed to make energy savings positive",
            "updates_claim_ids": "CL-009; CL-012",
        },
    ]


def write_doc() -> None:
    path = DOC / "energy_economics_contention.md"
    text = """---
created: 2026-05-11T21:46:00Z
cycle: 16
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-ENERGY-1
---

# Energy, Economics, and Contention Falsification Harness

## Thesis and Limits

`derived`: Memory-centric placement has an energy or dollar case only when avoided recompute and avoided movement exceed added residency, transfer, validation, coordination, and contention cost:

`NetEnergyValue = E_recompute_avoided + E_movement_avoided - E_residency - E_transfer - E_validation - E_coordination`.

`simulated`: The CSV harness sweeps synthetic DC-001 per-byte energy/cost settings and DC-002 CXL/pooled-memory contention settings over the validated runtime, queueing, cost, and synthesis artifacts. The numbers are dimensionless proxies; they are useful for locating reversals, not for claiming measured savings.

`sourced_from_existing_calibration`: Existing calibration rows provide public capability ranges for HBM/GPU memory, interconnects, PCIe, CXL capability, NVMe, and workload/cache evidence, but DC-001 and DC-002 remain deferred because public sources do not expose comparable deployed per-byte energy or pooled-memory tail latency under contention.

`measurement_design`: The measurement table defines telemetry needed to replace synthetic rows: per-tier byte movement/residency, power counters, tier occupancy, chargeback, CXL p50/p95/p99 under contention, and security/provenance gate outcomes.

`speculative`: CL-012 remains speculative after this cycle. Sensitivity rows can say which measurements would support or falsify the claim, but they do not convert the claim to calibrated evidence.

## DC-001 and DC-002 Effects

`derived`: If DC-001 is zero, the energy/economics claim vanishes and only latency, capacity, and correctness arguments remain. Equal per-tier energy weakens byte-placement claims because retained value must come from recompute avoidance or capacity pressure rather than energy gradients.

`simulated`: High DC-002 CXL tail latency downgrades warm-tier placement when the contention setting exceeds the retained-value time-equivalent margin. This updates CL-004 and CL-005 by adding explicit CXL/contention collapse thresholds to the earlier queueing reversal claims.

`simulated`: Option A controls remain Option A under the sweeps unless positive non-KV retained value is present. Option B/C rows require safe retained value before any energy or dollar credit is counted.

`measurement_design`: Production adoption needs telemetry that joins bytes, object class, tier, reuse decision, power, queueing, and safety gates. Energy savings do not count when reuse is unsafe, unauthorized, stale, or below measurement noise.

## Hard Downgrade Rules

`derived`: Downgrade energy/economics claims if measured energy savings are below instrument noise, arithmetic dominates total energy, or retained bytes increase capacity reservation without reducing recompute, movement, or latency cost.

`derived`: Downgrade warm-tier placement if CXL or pooled-memory p95/p99 exceeds the retained-value margin plus migration and policy queue costs.

`derived`: Downgrade Option B/C to Option A when safe non-KV retained value is absent. Unsafe reuse forces positive retained value to zero before energy or dollar savings are counted.

`measurement_design`: CL-012 can move out of speculative only after DC-001 and DC-002 telemetry is measured on the target hardware and workload mix.

## Figures

![Option A/B/C robustness under per-byte energy/cost sweeps.](../data/energy_architecture_sensitivity.png)

![CXL/pooled-memory latency thresholds where warm-tier placement reverses.](../data/cxl_contention_thresholds.png)

![Synthesis claims updated by DC-001/DC-002 measurement outcomes.](../data/energy_claim_update_map.png)
"""
    path.write_text(text)
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    inputs = load_inputs()
    joined = build_joined(inputs)
    write_csv(
        DATA / "energy_economics_scenarios.csv",
        scenario_rows(joined),
        [
            "scenario_id",
            "workload_class",
            "architecture_option",
            "bytes_moved_proxy",
            "bytes_retained_proxy",
            "recompute_proxy",
            "energy_per_byte_setting",
            "dollar_per_byte_setting",
            "cxl_latency_setting",
            "net_energy_proxy",
            "net_dollar_proxy",
            "decision",
            "evidence_label",
        ],
    )
    write_csv(
        DATA / "energy_architecture_sensitivity.csv",
        sensitivity_rows(joined),
        [
            "workload_class",
            "baseline_option",
            "tested_option",
            "dc001_setting",
            "dc002_setting",
            "option_before",
            "option_after",
            "collapse_reason",
            "claim_updates",
            "evidence_label",
        ],
    )
    write_csv(
        DATA / "cxl_contention_thresholds.csv",
        cxl_rows(joined),
        [
            "threshold_id",
            "workload_class",
            "object_class",
            "placement_tier",
            "latency_percentile",
            "contention_setting",
            "benefit_margin",
            "collapse_threshold",
            "decision",
            "evidence_label",
        ],
    )
    write_csv(
        DATA / "energy_claim_update_matrix.csv",
        claim_update_rows(inputs),
        [
            "claim_id",
            "claim_before",
            "claim_after",
            "dc001_effect",
            "dc002_effect",
            "decision",
            "evidence_label",
        ],
    )
    write_csv(
        DATA / "energy_measurement_requirements.csv",
        measurement_rows(),
        [
            "measurement_id",
            "quantity",
            "required_telemetry",
            "aggregation_unit",
            "supports_if",
            "falsifies_if",
            "updates_claim_ids",
        ],
    )
    write_doc()


if __name__ == "__main__":
    main()
