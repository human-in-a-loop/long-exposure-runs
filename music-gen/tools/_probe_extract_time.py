"""Time-check extraction on the shortest song before running all 43."""
from pathlib import Path
import time
from scripts.ear_v0.ingest_ratings import discover_songs
from scripts.ear_v0.extract_features_v0 import extract_song

songs = discover_songs(Path("."))
songs_by_sz = sorted(songs, key=lambda s: s.path.stat().st_size)
s = songs_by_sz[0]
print(f"Testing: band={s.band} {s.path.name} size_kb={s.path.stat().st_size // 1024}")
t0 = time.time()
v = extract_song(s)
print(f"shape={v.shape} dtype={v.dtype} took={time.time() - t0:.1f}s")
print(f"panns_sample={v[:5]} heur={v[-4:]}")
