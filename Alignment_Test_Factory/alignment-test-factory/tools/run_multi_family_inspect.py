# created: 2026-05-13T23:10:00Z
# cycle: 6
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-6
"""Run the multi-family Inspect eval and export per-sample score evidence."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import inspect_ai
from inspect_ai.log import list_eval_logs, read_eval_log

ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = ROOT / "evals"
OUT_DIR = ROOT / "examples" / "inspect"
LOG_DIR = OUT_DIR / "logs"
SUMMARY_PATH = OUT_DIR / "multi_family_inspect_score_summary.json"
MANIFEST_PATH = OUT_DIR / "multi_family_inspect_log_manifest.json"


def inspect_command() -> list[str]:
    return [
        "inspect",
        "eval",
        "multi_family_smoke.py",
        "--model",
        "mockllm/model",
        "--log-dir",
        str(LOG_DIR),
        "--log-format",
        "json",
        "--max-samples",
        "1",
    ]


def run_inspect_eval() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    before = {str(info.name) for info in list_eval_logs(str(LOG_DIR))}
    subprocess.run(inspect_command(), cwd=EVALS_DIR, check=True)
    after = list_eval_logs(str(LOG_DIR))
    new_logs = [info for info in after if str(info.name) not in before]
    if not new_logs:
        new_logs = after[:1]
    if not new_logs:
        raise RuntimeError("Inspect eval completed but no log file was discovered")
    return Path(str(new_logs[0].name))


def export_summary(log_path: Path) -> dict:
    log = read_eval_log(log_path, format="json")
    samples = []
    for sample in log.samples or []:
        if "deterministic_multi_family_score" not in sample.scores:
            raise RuntimeError(f"missing deterministic score for sample {sample.id}")
        score = sample.scores["deterministic_multi_family_score"]
        summary = dict(score.metadata or {})
        summary["inspect_score_value"] = score.value
        summary["inspect_score_answer"] = score.answer
        summary["inspect_score_explanation"] = score.explanation
        samples.append(summary)

    samples.sort(key=lambda item: item["sample_id"])
    exported = {
        "task_name": log.eval.task,
        "model": log.eval.model,
        "inspect_log_path": str(log_path),
        "sample_count": len(samples),
        "samples": samples,
    }
    SUMMARY_PATH.write_text(json.dumps(exported, indent=2) + "\n", encoding="utf-8")
    return exported


def export_manifest(log_path: Path) -> None:
    manifest = {
        "command": inspect_command(),
        "working_directory": str(EVALS_DIR),
        "inspect_version": getattr(inspect_ai, "__version__", "unknown"),
        "log_file_path": str(log_path),
        "score_summary_path": str(SUMMARY_PATH),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    inspect_bin = shutil.which("inspect")
    if inspect_bin is None:
        raise RuntimeError("inspect executable not found on PATH")
    log_path = run_inspect_eval()
    summary = export_summary(log_path)
    export_manifest(log_path)
    verdicts = {
        sample["sample_id"]: {item["predicate_id"]: item["verdict"] for item in sample["predicate_results"]}
        for sample in summary["samples"]
    }
    print(f"log: {log_path}")
    print(f"summary: {SUMMARY_PATH}")
    print(f"manifest: {MANIFEST_PATH}")
    print(f"verdicts: {verdicts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
