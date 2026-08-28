"""Ingestion chassis for the Music-Gen campaign (M-INGEST-1).

Fixed decisions (do not parameterize):
- 30 s clips with 5 s overlap -> 25 s hop.
- Tail-anchored final clip when a partial-length tail remains.
- Sample-accurate boundaries; timestamps derived from (sample_index, sr_hz).
- No non-factor fields in this schema; classifier owns that sidecar.
"""

__version__ = "0.1.0"
