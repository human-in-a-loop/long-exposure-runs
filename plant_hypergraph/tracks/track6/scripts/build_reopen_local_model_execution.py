#!/usr/bin/env python3
"""Build Track 6 local/free/open model execution reopen artifacts.

created: 2026-05-18T19:05:00+00:00
cycle: 26
run_id: run-phytograph-cycle26-track6-local-model-execution-reopen
agent: worker
milestone: _plan/track6-local-model-execution-reopen
"""
from __future__ import annotations

import importlib.metadata
import importlib.util
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "track6"
DATA = TRACK / "data"
REPORTS = TRACK / "reports"

QUESTION_BANK = DATA / "offline_probe_question_bank.tsv"
AVAILABILITY = DATA / "local_model_availability_reopen.tsv"
RESPONSES = DATA / "local_model_probe_responses.tsv"
DIAGNOSTICS = DATA / "local_model_probe_scoring_diagnostics.tsv"
REPORT = REPORTS / "track6_reopen_local_model_execution.md"

DETERMINATION = "no_new_qualifying_evidence"
RUN_ID = "run-phytograph-cycle26-track6-local-model-execution-reopen"
CREATED = "2026-05-18T19:05:00+00:00"

RUNTIME_PACKAGES = [
    ("python-package:llama_cpp", "llama_cpp"),
    ("python-package:transformers", "transformers"),
    ("python-package:torch", "torch"),
    ("python-package:ctransformers", "ctransformers"),
    ("python-package:gpt4all", "gpt4all"),
    ("python-package:onnxruntime", "onnxruntime"),
    ("python-package:sentencepiece", "sentencepiece"),
]

RUNTIME_BINARIES = [
    ("binary:ollama", "ollama"),
    ("binary:llama-cli", "llama-cli"),
    ("binary:llamafile", "llamafile"),
    ("binary:gpt4all", "gpt4all"),
]

MODEL_PATTERNS = ["*.gguf", "*.safetensors", "pytorch_model*.bin", "model*.onnx"]

AVAILABILITY_COLUMNS = [
    "runtime_name",
    "availability",
    "version_if_detectable",
    "model_path",
    "license_or_provenance_status",
    "runnable_flag",
    "blocker",
]

RESPONSE_COLUMNS = [
    "model_id",
    "question_id",
    "category",
    "prompt_variant",
    "raw_response_path",
    "response_text_digest",
    "deterministic_settings",
    "timestamp",
    "execution_status",
]

DIAGNOSTIC_COLUMNS = [
    "category",
    "static_benchmark_questions",
    "runnable_response_count",
    "scored_response_count",
    "skipped_response_count",
    "scorer_coverage",
    "error_rate_claim_allowed",
    "dominant_blocker",
]


def _package_version(module_name: str) -> str:
    try:
        return importlib.metadata.version(module_name.replace("_", "-"))
    except importlib.metadata.PackageNotFoundError:
        try:
            return importlib.metadata.version(module_name)
        except importlib.metadata.PackageNotFoundError:
            return ""


def inspect_availability() -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    any_runtime = False
    for runtime_name, module_name in RUNTIME_PACKAGES:
        available = importlib.util.find_spec(module_name) is not None
        any_runtime = any_runtime or available
        rows.append(
            {
                "runtime_name": runtime_name,
                "availability": "available" if available else "missing",
                "version_if_detectable": _package_version(module_name) if available else "",
                "model_path": "",
                "license_or_provenance_status": "package_only_no_model_license" if available else "not_applicable",
                "runnable_flag": "false",
                "blocker": (
                    "runtime package present but no compatible local model weights were found"
                    if available
                    else "runtime package not installed in local environment"
                ),
            }
        )
    for runtime_name, binary_name in RUNTIME_BINARIES:
        path = shutil.which(binary_name)
        available = bool(path)
        any_runtime = any_runtime or available
        rows.append(
            {
                "runtime_name": runtime_name,
                "availability": "available" if available else "missing",
                "version_if_detectable": "",
                "model_path": "",
                "license_or_provenance_status": "binary_only_no_model_license" if available else "not_applicable",
                "runnable_flag": "false",
                "blocker": (
                    "runtime binary present but no compatible local model weights were found"
                    if available
                    else "runtime binary not found on PATH"
                ),
            }
        )

    model_files: list[Path] = []
    for pattern in MODEL_PATTERNS:
        model_files.extend(ROOT.glob(f"**/{pattern}"))
    model_files = sorted({path for path in model_files if path.is_file()})
    if model_files:
        for path in model_files:
            rows.append(
                {
                    "runtime_name": "workspace-model-file",
                    "availability": "available",
                    "version_if_detectable": "",
                    "model_path": str(path.relative_to(ROOT)),
                    "license_or_provenance_status": "unknown_local_file_requires_manual_license_audit",
                    "runnable_flag": "false",
                    "blocker": "model file present but no compatible audited runtime pairing was established",
                }
            )
    else:
        rows.append(
            {
                "runtime_name": "workspace-model-files",
                "availability": "missing",
                "version_if_detectable": "",
                "model_path": "",
                "license_or_provenance_status": "not_applicable",
                "runnable_flag": "false",
                "blocker": "no workspace model weights found for patterns: " + ", ".join(MODEL_PATTERNS),
            }
        )

    availability = pd.DataFrame(rows, columns=AVAILABILITY_COLUMNS)
    if any_runtime and model_files:
        availability.loc[:, "runnable_flag"] = "false"
        availability.loc[:, "blocker"] = availability["blocker"].where(
            availability["availability"] == "missing",
            "local runtime or model asset is partial; no audited free/open runtime-plus-weight pairing was established",
        )
    return availability


def build_response_table(question_bank: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in question_bank.to_dict("records"):
        rows.append(
            {
                "model_id": "not_run_no_local_model",
                "question_id": row["question_id"],
                "category": row["category"],
                "prompt_variant": row["prompt_template_id"],
                "raw_response_path": "",
                "response_text_digest": "",
                "deterministic_settings": "temperature=0; top_p=1; seed=0; max_new_tokens=256; not executed",
                "timestamp": CREATED,
                "execution_status": "not_run_no_local_model",
            }
        )
    return pd.DataFrame(rows, columns=RESPONSE_COLUMNS)


def build_diagnostics(question_bank: pd.DataFrame, responses: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for category, group in question_bank.groupby("category", sort=True):
        category_responses = responses[responses["category"] == category]
        runnable = int((category_responses["execution_status"] == "executed").sum())
        scored = 0
        rows.append(
            {
                "category": category,
                "static_benchmark_questions": int(len(group)),
                "runnable_response_count": runnable,
                "scored_response_count": scored,
                "skipped_response_count": int(len(category_responses) - runnable),
                "scorer_coverage": "0.0",
                "error_rate_claim_allowed": "false",
                "dominant_blocker": "no runnable local/free/open model runtime plus weights available",
            }
        )
    return pd.DataFrame(rows, columns=DIAGNOSTIC_COLUMNS)


def _markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in df.to_dict("records"):
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def write_report(availability: pd.DataFrame, responses: pd.DataFrame, diagnostics: pd.DataFrame) -> None:
    runnable_rows = int((availability["runnable_flag"] == "true").sum())
    executed_rows = int((responses["execution_status"] == "executed").sum())
    scored_rows = int(diagnostics["scored_response_count"].sum())
    static_questions = int(diagnostics["static_benchmark_questions"].sum())
    report = f"""---
created: {CREATED}
cycle: 26
run_id: {RUN_ID}
agent: worker
milestone: _plan/track6-local-model-execution-reopen
---

# Track 6 Reopen Local Model Execution

## Determination

determination: `{DETERMINATION}`.

The Track 6 reopen predicate is not met. The workspace contains a valid static benchmark and deterministic scorer, but local inspection found no audited free/open/local model runtime plus compatible model weights that can execute without credentials, payment, remote inference, or downloads. H6 therefore remains `environment_limited_untested`, and no model-performance, leaderboard, vendor-comparison, toxicity-safety, or failure-rate claim is promoted.

## Runtime And Weight Inspection

| Runtime or asset | Availability | Version | Model path | License/provenance status | Runnable | Blocker |
|---|---:|---|---|---|---:|---|
{_markdown_table(availability, AVAILABILITY_COLUMNS).split(chr(10), 2)[2]}

## Probe Execution

The static benchmark has {static_questions} question-category rows in this reopen table. Executed model responses: {executed_rows}. Scored model responses: {scored_rows}. All rows in `local_model_probe_responses.tsv` are explicit `not_run_no_local_model` rows, preserving question/category coverage while avoiding fabricated responses.

## Scoring Controls

| Category | Static questions | Runnable responses | Scored responses | Skipped responses | Scorer coverage | Error-rate claim allowed | Dominant blocker |
|---|---:|---:|---:|---:|---:|---:|---|
{_markdown_table(diagnostics, DIAGNOSTIC_COLUMNS).split(chr(10), 2)[2]}

![Track 6 reopen coverage by probe category, showing static benchmark size, runnable-response count, and scored-response count.](../figures/track6_reopen_execution_coverage.png)

## Reopen Gate

`reopen_threshold_met` requires at least one local/free/open model runtime plus weights to produce nonzero audited responses across at least two probe categories. The current run has {runnable_rows} runnable runtime/weight pairings, {executed_rows} executed responses, and {scored_rows} scored responses. Since error-rate estimates require a nonzero denominator, bounded per-category model-error estimates are undefined here.

## Future Runtime Recipe

A future reopen cycle needs an approved local model artifact with documented license/provenance, an offline adapter that performs deterministic decoding, response capture by question ID, and scorer diagnostics showing nonzero audited response coverage. Remote provider APIs, key export, hosted inference, and live paid services remain excluded unless a later directive explicitly changes the Track 6 constraint.
"""
    REPORTS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report)


def run() -> dict[str, Path]:
    question_bank = pd.read_csv(QUESTION_BANK, sep="\t", dtype=str)
    availability = inspect_availability()
    responses = build_response_table(question_bank)
    diagnostics = build_diagnostics(question_bank, responses)

    DATA.mkdir(parents=True, exist_ok=True)
    availability.to_csv(AVAILABILITY, sep="\t", index=False)
    responses.to_csv(RESPONSES, sep="\t", index=False)
    diagnostics.to_csv(DIAGNOSTICS, sep="\t", index=False)
    write_report(availability, responses, diagnostics)
    return {
        "availability": AVAILABILITY,
        "responses": RESPONSES,
        "diagnostics": DIAGNOSTICS,
        "report": REPORT,
    }


def main() -> int:
    outputs = run()
    for name, path in outputs.items():
        print(f"wrote {name}: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
