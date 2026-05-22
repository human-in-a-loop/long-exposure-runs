#!/usr/bin/env bash
# Probe M1.6 domestication source landing pages. No bulk downloads; capture http status + small HTML for audit trail.
set -u
OUT=substrate/staging/domestication_sources/raw
mkdir -p "$OUT"
declare -a SOURCES=(
  "genesys_api|https://api.genesys-pgr.org/"
  "genesys_web|https://www.genesys-pgr.org/"
  "grin|https://npgsweb.ars-grin.gov/gringlobal/search"
  "wiews|https://www.fao.org/wiews/en/"
  "fao_cwr|https://www.fao.org/plant-treaty/en"
  "worldclim|https://www.worldclim.org/data/worldclim21.html"
  "chelsa|https://chelsa-climate.org/bioclim/"
  "cwr_checklist|https://www.cwrdiversity.org/checklist/"
)
echo "label	url	http_status	bytes	content_type	access_date" > "$OUT/probe_results.tsv"
for entry in "${SOURCES[@]}"; do
  label="${entry%%|*}"
  url="${entry##*|}"
  out="$OUT/${label}.html"
  status_line=$(curl -sS -o "$out" -w "%{http_code}|%{size_download}|%{content_type}" --max-time 12 -A "PhytoGraph-M1.6-Probe/1.0 (research; contact@example.invalid)" "$url" 2>/dev/null || echo "000|0|unreachable")
  http_status="${status_line%%|*}"
  rest="${status_line#*|}"
  bytes="${rest%%|*}"
  ct="${rest##*|}"
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$label" "$url" "$http_status" "$bytes" "$ct" "$(date -u +%Y-%m-%d)" >> "$OUT/probe_results.tsv"
done
cat "$OUT/probe_results.tsv"
