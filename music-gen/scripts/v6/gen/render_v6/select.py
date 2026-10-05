#!/usr/bin/python3
"""v6 Phase 4 — per-song patch SELECTION and ensemble plan (timbre-matched to the donor's stems, SHA-drawn, no PRNG).

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

For every role the generator plays (bass, drums, keys always; comp_guitar p~0.5, pad p~0.35, percussion p~0.25, melody
always with a SHA-drawn instrument family), pick ONE pool patch (scripts/v6/patches/pool_v6.json, deterministic backends
only):
  * donor stems present (data/v6/stems/<sha16>/{bass,other,drums}.wav, written by the separation agent — READ ONLY here):
    CLAP-embed 3 x 10 s windows of the matching stem (bass -> bass; keys/comp_guitar/pad/melody -> other; drums/percussion
    -> drums), mean-pool, cosine-similarity to every pool patch's timbre vector, keep the top-5 and draw by
    softmax(sim / temperature) with a SHA-256 uniform seeded by (song, donor, seed, iteration, role). temperature -> 0 is
    the arg-max. Donor embeddings are cached under data/v6/render_v6/donor_timbre/ by stem sha256; torch at 2 threads.
  * stems absent: a per-band prior over inventory roles (band 7 acoustic-leaning, band 4 synth-leaning, band 5 mixed) times
    a library-quality factor (multi-velocity sfz > single-layer sfz > GM sf2), normalised per inventory role so the four GM
    banks do not out-vote the sampled libraries; same SHA draw. Drum kits use a jazz/neutral/rock family prior per band.
Phase 5 (iteration 04) realism priors, applied on BOTH paths and recorded per candidate in patch_plan.json ("priors" block +
`library_prior` on every candidate): (a) the four GM sf2 banks (GM_BANKS) weigh GM_BANK_FACTOR = 0.3 in every role unless the
role's candidate set has no sfz option; on the CLAP path the prior enters the softmax as score = cosine + temperature * ln(prior),
so a GM patch must be clearly MORE similar to win; (b) the melody family pool is MELODY_FAMILIES_DEFAULT (electric_piano, piano,
electric_guitar, acoustic_guitar — borrowed from the comp_guitar pool — and real brass sections); synth leads and synth brass
join only for a synth-leaning band (BAND_PRIOR lead weight >= SYNTH_LEANING_LEAD_W, i.e. band 4), and calliope / square / fifths
GM-style leads (LEAD_EXCLUDE) never do; (c) keys: sampled pianos / e-pianos (KEYS_PREFERRED: Salamander, Upright KW, FM Piano)
weigh KEYS_SAMPLED_FACTOR = 2.0.
Everything (choice, similarities, probabilities, priors, the uniform draw) is recorded in patch_plan.json by plan_patches().
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from pathlib import Path

from scripts.v6.gen.common import WS, u, read_json, sha_file

POOL_PATH = WS / "scripts" / "v6" / "patches" / "pool_v6.json"
STEMS_ROOT = WS / "data" / "v6" / "stems"
DONOR_CACHE = WS / "data" / "v6" / "render_v6" / "donor_timbre"
RECEIPTS = WS / "corpus" / "ratings" / "ingest_receipts.jsonl"
ROLE_STEM = {"bass": "bass", "keys": "other", "comp_guitar": "other", "pad": "other", "melody": "other", "drums": "drums", "percussion": "drums"}
TOP_K, DEFAULT_TEMPERATURE, DEFAULT_BAND = 5, 0.05, 5
ENSEMBLE_P = {"bass": 1.0, "drums": 1.0, "keys": 1.0, "melody": 1.0, "comp_guitar": 0.5, "pad": 0.35, "percussion": 0.25}
MELODY_FAMILIES = ("lead", "electric_piano", "electric_guitar", "piano", "brass")  # inventory families the pool's melody role knows
MELODY_FAMILIES_DEFAULT = ("electric_piano", "piano", "electric_guitar", "acoustic_guitar", "brass")  # Phase 5 default melody pool
SYNTH_LEANING_LEAD_W = 0.5  # a band whose BAND_PRIOR["lead"] >= this is synth-leaning: "lead" joins the melody families
GM_BANKS = ("fluidr3_gm", "freepats_gm", "generaluser_gs", "musescore_general")
GM_BANK_FACTOR, KEYS_SAMPLED_FACTOR = 0.3, 2.0
KEYS_PREFERRED = re.compile(r"salamander|upright_piano_kw|fm_piano", re.I)  # sampled pianos / e-pianos (library ids)
LEAD_EXCLUDE = re.compile(r"calliope|square|fifths", re.I)  # GM-style leads never used for a melody
SYNTH_BRASS = re.compile(r"synth[ _]?brass", re.I)
BAND_PRIOR = {  # inventory role -> weight; rows are re-normalised per pool role at draw time
    7: {"electric_bass": 0.55, "acoustic_bass": 0.35, "synth_bass": 0.10, "piano": 0.45, "electric_piano": 0.40, "organ": 0.15, "acoustic_guitar": 0.55, "electric_guitar": 0.45,
        "lead": 0.10, "brass": 0.20, "pad": 0.30, "strings_pad": 0.70, "drums": 1.0, "percussion": 1.0},
    5: {"electric_bass": 0.60, "acoustic_bass": 0.10, "synth_bass": 0.30, "piano": 0.30, "electric_piano": 0.50, "organ": 0.20, "acoustic_guitar": 0.30, "electric_guitar": 0.70,
        "lead": 0.30, "brass": 0.30, "pad": 0.50, "strings_pad": 0.50, "drums": 1.0, "percussion": 1.0},
    4: {"electric_bass": 0.30, "acoustic_bass": 0.05, "synth_bass": 0.65, "piano": 0.20, "electric_piano": 0.45, "organ": 0.35, "acoustic_guitar": 0.15, "electric_guitar": 0.85,
        "lead": 0.60, "brass": 0.15, "pad": 0.70, "strings_pad": 0.30, "drums": 1.0, "percussion": 1.0},
}
KIT_FAMILY_PRIOR = {7: {"jazz": 0.5, "neutral": 0.4, "rock": 0.1}, 5: {"jazz": 0.25, "neutral": 0.5, "rock": 0.25}, 4: {"jazz": 0.1, "neutral": 0.45, "rock": 0.45}}


# ------------------------------------------------------------------------------------------------------------ pool ----
def load_pool(path: Path = POOL_PATH) -> dict:
    pool = read_json(path)
    pool["_sha256"], pool["_path"] = sha_file(path), str(path)
    return pool


def kit_family(patch: dict) -> str:
    n = patch["name"].lower()
    if re.search(r"brush|jazz|bop|buskman", n):
        return "jazz"
    if re.search(r"power|zeppelin|room|rock", n):
        return "rock"
    return "neutral"


def quality_factor(patch: dict) -> float:
    if patch["backend"] == "sfz":
        return 3.0 if (patch.get("velocity_layers") or 1) > 1 else 2.0
    return 1.0


def band_for(band: int) -> int:
    return int(band) if int(band) in BAND_PRIOR else min(BAND_PRIOR, key=lambda b: abs(b - int(band)))


def synth_leaning(band: int) -> bool:
    return BAND_PRIOR[band_for(band)]["lead"] >= SYNTH_LEANING_LEAD_W


def melody_families(band: int) -> tuple:
    return MELODY_FAMILIES_DEFAULT + (("lead",) if synth_leaning(band) else ())


def role_candidates(pool: dict, role: str, band: int, inventory_roles=None) -> list:
    """Patch ids eligible for `role`: the pool's role list, for melody extended with the comp_guitar pool's acoustic guitars and
    filtered by the Phase 5 family rules (LEAD_EXCLUDE always; synth leads / synth brass only for a synth-leaning band)."""
    ids = list(pool["roles"][role])
    if role == "melody":
        ids += [i for i in pool["roles"].get("comp_guitar", []) if pool["patches"][i]["inventory_role"] == "acoustic_guitar" and i not in ids]
        keep = []
        for i in ids:
            p = pool["patches"][i]
            if p["inventory_role"] == "lead" and (LEAD_EXCLUDE.search(p["name"]) or LEAD_EXCLUDE.search(p["library"]) or not synth_leaning(band)):
                continue
            if p["inventory_role"] == "brass" and SYNTH_BRASS.search(p["name"]) and not synth_leaning(band):
                continue
            keep.append(i)
        ids = keep
    if inventory_roles is not None:
        ids = [i for i in ids if pool["patches"][i]["inventory_role"] in inventory_roles]
    return sorted(ids)


def library_prior(pool: dict, role: str, patch_id: str, candidate_ids: list) -> float:
    """Phase 5 library prior for one candidate: GM_BANK_FACTOR for a GM sf2 bank when the candidate set has an sfz option,
    KEYS_SAMPLED_FACTOR for a sampled piano / e-piano in the keys role, else 1.0."""
    p = pool["patches"][patch_id]
    w = 1.0
    if p["library"] in GM_BANKS and any(pool["patches"][i]["backend"] == "sfz" for i in candidate_ids):
        w *= GM_BANK_FACTOR
    if role == "keys" and KEYS_PREFERRED.search(p["library"]):
        w *= KEYS_SAMPLED_FACTOR
    return w


def prior_weights(pool: dict, role: str, band: int, inventory_roles=None) -> dict:
    """{patch_id: weight} for the stems-absent path (per-inventory-role mass x quality, normalised within inventory role)."""
    bp = BAND_PRIOR[band_for(band)]
    ids = role_candidates(pool, role, band, inventory_roles)
    groups = {}
    for i in ids:
        groups.setdefault(pool["patches"][i]["inventory_role"], []).append(i)
    w = {}
    for inv_role, members in groups.items():
        q = {i: quality_factor(pool["patches"][i]) * library_prior(pool, role, i, ids) for i in members}
        if role == "drums":
            kf = KIT_FAMILY_PRIOR[band_for(band)]
            q = {i: q[i] * kf[kit_family(pool["patches"][i])] for i in members}
        tot = sum(q.values()) or 1.0
        for i in members:
            w[i] = bp.get(inv_role, 0.2) * q[i] / tot
    return w


# --------------------------------------------------------------------------------------------------- donor timbre ----
def donor_stem_path(donor: str, stem: str, stems_root: Path = STEMS_ROOT) -> Path | None:
    p = Path(stems_root) / donor / f"{stem}.wav"
    return p if p.exists() else None


_CLAP_BB = None


def _clap_backbone(ea):
    """Process-wide CLAP singleton: a fresh ClapModel per donor stem leaked ~0.45 GB per load and OOM-killed the 29-song
    iteration at 13 GB RSS (2026-10-05)."""
    global _CLAP_BB
    if _CLAP_BB is None:
        _CLAP_BB = ea.ClapBackbone()
    return _CLAP_BB


def donor_timbre(donor: str, stem: str, stems_root: Path = STEMS_ROOT, cache_dir: Path = DONOR_CACHE, log=print):
    """Mean-pooled unit-norm CLAP vector (3 x 10 s windows at the stem's quartiles) or None when the stem is absent."""
    import numpy as np
    p = donor_stem_path(donor, stem, stems_root)
    if p is None:
        return None
    sha = sha_file(p)
    cache_dir = Path(cache_dir)
    npz, side = cache_dir / f"{donor}_{stem}.npz", cache_dir / f"{donor}_{stem}.json"
    if npz.exists() and side.exists() and read_json(side).get("stem_sha256") == sha:
        return np.load(npz)["mean"]
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    import torch
    torch.set_num_threads(2)
    torch.manual_seed(0)
    from scripts.v6 import embed_audio as ea
    t0 = time.time()
    bb = _clap_backbone(ea)
    x, dur = ea.load_mono(p, bb.sr)
    L = int(10.0 * bb.sr)
    if len(x) < L:
        x = np.pad(x, (0, L - len(x)))
    starts = sorted({int(max(0, min(len(x) - L, round(q * len(x)) - L // 2))) for q in (0.25, 0.5, 0.75)})
    wins = [x[s:s + L] for s in starts if ea.rms_dbfs(x[s:s + L]) >= -60.0] or [x[starts[len(starts) // 2]:starts[len(starts) // 2] + L]]
    emb = bb.embed(np.stack(wins).astype(np.float32), 8)
    mean = emb.mean(axis=0)
    mean = (mean / max(float(np.linalg.norm(mean)), 1e-12)).astype(np.float32)
    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp = npz.with_name(npz.name + ".tmp.npz")
    np.savez(tmp, mean=mean, windows=emb, window_start_s=np.asarray(starts, dtype=np.float64) / bb.sr)
    os.replace(tmp, npz)
    side.write_text(json.dumps({"stem_sha256": sha, "path": str(p), "duration_s": round(dur, 3), "n_windows": len(wins), "model": ea.MODEL_IDS["clap"],
                                "window_s": 10.0, "wall_s": round(time.time() - t0, 3)}, sort_keys=True, indent=2) + "\n")
    log(f"[select] donor timbre {donor}/{stem}: {len(wins)} windows in {time.time() - t0:.1f}s")
    return mean


def similarities(vec, pool: dict, role: str, inventory_roles=None, band: int = DEFAULT_BAND) -> list:
    """[(patch_id, cosine)] descending over the role's eligible patches (role_candidates) that have a timbre vector."""
    import numpy as np
    out = []
    for i in role_candidates(pool, role, band, inventory_roles):
        p = pool["patches"][i]
        if p.get("timbre") is None:
            continue
        t = np.asarray(p["timbre"], dtype=np.float64)
        out.append((i, float(np.dot(vec, t) / max(np.linalg.norm(t) * np.linalg.norm(vec), 1e-12))))
    return sorted(out, key=lambda x: (-x[1], x[0]))


def apply_library_prior(sims: list, pool: dict, role: str, temperature: float) -> tuple[list, dict]:
    """score = cosine + temperature * ln(library_prior): the prior multiplies the softmax mass (temperature 0: it still orders
    ties and lets a 0.3-prior GM patch win only when its cosine is higher by > T*ln(1/0.3)). Returns (scored, {id: prior})."""
    ids = [i for i, _ in sims]
    pri = {i: library_prior(pool, role, i, ids) for i in ids}
    t = max(temperature, 1e-9)
    return sorted([(i, s + t * math.log(pri[i])) for i, s in sims], key=lambda x: (-x[1], x[0])), pri


# ------------------------------------------------------------------------------------------------------------ draw ----
def softmax_pick(cands: list, temperature: float, tag: str) -> tuple[str, list, float]:
    """cands [(id, score)] -> (chosen id, [{id, score, prob}], uniform). temperature <= 1e-9 is the arg-max."""
    if not cands:
        raise ValueError("no candidates")
    x = u(tag)
    if temperature <= 1e-9:
        best = max(cands, key=lambda c: (c[1], c[0]))[0]
        return best, [{"id": i, "score": round(s, 6), "prob": 1.0 if i == best else 0.0} for i, s in cands], x
    m = max(s for _, s in cands)
    ex = [(i, math.exp((s - m) / temperature)) for i, s in cands]
    z = sum(e for _, e in ex)
    probs = [(i, e / z) for i, e in ex]
    acc, chosen = 0.0, probs[-1][0]
    for i, pr in sorted(probs, key=lambda c: c[0]):  # sorted-key inverse CDF (same convention as common.draw_from)
        acc += pr
        if x < acc:
            chosen = i
            break
    pm = dict(probs)
    return chosen, [{"id": i, "score": round(s, 6), "prob": round(pm[i], 6)} for i, s in cands], x


def select_patch(pool: dict, role: str, tag: str, band: int, temperature: float = DEFAULT_TEMPERATURE, donor_vec=None, inventory_roles=None) -> dict:
    if donor_vec is not None:
        raw = similarities(donor_vec, pool, role, inventory_roles, band)
        scored, pri = apply_library_prior(raw, pool, role, temperature)
        sims = scored[:TOP_K]
        if sims:
            chosen, cands, x = softmax_pick(sims, temperature, f"{tag}|patch")
            cos = dict(raw)
            for c in cands:
                c["cosine"], c["library_prior"] = round(cos[c["id"]], 6), pri[c["id"]]
            return {"patch_id": chosen, "method": "clap_similarity_softmax_top5", "temperature": temperature, "candidates": cands, "draw_u": round(x, 9),
                    "similarity": round(cos[chosen], 6), "score": next(c["score"] for c in cands if c["id"] == chosen), "library_prior": pri[chosen],
                    "score_rule": "cosine + temperature * ln(library_prior); top-5 by score; softmax(score / temperature)"}
    w = prior_weights(pool, role, band, inventory_roles)
    if not w:
        raise ValueError(f"no pool patches for role {role!r} / {inventory_roles}")
    x, tot, acc, chosen = u(f"{tag}|patch"), sum(w.values()), 0.0, sorted(w)[-1]  # the prior IS the mass: sorted-key inverse CDF on it
    for i in sorted(w):
        acc += w[i] / tot
        if x < acc:
            chosen = i
            break
    ids = sorted(w)
    cands = [{"id": i, "prior_weight": round(w[i] / tot, 6), "library_prior": library_prior(pool, role, i, ids)} for i in sorted(w, key=lambda k: (-w[k], k))[:8]]
    return {"patch_id": chosen, "method": f"band_prior(band={band_for(band)})", "candidates": cands, "draw_u": round(x, 9), "prior_weight": round(w[chosen] / tot, 6),
            "library_prior": library_prior(pool, role, chosen, ids)}


# ---------------------------------------------------------------------------------------------------- plan / band ----
def donor_band(donor: str, receipts: Path = RECEIPTS, default: int = DEFAULT_BAND) -> tuple[int, str]:
    if Path(receipts).exists():
        for line in Path(receipts).read_text(encoding="utf-8").splitlines():
            if line.strip() and json.loads(line).get("sha16") == donor:
                return int(json.loads(line)["band"]), "ingest_receipts"
    return default, "default (donor not in receipts)"


def ensemble_plan(tag: str, band: int) -> dict:
    roles, draws = {}, {}
    for role in sorted(ENSEMBLE_P):
        x = u(f"{tag}|ensemble|{role}")
        roles[role] = bool(x < ENSEMBLE_P[role])
        draws[role] = round(x, 6)
    bp = BAND_PRIOR[band_for(band)]
    fams = melody_families(band)
    fam_w = {f: bp[f] for f in fams}
    x = u(f"{tag}|ensemble|melody_family")
    acc, fam = 0.0, fams[-1]
    for f in sorted(fam_w):
        acc += fam_w[f] / sum(fam_w.values())
        if x < acc:
            fam = f
            break
    return {"roles": roles, "probabilities": dict(ENSEMBLE_P), "draws": draws, "melody_family": fam, "melody_family_weights": fam_w,
            "melody_families": list(fams), "synth_leaning": synth_leaning(band),
            "melody_pan": 0.1 if u(f"{tag}|ensemble|melody_pan") < 0.5 else -0.1}


def plan_patches(song_id: str, donor: str, iteration: int, seed: int, pool: dict | None = None, band: int | None = None, stems_root: Path = STEMS_ROOT,
                 temperature: float = DEFAULT_TEMPERATURE, cache_dir: Path = DONOR_CACHE, receipts: Path = RECEIPTS, log=print) -> dict:
    pool = pool or load_pool()
    if band is None:
        band, band_src = donor_band(donor, receipts)
    else:
        band_src = "argument"
    tag = f"render_v6|song={song_id}|donor={donor}|seed={seed}|iter={iteration}"
    ens = ensemble_plan(tag, band)
    stems_found = {s: str(donor_stem_path(donor, s, stems_root)) for s in ("bass", "other", "drums") if donor_stem_path(donor, s, stems_root)}
    vecs = {s: donor_timbre(donor, s, stems_root, cache_dir, log) for s in stems_found}
    selection = {}
    for role in sorted(ENSEMBLE_P):
        if not ens["roles"][role]:
            continue
        inv = (ens["melody_family"],) if role == "melody" else None
        sel = select_patch(pool, role, f"{tag}|role={role}", band, temperature, vecs.get(ROLE_STEM[role]), inv)
        if role == "melody" and sel is None:
            sel = select_patch(pool, role, f"{tag}|role={role}", band, temperature, vecs.get(ROLE_STEM[role]))
        p = pool["patches"][sel["patch_id"]]
        sel.update({"stem_used": ROLE_STEM[role] if ROLE_STEM[role] in vecs else None, "patch": {k: p.get(k) for k in ("id", "name", "library", "inventory_role", "backend", "path", "bank", "program",
                                                                                                                       "velocity_layers", "note_range", "license", "deterministic")}})
        selection[role] = sel
    priors = {"gm_banks": list(GM_BANKS), "gm_bank_factor": GM_BANK_FACTOR, "gm_factor_applies": "when the role's candidate set has an sfz option",
              "keys_sampled_factor": KEYS_SAMPLED_FACTOR, "keys_preferred": KEYS_PREFERRED.pattern, "melody_families_default": list(MELODY_FAMILIES_DEFAULT),
              "synth_leaning_lead_w": SYNTH_LEANING_LEAD_W, "lead_exclude": LEAD_EXCLUDE.pattern, "synth_brass_excluded_unless_synth_leaning": SYNTH_BRASS.pattern,
              "clap_path": "score = cosine + temperature * ln(library_prior), top-5 by score, softmax(score / temperature)",
              "band_prior": BAND_PRIOR[band_for(band)], "kit_family_prior": KIT_FAMILY_PRIOR[band_for(band)]}
    return {"schema_version": 2, "song_id": song_id, "donor": donor, "iteration": iteration, "seed": seed, "band": band, "band_source": band_src, "tag": tag, "temperature": temperature,
            "stems_root": str(stems_root), "stems_found": stems_found, "ensemble": ens, "selection": selection, "priors": priors,
            "pool": {"path": pool.get("_path"), "sha256": pool.get("_sha256"), "counts": pool.get("counts")}, "sampling": "SHA-256 inverse-CDF (no PRNG)"}
