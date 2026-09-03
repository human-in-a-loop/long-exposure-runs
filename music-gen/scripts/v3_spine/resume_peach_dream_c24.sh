#!/bin/bash
# Resume Peach Dream via c24 checkpointed driver — operator directive point 3.
#
# Prerequisites (already on disk from c23 clone-1):
#   data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/section.wav
#   data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/rc9_6stem/*.wav
#
# The checkpointed driver uses its own work dir
# (data/v3_spine/88d247468cb6d49f/operator_section_c24_checkpointed/).
# To reuse c23's completed slice + rehtdemucs outputs, seed the c24 work dir
# with a byte-copy of section.wav and rc9_6stem/ before the first invocation;
# stage_cache will then HIT on both stages because their inputs are unchanged.
#
# Invoke DETACHED so a session boundary in the launching agent does not kill
# the multi-hour muscriptor stages (see docs/v3_spine_stage_checkpointed_driver_spec.md).

set -euo pipefail

# Env pins mandatory for byte-determinism
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH=1756463424
export TZ=UTC
export LC_ALL=C.UTF-8
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

SONG=88d247468cb6d49f
CYCLE=24
SRC="data/v3_spine/$SONG/operator_section_c23_unified"
DST="data/v3_spine/$SONG/operator_section_c24_checkpointed"
LOGFILE="data/v3_spine/$SONG/resume_peach_dream_c24.log"

# Seed: copy c23 completed stage-1 + stage-2 outputs into the c24 work dir so
# the checkpointed driver's slice + rehtdemucs stages HIT on their first probe.
mkdir -p "$DST/rc9_6stem"
cp -n "$SRC/section.wav" "$DST/section.wav"
cp -n "$SRC/rc9_6stem/"*.wav "$DST/rc9_6stem/"
echo "seed: section.wav + 6 stems copied into $DST"

# Detached launch — session boundary in the caller no longer kills this job.
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
