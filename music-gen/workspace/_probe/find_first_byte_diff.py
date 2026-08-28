"""Locate the first byte at which two WAV files differ (used to prove that
UMXHQ byte-hash mismatches are header-only, not audio-sample nondeterminism)."""
import sys
from pathlib import Path
ROOT = Path('/home/user/long-exposure-runs/music-gen')
a = (ROOT / 'data/separation/runs/openunmix/synth_030s/drums.wav').read_bytes()
b = (ROOT / 'data/separation/runs/openunmix/synth_030s_verify/drums.wav').read_bytes()
print('len_a', len(a), 'len_b', len(b))
first = None
for i, (x, y) in enumerate(zip(a, b)):
    if x != y:
        first = i
        print(f'first byte diff at offset {i} (hex {i:#06x}): a={x:#04x} b={y:#04x}')
        break
if first is None:
    print('files identical over shared prefix')
    sys.exit(0)
# Print the surrounding region interpreted as ASCII to reveal a chunk-id if any.
lo = max(0, first - 16); hi = min(len(a), first + 16)
print('a bytes near diff (ascii):', a[lo:hi])
print('b bytes near diff (ascii):', b[lo:hi])
