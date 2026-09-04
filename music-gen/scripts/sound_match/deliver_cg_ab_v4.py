#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T23:45:00Z
# cycle: 9
# last_edit: 2026-09-04
# last_edit_cycle: 17
# run_id: run-2026-09-04T000000Z
# agent: worker
# milestone: M-V4-SHOWCASE-1/cg-ab-full-render
# ---
"""Deliver CG sound-matched A/B under v4.

Two modes:
  --smoke-test : consume pinned profiles, document missing/present cells,
                 write scaffold_smoke_test.json. rc=0 on complete, rc=2 on
                 missing (retained from c9 scaffold).
  --full-render (default when profiles complete): assemble the CG A/B mix
                 by combining per-cell sources per acceptance forks:
                   bass   -> bass_v2 sf2 replay (fluidsynth, mono -> stereo)
                   drums  -> htdemucs stem substitution (OPT3, c14)
                   guitar -> htdemucs stem substitution (OPT3, c15)
                   piano  -> NULL (audibility-grounded silent per-track)
                   other  -> NULL (audibility-grounded silent per-track)
                   vocals -> htdemucs hybrid overlay (per campaign L59-60)
                 Per-cell loudness: htdemucs stems used verbatim (already at
                 reference); bass render RMS-normalized to reference bass
                 stem RMS. Sum stereo. Peak-limit at 0.99.

Writes into <delivery-root>/<song>/:
  cg_ab_mix.wav               summed stereo 30 s @ 44.1 kHz
  cg_ab_mix.manifest.json     per-cell provenance SHAs + env pins
  cg_ab_mix.replay_proof.json byte-det x2 sha table (new code path)

Discipline:
  - 7-key env pin (env_pin_sha256 = 2ac444c3...922ca)
  - /usr/bin/python3 interpreter guard
  - no PRNG, no sidecar_nonfactor, no --verify-det pass-through
  - deterministic sum (float32 accumulate, then int16 quantize)
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
    raise RuntimeError(f"deliver_cg_ab_v4 requires /usr/bin/python3 (got {sys.executable})")

_ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

REQUIRED_PROFILES = ["bass", "drums", "piano", "guitar", "other"]
# Vocals sourced via hybrid overlay (campaign prompt L59-60).


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _read_stereo_int16(path: Path) -> tuple[list[int], list[int], int]:
    """Read 16-bit stereo WAV -> (left, right, sr). Also accepts mono."""
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


def _write_stereo_int16(path: Path, left: list[int], right: list[int], sr: int) -> None:
    n = min(len(left), len(right))
    interleaved = [0] * (2 * n)
    for i in range(n):
        # Clip to int16 range for safety (already clipped by mixer, this is defense).
        li = left[i]
        ri = right[i]
        if li > 32767: li = 32767
        elif li < -32768: li = -32768
        if ri > 32767: ri = 32767
        elif ri < -32768: ri = -32768
        interleaved[2 * i] = li
        interleaved[2 * i + 1] = ri
    raw = struct.pack("<" + "h" * (2 * n), *interleaved)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(raw)


def _rms_int16(samples: Iterable[int]) -> float:
    n = 0
    acc = 0.0
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
        # Downmix to mono average.
        mono = [(ints[2 * i] + ints[2 * i + 1]) // 2 for i in range(len(ints) // 2)]
        return mono, sr
    return ints, sr


def _render_bass_via_sf2(
    profile_path: Path, midi_path: Path, out_wav: Path,
) -> tuple[str, dict]:
    """Invoke sound_match.replay on the bass_v2 sf2 profile.

    Returns (render_sha256, profile_dict).
    """
    profile = json.loads(profile_path.read_text())
    # Import here to keep top-level lean and to preserve module isolation.
    from scripts.sound_match.replay import replay  # type: ignore
    sha = replay(profile, midi_path, out_wav)
    return sha, profile


def _load_and_upmix_bass(bass_mono_path: Path) -> tuple[list[int], list[int], int]:
    mono, sr = _read_mono_int16(bass_mono_path)
    # Trivial mono -> stereo: duplicate to both channels.
    return list(mono), list(mono), sr


def _sum_stereo_tracks(
    tracks: list[tuple[list[int], list[int]]], target_len: int,
) -> tuple[list[int], list[int]]:
    """Sum stereo tracks with float accumulate, clamp to int16 at output."""
    accL = [0.0] * target_len
    accR = [0.0] * target_len
    for L, R in tracks:
        n = min(len(L), target_len)
        for i in range(n):
            accL[i] += L[i]
            accR[i] += R[i]
        m = min(len(R), target_len)
        # (L and R same length per read above; guard anyway)
        for i in range(m):
            pass
    outL = [0] * target_len
    outR = [0] * target_len
    peak = 1.0
    for i in range(target_len):
        a = abs(accL[i])
        b = abs(accR[i])
        if a > peak: peak = a
        if b > peak: peak = b
    # If peak exceeds ~99% of int16 range, apply headroom gain to keep 0.99 peak.
    ceiling = 0.99 * 32767.0
    gain = 1.0 if peak <= ceiling else (ceiling / peak)
    for i in range(target_len):
        li = int(round(accL[i] * gain))
        ri = int(round(accR[i] * gain))
        if li > 32767: li = 32767
        elif li < -32768: li = -32768
        if ri > 32767: ri = 32767
        elif ri < -32768: ri = -32768
        outL[i] = li
        outR[i] = ri
    return outL, outR


def _render_cg_ab_mix(
    profiles_root: Path,
    delivery_dir: Path,
    stems_dir: Path,
    bass_midi: Path,
    bass_v2_profile: Path,
    out_wav: Path,
) -> dict:
    """Assemble the CG A/B mix. Returns per-cell provenance dict."""
    provenance: dict = {}

    # 1) Bass via sf2 replay.
    bass_mono_tmp = out_wav.parent / ".bass_v2_render_mono.wav"
    bass_sha, bass_profile = _render_bass_via_sf2(bass_v2_profile, bass_midi, bass_mono_tmp)
    provenance["bass"] = {
        "render_family": "sf2",
        "profile_relpath": str(bass_v2_profile.relative_to(bass_v2_profile.parents[3])),
        "profile_sha256": _sha(bass_v2_profile),
        "midi_relpath": str(bass_midi.relative_to(bass_midi.parents[4])),
        "midi_sha256": _sha(bass_midi),
        "render_sha256": bass_sha,
        "render_sha256_canonical_replay_expected": bass_profile.get("render_sha256_canonical_replay"),
    }
    bass_L, bass_R, sr_bass = _load_and_upmix_bass(bass_mono_tmp)

    # RMS-normalize bass to reference stem (drums-adjacent — use reference bass stem).
    ref_bass = stems_dir / "bass.wav"
    refL, refR, sr_ref = _read_stereo_int16(ref_bass)
    ref_rms = 0.5 * (_rms_int16(refL) + _rms_int16(refR))
    ren_rms = 0.5 * (_rms_int16(bass_L) + _rms_int16(bass_R))
    if ren_rms > 1e-9:
        gain = ref_rms / ren_rms
        # Cap gain to reasonable range to avoid runaway on empty renders.
        if gain > 4.0: gain = 4.0
        if gain < 0.05: gain = 0.05
    else:
        gain = 1.0
    bass_L = _scale_int16(bass_L, gain)
    bass_R = _scale_int16(bass_R, gain)
    provenance["bass"]["rms_normalize_gain"] = round(gain, 6)
    provenance["bass"]["ref_stem_relpath"] = str(ref_bass.relative_to(ref_bass.parents[4]))
    provenance["bass"]["ref_stem_sha256"] = _sha(ref_bass)
    # Clean up temp mono file (keep sha in provenance).
    try:
        bass_mono_tmp.unlink()
        (bass_mono_tmp.with_suffix(".prog_forced.mid")).unlink()
    except FileNotFoundError:
        pass

    # 2) Drums OPT3 htdemucs stem substitution.
    drums_stem = stems_dir / "drums.wav"
    drums_L, drums_R, sr_d = _read_stereo_int16(drums_stem)
    provenance["drums"] = {
        "render_family": "htdemucs_stem_substitution",
        "acceptance": "OPT3",
        "source_relpath": str(drums_stem.relative_to(drums_stem.parents[4])),
        "source_sha256": _sha(drums_stem),
    }

    # 3) Guitar OPT3 htdemucs stem substitution.
    guitar_stem = stems_dir / "guitar.wav"
    guitar_L, guitar_R, sr_g = _read_stereo_int16(guitar_stem)
    provenance["guitar"] = {
        "render_family": "htdemucs_stem_substitution",
        "acceptance": "OPT3",
        "source_relpath": str(guitar_stem.relative_to(guitar_stem.parents[4])),
        "source_sha256": _sha(guitar_stem),
    }

    # 4) Vocals hybrid overlay.
    vocals_stem = stems_dir / "vocals.wav"
    vocals_L, vocals_R, sr_v = _read_stereo_int16(vocals_stem)
    provenance["vocals"] = {
        "render_family": "htdemucs_hybrid_overlay",
        "source_relpath": str(vocals_stem.relative_to(vocals_stem.parents[4])),
        "source_sha256": _sha(vocals_stem),
    }

    # 5) Piano NULL (silent per-track).
    provenance["piano"] = {
        "render_family": "null_no_synthesis",
        "verdict": "PIANO_NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE",
        "showcase_dispatch": "silent per-track",
    }

    # 6) Other NULL (silent per-track).
    provenance["other"] = {
        "render_family": "null_no_synthesis",
        "verdict": "OTHER_NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE",
        "showcase_dispatch": "silent per-track",
    }

    # Sanity: all SRs must match.
    srs = {sr_bass, sr_ref, sr_d, sr_g, sr_v}
    if len(srs) != 1:
        raise RuntimeError(f"sample-rate mismatch across cells: {srs}")
    sr = sr_bass

    target_len = min(
        len(bass_L), len(drums_L), len(guitar_L), len(vocals_L),
    )
    outL, outR = _sum_stereo_tracks(
        [(bass_L, bass_R), (drums_L, drums_R), (guitar_L, guitar_R), (vocals_L, vocals_R)],
        target_len,
    )

    _write_stereo_int16(out_wav, outL, outR, sr)
    provenance["_mix"] = {
        "sample_rate": sr,
        "n_frames": target_len,
        "duration_s": round(target_len / sr, 6),
        "n_channels": 2,
        "sum_method": "float_accumulate_peaklimit_099",
        "mix_wav_sha256": _sha(out_wav),
    }
    return provenance


def _cmd_smoke(delivery_dir: Path, out_dir: Path, root: Path) -> tuple[dict, list[str]]:
    """Scan pinned profiles/null findings; return (smoke_dict, missing_list)."""
    present: dict[str, dict] = {}
    missing: list[str] = []

    # Bass
    pinned = delivery_dir / "cg_bass_pinned_profile.json"
    if pinned.exists():
        m = json.loads(pinned.read_text())
        pp = m.get("pinned_profile") or {}
        present["bass"] = {
            "pinned_manifest": str(pinned),
            "manifest_sha256": _sha(pinned),
            "profile_relpath": pp.get("relative_path"),
            "profile_sha256": pp.get("profile_sha256"),
            "profile_id": pp.get("profile_id"),
            "render_family": pp.get("render_family"),
        }
    else:
        missing.append("bass (no cg_bass_pinned_profile.json)")

    # Drums OPT3
    drums_pinned = delivery_dir / "cg_drums_pinned_profile.json"
    if drums_pinned.exists():
        dm = json.loads(drums_pinned.read_text())
        if dm.get("acceptance_option") == "OPT3":
            present["drums"] = {
                "pinned_manifest": str(drums_pinned),
                "manifest_sha256": _sha(drums_pinned),
                "render_family": "htdemucs_stem_substitution",
                "source_stem_relpath": dm.get("drums_source_for_showcase"),
                "source_stem_sha256": dm.get("drums_source_sha256"),
                "showcase_dispatch": "read source_stem_relpath verbatim, no synthesis",
            }
        else:
            pp = dm.get("pinned_profile") or {}
            present["drums"] = {
                "pinned_manifest": str(drums_pinned),
                "manifest_sha256": _sha(drums_pinned),
                "profile_relpath": pp.get("relative_path"),
                "profile_sha256": pp.get("profile_sha256"),
                "profile_id": pp.get("profile_id"),
                "render_family": pp.get("render_family"),
            }
    else:
        missing.append("drums (no cg_drums_pinned_profile.json)")

    # Guitar OPT3
    guitar_pinned = delivery_dir / "cg_guitar_pinned_profile.json"
    guitar_opt3_handled = False
    if guitar_pinned.exists():
        gm = json.loads(guitar_pinned.read_text())
        if gm.get("acceptance_option") == "OPT3":
            present["guitar"] = {
                "pinned_manifest": str(guitar_pinned),
                "manifest_sha256": _sha(guitar_pinned),
                "render_family": "htdemucs_stem_substitution",
                "source_stem_relpath": gm.get("guitar_source_for_showcase"),
                "source_stem_sha256": gm.get("guitar_source_sha256"),
                "acceptance_option": "OPT3",
            }
            guitar_opt3_handled = True

    profiles_root = root / "data/v4/profiles" / delivery_dir.name
    for inst in ["piano", "guitar", "other"]:
        if inst == "guitar" and guitar_opt3_handled:
            continue
        p = profiles_root / f"{inst}.json"
        null_finding = profiles_root / f"{inst}_null_finding.json"
        if p.exists():
            present[inst] = {
                "profile_relpath": str(p.relative_to(root)),
                "profile_sha256": _sha(p),
                "render_family": "unknown_pending_manifest",
            }
        elif null_finding.exists():
            nf = json.loads(null_finding.read_text())
            present[inst] = {
                "null_finding_relpath": str(null_finding.relative_to(root)),
                "null_finding_sha256": _sha(null_finding),
                "verdict": nf.get("verdict"),
                "render_family": "null_no_synthesis",
                "showcase_dispatch": "empty MIDI track -> silent per-track (v3 spine default)",
            }
        else:
            missing.append(f"{inst} ({p.relative_to(root)} not present, no null_finding sibling)")

    smoke = {
        "kind": "cg_ab_v4_smoke_test",
        "song_sha16": delivery_dir.name,
        "cycle": 17,
        "run_id": "run-2026-09-04T000000Z",
        "created": "2026-09-04T00:00:00Z",
        "required_instrument_profiles": REQUIRED_PROFILES,
        "present": present,
        "missing": missing,
        "vocals_dispatch": "htdemucs hybrid overlay (per campaign prompt L59-60)",
        "mix_match_dispatch": "per-cell RMS-match; sum with float accumulate + 0.99 peak limit",
        "output_target": str((out_dir / "cg_ab_mix.wav").relative_to(root)),
        "renderable_now": len(missing) == 0,
        "env_pin": {k: os.environ.get(k) for k in _PINS},
        "env_pin_sha256": _ENV_PIN_SHA256,
    }
    return smoke, missing


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="CG A/B delivery driver (v4 full render, c17+).")
    ap.add_argument("--song", default="31a164f845f8e27e")
    ap.add_argument("--delivery-root", default="data/v4/deliveries")
    ap.add_argument("--out", default=None,
                    help="Directory for A/B output; default <delivery-root>/<song>/")
    ap.add_argument("--smoke-test", action="store_true",
                    help="Do not render; write scaffold_smoke_test.json only.")
    ap.add_argument("--full-render", action="store_true",
                    help="Perform the full CG A/B render (default when profiles complete).")
    ap.add_argument("--prove-replay", action="store_true",
                    help="After render, run a second render into a fresh tempfile.mkdtemp "
                         "and compare SHAs -> cg_ab_mix.replay_proof.json.")
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parents[2]
    # Ensure /root is 'root' of workspace (music-gen dir).
    delivery_dir = root / args.delivery_root / args.song
    out_dir = Path(args.out) if args.out else delivery_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Verify env pins.
    for k, v in _PINS.items():
        if os.environ.get(k) != v:
            raise RuntimeError(f"env pin drift {k}={os.environ.get(k)!r} expected {v!r}")

    smoke, missing = _cmd_smoke(delivery_dir, out_dir, root)

    if args.smoke_test or missing:
        out = out_dir / "scaffold_smoke_test.json"
        out.write_text(json.dumps(smoke, sort_keys=True, indent=2) + "\n")
        print(f"SMOKE_TEST_WRITTEN {out} -- missing={len(missing)}")
        return 0 if not missing else 2

    if missing:
        raise RuntimeError(f"cannot full-render, missing cells: {missing}")

    # Full render.
    stems_dir = root / "data/v3/deliveries" / args.song / "cert_run1" / "stems_6s"
    bass_midi = root / "data/v4/profiles" / args.song / "bass_sweep_stage1" / "inputs" / "bass.mid"
    bass_v2_profile = root / "data/v4/profiles" / args.song / "bass_v2.json"

    out_wav = out_dir / "cg_ab_mix.wav"
    provenance = _render_cg_ab_mix(
        profiles_root=root / "data/v4/profiles" / args.song,
        delivery_dir=delivery_dir,
        stems_dir=stems_dir,
        bass_midi=bass_midi,
        bass_v2_profile=bass_v2_profile,
        out_wav=out_wav,
    )

    manifest = {
        "kind": "cg_ab_v4_full_render_manifest",
        "song_sha16": args.song,
        "cycle": 17,
        "run_id": "run-2026-09-04T000000Z",
        "created": "2026-09-04T00:00:00Z",
        "output_relpath": str(out_wav.relative_to(root)),
        "output_sha256": _sha(out_wav),
        "env_pin": {k: os.environ.get(k) for k in _PINS},
        "env_pin_sha256": _ENV_PIN_SHA256,
        "provenance": provenance,
        "smoke_test_snapshot": smoke,
        "notes": (
            "Track 2 embedding-metric-semantics escalation (M-V4-METRIC-SEMANTICS-c16) "
            "is orthogonal to this delivery. OPT3 htdemucs stems are operator-heard "
            "reference bytes; bass_v2 acceptance is composite-relative WINNER per operator "
            "directive 2026-09-03 part (1) and not threshold-based. Operator ear remains "
            "LANDS authority post-hoc per FD-6."
        ),
    }
    manifest_path = out_dir / "cg_ab_mix.manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print(f"RENDERED {out_wav} sha256={manifest['output_sha256']}")
    print(f"MANIFEST_WRITTEN {manifest_path}")

    if args.prove_replay:
        # New code path -> run once more into a fresh tempfile.mkdtemp() and compare.
        tmp = Path(tempfile.mkdtemp(prefix="cg_ab_replay_"))
        try:
            tmp_wav = tmp / "cg_ab_mix.wav"
            _render_cg_ab_mix(
                profiles_root=root / "data/v4/profiles" / args.song,
                delivery_dir=delivery_dir,
                stems_dir=stems_dir,
                bass_midi=bass_midi,
                bass_v2_profile=bass_v2_profile,
                out_wav=tmp_wav,
            )
            run2_sha = _sha(tmp_wav)
        finally:
            # Leave temp dir contents in place for external inspection until process exits;
            # ideally clean, but the shas + provenance are already captured.
            pass
        proof = {
            "kind": "cg_ab_v4_full_render_replay_proof",
            "song_sha16": args.song,
            "cycle": 17,
            "run_id": "run-2026-09-04T000000Z",
            "created": "2026-09-04T00:00:00Z",
            "run1_sha256": manifest["output_sha256"],
            "run2_sha256": run2_sha,
            "run2_tempdir": str(tmp),
            "verdict": "REPLAY_PROOF_HOLDS" if manifest["output_sha256"] == run2_sha else "REPLAY_PROOF_FAILS",
            "env_pin_sha256": _ENV_PIN_SHA256,
            "scoping_note": "per FD-16(c) + operator relaxation 2026-09-03: proof x2 once per NEW code path (cg_ab_v4 full render).",
        }
        proof_path = out_dir / "cg_ab_mix.replay_proof.json"
        proof_path.write_text(json.dumps(proof, sort_keys=True, indent=2) + "\n")
        print(f"REPLAY_PROOF {proof['verdict']} run2_sha256={run2_sha} -> {proof_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
