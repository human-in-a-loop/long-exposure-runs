#!/usr/bin/python3
"""v6 Phase 4 — which MIDI keys a SoundFont preset actually maps (pure-stdlib RIFF/pdta reader).

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

`preset_keys(sf2_path, bank, program)` -> sorted list of MIDI keys that have at least one sample zone, by walking
phdr -> pbag -> pgen(instrument=41, keyRange=43) -> inst -> ibag -> igen(keyRange=43, sampleID=53). Zones without a
keyRange cover 0..127; a preset-zone keyRange intersects the instrument zones it references; global zones (no
instrument / no sampleID generator) contribute nothing by themselves. Used by build_pool.py to drop drum kits whose
kick/snare/hat are not where the composer puts them (GM 36 / 38|40 / 42) and to record melodic note ranges.
"""
from __future__ import annotations

import struct
from functools import lru_cache
from pathlib import Path

GEN_INSTRUMENT, GEN_KEYRANGE, GEN_VELRANGE, GEN_SAMPLEID = 41, 43, 44, 53
GM_DRUM_REQUIRED = {"kick": (36,), "snare": (38, 40), "closed_hat": (42,)}
GM_DRUM_OPTIONAL = {"open_hat": (46,), "crash": (49,), "ride": (51,), "tom_low": (45,), "tom_mid": (47,), "tom_high": (50,)}


def _chunks(data: bytes, start: int, end: int):
    i = start
    while i + 8 <= end:
        cid, size = data[i:i + 4], struct.unpack("<I", data[i + 4:i + 8])[0]
        yield cid, i + 8, i + 8 + size
        i += 8 + size + (size & 1)


def _pdta(data: bytes) -> dict:
    if data[:4] != b"RIFF" or data[8:12] != b"sfbk":
        raise ValueError("not a SoundFont 2 file")
    out = {}
    for cid, a, b in _chunks(data, 12, len(data)):
        if cid == b"LIST" and data[a:a + 4] == b"pdta":
            for sid, c, d in _chunks(data, a + 4, b):
                out[sid.decode("ascii")] = data[c:d]
    return out


def _records(blob: bytes, fmt: str):
    n = struct.calcsize(fmt)
    return [struct.unpack(fmt, blob[i:i + n]) for i in range(0, len(blob) - len(blob) % n, n)]


@lru_cache(maxsize=16)
def _parse(path: str) -> dict:
    p = _pdta(Path(path).read_bytes())
    phdr = [(r[0].split(b"\0")[0].decode("latin-1"), r[1], r[2], r[3]) for r in _records(p["phdr"], "<20sHHHIII")]
    pbag = _records(p["pbag"], "<HH")
    pgen = _records(p["pgen"], "<HH")
    inst = [(r[0].split(b"\0")[0].decode("latin-1"), r[1]) for r in _records(p["inst"], "<20sH")]
    ibag = _records(p["ibag"], "<HH")
    igen = _records(p["igen"], "<HH")
    return {"phdr": phdr, "pbag": pbag, "pgen": pgen, "inst": inst, "ibag": ibag, "igen": igen}


def _zone_gens(bags: list, gens: list, lo: int, hi: int) -> list:
    """[{gen_oper: amount}] for bag indices lo..hi-1."""
    zones = []
    for zi in range(lo, hi):
        g0, g1 = bags[zi][0], bags[zi + 1][0] if zi + 1 < len(bags) else len(gens)
        zones.append({op: amt for op, amt in gens[g0:g1]})
    return zones


def _keyrange(z: dict) -> tuple:
    if GEN_KEYRANGE not in z:
        return (0, 127)
    amt = z[GEN_KEYRANGE]
    return (amt & 0xFF, (amt >> 8) & 0xFF)


def instrument_keys(path: str, inst_index: int) -> set:
    d = _parse(path)
    inst, ibag, igen = d["inst"], d["ibag"], d["igen"]
    if inst_index + 1 >= len(inst):
        return set()
    keys = set()
    for z in _zone_gens(ibag, igen, inst[inst_index][1], inst[inst_index + 1][1]):
        if GEN_SAMPLEID not in z:
            continue  # global zone
        lo, hi = _keyrange(z)
        keys.update(range(min(lo, hi), max(lo, hi) + 1))
    return keys


def presets(path: str) -> dict:
    """{(bank, program): name} for every preset (terminal 'EOP' excluded)."""
    return {(r[2], r[1]): r[0] for r in _parse(str(path))["phdr"][:-1]}


def preset_keys(path: str, bank: int, program: int) -> list:
    d = _parse(str(path))
    phdr, pbag, pgen = d["phdr"], d["pbag"], d["pgen"]
    keys = set()
    for i, (name, prog, bnk, bag) in enumerate(phdr[:-1]):
        if (bnk, prog) != (int(bank), int(program)):
            continue
        for z in _zone_gens(pbag, pgen, bag, phdr[i + 1][3]):
            if GEN_INSTRUMENT not in z:
                continue  # global preset zone
            lo, hi = _keyrange(z)
            keys.update(k for k in instrument_keys(str(path), z[GEN_INSTRUMENT]) if min(lo, hi) <= k <= max(lo, hi))
    return sorted(keys)


def preset_velocity_layers(path: str, bank: int, program: int) -> int:
    """Number of distinct velocity ranges across the sample zones the preset reaches (1 = no velocity switching)."""
    d = _parse(str(path))
    phdr, pbag, pgen = d["phdr"], d["pbag"], d["pgen"]
    ranges = set()
    for i, (name, prog, bnk, bag) in enumerate(phdr[:-1]):
        if (bnk, prog) != (int(bank), int(program)):
            continue
        for z in _zone_gens(pbag, pgen, bag, phdr[i + 1][3]):
            if GEN_INSTRUMENT not in z:
                continue
            ii = z[GEN_INSTRUMENT]
            inst, ibag, igen = d["inst"], d["ibag"], d["igen"]
            if ii + 1 >= len(inst):
                continue
            pv = z.get(GEN_VELRANGE, 127 << 8)
            for iz in _zone_gens(ibag, igen, inst[ii][1], inst[ii + 1][1]):
                if GEN_SAMPLEID in iz:
                    amt = iz.get(GEN_VELRANGE, 127 << 8)
                    ranges.add((max(pv & 0xFF, amt & 0xFF), min((pv >> 8) & 0xFF, (amt >> 8) & 0xFF)))
    return max(1, len(ranges))


def gm_drum_check(keys) -> dict:
    """{ok, missing_required: [...], present_optional: [...], missing_optional: [...]} for a drum key set."""
    ks = set(keys)
    missing = [n for n, alts in GM_DRUM_REQUIRED.items() if not any(a in ks for a in alts)]
    present = [n for n, alts in GM_DRUM_OPTIONAL.items() if any(a in ks for a in alts)]
    return {"ok": not missing, "missing_required": missing, "present_optional": present,
            "missing_optional": [n for n in GM_DRUM_OPTIONAL if n not in present]}


if __name__ == "__main__":  # pragma: no cover
    import sys
    p, b, pr = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    ks = preset_keys(p, b, pr)
    print(presets(p).get((b, pr)), len(ks), ks[:8], "...", ks[-8:] if ks else [], gm_drum_check(ks))
