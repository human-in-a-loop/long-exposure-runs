#!/usr/bin/python3
"""v6 Phase 4 — build the per-ROLE patch pool (scripts/v6/patches/pool_v6.json) from workspace/instruments/INVENTORY.json.

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

    /usr/bin/python3 scripts/v6/patches/build_pool.py [--no-timbre] [--inventory PATH] [--out PATH]

Pool roles (generator roles) <- inventory roles:
    bass        <- electric_bass, synth_bass, acoustic_bass
    keys        <- piano, electric_piano, organ
    comp_guitar <- electric_guitar, acoustic_guitar
    melody      <- lead, electric_piano, electric_guitar, piano, brass
    pad         <- pad, strings_pad
    drums       <- drums   (GM note-map check: kick 36, snare 38|40, closed hat 42 REQUIRED; 46/49/51/45/47/50 recorded)
    percussion  <- percussion
Each patch entry: id, name, library, inventory_role, roles, backend (sfz|sf2|dawdreamer), path (sfz .ram.sfz wrapper /
sf2 file / plugin preset), bank+program (sf2), deterministic, velocity_layers, note_range [lo, hi], license, smoke-render
wav + sha256 + rms_dbfs, and "timbre": the unit-norm CLAP embedding (laion/clap-htsat-unfused, 512-d, 4 dp) of the
inventory smoke render (3 x 5 s windows, hop 2.5 s, mean-pooled). Embeddings are cached in
data/v6/patches/timbre_clap.npz (+ .json sidecar keyed by render sha256) so each render is embedded once;
torch runs at 2 threads (shared CPU). dawdreamer (Surge XT / Dexed) patches are NOT bit-deterministic: they are listed
under "audition" and excluded from the default role lists. Deterministic output (sorted keys, atomic write).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

WS = Path(__file__).resolve().parent.parent.parent.parent
if str(WS) not in sys.path:
    sys.path.insert(0, str(WS))

from scripts.v6.patches import sf2_keymap  # noqa: E402

SCHEMA_VERSION = 1
INSTR_ROOT = WS / "workspace" / "instruments"
INVENTORY = INSTR_ROOT / "INVENTORY.json"
POOL_OUT = Path(__file__).with_name("pool_v6.json")
TIMBRE_CACHE = WS / "data" / "v6" / "patches" / "timbre_clap.npz"
CLAP_MODEL = "laion/clap-htsat-unfused"
TIMBRE_WINDOW_S, TIMBRE_HOP_S, TIMBRE_DP = 5.0, 2.5, 4
ROLE_MAP = {"bass": ("electric_bass", "synth_bass", "acoustic_bass"), "keys": ("piano", "electric_piano", "organ"),
            "comp_guitar": ("electric_guitar", "acoustic_guitar"), "melody": ("lead", "electric_piano", "electric_guitar", "piano", "brass"),
            "pad": ("pad", "strings_pad"), "drums": ("drums",), "percussion": ("percussion",)}
DETERMINISTIC_BACKENDS = ("sfz", "sf2")


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


# --------------------------------------------------------------------------------------------------------- sfz scan ----
def sfz_text(path: Path, seen: set | None = None) -> str:
    seen = seen if seen is not None else set()
    if path in seen or not path.exists():
        return ""
    seen.add(path)
    txt = path.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'#include\s+"([^"]+)"', txt):
        txt += "\n" + sfz_text(path.parent / m.group(1), seen)
    return txt


def sfz_keys(path: Path) -> list:
    """Keys with at least one region: key=/lokey=/hikey= with <group> inheritance (sfz note names resolved)."""
    names = {"c": 0, "c#": 1, "db": 1, "d": 2, "d#": 3, "eb": 3, "e": 4, "f": 5, "f#": 6, "gb": 6, "g": 7, "g#": 8, "ab": 8, "a": 9, "a#": 10, "bb": 10, "b": 11}

    def n2m(s: str):
        s = s.strip().lower()
        if re.fullmatch(r"-?\d+", s):
            return int(s)
        m = re.fullmatch(r"([a-g][#b]?)(-?\d+)", s)
        return (int(m.group(2)) + 1) * 12 + names[m.group(1)] if m else None

    keys, group, cur, in_region = set(), {}, {}, False

    def flush():
        if in_region:
            z = dict(group, **cur)
            lo = n2m(z["lokey"]) if "lokey" in z else (n2m(z["key"]) if "key" in z else 0)
            hi = n2m(z["hikey"]) if "hikey" in z else (n2m(z["key"]) if "key" in z else 127)
            if lo is not None and hi is not None and "sample" in z:
                keys.update(range(min(lo, hi), max(lo, hi) + 1))

    for tok in re.split(r"(<[a-z]+>)", re.sub(r"//[^\n]*", "", sfz_text(path))):
        if tok.startswith("<"):
            flush()
            if tok in ("<group>", "<master>", "<global>"):
                if tok == "<group>":
                    group = {}
                cur, in_region = {}, False
            elif tok == "<region>":
                cur, in_region = {}, True
            else:
                cur, in_region = {}, False
            continue
        for k, v in re.findall(r"(\w+)=(\S+)", tok):
            if in_region:
                cur[k] = v
            else:
                group[k] = v
    flush()
    return sorted(keys)


# ----------------------------------------------------------------------------------------------------------- timbre ----
def load_timbre_cache(path: Path = TIMBRE_CACHE) -> tuple[dict, dict]:
    import numpy as np
    side = path.with_suffix(".json")
    if not (path.exists() and side.exists()):
        return {}, {}
    z = np.load(path)
    vecs = {k: z[k] for k in z.files}
    return vecs, json.loads(side.read_text())


def save_timbre_cache(vecs: dict, meta: dict, path: Path = TIMBRE_CACHE) -> None:
    import numpy as np
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp.npz")
    np.savez(tmp, **{k: vecs[k] for k in sorted(vecs)})
    os.replace(tmp, path)
    side = path.with_suffix(".json")
    side.write_text(json.dumps(meta, sort_keys=True, indent=2) + "\n")


def embed_renders(entries: list, cache_path: Path = TIMBRE_CACHE, log=print) -> dict:
    """{patch_id: unit-norm 512-d} for every entry with a smoke render; embeds only cache misses (by render sha256)."""
    import numpy as np
    vecs, meta = load_timbre_cache(cache_path)
    todo = [e for e in entries if e.get("render_wav") and (e["id"] not in vecs or meta.get(e["id"], {}).get("render_sha256") != e["render_sha256"])]
    log(f"[timbre] {len(entries)} entries, {len(entries) - len(todo)} cached, {len(todo)} to embed")
    if todo:
        import torch
        torch.set_num_threads(2)
        torch.manual_seed(0)
        from scripts.v6 import embed_audio as ea
        bb = ea.ClapBackbone()
        for e in todo:
            t0 = time.time()
            x, dur = ea.load_mono(INSTR_ROOT / e["render_wav"], bb.sr)
            w, starts = ea.cut_windows(x, bb.sr, TIMBRE_WINDOW_S, TIMBRE_HOP_S, -60.0, 3)
            if len(w) == 0:  # very quiet render: embed the whole clip once
                w = x[: int(TIMBRE_WINDOW_S * bb.sr)][None, :]
            emb = bb.embed(w, 8)
            v = emb.mean(axis=0)
            v = (v / max(float(np.linalg.norm(v)), 1e-12)).astype(np.float32)
            vecs[e["id"]] = v
            meta[e["id"]] = {"render_sha256": e["render_sha256"], "n_windows": int(len(w)), "model": CLAP_MODEL,
                             "window_s": TIMBRE_WINDOW_S, "hop_s": TIMBRE_HOP_S, "wall_s": round(time.time() - t0, 3)}
            log(f"[timbre] {e['id']} n_windows={len(w)} {meta[e['id']]['wall_s']}s")
            save_timbre_cache(vecs, meta, cache_path)
    return {e["id"]: vecs[e["id"]] for e in entries if e["id"] in vecs}


# ------------------------------------------------------------------------------------------------------------ build ----
def abs_path(p: str) -> str:
    return p if os.path.isabs(p) else str(INSTR_ROOT / p)


def entry_from(lib: dict, inst: dict) -> dict:
    backend = inst.get("backend") or lib.get("format")
    name, role = inst["name"], inst["role"]
    e = {"id": f"{lib['slug']}__{slugify(name)}", "name": name, "library": lib["slug"], "inventory_role": role, "backend": backend,
         "license": (lib.get("license") or {}).get("id"), "deterministic": backend in DETERMINISTIC_BACKENDS,
         "notes": inst.get("notes", ""), "roles": sorted(r for r, srcs in ROLE_MAP.items() if role in srcs)}
    rnd = inst.get("render") or {}
    e.update({"render_wav": rnd.get("wav"), "render_sha256": rnd.get("sha256"), "render_rms_dbfs": rnd.get("rms_dbfs"), "render_status": rnd.get("status")})
    if backend == "sfz":
        e["path"] = abs_path(inst["path"])
        sc = inst.get("sfz_scan") or {}
        e["velocity_layers"] = int(sc.get("velocity_layers") or 1)
        e["note_range"] = [sc.get("lokey"), sc.get("hikey")]
        e["round_robin"] = bool(sc.get("round_robin"))
        if role == "drums":
            e["mapped_keys"] = sfz_keys(Path(e["path"]))
    elif backend == "sf2":
        e["path"], e["bank"], e["program"] = abs_path(inst["path"]), int(inst["bank"]), int(inst["program"])
        keys = sf2_keymap.preset_keys(e["path"], e["bank"], e["program"])
        e["velocity_layers"] = sf2_keymap.preset_velocity_layers(e["path"], e["bank"], e["program"])
        e["note_range"] = [keys[0], keys[-1]] if keys else [None, None]
        if role == "drums":
            e["mapped_keys"] = keys
    else:  # dawdreamer
        e.update({"path": inst.get("path"), "plugin": inst.get("plugin"), "preset": inst.get("preset"), "program": inst.get("program"),
                  "velocity_layers": None, "note_range": [0, 127], "deterministic": False})
    if inst.get("keys"):
        e["mapped_keys"] = list(inst["keys"])
    if role == "drums":
        e["gm_drum_check"] = sf2_keymap.gm_drum_check(e.get("mapped_keys", []))
        e["mapped_keys"] = [k for k in e["mapped_keys"] if 27 <= k <= 87]
    return e


def build_pool(inventory: dict, timbre: bool = True, cache_path: Path = TIMBRE_CACHE, log=print) -> dict:
    entries, dropped = [], []
    for lib in inventory["libraries"]:
        for inst in lib.get("instruments", []):
            e = entry_from(lib, inst)
            if e.get("render_status") not in (None, "ok"):
                dropped.append({"id": e["id"], "reason": f"smoke render status {e['render_status']}"})
                continue
            if e["inventory_role"] == "drums" and not e["gm_drum_check"]["ok"]:
                dropped.append({"id": e["id"], "reason": "GM drum map: missing " + ",".join(e["gm_drum_check"]["missing_required"]),
                                "mapped_keys": e.get("mapped_keys")})
                continue
            entries.append(e)
    if timbre:
        vecs = embed_renders(entries, cache_path, log)
        for e in entries:
            v = vecs.get(e["id"])
            e["timbre"] = [round(float(x), TIMBRE_DP) for x in v] if v is not None else None
    patches = {e["id"]: e for e in entries}
    roles = {r: sorted(e["id"] for e in entries if r in e["roles"] and e["deterministic"]) for r in ROLE_MAP}
    audition = {r: sorted(e["id"] for e in entries if r in e["roles"] and not e["deterministic"]) for r in ROLE_MAP}
    from scripts.v6.gen.common import sha_file
    return {"schema_version": SCHEMA_VERSION, "built_from": {"inventory": str(INVENTORY.relative_to(WS)), "inventory_sha256": sha_file(INVENTORY)},
            "role_map": {r: list(v) for r, v in ROLE_MAP.items()}, "timbre": {"model": CLAP_MODEL, "dim": 512, "window_s": TIMBRE_WINDOW_S, "hop_s": TIMBRE_HOP_S,
                                                                            "pooling": "mean of <=3 windows, unit-norm", "decimals": TIMBRE_DP, "cache": str(cache_path.relative_to(WS)) if timbre else None},
            "roles": roles, "audition": audition, "patches": patches, "dropped": dropped,
            "counts": {"patches": len(patches), "deterministic": sum(e["deterministic"] for e in entries), "audition": sum(not e["deterministic"] for e in entries),
                       "per_role": {r: len(v) for r, v in roles.items()}, "per_role_audition": {r: len(v) for r, v in audition.items()}, "dropped": len(dropped)}}


def write_pool(pool: dict, out: Path) -> None:
    """Sorted-key JSON, indent 1, but every 'timbre' vector on a single line; atomic replace."""
    txt = json.dumps(pool, sort_keys=True, indent=1)
    for pid, e in pool["patches"].items():
        if e.get("timbre"):
            compact = json.dumps(e["timbre"], separators=(",", ":"))
            pretty = json.dumps(e["timbre"], indent=1).replace("\n", "\n   ")  # patches>id>timbre sits at depth 3
            assert pretty in txt, pid
            txt = txt.replace(pretty, compact, 1)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(txt + "\n", encoding="utf-8")
    os.replace(tmp, out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="build pool_v6.json from INVENTORY.json")
    ap.add_argument("--inventory", default=str(INVENTORY))
    ap.add_argument("--out", default=str(POOL_OUT))
    ap.add_argument("--timbre-cache", default=str(TIMBRE_CACHE))
    ap.add_argument("--no-timbre", action="store_true", help="skip CLAP embeddings (entries get timbre=null)")
    args = ap.parse_args(argv)
    inv = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    t0 = time.time()
    pool = build_pool(inv, not args.no_timbre, Path(args.timbre_cache))
    write_pool(pool, Path(args.out))
    print(json.dumps(pool["counts"], sort_keys=True), f"dropped={[d['id'] for d in pool['dropped']]}", f"wall={time.time() - t0:.1f}s", f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
