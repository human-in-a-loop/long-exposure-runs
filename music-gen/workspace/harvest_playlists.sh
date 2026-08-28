#!/usr/bin/env bash
# Download the user's rated YouTube playlists into the music-gen corpus.
#
# Band mapping (playlist title = rating band on the 1-7 ear scale):
#   6 -> PLoxlz_x73gZO1UKfmdIRRvnJBiJkQd53l
#   5 -> PLoxlz_x73gZPwSJkctwHkzMT6RpFnZqXQ
#   4 -> PLoxlz_x73gZNv_Ae3HP2b-uhjQNnb5YnN
#
# NOTE (2026-08-28): in the current remote workspace the egress gateway
# policy-denies googlevideo.com (YouTube's media CDN), so playlist METADATA
# resolves but media downloads fail with proxy 403/connect-rejected. Run this
# script from an environment whose network policy allows *.googlevideo.com.
# The tv_embedded player client is required to bypass YouTube's datacenter
# bot-check on stream extraction.
#
# Audio lands in corpus/ratings/<band>/ (gitignored - never commit audio).
set -euo pipefail

CORPUS="${1:-/home/user/long-exposure-runs/music-gen/corpus/ratings}"
mkdir -p "$CORPUS"/{4,5,6}
cd "$CORPUS"

declare -A BANDS=(
  [6]=PLoxlz_x73gZO1UKfmdIRRvnJBiJkQd53l
  [5]=PLoxlz_x73gZPwSJkctwHkzMT6RpFnZqXQ
  [4]=PLoxlz_x73gZNv_Ae3HP2b-uhjQNnb5YnN
)

printf 'rating\tplaylist_id\tvideo_id\ttitle\tduration_s\turl\n' > ratings_manifest.tsv
for band in 6 5 4; do
  pl="${BANDS[$band]}"
  yt-dlp --flat-playlist --no-warnings \
    --print "$band	$pl	%(id)s	%(title)s	%(duration)s	%(url)s" \
    "https://youtube.com/playlist?list=$pl" >> ratings_manifest.tsv
  yt-dlp -f bestaudio -x --ignore-errors --no-warnings --restrict-filenames \
    --sleep-requests 1 \
    --extractor-args "youtube:player_client=tv_embedded" \
    -o "$band/%(playlist_index)03d__%(id)s__%(title).80s.%(ext)s" \
    "https://youtube.com/playlist?list=$pl" > "$band/download.log" 2>&1 || true
  echo "band $band: $(ls "$band" | grep -cv download.log) files"
done
