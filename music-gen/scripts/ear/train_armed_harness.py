"""M-EAR-1 armed harness — extends the cycle-8 egress-ready state machine
with TRAINING and TRAINED states.

Trigger contract:
    READY  -> TRAINING  when
        (a) `data/ear/rated_ready.flag` exists, AND
        (b) EITHER `data/ear/trained_v1.flag` is absent
            OR the ratings-manifest content-hash differs from the
            hash recorded inside `trained_v1.flag`.

TRAINING entry sanity check:
    Each ratings-manifest row is checked for audio resolvability under
    `data/ingestion/clips/`. If any row's audio is missing, transition
    goes IDLE -> FAILED with `failed_stage="training/audio_missing"`
    without invoking the training loop.

TRAINING body:
    Invokes `scripts.ear.train` in-process (deterministic, tests can
    swap via a hook). On rc=0 AND finite mean MAE, writes
    `data/ear/trained_v1.flag` with the ratings-manifest content-hash
    and transitions to TRAINED. On failure (subprocess rc != 0 or NaN
    loss), transitions to FAILED with `failed_stage="training/loop"`.

Idempotency:
    If the flag is present AND the checkpoint is present AND the
    ratings-manifest content-hash matches, a repeat invocation writes
    a single `{... "noop": true}` row to transitions.jsonl and exits.

Zero live network. Zero sidecar_nonfactor imports.
"""
# created: 2026-08-28T11:00:00Z  cycle: 11  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2)  milestone: M-EAR-1/armed-harness
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

import argparse
import hashlib
import json
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# NOTE: the harness reads and writes files; it never opens a socket.
# The AST-level integration test asserts the absence of network-lib
# imports and string references in this module.


class HState(Enum):
    """Extended state set: READY (chain-terminal from cycle-8) is the
    entry state for the training extension; TRAINING = firing;
    TRAINED = final; FAILED with `failed_stage in {training/loop,
    training/audio_missing}` = training failed."""
    READY = "READY"
    TRAINING = "TRAINING"
    TRAINED = "TRAINED"
    FAILED = "FAILED"


HTRANSITIONS: Dict[HState, set] = {
    HState.READY:    {HState.TRAINING, HState.FAILED},
    HState.TRAINING: {HState.TRAINED, HState.FAILED},
    HState.TRAINED:  set(),  # terminal until manifest hash changes
    HState.FAILED:   {HState.TRAINING},  # resumable via retry
}


class InvalidHarnessTransition(Exception):
    pass


@dataclass
class HClock:
    now: Callable[[], datetime]

    @staticmethod
    def system() -> "HClock":
        return HClock(now=lambda: datetime.now(timezone.utc))


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(text)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name
    os.replace(tmp_path, str(path))


def content_hash_manifest(manifest: Path) -> str:
    """SHA-256 of the ratings-manifest bytes."""
    return hashlib.sha256(manifest.read_bytes()).hexdigest()


@dataclass
class HPersisted:
    state: HState
    last_transition_utc: str
    manifest_hash: Optional[str]  # of the ratings manifest at last transition
    checkpoint_path: Optional[str]
    failed_stage: Optional[str]
    training_result_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "last_transition_utc": self.last_transition_utc,
            "manifest_hash": self.manifest_hash,
            "checkpoint_path": self.checkpoint_path,
            "failed_stage": self.failed_stage,
            "training_result_path": self.training_result_path,
        }

    @staticmethod
    def initial() -> "HPersisted":
        return HPersisted(HState.READY, "", None, None, None, None)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "HPersisted":
        return HPersisted(
            state=HState(d["state"]),
            last_transition_utc=d.get("last_transition_utc", ""),
            manifest_hash=d.get("manifest_hash"),
            checkpoint_path=d.get("checkpoint_path"),
            failed_stage=d.get("failed_stage"),
            training_result_path=d.get("training_result_path"),
        )


@dataclass
class TrainingHookResult:
    ok: bool
    mean_mae: float
    stderr_tail: str = ""
    returncode: Optional[int] = None
    training_result_path: Optional[str] = None
    checkpoint_path: Optional[str] = None


class TrainingHooks:
    """Injection point for the training subprocess call.

    Tests subclass this and override `run_training` with a no-op or a
    fake failure. The state machine only ever calls training through
    the instance it was constructed with; no direct subprocess.run
    lives in the machine body.
    """

    def __init__(self, features_dir: Path, out_dir: Path,
                 synth_valset: bool = False,
                 valset_manifest: Optional[Path] = None,
                 epochs: int = 200,
                 seed: int = 0):
        self.features_dir = Path(features_dir)
        self.out_dir = Path(out_dir)
        self.synth_valset = synth_valset
        self.valset_manifest = Path(valset_manifest) if valset_manifest else None
        self.epochs = epochs
        self.seed = seed

    def run_training(self, ratings_manifest: Path) -> TrainingHookResult:
        # In-process call — deterministic, no network. Also faster than
        # forking a subprocess (which would carry cache-warmth cost).
        from scripts.ear import train as _train_mod
        manifest = Path(ratings_manifest)
        if self.synth_valset and self.valset_manifest:
            synth = self.out_dir / "synth_ratings_manifest.tsv"
            _train_mod._synth_manifest_for_valset(
                self.valset_manifest, synth, self.features_dir, seed=self.seed)
            manifest = synth
            calibration = "synthetic_labels_only"
        else:
            calibration = "user_ratings"

        try:
            result = _train_mod.train(
                features_dir=self.features_dir,
                ratings_manifest=manifest,
                out_dir=self.out_dir,
                seed=self.seed,
                epochs=self.epochs,
                calibration=calibration,
            )
        except Exception as e:
            return TrainingHookResult(
                ok=False,
                mean_mae=float("nan"),
                stderr_tail=f"{type(e).__name__}: {e}",
                returncode=1,
            )
        import math
        ok = math.isfinite(result.mean_mae)
        # `result.checkpoint_path` is a basename ("corn_head_v1.pt");
        # resolve to a full path relative to this hook's out_dir so
        # the state.json's checkpoint field is a valid path callers
        # can .is_file() on.
        full_ckpt = str((self.out_dir / result.checkpoint_path).resolve())
        return TrainingHookResult(
            ok=ok,
            mean_mae=result.mean_mae,
            stderr_tail="" if ok else "non-finite mean_mae",
            returncode=0 if ok else 2,
            training_result_path=str((self.out_dir / "training_result.json").resolve()),
            checkpoint_path=full_ckpt,
        )


class ArmedHarness:
    """Extension of the egress-ready state machine.

    Reads state from `state_path` (JSON), appends transitions to
    `transitions_path` (JSONL), consults `rated_ready_flag` and
    `ratings_manifest` for gating, writes `trained_flag` on success.

    All file writes are POSIX-atomic (tempfile + os.replace on the
    same directory).
    """

    def __init__(
        self,
        state_path: Path,
        transitions_path: Path,
        rated_ready_flag: Path,
        ratings_manifest: Path,
        trained_flag: Path,
        training_out_dir: Path,
        hooks: Optional[TrainingHooks] = None,
        clock: Optional[HClock] = None,
        clips_dir: Optional[Path] = None,
    ):
        self.state_path = Path(state_path)
        self.transitions_path = Path(transitions_path)
        self.rated_ready_flag = Path(rated_ready_flag)
        self.ratings_manifest = Path(ratings_manifest)
        self.trained_flag = Path(trained_flag)
        self.training_out_dir = Path(training_out_dir)
        self.hooks = hooks if hooks is not None else TrainingHooks(
            features_dir=Path("data/ear/features"),
            out_dir=self.training_out_dir,
        )
        self.clock = clock if clock is not None else HClock.system()
        self.clips_dir = Path(clips_dir) if clips_dir else Path("data/ingestion/clips")

        if self.state_path.is_file():
            try:
                d = json.loads(self.state_path.read_text(encoding="utf-8"))
                self.persisted = HPersisted.from_dict(d)
            except (json.JSONDecodeError, KeyError, ValueError):
                self.persisted = HPersisted.initial()
        else:
            self.persisted = HPersisted.initial()

    def _persist(self) -> None:
        _atomic_write_text(
            self.state_path,
            json.dumps(self.persisted.to_dict(), indent=2, sort_keys=True) + "\n",
        )

    def _audit(self, from_state: HState, to_state: HState, reason: str,
               evidence: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        self.transitions_path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp_utc": _iso(self.clock.now()),
            "from_state": from_state.value,
            "to_state": to_state.value,
            "reason": reason,
            "evidence": evidence,
        }
        if extra:
            event.update(extra)
        with open(self.transitions_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")

    def _transition(self, to_state: HState, reason: str,
                    evidence: Any = None,
                    manifest_hash: Optional[str] = None,
                    checkpoint_path: Optional[str] = None,
                    failed_stage: Optional[str] = None,
                    training_result_path: Optional[str] = None) -> None:
        cur = self.persisted.state
        if to_state not in HTRANSITIONS.get(cur, set()) and to_state != cur:
            raise InvalidHarnessTransition(
                f"illegal transition {cur.value} -> {to_state.value} (reason={reason!r})"
            )
        self._audit(cur, to_state, reason, evidence)
        # Field lifetime rules.
        new_mh = manifest_hash if manifest_hash is not None else self.persisted.manifest_hash
        new_ck = checkpoint_path if checkpoint_path is not None else self.persisted.checkpoint_path
        new_fs = failed_stage if to_state == HState.FAILED else None
        new_tr = training_result_path if training_result_path is not None else self.persisted.training_result_path
        self.persisted = HPersisted(
            state=to_state,
            last_transition_utc=_iso(self.clock.now()),
            manifest_hash=new_mh,
            checkpoint_path=new_ck,
            failed_stage=new_fs,
            training_result_path=new_tr,
        )
        self._persist()

    def _noop(self, reason: str) -> None:
        """Idempotent no-op row on transitions.jsonl; state unchanged."""
        self._audit(self.persisted.state, self.persisted.state,
                    f"noop: {reason}", None, extra={"noop": True})

    def _audio_missing(self) -> Optional[str]:
        """Return the first ratings_manifest identifier whose audio file
        is not present under clips_dir, or None if all resolve.

        The heuristic: if the manifest has an `audio_sha256` column,
        require `{clips_dir}/{audio_sha256}.wav` to exist. Otherwise,
        require `{clips_dir}/{clip_id or video_id}.wav`. If the
        manifest has no rows at all, that also counts as missing.
        """
        try:
            with self.ratings_manifest.open() as fh:
                header = fh.readline().rstrip("\n").split("\t")
                rows = [dict(zip(header, ln.rstrip("\n").split("\t")))
                        for ln in fh if ln.strip()]
        except Exception as e:
            return f"manifest_unreadable:{type(e).__name__}"
        if not rows:
            return "empty_manifest"

        key = None
        for cand in ("audio_sha256", "clip_id", "video_id"):
            if cand in header:
                key = cand
                break
        if key is None:
            return "no_audio_join_key"
        for r in rows:
            ident = r.get(key, "")
            if not ident:
                return f"row_missing_{key}"
            if not (self.clips_dir / f"{ident}.wav").is_file():
                return f"{key}={ident}"
        return None

    def scan_and_advance(self) -> HState:
        cur = self.persisted.state

        # TRAINED: idempotent hold unless the manifest hash changes.
        if cur == HState.TRAINED:
            if not self.rated_ready_flag.is_file():
                # Ready flag went away; keep TRAINED terminal.
                self._noop("trained: no ready flag, hold")
                return cur
            if not self.ratings_manifest.is_file():
                self._noop("trained: no ratings manifest present")
                return cur
            cur_hash = content_hash_manifest(self.ratings_manifest)
            if cur_hash == self.persisted.manifest_hash:
                self._noop("trained + hash unchanged")
                return cur
            # Hash changed → retrain. TRAINED has no legal transition,
            # so we detour via READY-equivalent by resetting to READY-
            # then-TRAINING. But HTRANSITIONS from TRAINED is empty by
            # design. Instead we snap the persisted state back to READY
            # via a forced audit row and then take the standard READY
            # -> TRAINING path.
            self._audit(HState.TRAINED, HState.READY,
                        "retrain: manifest hash changed", cur_hash,
                        extra={"forced_reset": True})
            self.persisted = HPersisted(
                state=HState.READY,
                last_transition_utc=_iso(self.clock.now()),
                manifest_hash=self.persisted.manifest_hash,
                checkpoint_path=self.persisted.checkpoint_path,
                failed_stage=None,
                training_result_path=self.persisted.training_result_path,
            )
            self._persist()
            cur = HState.READY
            # fallthrough

        # FAILED: retry on next scan (fresh restart, not partial).
        if cur == HState.FAILED:
            if not self.rated_ready_flag.is_file():
                self._noop("failed: no ready flag, hold")
                return cur
            # Retry: FAILED -> TRAINING (fresh) — clean restart.
            return self._fire_training(from_state=HState.FAILED,
                                       reason="retry from FAILED")

        # READY: normal entry.
        if cur == HState.READY:
            if not self.rated_ready_flag.is_file():
                self._noop("ready: waiting for rated_ready.flag")
                return cur
            if not self.ratings_manifest.is_file():
                self._noop("ready: no ratings manifest present")
                return cur

            # Idempotency: if trained_flag exists and hash matches, no-op.
            if self.trained_flag.is_file() and self.persisted.checkpoint_path:
                try:
                    stored = json.loads(self.trained_flag.read_text(encoding="utf-8"))
                    stored_hash = stored.get("manifest_hash")
                except Exception:
                    stored_hash = None
                cur_hash = content_hash_manifest(self.ratings_manifest)
                if stored_hash == cur_hash and Path(self.persisted.checkpoint_path).is_file():
                    self._noop("idempotent: trained_flag hash matches manifest")
                    return cur

            return self._fire_training(from_state=HState.READY,
                                       reason="ready + flag present")

        # TRAINING: partial state (should not persist unless a crash happened
        # mid-run). On next scan, treat it like a FAILED with a diagnostic.
        if cur == HState.TRAINING:
            self._transition(HState.FAILED,
                             "training was in-flight — crash suspected",
                             evidence="mid_training_wake",
                             failed_stage="training/loop")
            return HState.FAILED

        return cur

    def _fire_training(self, from_state: HState, reason: str) -> HState:
        # Audio-missing pre-check.
        missing = self._audio_missing()
        if missing is not None:
            self._transition(HState.FAILED,
                             f"audio missing: {missing}",
                             evidence=missing,
                             failed_stage="training/audio_missing")
            return HState.FAILED

        # Enter TRAINING. Evidence is the manifest CONTENT hash (not its
        # path) so transitions.jsonl is byte-deterministic across runs
        # whose tmpdir differs.
        entry_hash = content_hash_manifest(self.ratings_manifest)
        self._transition(HState.TRAINING, reason,
                         evidence={"manifest_sha256": entry_hash})
        # Fire.
        result = self.hooks.run_training(self.ratings_manifest)
        if not result.ok:
            self._transition(HState.FAILED,
                             f"training loop failed: {result.stderr_tail[:120]}",
                             evidence={"returncode": result.returncode,
                                       "mean_mae": result.mean_mae},
                             failed_stage="training/loop")
            return HState.FAILED

        # Success. Write trained_flag with content-hash.
        cur_hash = content_hash_manifest(self.ratings_manifest)
        trained_payload = {
            "manifest_hash": cur_hash,
            "checkpoint_path": result.checkpoint_path,
            "mean_mae": result.mean_mae,
            "trained_at_utc": _iso(self.clock.now()),
        }
        _atomic_write_text(
            self.trained_flag,
            json.dumps(trained_payload, indent=2, sort_keys=True) + "\n",
        )
        self._transition(HState.TRAINED,
                         "training success",
                         evidence={"mean_mae": result.mean_mae},
                         manifest_hash=cur_hash,
                         checkpoint_path=result.checkpoint_path,
                         training_result_path=result.training_result_path)
        return HState.TRAINED


def _main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", type=Path, default=Path("data/ear/harness"))
    ap.add_argument("--rated-ready-flag", type=Path,
                    default=Path("data/ear/rated_ready.flag"))
    ap.add_argument("--ratings-manifest", type=Path,
                    default=Path("corpus/ratings/ratings_manifest.tsv"))
    ap.add_argument("--trained-flag", type=Path,
                    default=Path("data/ear/trained_v1.flag"))
    ap.add_argument("--training-out-dir", type=Path,
                    default=Path("data/ear/training_v1"))
    ap.add_argument("--clips-dir", type=Path,
                    default=Path("data/ingestion/clips"))
    ap.add_argument("--synth-valset", action="store_true",
                    help="Use the M-CLASS-1 synth-label valset instead of user ratings.")
    ap.add_argument("--valset-manifest", type=Path,
                    default=Path("data/classifier/valset/valset_manifest.tsv"))
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    state_dir = args.state_dir
    state_dir.mkdir(parents=True, exist_ok=True)
    hooks = TrainingHooks(
        features_dir=Path("data/ear/features"),
        out_dir=args.training_out_dir,
        synth_valset=args.synth_valset,
        valset_manifest=args.valset_manifest,
        epochs=args.epochs,
        seed=args.seed,
    )
    h = ArmedHarness(
        state_path=state_dir / "state.json",
        transitions_path=state_dir / "transitions.jsonl",
        rated_ready_flag=args.rated_ready_flag,
        ratings_manifest=args.ratings_manifest,
        trained_flag=args.trained_flag,
        training_out_dir=args.training_out_dir,
        hooks=hooks,
        clips_dir=args.clips_dir,
    )
    state = h.scan_and_advance()
    print(f"[harness] state = {state.value}")
    print(f"[harness] failed_stage = {h.persisted.failed_stage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
