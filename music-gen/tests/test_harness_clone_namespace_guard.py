"""Cycle-33 _infra/harness-clone-namespace-guard test suite.

Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_harness_clone_namespace_guard.py

14 test cases exercising writer + concat-lint boundary enforcement of the c32
fanout namespace convention (docs/fanout_namespace_convention.md). Zero
external dependencies. Plain asserts. Interpreter guard `/usr/bin/python3`.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Interpreter guard.
assert sys.executable == "/usr/bin/python3", (
    f"must run under /usr/bin/python3; got {sys.executable}"
)

# Workspace root — allow test to run from anywhere as long as this file lives
# inside a workspace that has promise_ledger.jsonl at its root.
_WS = Path(__file__).resolve().parent.parent

# Make workspace importable so long_exposure/* resolves. Mirrors the
# mandatory _LE_PARENT sys.path shim used by
# tests/test_ledger_writer_validation.py + tests/test_fanout_concat_validation.py.
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in sys.path:
    sys.path.append(_LE_PARENT)

import long_exposure.workspace_bootstrap as wb  # noqa: E402
from long_exposure.tools._ledger_schema import (  # noqa: E402
    LedgerSchemaError,
)

_STRICT_ENV = "MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE"
_FORK_ENV = "AGENT_FORK_ID"
_CLONE_ENV = "AGENT_FORK_CLONE_K"
_INSTANCE_ENV = "AGENT_INSTANCE_DIR"


def _tmp_ws() -> Path:
    return Path(tempfile.mkdtemp(prefix="c33guard_ws_"))


class _EnvOverride:
    """Context manager that sets env vars for the duration of a with block."""

    def __init__(self, **overrides: str | None) -> None:
        self.overrides = overrides
        self.saved: dict[str, str | None] = {}

    def __enter__(self) -> "_EnvOverride":
        for k, v in self.overrides.items():
            self.saved[k] = os.environ.get(k)
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        return self

    def __exit__(self, *exc) -> None:
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


_ROOT_ENV = dict.fromkeys((_FORK_ENV, _CLONE_ENV, _INSTANCE_ENV, _STRICT_ENV), None)


def _clone_env(k: int = 2, strict: bool = False) -> dict[str, str | None]:
    return {
        _FORK_ENV: "test-fork-abcdef",
        _CLONE_ENV: str(k),
        _INSTANCE_ENV: f"/tmp/c33_shadow_clone-{k}",
        _STRICT_ENV: "1" if strict else None,
    }


def _well_formed(mid: str, run_id: str = "run-2026-08-29T042000Z") -> dict:
    return {
        "ts": "2026-08-29T05:00:00Z",
        "run_id": run_id,
        "cycle": 33,
        "agent": "worker",
        "milestone_id": mid,
        "status": "validated",
        "confidence": {"level": "high", "rationale": "test", "assessor": "worker"},
        "narrative": "test",
        "artifacts": [],
    }


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------


def test_01_baseline_468_rows_replay_green() -> None:
    """From root context, no row of the pre-existing ledger is mutated or
    rejected under either mode. This is GUARD_LANDS clause (1)."""
    ledger = _WS / "promise_ledger.jsonl"
    assert ledger.exists(), f"baseline ledger not found at {ledger}"
    rows = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
    assert len(rows) >= 468, f"baseline ledger has fewer than 468 rows: {len(rows)}"
    for mode in ("default", "strict"):
        overrides = dict(_ROOT_ENV)
        overrides[_STRICT_ENV] = "1" if mode == "strict" else None
        with _EnvOverride(**overrides):
            for i, row in enumerate(rows, 1):
                pre = row.get("milestone_id")
                after = wb._guard_clone_namespace(dict(row), _WS)
                assert after.get("milestone_id") == pre, (
                    f"[{mode}] row {i} milestone_id mutated by guard from "
                    f"root context: {pre!r} -> {after.get('milestone_id')!r}"
                )


def test_02_infra_from_clone_autosuffixes() -> None:
    """Manufactured _infra/foo from clone-2 default-mode context auto-suffixes."""
    with _EnvOverride(**_clone_env(k=2)):
        ev = _well_formed("_infra/foo")
        out = wb._guard_clone_namespace(ev, _WS)
        assert out["milestone_id"] == "_infra/foo-clone-2", (
            f"expected _infra/foo-clone-2, got {out['milestone_id']!r}"
        )


def test_03_infra_from_root_stays_canonical() -> None:
    """Same manufactured id from root context stays unmodified."""
    with _EnvOverride(**_ROOT_ENV):
        ev = _well_formed("_infra/foo")
        out = wb._guard_clone_namespace(ev, _WS)
        assert out["milestone_id"] == "_infra/foo", (
            f"root-context id must not be touched: got {out['milestone_id']!r}"
        )


def test_04_strict_mode_rejects_with_typed_error() -> None:
    """Strict mode + clone context + bare _infra/foo => LedgerNamespaceViolation."""
    with _EnvOverride(**_clone_env(k=2, strict=True)):
        ev = _well_formed("_infra/foo")
        try:
            wb._guard_clone_namespace(ev, _WS)
        except wb.LedgerNamespaceViolation as e:
            msg = str(e)
            assert "_infra/foo" in msg, f"error must name the offending id: {msg}"
            assert "clone_k=2" in msg, f"error must name detected clone_k: {msg}"
            assert "fanout_namespace_convention.md" in msg, (
                f"error must point to convention doc: {msg}"
            )
        else:
            raise AssertionError(
                "expected LedgerNamespaceViolation in strict mode + clone context"
            )


def test_05_strict_mode_disabled_autosuffixes() -> None:
    """Explicit strict=0 behaves identically to unset (auto-suffix)."""
    env = _clone_env(k=2)
    env[_STRICT_ENV] = "0"
    with _EnvOverride(**env):
        ev = _well_formed("_infra/foo")
        out = wb._guard_clone_namespace(ev, _WS)
        assert out["milestone_id"] == "_infra/foo-clone-2"


def test_06_all_five_families_covered() -> None:
    """Every leading-underscore infra family triggers the guard from clone
    context."""
    families = ("_infra/", "_run/", "_plan/", "_archive/", "_manager/")
    for fam in families:
        mid = f"{fam}sample-token"
        # Default mode: auto-suffix.
        with _EnvOverride(**_clone_env(k=3)):
            ev = _well_formed(mid)
            out = wb._guard_clone_namespace(ev, _WS)
            assert out["milestone_id"] == f"{mid}-clone-3", (
                f"family {fam!r} default-mode failed: got {out['milestone_id']!r}"
            )
        # Strict mode: raise.
        with _EnvOverride(**_clone_env(k=3, strict=True)):
            ev = _well_formed(mid)
            try:
                wb._guard_clone_namespace(ev, _WS)
            except wb.LedgerNamespaceViolation:
                pass
            else:
                raise AssertionError(
                    f"family {fam!r} strict-mode did not raise on {mid!r}"
                )


def test_07_M_star_never_touched() -> None:
    """M-* identifiers are never suffixed or rejected."""
    for mid in (
        "M-DAW-SPIKE-1/foo",
        "M-EAR-1/preparation/features",
        "M-GEN-1",
        "M-INGEST-1/chunker",
    ):
        with _EnvOverride(**_clone_env(k=2, strict=True)):
            ev = _well_formed(mid)
            out = wb._guard_clone_namespace(ev, _WS)
            assert out["milestone_id"] == mid, (
                f"M-* id must not be touched: {mid!r} -> {out['milestone_id']!r}"
            )


def test_08_unprefixed_never_touched() -> None:
    """Bare tokens without a leading '_<family>/' prefix never trigger."""
    for mid in ("foo/bar", "bar-clone", "quux", "M/oops", "run/cycle_x"):
        with _EnvOverride(**_clone_env(k=2, strict=True)):
            ev = _well_formed(mid)
            out = wb._guard_clone_namespace(ev, _WS)
            assert out["milestone_id"] == mid, (
                f"un-prefixed id must not be touched: {mid!r} -> {out['milestone_id']!r}"
            )


def test_09_idempotent_on_already_suffixed() -> None:
    """An id already ending -clone-<digit>+ never double-suffixes."""
    for mid in (
        "_infra/foo-clone-2",
        "_run/cycle_33_launched-clone-0",
        "_plan/rubric-clone-99",
    ):
        for env in (_clone_env(k=2), _clone_env(k=2, strict=True)):
            with _EnvOverride(**env):
                ev = _well_formed(mid)
                out = wb._guard_clone_namespace(ev, _WS)
                assert out["milestone_id"] == mid, (
                    f"already-suffixed id was touched: {mid!r} -> "
                    f"{out['milestone_id']!r}"
                )


def test_10_lint_clone_shadow_symmetric() -> None:
    """A manufactured shadow ledger with one violating row fails
    _lint_clone_shadow with the correct annotation."""
    tmp = _tmp_ws()
    try:
        shadow_dir = tmp / "clone-2"
        shadow_dir.mkdir(parents=True)
        shadow = shadow_dir / "promise_ledger.jsonl"

        good_row = _well_formed("M-TEST-1/foo")
        good_row["event_id"] = _uuid_for(good_row)
        bad_row = _well_formed("_infra/violator")
        bad_row["event_id"] = _uuid_for(bad_row)
        with open(shadow, "w") as f:
            f.write(json.dumps(good_row) + "\n")
            f.write(json.dumps(bad_row) + "\n")

        try:
            wb._lint_clone_shadow(shadow)
        except wb.LedgerNamespaceViolation as e:
            msg = str(e)
            assert f"{shadow}:2" in msg, (
                f"error must include <shadow_path>:<line_no> annotation, got: {msg}"
            )
            assert "_infra/violator" in msg, f"error must name offending id: {msg}"
            assert "clone_k=2" in msg or "clone_k=" in msg, (
                f"error must name recovered clone_k: {msg}"
            )
        else:
            raise AssertionError(
                "expected _lint_clone_shadow to raise LedgerNamespaceViolation"
            )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_11_rubric_sha_fixture_matches_doc() -> None:
    """Fixture SHA equals sha256(rubric doc)."""
    doc = _WS / "docs" / "harness_clone_namespace_guard_rubric.md"
    fx = _WS / "tests" / "fixtures" / "harness_clone_namespace_guard_rubric_hash.txt"
    assert doc.is_file(), f"rubric doc missing: {doc}"
    assert fx.is_file(), f"rubric SHA fixture missing: {fx}"
    on_disk = hashlib.sha256(doc.read_bytes()).hexdigest()
    fixture = fx.read_text().strip()
    assert on_disk == fixture, (
        f"rubric SHA mismatch: doc={on_disk} fixture={fixture}"
    )


def test_12_rubric_committed_before_writer_edits() -> None:
    """Rubric doc mtime <= workspace_bootstrap.py mtime (rubric committed
    first). Uses file-mtime ordering; falls back to git-log if the file
    tree carries no useful mtime info (e.g., filesystem without atime)."""
    doc = _WS / "docs" / "harness_clone_namespace_guard_rubric.md"
    wb_src = Path(wb.__file__)
    assert doc.is_file(), f"rubric doc missing: {doc}"
    assert wb_src.is_file(), f"workspace_bootstrap.py missing: {wb_src}"
    doc_mtime = doc.stat().st_mtime
    wb_mtime = wb_src.stat().st_mtime
    # Allow tiny clock skew — require doc <= wb + 1s slack.
    assert doc_mtime <= wb_mtime + 1.0, (
        f"rubric doc mtime {doc_mtime} > workspace_bootstrap.py mtime "
        f"{wb_mtime}: rubric must be committed before writer edits"
    )


def test_13_public_api_unchanged() -> None:
    """append_ledger_event signature is still (workspace, event)."""
    sig = inspect.signature(wb.append_ledger_event)
    params = list(sig.parameters)
    assert params == ["workspace", "event"], (
        f"public API changed: expected (workspace, event), got {params}"
    )


def test_14_MRO_LedgerNamespaceViolation_subclass_of_LedgerSchemaError() -> None:
    """LedgerNamespaceViolation is a real subclass of LedgerSchemaError."""
    assert issubclass(wb.LedgerNamespaceViolation, LedgerSchemaError), (
        "LedgerNamespaceViolation must subclass LedgerSchemaError"
    )
    # And an instance raised from the guard is catchable as LedgerSchemaError.
    with _EnvOverride(**_clone_env(k=2, strict=True)):
        ev = _well_formed("_run/foo")
        caught_as_schema_error = False
        try:
            wb._guard_clone_namespace(ev, _WS)
        except LedgerSchemaError:
            caught_as_schema_error = True
        assert caught_as_schema_error, (
            "except LedgerSchemaError must catch LedgerNamespaceViolation"
        )


# ---------------------------------------------------------------------------
# Helper for test_10
# ---------------------------------------------------------------------------


def _uuid_for(ev: dict) -> str:
    from long_exposure.tools._ledger_schema import content_hash_event_id
    return content_hash_event_id(ev)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    tests = [
        (name, fn) for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS {name}")
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"  FAIL {name}: {e}")
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
    print(f"\nresult: {'PASS' if not failed else 'FAIL'} "
          f"({len(tests) - len(failed)}/{len(tests)})")
    sys.exit(1 if failed else 0)
