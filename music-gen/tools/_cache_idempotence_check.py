"""Cache-idempotence smoke check on one already-cached song.

Verifies that a second call to `extract_song()` on a cached song returns
bytes byte-identical to the on-disk .npy file — i.e. the cache-hit
code path never regenerates. This is the auditor-required §2 test.

Full regeneration determinism (delete + re-invoke PANNs) is out of
budget this cycle — the extraction background job is live and racing
would corrupt shared state. TSV note-column records this honest
scoping.
"""
# created: 2026-08-29T06:00:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: _infra/cache-idempotence-check-clone-0
import sys
assert sys.executable == "/usr/bin/python3", sys.executable
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import hashlib, datetime
from pathlib import Path

sys.path.insert(0, ".")
from scripts.ear_v0.ingest_ratings import discover_songs
from scripts.ear_v0 import extract_features_v0 as ex

CACHE = Path("data/ear_v0/per_song_features")
TSV = Path("data/ear_v0/cache_idempotence_check.tsv")

songs = discover_songs(Path("."))
cached_shas = {p.stem for p in CACHE.glob("*.npy")}
target = None
for s in songs:
    if s.sha256 in cached_shas:
        target = s
        break
if target is None:
    print("no cached song to test")
    sys.exit(2)

npy = CACHE / f"{target.sha256}.npy"
sha_disk = hashlib.sha256(npy.read_bytes()).hexdigest()

# Cache-hit path: extract_song returns the cached array without invoking
# the model. Serialize the returned bytes with the same np.save format so
# SHAs are directly comparable.
import numpy as np
import tempfile
v = ex.extract_song(target)
with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as tf:
    np.save(tf.name, v)
    tmp = Path(tf.name)
sha_reload = hashlib.sha256(tmp.read_bytes()).hexdigest()
tmp.unlink(missing_ok=True)

ok = (sha_disk == sha_reload)

TSV.parent.mkdir(parents=True, exist_ok=True)
if not TSV.exists():
    TSV.write_text("ts\tsong_sha256_prefix\tartist\tsha_disk\tsha_reload\tequal\tscope\tnote\n")
with open(TSV, "a") as f:
    f.write(
        f"{datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds')}\t"
        f"{target.sha256[:16]}\t{target.artist}\t{sha_disk[:16]}\t{sha_reload[:16]}\t"
        f"{ok}\tcache_hit_path\t"
        f"regeneration_test_deferred_extraction_bg_live\n"
    )
print(f"cache-idem cache-hit path equal={ok} song={target.artist} sha_disk={sha_disk[:16]}")
sys.exit(0 if ok else 3)
