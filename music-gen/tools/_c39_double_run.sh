#!/usr/bin/env bash
# Run mscore3 twice, compute SHA-256 x2, then fidelity vs reference.
set -uo pipefail
cd /home/user/long-exposure-runs/music-gen
export PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1730000000 TZ=UTC LC_ALL=C.UTF-8
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export QT_QPA_PLATFORM=offscreen

IN=data/score_bridge_real_audio_normalizer_v2/inputs/merged_normalized_v2.musicxml
D1="$(mktemp -d)"
D2="$(mktemp -d)"
mscore3 -F -o "$D1/out.mid" "$IN" >/dev/null 2>&1
RC1=$?
mscore3 -F -o "$D2/out.mid" "$IN" >/dev/null 2>&1
RC2=$?
echo "rc1=$RC1 rc2=$RC2"
/usr/bin/python3 -c "
import hashlib, pathlib
b1 = pathlib.Path('$D1/out.mid').read_bytes()
b2 = pathlib.Path('$D2/out.mid').read_bytes()
h1 = hashlib.sha256(b1).hexdigest()
h2 = hashlib.sha256(b2).hexdigest()
print('sha1:', h1)
print('sha2:', h2)
print('equal:', h1 == h2)
print('len1:', len(b1), 'len2:', len(b2))
"
echo "--- fidelity vs reference ---"
/usr/bin/python3 tools/_c39_probe_output.py "$D1/out.mid"
echo "$D1"
