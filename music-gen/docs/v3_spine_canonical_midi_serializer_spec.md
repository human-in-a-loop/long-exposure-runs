<!--
created: 2026-09-02T00:00:00Z
cycle: 4
run_id: run-2026-09-02T000000Z
agent: worker
milestone: M-V3-SPINE-1/canonical-serializer-spec-committed
-->

# v3 Spine — Canonical JSON→MIDI Serializer Specification

## Purpose

Cycle 3 established that MuScriptor's JSON events on Chicken Grease bass are
byte-deterministic (`sha256 e80ab193…203ae853` twice) while its
`--format midi` output for the same events is not (663 B vs 639 B, first
diff byte 40). Per operator OPTION A (2026-09-02), we canonicalize the
authoritative MIDI ourselves from the byte-deterministic JSON events with
a fully-specified serializer. This document freezes the serializer's
contract BEFORE any implementation lands.

## Contract

### Public API

```python
def serialize(
    json_events_path: str,
    out_midi_path: str,
    tempo_bpm: float,
    time_signature: tuple[int, int],
) -> None
```

Pure function of inputs. No PRNG, no wall-clock, no external I/O beyond
the input JSON path and output MIDI path. Raises `CanonicalSerializerError`
(typed) on any pin mismatch or invalid input.

### Library pin

- `mido == 1.3.3` (installed; version obtained via
  `importlib.metadata.version("mido")` because 1.3.3 does not expose
  `mido.__version__`).
- Version-mismatch raises `CanonicalSerializerError` with message naming
  the actual installed version.

### PPQ / ticks per beat

- **PPQ = 480**. Set at `mido.MidiFile(type=1, ticks_per_beat=480)`.

### Tempo & time-signature meta

- Written as exactly two meta events on track 0 at tick 0:
  - `MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo_bpm), time=0)`
  - `MetaMessage("time_signature", numerator=ts_num, denominator=ts_den,
    clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0)`
- No subsequent tempo changes this cycle (v3 spine renders a fixed-tempo
  chosen section).

### JSON schema (input)

- MuScriptor `--format json` output, a JSON array of events:
  - `start` event: `{"type":"start","pitch":int,"start_time":float,
    "index":int,"instrument":str}`
  - `end` event: `{"type":"end","end_time":float,"start_event_index":int}`
- Each `end` references the matching `start` via `start_event_index`.
- Events with no matching `end` (dangling `start`) are given a 100 ms
  synthetic duration and flagged in the serializer log.
- Events with `end_time` earlier than or equal to `start_time` after
  rounding to ticks are widened by 1 tick so `note_off` follows
  `note_on`.

### Instrument→channel mapping

Deterministic per-stem channel assignment (used for stems that mix
multiple instrument labels, e.g. `full_mix`):

| MuScriptor label prefix       | Channel (0-indexed) |
|-------------------------------|---------------------|
| `drums`                        | 9 (GM channel 10)   |
| `electric_bass` / `bass_*`     | 0                   |
| `clean_electric_guitar` / `distorted_electric_guitar` / `guitar*` | 1 |
| `piano` / `acoustic_piano` / `electric_piano` | 2 |
| `voice`                        | 3                   |
| everything else                | 4                   |

For per-stem serialization, the stem's own default channel is used and
this mapping is a no-op.

### Sort key (event ordering in MIDI stream)

Events sorted by tuple:

```
(tick, channel, pitch, event_kind)
```

where `event_kind = 0` for note-on, `1` for note-off. Note-on before
note-off explicitly documented so simultaneous events for the same
`(tick, channel, pitch)` do not silence the note.

### Empty-events baseline

If the JSON array is empty, the serializer writes a minimal MIDI
containing the tempo + time-signature meta only. Byte-determinism ×2
holds trivially.

### JSON canonicalization for cache invariance

If the caller re-serializes an existing JSON blob (e.g. for a
byte-determinism ×2 probe), canonical form is:

```
json.dumps(events, sort_keys=True, separators=(",",":"),
           ensure_ascii=False)
```

with LF line endings.

### Determinism / no-nondeterminism sources

- No PRNG usage anywhere (`ast.parse` grep gate at test time).
- No wall-clock (`time.time()` / `datetime.now()`) — the file MUST NOT
  contain them, checked by test.
- No dict-order dependence: all events are written from a list sorted
  by the explicit sort key above.
- No environment reads beyond argv.

### Writer (I/O)

- `mido.MidiFile.save(path)` on a `tempfile.NamedTemporaryFile(delete=False,
  dir=out_dir)`, followed by `os.replace(tmp_path, out_midi_path)` for
  atomic write (mido 1.3.3 does not accept an `atomic_write` kwarg).

## Test coverage requirement (≥8 cases)

1. PPQ correct: read back MIDI, assert `ticks_per_beat == 480`.
2. Sort-key exhaustive: 3 events at the same tick with different
   `(channel, pitch, kind)` produce a canonical ordering that reproduces
   ×2.
3. On-before-off: `start` and `end` at the same time round to same tick;
   note-on emitted before note-off (verified via mido event iteration).
4. Empty events → minimal file baseline (only tempo + time-signature
   meta); byte-determinism ×2.
5. mido version check: importing the serializer with a fake version raises
   `CanonicalSerializerError`.
6. Byte-determinism ×2 on synthetic 3-note event set.
7. Byte-determinism ×2 on synthetic 12-note event set with overlapping
   pitches.
8. Byte-determinism ×2 on a synthetic empty event set.

## Mtime discipline

This document MUST land on disk BEFORE any script under
`scripts/v3_spine/midi_from_json_events*` or
`scripts/v3_spine/canonicalize_all_probes*`. Test 01 in
`tests/test_v3_spine_c4.py` enforces this via file `st_mtime` ordering.

## SHA pin

The SHA-256 of this document is pinned to
`data/v3_spine/canonical_serializer_spec_hash.txt` on landing.
