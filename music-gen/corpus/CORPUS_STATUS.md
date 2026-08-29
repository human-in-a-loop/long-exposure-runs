# Corpus status — 2026-08-29 (updated)

Rated corpus (playlist title = ear rating band; band 7 is local-only):

- band 7: LOCAL_BAND_7 — user-supplied local files (new tier, added 2026-08-29)
- band 6: PLoxlz_x73gZO1UKfmdIRRvnJBiJkQd53l — 30 songs
- band 5: PLoxlz_x73gZPwSJkctwHkzMT6RpFnZqXQ — 30 songs
- band 4: PLoxlz_x73gZNv_Ae3HP2b-uhjQNnb5YnN — 20 songs

`ratings/ratings_manifest.tsv` holds full provenance (rating, playlist id,
video id, title, duration, URL) for all 80 songs.

## Audio availability (2026-08-29)

**Local uploads (band 6, partial):** three MP3s supplied by the user via the
local-folder harvester front door and placed under `ratings/6/` with
harvester-convention filenames (`015__wXvX1vOe0rQ__Peach_Dream.mp3`,
`016__1GmuDka6pbk__Loyle_Carner_-_Angel_ft._Tom_Misch.mp3`,
`017__It2s36sL4aM__Chicken_Grease.mp3`). Durations match manifest within
±1 s; sha256 receipts in `ratings/6/RECEIPTS.md`. **More uploads expected.**

**YouTube harvest (all bands): still blocked in this workspace.**
Two independent obstacles apply:
1. YouTube's datacenter bot detection now gates stream URL extraction across
   every yt-dlp player-client bypass (`tv_embedded` used to work on
   2026-08-28 morning but is closed as of 2026-08-29). Fix requires
   `--cookies` / `--cookies-from-browser` from a signed-in browser.
2. The workspace egress gateway policy-denies `*.googlevideo.com` (YouTube's
   media CDN); even successful extraction would refuse to stream bytes.

`workspace/harvest_playlists.sh` will only work once BOTH conditions clear.
Meanwhile, per-song local uploads are the reliable path — the harvester's
local-folder front door ingests them with identical provenance.

Use case: experimental / test-run only. Downloaded audio bytes are never
committed to the repo (see `.gitignore`).
