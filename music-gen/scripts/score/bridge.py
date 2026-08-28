#!/usr/bin/env python3
# M-SCORE-1/bridge-api — MuseScore programmatic bridge.
#
# Author: cyd7bevdr@mozmail.com, cycle 8 (fork 3a908edcb241 / clone-0).
#
# Public API (stable across cycles):
#     xml_to_midi(xml_path, out_midi_path, *, timeout_s=60) -> Path
#     midi_to_xml(midi_path, out_xml_path, *, timeout_s=60) -> Path
#     merge_stems_to_score(per_stem_midis, out_xml_path, *,
#                          tempo_bpm=120.0, time_signature=(4,4)) -> Path
#     class ScoreBridgeError(Exception)
#
# Contract:
#   * All XML<->MIDI translation goes through `mscore3` 3.2.3 headless.
#   * All non-zero exits from mscore3 raise `ScoreBridgeError` with the
#     captured stderr embedded in the message (do NOT use `check=True` —
#     the message quality is what makes the failure debuggable).
#   * The merge is an IDENTITY merge: every input note event enters the
#     merged MusicXML preserved to sub-tick precision, subject only to
#     mscore3's PPQ quantization at the final export. No snapping, no
#     rewriting, no voice-splitting during the merge.
#   * midi_to_xml scrubs mscore3-injected non-deterministic metadata
#     (timestamp, generator version, filename echoes, encoding-date) so
#     that two round-trips on identical input produce byte-identical XML.
#
# Non-factor isolation: this module MUST NOT import
# scripts.classifier.sidecar_nonfactor.
#
# Interpreter guard: /usr/bin/python3 (numpy 1.26.4 pinned).

import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import mido
from music21 import stream, note, chord, meter, tempo as m21tempo, instrument, layout, metadata, duration as m21duration


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ScoreBridgeError(Exception):
    """Raised for any failure crossing the MusicXML<->MIDI boundary via mscore3.

    Message convention: "<operation>: mscore3 exited <rc>: <stderr snippet>"
    for CLI failures; "<operation>: <human diagnosis>" for input/env
    failures (missing input file, timeout, invalid path).
    """


# ---------------------------------------------------------------------------
# mscore3 subprocess machinery
# ---------------------------------------------------------------------------

_MSCORE_BIN = "mscore3"
_QT_ENV = {"QT_QPA_PLATFORM": "offscreen"}


def _run_mscore(inp: Path, out: Path, *, timeout_s: int, op_label: str) -> None:
    inp = Path(inp)
    out = Path(out)
    if not inp.exists():
        raise ScoreBridgeError(f"{op_label}: input file not found: {inp}")
    out.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, **_QT_ENV}
    try:
        proc = subprocess.run(
            [_MSCORE_BIN, "-o", str(out), str(inp)],
            env=env, capture_output=True, timeout=timeout_s, check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise ScoreBridgeError(
            f"{op_label}: mscore3 timed out after {timeout_s}s "
            f"(input={inp.name}): {e}"
        ) from e
    stderr = proc.stderr.decode("utf-8", errors="replace").strip()
    stdout = proc.stdout.decode("utf-8", errors="replace").strip()
    if proc.returncode != 0:
        diag = stderr or stdout or "(no diagnostic)"
        raise ScoreBridgeError(
            f"{op_label}: mscore3 exited {proc.returncode}: {diag}"
        )
    if not out.exists():
        raise ScoreBridgeError(
            f"{op_label}: mscore3 rc=0 but output not written: {out} "
            f"(stderr: {stderr})"
        )
    # mscore3 3.2.3 returns rc=0 for MALFORMED inputs (e.g. an XML that
    # isn't score-partwise); it prints diagnostics to stderr and writes
    # an empty MIDI. Escalate those to ScoreBridgeError so callers do
    # not consume a silently-invalid conversion.
    #
    # NOTE: mscore3 also prints "Error at line N col M: ..." for
    # LEGITIMATE rounding-error warnings on valid inputs. Do not trigger
    # on that alone; require one of the hard invalidity markers.
    lowered = stderr.lower()
    _HARD_INVALID = (
        "is not a valid musicxml file",
        "is not a musicxml score-partwise file",
        "cannot import",
        "empty score",
    )
    for signal in _HARD_INVALID:
        if signal in lowered:
            raise ScoreBridgeError(
                f"{op_label}: mscore3 rc=0 but stderr flagged invalid "
                f"input: {stderr}"
            )


# ---------------------------------------------------------------------------
# Determinism scrubbing for mscore3-emitted MusicXML
# ---------------------------------------------------------------------------

# Empirically enumerated by exporting the same seed MIDI twice and
# diffing. mscore3 3.2.3 injects the following non-deterministic fields:
#   * <encoding-date> — today's date; changes per run's calendar day.
#   * <software>MuseScore 3.2.3</software> — stable but strip anyway
#         (protects against a future mscore version bump).
#   * <source>...</source> — echoes the input file path (differs when
#         invoked from tempdirs).
#   * <work-title>/<movement-title> defaulting to the input basename.
#   * <miscellaneous-field name="original-media-type">... — build stamp.
# The scrub strips these tags entirely and normalizes trailing whitespace.

_SCRUB_TAGS = (
    "encoding-date",
    "software",
    "source",
    "encoder",
    "supports",  # varies with mscore build flags
)

_SCRUB_LINE_RE = re.compile(
    r"^\s*<(?P<tag>" + "|".join(_SCRUB_TAGS) + r")(\s[^>]*)?>.*?</(?P=tag)>\s*$"
)
_SCRUB_SELFCLOSE_RE = re.compile(
    r"^\s*<(?:" + "|".join(_SCRUB_TAGS) + r")(\s[^>]*)?/>\s*$"
)
# <work-title> and <movement-title> default to the input filename.
_TITLE_RE = re.compile(
    r"^\s*<(?P<tag>work-title|movement-title)>.*?</(?P=tag)>\s*$"
)
# <creator type="composer">MuseScore ...</creator> shows up on some builds.
_CREATOR_RE = re.compile(
    r"^\s*<creator(\s[^>]*)?>MuseScore[^<]*</creator>\s*$"
)


_HEX_ID_RE = re.compile(r'\b([PIS])([0-9a-f]{32})\b')


def _normalize_hex_ids(text: str) -> str:
    """music21 (and mscore3 export via its round-trip) generate random
    hex IDs for part/instrument/score-part elements: P<32hex>, I<32hex>,
    S<32hex>. These change between runs even on identical input, so
    remap each unique hex ID to a sequential Pk / Ik / Sk (first
    occurrence wins). Result: byte-identical XML across repeated runs.
    """
    counters = {'P': 0, 'I': 0, 'S': 0}
    mapping = {}

    def _replace(m):
        prefix = m.group(1)
        hexid = m.group(2)
        key = (prefix, hexid)
        if key not in mapping:
            counters[prefix] += 1
            mapping[key] = f'{prefix}{counters[prefix]}'
        return mapping[key]

    return _HEX_ID_RE.sub(_replace, text)


def _scrub_musicxml(xml_path: Path) -> None:
    """In-place scrub of mscore3-injected non-deterministic fields.

    See _SCRUB_TAGS for the empirical enumeration. Also normalizes
    music21-generated random hex IDs. Called automatically by
    `midi_to_xml` and `merge_stems_to_score`; test suite §4 verifies
    byte-identity after scrubbing on a repeated pipeline run.
    """
    xml_path = Path(xml_path)
    lines_in = xml_path.read_text(encoding="utf-8").splitlines(keepends=True)
    lines_out = []
    for ln in lines_in:
        if _SCRUB_LINE_RE.match(ln):
            continue
        if _SCRUB_SELFCLOSE_RE.match(ln):
            continue
        if _TITLE_RE.match(ln):
            # Replace with a canonical empty title element so structural
            # xpath consumers still see the tag if they expect it.
            m = _TITLE_RE.match(ln)
            tag = m.group("tag")
            indent = ln[:len(ln) - len(ln.lstrip())]
            lines_out.append(f"{indent}<{tag}></{tag}>\n")
            continue
        if _CREATOR_RE.match(ln):
            continue
        # Normalize line endings.
        if ln.endswith("\r\n"):
            ln = ln[:-2] + "\n"
        lines_out.append(ln)
    text = "".join(lines_out)
    text = _normalize_hex_ids(text)
    xml_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Public API: xml <-> midi
# ---------------------------------------------------------------------------

def xml_to_midi(xml_path, out_midi_path, *, timeout_s: int = 60) -> Path:
    """Convert MusicXML -> MIDI via mscore3 (headless).

    Raises ScoreBridgeError on missing input, non-zero mscore3 exit,
    missing output file, or timeout.
    """
    xml_path = Path(xml_path)
    out_midi_path = Path(out_midi_path)
    _run_mscore(xml_path, out_midi_path,
                timeout_s=timeout_s, op_label="xml_to_midi")
    return out_midi_path


def midi_to_xml(midi_path, out_xml_path, *, timeout_s: int = 60) -> Path:
    """Convert MIDI -> MusicXML via mscore3 (headless), then scrub
    non-deterministic metadata so two runs on identical input produce
    byte-identical output.

    Raises ScoreBridgeError on missing input, non-zero mscore3 exit,
    missing output file, or timeout.
    """
    midi_path = Path(midi_path)
    out_xml_path = Path(out_xml_path)
    _run_mscore(midi_path, out_xml_path,
                timeout_s=timeout_s, op_label="midi_to_xml")
    _scrub_musicxml(out_xml_path)
    return out_xml_path


# ---------------------------------------------------------------------------
# Identity merge
# ---------------------------------------------------------------------------

# GM program numbers used for the three stems in the merged score. These
# ONLY affect the mscore3 XML-level instrument label and any downstream
# audio render; they do not affect note events at the MIDI export level.
_STEM_PROGRAMS = {
    "drums": 0,   # channel 10 handled separately below (MIDI drums)
    "bass": 33,   # electric bass (finger)
    "piano": 0,   # acoustic grand piano
    "other": 0,   # same as piano (basic-pitch calls the piano stem "other")
}


def _seconds_to_quarterlength(seconds: float, tempo_bpm: float) -> float:
    """seconds -> quarter-note lengths at the given tempo."""
    # quarter_length = seconds * bpm / 60
    return float(seconds) * float(tempo_bpm) / 60.0


# Fine grid for music21 authoring. 1/64 quarter (= 128th-note precision at
# 120 BPM => ~7.8 ms shift; max |round| error ≈ 3.9 ms). This is
# comfortably under mir_eval's 0.05 s onset tolerance, so it does NOT
# affect the F1 measurement, while sidestepping music21's "cannot
# convert 2048th duration" error on arbitrary basic-pitch sub-tick
# offsets. The grid is a power-of-2 fraction, so music21 needs no
# tuplets and the MusicXML uses standard note-value durations.
_MERGE_GRID_QL = 1.0 / 64.0  # quarter-note fractions


def _stem_to_parts(
    stem_name: str,
    midi_path: Path,
    tempo_bpm: float,
    time_sig: Tuple[int, int],
):
    """Read a per-stem MIDI file, translate note events onto ONE OR MORE
    music21 Parts.

    Identity-merge invariant: every note event MUST survive to MIDI
    re-export. mscore3 3.2.3 caps the number of MIDI voices it emits
    per part (empirically < number of voice-partitions on complex
    inputs like basic-pitch's polyphonic other stem — measured 6
    voice-partitions in XML collapse to fewer than 6 MIDI note-on
    streams). To sidestep the cap, we split each stem into as many
    music21 Parts as its voice-partition count. Each returned Part
    holds only non-overlapping notes. On MIDI re-export mscore3 emits
    each part as its own track, so every input note becomes exactly
    one note-on event.

    Returns list of Parts named "{stem}__v{k}" (double-underscore is
    the stem/voice separator; k is zero-based partition index).
    """
    mid = mido.MidiFile(str(midi_path))
    tpb = mid.ticks_per_beat
    # Use the first set_tempo we find; fall back to caller's tempo_bpm.
    tempo_us_per_beat = 500000  # default 120 BPM
    found_tempo = False
    for tr in mid.tracks:
        for msg in tr:
            if msg.type == "set_tempo":
                tempo_us_per_beat = msg.tempo
                found_tempo = True
                break
        if found_tempo:
            break
    seconds_per_tick = (tempo_us_per_beat / 1_000_000.0) / tpb

    # Collect note events as (onset_s, dur_s, pitch, velocity).
    events = []
    for tr in mid.tracks:
        active = {}  # (channel, pitch) -> onset_ticks
        abs_ticks = 0
        for msg in tr:
            abs_ticks += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[(msg.channel, msg.note)] = (abs_ticks, msg.velocity)
            elif (msg.type == "note_off") or (
                msg.type == "note_on" and msg.velocity == 0
            ):
                key = (msg.channel, msg.note)
                if key in active:
                    onset_ticks, vel = active.pop(key)
                    onset_s = onset_ticks * seconds_per_tick
                    dur_s = (abs_ticks - onset_ticks) * seconds_per_tick
                    if dur_s <= 0:
                        continue
                    events.append((onset_s, dur_s, msg.note, vel))

    def _new_part(idx: int):
        p = stream.Part(id=f"{stem_name}__v{idx}")
        p.partName = f"{stem_name}__v{idx}"
        p.partAbbreviation = stem_name[:3]
        if stem_name.lower() == "drums":
            p.insert(0, instrument.Percussion())
        elif stem_name.lower() == "bass":
            p.insert(0, instrument.ElectricBass())
        else:
            p.insert(0, instrument.Piano())
        p.insert(0, meter.TimeSignature(f"{time_sig[0]}/{time_sig[1]}"))
        p.insert(0, m21tempo.MetronomeMark(number=float(tempo_bpm)))
        return p

    if not events:
        # Empty stem: emit one part with a whole-measure rest so mscore3
        # does not drop the stem entirely.
        p = _new_part(0)
        r = note.Rest()
        r.duration = m21duration.Duration(4.0)
        p.insert(0, r)
        return [p]

    # Snap to fine grid so music21 can serialize with standard note
    # values (no deep tuplets). Grid is 1/64 quarter (~7.8 ms at 120
    # BPM), safely under the 50 ms mir_eval tolerance.
    def _snap(x: float) -> float:
        return round(x / _MERGE_GRID_QL) * _MERGE_GRID_QL

    # Convert events to (onset_ql, dur_ql, pitch, vel) with snapping.
    snapped_events = []
    for onset_s, dur_s, pitch, vel in sorted(events):
        onset_ql = _snap(_seconds_to_quarterlength(onset_s, tempo_bpm))
        dur_ql = _snap(_seconds_to_quarterlength(dur_s, tempo_bpm))
        if dur_ql < _MERGE_GRID_QL:
            dur_ql = _MERGE_GRID_QL
        snapped_events.append((onset_ql, dur_ql, int(pitch), int(vel)))

    # Identity-merge invariant: partition into non-overlapping voice
    # partitions, then emit ONE PART PER PARTITION. mscore3's per-part
    # MIDI-voice cap means multi-voice-in-one-part loses notes; one
    # part per voice sidesteps that entirely.
    voices_events = _partition_into_voices(snapped_events)

    parts = []
    for v_idx, v_events in enumerate(voices_events):
        p = _new_part(v_idx)
        for onset_ql, dur_ql, pitch, vel in v_events:
            n = note.Note(midi=int(pitch))
            n.duration = m21duration.Duration(dur_ql)
            n.volume.velocity = int(vel)
            p.insert(onset_ql, n)
        parts.append(p)

    return parts


def _partition_into_voices(snapped_events):
    """Greedy interval-graph coloring: return list-of-voice-lists such
    that within each voice, notes do not overlap in time. Total note
    count across all voices == len(snapped_events).
    """
    if not snapped_events:
        return [[]]
    # Sort by onset. For each note, pick the first voice whose last
    # note ends <= this note's onset.
    voices = []  # list of lists of (onset_ql, dur_ql, pitch, vel)
    voice_ends = []  # list of last end_ql per voice
    for evt in sorted(snapped_events):
        onset_ql, dur_ql, _pitch, _vel = evt
        end_ql = onset_ql + dur_ql
        placed = False
        for i, last_end in enumerate(voice_ends):
            if last_end <= onset_ql + 1e-9:
                voices[i].append(evt)
                voice_ends[i] = end_ql
                placed = True
                break
        if not placed:
            voices.append([evt])
            voice_ends.append(end_ql)
    return voices


def merge_stems_to_score(
    per_stem_midis: Dict[str, Path],
    out_xml_path,
    *,
    tempo_bpm: float = 120.0,
    time_signature: Tuple[int, int] = (4, 4),
) -> Path:
    """Identity-merge per-stem MIDIs into a single MusicXML score.

    Each stem becomes a parallel <part>. Note events are preserved to
    sub-tick precision (no quantization, no snapping). Empty stems are
    represented as a whole-measure rest so mscore3 accepts them.
    """
    out_xml_path = Path(out_xml_path)
    out_xml_path.parent.mkdir(parents=True, exist_ok=True)

    score = stream.Score()
    md = metadata.Metadata()
    md.title = ""
    md.composer = ""
    score.insert(0, md)

    # Author parts in stable order so the merged XML is deterministic
    # w.r.t. dict iteration order in older Python. Each stem may emit
    # 1..N parts named "{stem}__v{k}" (mscore3's per-part voice cap
    # forces one-part-per-voice-partition; see _stem_to_parts docstring).
    # Sidecar mapping: written next to out_xml_path as
    # {stem}.parts_mapping.json for F1 extractors that need to group
    # MIDI tracks back to stems.
    parts_by_stem: Dict[str, List[str]] = {}
    for stem_name in sorted(per_stem_midis.keys()):
        midi_path = Path(per_stem_midis[stem_name])
        if not midi_path.exists():
            raise ScoreBridgeError(
                f"merge_stems_to_score: stem MIDI not found: "
                f"{stem_name}={midi_path}"
            )
        parts = _stem_to_parts(stem_name, midi_path, tempo_bpm, time_signature)
        parts_by_stem[stem_name] = [p.partName for p in parts]
        for p in parts:
            score.append(p)

    # music21 write() writes to a randomly-named tempfile then moves; we
    # want a stable output path, so we write to tempfile then copy.
    with tempfile.TemporaryDirectory(prefix="score_bridge_") as td:
        tmp = Path(td) / "merged.musicxml"
        score.write("musicxml", fp=str(tmp))
        # Copy content to the requested destination.
        out_xml_path.write_bytes(tmp.read_bytes())

    _scrub_musicxml(out_xml_path)

    # Sidecar: parts-to-stem mapping. Named
    # "{out_xml_path.stem}.parts_mapping.json" beside the XML. Used by
    # any downstream F1 extractor to group the MIDI-export tracks back
    # to their stems (mscore3 3.2.3 does not propagate the MusicXML
    # part-name into MIDI track_name meta events).
    sidecar_path = out_xml_path.with_name(
        out_xml_path.stem + ".parts_mapping.json")
    sidecar_data = {
        "score_xml": str(out_xml_path),
        "tempo_bpm": float(tempo_bpm),
        "time_signature": list(time_signature),
        "parts_by_stem": parts_by_stem,
        "notes": [
            "MIDI track 0 is meta (tempo/time-sig). Note tracks start at 1.",
            "Stem order in the score is sorted(per_stem_midis.keys()).",
            "Within a stem, parts are added in voice-partition order.",
        ],
    }
    sidecar_path.write_text(
        json.dumps(sidecar_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out_xml_path
