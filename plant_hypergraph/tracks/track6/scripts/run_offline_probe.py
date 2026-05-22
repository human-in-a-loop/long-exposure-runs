#!/usr/bin/env python3
"""Run the Track 6 offline probe with deterministic local controls.

This runner intentionally performs no hosted, paid, key-gated, or network model
execution. If no local free/open model runtime and model files are discoverable,
it produces benchmark-only control results that exercise the scoring path.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "track6"
DATA = TRACK / "data"
SCORER_PATH = TRACK / "scripts" / "score_offline_probe.py"
DEFAULT_BANK = DATA / "offline_probe_question_bank.parquet"
DEFAULT_RESULTS = DATA / "probe_results.tsv"
DEFAULT_MODEL_SUMMARY = DATA / "probe_model_summary.tsv"
DEFAULT_CATEGORY_SUMMARY = DATA / "probe_category_summary.tsv"
DEFAULT_AVAILABILITY = DATA / "local_model_availability.json"
DEFAULT_FIGURE = DATA / "offline_probe_error_by_category.png"
DEFAULT_REPORT = TRACK / "track6_foundation_model_probe.md"

LOCAL_RUNTIME_MODULES = ("transformers", "torch", "llama_cpp")
LOCAL_MODEL_PATTERNS = ("*.gguf", "*.safetensors", "config.json")


def _load_scorer():
    spec = importlib.util.spec_from_file_location("track6_score_offline_probe", SCORER_PATH)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"cannot load scorer from {SCORER_PATH}")
    spec.loader.exec_module(module)
    return module.score_responses


def discover_local_model_availability(root: Path = ROOT) -> dict[str, Any]:
    """Detect local-only model prerequisites without importing model runtimes."""
    modules = {name: importlib.util.find_spec(name) is not None for name in LOCAL_RUNTIME_MODULES}
    model_files: list[str] = []
    for pattern in LOCAL_MODEL_PATTERNS:
        model_files.extend(str(path.relative_to(root)) for path in root.glob(f"**/{pattern}") if path.is_file())
    model_files = sorted(set(model_files))
    runnable = bool(model_files) and (modules.get("llama_cpp") or (modules.get("transformers") and modules.get("torch")))
    return {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "workspace-local discovery only; no model import, network call, or inference",
        "runtime_modules_available": modules,
        "local_model_files": model_files,
        "local_open_model_runnable": bool(runnable),
        "runner_mode": "local_model_available_not_executed" if runnable else "benchmark_only_data_limited",
        "caveat": (
            "No free/open local model configuration is runnable from this workspace."
            if not runnable
            else "A local runtime and model file were detected, but this runner still requires an explicit local-model adapter before inference."
        ),
    }


def _minimal_scoped_response(row: pd.Series) -> str:
    required = json.loads(row.required_terms_json)
    return " ".join(required) + " scoped evidence only"


def _forbidden_overclaim_response(row: pd.Series) -> str:
    required = json.loads(row.required_terms_json)
    forbidden = json.loads(row.forbidden_terms_json)
    first_forbidden = forbidden[0] if forbidden else "unsupported claim"
    return " ".join(required) + f" {first_forbidden}"


def build_control_responses(question_bank: pd.DataFrame) -> pd.DataFrame:
    """Create deterministic controls that make scorer sensitivity observable."""
    rows: list[dict[str, Any]] = []
    controls = [
        (
            "rubric_minimal_scoped_control",
            "positive_control",
            lambda row: _minimal_scoped_response(row),
            "Contains all required rubric terms and no forbidden terms.",
        ),
        (
            "empty_response_control",
            "negative_control",
            lambda row: "",
            "Missing response should fail every question.",
        ),
        (
            "forbidden_overclaim_control",
            "negative_control",
            lambda row: _forbidden_overclaim_response(row),
            "Contains required terms plus one forbidden overclaim term.",
        ),
        (
            "verbatim_expected_answer_diagnostic",
            "scorer_limitation_probe",
            lambda row: str(row.expected_answer),
            "Narrative expected answers may include forbidden phrases in negated form; this exposes lexical scorer limits.",
        ),
    ]
    for model_id, role, factory, caveat in controls:
        for _, row in question_bank.iterrows():
            rows.append(
                {
                    "model_id": model_id,
                    "result_role": role,
                    "question_id": row.question_id,
                    "response_text": factory(row),
                    "offline_only": True,
                    "provider_execution": "none",
                    "response_source": "deterministic_local_control",
                    "control_caveat": caveat,
                }
            )
    return pd.DataFrame(rows)


def score_control_responses(question_bank: pd.DataFrame, responses: pd.DataFrame) -> pd.DataFrame:
    score_responses = _load_scorer()
    scored_parts = []
    for model_id, group in responses.groupby("model_id", sort=True):
        scored = score_responses(question_bank, group[["question_id", "response_text"]])
        meta = group[["question_id", "model_id", "result_role", "offline_only", "provider_execution", "response_source", "control_caveat"]]
        scored = scored.merge(meta, on="question_id", how="left")
        scored_parts.append(scored)
    result = pd.concat(scored_parts, ignore_index=True)
    result["result_status"] = result["result_role"].map(
        {
            "positive_control": "control_pass_expected",
            "negative_control": "control_fail_expected",
            "scorer_limitation_probe": "diagnostic_only",
        }
    )
    return result[
        [
            "model_id",
            "result_role",
            "question_id",
            "category",
            "passed",
            "required_ok",
            "forbidden_hits_json",
            "missing_response",
            "offline_only",
            "provider_execution",
            "response_source",
            "result_status",
            "control_caveat",
        ]
    ].sort_values(["model_id", "category", "question_id"], kind="mergesort")


def summarize_results(results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    model_summary = (
        results.groupby(["model_id", "result_role"], sort=True)
        .agg(
            questions=("question_id", "count"),
            passed=("passed", "sum"),
            missing_responses=("missing_response", "sum"),
        )
        .reset_index()
    )
    model_summary["pass_rate"] = model_summary["passed"] / model_summary["questions"]
    category_summary = (
        results.groupby(["model_id", "result_role", "category"], sort=True)
        .agg(questions=("question_id", "count"), passed=("passed", "sum"))
        .reset_index()
    )
    category_summary["pass_rate"] = category_summary["passed"] / category_summary["questions"]
    return model_summary, category_summary


def write_category_figure(category_summary: pd.DataFrame, output: Path) -> None:
    pivot = category_summary.pivot(index="category", columns="model_id", values="pass_rate").fillna(0.0)
    desired = [
        "rubric_minimal_scoped_control",
        "empty_response_control",
        "forbidden_overclaim_control",
        "verbatim_expected_answer_diagnostic",
    ]
    pivot = pivot[[col for col in desired if col in pivot.columns]]
    ax = pivot.plot(kind="bar", figsize=(12, 6), width=0.82)
    ax.set_ylabel("pass rate")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("probe category")
    ax.set_title("Track 6 offline probe deterministic control pass rates")
    ax.legend(title="control", fontsize=8)
    ax.tick_params(axis="x", labelrotation=35)
    plt.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=160)
    plt.close()


def _markdown_table(df: pd.DataFrame, columns: list[str]) -> list[str]:
    rows = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return rows


def write_report(
    *,
    question_bank: pd.DataFrame,
    results: pd.DataFrame,
    model_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    availability: dict[str, Any],
    report_path: Path,
) -> None:
    counts = question_bank["category"].value_counts().sort_index().reset_index()
    counts.columns = ["category", "questions"]
    summary = model_summary.copy()
    summary["pass_rate"] = summary["pass_rate"].map(lambda value: f"{value:.3f}")
    expected_diag = summary[summary["model_id"] == "verbatim_expected_answer_diagnostic"]
    diag_rate = expected_diag["pass_rate"].iloc[0] if not expected_diag.empty else "n/a"
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "---",
        f"created: {now}",
        "milestone: M3.T6",
        "agent: fork-e08673192f98-clone-5",
        "schema_version: phytograph v1.0",
        "runner_mode: benchmark_only_data_limited",
        "---",
        "",
        "# Track 6 Foundation Model Probe — Offline Runner",
        "",
        "## Status",
        "",
        "**benchmark-only / data-limited for model execution.** The Track 6 Wave 3 runner executed the offline scoring path against deterministic local controls. No hosted, paid, key-gated, remote, or live model provider was called. No local free/open model runtime plus model weights were discoverable in the workspace, so this artifact does not claim foundation-model error rates.",
        "",
        "## Inputs",
        "",
        "- `tracks/track6/data/offline_probe_question_bank.parquet`",
        "- `tracks/track6/data/probe_ground_truth_edges.parquet`",
        "- `tracks/track6/scripts/score_offline_probe.py`",
        "",
        "## Outputs",
        "",
        "- `tracks/track6/data/probe_results.tsv`",
        "- `tracks/track6/data/probe_model_summary.tsv`",
        "- `tracks/track6/data/probe_category_summary.tsv`",
        "- `tracks/track6/data/local_model_availability.json`",
        "- `tracks/track6/data/offline_probe_error_by_category.png`",
        "- `tracks/track6/track6_foundation_model_probe.md`",
        "",
        "## Probe Coverage",
        "",
        f"Questions scored: **{len(question_bank)}** across **{question_bank['category'].nunique()}** categories.",
        "",
    ]
    lines.extend(_markdown_table(counts, ["category", "questions"]))
    lines.extend(
        [
            "",
            "## Local Model Availability",
            "",
            f"Runner mode: `{availability['runner_mode']}`.",
            f"Runnable local open model config found: `{availability['local_open_model_runnable']}`.",
            f"Runtime modules available: `{json.dumps(availability['runtime_modules_available'], sort_keys=True)}`.",
            f"Local model files found: `{len(availability['local_model_files'])}`.",
            "",
            "Because no runnable local model configuration was available, `probe_results.tsv` contains deterministic controls only. These rows validate the offline scoring mechanism; they are not model performance measurements.",
            "",
            "## Control Results",
            "",
        ]
    )
    lines.extend(_markdown_table(summary, ["model_id", "result_role", "questions", "passed", "missing_responses", "pass_rate"]))
    lines.extend(
        [
            "",
            "## Mechanism Interpretation",
            "",
            "- `rubric_minimal_scoped_control` is the positive control: it includes every required rubric term and no forbidden terms.",
            "- `empty_response_control` is a missing-output negative control.",
            "- `forbidden_overclaim_control` is a high-stakes overclaim negative control.",
            f"- `verbatim_expected_answer_diagnostic` passed at rate `{diag_rate}` because the scorer is lexical: several narrative expected answers contain forbidden phrases in explicitly negated form. This is a scorer limitation to fix before treating results as semantic model evaluation.",
            "",
            "The current instrument therefore validates the offline benchmark and deterministic scoring path, not any live/local foundation-model capability. Wave 4 validation should either add a local semantic scorer or require manually audited response subsets before making publishable model-error claims.",
            "",
            "## Evidence Boundaries",
            "",
            "- Synonym rows test name-normalization stability only; they do not support trait, range, edibility, or phylogeny claims.",
            "- Hybrid/pedigree rows test source-scoped parentage reasoning only; they do not establish new taxonomy, dates, or performance.",
            "- Region rows test region/status scoping only; native/current/global distribution remain distinct.",
            "- Ghost-partner rows test recognition of cited hypotheses; they are not validation of extinct ecological interactions.",
            "- Convergence rows test whether trait similarity is overread; they do not establish convergence without Track 3 analysis.",
            "- Phytochemistry rows test safety/bioactivity overclaim resistance; they do not support clinical efficacy, dose, or edibility advice.",
            "- Media-scope rows test image-evidence boundaries; image availability is not biological importance or safety evidence.",
            "",
            "## Barrier 3 Readiness",
            "",
            "Track 6 can be exposed in the Atlas as an offline benchmark with deterministic control results and clear `data-limited` status for actual model scoring. It is not ready to contribute model leaderboard claims until a free/open/local model adapter or audited response file is added.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    *,
    question_bank_path: Path = DEFAULT_BANK,
    results_path: Path = DEFAULT_RESULTS,
    model_summary_path: Path = DEFAULT_MODEL_SUMMARY,
    category_summary_path: Path = DEFAULT_CATEGORY_SUMMARY,
    availability_path: Path = DEFAULT_AVAILABILITY,
    figure_path: Path = DEFAULT_FIGURE,
    report_path: Path = DEFAULT_REPORT,
    make_plot: bool = True,
) -> dict[str, Path]:
    question_bank = pd.read_parquet(question_bank_path)
    availability = discover_local_model_availability()
    responses = build_control_responses(question_bank)
    results = score_control_responses(question_bank, responses)
    model_summary, category_summary = summarize_results(results)

    results_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(results_path, sep="\t", index=False)
    model_summary.to_csv(model_summary_path, sep="\t", index=False)
    category_summary.to_csv(category_summary_path, sep="\t", index=False)
    availability_path.write_text(json.dumps(availability, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if make_plot:
        write_category_figure(category_summary, figure_path)
    write_report(
        question_bank=question_bank,
        results=results,
        model_summary=model_summary,
        category_summary=category_summary,
        availability=availability,
        report_path=report_path,
    )
    return {
        "results": results_path,
        "model_summary": model_summary_path,
        "category_summary": category_summary_path,
        "availability": availability_path,
        "figure": figure_path,
        "report": report_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--model-summary", type=Path, default=DEFAULT_MODEL_SUMMARY)
    parser.add_argument("--category-summary", type=Path, default=DEFAULT_CATEGORY_SUMMARY)
    parser.add_argument("--availability", type=Path, default=DEFAULT_AVAILABILITY)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args()
    outputs = run(
        question_bank_path=args.question_bank,
        results_path=args.results,
        model_summary_path=args.model_summary,
        category_summary_path=args.category_summary,
        availability_path=args.availability,
        figure_path=args.figure,
        report_path=args.report,
        make_plot=not args.no_plot,
    )
    for label, path in outputs.items():
        print(f"WROTE {label}: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
