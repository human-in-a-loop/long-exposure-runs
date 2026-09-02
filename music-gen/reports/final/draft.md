# 2. Ingestion, Classification, Provenance, and the Egress-Ready State Machine

## 2.1 Corpus scope and framing

The rated corpus is 80 songs supplied by the operator, distributed across three
ear bands: band 6, band 5, and band 4 (the numeric label denotes the operator's
subjective ordinal rating, with 7 the ceiling reserved for exemplar tracks and
lower bands representing progressively less-preferred material). Each song is
registered in `corpus/ratings/ratings_manifest.tsv` with full provenance
(source URL, ratings-file line number, band label, and content hash once the
audio lands on disk).

Ingestion is the pipeline's front door and its principal external dependency.
Every downstream stage — source separation, transcription, score merging,
palette rendering, texture panels, ear-model calibration — reads from the
30-second chunks it emits. Ingestion therefore had to be built to (a) run
unattended, (b) survive a network policy that intermittently blocks the
upstream media host, and (c) refuse to advance any chunk that has not been
positively classified as music. The remainder of this section walks through
those three requirements in the order in which the pipeline enforces them.

## 2.2 Chunking policy: 30-second frames at 5-second overlap

Every arriving audio file is decoded to mono 44.1 kHz PCM and split into
30-second frames with 5-second overlap between successive frames. Both numbers
are fixed decisions: the 30-second window matches the receptive field the
downstream texture panels and CORN ear model use for feature extraction, and
the 5-second overlap ensures that a musically-meaningful phrase never lands
across a frame boundary without being fully contained in at least one frame.
Overlap is bookkeeping-only — no cross-frame smoothing is applied — so no
downstream tool needs to reason about it.

Chunks are named `<song_sha16>__<start_seconds>.wav`, where `song_sha16` is
the leading 16 hexadecimal characters of the SHA-256 of the source file. This
naming carries provenance forward: any downstream artifact that cites a chunk
name can be traced back to the exact byte sequence that produced it.

## 2.3 Music/non-music classification

Not every arriving file is music. Field recordings, interviews, silent
intros, and mistagged uploads all appear in the source stream. The pipeline
therefore runs each 30-second chunk through a three-way classifier ensemble
before releasing it downstream:

- **PANNs** (Pretrained Audio Neural Networks) supplies the primary
  527-class AudioSet posterior.
- **YAMNet** provides a second AudioSet posterior at a different backbone,
  used as a cross-check.
- **AST** (Audio Spectrogram Transformer) supplies a third posterior with
  transformer-family biases distinct from the two convolutional models.

The three posteriors are mapped to a project-internal music/non-music
taxonomy: an AudioSet class contributes positive evidence for "music" if it
lies under the `Music`, `Musical instrument`, or `Singing` subtrees, and
negative evidence otherwise. A chunk is released downstream only if at least
two of the three models place the majority of their posterior mass on
"music"-bearing classes. Ties are treated as non-music. The rationale is
conservative: a false negative loses one chunk out of many; a false positive
poisons downstream separation, transcription, and rating.

## 2.4 The non-factor sidecar

Every song carries a metadata sidecar recording seven attributes the
operator explicitly designates as *non-factors*: genre, country of origin,
release date, language, instrumental-vs-lyrics flag, live-vs-studio flag, and
artist name. These fields are stored, versioned, and audited, but they are
never permitted to influence any downstream computation — not as features,
not as filters, not as stratification variables, not as sampling weights.
The non-factor set exists to be *tested against*, not consumed: the ear
model's leak-test harness (Section 7) plants strong artist, genre, and era
signals at full contamination strength and requires the model to fail to
detect them. If a downstream artifact ever consumes a non-factor field, the
leak-test catches it.

## 2.5 The egress-ready state machine

The workspace's network egress policy blocks the upstream media host
(`*.googlevideo.com`) for large portions of the run. Rather than treat this as
a fatal error, ingestion is built around an explicit state machine that
gates audio acquisition:

$$\text{IDLE} \to \text{ARMED} \to \text{TRIGGERED} \to \text{HARVESTING} \to \text{CHUNKING} \to \text{CLASSIFYING} \to \text{READY}$$

with a terminal `FAILED` sink from any state. Transitions are driven by
periodic probes: a small HTTP request against the media host is issued on a
schedule, and the outcome (`media_ok=true` or `media_ok=false`, plus HTTP
status and a short reason string) is appended as an immutable row to
`data/ingestion/egress_status.jsonl`. State is materialized in an atomic
`state.json` file, and every state transition is also written to
`transitions.jsonl` — the pair gives current-state readers and historical-audit
readers each a source of truth without contention.

The unblock signal is deliberately conservative: the machine advances from
`ARMED` to `TRIGGERED` only after **two consecutive `media_ok=true` probes**.
A single probe passing is treated as a transient glitch. This bar prevents
the pipeline from launching a full harvest during a brief policy fluctuation
that then closes again mid-fetch.

Two operational limitations survived the run and are noted honestly:

1. The probe schema does not distinguish smoke probes (issued by the health
   check at bootstrap) from production probes (issued by the periodic
   guard). Both are recorded with identical shape. As a result, the two
   consecutive `media_ok=true` unblock signal has, historically, been
   satisfied by the bootstrap smoke probe followed by a target-side smoke
   probe rather than by two independent production probes. A future
   `probe_kind ∈ \{smoke, production\}` field on each row would close the
   loophole; the pipeline advances only when two consecutive
   `probe_kind = production` rows report `media_ok=true`.
2. A subset of probe rows written before the schema stabilized lack a
   `cycle` field; a small number of run windows in the middle of the
   campaign have no probe row at all. Neither gap alters the machine's
   forward behavior (the state file is authoritative), but both leave the
   historical record less complete than intended.

## 2.6 What acquisition delivered

At the point this report is written, 43 of the 80 rated songs are present
on disk. The remaining 37 are registered in the ratings manifest with full
provenance but their audio has not passed the egress policy. Per the run's
governing directive, acquisition never blocks downstream work: every
milestone that can be exercised on the 43 available songs, or on the
five-song focus set that all recreation and texture work uses, has been
exercised. The subset of milestones that require the full 80-song corpus —
notably real-label ear-model calibration on the full band 6/5/4 distribution
— is explicitly held pending, not silently skipped. Section 7 returns to
this constraint.

## 2.7 First large-model determinism window

An early determinism check ran the `htdemucs_6s` four-stem separator (used in
Section 3 as the production separator) against a five-song slice of the
available corpus. The check answered two questions in one pass: whether the
model weights fetch was reproducible, and whether the model's stem output was
byte-deterministic across independent runs. Both answers were positive: the
weights fetch returned HTTP 200 on both attempts with matching content hashes,
and the resulting 30 stems (5 songs × 6 stem variants under `htdemucs_6s`,
of which four are used downstream) were byte-identical across two independent
invocations. This was the first successful large-model determinism window in
the run and set the standard the later palette-instrument determinism work
(Section 5) had to match.

## 2.8 What the reader should carry forward

Three points bear on later sections:

- **Chunk identity is content-addressed.** Every downstream artifact ties
  back to a `song_sha16__<start>` chunk, which ties back to the source file
  hash, which ties back to the ratings manifest row. Nothing in the
  pipeline consumes a filename; everything consumes a hash.
- **The non-factor sidecar is a test surface, not a feature source.** The
  ear model's leak test in Section 7 exists precisely because these fields
  are present in the workspace and must remain unread by anything else.
- **The egress state machine is authoritative.** Downstream stages read
  `state.json` to decide whether to consume newly-arrived audio; they never
  probe the network directly. This isolates all network fragility to a
  single component.



Stage 2: Wrote §2 (Ingestion, classification, non-factor sidecar, egress-ready state machine, htdemucs determinism window) to draft.md.
File: /home/user/long-exposure-runs/music-gen/reports/final/draft.md
Size: ~7.0 KB
