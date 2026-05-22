# Climate envelope source citations (M1.6)

This staging branch stages PER-TAXON BIOCLIM FEATURE VECTORS only.
NO RASTER FILES are redistributed in this substrate.

The per-taxon vectors are a derived product permitted under both source licenses.

## WorldClim v2.1
Fick S.E. & Hijmans R.J. 2017. WorldClim 2: new 1km spatial resolution climate
surfaces for global land areas. International Journal of Climatology 37(12):4302-4315.
DOI: 10.1002/joc.5086
Source URL: https://www.worldclim.org/data/worldclim21.html
License: CC-BY 4.0 (rasters); derived per-taxon summaries permitted with citation.
Version: v2.1 (2020 release).
Accessed: 2026-05-17.

## CHELSA v2.1
Karger D.N. et al. 2017. Climatologies at high resolution for the earth's land
surface areas. Scientific Data 4:170122.
DOI: 10.1038/sdata.2017.122
Source URL: https://chelsa-climate.org/bioclim/
License: CC-BY 4.0 (rasters); derived per-taxon summaries permitted with citation.
Version: v2.1.
Accessed: 2026-05-17.

## Licensing posture (BINDING)
- Raw rasters are NOT redistributed. The license-compliance test
  (tests/m1_6_domestication/test_license_compliance.py) verifies that no
  files matching .tif/.geotiff/.nc/.bil/.adf/.asc exist in
  substrate/staging/domestication_sources/. This test MUST PASS at every
  Barrier-1 entry.
- The 19 BIO variables (BIO1-BIO19) are the standard reduced summary used
  by both sources; per-taxon median + IQR over occurrence cells constitutes
  a derived statistical product.
- Downstream tools that need pixel-level data must access the source rasters
  directly under their respective licenses; this substrate does not warehouse them.
