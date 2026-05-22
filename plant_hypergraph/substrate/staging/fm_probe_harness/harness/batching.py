# PhytoGraph M1.8 — token-budgeted batcher. cycle 2, worker.
"""Plan a batch of calls against a remaining USD budget.

This is a planner, not a dispatcher: it returns the prefix of calls that
fits within the remaining cap. The FMClient invokes calls one at a time
and re-checks the cap before each, so the planner is advisory — the cap
itself is enforced atomically inside FMClient.call().
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from .cost import PricingTable


@dataclass(frozen=True)
class CallPlan:
    provider: str
    model_id: str
    tokens_in_est: int
    tokens_out_max: int
    estimated_cost_usd: float


def plan_batch(
    calls: Sequence[Tuple[str, str, int, int]],
    remaining_usd: float,
    pricing: PricingTable,
) -> Tuple[List[CallPlan], List[CallPlan]]:
    """Greedily admit calls until the budget would be exceeded.

    `calls` is a list of (provider, model_id, tokens_in_est, tokens_out_max).
    Returns (admitted, deferred). Deferred calls are the suffix that would
    exceed the remaining budget; caller may retry them next cycle.
    """
    admitted: List[CallPlan] = []
    deferred: List[CallPlan] = []
    used = 0.0
    for prov, model, t_in, t_out in calls:
        est = pricing.estimate_cost(prov, model, t_in, t_out)
        plan = CallPlan(prov, model, t_in, t_out, est)
        if used + est <= remaining_usd:
            admitted.append(plan)
            used += est
        else:
            deferred.append(plan)
    return admitted, deferred
