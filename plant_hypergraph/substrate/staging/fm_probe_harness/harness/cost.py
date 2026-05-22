# PhytoGraph M1.8 — pricing lookup + cost estimation. cycle 2, worker.
"""Pricing and cost estimation.

Convention: prices are USD per 1,000,000 tokens. Always round UP to the next
$0.000001 so under-estimation cannot defeat the cap. When a model is not
listed under its provider, fall back to the provider's `_default` entry.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PRICING_PATH_DEFAULT = Path(__file__).parent.parent / "pricing_table.json"


@dataclass(frozen=True)
class PriceRow:
    input_per_mtok: float
    output_per_mtok: float


class PricingTable:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else PRICING_PATH_DEFAULT
        with open(self.path) as f:
            self._table = json.load(f)

    def lookup(self, provider: str, model_id: str) -> PriceRow:
        prov = self._table.get(provider)
        if not prov:
            raise KeyError(f"No pricing entry for provider {provider!r}")
        row = prov.get(model_id) or prov.get("_default")
        if not row:
            raise KeyError(f"No pricing entry for {provider}/{model_id}")
        return PriceRow(float(row["input_per_mtok"]), float(row["output_per_mtok"]))

    def estimate_cost(
        self,
        provider: str,
        model_id: str,
        tokens_in: int,
        tokens_out_max: int,
    ) -> float:
        """Upper-bound the call cost. tokens_out_max is the worst case (typically max_tokens)."""
        row = self.lookup(provider, model_id)
        cost = (
            (tokens_in * row.input_per_mtok / 1_000_000.0)
            + (tokens_out_max * row.output_per_mtok / 1_000_000.0)
        )
        # Round UP to the next micro-dollar so we never under-estimate.
        return math.ceil(cost * 1_000_000) / 1_000_000.0

    def actual_cost(
        self,
        provider: str,
        model_id: str,
        tokens_in: int,
        tokens_out: int,
    ) -> float:
        """Post-call cost computed from the realized token counts."""
        row = self.lookup(provider, model_id)
        cost = (
            (tokens_in * row.input_per_mtok / 1_000_000.0)
            + (tokens_out * row.output_per_mtok / 1_000_000.0)
        )
        return math.ceil(cost * 1_000_000) / 1_000_000.0
