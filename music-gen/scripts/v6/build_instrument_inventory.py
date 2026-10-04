#!/usr/bin/python3
"""Phase 4 (instrument realism) — build workspace/instruments/INVENTORY.json.

created: 2026-10-04
milestone: M-V6-INSTRUMENTS-1

Scans the libraries downloaded under workspace/instruments/<slug>/ (plus the sf2 banks that
already ship on this box) and writes INVENTORY.json: one record per library (slug, source URL,
license id+URL, size_mb, format, roles) with instrument entries [{name, role, path, bank,
program, notes}]. SFZ entries get their key range / velocity-layer count by scanning the .sfz
text; SF2 entries are only emitted when the (bank, program) preset actually exists in the file.

Entries for the DawDreamer backend (Surge XT / Dexed) are appended by render_vst_test.py.
Run render_patch_test.py --all --prune afterwards to smoke-render and reject silent entries.
"""
from __future__ import annotations

import json
import os
import re
import struct
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent.parent
INSTR_ROOT = WS / "workspace" / "instruments"
INVENTORY = INSTR_ROOT / "INVENTORY.json"

LIC = {
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC-BY-SA-3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
    "CC-BY-SA-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "GPL-3.0-or-later WITH FreePats-sample-exception": "https://freepats.zenvoid.org/licenses.html#GPL_exception",
    "MIT": "https://opensource.org/licenses/MIT",
    "GeneralUser-GS-License-2.0": "https://www.schristiancollins.com/generaluser.php",
    "GPL-3.0-only": "https://www.gnu.org/licenses/gpl-3.0.html",
}

FP = "https://freepats.zenvoid.org"
GH = "https://github.com/freepats"

# ----------------------------------------------------------------------------- SFZ libraries
# slug -> (source_url, license_id, license_file, [(sfz_relpath, name, role, notes, keys)])
SFZ_LIBS = {
    "salamander_grand_piano": (f"{FP}/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SFZ+FLAC-V3+20200602.tar.gz",
        "CC-BY-3.0", "readme.txt", [
        ("SalamanderGrandPiano-V3+20200602.sfz", "Salamander Grand Piano V3", "piano",
         "Yamaha C5 grand, 16 velocity layers sampled in minor thirds, hammer + string-resonance releases, pedal noises"),
        ("SalamanderGrandPianoRetuned-V3+20200602.sfz", "Salamander Grand Piano V3 (retuned)", "piano",
         "same samples, retuned to equal temperament by Markus Fiedler")]),
    "upright_piano_kw": (f"{FP}/Piano/UprightPianoKW/UprightPianoKW-SFZ+FLAC-20220221.7z", "CC0-1.0", "readme.txt", [
        ("UprightPianoKW-20220221.sfz", "Upright Piano KW", "piano", "Kawai upright, stereo, chromatic")]),
    "old_piano_fb": (f"{GH}/old-piano-FB/releases/download/2020-04-01/PianoFB-small-SFZ+FLAC-20200401.7z", "CC0-1.0", "README.txt", [
        ("PianoFB small 20200401.sfz", "Old Piano FB (honky-tonk)", "piano", "Francis Bacon player piano, honky-tonk character; 'small' edition")]),
    "fm_piano1": (f"{GH}/fm-piano1/releases/download/2019-09-16/FM-Piano1-SFZ+FLAC-20190916.7z", "CC0-1.0", "README.txt", [
        ("FM-Piano1 20190916.sfz", "FM Piano 1 (DX7-style)", "electric_piano", "DX7 e-piano imitation, FM synthesis samples, 2 velocity layers")]),
    "fm_piano2": (f"{GH}/fm-piano2/releases/download/2016-11-12/FM-Piano2-SFZ+FLAC-20161112.7z", "CC0-1.0", "README.txt", [
        ("FM-Piano2 20161112.sfz", "FM Piano 2 (DX7-style)", "electric_piano", "DX7 e-piano imitation, darker variant")]),
    "finger_bass_yr": (f"{GH}/electric-bass-YR/releases/download/2019-09-30/FingerBassYR-SFZ+FLAC-20190930.7z", "CC0-1.0", "README.txt", [
        ("FingerBassYR 20190930.sfz", "Finger Bass YR", "electric_bass", "Yamaha RBX, fingered, D1-A2 sampled range (sfizz extends by pitch-shift)")]),
    "picked_bass_yr": (f"{GH}/electric-bass-YR/releases/download/2019-09-30/PickedBassYR-SFZ+FLAC-20190930.7z", "CC0-1.0", "README.txt", [
        ("PickedBassYR 20190930.sfz", "Picked Bass YR", "electric_bass", "Yamaha RBX, picked")]),
    "lately_bass": (f"{GH}/lately-bass/releases/download/2024-04-09/LatelyBass-SFZ+FLAC-20240409.7z", "CC0-1.0", "README.txt", [
        ("LatelyBass 20240409.sfz", "Lately Bass", "synth_bass", "TX81Z-style FM synth bass")]),
    "synth_bass_1": (f"{GH}/synth-bass-1/releases/download/2019-07-23/SynthBass1-SFZ+FLAC-20190723.7z", "CC0-1.0", "README.txt", [
        ("SynthBass1 20190723.sfz", "Synth Bass 1", "synth_bass", "GM-style synth bass 1")]),
    "synth_bass_2": (f"{GH}/synth-bass-2/releases/download/2021-04-05/SynthBass2-SFZ+FLAC-20210405.7z", "CC0-1.0", "README.txt", [
        ("SynthBass2 20210405.sfz", "Synth Bass 2", "synth_bass", "GM-style synth bass 2")]),
    "synth_bass_lead": (f"{GH}/synth-bass-lead/releases/download/2020-05-22/SynthBassLead-SFZ+FLAC-20200522.7z", "CC0-1.0", "README.txt", [
        ("SynthBassLead 20200522.sfz", "Synth Bass+Lead", "lead", "GM 'Bass+Lead' style")]),
    "eguitar_fsbs_clean": (f"{GH}/electric-guitar-FSBS-clean/releases/download/2026-08-07/EGuitarFSBS-clean-SFZ+FLAC-20260807.7z", "CC0-1.0", "LICENSE.txt", [
        ("EGuitarFSBS-clean bridge 20260807.sfz", "EGuitar FSBS clean (bridge)", "electric_guitar", "Fender Stratocaster, bridge pickup, clean amp sim, 2 velocity layers, 4x round robin")]),
    "eguitar_fsbs_direct": (f"{GH}/electric-guitar-FSBS-direct/releases/download/2022-09-11/EGuitarFSBS-direct-SFZ+FLAC-20220911.7z", "CC0-1.0", "LICENSE.txt", [
        ("EGuitarFSBS-direct bridge 20220911.sfz", "EGuitar FSBS direct (DI)", "electric_guitar", "Fender Stratocaster DI (no amp) — good for funk/muted-style processing via pedalboard")]),
    "eguitar_fsbs_jazz": (f"{GH}/electric-guitar-FSBS-jazz/releases/download/2026-08-07/EGuitarFSBS-jazz-SFZ+FLAC-20260807.7z", "CC0-1.0", "LICENSE.txt", [
        ("EGuitarFSBS-jazz bridge 20260807.sfz", "EGuitar FSBS jazz tone", "electric_guitar", "Fender Stratocaster, mellow jazz amp tone")]),
    "spanish_classical_guitar": (f"{FP}/Guitar/SpanishClassicalGuitar/SpanishClassicalGuitar-SFZ+FLAC-20190618.7z", "CC0-1.0", "readme.txt", [
        ("SpanishClassicalGuitar-20190618.sfz", "Spanish Classical Guitar (nylon)", "acoustic_guitar", "nylon string, chromatic")]),
    "fss_steel_string_guitar": (f"{FP}/Guitar/FSS-SteelStringGuitar/FSS-SteelStringGuitar-SFZ-20200521.tar.xz",
        "GPL-3.0-or-later WITH FreePats-sample-exception", "readme.txt", [
        ("FSS-SteelStringGuitar-20200521.sfz", "FSS Steel String Guitar", "acoustic_guitar", "steel string acoustic, 5 velocity layers")]),
    "drawbar_organ_emulation": (f"{FP}/Organ/DrawbarOrganEmulation/DrawbarOrganEmulation-SFZ-20190712.tar.xz", "CC0-1.0", "readme.txt", [
        ("DrawbarOrganEmulation-20190712.sfz", "Drawbar Organ Emulation", "organ", "Hammond-style drawbar organ (synthesized emulation)")]),
    "percussive_organ_emulation": (f"{FP}/Organ/PercussiveOrganEmulation/PercussiveOrganEmulation-SFZ-20190715.tar.xz", "CC0-1.0", "readme.txt", [
        ("PercussiveOrganEmulation-20190715.sfz", "Percussive Organ Emulation", "organ", "percussive Hammond-style")]),
    "rock_organ_emulation": (f"{FP}/Organ/RockOrganEmulation/RockOrganEmulation-SFZ-20190715.tar.xz", "CC0-1.0", "readme.txt", [
        ("RockOrganEmulation-20190715.sfz", "Rock Organ Emulation", "organ", "rock organ, overdriven Hammond-style")]),
    "muldjord_kit": (f"{GH}/muldjordkit/releases/download/2020-10-18/MuldjordKit-SFZ+FLAC-20201018.7z", "CC-BY-4.0", "LICENSE.txt", [
        ("MuldjordKit 20201018.sfz", "Muldjord Kit (rock, stereo)", "drums", "DrumGizmo MuldjordKit stereo mixdown, GM mapping, many velocity layers + round robin")]),
    "salamander_drumkit": ("https://archive.org/download/SalamanderDrumkit/salamanderDrumkit.tar.bz2", "CC-BY-SA-3.0", "REAMDE", [
        ("ALL.sfz", "Salamander Drumkit (OH mics)", "drums",
         "Alexander Holm birch kit; keys 35/36 kick, 37-41 snares, 42/44/46 hats, 43/45 toms, 48-53 rides, 47/54-64 crashes/china; 2-3 velocity layers x many round robins")]),
    "new_age_pad": (f"{GH}/new-age/releases/download/2019-07-30/NewAge-SFZ+FLAC-20190730.7z", "CC0-1.0", "README.txt", [
        ("NewAge 20190730.sfz", "New Age Pad", "pad", "GM 'Pad 1 (new age)' style")]),
    "sweep_pad": (f"{GH}/sweep-pad/releases/download/2019-08-13/SweepPad-SFZ+FLAC-20190813.7z", "CC0-1.0", "README.txt", [
        ("SweepPad 20190813.sfz", "Sweep Pad", "pad", "GM 'Pad 8 (sweep)' style")]),
    "synth_pad_bowed": (f"{GH}/synth-pad-bowed/releases/download/2019-07-19/SynthPadBowed-SFZ+FLAC-20190719.7z", "CC0-1.0", "README.txt", [
        ("SynthPadBowed 20190719.sfz", "Synth Pad Bowed", "pad", "GM 'Pad 5 (bowed)' style")]),
    "synth_pad_choir": (f"{GH}/synth-pad-choir/releases/download/2020-05-16/SynthPadChoir-SFZ+FLAC-20200516.7z", "CC0-1.0", "README.txt", [
        ("SynthPadChoir 20200516.sfz", "Synth Pad Choir", "pad", "GM 'Pad 4 (choir)' style")]),
    "synth_strings_1": (f"{GH}/synth-strings-1/releases/download/2020-05-28/SynthStrings1-SFZ+FLAC-20200528.7z", "CC0-1.0", "README.txt", [
        ("SynthStrings1 20200528.sfz", "Synth Strings 1", "strings_pad", "GM 'Synth Strings 1' style")]),
    "synth_strings_2": (f"{GH}/synth-strings-2/releases/download/2020-05-28/SynthStrings2-SFZ+FLAC-20200528.7z", "CC0-1.0", "README.txt", [
        ("SynthStrings2 20200528.sfz", "Synth Strings 2", "strings_pad", "GM 'Synth Strings 2' style")]),
    "synth_square": (f"{GH}/synth-square/releases/download/2020-05-12/SynthSquare-SFZ+FLAC-20200512.7z", "CC0-1.0", "README.txt", [
        ("SynthSquare 20200512.sfz", "Synth Square Lead", "lead", "GM 'Lead 1 (square)' style")]),
    "synth_fifths": (f"{GH}/synth-fifths/releases/download/2020-05-19/SynthFifths-SFZ+FLAC-20200519.7z", "CC0-1.0", "README.txt", [
        ("SynthFifths 20200519.sfz", "Synth Fifths Lead", "lead", "GM 'Lead 7 (fifths)' style")]),
    "synth_calliope": (f"{GH}/synth-calliope/releases/download/2020-05-12/SynthCalliope-SFZ+FLAC-20200512.7z", "CC0-1.0", "README.txt", [
        ("SynthCalliope 20200512.sfz", "Synth Calliope Lead", "lead", "GM 'Lead 3 (calliope)' style")]),
    "synth_brass_1": (f"{GH}/synth-brass-1/releases/download/2021-04-26/SynthBrass1-SFZ+FLAC-20210426.7z", "CC0-1.0", "README.txt", [
        ("SynthBrass1 20210426.sfz", "Synth Brass 1", "brass", "GM 'Synth Brass 1' style")]),
    "synth_brass_2": (f"{GH}/synth-brass-2/releases/download/2024-06-10/SynthBrass2-SFZ+FLAC-20240610.7z", "CC0-1.0", "README.txt", [
        ("SynthBrass2 20240610.sfz", "Synth Brass 2", "brass", "GM 'Synth Brass 2' style")]),
    "world_percussion": (f"{GH}/world-percussion/releases/download/2020-09-05/WorldPercussion-SFZ+FLAC-20200905.7z", "CC0-1.0", "LICENSE.txt", [
        ("WorldPercussion 20200905.sfz", "World Percussion", "percussion",
         "cajon, bongos, congas, shaker, tambourine, castanets, maracas, claves, darbuka, hand clap; see README for note map")]),
}

# ----------------------------------------------------------------------------- SF2 banks
GM_MELODIC = [  # (program, role, notes)
    (0, "piano", "GM 0 Acoustic Grand"), (1, "piano", "GM 1 Bright Acoustic"),
    (4, "electric_piano", "GM 4 Electric Piano 1 (Rhodes-type)"), (5, "electric_piano", "GM 5 Electric Piano 2 (FM/DX-type)"),
    (16, "organ", "GM 16 Drawbar Organ"), (17, "organ", "GM 17 Percussive Organ"), (18, "organ", "GM 18 Rock Organ"),
    (24, "acoustic_guitar", "GM 24 Nylon Guitar"), (25, "acoustic_guitar", "GM 25 Steel Guitar"),
    (26, "electric_guitar", "GM 26 Jazz Guitar"), (27, "electric_guitar", "GM 27 Clean Electric Guitar"),
    (28, "electric_guitar", "GM 28 Muted Electric Guitar (palm-mute/funk)"),
    (32, "acoustic_bass", "GM 32 Acoustic (upright) Bass"), (33, "electric_bass", "GM 33 Fingered Bass"),
    (34, "electric_bass", "GM 34 Picked Bass"), (38, "synth_bass", "GM 38 Synth Bass 1"), (39, "synth_bass", "GM 39 Synth Bass 2"),
    (48, "strings_pad", "GM 48 String Ensemble"), (49, "strings_pad", "GM 49 Slow Strings"),
    (61, "brass", "GM 61 Brass Section"), (62, "brass", "GM 62 Synth Brass 1"),
    (80, "lead", "GM 80 Square Lead"), (81, "lead", "GM 81 Saw Lead"),
    (88, "pad", "GM 88 New Age Pad"), (89, "pad", "GM 89 Warm Pad"), (91, "pad", "GM 91 Choir Pad"),
]
GM_DRUMS = {0: "Standard kit", 8: "Room kit (tighter)", 16: "Power kit", 32: "Jazz kit", 40: "Brush kit"}

SF2_LIBS = {
    # slug: (sf2 path (relative to INSTR_ROOT or absolute), source_url, license_id, license_file, notes, drums, melodic)
    "freepats_gm": ("freepats_gm/FreePatsGM-20221026.sf2", f"{FP}/SoundSets/FreePats-GeneralMIDI/FreePatsGM-SF2-20221026.7z",
                    "GPL-3.0-or-later WITH FreePats-sample-exception", "freepats_gm/readme.txt",
                    "FreePats General MIDI set (incomplete GM coverage, all instruments original/free-licensed)", True, True),
    "musescore_general": ("musescore_general/MuseScore_General.sf2",
                          "https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf2",
                          "MIT", "musescore_general/MuseScore_General_License.md",
                          "MuseScore_General 0.2 (FluidR3Mono-derived with replacement instruments; 8 drum kits)", True, True),
    "generaluser_gs": ("generaluser_gs/GeneralUser-GS.sf2",
                       "https://archive.org/download/general-user-gs-v-2.0.2-doc-r-4/GeneralUser_GS_v2.0.2--doc_r4.zip",
                       "GeneralUser-GS-License-2.0", "generaluser_gs/documentation/LICENSE.txt",
                       "GeneralUser GS 2.0.2 by S. Christian Collins (official release zip, archive.org mirror of schristiancollins.com)", True, True),
    "fluidr3_gm": ("/usr/share/sounds/sf2/FluidR3_GM.sf2", "(preinstalled: Debian fluid-soundfont-gm)", "MIT",
                   "/usr/share/doc/fluid-soundfont-gm/copyright", "FluidR3 GM — current pipeline baseline, kept for comparison", True, True),
}
AVL_KITS = [  # (sf2 abs path, name, notes)
    ("/usr/share/sounds/sf2/Black_Pearl_4_LV2.sf2", "AVL Black Pearl 4pc", "tight 4-piece kit (funk/soul/pop)"),
    ("/usr/share/sounds/sf2/Red_Zeppelin_4_LV2.sf2", "AVL Red Zeppelin 4pc", "big rock kit"),
    ("/usr/share/sounds/sf2/Blonde_Bop_LV2.sf2", "AVL Blonde Bop", "jazz bop kit, sticks"),
    ("/usr/share/sounds/sf2/Blonde_Bop_HR_LV2.sf2", "AVL Blonde Bop HR", "jazz bop kit, hot-rod/brushed-style sticks"),
    ("/usr/share/sounds/sf2/Buskmans_Holiday_LV2.sf2", "AVL Buskmans Holiday", "small busking kit (suitcase-style)"),
]

# ----------------------------------------------------------------------------- helpers
NOTE = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def _n2m(s: str):
    s = s.strip()
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    m = re.fullmatch(r"([a-gA-G])([#b]?)(-?\d+)", s)
    if not m:
        return None
    return NOTE[m.group(1).lower()] + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0) + (int(m.group(3)) + 1) * 12


def _sfz_text(path: Path, seen=None) -> str:
    seen = seen or set()
    if path in seen or not path.exists():
        return ""
    seen.add(path)
    txt = path.read_text(encoding="latin1")
    for inc in re.findall(r'#include\s+"([^"]+)"', txt):
        txt += "\n" + _sfz_text(path.parent / inc.replace("\\", "/"), seen)
    return re.sub(r"//.*", "", txt)


def sfz_summary(path: Path) -> dict:
    txt = _sfz_text(path)
    keys = [_n2m(v) for v in re.findall(r"\b(?:lokey|hikey|key|pitch_keycenter)=(\S+)", txt)]
    keys = [k for k in keys if k is not None and 0 <= k <= 127]
    lov = re.findall(r"\blovel=(\d+)", txt)
    hiv = re.findall(r"\bhivel=(\d+)", txt)
    vel = set(zip(lov, hiv)) if len(lov) == len(hiv) else set(lov) | set(hiv)
    return {"regions": len(re.findall(r"<region>", txt)), "lokey": min(keys) if keys else None,
            "hikey": max(keys) if keys else None, "velocity_layers": max(1, len(vel)),
            "round_robin": bool(re.search(r"\b(seq_length|lorand)=", txt)),
            "release_samples": bool(re.search(r"trigger=release", txt))}


def sf2_presets(path: Path) -> dict[tuple[int, int], str]:
    data = path.read_bytes()
    out = {}
    i = 12
    while i < len(data):
        cid = data[i:i + 4]
        sz = struct.unpack("<I", data[i + 4:i + 8])[0]
        if cid == b"LIST" and data[i + 8:i + 12] == b"pdta":
            j = i + 12
            end = i + 8 + sz
            while j < end:
                sid = data[j:j + 4]
                ssz = struct.unpack("<I", data[j + 4:j + 8])[0]
                if sid == b"phdr":
                    for k in range(j + 8, j + 8 + ssz - 38, 38):
                        name = data[k:k + 20].split(b"\0")[0].decode("latin1").strip()
                        prog, bank = struct.unpack("<HH", data[k + 20:k + 24])
                        out[(bank, prog)] = name
                j += 8 + ssz + (ssz & 1)
        i += 8 + sz + (sz & 1)
    return out


def dir_size_mb(p: Path) -> float:
    if p.is_file():
        return round(p.stat().st_size / 1e6, 1)
    return round(sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1e6, 1)


def rel(p: Path | str) -> str:
    p = Path(p)
    return str(p.relative_to(INSTR_ROOT)) if str(p).startswith(str(INSTR_ROOT)) else str(p)


# ----------------------------------------------------------------------------- build
def build() -> dict:
    libs = []
    missing = []
    for slug, (url, lic, licfile, insts) in SFZ_LIBS.items():
        root = INSTR_ROOT / slug
        if not root.is_dir():
            missing.append({"slug": slug, "reason": "directory missing (download failed?)", "source_url": url})
            continue
        entries = []
        for sfz_rel, name, role, notes in insts:
            sfz = root / sfz_rel
            if not sfz.exists():
                missing.append({"slug": slug, "instrument": name, "reason": f"sfz not found: {sfz_rel}"})
                continue
            summ = sfz_summary(sfz)
            # sfizz streams sample tails from disk in a background thread; that race made repeated renders of
            # long one-shot kits differ sporadically. A wrapper with hint_ram_based=1 loads everything into RAM
            # at load time and makes sfizz_render byte-deterministic (verified on salamander_drumkit).
            ram = sfz.with_name(sfz.stem + ".ram.sfz")
            ram.write_text(f'// generated by build_instrument_inventory.py: RAM-load wrapper for deterministic sfizz renders\n'
                           f'<control> hint_ram_based=1\n#include "{sfz.name}"\n', encoding="utf-8")
            e = {"name": name, "role": role, "path": rel(ram), "path_original": rel(sfz), "backend": "sfz", "notes": notes,
                 "sfz_scan": summ}
            if role == "percussion" and summ["lokey"] is not None:
                e["keys"] = list(range(summ["lokey"], summ["hikey"] + 1))
            entries.append(e)
        libs.append({"slug": slug, "source_url": url, "license": {"id": lic, "url": LIC[lic], "file": rel(root / licfile) if (root / licfile).exists() else None},
                     "size_mb": dir_size_mb(root), "format": "sfz", "roles": sorted({e["role"] for e in entries}), "instruments": entries})

    for slug, (sf2p, url, lic, licfile, notes, drums, melodic) in SF2_LIBS.items():
        sf2 = Path(sf2p) if os.path.isabs(sf2p) else INSTR_ROOT / sf2p
        if not sf2.exists():
            missing.append({"slug": slug, "reason": f"sf2 missing: {sf2}", "source_url": url})
            continue
        presets = sf2_presets(sf2)
        entries = []
        if melodic:
            for prog, role, n in GM_MELODIC:
                pname = presets.get((0, prog))
                if pname is None:
                    continue
                entries.append({"name": f"{pname} [0:{prog}]", "role": role, "path": rel(sf2), "bank": 0, "program": prog,
                                "backend": "sf2", "notes": n})
        if drums:
            for prog, n in GM_DRUMS.items():
                pname = presets.get((128, prog))
                if pname is None:
                    continue
                entries.append({"name": f"{pname} [128:{prog}]", "role": "drums", "path": rel(sf2), "bank": 128, "program": prog,
                                "backend": "sf2", "notes": f"GM drum map; {n}"})
        libs.append({"slug": slug, "source_url": url, "license": {"id": lic, "url": LIC[lic], "file": licfile if Path(licfile).is_absolute() or (INSTR_ROOT / licfile).exists() else None},
                     "size_mb": dir_size_mb(sf2), "format": "sf2", "notes": notes, "roles": sorted({e["role"] for e in entries}),
                     "instruments": entries, "preinstalled": sf2.is_absolute() and not str(sf2).startswith(str(INSTR_ROOT))})

    avl_entries = []
    for p, name, n in AVL_KITS:
        if Path(p).exists():
            presets = sf2_presets(Path(p))
            (bank, prog), pname = sorted(presets.items())[0]
            avl_entries.append({"name": name, "role": "drums", "path": p, "bank": bank, "program": prog, "backend": "sf2",
                                "notes": f"{n}; preset '{pname}', GM-compatible map (AVL Drumkits)"})
    if avl_entries:
        libs.append({"slug": "avl_drumkits_sf2", "source_url": "(preinstalled: Debian avldrums.lv2 / x42 AVL Drumkits sf2 export)",
                     "license": {"id": "CC-BY-SA-3.0", "url": LIC["CC-BY-SA-3.0"], "file": "/usr/share/doc/avldrums.lv2/copyright", "author": "Glen MacArthur (sf2/*)"},
                     "size_mb": round(sum(dir_size_mb(Path(p)) for p, _, _ in AVL_KITS if Path(p).exists()), 1), "format": "sf2",
                     "roles": ["drums"], "instruments": avl_entries, "preinstalled": True})

    inv = {"schema_version": "instruments-inventory-1", "root": str(INSTR_ROOT), "libraries": libs,
           "rejected": [], "missing": missing,
           "total_downloaded_mb": round(sum(l["size_mb"] for l in libs if not l.get("preinstalled")), 1)}
    return inv


def main() -> int:
    inv = build()
    # keep any dawdreamer libraries / rejected entries written earlier by render_vst_test.py / render_patch_test.py
    if INVENTORY.exists():
        try:
            old = json.load(open(INVENTORY, encoding="utf-8"))
            for lib in old.get("libraries", []):
                if lib.get("format") == "dawdreamer":
                    inv["libraries"].append(lib)
        except Exception:  # noqa: BLE001
            pass
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    with open(INVENTORY, "w", encoding="utf-8") as fh:
        json.dump(inv, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    n = sum(len(l["instruments"]) for l in inv["libraries"])
    print(f"wrote {INVENTORY}: {len(inv['libraries'])} libraries, {n} instrument entries, {len(inv['missing'])} missing; "
          f"downloaded {inv['total_downloaded_mb']} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
