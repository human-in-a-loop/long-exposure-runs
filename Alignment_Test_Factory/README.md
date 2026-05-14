# Alignment Test Factory

This folder contains public artifacts from a long-exposure run exploring an
open alignment test factory for agentic AI systems.

The run investigated whether high-level safety properties can be converted into
safe, reproducible, trace-scored evaluation tasks for agents that use tools,
state, delegation, and multi-step workflows. The result is a bounded prototype:
a provider-agnostic task schema, benign synthetic task families, deterministic
trace scorers, Inspect AI smoke integrations, stress probes, tests, and final
audit/report artifacts.

## Start Here

- `reports/final/final_report.md` and `reports/final/final_report.pdf` contain
  the final synthesis.
- `audits/final/final_audit_report.md` and
  `audits/final/final_audit_report.pdf` contain the final closure audit.
- `alignment-test-factory/` contains the prototype schema, runtime, scorers,
  eval adapters, examples, and helper tools.
- `tests/` contains the focused regression tests used by the run.
- `reports/cycles/` contains periodic cycle reports.
- `MANIFEST.md` maps the important files and how they support the final claims.

## Reproduction Notes

The prototype is a research artifact rather than a packaged library. It was
validated with Python 3.12, `pytest`, `pydantic`, and Inspect AI. The most useful
entry points are:

```bash
cd Alignment_Test_Factory
python -m pytest tests/test_task_spec_schema.py tests/test_toy_environment.py tests/test_inspect_smoke.py tests/test_task_families.py tests/test_multi_family_inspect.py tests/test_benchmark_stress.py
python alignment-test-factory/tools/validate_specs.py
python alignment-test-factory/tools/run_task_families.py
python alignment-test-factory/tools/run_benchmark_stress.py
```

Raw local runtime state, virtual environments, caches, and bulky Inspect log
dumps were intentionally omitted from this public folder. Local machine paths in
generated reports were sanitized with placeholders such as `<RUN_WORKSPACE>`.
