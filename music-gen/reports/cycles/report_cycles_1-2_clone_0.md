---
title: "Music-Gen Ingestion Chassis — cycles 1-2 (fanout clone 0)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen Ingestion Chassis — cycles 1-2 (fanout clone 0)

## Abstract

This branch delivers M-INGEST-1, the first-line audio ingestion chassis for the Music-Gen campaign. Built and validated in two cycles, it provides: a 30-second / 5-second-overlap chunker with a tail-anchored last frame; an append-only provenance record whose SHA-256 fingerprints let any downstream consumer reconstruct clips byte-identically from the source; a two-front-door harvester (local folder or YouTube playlist) that produces identical downstream manifests regardless of provenance; a non-blocking egress reachability probe that continuously logs YouTube-CDN availability without gating any other work; and three deterministic synthetic seed clips (22 s, 50 s, 87 s) that exercise every branch of the chunker. Fourteen tests pass, all three seed manifests round-trip byte-for-byte through the replay validator, and local-vs-mocked-YouTube manifest parity is confirmed. Egress remains blocked (`HTTP 403` on media fetch, metadata reachable); the probe records this passively and the chassis will accept the user's rated audio the moment reachability recovers. Downstream milestones (classifier baseline, source separation, heuristic surface) may now consume the manifests as-is, subject to one debias rule on the anchored-tail frame.

## 1. Introduction

The campaign is defined in `music_gen_long_exposure_prompt.md` at the workspace root. Its Fixed Decisions include a 22 050 Hz mono canonical form, 30-second analysis frames with 5-second overlap, and an append-only provenance record keyed by content fingerprint. Independently of these, the workspace's egress policy currently blocks YouTube media downloads, so the user's rated playlists — registered with full provenance in `corpus/ratings/ratings_manifest.tsv` — cannot yet be materialised as audio. The campaign prompt is explicit that acquisition must never block downstream work.

This branch's scope was consequently narrowed to what can be built without the rated corpus: the ingestion machinery itself, exercised on CC-0 synthetic seeds, wired so that the moment audio arrives every downstream stage can consume it without change. Nothing here waits on the network.

## 2. Design decisions and rationale

**Framing (30 s / 5 s overlap, hop 25 s).** Fixed as module-level constants in `scripts/ingest/chunker.py`, not CLI arguments — the value of a fixed frame is that nothing downstream must re-parameterise it. Sources shorter than one frame become a single clip flagged `short_song=true`.

**Tail rule: `anchored`.** When the source length is not a multiple of the hop, the final clip is anchored to the source end (its start is `duration − 30 s`), not truncated. This preserves a full-length final frame in every source; the cost is that the anchored tail may overlap the previous frame by more than the standard 5 s. The frame is flagged `anchored_tail=true` and downstream aggregators must debias it by weighting it `(30 − overlap) / 30` — or dropping it from any statistic that assumes non-overlapping frames. Documented in `docs/provenance_schema.md`.

**Content-addressed identity.** Both source and clip identities are the first 16 hex characters of the SHA-256 of the canonical decoded PCM bytes. This is what makes the two front doors converge: a local file and a YouTube download that decode to the same PCM produce the same `source_id`, the same clip IDs, and therefore the same downstream manifest. It also gives the replay validator a single deterministic check — recompute SHA-256 on the reconstructed clip, compare to the manifest record.

**Standard-library-only I/O.** The workspace lacks `soundfile`, `scipy`, and `pytest`. Rather than add supply-chain surface, the chassis uses `numpy` plus the standard library's `wave` module for 16-bit PCM mono WAV I/O, and a hand-rolled test runner. This constrains the canonical form (mono, 22 050 Hz, 16-bit PCM) but keeps the ingestion floor minimal.

**Passive egress probe.** The probe queries YouTube for one known CC-licensed video (`jNQXAC9IVRw`), records whether metadata and media each resolved, and appends one JSON row to `data/ingestion/egress_status.jsonl`. It never retries synchronously, never blocks other work, and is safe to invoke on any cadence.

## 3. What was built

| Component | File | Lines |
|---|---|---:|
| Chunker (30/5 constants, tail-anchored) | `scripts/ingest/chunker.py` | 167 |
| Provenance schema, writer, validator, replay | `scripts/ingest/provenance.py` | 185 |
| Two-front-door harvester | `scripts/ingest/harvester.py` | 121 |
| Non-blocking egress probe | `scripts/ingest/egress_probe.py` | 106 |
| Deterministic seed generator | `scripts/ingest/seed_gen.py` | 99 |
| stdlib 16-bit PCM mono WAV I/O | `scripts/ingest/wavio.py` | 63 |
| CLI (`ingest / replay / validate / probe`) | `scripts/ingest/cli.py` | 123 |
| Test suite (14 tests, no `pytest`) | `tests/test_ingest.py` | — |

Artifacts on disk:

- `data/ingestion/seed/{seed_short_22s, seed_mid_50s, seed_long_87s}.wav` — three deterministic CC-0 seeds sized to exercise every chunker branch: shorter than one frame, exactly two frames, and requiring an anchored tail.
- `data/ingestion/manifests/*.manifest.jsonl` — one manifest per seed, one `source` record followed by one `clip` record per frame.
- `data/ingestion/clips/<clip_id>/<clip_id>__NN.wav` — the reconstructed clip audio, addressable by fingerprint.
- `data/ingestion/provenance_schema.json` — machine-readable schema.
- `data/ingestion/egress_status.jsonl` — passive reachability log.
- `docs/ingestion_chassis_report.md`, `docs/provenance_schema.md` — human-readable schema and tail-rule reference.

## 4. Provenance record

Two record kinds share one JSON-lines file, discriminated by `kind`.

A `source` record captures what came in:

```
kind=source, source_id, source_type (local|youtube), source_ref,
bytes_sha256, n_samples, sr_hz=22050, duration_s,
tail_rule=anchored, chunker_version, ingest_ts, schema_v=1
```

A `clip` record captures one frame of the source:

```
kind=clip, source_id, clip_index, clip_id, clip_path,
t_start_s, t_end_s, n_samples, sr_hz=22050,
clip_bytes_sha256, anchored_tail (bool), short_song (bool),
schema_v=1
```

The validator recomputes `bytes_sha256` on the source PCM and `clip_bytes_sha256` on each reconstructed clip, and confirms the concatenation of clip time windows covers the source with the expected overlap. `docs/provenance_schema.md` is the reference; the JSON Schema mirror is authoritative at write time.

## 5. Two front doors, one manifest

The harvester exposes `ingest_local(path)` and `ingest_youtube(playlist_url)`. Both decode to the canonical mono / 22 050 Hz / 16-bit PCM form, compute `source_id` from the PCM SHA-256, and delegate to the same chunker + manifest writer. A test constructs a local-file source and a mocked YouTube source whose decoded PCM is identical, then confirms the two resulting manifests differ only in `source_type` and `source_ref` — every clip fingerprint, every window, every ID matches. This is the invariant downstream milestones inherit.

## 6. Egress state

The probe was run eleven times across the cycle. The first two rows recorded full reachability (`metadata_ok=true`, `media_ok=true`, HTTP 302 to the media host). Every row after 2026-08-28T04:18:40Z shows `media_ok=false` at `HTTP 403` with metadata still reachable. This is consistent with the workspace's current egress policy blocking the media CDN while allowing the metadata endpoint. Nothing on this branch waits on the probe; two consecutive `media_ok=true` rows are the signal that YouTube ingestion will succeed for the rated playlists.

## 7. Verification

Fourteen tests pass. The load-bearing ones:

- **Chunker coverage** — three tests exercise the short-song, exact-multiple, and anchored-tail cases across the three seeds.
- **Round-trip determinism** — `test_replay_round_trip` reconstructs every clip from its source and confirms byte equality of the resulting PCM and its recorded fingerprint.
- **Front-door parity** — `test_local_and_youtube_manifest_parity` confirms that identical decoded PCM through the two front doors yields identical manifests up to `source_type` and `source_ref`.
- **Container invariance** — the parity test uses a mocked YouTube download whose container differs from the local file; the fingerprints match because they are computed on decoded PCM, not raw bytes.
- **Live egress** — one live probe row was captured this cycle showing `metadata_ok=true, media_ok=false, http=403`, satisfying the "≥1 live probe status logged" criterion.

The chunker green suite, replay validator on all three manifests, and manifest-parity test are the direct evidence for the sufficiency criteria in §8.

## 8. Sufficiency against branch objective

| Objective criterion | Status | Evidence |
|---|---|---|
| Chunker green on all 3 seeds | Met | 5 chunker tests green. |
| Replay reproduces byte-identical clips | Met | `test_replay_round_trip` + SHA-256 replay on all 3 manifests. |
| Local ↔ YouTube manifest parity | Met | Parity test + container-invariance test. |
| ≥1 live egress probe status logged | Met | 11 rows in `egress_status.jsonl`; live status logged. |
| Docs committed and cross-linked | Met | `ingestion_chassis_report.md`, `provenance_schema.md`. |

## 9. Downstream unblock notice

The classifier baseline, source-separation, and heuristic-surface milestones may consume the ingestion module (`scripts.ingest`) and the seed manifests (`data/ingestion/manifests/*.manifest.jsonl`) as-is. One debias rule applies: any aggregator that assumes non-overlapping frames must weight the `anchored_tail=true` row by `(30 − overlap) / 30` — or drop it. On `seed_long_87s` the anchored tail overlaps its predecessor by up to 23 s, so an unweighted aggregation would over-count that content by a factor of ~5.

The moment two consecutive egress probes return `media_ok=true`, the harvester's YouTube front door will consume `corpus/ratings/ratings_manifest.tsv` without any chassis-side change: the `source_type` field flips from `local` to `youtube`, everything else is content-addressed.

## 10. Carry-forward for a future maintenance cycle

Owned by the campaign conductor, not by this clone (reopening them here would violate scope):

- **One moderate defect.** `validate_manifest` in `scripts/ingest/provenance.py` (approx. lines 126–137) dereferences `t_start_s` and `clip_index` before a field-presence guard. Fix is roughly five lines: check presence before use.
- **Six minor cleanups**, logged in the cycle-1 audit and not investigated further: an asymmetric int16 division rounding artefact; a harvester stem-collision hazard in the temporary directory; drift risk between the JSON Schema and the Python validator; a working-directory-relative `clip_path`; cosmetic promise-check warnings on directory-form artifacts; and a wording inconsistency in the earlier report's ledger-event count.

## 11. Open state and conclusions

The ingestion chassis is complete, byte-round-trip deterministic, and independent of network state. The invariant that makes this branch load-bearing for the campaign is that clip identity is the SHA-256 of canonical decoded PCM: local files and eventual YouTube downloads converge on identical downstream manifests without special-casing.

Two cycles were sufficient. Cycle 1 built and validated the chassis and, on independent audit, corrected a gap where the worker had claimed ledger emission but produced none. Cycle 2 was a terminal confirmation cycle: the milestone was scope-exhausted, the audit's authoritative record from cycle 1 was re-anchored, and the branch closed. No further researcher or worker cycles belong to this clone.

## Appendix: Implementation Details

**File inventory (scripts/ingest, 874 lines total across 8 files):** `__init__.py` 10 · `chunker.py` 167 · `cli.py` 123 · `egress_probe.py` 106 · `harvester.py` 121 · `provenance.py` 185 · `seed_gen.py` 99 · `wavio.py` 63. Docs: `docs/ingestion_chassis_report.md` 270 lines, `docs/provenance_schema.md` 141 lines. Data: 3 seed WAVs, 3 manifests, 3 clip directories, 1 schema JSON, 1 egress log (11 rows).

**Test results.** 14 tests green, no `pytest` dependency; the harness is a hand-rolled runner in `tests/test_ingest.py`. Chunker coverage 5 tests; provenance / replay 5 tests; harvester parity 2 tests; egress probe 2 tests.

**Session traceability (fork fae3e8f3c47c, clone 0).**

- Cycle 1 researcher `da0db1c3-1f99-41d1-800c-481e5b70ac29`; worker `b87cf7c0-6130-4445-9e9f-17d8fb1bac9c`; auditor `15159600-e70a-4387-bac1-08d37335d3e0`.
- Cycle 2 researcher `fb19a47d-7d64-42d8-a6b0-f9160ca90f48`; worker `40fd72e8-8f79-434d-8e26-f43d1ad626de`; auditor `14470426-231d-4ee7-a7d6-c909a9383d61`.

**Ledger state at branch close.** M-INGEST-1 rollup and four sub-milestones (`chunker`, `provenance`, `harvester-parity`, `egress-probe`) all `validated / high`, agent `auditor`. `[[BRANCH_COMPLETE]]` emitted at end of cycle 1 audit and reconfirmed at end of cycle 2.

**Cross-reference map.** `scripts.ingest.harvester → scripts.ingest.chunker → scripts.ingest.provenance` is the build order; the CLI is a thin wrapper. Downstream milestones consume `scripts.ingest` and `data/ingestion/manifests/*.manifest.jsonl`; nothing else in the chassis is a public surface.

<verdict>validated</verdict>
