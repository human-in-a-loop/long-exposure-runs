"""AudioSet-527 → project-taxonomy (5 class) mapper.

The project taxonomy is FIXED by the campaign prompt:
    SPEECH, APPLAUSE, AMBIENT, MUSIC_LIVE, MUSIC_RECORDED.

MUSIC_LIVE is a composite rule (AudioSet's `Live music` leaf alone is
low-recall; we require music mass + a live/applause cue). See
`taxonomy_map.yaml`.
"""
from __future__ import annotations
from . import _interp  # noqa: F401 — interpreter guard

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import yaml


TAXONOMY_CLASSES: Tuple[str, ...] = (
    "SPEECH", "APPLAUSE", "AMBIENT", "MUSIC_LIVE", "MUSIC_RECORDED",
)


@dataclass(frozen=True)
class TaxonomyDecision:
    verdict: str                       # one of TAXONOMY_CLASSES
    class_probs: Dict[str, float]      # 5-class probs (sum ~1)
    music_mass: float                  # from MUSIC bucket
    live_leaf_mass: float              # from LIVE_MUSIC_LEAF bucket
    applause_mass: float               # from APPLAUSE bucket
    low_confidence: bool               # music in ambiguous band
    top_audioset: List[Tuple[str, float]]  # top-5 (name, prob) for audit

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "class_probs": self.class_probs,
            "music_mass": self.music_mass,
            "live_leaf_mass": self.live_leaf_mass,
            "applause_mass": self.applause_mass,
            "low_confidence": self.low_confidence,
            "top_audioset": self.top_audioset,
        }


class TaxonomyMapper:
    """Reduce a PANNs-style 527-D distribution to the 5-class taxonomy."""

    def __init__(
        self,
        audioset_labels_csv: str | Path,
        taxonomy_yaml: str | Path,
    ) -> None:
        self._mid_to_idx, self._idx_to_name = _load_audioset_index(
            Path(audioset_labels_csv)
        )
        with open(taxonomy_yaml) as f:
            cfg = yaml.safe_load(f)
        dm = cfg["direct_map"]
        self._buckets: Dict[str, List[int]] = {}
        for bucket in ("SPEECH", "APPLAUSE", "AMBIENT", "MUSIC", "LIVE_MUSIC_LEAF"):
            entries = dm.get(bucket, [])
            self._buckets[bucket] = [
                self._mid_to_idx[e["mid"]]
                for e in entries
                if e["mid"] in self._mid_to_idx
            ]
        self._composite = cfg["composite_rules"]
        self._lo_band = tuple(cfg["low_confidence_music_band"])

    def reduce(self, dist527: np.ndarray) -> TaxonomyDecision:
        assert dist527.shape == (527,), f"expected shape (527,), got {dist527.shape}"
        masses = {
            bucket: float(np.sum(dist527[idxs])) if idxs else 0.0
            for bucket, idxs in self._buckets.items()
        }
        speech = masses["SPEECH"]
        applause = masses["APPLAUSE"]
        ambient = masses["AMBIENT"]
        music = masses["MUSIC"]
        live_leaf = masses["LIVE_MUSIC_LEAF"]

        cr = self._composite
        is_music = music >= cr["music_min"]
        is_live = (
            live_leaf >= cr["live_leaf_min"]
            or applause >= cr["applause_min"]
        )

        if is_music and is_live:
            music_live = music
            music_recorded = 0.0
        elif is_music:
            music_live = 0.0
            music_recorded = music
        else:
            music_live = 0.0
            music_recorded = 0.0

        raw = {
            "SPEECH": speech,
            "APPLAUSE": applause,
            "AMBIENT": ambient,
            "MUSIC_LIVE": music_live,
            "MUSIC_RECORDED": music_recorded,
        }
        total = sum(raw.values())
        if total <= 0:
            raw["AMBIENT"] = 1.0
            total = 1.0
        probs = {k: v / total for k, v in raw.items()}
        verdict = max(probs, key=probs.get)

        low_conf = self._lo_band[0] <= music <= self._lo_band[1]

        top_idx = np.argsort(dist527)[::-1][:5]
        top = [(self._idx_to_name[int(i)], float(dist527[int(i)])) for i in top_idx]

        return TaxonomyDecision(
            verdict=verdict,
            class_probs=probs,
            music_mass=music,
            live_leaf_mass=live_leaf,
            applause_mass=applause,
            low_confidence=low_conf,
            top_audioset=top,
        )


def _load_audioset_index(csv_path: Path):
    mid_to_idx: Dict[str, int] = {}
    idx_to_name: Dict[int, str] = {}
    with open(csv_path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            idx = int(row[0]); mid = row[1]; name = row[2]
            mid_to_idx[mid] = idx
            idx_to_name[idx] = name
    return mid_to_idx, idx_to_name
