#!/usr/bin/env python3
"""Music-Gen workspace smoke test.

Proves the pre-provisioned toolchain works unattended, end to end:
MIDI -> session -> synth render -> effects -> analysis, plus the
harvest/separation/transcription tooling. Each stage reports PASS,
PARTIAL, or FAIL and the script exits nonzero if any required stage
fails. Artifacts go to --workdir (default: a temp dir), never the repo.

A green run of this script is a launch precondition for the
autonomous run (see music-gen/README.md).
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import traceback

RESULTS = []  # (stage, status, detail)


def record(stage, status, detail=""):
    RESULTS.append((stage, status, detail))
    print(f"[{status:7s}] {stage}" + (f" — {detail}" if detail else ""), flush=True)


def run(cmd, timeout=300, env=None, **kw):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=e, **kw)


def stage(name, required=True):
    def deco(fn):
        def wrapper(ctx):
            try:
                detail = fn(ctx) or ""
                record(name, "PASS", detail)
            except SkipPartial as e:
                record(name, "PARTIAL", str(e))
            except Exception as e:
                record(name, "FAIL" if required else "PARTIAL", f"{type(e).__name__}: {e}")
                if os.environ.get("SMOKE_DEBUG"):
                    traceback.print_exc()
        wrapper.__name__ = fn.__name__
        return wrapper
    return deco


class SkipPartial(Exception):
    """Raise to mark a stage installed-but-degraded (e.g. weights not seeded)."""


# ---------------------------------------------------------------- stages

@stage("python imports (audio/ML stack)")
def s_imports(ctx):
    import numpy, soundfile, mido, pretty_midi, librosa, pedalboard  # noqa: F401
    import dawdreamer  # noqa: F401
    import yt_dlp  # noqa: F401
    return "numpy, soundfile, mido, pretty_midi, librosa, pedalboard, dawdreamer, yt_dlp"


@stage("test MIDI authored (pretty_midi)")
def s_midi(ctx):
    import pretty_midi
    pm = pretty_midi.PrettyMIDI(initial_tempo=100)
    piano = pretty_midi.Instrument(program=0, name="piano")
    bass = pretty_midi.Instrument(program=33, name="bass")
    melody = [60, 62, 64, 67, 69, 67, 64, 62, 60, 64, 67, 72, 71, 67, 64, 60]
    for i, note in enumerate(melody):
        t = i * 0.5
        piano.notes.append(pretty_midi.Note(velocity=90, pitch=note, start=t, end=t + 0.45))
        if i % 4 == 0:
            bass.notes.append(pretty_midi.Note(velocity=80, pitch=note - 24, start=t, end=t + 1.9))
    pm.instruments += [piano, bass]
    ctx["midi"] = os.path.join(ctx["dir"], "test.mid")
    pm.write(ctx["midi"])
    return f"{len(melody)} melody notes + bass, 8s"


@stage("MuseScore headless round trip (MIDI -> MusicXML -> MIDI)")
def s_musescore(ctx):
    env = {"QT_QPA_PLATFORM": "offscreen", "XDG_RUNTIME_DIR": ctx["dir"]}
    xml = os.path.join(ctx["dir"], "score.musicxml")
    mid2 = os.path.join(ctx["dir"], "roundtrip.mid")
    r = run(["mscore3", ctx["midi"], "-o", xml], env=env)
    if not os.path.exists(xml):
        raise RuntimeError(f"MIDI->MusicXML failed: {r.stderr[-300:]}")
    r = run(["mscore3", xml, "-o", mid2], env=env)
    if not os.path.exists(mid2):
        raise RuntimeError(f"MusicXML->MIDI failed: {r.stderr[-300:]}")
    import pretty_midi
    n = sum(len(i.notes) for i in pretty_midi.PrettyMIDI(mid2).instruments)
    if n == 0:
        raise RuntimeError("round-tripped MIDI has no notes")
    return f"score.musicxml written; round-trip MIDI has {n} notes"


@stage("fluidsynth render (MIDI -> WAV, GM soundfont)")
def s_fluidsynth(ctx):
    sf2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    wav = os.path.join(ctx["dir"], "fluid.wav")
    r = run(["fluidsynth", "-ni", "-F", wav, "-r", "44100", sf2, ctx["midi"]])
    import soundfile as sfio
    data, sr = sfio.read(wav)
    peak = float(abs(data).max())
    if peak < 1e-4:
        raise RuntimeError("rendered audio is silent")
    ctx["fluid_wav"] = wav
    return f"{len(data)/sr:.1f}s @ {sr}Hz, peak {peak:.2f}"


@stage("DawDreamer render (MIDI through Surge XT VST3)")
def s_dawdreamer(ctx):
    import dawdreamer as daw
    import soundfile as sfio
    eng = daw.RenderEngine(44100, 512)
    synth = eng.make_plugin_processor("synth", "/usr/lib/vst3/Surge XT.vst3")
    synth.load_midi(ctx["midi"], beats=False, all_events=True)
    eng.load_graph([(synth, [])])
    eng.render(9.0)
    audio = eng.get_audio().transpose()
    peak = float(abs(audio).max())
    if peak < 1e-4:
        raise RuntimeError("Surge XT render is silent")
    wav = os.path.join(ctx["dir"], "surge.wav")
    sfio.write(wav, audio, 44100)
    ctx["surge_wav"] = wav
    return f"9.0s rendered, peak {peak:.2f}"


@stage("Pedalboard effect chain (+ external VST3 load)")
def s_pedalboard(ctx):
    import soundfile as sfio
    from pedalboard import Pedalboard, Compressor, Reverb, Gain, Limiter
    src = ctx.get("surge_wav") or ctx["fluid_wav"]
    audio, sr = sfio.read(src)
    board = Pedalboard([Compressor(threshold_db=-18, ratio=3),
                        Reverb(room_size=0.4, wet_level=0.2),
                        Gain(gain_db=2), Limiter()])
    out = board(audio.T if audio.ndim > 1 else audio, sr)
    wav = os.path.join(ctx["dir"], "textured.wav")
    sfio.write(wav, out.T if out.ndim > 1 else out, sr)
    ctx["textured_wav"] = wav
    detail = "built-in chain ok"
    try:
        from pedalboard import load_plugin
        fx = load_plugin("/usr/lib/vst3/Surge XT Effects.vst3")
        detail += f"; external VST3 loaded ({fx.name})"
    except Exception as e:
        detail += f"; external VST3 load failed ({type(e).__name__})"
    return detail


@stage("texture panel prototype (librosa analysis)")
def s_librosa(ctx):
    import numpy as np
    import librosa
    a, sr = librosa.load(ctx["fluid_wav"], sr=22050, mono=True)
    b, _ = librosa.load(ctx["textured_wav"], sr=22050, mono=True)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    mel = lambda x: librosa.power_to_db(librosa.feature.melspectrogram(y=x, sr=22050))
    mel_dist = float(np.mean(np.abs(mel(a) - mel(b))))
    rms_err = float(np.mean(np.abs(librosa.feature.rms(y=a) - librosa.feature.rms(y=b))))
    tempo = librosa.beat.beat_track(y=a, sr=22050)[0]
    tempo = float(np.atleast_1d(tempo)[0])
    return f"mel-dist {mel_dist:.2f} dB, rms-err {rms_err:.4f}, tempo est {tempo:.0f} bpm"


@stage("Ardour headless session (create + verify on disk)")
def s_ardour(ctx):
    sdir = os.path.join(ctx["dir"], "ardour_sessions")
    env = {"XDG_RUNTIME_DIR": ctx["dir"], "HOME": os.environ.get("HOME", "/root")}
    r = run(["ardour8-new_empty_session", sdir, "smoke"], env=env, timeout=180)
    session_file = os.path.join(sdir, "smoke.ardour")
    if not os.path.exists(session_file):
        raise RuntimeError(f"no session file created: {(r.stderr or r.stdout)[-300:]}")
    size = os.path.getsize(session_file)
    lua = shutil.which("ardour8-lua")
    return f"smoke.ardour written ({size}B); ardour8-lua {'present' if lua else 'MISSING'}"


@stage("LV2 plugin palette visible to hosts")
def s_lv2(ctx):
    r = run(["lv2ls"])
    uris = r.stdout.splitlines()
    fams = {"calf": "calf", "lsp": "lsp-plug", "x42": "x42|gareus", "surge": "surge",
            "dragonfly": "dragonfly", "avldrums": "avldrums|x42.*avldrums"}
    import re
    present = [k for k, pat in fams.items() if any(re.search(pat, u, re.I) for u in uris)]
    missing = sorted(set(fams) - set(present))
    if len(present) < 4:
        raise RuntimeError(f"only {present} visible of {sorted(fams)}")
    d = f"{len(uris)} LV2 plugins; families present: {', '.join(sorted(present))}"
    return d + (f"; missing: {', '.join(missing)}" if missing else "")


@stage("sfizz (headless SFZ render of test MIDI)", required=False)
def s_sfizz(ctx):
    if not shutil.which("sfizz_render"):
        raise SkipPartial("sfizz_render not on PATH (build not installed)")
    import numpy as np
    import soundfile as sfio
    sr = 44100
    t = np.linspace(0, 1.0, sr, False)
    tone = (0.6 * np.sin(2 * np.pi * 261.63 * t) * np.exp(-3 * t)).astype("float32")
    sample = os.path.join(ctx["dir"], "c4.wav")
    sfio.write(sample, tone, sr)
    sfz = os.path.join(ctx["dir"], "test.sfz")
    with open(sfz, "w") as f:
        f.write("<region> sample=c4.wav pitch_keycenter=60 lokey=0 hikey=127\n")
    out = os.path.join(ctx["dir"], "sfizz_out.wav")
    r = run(["sfizz_render", "--sfz", sfz, "--midi", ctx["midi"], "--wav", out])
    if not os.path.exists(out):
        raise RuntimeError(r.stderr[-200:])
    data, _ = sfio.read(out)
    peak = float(abs(data).max())
    if peak < 1e-4:
        raise RuntimeError("sfizz render is silent")
    return f"{len(data)/sr:.1f}s rendered from synthetic SFZ, peak {peak:.2f}"


@stage("basic-pitch transcription (WAV -> MIDI)", required=False)
def s_basicpitch(ctx):
    from basic_pitch.inference import predict
    from basic_pitch import ICASSP_2022_MODEL_PATH
    _, midi_data, _ = predict(ctx["fluid_wav"], ICASSP_2022_MODEL_PATH)
    n = sum(len(i.notes) for i in midi_data.instruments)
    if n == 0:
        raise RuntimeError("no notes transcribed from rendered audio")
    return f"{n} notes transcribed from fluidsynth render"


@stage("demucs separation (2-stem on synthetic mix)", required=False)
def s_demucs(ctx):
    out = os.path.join(ctx["dir"], "demucs_out")
    src = ctx.get("surge_wav") or ctx["fluid_wav"]
    r = run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs",
             "-o", out, src], timeout=900)
    if r.returncode != 0:
        low = (r.stderr or "").lower()
        if any(k in low for k in ("download", "urlopen", "connection", "http", "certificate")):
            raise SkipPartial("engine runs but model weights not downloadable here — pre-seed "
                              "~/.cache/torch/hub/checkpoints at provisioning time")
        raise RuntimeError(r.stderr[-300:])
    import glob
    stems = glob.glob(os.path.join(out, "**", "*.wav"), recursive=True)
    if len(stems) < 2:
        raise RuntimeError(f"expected 2 stems, found {len(stems)}")
    return f"{len(stems)} stems written"


@stage("harvester present (yt-dlp, version check only)")
def s_ytdlp(ctx):
    import yt_dlp
    return f"yt-dlp {yt_dlp.version.__version__} importable (no network fetch attempted)"


@stage("ffmpeg transcode")
def s_ffmpeg(ctx):
    mp3 = os.path.join(ctx["dir"], "textured.mp3")
    r = run(["ffmpeg", "-y", "-loglevel", "error", "-i", ctx["textured_wav"], mp3])
    if not os.path.exists(mp3) or os.path.getsize(mp3) < 1000:
        raise RuntimeError(r.stderr[-200:])
    return f"wav -> mp3 ({os.path.getsize(mp3)//1024} KiB)"


STAGES = [s_imports, s_midi, s_musescore, s_fluidsynth, s_dawdreamer, s_pedalboard,
          s_librosa, s_ardour, s_lv2, s_sfizz, s_basicpitch, s_demucs, s_ytdlp, s_ffmpeg]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=None, help="artifact dir (default: temp dir)")
    args = ap.parse_args()
    workdir = args.workdir or tempfile.mkdtemp(prefix="musicgen_smoke_")
    os.makedirs(workdir, exist_ok=True)
    ctx = {"dir": workdir}
    print(f"smoke test artifacts -> {workdir}\n", flush=True)
    for fn in STAGES:
        fn(ctx)
    print("\n=== SUMMARY ===")
    for stage_name, status, detail in RESULTS:
        print(f"{status:7s} {stage_name}")
    fails = [s for s, st, _ in RESULTS if st == "FAIL"]
    partials = [s for s, st, _ in RESULTS if st == "PARTIAL"]
    print(f"\n{len(RESULTS)} stages: {len(RESULTS)-len(fails)-len(partials)} pass, "
          f"{len(partials)} partial, {len(fails)} fail")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
