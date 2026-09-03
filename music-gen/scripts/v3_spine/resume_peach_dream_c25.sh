#!/bin/bash
# Resume Peach Dream via c24 checkpointed driver — cycle-25 delivery variant.
#
# Mirrors resume_peach_dream_c24.sh (which is READ-ONLY anchor) but targets
# cycle25/ output per the c25 fanout brief. The checkpointed driver's cache
# keys are content-addressed (not cycle-scoped), so the c24 seed and any
# stage-cache entries already on disk under
# data/v3_spine/<sha16>/operator_section_c25_checkpointed/ HIT unchanged.
#
# Prerequisites (byte-verified on disk from c23 clone-1):
#   data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/section.wav
#   data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/rc9_6stem/*.wav
#
# Launches DETACHED (start_new_session=True) so session-boundary events in the
# launching agent cannot kill the multi-hour muscriptor stages again (c23 root
# cause). Poll the returned PID + logfile until exit or wall-budget expires.

set -euo pipefail

# Env pins mandatory for byte-determinism (must be set BEFORE any observed import).
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH=1756463424
export TZ=UTC
export LC_ALL=C.UTF-8
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

SONG=88d247468cb6d49f
CYCLE=25
SRC="data/v3_spine/$SONG/operator_section_c23_unified"
DST="data/v3_spine/$SONG/operator_section_c25_checkpointed"
LOGFILE="data/v3_spine/$SONG/resume_peach_dream_c25.log"

# Seed: copy c23 completed stage-1 + stage-2 outputs into the c25 work dir so
# the checkpointed driver's slice + rehtdemucs stages HIT on their first probe.
mkdir -p "$DST/rc9_6stem"
cp -n "$SRC/section.wav" "$DST/section.wav"
cp -n "$SRC/rc9_6stem/"*.wav "$DST/rc9_6stem/"
echo "seed: section.wav + 6 stems copied into $DST"

# Detached launch.
/usr/bin/python3 -c "
import sys
sys.path.insert(0, 'scripts/v3_spine')
from launch_detached import launch_detached
from pathlib import Path
pid = launch_detached(
    ['/usr/bin/python3', 'scripts/v3_spine/recreate_v3_checkpointed.py',
     '--song', '$SONG', '--section', 'operator', '--cycle', '$CYCLE',
     '--verify-det',
     '--out', 'data/v3/deliveries/$SONG/cycle$CYCLE/'],
    Path('$LOGFILE'),
)
print(f'DETACHED_PID={pid}')
print(f'LOG={\"$LOGFILE\"}')
print(f'poll: os.kill({pid}, 0)')
"
