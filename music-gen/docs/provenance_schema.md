---
created: 2026-08-28T04:20:00Z
cycle: 1
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-INGEST-1
---

# Ingestion provenance schema (v1) and tail-handling rule

The ingestion chassis writes one JSONL manifest per source audio file.
Every manifest is append-only, self-contained (no external database
required to replay), and validated by
`scripts/ingest/provenance.py::validate_manifest`.

The authoritative machine-readable version lives at
`data/ingestion/provenance_schema.json`; this document is the
human-facing narrative.

## Row kinds

The first non-empty line of every manifest is a `kind:"source"` row.
Every subsequent line is a `kind:"clip"` row that FKs into it via
`source_id`. Exactly one source row per manifest.

### `kind:"source"` — fields

| field             | type   | meaning                                                                 |
|-------------------|--------|-------------------------------------------------------------------------|
| `kind`            | str    | Literal `"source"`.                                                     |
| `schema_v`        | int    | Schema version. Currently `1`.                                          |
| `source_id`       | str    | First 16 hex chars of `bytes_sha256`. Content address.                  |
| `source_type`     | str    | `"local"` or `"youtube"`.                                               |
| `source_ref`      | str    | Absolute filesystem path or full YouTube video URL.                     |
| `sr_hz`           | int    | Sample rate of the decoded canonical form.                              |
| `n_samples`       | int    | Total mono sample count of the decoded canonical form.                  |
| `duration_s`      | float  | Derived: `n_samples / sr_hz`. Present for reader convenience.            |
| `bytes_sha256`    | str    | SHA-256 of the decoded canonical 16-bit-PCM mono byte stream.           |
| `chunker_version` | str    | Semver tag of the chunker module used (`"ingest/0.1.0"`).               |
| `tail_rule`       | str    | Currently always `"anchored"`.                                          |
| `ingest_ts`       | str    | ISO-8601 UTC timestamp of manifest emission.                             |

### `kind:"clip"` — fields

| field                | type   | meaning                                                                                    |
|----------------------|--------|--------------------------------------------------------------------------------------------|
| `kind`               | str    | Literal `"clip"`.                                                                          |
| `schema_v`           | int    | Schema version. Currently `1`.                                                             |
| `source_id`          | str    | FK to the source row.                                                                      |
| `clip_index`         | int    | Zero-based index in the source's clip sequence.                                            |
| `clip_id`            | str    | First 16 hex chars of `clip_bytes_sha256`.                                                 |
| `t_start_s`          | float  | Derived from `start_sample / sr_hz`. Sample-accurate.                                      |
| `t_end_s`            | float  | Derived from `(start_sample + n_samples) / sr_hz`.                                         |
| `n_samples`          | int    | Sample count of this clip.                                                                 |
| `sr_hz`              | int    | Sample rate (same as source).                                                              |
| `clip_path`          | str    | Path of the on-disk WAV. `data/ingestion/clips/<source_id>/<source_id>__<idx>.wav`.        |
| `clip_bytes_sha256`  | str    | SHA-256 of the clip's 16-bit-PCM mono byte stream. Used by the replay proof.               |
| `short_song`         | bool   | `true` iff the entire source was shorter than 30 s.                                         |
| `anchored_tail`      | bool   | `true` iff this is the final tail-anchored clip.                                            |

## Non-factor exclusion (deliberate)

The schema deliberately **does not** carry `title`, `artist`, `genre`,
`date`, `language`, `live_vs_recorded`, or any other non-factor
attribute. Ingestion is content-addressed; every downstream decision
that could touch a non-factor lives in a sidecar owned by
M-CLASS-1's classifier, in a directory this chassis never imports.

Consequences the reader should expect:

- Ingestion produces byte-identical manifests when the *same audio*
  is delivered by different front doors, even if the local file's
  name says "Beethoven Op 131" and the YouTube URL is titled
  "unlabelled string quartet". Container / metadata / channel-count
  differences are washed out by the decode-to-canonical step.
- Downstream code that filters by artist/genre reads the classifier
  sidecar, not this manifest.

## Tail-handling rule ("anchored final clip")

The 30 s / 5 s-overlap grid is a promise that any phrase cut at one
clip boundary appears whole in a neighboring clip's 5 s overlap zone.
Two failure modes threaten that promise at the tail of a source:

1. **Truncation.** Stop when the last hop-strided start no longer
   fits. This drops audio and violates the "whole song ingested"
   invariant.
2. **Zero-pad.** Extend the final clip past `duration_s` with
   silence. This introduces synthetic silence downstream stages
   would mistake for a real quiet passage — a classifier-, ear-,
   and heuristic-relevant artifact.

**Adopted rule (`tail_rule: "anchored"`).** If the last hop-strided
clip does not already end at `n_samples`, append one additional
"tail-anchored" clip whose *end* is exactly `n_samples` and whose
length is exactly `clip_len`:

    starts.append(n_samples - clip_len)

Consequences:

- The anchored clip's overlap with the previous clip is `>= 5 s` by
  construction (equality only in the degenerate case where the tail
  fills exactly one hop). In the worst case it can approach `30 - eps`
  seconds — that is a *stronger* neighborhood guarantee than the
  standard-case 5 s.
- Every clip is full-length. Downstream stages can assume a fixed
  clip length except when they explicitly consult `short_song`.
- The validator accepts overlaps `>= 5 s`, not exactly `5 s`, so
  anchored-tail clips pass without a special case.

**Short-song rule** (special case). If `n_samples < clip_len`, emit
a single clip whose length is the whole source and set
`short_song: true`. No zero-padding. Downstream stages branch on
this flag if they require a minimum length. The validator relaxes
the overlap invariant for short-song manifests (there is no
neighbor to overlap with).

## Replay proof

The manifest is complete enough to regenerate every clip file
byte-for-byte from the source WAV alone. `provenance.replay(manifest,
source_wav, clip_dir)` runs the chunker again against the source and
diffs the new clip SHA-256s against the manifest. Any mismatch is a
regression of the determinism guarantee. The suite exercises this on
`seed_long_87s.wav` in `tests/test_ingest.py::test_replay_round_trip`.

## Validator checks

`validate_manifest(manifest_path)` returns a list of failure strings
(empty list = pass). It enforces:

1. Every JSONL line parses.
2. Exactly one source row; every clip row's `source_id` matches.
3. Required fields present with correct types in every row.
4. No duplicate `(source_id, clip_index)` pairs (append-only).
5. `t_start_s` monotonic across clips.
6. Adjacent-clip overlap `>= OVERLAP_S - 1/sr_hz` (short-song
   manifests are exempt from #6).
7. Every `clip_path` exists on disk **and** its recomputed
   decoded-bytes SHA-256 equals `clip_bytes_sha256`.
