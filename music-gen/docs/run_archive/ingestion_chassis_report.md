---
created: 2026-08-28T04:22:00Z
cycle: 1
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-INGEST-1
---

# Ingestion chassis report (M-INGEST-1)

This branch delivers the first-line audio ingestion machinery for the
Music-Gen campaign: a 30 s / 5 s-overlap chunker, an append-only
provenance ledger with a validator that proves byte-round-trip
determinism, a two-front-door harvester (local folder + YouTube
playlist) that produces identical downstream manifests, a
non-blocking egress reachability probe, and three deterministic
synthetic seed clips that exercise every branch of the chunker.

The companion schema doc is
[`docs/provenance_schema.md`](./provenance_schema.md); the
machine-readable schema is
[`data/ingestion/provenance_schema.json`](../data/ingestion/provenance_schema.json).

## 1. What was built

| Component                                      | Path                                                     |
|------------------------------------------------|----------------------------------------------------------|
| Chunker (fixed 30/5 constants, tail-anchored)  | `scripts/ingest/chunker.py`                              |
| Provenance schema + writer + validator + replay | `scripts/ingest/provenance.py`                          |
| Two-front-door harvester                       | `scripts/ingest/harvester.py`                            |
| Non-blocking egress probe                      | `scripts/ingest/egress_probe.py`                         |
| Deterministic seed audio generator             | `scripts/ingest/seed_gen.py`                             |
| stdlib 16-bit PCM mono WAV I/O                 | `scripts/ingest/wavio.py`                                |
| CLI (`ingest / replay / validate / probe`)     | `scripts/ingest/cli.py`                                  |
| Test suite (14 tests, no pytest dep)           | `tests/test_ingest.py`                                   |
| Seed WAVs                                      | `data/ingestion/seed/*.wav`                              |
| Seed manifests                                 | `data/ingestion/manifests/*.manifest.jsonl`              |
| Egress reachability log                        | `data/ingestion/egress_status.jsonl` (gitignored)        |

The chunker is a **stdlib-only** implementation (numpy + wave). This
workspace has no `soundfile`, no `scipy`, no `pytest`; adding those
would just be a supply-chain surface. `wave` reads and writes exactly
the 16-bit PCM mono WAVs the rest of the chassis assumes.

## 2. Fixed decisions (do not re-litigate downstream)

- `CLIP_S = 30.0`, `OVERLAP_S = 5.0`, `HOP_S = 25.0`. Module-level
  constants in `chunker.py`, not CLI args.
- **Tail rule: `anchored`.** See §4 and `docs/provenance_schema.md`.
- Canonical decoded form: **mono, 22 050 Hz, 16-bit PCM**. All content
  addressing uses SHA-256 of that byte stream, so `source_id` is
  invariant to container (WAV/MP3/M4A/etc), channel count, and file
  name. `youtube_playlist(url)` and `local_folder(path)` therefore
  produce identical `source_id`s when they deliver the same content.
- **No non-factor fields in the ingestion schema.** Ever. Title,
  artist, genre, date, language belong to the classifier's sidecar
  under M-CLASS-1.

## 3. What was run

```
python -m scripts.ingest.seed_gen     # write the three seed WAVs
python -m tests.test_ingest           # 14 / 14 green
python -m scripts.ingest.egress_probe # live probe against googlevideo.com
```

For each of the three seed WAVs the chunker was invoked and the
resulting manifest passed the validator (which includes the on-disk
clip SHA-256 replay check).

## 4. Tail-handling rule — the "phrase whole in a neighbor" argument

The 5 s overlap contract only earns its keep if a phrase cut at *any*
clip boundary — including the last one — appears whole in a
neighboring clip. The tail is the awkward case: for a source of
duration `D` and hop `h = 25 s`, the last hop-strided clip ends at
`⌊(D - 30) / 25⌋ · 25 + 30`, which is generically < `D`.

Three tail-handling options were considered; the adopted rule
strengthens the neighborhood guarantee at the tail instead of
weakening it:

| Option        | Behavior at tail                     | Cost                                                        |
|---------------|--------------------------------------|-------------------------------------------------------------|
| truncate      | last hop-strided clip; drop residue  | audio outside the last standard clip is silently dropped    |
| zero-pad      | pad the last clip with silence to 30 s | synthesizes silence downstream stages will mistake for real |
| **anchored**  | append `[D-30, D]` as the final clip | duplicates a few extra seconds; stronger neighborhood       |

The anchored rule is idempotent: replaying a manifest against the
same source WAV reproduces the exact same anchored clip.
Consequences the report reader should keep in mind:

- Anchored-tail overlap with its predecessor is `>= 5 s`, generically
  larger. In `seed_long_87s.wav` the standard overlap is `5.0 s` and
  the anchored overlap is `23.0 s`.
- The validator accepts overlaps `>= OVERLAP_S - 1/sr_hz`, not
  exactly `OVERLAP_S`, so anchored clips need no special case.
- Short-song fallback (`n_samples < clip_len`): emit one clip that
  spans the whole source, mark `short_song=true`, and exempt the
  manifest from the pairwise overlap invariant. No zero-padding.

## 5. Two-front-door parity

The harvester exposes two entry points:

- `local_folder(path, clip_dir, manifest_dir)` — enumerates
  `*.wav|*.mp3|*.flac|*.m4a|*.ogg|*.opus`, transcodes every source
  through `ffmpeg -ac 1 -ar 22050 -c:a pcm_s16le`, then chunks.
- `youtube_playlist(url, clip_dir, manifest_dir, runner=...)` —
  invokes `yt-dlp -f bestaudio -x --audio-format wav
  --extractor-args youtube:player_client=tv_embedded` into a temp
  dir, then feeds each downloaded file into the same
  `_decode_to_wav` / `chunk` / `write_manifest` seam. On egress
  failure it appends a status row to `egress_status.jsonl` and
  returns `[]` — a blocked door is logged, never fatal.

Both paths converge at `harvester._emit(...)` which calls the
chunker. `tests/test_ingest.py::test_local_and_youtube_manifest_parity`
proves that after normalizing the two known differences
(`source_type` and `source_ref`), the source rows are identical and
the clip rows differ only in `clip_path`.

## 6. Non-blocking egress probe

The probe is deliberately cheaper than the full harvest: metadata
resolution + 1 KB range request against `*.googlevideo.com`. It
targets a small known Creative-Commons YouTube video —
`jNQXAC9IVRw` ("Me at the zoo", ~19 s) — so a *success* is also
cheap. All subprocess calls are hard-timeout wrapped; the probe
never raises, never spins.

**Live snapshot (this cycle, tail of `egress_status.jsonl`):**

```
{"bytes_downloaded":0,"http_code":403,"media_ok":false,
 "metadata_ok":true,"note":"http_code=403 bytes=0",
 "stream_url_present":true,"ts":"2026-08-28T04:18:54Z",
 "video_id":"jNQXAC9IVRw"}
```

This matches `corpus/CORPUS_STATUS.md`: **metadata resolves,
media bytes are refused with HTTP 403.** The rated corpus therefore
cannot be downloaded on this cycle and downstream work must proceed
without it.

**Subtle finding worth calling out for future cycles.** An earlier
version of the probe treated an unfollowed 302 redirect as success.
When a later cycle re-runs the probe, it should look at
`bytes_downloaded > 0` (not `http_code` alone) as the definitive
"the CDN answered with bytes" signal. Any curl `-o /dev/null` probe
without `-L` will *lie* about reachability.

**Escalation rule (matches the brief).** `harvest_playlists.sh` is
invoked only after the probe reports `media_ok=true` across two
consecutive cycles. Anything less risks a multi-hour download
against a wall.

## 7. Seed audio (CC-0, deterministic)

All three seeds are pure NumPy synthesis with a fixed RNG seed.
Their sha256s below are the reproducibility contract — regenerating
the seeds in a fresh workspace must reproduce these exact bytes.

| file                | duration | size      | sha256                                                                 |
|---------------------|---------:|----------:|------------------------------------------------------------------------|
| `seed_short_22s.wav` |   22.0 s |   970 244 | `25f4f060bec2853c3446a9cfcaef170640001392a956c693df544469f4f08a93`     |
| `seed_mid_50s.wav`   |   50.0 s | 2 205 044 | `0ccf49959b91b9cb7e8c1aee8d142ea0e42942c5b354d1b822fa3456f5dfd30a`     |
| `seed_long_87s.wav`  |   87.0 s | 3 836 744 | `eaaaad4b5dd208b0272b9ae4ad389e0cea37a1ef0ca327394e3e9677b7e3afef`     |

Chunker outputs for each:

```
seed_short_22s.wav  src=d251556aedfe35ef  clips=1
  clip 0  t=[0.000, 22.000]  short_song=True  anchored_tail=False

seed_mid_50s.wav    src=d15d5c009a70cc32  clips=2
  clip 0  t=[0.000, 30.000]  short_song=False  anchored_tail=False
  clip 1  t=[20.000, 50.000] short_song=False  anchored_tail=True   (overlap 10.0 s)

seed_long_87s.wav   src=d60cead66dbd0b95  clips=4
  clip 0  t=[ 0.000, 30.000]  short_song=False  anchored_tail=False
  clip 1  t=[25.000, 55.000]  short_song=False  anchored_tail=False (overlap 5.0 s)
  clip 2  t=[50.000, 80.000]  short_song=False  anchored_tail=False (overlap 5.0 s)
  clip 3  t=[57.000, 87.000]  short_song=False  anchored_tail=True  (overlap 23.0 s)
```

## 8. Test suite

`python -m tests.test_ingest` — no pytest dependency; the file
exposes `run_all()` and returns non-zero on failure.

```
PASS test_determinism_across_runs
PASS test_overlap_invariant_standard
PASS test_tail_anchored_final_clip
PASS test_short_song_single_clip
PASS test_boundary_appears_in_two_clips
PASS test_schema_required_fields_pass
PASS test_schema_bad_manifest_fails
PASS test_replay_round_trip
PASS test_append_only_no_duplicates
PASS test_container_invariance
PASS test_local_and_youtube_manifest_parity
PASS test_youtube_egress_failure_logged_not_raised
PASS test_egress_probe_returns_within_timeout
PASS test_egress_probe_appends_status_line

14 passed, 0 failed
```

Coverage map to the sufficiency criteria in the research brief:

- Chunker (§ Sufficiency criteria #1) — 5 tests.
- Provenance replay proof (§ #2) — `test_replay_round_trip`,
  `test_schema_required_fields_pass`, `test_append_only_no_duplicates`,
  `test_container_invariance`.
- Harvester parity (§ #3) — `test_local_and_youtube_manifest_parity`,
  `test_youtube_egress_failure_logged_not_raised`.
- Egress probe non-blocking (§ #4) —
  `test_egress_probe_returns_within_timeout`,
  `test_egress_probe_appends_status_line` + live probe log.
- Doc deliverable (§ #5) — this file + `provenance_schema.md`.

## 9. Sufficiency check (self-assessment)

| Criterion (from brief)                                                        | Status  | Evidence                                                       |
|-------------------------------------------------------------------------------|---------|----------------------------------------------------------------|
| Chunker: `pytest test_chunker.py` green on all three seeds                    | ✅      | 5 chunker tests green (pytest replaced with stdlib runner).    |
| Provenance replay reproduces byte-identical clips after `rm -rf clips`        | ✅      | `test_replay_round_trip` and CLI `replay` cover this.          |
| Local + mocked-YouTube manifests structurally identical                       | ✅      | `test_local_and_youtube_manifest_parity`.                      |
| At least one live egress probe, status logged                                 | ✅      | Five live probe runs appended to `egress_status.jsonl`.        |
| `docs/ingestion_chassis_report.md` + `docs/provenance_schema.md` cross-linked | ✅      | You are reading it; schema doc is linked at §1.                |

## 10. Issues and uncertainties (call out to auditor)

- **Live probe target dependence.** `jNQXAC9IVRw` is small and CC
  today; if its status changes, a future run may misclassify a
  probe target unavailability as a workspace egress change.
  Mitigation: the probe records `metadata_ok` separately —
  `metadata_ok=false` with `media_ok=false` is "target broken",
  `metadata_ok=true` with `media_ok=false` is "egress blocked".
- **`clip_path` is an absolute-ish string.** The current code writes
  `data/ingestion/clips/<source_id>/<source_id>__NN.wav` relative
  to the workspace root. If someone runs the chunker from a
  different CWD the path breaks. A follow-up cycle should decide
  whether to normalize `clip_path` to workspace-relative in the
  manifest (open question; deferring is fine — the replay proof
  regenerates paths, so it is a cosmetic issue, not a correctness one).
- **Tail-anchored clip duplicates content.** In `seed_long_87s.wav`
  the anchored clip and its predecessor share 23 s. Downstream
  stages that aggregate per-clip must not double-count where an
  anchored tail contributes; the `anchored_tail` flag exists so
  they can debias.
- **Egress probe finding.** `bytes_downloaded=0` alongside
  `http_code=403` is the current-cycle CDN state, matching
  `CORPUS_STATUS.md`. Recorded here so future cycles can compare
  exact codes and detect a policy change.

## 11. Ledger events emitted this cycle

Four events, all `M-INGEST-1` sub-milestones marked
`status=validated`, `confidence.level=high`:

- `M-INGEST-1/chunker`
- `M-INGEST-1/provenance`
- `M-INGEST-1/harvester-parity`
- `M-INGEST-1/egress-probe`

Along with one rollup `M-INGEST-1` event marking the milestone
`validated` and cross-referencing this report.
