#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-05T18:00:00Z
# cycle: 69
# run_id: run-2026-09-05T180000Z
# agent: worker
# milestone: M-V4-SHOWCASE-1/<song>-ab-full-render
# ---
"""Per-song sound-matched A/B delivery driver (v4).

Sibling to c17 ``deliver_cg_ab_v4.py`` (READ-ONLY per FD-1 + invariant (d)).
Extends the CG A/B mix shape to the four non-CG focus songs (WIG + Rome +
Peach Dream + Disco A) per OPERATOR PIVOT DIRECTIVE 2026-09-05.

For each song:
  bass   -> sf2 replay via ``profiles/<song>/bass.json`` (per-song pinned)
  drums  -> sf2 replay via ``profiles/<song>/drums.json`` (per-song pinned)
  guitar -> absent (no pinned profile emitted; honest render per operator)
  piano  -> absent (idem)
  other  -> absent (idem)
  vocals -> htdemucs hybrid overlay from ``<stems-root>/vocals.wav``
             (campaign prompt L59-60)

Per-cell loudness: htdemucs vocals used verbatim; bass + drums render
RMS-normalized to the reference stem RMS at ``<stems-root>/<cell>.wav``.
Sum stereo. Peak-limit at 0.99.

Discipline:
  - 7-key env pin (env_pin_sha256 = 2ac444c3...922ca)
  - /usr/bin/python3 interpreter guard
  - no PRNG, no sidecar_nonfactor, no --verify-det pass-through
  - deterministic sum (float32 accumulate, then int16 quantize)

Writes into <delivery-root>/<song>/:
  ab_mix.wav                summed stereo 30 s @ 44.1 kHz
  ab_mix.manifest.json      per-cell provenance SHAs + env pins
  ab_mix.replay_proof.json  byte-det x2 sha table (per-song, per-family FD-16c)

Path convention: non-standard stems path per invariant (d) is discoverable
via the ``stem_manifest.json`` at ``data/v4/profiles/<song>/`` if present.
Peach Dream is the known non-standard case (c19+): stems live under
``data/v3_spine/<song>/operator_section_c25_checkpointed/rc9_6stem/``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import tempfile
import wave
from pathlib import Path
from typing import Iterable

_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for k, v in _PINS.items():
    os.environ.setdefault(k, v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(f"deliver_ab_v4 requires /usr/bin/python3 (got {sys.executable})")

_ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _read_stereo_int16(path: Path) -> tuple[list[int], list[int], int]:
    with wave.open(str(path), "rb") as w:
        nch = w.getnchannels()
        sr = w.getframerate()
        nframes = w.getnframes()
        sw = w.getsampwidth()
        assert sw == 2, f"expected 16-bit, got sampwidth={sw} for {path}"
        raw = w.readframes(nframes)
    ints = list(struct.unpack("<" + "h" * (len(raw) // 2), raw))
    if nch == 2:
        left = ints[0::2]
        right = ints[1::2]
    else:
        left = ints
        right = list(ints)
    return left, right, sr


def _read_mono_int16(path: Path) -> tuple[list[int], int]:
    with wave.open(str(path), "rb") as w:
        nch = w.getnchannels()
        sr = w.getframerate()
        nframes = w.getnframes()
        sw = w.getsampwidth()
        assert sw == 2, f"expected 16-bit, got sampwidth={sw} for {path}"
        raw = w.readframes(nframes)
    ints = list(struct.unpack("<" + "h" * (len(raw) // 2), raw))
    if nch == 2:
        mono = [(ints[2 * i] + ints[2 * i + 1]) // 2 for i in range(len(ints) // 2)]
        return mono, sr
    return ints, sr


def _write_stereo_int16(path: Path, left: list[int], right: list[int], sr: int) -> None:
    n = min(len(left), len(right))
    interleaved = [0] * (2 * n)
    for i in range(n):
        li = left[i]; ri = right[i]
        if li > 32767: li = 32767
        elif li < -32768: li = -32768
        if ri > 32767: ri = 32767
        elif ri < -32768: ri = -32768
        interleaved[2 * i] = li
        interleaved[2 * i + 1] = ri
    raw = struct.pack("<" + "h" * (2 * n), *interleaved)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(raw)


def _rms_int16(samples: Iterable[int]) -> float:
    n = 0; acc = 0.0
    for s in samples:
        acc += (s / 32768.0) ** 2
        n += 1
    if n == 0:
        return 0.0
    return math.sqrt(acc / n)


def _scale_int16(samples: list[int], gain: float) -> list[int]:
    out = [0] * len(samples)
    for i, s in enumerate(samples):
        v = int(round(s * gain))
        if v > 32767: v = 32767
        elif v < -32768: v = -32768
        out[i] = v
    return out


def _render_via_sf2(profile_path: Path, midi_path: Path, out_wav: Path) -> tuple[str, dict]:
    profile = json.loads(profile_path.read_text())
    from scripts.sound_match.replay import replay  # type: ignore
    sha = replay(profile, midi_path, out_wav)
    return sha, profile


def _rms_match_to_ref(samples_L: list[int], samples_R: list[int],
                      ref_L: list[int], ref_R: list[int]) -> tuple[list[int], list[int], float]:
    ref_rms = 0.5 * (_rms_int16(ref_L) + _rms_int16(ref_R))
    ren_rms = 0.5 * (_rms_int16(samples_L) + _rms_int16(samples_R))
    if ren_rms > 1e-9:
        gain = ref_rms / ren_rms
        if gain > 4.0: gain = 4.0
        if gain < 0.05: gain = 0.05
    else:
        gain = 1.0
    return _scale_int16(samples_L, gain), _scale_int16(samples_R, gain), gain


def _sum_stereo_tracks(tracks: list[tuple[list[int], list[int]]], target_len: int) -> tuple[list[int], list[int]]:
    accL = [0.0] * target_len
    accR = [0.0] * target_len
    for L, R in tracks:
        n = min(len(L), target_len)
        for i in range(n):
            accL[i] += L[i]
            accR[i] += R[i]
    peak = 1.0
    for i in range(target_len):
        a = abs(accL[i]); b = abs(accR[i])
        if a > peak: peak = a
        if b > peak: peak = b
    ceiling = 0.99 * 32767.0
    gain = 1.0 if peak <= ceiling else (ceiling / peak)
    outL = [0] * target_len; outR = [0] * target_len
    for i in range(target_len):
        li = int(round(accL[i] * gain))
        ri = int(round(accR[i] * gain))
        if li > 32767: li = 32767
        elif li < -32768: li = -32768
        if ri > 32767: ri = 32767
        elif ri < -32768: ri = -32768
        outL[i] = li; outR[i] = ri
    return outL, outR


_SILENCE_FLOOR_DBFS = -60.0
_UNPROFILED_STEMS = ("guitar", "piano", "other")


def _absent_stem_dispatch(stem_name: str, stems_dir: Path, root: Path) -> dict:
    """c71: gate absent (no pinned profile) stems on htdemucs audibility.

    Returns a dispatch dict with a `kind` field ∈
    {'absent_no_audible_signal', 'htdemucs_stem_substitution'}.
    When audible (rms_dbfs > -60 dB), also carries the loaded stereo int16
    samples so the caller can splice into the mix.
    """
    from scripts.sound_match.measure_stem_audibility import (  # type: ignore
        measure, SILENCE_FLOOR_DB,
    )
    ref_stem = stems_dir / (stem_name + ".wav")
    if not ref_stem.exists():
        return {"kind": "absent_no_audible_signal",
                "audibility_verdict": False, "reason": "stem_wav_missing"}
    m = measure(ref_stem)
    if not m["verdict_audible"]:
        return {
            "kind": "absent_no_audible_signal",
            "audibility_verdict": False,
            "rms_dbfs": m["rms_dbfs"],
            "peak_dbfs": m["peak_dbfs"],
            "silence_floor_dbfs": SILENCE_FLOOR_DB,
            "ref_stem_relpath": str(ref_stem.relative_to(root)),
            "ref_stem_sha256": m["wav_sha256"],
        }
    left, right, sr = _read_stereo_int16(ref_stem)
    return {
        "kind": "htdemucs_stem_substitution",
        "audibility_verdict": True,
        "rms_dbfs": m["rms_dbfs"],
        "peak_dbfs": m["peak_dbfs"],
        "silence_floor_dbfs": SILENCE_FLOOR_DB,
        "ref_stem_relpath": str(ref_stem.relative_to(root)),
        "ref_stem_sha256": m["wav_sha256"],
        "samples_left": left,
        "samples_right": right,
        "sample_rate": sr,
    }


def _resolve_stems_root(root: Path, song: str) -> Path:
    """Return the operator-section rc9_6stem/ dir for the song, honouring
    the Peach Dream non-standard path per invariant (d)."""
    std = root / "data/v3_spine" / song / "operator_section" / "rc9_6stem"
    if std.is_dir():
        return std
    alt = root / "data/v3_spine" / song / "operator_section_c25_checkpointed" / "rc9_6stem"
    if alt.is_dir():
        return alt
    raise FileNotFoundError(
        f"no stems root found for {song}: tried {std} and {alt}"
    )


def _render_ab_mix(root: Path, song: str, out_wav: Path) -> dict:
    provenance: dict = {}
    profiles_root = root / "data/v4/profiles" / song
    stems_dir = _resolve_stems_root(root, song)

    # Bass
    bass_profile_p = profiles_root / "bass.json"
    bass_midi = profiles_root / "bass_sweep_stage1" / "bass_excerpt.mid"
    bass_tmp = out_wav.parent / f".{song}_bass_render_mono.wav"
    bass_sha, bass_profile = _render_via_sf2(bass_profile_p, bass_midi, bass_tmp)
    bass_mono, sr_b = _read_mono_int16(bass_tmp)
    bass_L, bass_R = list(bass_mono), list(bass_mono)
    ref_bass = stems_dir / "bass.wav"
    refL, refR, sr_rb = _read_stereo_int16(ref_bass)
    bass_L, bass_R, bass_gain = _rms_match_to_ref(bass_L, bass_R, refL, refR)
    provenance["bass"] = {
        "render_family": "sf2",
        "profile_relpath": str(bass_profile_p.relative_to(root)),
        "profile_sha256": _sha(bass_profile_p),
        "midi_relpath": str(bass_midi.relative_to(root)),
        "midi_sha256": _sha(bass_midi),
        "render_sha256": bass_sha,
        "render_sha256_canonical_replay_expected": bass_profile.get("render_sha256_canonical_replay"),
        "rms_normalize_gain": round(bass_gain, 6),
        "ref_stem_relpath": str(ref_bass.relative_to(root)),
        "ref_stem_sha256": _sha(ref_bass),
    }
    for aux in [bass_tmp, bass_tmp.with_suffix(".prog_forced.mid")]:
        try:
            aux.unlink()
        except FileNotFoundError:
            pass

    # Drums
    drums_profile_p = profiles_root / "drums.json"
    drums_midi = profiles_root / "drums_sweep_stage1" / "drums_excerpt.mid"
    drums_tmp = out_wav.parent / f".{song}_drums_render_mono.wav"
    drums_sha, drums_profile = _render_via_sf2(drums_profile_p, drums_midi, drums_tmp)
    drums_mono, sr_d = _read_mono_int16(drums_tmp)
    drums_L, drums_R = list(drums_mono), list(drums_mono)
    ref_drums = stems_dir / "drums.wav"
    drefL, drefR, sr_rd = _read_stereo_int16(ref_drums)
    drums_L, drums_R, drums_gain = _rms_match_to_ref(drums_L, drums_R, drefL, drefR)
    provenance["drums"] = {
        "render_family": "sf2",
        "profile_relpath": str(drums_profile_p.relative_to(root)),
        "profile_sha256": _sha(drums_profile_p),
        "midi_relpath": str(drums_midi.relative_to(root)),
        "midi_sha256": _sha(drums_midi),
        "render_sha256": drums_sha,
        "render_sha256_canonical_replay_expected": drums_profile.get("render_sha256_canonical_replay"),
        "rms_normalize_gain": round(drums_gain, 6),
        "ref_stem_relpath": str(ref_drums.relative_to(root)),
        "ref_stem_sha256": _sha(ref_drums),
    }
    for aux in [drums_tmp, drums_tmp.with_suffix(".prog_forced.mid")]:
        try:
            aux.unlink()
        except FileNotFoundError:
            pass

    # Vocals hybrid overlay
    vocals_stem = stems_dir / "vocals.wav"
    vocals_L, vocals_R, sr_v = _read_stereo_int16(vocals_stem)
    provenance["vocals"] = {
        "render_family": "htdemucs_hybrid_overlay",
        "source_relpath": str(vocals_stem.relative_to(root)),
        "source_sha256": _sha(vocals_stem),
    }

    # Unprofiled stems: c71 audibility-gated htdemucs stem substitution
    # (per operator directive 2026-09-05 + c63 skip-close policy).
    # For each unprofiled stem, if the reference htdemucs stem is audible
    # (rms_dbfs > -60 dB per c14 canonical floor), include the stem in the
    # mix RMS-matched to itself (no-op gain=1.0 for the substituted branch;
    # the reference stem IS the source). Silent stems retain c69 semantics.
    audible_tracks: list[tuple[list[int], list[int]]] = []
    audible_lens: list[int] = []
    audible_srs: set[int] = set()
    import hashlib as _hl
    from scripts.sound_match.measure_stem_audibility import (  # type: ignore
        _env_pin_sha256 as _audibility_env_pin_sha,
    )
    for absent in _UNPROFILED_STEMS:
        dispatch = _absent_stem_dispatch(absent, stems_dir, root)
        if dispatch["kind"] == "htdemucs_stem_substitution":
            L = dispatch["samples_left"]; R = dispatch["samples_right"]
            sr_s = dispatch["sample_rate"]
            # RMS-match to reference: reference IS the source, so gain = 1.0
            audible_tracks.append((L, R))
            audible_lens.append(len(L))
            audible_srs.add(sr_s)
            provenance[absent] = {
                "render_family": "htdemucs_stem_substitution",
                "source_relpath": dispatch["ref_stem_relpath"],
                "source_sha256": dispatch["ref_stem_sha256"],
                "rms_dbfs": dispatch["rms_dbfs"],
                "audibility_verdict": True,
                "audibility_probe_module_sha256": _hl.sha256(
                    Path(__file__).parent.joinpath("measure_stem_audibility.py").read_bytes()
                ).hexdigest(),
                "audibility_env_pin_sha256": _audibility_env_pin_sha(),
                "silence_floor_dbfs": dispatch["silence_floor_dbfs"],
                "rms_normalize_gain": 1.0,
            }
        else:
            provenance[absent] = {
                "render_family": "absent_no_audible_signal",
                "audibility_verdict": False,
                "rms_dbfs": dispatch.get("rms_dbfs"),
                "silence_floor_dbfs": dispatch.get("silence_floor_dbfs"),
                "ref_stem_relpath": dispatch.get("ref_stem_relpath"),
                "ref_stem_sha256": dispatch.get("ref_stem_sha256"),
                "showcase_dispatch": "silent per-track (audibility-gated per c71 fix; c63 skip-close policy)",
            }

    srs = {sr_b, sr_rb, sr_d, sr_rd, sr_v} | audible_srs
    if len(srs) != 1:
        raise RuntimeError(f"sample-rate mismatch across cells: {srs}")
    sr = sr_b

    # c71 fix: max-truncation policy (was min-truncation at c69). Shorter
    # cells zero-pad to the longest cell. Fixes WIG partial-mix issue as
    # a side effect: sparse canonical bass/drums MIDI (~9 s) zero-pad to
    # full section length (~30 s) driven by vocals + audible stems.
    tracks = [(bass_L, bass_R), (drums_L, drums_R), (vocals_L, vocals_R)] + audible_tracks
    lens = [len(bass_L), len(drums_L), len(vocals_L)] + audible_lens
    target_len = max(lens)
    outL, outR = _sum_stereo_tracks(tracks, target_len)
    _write_stereo_int16(out_wav, outL, outR, sr)
    provenance["_mix"] = {
        "sample_rate": sr,
        "n_frames": target_len,
        "duration_s": round(target_len / sr, 6),
        "n_channels": 2,
        "sum_method": "float_accumulate_peaklimit_099_max_len_zero_pad",
        "mix_wav_sha256": _sha(out_wav),
        "cell_lens": {
            "bass": len(bass_L),
            "drums": len(drums_L),
            "vocals": len(vocals_L),
            **{stem: alen for stem, alen in zip(
                [s for s in _UNPROFILED_STEMS if provenance[s]["render_family"] == "htdemucs_stem_substitution"],
                audible_lens
            )},
        },
    }
    return provenance


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Per-song A/B delivery driver (v4 non-CG, c69).")
    ap.add_argument("--song-sha16", required=True)
    ap.add_argument("--delivery-root", default="data/v4/deliveries")
    ap.add_argument("--out", default=None)
    ap.add_argument("--out-suffix", default="",
                    help="c71: filename suffix so v2 outputs land as siblings "
                         "to c69 v1 anchors (e.g. --out-suffix v2 -> ab_mix_v2.wav)")
    ap.add_argument("--prove-replay", action="store_true",
                    help="Second render into fresh tempfile.mkdtemp -> ab_mix.replay_proof.json")
    args = ap.parse_args(argv)

    song = args.song_sha16
    root = Path(__file__).resolve().parents[2]
    delivery_dir = root / args.delivery_root / song
    out_dir = Path(args.out) if args.out else delivery_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    for k, v in _PINS.items():
        if os.environ.get(k) != v:
            raise RuntimeError(f"env pin drift {k}={os.environ.get(k)!r} expected {v!r}")

    _suffix = ("_" + args.out_suffix) if args.out_suffix else ""
    out_wav = out_dir / ("ab_mix" + _suffix + ".wav")
    provenance = _render_ab_mix(root, song, out_wav)

    _is_v2 = bool(args.out_suffix)
    manifest = {
        "kind": "ab_v4_full_render_manifest",
        "song_sha16": song,
        "cycle": 71 if _is_v2 else 69,
        "run_id": "run-2026-09-05T190000Z" if _is_v2 else "run-2026-09-05T180000Z",
        "created": "2026-09-05T19:00:00Z" if _is_v2 else "2026-09-05T18:00:00Z",
        "out_suffix": args.out_suffix,
        "output_relpath": str(out_wav.relative_to(root)),
        "output_sha256": _sha(out_wav),
        "env_pin": {k: os.environ.get(k) for k in _PINS},
        "env_pin_sha256": _ENV_PIN_SHA256,
        "provenance": provenance,
        "notes": (
            "Per OPERATOR PIVOT 2026-09-05: bass+drums via sf2 replay against per-song pinned "
            "profiles; guitar/piano/other absent (no pinned profile emitted, honest render); "
            "vocals htdemucs hybrid overlay per campaign L59-60. Per-cell RMS-match to reference "
            "stems; sum with float accumulate + 0.99 peak limit. Operator ear = LANDS authority "
            "post-hoc per FD-6."
        ),
    }
    manifest_path = out_dir / ("ab_mix" + _suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print(f"RENDERED {out_wav} sha256={manifest['output_sha256']}")
    print(f"MANIFEST_WRITTEN {manifest_path}")

    if args.prove_replay:
        tmp = Path(tempfile.mkdtemp(prefix=f"ab_replay_{song}_"))
        try:
            tmp_wav = tmp / ("ab_mix" + _suffix + ".wav")
            _render_ab_mix(root, song, tmp_wav)
            run2_sha = _sha(tmp_wav)
        finally:
            pass
        proof = {
            "kind": "ab_v4_full_render_replay_proof",
            "song_sha16": song,
            "cycle": 71 if _is_v2 else 69,
            "run_id": "run-2026-09-05T190000Z" if _is_v2 else "run-2026-09-05T180000Z",
            "created": "2026-09-05T19:00:00Z" if _is_v2 else "2026-09-05T18:00:00Z",
            "out_suffix": args.out_suffix,
            "run1_sha256": manifest["output_sha256"],
            "run2_sha256": run2_sha,
            "run2_tempdir": str(tmp),
            "verdict": "REPLAY_PROOF_HOLDS" if manifest["output_sha256"] == run2_sha else "REPLAY_PROOF_FAILS",
            "env_pin_sha256": _ENV_PIN_SHA256,
            "scoping_note": ("per FD-16(c) + operator relaxation 2026-09-03: proof x2 once per "
                             "NEW code path (c71 audibility-gated htdemucs stem substitution + "
                             "max-truncation policy in deliver_ab_v4)."),
        }
        proof_path = out_dir / ("ab_mix" + _suffix + ".replay_proof.json")
        proof_path.write_text(json.dumps(proof, sort_keys=True, indent=2) + "\n")
        print(f"REPLAY_PROOF {proof['verdict']} run2_sha256={run2_sha} -> {proof_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
