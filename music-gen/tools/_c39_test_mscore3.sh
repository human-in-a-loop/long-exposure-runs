#!/usr/bin/env bash
# Test mscore3 -F -o <midi> <normalized-v2-xml>
set -uo pipefail
cd /home/user/long-exposure-runs/music-gen
TMPDIR="$(mktemp -d)"
export PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1730000000 TZ=UTC LC_ALL=C.UTF-8
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export QT_QPA_PLATFORM=offscreen
IN=data/score_bridge_real_audio_normalizer_v2/inputs/merged_normalized_v2.musicxml
OUT="$TMPDIR/out.mid"
mscore3 -F -o "$OUT" "$IN" 2>&1 | head -40
echo "---"
echo "rc=$?"
ls -la "$OUT" 2>&1 || echo "no output"
if [ -f "$OUT" ]; then
  /usr/bin/python3 -c "
import hashlib, pathlib
b = pathlib.Path('$OUT').read_bytes()
print('sha256:', hashlib.sha256(b).hexdigest())
print('bytes:', len(b))
"
fi
