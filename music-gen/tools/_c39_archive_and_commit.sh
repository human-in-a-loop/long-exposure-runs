#!/usr/bin/env bash
# Archive c39 scratch to tools/stale/, commit c39 scripts+data+docs+tests.
set -euo pipefail
cd /home/user/long-exposure-runs/music-gen

mkdir -p tools/stale

# Move c39 scratch (exclude the archive script + the merge_report writer)
for f in _c39_fixture_inspect.py _c39_duration_analysis.py _c39_probe_output.py \
         _c39_investigate_drift.py _c39_anchor_preservation.py _c39_emit_ledger.py \
         _c39_run_normalize.sh _c39_test_mscore3.sh _c39_double_run.sh \
         _c39_run_all.sh _c39_run_tests.sh _c39_emit_ledger.sh \
         _c39_git_commit_rubric.sh _c39_write_merge_report.py; do
  if [ -f "tools/$f" ]; then
    mv "tools/$f" "tools/stale/$f" && echo "archived: $f"
  fi
done

# Commit c39 substantive artifacts
git add scripts/score_bridge_v2/normalize_v2.py
git add scripts/score_bridge_v2/run_normalizer_v2.py
git add tests/test_score_bridge_normalizer_v2.py
git add docs/score_bridge_real_audio_quantization_normalizer_v2_report.md
# tools/stale gitignored — not committed

git commit -m "M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2: scripts + tests + report + data (c39 clone-1)

Verdict: QUANTIZATION_NORMALIZER_V2_FAILS (event_count_wrong).
mscore3 3.2.3 now accepts fully canonicalized fixture (rc=0, byte-det × 2)
but drops 3 events (192/195). Divisions/type/dot arithmetic mismatch
confirmed necessary but not sufficient — tie-boundary residuals
(31/n patterns) remain unfixed. rubric_hash=4dfe067f... committed at
904df26 BEFORE any script (mtime+git-log dual gate satisfied).
18/18 tests pass. 19 anchors preserved (5 SHA-verified).
c40 handoff seed HS-1: tie-pair rewriting of 23 residual durations.

Co-Authored-By: c39-worker-clone-1 <noreply@anthropic.com>"

echo "---"
git log --oneline -3
