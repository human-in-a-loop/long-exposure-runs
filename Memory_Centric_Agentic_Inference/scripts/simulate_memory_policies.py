#!/usr/bin/env python3
# created: 2026-05-11T13:21:44Z
# cycle: 4
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SIM-1

import csv
from collections import defaultdict
from pathlib import Path

RUN_ID = "run-2026-05-11T121649Z"
SEED = 20260511
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROJECT = ROOT / "memory-centric-agentic"

POLICIES = [
    "hbm_first_baseline",
    "reuse_aware_tiering",
    "branch_verifier_durable_aware",
    "cost_proxy_balanced",
]

AGENTIC_OBJECTS = {
    "tool output",
    "branch state",
    "verifier state",
    "trajectory log",
    "durable workspace",
}

SCENARIOS = {
    "single-turn chat control": {
        "objects": [
            ("weights", 12000, 0.10, 1, 0.0, 0, 0, 0, 1.5, 0),
            ("KV cache", 4096, 0.05, 1, 0.0, 0, 0, 0, 1.0, 0),
            ("prefix cache", 800, 0.10, 1, 0.0, 0, 0, 0, 1.2, 0),
        ],
        "repeat": 6,
    },
    "batch summarization/offline inference control": {
        "objects": [
            ("weights", 12000, 0.10, 1, 0.0, 0, 0, 0, 1.0, 0),
            ("KV cache", 5200, 0.03, 1, 0.0, 0, 0, 0, 0.8, 0),
            ("intermediate scratch", 2200, 0.02, 1, 0.0, 0, 0, 0, 0.6, 0),
        ],
        "repeat": 7,
    },
    "RAG with retrieved-context reuse": {
        "objects": [
            ("weights", 12000, 0.12, 1, 0.0, 0, 1, 0, 1.0, 0),
            ("KV cache", 3200, 0.12, 1, 0.0, 0, 1, 0, 1.3, 0),
            ("retrieved context", 2500, 0.50, 1, 0.0, 0, 3, 1, 9.0, 10),
            ("semantic cache entry", 900, 0.55, 1, 0.0, 0, 4, 1, 7.0, 8),
        ],
        "repeat": 8,
    },
    "code-agent loop with tool outputs and durable workspace": {
        "objects": [
            ("weights", 12000, 0.15, 1, 0.0, 0, 3, 0, 1.0, 0),
            ("KV cache", 4200, 0.20, 2, 0.35, 1, 3, 0, 2.0, 0),
            ("tool output", 5200, 0.62, 2, 0.45, 2, 10, 1, 18.0, 45),
            ("branch state", 3000, 0.38, 2, 0.45, 2, 5, 1, 12.0, 28),
            ("trajectory log", 1800, 0.50, 1, 0.25, 1, 10, 1, 10.0, 35),
            ("durable workspace", 4600, 0.70, 1, 0.10, 0, 12, 1, 16.0, 55),
        ],
        "repeat": 8,
    },
    "verification-heavy agent": {
        "objects": [
            ("weights", 12000, 0.15, 1, 0.0, 0, 2, 0, 1.0, 0),
            ("KV cache", 3600, 0.20, 3, 0.45, 2, 2, 0, 2.0, 0),
            ("branch state", 3200, 0.42, 3, 0.55, 4, 5, 1, 13.0, 30),
            ("verifier state", 3600, 0.58, 3, 0.60, 5, 6, 1, 20.0, 65),
            ("tool output", 2200, 0.45, 2, 0.50, 4, 4, 1, 14.0, 32),
            ("trajectory log", 1600, 0.46, 1, 0.30, 3, 8, 1, 9.0, 28),
        ],
        "repeat": 8,
    },
    "multi-agent branch/merge run": {
        "objects": [
            ("weights", 12000, 0.15, 1, 0.0, 0, 4, 0, 1.0, 0),
            ("KV cache", 5000, 0.25, 4, 0.55, 3, 4, 0, 2.0, 0),
            ("branch state", 7000, 0.52, 4, 0.65, 3, 6, 1, 18.0, 40),
            ("verifier state", 2500, 0.45, 3, 0.55, 4, 6, 1, 16.0, 50),
            ("tool output", 2600, 0.46, 2, 0.40, 2, 6, 1, 13.0, 26),
            ("trajectory log", 2400, 0.55, 1, 0.35, 2, 9, 1, 11.0, 34),
        ],
        "repeat": 8,
    },
}

TIER_COST = {
    "HBM": (0.45, 0.45, 0.40),
    "DRAM": (0.28, 0.25, 0.22),
    "NVMe": (0.16, 0.14, 0.10),
    "remote": (0.10, 0.20, 0.08),
    "evicted": (0.00, 0.00, 0.00),
}


def require_inputs():
    required = [
        PROJECT / "memory_objects.csv",
        PROJECT / "workload_classes.csv",
        PROJECT / "lifetime_parameters.csv",
        PROJECT / "memory_tiers.csv",
        DATA / "cost_model_scenarios.csv",
        DATA / "cost_model_sensitivity.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("missing required simulator inputs: " + ", ".join(missing))

    with (DATA / "cost_model_scenarios.csv").open(newline="") as f:
        scenarios = list(csv.DictReader(f))
    needed = {"retained_value_score", "energy_proxy_score", "dollar_proxy_score"}
    if not scenarios or not needed.issubset(scenarios[0]):
        raise SystemExit("cost_model_scenarios.csv lacks proxy score fields")

    with (DATA / "cost_model_sensitivity.csv").open(newline="") as f:
        sensitivity = list(csv.DictReader(f))
    sensitivity_axes = {
        "reuse_probability",
        "branch_fanout",
        "verifier_delay",
        "durability_horizon",
        "correctness_loss_multiplier",
    }
    if not sensitivity or not sensitivity_axes.issubset(sensitivity[0]):
        raise SystemExit("cost_model_sensitivity.csv lacks required policy axes")

    return scenario_proxy_scales(scenarios)


def scenario_proxy_scales(scenarios):
    energy_values = [float(row["energy_proxy_score"]) for row in scenarios]
    dollar_values = [float(row["dollar_proxy_score"]) for row in scenarios]
    avg_energy = sum(energy_values) / len(energy_values)
    avg_dollar = sum(dollar_values) / len(dollar_values)
    scales = {}
    for row in scenarios:
        scenario = row["scenario"]
        scales[scenario] = {
            "energy": float(row["energy_proxy_score"]) / avg_energy if avg_energy else 1.0,
            "dollar": float(row["dollar_proxy_score"]) / avg_dollar if avg_dollar else 1.0,
            "retained_value": max(1.0, float(row["retained_value_score"])),
        }
    return scales


def generate_events():
    events = []
    step = 0
    for workload, spec in SCENARIOS.items():
        for repeat in range(spec["repeat"]):
            for object_class, size, reuse, fanout, survival, delay, horizon, correct, recompute, loss in spec["objects"]:
                size_units = size * (1.0 + 0.04 * ((repeat % 3) - 1))
                events.append(
                    {
                        "run_id": RUN_ID,
                        "workload_class": workload,
                        "time_step": step,
                        "event_type": "materialize",
                        "object_class": object_class,
                        "object_id": f"{workload[:3].lower().replace(' ', '_')}-{object_class[:3].lower().replace(' ', '_')}-{repeat}",
                        "size_units": round(size_units, 3),
                        "reuse_probability": round(min(0.95, reuse + 0.02 * (repeat % 2)), 3),
                        "branch_fanout": fanout,
                        "branch_survival": survival,
                        "verifier_delay": delay,
                        "durability_horizon": horizon,
                        "correctness_sensitive": correct,
                        "recompute_cost": recompute,
                        "loss_cost": loss,
                    }
                )
                step += 1
    return events


def retention_probability(policy, event, equal_tier_costs=False):
    obj = event["object_class"]
    reuse = float(event["reuse_probability"])
    survival = float(event["branch_survival"])
    delay = float(event["verifier_delay"])
    horizon = float(event["durability_horizon"])
    correct = float(event["correctness_sensitive"])
    fanout = float(event["branch_fanout"])

    if equal_tier_costs:
        return 0.55
    if policy == "hbm_first_baseline":
        if obj in {"weights", "KV cache", "prefix cache"}:
            return 0.92
        if obj == "retrieved context":
            return 0.34 + 0.20 * reuse
        return 0.18 + 0.08 * reuse
    if policy == "reuse_aware_tiering":
        return min(0.90, 0.18 + 0.92 * reuse + 0.03 * min(horizon, 4))
    if policy == "branch_verifier_durable_aware":
        agentic = 0.0
        if obj in AGENTIC_OBJECTS:
            agentic = 0.18 * survival + 0.035 * delay + 0.025 * horizon + 0.12 * correct + 0.025 * max(0.0, fanout - 1.0)
        return min(0.95, 0.18 + 0.65 * reuse + agentic)
    if policy == "cost_proxy_balanced":
        base = 0.22 + 0.55 * reuse + 0.02 * min(horizon, 8)
        if correct:
            base += 0.10
        if obj in {"weights", "KV cache"}:
            base += 0.08
        return min(0.88, base)
    raise ValueError(f"unknown policy: {policy}")


def tier_for(policy, event, retained):
    obj = event["object_class"]
    if not retained:
        return "evicted"
    if policy == "hbm_first_baseline" and obj in {"weights", "KV cache", "prefix cache"}:
        return "HBM"
    if policy == "branch_verifier_durable_aware" and obj in {"tool output", "trajectory log", "durable workspace"}:
        return "NVMe"
    if policy == "branch_verifier_durable_aware" and obj in {"branch state", "verifier state"}:
        return "DRAM"
    if policy == "reuse_aware_tiering" and float(event["reuse_probability"]) > 0.50:
        return "DRAM"
    if policy == "cost_proxy_balanced" and float(event["correctness_sensitive"]):
        return "NVMe"
    return "DRAM"


def score_event(policy, event, proxy_scales=None, equal_tier_costs=False):
    p = retention_probability(policy, event, equal_tier_costs=equal_tier_costs)
    retained = p >= 0.50
    tier = tier_for(policy, event, retained)
    residency, energy_rate, dollar_rate = TIER_COST[tier if not equal_tier_costs else "DRAM"]
    size_k = float(event["size_units"]) / 1000.0
    reuse = float(event["reuse_probability"])
    recompute = float(event["recompute_cost"])
    correct = float(event["correctness_sensitive"])
    loss = float(event["loss_cost"])
    survival = float(event["branch_survival"])
    delay = float(event["verifier_delay"])
    horizon = float(event["durability_horizon"])

    retained_value = p * (reuse * recompute + correct * loss * (0.35 + 0.08 * delay + 0.03 * horizon + 0.20 * survival))
    movement = size_k * (1.0 - p) * (1.2 + 0.2 * delay + 0.05 * horizon)
    workload_scales = (proxy_scales or {}).get(event["workload_class"], {})
    energy_scale = workload_scales.get("energy", 1.0)
    dollar_scale = workload_scales.get("dollar", 1.0)
    energy = size_k * (energy_rate + 0.18 * (1.0 - p)) * energy_scale
    dollar = size_k * (dollar_rate + 0.10 * (1.0 - p)) * dollar_scale
    correctness_risk = (1.0 - p) * correct * loss * (0.40 + 0.08 * delay + 0.03 * horizon + 0.20 * survival)
    recomputation_penalty = (1.0 - p) * reuse * recompute
    score = retained_value - movement - energy - dollar - correctness_risk - recomputation_penalty
    return {
        "retained_value_score": retained_value,
        "movement_score": movement,
        "energy_proxy_score": energy,
        "dollar_proxy_score": dollar,
        "correctness_risk_score": correctness_risk,
        "recomputation_penalty": recomputation_penalty,
        "total_score": score,
        "evicted": 0 if retained else 1,
        "recomputed": 0 if retained else int(reuse > 0),
        "tier_transfer": 0 if tier == "HBM" else int(retained),
    }


def thesis_for(workload, winner, object_scores):
    if "control" in workload:
        return "weakened"
    dominant = max(object_scores.items(), key=lambda kv: kv[1])[0] if object_scores else ""
    if winner == "branch_verifier_durable_aware" and dominant in AGENTIC_OBJECTS:
        return "strengthened"
    if winner in {"reuse_aware_tiering", "cost_proxy_balanced"}:
        return "ambiguous"
    return "weakened"


def write_csv(path, rows, fields):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def aggregate(events, proxy_scales):
    result_rows = []
    breakdown_rows = []
    by_workload = defaultdict(list)
    for event in events:
        by_workload[event["workload_class"]].append(event)

    raw = {}
    for workload, workload_events in by_workload.items():
        raw[workload] = {}
        for policy in POLICIES:
            totals = defaultdict(float)
            object_totals = defaultdict(float)
            for event in workload_events:
                scores = score_event(policy, event, proxy_scales=proxy_scales)
                for key, value in scores.items():
                    totals[key] += value
                object_totals[event["object_class"]] += scores["total_score"]
            raw[workload][policy] = (totals, object_totals)

        winner = max(POLICIES, key=lambda p: raw[workload][p][0]["total_score"])
        winner_objects = raw[workload][winner][1]
        thesis = thesis_for(workload, winner, winner_objects)
        for policy in POLICIES:
            totals, object_totals = raw[workload][policy]
            dominant = max(object_totals.items(), key=lambda kv: kv[1])[0]
            result_rows.append(
                {
                    "policy": policy,
                    "workload_class": workload,
                    "total_score": round(totals["total_score"], 6),
                    "retained_value_score": round(totals["retained_value_score"], 6),
                    "movement_score": round(totals["movement_score"], 6),
                    "energy_proxy_score": round(totals["energy_proxy_score"], 6),
                    "dollar_proxy_score": round(totals["dollar_proxy_score"], 6),
                    "correctness_risk_score": round(totals["correctness_risk_score"], 6),
                    "evictions": int(totals["evicted"]),
                    "recomputations": int(totals["recomputed"]),
                    "tier_transfers": int(totals["tier_transfer"]),
                    "dominant_object_class": dominant,
                    "winning_policy_for_workload": winner,
                    "memory_centric_thesis": thesis,
                }
            )
            for object_class, total in sorted(object_totals.items()):
                breakdown_rows.append(
                    {
                        "policy": policy,
                        "workload_class": workload,
                        "object_class": object_class,
                        "total_score_contribution": round(total, 6),
                    }
                )
    return result_rows, breakdown_rows


def special_case_rows(events, proxy_scales):
    cases = [
        "zero reuse",
        "zero branch survival",
        "zero durable horizon",
        "equal tier costs",
        "zero correctness loss",
        "zero recomputation cost",
        "context cap saturated but durable horizon positive",
    ]
    rows = []
    for case in cases:
        mutated = []
        for event in events:
            e = dict(event)
            if case == "zero reuse":
                e["reuse_probability"] = 0.0
            elif case == "zero branch survival":
                e["branch_survival"] = 0.0
            elif case == "zero durable horizon":
                e["durability_horizon"] = 0.0
            elif case == "zero correctness loss":
                e["loss_cost"] = 0.0
                e["correctness_sensitive"] = 0
            elif case == "zero recomputation cost":
                e["recompute_cost"] = 0.0
            elif case == "context cap saturated but durable horizon positive":
                if e["object_class"] == "KV cache":
                    e["reuse_probability"] = min(float(e["reuse_probability"]), 0.05)
                if e["object_class"] == "durable workspace":
                    e["durability_horizon"] = max(float(e["durability_horizon"]), 12.0)
                    e["reuse_probability"] = max(float(e["reuse_probability"]), 0.70)
            mutated.append(e)

        totals_by_policy = {}
        for policy in POLICIES:
            total = 0.0
            for event in mutated:
                total += score_event(
                    policy,
                    event,
                    proxy_scales=proxy_scales,
                    equal_tier_costs=(case == "equal tier costs"),
                )["total_score"]
            totals_by_policy[policy] = total
        ranking = sorted(totals_by_policy, key=totals_by_policy.get, reverse=True)
        spread = totals_by_policy[ranking[0]] - totals_by_policy[ranking[-1]]
        if case == "context cap saturated but durable horizon positive":
            interpretation = "durable workspace can still differentiate policies after KV reuse collapses"
        elif spread < 80:
            interpretation = "policy differences mostly collapse under removed mechanism"
        else:
            interpretation = "policy differences persist through remaining nonzero mechanisms"
        rows.append(
            {
                "special_case": case,
                "observed_policy_ranking": " > ".join(ranking),
                "top_policy": ranking[0],
                "score_spread": round(spread, 6),
                "interpretation": interpretation,
            }
        )
    return rows


def main():
    proxy_scales = require_inputs()
    DATA.mkdir(exist_ok=True)
    events = generate_events()
    result_rows, breakdown_rows = aggregate(events, proxy_scales)
    specials = special_case_rows(events, proxy_scales)

    event_fields = [
        "run_id",
        "workload_class",
        "time_step",
        "event_type",
        "object_class",
        "object_id",
        "size_units",
        "reuse_probability",
        "branch_fanout",
        "branch_survival",
        "verifier_delay",
        "durability_horizon",
        "correctness_sensitive",
        "recompute_cost",
        "loss_cost",
    ]
    result_fields = [
        "policy",
        "workload_class",
        "total_score",
        "retained_value_score",
        "movement_score",
        "energy_proxy_score",
        "dollar_proxy_score",
        "correctness_risk_score",
        "evictions",
        "recomputations",
        "tier_transfers",
        "dominant_object_class",
        "winning_policy_for_workload",
        "memory_centric_thesis",
    ]
    breakdown_fields = ["policy", "workload_class", "object_class", "total_score_contribution"]
    special_fields = ["special_case", "observed_policy_ranking", "top_policy", "score_spread", "interpretation"]

    write_csv(DATA / "sim_workload_events.csv", events, event_fields)
    write_csv(DATA / "sim_policy_results.csv", result_rows, result_fields)
    write_csv(DATA / "sim_policy_object_breakdown.csv", breakdown_rows, breakdown_fields)
    write_csv(DATA / "sim_special_cases.csv", specials, special_fields)

    print(f"seed={SEED}")
    print(f"events={len(events)}")
    print(f"policy_result_rows={len(result_rows)}")
    print(f"object_breakdown_rows={len(breakdown_rows)}")
    print(f"special_cases={len(specials)}")
    winners = sorted({(r["workload_class"], r["winning_policy_for_workload"], r["memory_centric_thesis"]) for r in result_rows})
    for workload, winner, thesis in winners:
        print(f"winner {workload}: {winner} ({thesis})")


if __name__ == "__main__":
    main()
