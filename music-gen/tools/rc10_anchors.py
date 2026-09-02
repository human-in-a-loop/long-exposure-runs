"""Snapshot anchor preservation SHAs for RC10 Branch C (≥25 anchors)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

WS = Path(__file__).resolve().parent.parent


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


anchors = []
# c50 v2 rubric
anchors.append({"path": "docs/m_recreate_2_accurate_small_set_rubric_v2.md",
                "sha256": sha(WS / "docs/m_recreate_2_accurate_small_set_rubric_v2.md"),
                "role": "v2_rubric_doc"})
anchors.append({"path": "data/recreate_v2/rubric_hash_v2.txt",
                "sha256": sha(WS / "data/recreate_v2/rubric_hash_v2.txt"),
                "role": "v2_rubric_hash_pin"})

# c51 Branch A verdict
anchors.append({"path": "data/rc1_rc9_impl/verdict.json",
                "sha256": sha(WS / "data/rc1_rc9_impl/verdict.json"),
                "role": "c51_branch_a_verdict_readonly"})

# c52 render_stem.py
anchors.append({"path": "scripts/palette_render/render_stem.py",
                "sha256": sha(WS / "scripts/palette_render/render_stem.py"),
                "role": "c52_render_stem_do_not_touch"})

# c53-clone-0 rc5 baseline (all 5)
focus = json.loads((WS / "data/recreate_v2/focus_set_v2.json").read_text())
for s in focus["songs"]:
    sha16 = s["audio_sha16"]
    rc5 = WS / f"data/rc5_impl/{sha16}/rc5_tempo_estimate.json"
    if rc5.exists():
        anchors.append({"path": f"data/rc5_impl/{sha16}/rc5_tempo_estimate.json",
                        "sha256": sha(rc5), "role": "rc5_tempo_estimate"})

# all 10 baseline stems
for s in focus["songs"]:
    sha16 = s["audio_sha16"]
    for stem in ("vocals", "other"):
        p = WS / f"data/recreate_v2/baseline/{sha16}/rc9_6stem/{stem}.wav"
        anchors.append({"path": str(p.relative_to(WS)),
                        "sha256": sha(p), "role": f"baseline_{stem}"})

# c49 v1 rubric (should also be READ-ONLY)
c49 = WS / "docs/m_recreate_2_accurate_small_set_rubric.md"
if c49.exists():
    anchors.append({"path": "docs/m_recreate_2_accurate_small_set_rubric.md",
                    "sha256": sha(c49), "role": "c49_v1_rubric_readonly"})
c49_txt = WS / "data/recreate_v2/rubric_hash.txt"
if c49_txt.exists():
    anchors.append({"path": "data/recreate_v2/rubric_hash.txt",
                    "sha256": sha(c49_txt), "role": "c49_v1_rubric_hash_pin"})

# focus_set_v2
anchors.append({"path": "data/recreate_v2/focus_set_v2.json",
                "sha256": sha(WS / "data/recreate_v2/focus_set_v2.json"),
                "role": "focus_set_v2"})

# c49 rc0 baseline rollup (READ-ONLY)
rc0 = WS / "data/recreate_v2/rc0_baseline_rollup.json"
if rc0.exists():
    anchors.append({"path": "data/recreate_v2/rc0_baseline_rollup.json",
                    "sha256": sha(rc0), "role": "c49_rc0_baseline_rollup"})
# focus_set (v1) — c49 anchor
fs1 = WS / "data/recreate_v2/focus_set.json"
if fs1.exists():
    anchors.append({"path": "data/recreate_v2/focus_set.json",
                    "sha256": sha(fs1), "role": "c49_focus_set_v1"})

# RC10 own rubric (this cycle's canonical)
anchors.append({"path": "docs/rc10_other_vocals_rubric.md",
                "sha256": sha(WS / "docs/rc10_other_vocals_rubric.md"),
                "role": "rc10_rubric_doc"})
anchors.append({"path": "data/rc10_impl/other_vocals/rubric_hash.txt",
                "sha256": sha(WS / "data/rc10_impl/other_vocals/rubric_hash.txt"),
                "role": "rc10_rubric_hash_pin"})

out = {
    "milestone": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey (Branch C)",
    "clone": "clone-2",
    "cycle": 53,
    "n_anchors": len(anchors),
    "anchors": anchors,
}
(WS / "data/rc10_impl/other_vocals/anchor_preservation.json").write_text(
    json.dumps(out, indent=2, sort_keys=True) + "\n"
)
print(f"snapshot {len(anchors)} anchors")
