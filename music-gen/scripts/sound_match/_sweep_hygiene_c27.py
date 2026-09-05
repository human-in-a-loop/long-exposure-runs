#!/usr/bin/python3
"""Canonical sweep-storage-hygiene helpers per OPERATOR DIRECTIVE 2026-09-05.

Fixes the c26 stage-2 sweep failure mode where drivers batch-rendered every
candidate WAV to disk before scoring (hit 90 % disk usage on WIG + Disco A).

Contract (per operator directive, brief c27 Track A):
- render -> score -> delete each candidate before rendering the next
- retain only the running top-K by composite (default K=5)
- delete all non-pin WAVs after each pin is emitted
- df guard: prune first if usage >= 85 %; abort if still >= 90 %
- working audio budget: <=500 MB per instrument per song at any moment

This module is the SINGLE SOURCE OF TRUTH for hygiene going forward. Drivers
import from here; do NOT re-implement.

Discipline (AST-scannable): no PRNG, no sidecar_nonfactor, no VST3 state
APIs, no --verify-det. Interpreter guard on every consumer.
"""
from __future__ import annotations

import heapq
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional


# ------- pure helpers -------

def _dir_size_bytes(p: Path) -> int:
    """Recursive size in bytes (missing dir -> 0)."""
    if not p.exists():
        return 0
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def _disk_usage_pct(path: Path) -> float:
    """DIAGNOSTIC ONLY - advisory percentage. Includes root-reserved blocks
    (statvfs f_blocks denominator), so on ext4 with 5 % reserved this reads
    ~14 pp higher than `df -h`. Do NOT use as an abort gate; use _disk_ok.
    """
    st = os.statvfs(str(path))
    total = st.f_blocks * st.f_frsize
    free = st.f_bavail * st.f_frsize
    return 100.0 * (1.0 - free / max(total, 1))


def _disk_free_pct_user(path: Path) -> float:
    """User-available free space as percent of user-visible total.
    Excludes root-reserved blocks. Matches `df -h` semantics.
    """
    st = os.statvfs(str(path))
    total_user = (st.f_blocks - (st.f_blocks - st.f_bavail)) * st.f_frsize
    # Equivalent to available/total on the user-visible partition.
    avail = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = total - st.f_bfree * st.f_frsize
    denom = used + avail
    if denom <= 0:
        return 100.0
    return 100.0 * avail / denom


def _disk_used_pct_user(path: Path) -> float:
    """User-visible used percent (mirrors `df -h`). Used by df guard."""
    return 100.0 - _disk_free_pct_user(path)


def _disk_ok(path: Path, budget_bytes: int, safety_factor: float = 2.0) -> bool:
    """Absolute-budget disk check (c10 semantics preserved).

    Contract: "do we have room for the sweep's working audio budget * safety?"
    NOT "is the disk absolutely empty". budget_bytes<=0 short-circuits True.
    Uses f_bavail (user-available; excludes reserved).
    """
    if budget_bytes <= 0:
        return True
    st = os.statvfs(str(path))
    avail_bytes = st.f_bavail * st.f_frsize
    return avail_bytes >= budget_bytes * safety_factor


# ------- df guard: prune -> abort per operator directive -------

def _prune_stale_sweep_audio(
    root: Path, min_age_seconds: float = 60.0
) -> list[str]:
    """Delete all `*.wav` under `<root>/data/v4/profiles/*/*_sweep_stage*/`
    older than `min_age_seconds`. Returns list of pruned paths.

    Called by df_guard_before_stage() when usage >= prune_pct. Age gate
    prevents deleting the current sweep's in-flight renders.
    """
    pruned: list[str] = []
    now = time.time()
    profiles = root / "data" / "v4" / "profiles"
    if not profiles.exists():
        return pruned
    for song_dir in profiles.iterdir():
        if not song_dir.is_dir():
            continue
        for sweep_dir in song_dir.glob("*_sweep_stage*"):
            if not sweep_dir.is_dir():
                continue
            for wav in sweep_dir.rglob("*.wav"):
                try:
                    age = now - wav.stat().st_mtime
                except FileNotFoundError:
                    continue
                if age < min_age_seconds:
                    continue
                try:
                    wav.unlink()
                    pruned.append(str(wav))
                except OSError:
                    pass
    return pruned


def df_guard_before_stage(
    workspace_root: Path,
    stage_dir: Path,
    prune_pct: float = 85.0,
    abort_pct: float = 90.0,
) -> dict[str, Any]:
    """Operator-mandated df guard called BEFORE every sweep stage entry.

    Behavior per OPERATOR DIRECTIVE 2026-09-05:
      1. Check user-visible df usage on stage_dir's filesystem.
      2. If usage >= prune_pct: prune stale sweep audio via
         _prune_stale_sweep_audio(workspace_root).
      3. Re-check usage. If still >= abort_pct: raise RuntimeError (FD-1).
      4. Return status dict for logging.

    Never silently retries. FD-1 halt on any abort_pct breach.
    """
    pct_before = _disk_used_pct_user(stage_dir)
    pruned: list[str] = []
    if pct_before >= prune_pct:
        pruned = _prune_stale_sweep_audio(workspace_root)
    pct_after = _disk_used_pct_user(stage_dir)
    status = {
        "used_pct_before": round(pct_before, 2),
        "used_pct_after": round(pct_after, 2),
        "prune_pct_threshold": prune_pct,
        "abort_pct_threshold": abort_pct,
        "n_pruned": len(pruned),
        "pruned_paths": pruned[:20],  # bounded
    }
    if pct_after >= abort_pct:
        raise RuntimeError(
            f"df-guard abort: usage {pct_after:.1f} % >= abort ceiling "
            f"{abort_pct} % after pruning {len(pruned)} files - halting per FD-1"
        )
    return status


# ------- running top-K heap for per-candidate score-and-delete -------

class RunningTopK:
    """Bounded top-K tracker for sweep cells.

    On push(row):
      - if len(heap) < k: keep the cell's WAV; add to heap.
      - else if new row beats worst-in-heap (lower composite = better):
          evict worst, DELETE its WAV, add new row.
      - else: DELETE new row's WAV immediately (does not enter top-K).

    Purpose: enforce operator-mandated "render->score->delete each candidate
    WAV before rendering the next; keep only the running top-K audio".

    The heap is a max-heap by composite (Python heapq is min-heap; we push
    -composite as the sort key so the "worst" surface at top). Ties broken
    by SHA-256-tiebreak on render_wav_sha to preserve determinism.
    """

    def __init__(
        self,
        k: int = 5,
        key: Optional[Callable[[dict[str, Any]], float]] = None,
        delete_fn: Optional[Callable[[Path], None]] = None,
    ):
        if k < 1:
            raise ValueError("k must be >= 1")
        self.k = k
        self._key = key or (lambda r: r["composite"])
        self._delete_fn = delete_fn or self._default_delete
        # Heap entries: (-composite, tiebreak, row_dict). Max-heap by composite
        # via negation; worst (highest composite) at index 0.
        self._heap: list[tuple[float, str, dict[str, Any]]] = []
        self._n_pushed = 0
        self._n_evicted = 0
        self._n_rejected = 0

    @staticmethod
    def _default_delete(path: Path) -> None:
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass

    def _tiebreak(self, row: dict[str, Any]) -> str:
        sha = row.get("render_wav_sha") or row.get("render_sha256") or ""
        return str(sha)

    def push(self, row: dict[str, Any]) -> Optional[str]:
        """Push a scored cell. Returns path of the WAV that was DELETED
        (evicted or rejected on entry), or None if the row was kept.

        row must carry 'render_path' (str) and the key field (default 'composite').
        Non-finite composite (NaN/inf) is auto-rejected: deletes and skips.
        """
        self._n_pushed += 1
        try:
            comp = float(self._key(row))
        except (TypeError, ValueError):
            comp = float("inf")
        if comp != comp or comp == float("inf"):
            # NaN or inf: reject on entry.
            path = Path(row.get("render_path", ""))
            self._delete_fn(path)
            self._n_rejected += 1
            return str(path) if path else None

        tie = self._tiebreak(row)
        # Negation so heap[0] is worst (highest composite).
        entry = (-comp, tie, row)
        if len(self._heap) < self.k:
            heapq.heappush(self._heap, entry)
            return None
        worst = self._heap[0]
        # worst has -comp_worst; comp_worst = -worst[0]. New comp better if
        # comp < comp_worst i.e. -comp > worst[0]. Equivalent: entry > worst.
        if entry > worst:
            evicted = heapq.heapreplace(self._heap, entry)
            path = Path(evicted[2].get("render_path", ""))
            self._delete_fn(path)
            self._n_evicted += 1
            return str(path) if path else None
        else:
            # New row is worse - reject on entry.
            path = Path(row.get("render_path", ""))
            self._delete_fn(path)
            self._n_rejected += 1
            return str(path) if path else None

    def kept_rows(self) -> list[dict[str, Any]]:
        """Return rows currently in top-K, sorted best->worst (ascending composite)."""
        rows = [row for _, _, row in self._heap]
        rows.sort(key=lambda r: (float(self._key(r)) if self._key(r) is not None else float("inf")))
        return rows

    def kept_paths(self) -> list[str]:
        return [str(r.get("render_path", "")) for r in self.kept_rows()]

    def stats(self) -> dict[str, int]:
        return {
            "n_pushed": self._n_pushed,
            "n_kept": len(self._heap),
            "n_evicted": self._n_evicted,
            "n_rejected": self._n_rejected,
        }


def prune_after_pin(kept_rows: list[dict[str, Any]], pinned_paths: set[str]) -> list[str]:
    """After a profile is pinned, delete every kept WAV not in pinned_paths.

    Per operator directive: "After each pin, delete all remaining sweep
    audio for that instrument." pinned_paths is the set of WAV paths
    referenced by the emitted profile (usually just {top1_render_path}).
    """
    deleted: list[str] = []
    for r in kept_rows:
        p = str(r.get("render_path", ""))
        if not p or p in pinned_paths:
            continue
        path = Path(p)
        try:
            if path.exists():
                path.unlink()
                deleted.append(p)
        except OSError:
            pass
    return deleted


# ------- policy constants -------

DEFAULT_KEEP_TOP = 5
DEFAULT_MAX_AUDIO_MB = 500
DF_GUARD_PRUNE_PCT = 85.0
DF_GUARD_ABORT_PCT = 90.0
POLICY_VERSION = "c27-sweep-hygiene-fix-2026-09-05"
