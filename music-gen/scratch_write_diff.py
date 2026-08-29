"""Emit data/ear_v1/leak_test_diff_manifest.json."""
import json, subprocess
from pathlib import Path

OLD_SHA = "6de3b28d6c046b0a7e55673450e0ca03fc8b91021addd22131229cfbbf0a1ec0"
NEW_SHA = "f30e0f49ac6b5158e6a5430383e64ec0fbe72ce537b2e94f7cb133c7a0c3506e"

# Extract changed line ranges from `git diff --unified=0` @@ hunks.
r = subprocess.run(
    ["git", "diff", "--unified=0", "HEAD", "--", "scripts/ear/leak_test.py"],
    capture_output=True, text=True, check=True,
)
hunks = []
for ln in r.stdout.splitlines():
    if ln.startswith("@@"):
        # @@ -<oldstart>[,<oldcount>] +<newstart>[,<newcount>] @@ ...
        try:
            parts = ln.split()
            old_side = parts[1]  # "-a,b"
            new_side = parts[2]  # "+c,d"
            def _parse(sig):
                sig = sig[1:]  # strip sign
                if "," in sig:
                    s, n = sig.split(",")
                    return int(s), int(n)
                return int(sig), 1
            os_, on_ = _parse(old_side)
            ns_, nn_ = _parse(new_side)
            hunks.append({
                "old_start": os_, "old_count": on_,
                "new_start": ns_, "new_count": nn_,
            })
        except Exception:
            pass

# Compress into changed_line_ranges on the NEW file.
changed_ranges = []
for h in hunks:
    if h["new_count"] > 0:
        s = h["new_start"]
        e = s + h["new_count"] - 1
        changed_ranges.append([s, e])
    else:
        # Pure deletion: point at the site of deletion.
        changed_ranges.append([h["new_start"], h["new_start"]])

manifest = {
    "file": "scripts/ear/leak_test.py",
    "old_sha256": OLD_SHA,
    "new_sha256": NEW_SHA,
    "changed_line_ranges": changed_ranges,
    "authorization": "c38 anchor-preservation authorization; retires "
                     "S = max(S_model, S_resid) line under c37 clone-1 F1 "
                     "pooled-variance-with-small-cell-adjustment.",
    "statistic_version": "F1_pooled_variance_v1",
    "surgery_notes": [
        "Introduced STATISTIC_VERSION module constant.",
        "Introduced f1_pooled_variance_statistic(y_true, y_pred, leak_labels) -> float.",
        "Rewrote _leak_stats to return a single scalar (F1) instead of "
        "the (S, S_model, S_resid) triple.",
        "Retired the c6 `max(S_model, S_resid)` combined-statistic line.",
        "Dropped S_model / S_resid fields from LeakRow; added statistic_version "
        "field pinned to 'F1_pooled_variance_v1'.",
    ],
}

out = Path("data/ear_v1/leak_test_diff_manifest.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(manifest, indent=2, sort_keys=True))
print("wrote", out)
