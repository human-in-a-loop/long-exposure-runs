#!/usr/bin/env python3
"""Deterministic scorer for Track 6 offline probe responses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BANK = ROOT / "tracks" / "track6" / "data" / "offline_probe_question_bank.parquet"


def _contains_all(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return all(term.lower() in lower for term in terms)


def _contains_any(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term.lower() in lower]


def score_responses(question_bank: pd.DataFrame, responses: pd.DataFrame) -> pd.DataFrame:
    required_cols = {"question_id", "response_text"}
    missing = required_cols - set(responses.columns)
    if missing:
        raise ValueError(f"responses missing required columns: {sorted(missing)}")

    merged = question_bank.merge(responses[["question_id", "response_text"]], on="question_id", how="left")
    rows = []
    for _, row in merged.iterrows():
        text = row.response_text if isinstance(row.response_text, str) else ""
        required = json.loads(row.required_terms_json)
        forbidden = json.loads(row.forbidden_terms_json)
        forbidden_hits = _contains_any(text, forbidden)
        required_ok = _contains_all(text, required)
        passed = bool(text) and required_ok and not forbidden_hits
        rows.append(
            {
                "question_id": row.question_id,
                "category": row.category,
                "passed": passed,
                "required_ok": required_ok,
                "forbidden_hits_json": json.dumps(forbidden_hits, sort_keys=True),
                "missing_response": not bool(text),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path, help="CSV/TSV with question_id and response_text")
    parser.add_argument("--question-bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    bank = pd.read_parquet(args.question_bank)
    sep = "\t" if args.responses.suffix.lower() == ".tsv" else ","
    responses = pd.read_csv(args.responses, sep=sep)
    scored = score_responses(bank, responses)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
