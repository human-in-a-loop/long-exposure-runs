"""RC10 Musical Time + Repetition (c57 clone-1, W2 branch).

Introduces musical time as a first-class primitive: tempo, beat, downbeat,
16th-note grid + micro-timing offsets, loop-length detection, per-repeat
consensus aggregator, and cross-stem energy seed table.

Rubric: ``docs/rc10_musical_time_rubric.md`` (SHA pinned in
``data/rc10_musical_time/rubric_hash.txt``).

READ-ONLY anchors this branch depends on:
    - ``scripts/palette_render/render_stem.py`` (c33 do-not-touch)
    - ``docs/m_recreate_2_accurate_small_set_rubric_v2.md`` (c50)
    - ``data/recreate_v2/focus_set_v2.json``
    - ``data/recreate_v2/baseline/<sha16>/rc9_6stem/*.wav``
    - ``data/recreate_v2/baseline/<sha16>/rc5_tempo_bpm.json``
"""

RUBRIC_SHA_ANCHOR = "635499e666f54d08d66b7e74b8bd9e3106353a215022e73d179413d6f07a1ee6"
RUBRIC_HASH_PATH = "data/rc10_musical_time/rubric_hash.txt"
BASELINE_ANCHOR_ROOT = "data/recreate_v2/baseline"
FOCUS_SET_V2_PATH = "data/recreate_v2/focus_set_v2.json"
OUTPUT_ROOT = "data/rc10_musical_time"

STEM_ORDER = ("drums", "bass", "vocals", "guitar", "piano", "other")

# c48 env-flag defaults (OFF); c49+ default flip is outside worker scope.
import os as _os
_os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
_os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")
