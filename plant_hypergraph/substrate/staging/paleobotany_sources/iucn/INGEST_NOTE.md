# IUCN ingest note — redistribution constraint

IUCN Red List Spatial Data carries terms-of-use restrictions: range
polygons may NOT be redistributed. This clone respects that by staging
only **derived feature vectors**:

- centroid_lat, centroid_lon
- area_km2
- biome_list (coarse labels)
- IUCN status (LC/NT/VU/EN/CR/DD)
- diet_class
- family-level taxonomic context

Raw polygons are NOT in this staging directory and will NEVER be
redistributed by this clone. To obtain polygons, download directly
from iucnredlist.org under their terms.

Sandbox note: this clone has no network access. Records are
literature-curated from IUCN summary fields published in the
2024-2 release notes and species accounts. Re-ingest from IUCN API
at Barrier 1 is recommended; canonical-key deduplication will
reconcile against staged proxy rows.

Attribution (verbatim per IUCN policy):
> IUCN 2024. The IUCN Red List of Threatened Species. Version 2024-2.
> https://www.iucnredlist.org. Downloaded on 2026-05-17.
