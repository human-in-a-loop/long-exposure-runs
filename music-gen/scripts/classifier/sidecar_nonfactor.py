"""M-CLASS-1 non-factor sidecar writer.

Purpose
-------
The campaign prompt says non-factors (genre, country, artist, release
date, language, live-vs-recorded label, lyrics-vs-instrumental, etc.)
MAY be recorded for audit, but MUST NEVER be consumed by any downstream
decision, model input, curation branch, or judge.

Documentation alone does not enforce this. This module enforces it with
three structural barriers:

  1. **Path isolation.** All sidecar files land under
     `data/classifier/_nonfactor/`. The leading underscore is a
     filesystem-level "keep out"; STRUCTURE.md documents this folder
     as off-limits to any module except this one.

  2. **Namespace isolation.** This module has no public reader named
     `read_features`, `load`, `get_sidecar`, or anything a well-meaning
     downstream author would grep for. The only reader is
     `read_for_audit_only(clip_id, *, i_understand_this_is_non_factor=True)`.

  3. **Type isolation.** Every string field of a returned `AuditRecord`
     is wrapped in `NonFactorValue(raw=...)`. Its `__str__` /
     `__add__` / `__hash__` / json encoding all raise `TypeError`
     unless the caller explicitly calls `.audit_unwrap()`. A
     downstream `features_dict["genre"] = record.genre` fails at the
     dict assignment layer, not silently.

The static-analysis fourth layer lives in `tests/test_sidecar_isolation.py`
and is the enforcement mechanism the whole rule leans on.
"""
from __future__ import annotations
from . import _interp  # noqa: F401

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional


NONFACTOR_ROOT = Path("data/classifier/_nonfactor")

_UNWRAP_MARKER = object()  # sentinel proving audit_unwrap() was called


class NonFactorValue:
    """Wrapper that makes accidental use of a non-factor value fail hard.

    Instances are frozen-like: `raw` is settable only via the constructor;
    every operation that would let this value slip into downstream code
    (string concatenation, being written to a features dict, being JSON
    encoded, being hashed into a caching key, participating in equality)
    raises TypeError.

    The ONLY way to see the underlying value is to explicitly call
    `.audit_unwrap()`, whose name and signature broadcast intent.
    """
    __slots__ = ("_raw",)

    def __init__(self, raw: Any):
        object.__setattr__(self, "_raw", raw)

    def audit_unwrap(self) -> Any:
        """Return the raw underlying value. Named to make greps trivial.

        Any downstream module that calls this without an audit
        justification is caught by the static-analysis test in
        tests/test_sidecar_isolation.py.
        """
        return object.__getattribute__(self, "_raw")

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<NON_FACTOR_DO_NOT_USE: {raw!r}>"

    # --- Load-bearing refusals ---

    def __str__(self) -> str:  # e.g. f"...{v}..."
        raise TypeError(
            "NonFactorValue cannot be converted to str. This value is a "
            "recorded non-factor and must not be consumed downstream. "
            "Call .audit_unwrap() only inside an auditing context."
        )

    def __add__(self, other):
        raise TypeError("NonFactorValue cannot be concatenated.")

    def __radd__(self, other):
        raise TypeError("NonFactorValue cannot be concatenated.")

    def __eq__(self, other):
        raise TypeError(
            "NonFactorValue equality is forbidden (equality would leak "
            "non-factor info into decision logic)."
        )

    def __hash__(self):
        raise TypeError("NonFactorValue is not hashable (cannot be a dict key).")

    def __setattr__(self, k, v):
        raise TypeError("NonFactorValue is immutable.")

    def __bool__(self):
        raise TypeError(
            "NonFactorValue cannot participate in boolean expressions."
        )


@dataclass(frozen=True)
class AuditRecord:
    """Frozen snapshot of the non-factor sidecar for one clip.

    Every string field is a `NonFactorValue`. Numeric fields (probabilities
    of non-music AudioSet classes) are plain floats — those are NOT
    genre/artist/etc.; they are model-internal, not curatorial metadata.
    """
    clip_id: str
    genre: NonFactorValue
    country: NonFactorValue
    date_released: NonFactorValue
    language: NonFactorValue
    instrumental_vs_lyrics: NonFactorValue
    live_vs_recorded: NonFactorValue
    artist: NonFactorValue
    # Non-music-class posteriors from the tagger (audit-only, NOT features).
    prob_speech: float
    prob_applause: float
    prob_ambient: float
    # For provenance:
    model_id: str
    weights_sha256: str


def write_sidecar(
    clip_id: str,
    *,
    genre: Optional[str],
    country: Optional[str],
    date_released: Optional[str],
    language: Optional[str],
    instrumental_vs_lyrics: Optional[str],
    live_vs_recorded: Optional[str],
    artist: Optional[str],
    prob_speech: float,
    prob_applause: float,
    prob_ambient: float,
    model_id: str,
    weights_sha256: str,
    root: Path = NONFACTOR_ROOT,
) -> Path:
    """Write one non-factor sidecar to `<root>/<clip_id>.json`.

    Fields default to `null` on disk if None — the sidecar schema is what's
    being validated this cycle, not the completeness of the labels.
    """
    _assert_id_safe(clip_id)
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "__non_factor_do_not_consume__": True,
        "clip_id": clip_id,
        "genre": genre,
        "country": country,
        "date_released": date_released,
        "language": language,
        "instrumental_vs_lyrics": instrumental_vs_lyrics,
        "live_vs_recorded": live_vs_recorded,
        "artist": artist,
        "audit_only_non_music_probs": {
            "SPEECH": float(prob_speech),
            "APPLAUSE": float(prob_applause),
            "AMBIENT": float(prob_ambient),
        },
        "model_id": model_id,
        "weights_sha256": weights_sha256,
        "sidecar_schema_version": 1,
    }
    out = root / f"{clip_id}.json"
    out.write_text(json.dumps(payload, indent=2))
    return out


def read_for_audit_only(
    clip_id: str,
    *,
    i_understand_this_is_non_factor: bool,
    root: Path = NONFACTOR_ROOT,
) -> AuditRecord:
    """The ONLY reader. Deliberately awkward signature by design.

    Downstream authors who reach for this reader must:
      (a) name the keyword-only argument correctly, an assertion in itself;
      (b) explicitly pass True to it (silence-of-omission won't work);
      (c) then unwrap every string field via .audit_unwrap() to get the
          plain value — a second grep-catchable call site.

    All of that lands in the static-analysis test as forbidden imports
    outside `scripts/classifier/` and forbidden opens of `_nonfactor/`.
    """
    if i_understand_this_is_non_factor is not True:
        raise RuntimeError(
            "read_for_audit_only refuses to run without an explicit "
            "i_understand_this_is_non_factor=True. This is by design; see "
            "scripts/classifier/sidecar_nonfactor.py docstring."
        )
    _assert_id_safe(clip_id)
    path = root / f"{clip_id}.json"
    raw = json.loads(path.read_text())
    if not raw.get("__non_factor_do_not_consume__"):
        raise ValueError(
            f"sidecar {path} missing __non_factor_do_not_consume__ marker "
            "— refusing to read (likely wrong file)"
        )
    probs = raw["audit_only_non_music_probs"]
    return AuditRecord(
        clip_id=raw["clip_id"],
        genre=NonFactorValue(raw["genre"]),
        country=NonFactorValue(raw["country"]),
        date_released=NonFactorValue(raw["date_released"]),
        language=NonFactorValue(raw["language"]),
        instrumental_vs_lyrics=NonFactorValue(raw["instrumental_vs_lyrics"]),
        live_vs_recorded=NonFactorValue(raw["live_vs_recorded"]),
        artist=NonFactorValue(raw["artist"]),
        prob_speech=float(probs["SPEECH"]),
        prob_applause=float(probs["APPLAUSE"]),
        prob_ambient=float(probs["AMBIENT"]),
        model_id=raw["model_id"],
        weights_sha256=raw["weights_sha256"],
    )


def _assert_id_safe(clip_id: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9._\-]+", clip_id or ""):
        raise ValueError(f"unsafe clip_id: {clip_id!r}")
