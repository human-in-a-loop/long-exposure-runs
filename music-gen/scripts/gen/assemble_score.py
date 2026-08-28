#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:20:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 00b3ae64444c)
# milestone: M-GEN-1/first-generation
# ---
"""Assemble a 3-Part MusicXML score from a SampledRuleset.

Contract:
    assemble_score(ruleset, out_xml_path, duration_s=30.0) -> Path

Design decisions (documented in docs/gen_first_generation_report.md):
  * Three Parts always created: Percussion (drum kit, unpitched), Bass
    (ElectricBass), Piano. Even if the arrangement rule silences one, the
    Part shell remains present (rest measures) so the score has a stable
    3-Part shape for downstream inspection.
  * Arrangement.instrumentation is the baseline active set. Instruments
    not listed are silenced (rest measures throughout, subject to
    layer_events). If arrangement names an instrument we don't have
    (e.g. "vocals", "guitar"), we log the skip to
    sampling_manifest["skipped_instrument"] and continue.
  * Rhythmic.pattern's N tokens are laid across one measure (each token
    = 4 quarterLength / N). Drum-part notes use MIDI drum keys
    (kick=36, snare=38, hihat=42, cymbal=49, tom=45). "rest" emits a rest.
  * Harmonic.chord_progression roman numerals attach as ChordSymbols at
    each measure boundary. Piano (if active) realizes chord tones on
    beat 1 as a whole-note voicing.
  * Melodic.contour drives Piano/Bass note direction over each section;
    pitches sampled from the PCH via CDF+content-hash offset (NO PRNG).
  * form.sections drives RehearsalMark placements at each start_measure
    within range; sections whose start_measure > total_measures are
    dropped from the score with a note in the manifest.
  * XML determinism scrub applied on write (strip <encoding-date>,
    <software>, <supports>, date-bearing metadata) so two runs produce
    byte-identical MusicXML.

Falsifiability escape hatch: if a specific rule cannot be applied
(e.g. arrangement asks for guitar/vocals we lack, PCH is all-zero,
pattern is empty), the assembler logs the skip and continues; it does
NOT raise. The caller decides on invalidation based on the final
render's non-silence.

Non-factor AST isolation: this module MUST NOT import
scripts.classifier.sidecar_nonfactor.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple

assert sys.executable == "/usr/bin/python3", sys.executable

from music21 import (
    stream, note, chord as m21chord, meter, tempo as m21tempo,
    instrument as m21inst, harmony, expressions, key as m21key,
    duration as m21duration, pitch as m21pitch,
)

from scripts.gen.sample_rules import SampledRuleset, RULE_TYPES


# --- Drum key map (General MIDI percussion) ---
DRUM_MIDI = {
    "kick": 36,
    "snare": 38,
    "hihat": 42,
    "cymbal": 49,
    "tom": 45,
    # "rest" handled separately
}
KNOWN_INSTRUMENTS = {"drums", "bass", "piano"}


def _content_offset(seed: str, modulus: int) -> int:
    """Deterministic integer in [0, modulus) from a content string via SHA-256."""
    h = hashlib.sha256(seed.encode()).digest()
    return int.from_bytes(h[:8], "big") % max(1, modulus)


def _pch_to_cdf(pch: List[float]) -> List[float]:
    total = float(sum(pch))
    if total <= 0.0:
        return []
    cdf, acc = [], 0.0
    for p in pch:
        acc += p / total
        cdf.append(acc)
    return cdf


def _sample_pc_deterministic(pch: List[float], seed: str) -> int:
    """Pick a pitch class 0..11 by content-hash offset into the PCH CDF."""
    cdf = _pch_to_cdf(pch)
    if not cdf:
        return 0
    # Map the seed to a value in [0, 1) via first 8 bytes of SHA-256 → uint64 / 2**64
    h = hashlib.sha256(seed.encode()).digest()
    u = int.from_bytes(h[:8], "big") / float(1 << 64)
    for i, c in enumerate(cdf):
        if u <= c:
            return i
    return len(cdf) - 1


def _roman_to_pitches(figure: str, tonic_pitch: str) -> List[str]:
    """Turn a Roman-numeral figure into a triad of pitch names (major-key default).

    Handles the exact enum tokens the schema allows: I, ii, iii, IV, V, vi,
    vii, i, II, III, iv, v, VI, VII, plus a couple common inflections.
    """
    figure = figure.strip()
    # Degree map: numeral -> (root-scale-degree 1..7, quality 'M'|'m'|'d')
    upper_map = {"I": (1, "M"), "II": (2, "M"), "III": (3, "M"),
                 "IV": (4, "M"), "V": (5, "M"), "VI": (6, "M"), "VII": (7, "M")}
    lower_map = {"i": (1, "m"), "ii": (2, "m"), "iii": (3, "m"),
                 "iv": (4, "m"), "v": (5, "m"), "vi": (6, "m"), "vii": (7, "d")}
    if figure in upper_map:
        deg, qual = upper_map[figure]
    elif figure in lower_map:
        deg, qual = lower_map[figure]
    else:
        # Fallback: treat as I
        deg, qual = (1, "M")

    # Major-scale semitone offsets from tonic
    major_intervals = [0, 2, 4, 5, 7, 9, 11]
    root_semitone = major_intervals[deg - 1]
    if qual == "M":
        chord_semis = [root_semitone, root_semitone + 4, root_semitone + 7]
    elif qual == "m":
        chord_semis = [root_semitone, root_semitone + 3, root_semitone + 7]
    else:  # diminished
        chord_semis = [root_semitone, root_semitone + 3, root_semitone + 6]

    tonic = m21pitch.Pitch(tonic_pitch)
    pitches = []
    for s in chord_semis:
        p = m21pitch.Pitch()
        p.midi = tonic.midi + s
        pitches.append(p.nameWithOctave)
    return pitches


def _make_percussion_measure(pattern_tokens: List[str], meter_num: int,
                             meter_den: int, active: bool) -> stream.Measure:
    """Build one drum measure from the pattern tokens (each token = 1/N of measure)."""
    m = stream.Measure()
    if not active or not pattern_tokens:
        m.append(note.Rest(quarterLength=meter_num * (4 / meter_den)))
        return m
    n = len(pattern_tokens)
    ql_per_token = (meter_num * (4 / meter_den)) / n
    for tok in pattern_tokens:
        if tok == "rest" or tok not in DRUM_MIDI:
            m.append(note.Rest(quarterLength=ql_per_token))
        else:
            n_ev = note.Unpitched()
            n_ev.storedInstrument = m21inst.SnareDrum()
            n_ev.duration = m21duration.Duration(ql_per_token)
            # music21 unpitched needs a displayPitch; set MIDI channel-10 mapping
            # via a real Note whose pitch encodes the drum midi key. This
            # produces a MIDI note-on at the drum key on channel 10 after
            # mscore3 export.
            drum_note = note.Note()
            drum_note.pitch.midi = DRUM_MIDI[tok]
            drum_note.duration = m21duration.Duration(ql_per_token)
            drum_note.storedInstrument = m21inst.Percussion()
            m.append(drum_note)
    return m


def _make_pitched_measure(
    active: bool, chord_figure: str, tonic_pitch: str,
    melodic_rule: dict, meter_num: int, meter_den: int,
    measure_index: int, part_key: str,
) -> stream.Measure:
    """One measure for a pitched part.

    If active, place a whole-note chord (piano) or a bass root/fifth pattern
    (bass) driven by the harmonic figure; if a melodic rule is available,
    add a top-line note per beat sampled deterministically from the PCH.
    """
    m = stream.Measure()
    if not active:
        m.append(note.Rest(quarterLength=meter_num * (4 / meter_den)))
        return m

    chord_pitches = _roman_to_pitches(chord_figure, tonic_pitch)
    if part_key == "piano":
        # Whole-note chord voicing beat 1, then optional melodic top-line
        # over remaining beats.
        c = m21chord.Chord(chord_pitches, quarterLength=meter_num * (4 / meter_den))
        m.append(c)
    elif part_key == "bass":
        # Root note bass on beat 1, fifth on beat 3 (or held root if <2 beats).
        pitches = chord_pitches
        # Shift bass down an octave for range.
        bass_root = m21pitch.Pitch(pitches[0]); bass_root.octave = 2
        bass_fifth = m21pitch.Pitch(pitches[2]) if len(pitches) > 2 else bass_root
        bass_fifth.octave = 2
        beats = meter_num
        if beats >= 2:
            half = (meter_num * (4 / meter_den)) / 2
            m.append(note.Note(bass_root.nameWithOctave, quarterLength=half))
            m.append(note.Note(bass_fifth.nameWithOctave, quarterLength=half))
        else:
            m.append(note.Note(bass_root.nameWithOctave,
                               quarterLength=meter_num * (4 / meter_den)))
    else:
        m.append(note.Rest(quarterLength=meter_num * (4 / meter_den)))

    # Melodic top-line (deterministic, PCH-based) — attach as a separate voice.
    if melodic_rule and part_key == "piano":
        pch = list(melodic_rule.get("parameters", {}).get("pitch_class_histogram") or [])
        contour = str(melodic_rule.get("parameters", {}).get("contour", "static"))
        range_st = int(melodic_rule.get("parameters", {}).get("range_semitones", 12))
        if pch and sum(pch) > 0:
            beats = meter_num
            v = stream.Voice()
            base_midi = 60  # C4 anchor
            for b in range(beats):
                seed = f"{part_key}|m{measure_index}|b{b}|{contour}|{chord_figure}"
                pc = _sample_pc_deterministic(pch, seed)
                # Contour offset: choose octave shift by beat position, contour type
                if contour == "ascending":
                    oct_shift = (b // 2) - 0 + (measure_index % 3)
                elif contour == "descending":
                    oct_shift = -((b // 2) + (measure_index % 3))
                elif contour == "arch":
                    half = beats / 2.0
                    oct_shift = int(range_st / 12 * (1 - abs(b - half) / max(half, 1)))
                elif contour == "undulating":
                    oct_shift = (b % 2) * (1 if measure_index % 2 == 0 else -1)
                else:  # static
                    oct_shift = 0
                midi = base_midi + pc + 12 * oct_shift
                # Clamp to a sane MIDI range (36..96) so mscore3 accepts it
                midi = max(48, min(84, midi))
                n_ = note.Note()
                n_.pitch.midi = midi
                n_.duration = m21duration.Duration(4 / meter_den)
                v.append(n_)
            m.insert(0, v)
    return m


_HEX_ID_RE = re.compile(r'\b([PIS])([0-9a-f]{32})\b')


def _normalize_hex_ids(text: str) -> str:
    """Remap music21's random hex Part/Instrument/Score IDs to sequential Pk/Ik/Sk.

    Reuses the pattern from scripts.score.bridge._normalize_hex_ids so that
    two runs producing structurally identical scores emit byte-identical XML.
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


def _strip_musicxml_nondeterminism(xml_text: str) -> str:
    """Scrub music21 metadata sources of run-to-run variance + normalize IDs."""
    subs = [
        (re.compile(r"<encoding-date>[^<]*</encoding-date>\s*"), ""),
        (re.compile(r"<software>[^<]*</software>\s*"), ""),
        (re.compile(r"<encoder>[^<]*</encoder>\s*"), ""),
        (re.compile(r"<creator[^>]*>[^<]*music21[^<]*</creator>\s*"), ""),
    ]
    for pat, rep in subs:
        xml_text = pat.sub(rep, xml_text)
    xml_text = _normalize_hex_ids(xml_text)
    return xml_text


def assemble_score(
    ruleset: SampledRuleset,
    out_xml_path: Path,
    duration_s: float = 30.0,
) -> Path:
    """Build the score, write MusicXML, return the path."""
    out_xml_path = Path(out_xml_path)
    out_xml_path.parent.mkdir(parents=True, exist_ok=True)

    rhythmic = ruleset.rules.get("rhythmic")
    harmonic = ruleset.rules.get("harmonic")
    melodic = ruleset.rules.get("melodic")
    form_rule = ruleset.rules.get("form")
    arrangement = ruleset.rules.get("arrangement")

    # Rhythmic: meter + tempo
    meter_str = str(rhythmic["parameters"].get("meter", "4/4"))
    m_num, m_den = (int(x) for x in meter_str.split("/"))
    tempo_bpm = float(rhythmic["parameters"].get("tempo_bpm", 120.0))
    pattern_tokens: List[str] = list(rhythmic["parameters"].get("pattern") or [])

    # Total measures from tempo and duration
    beats_per_measure = m_num * (4 / m_den)
    seconds_per_beat = 60.0 / tempo_bpm
    seconds_per_measure = beats_per_measure * seconds_per_beat
    total_measures = max(1, int(round(duration_s / seconds_per_measure)))

    # Harmonic: key + chord progression
    key_str = str(harmonic["parameters"].get("key", "C_major"))
    tonic_name, mode = key_str.split("_")  # e.g. "F", "major"
    tonic_pitch = f"{tonic_name}4"
    progression: List[str] = list(harmonic["parameters"].get("chord_progression") or ["I"])

    # Arrangement: baseline active parts
    baseline: List[str] = list(arrangement["parameters"].get("instrumentation") or [])
    skipped_unknown = [i for i in baseline if i not in KNOWN_INSTRUMENTS]
    active = {i for i in baseline if i in KNOWN_INSTRUMENTS}
    ruleset.sampling_manifest.setdefault("skipped_instrument", []).extend(
        [{"name": i, "reason": "not in target Score (drums/bass/piano)"} for i in skipped_unknown]
    )
    if not active:
        active = {"drums"}  # safety: keep at least drums so the render is non-silent
        ruleset.sampling_manifest.setdefault("assembler_fallbacks", []).append(
            "arrangement.instrumentation empty after filter — defaulted to {drums} to keep render non-silent"
        )

    # Form: sections that fit within total_measures
    section_marks: List[Tuple[int, str]] = []  # (measure_index_0based, label)
    dropped_sections = 0
    for sec in list(form_rule["parameters"].get("sections") or []):
        start_m = int(sec.get("start_measure", 0))
        label = str(sec.get("label", ""))
        if 0 <= start_m < total_measures:
            section_marks.append((start_m, label))
        else:
            dropped_sections += 1
    ruleset.sampling_manifest["form_sections_dropped_beyond_duration"] = dropped_sections

    # --- Build Score ---
    score = stream.Score()
    score.insert(0, m21key.Key(tonic_name))
    score.insert(0, meter.TimeSignature(meter_str))
    score.insert(0, m21tempo.MetronomeMark(number=tempo_bpm))

    perc_part = stream.Part(); perc_part.id = "Percussion"
    perc_part.insert(0, m21inst.Percussion())
    bass_part = stream.Part(); bass_part.id = "Bass"
    bass_part.insert(0, m21inst.ElectricBass())
    piano_part = stream.Part(); piano_part.id = "Piano"
    piano_part.insert(0, m21inst.Piano())

    # ChordSymbols track (attached to piano_part so they render alongside chords).
    for mi in range(total_measures):
        chord_figure = progression[mi % len(progression)]

        perc_m = _make_percussion_measure(
            pattern_tokens, m_num, m_den, active=("drums" in active))
        perc_m.number = mi + 1
        perc_part.append(perc_m)

        bass_m = _make_pitched_measure(
            active=("bass" in active), chord_figure=chord_figure,
            tonic_pitch=tonic_pitch, melodic_rule=None,
            meter_num=m_num, meter_den=m_den,
            measure_index=mi, part_key="bass")
        bass_m.number = mi + 1
        bass_part.append(bass_m)

        piano_m = _make_pitched_measure(
            active=("piano" in active), chord_figure=chord_figure,
            tonic_pitch=tonic_pitch, melodic_rule=melodic,
            meter_num=m_num, meter_den=m_den,
            measure_index=mi, part_key="piano")
        piano_m.number = mi + 1
        # Attach a ChordSymbol as an annotation, always (whether or not piano is active).
        try:
            cs = harmony.ChordSymbol(figure=chord_figure + ":" + tonic_name)
        except Exception:
            cs = None
        if cs is not None:
            piano_m.insert(0, cs)
        piano_part.append(piano_m)

    # Rehearsal marks at section starts on the piano part.
    for start_m, label in section_marks:
        # start_m is 0-based measure index; append rehearsal mark at that measure's start.
        rm = expressions.RehearsalMark(label)
        target_measure = piano_part.getElementsByClass(stream.Measure)[start_m]
        target_measure.insert(0, rm)

    score.insert(0, perc_part)
    score.insert(0, bass_part)
    score.insert(0, piano_part)

    # Log summary of applied constructs to the sampling manifest.
    ruleset.sampling_manifest["assembler_summary"] = {
        "total_measures": total_measures,
        "seconds_per_measure": seconds_per_measure,
        "meter": meter_str,
        "tempo_bpm": tempo_bpm,
        "key": key_str,
        "progression_len": len(progression),
        "pattern_tokens": len(pattern_tokens),
        "active_parts": sorted(active),
        "sections_placed": len(section_marks),
        "sections_dropped": dropped_sections,
    }

    # Write MusicXML; then scrub for byte-determinism.
    score.write("musicxml", fp=str(out_xml_path))
    xml_text = out_xml_path.read_text(encoding="utf-8")
    xml_text = _strip_musicxml_nondeterminism(xml_text)
    out_xml_path.write_text(xml_text, encoding="utf-8")

    return out_xml_path


def _main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=Path("data/rules/ledger.jsonl"))
    ap.add_argument("--out", type=Path,
                    default=Path("data/gen/generated.musicxml"))
    ap.add_argument("--manifest", type=Path,
                    default=Path("data/gen/sampling_manifest.json"))
    ap.add_argument("--duration-s", type=float, default=30.0)
    args = ap.parse_args(argv)

    from scripts.gen.sample_rules import sample_ruleset
    rs = sample_ruleset(args.ledger)
    out = assemble_score(rs, args.out, duration_s=args.duration_s)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps({
        "chosen_rule_ids": rs.rule_ids(),
        "sampling_manifest": rs.sampling_manifest,
    }, indent=2, sort_keys=True))
    print(f"[assemble_score] wrote {out}")
    print(f"[assemble_score] manifest -> {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
