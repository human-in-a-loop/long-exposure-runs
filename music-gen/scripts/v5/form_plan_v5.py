#!/usr/bin/python3
"""c85 P1 (F1 LENGTH + FORM + ARRANGEMENT) — corpus form-plan model from bar-level self-similarity (pre-registered).

created: 2026-09-09T21:55:00Z
cycle: 85
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F1-form-arrangement

Pre-registration: data/v5/gen/form_prereg_c85.json (mtime must precede every output; asserted). Everything below is the
mechanical realisation of that file:
  corpus  = the 21 c84 harmony-chain songs (data/v5/rules/harmony_markov_v5_full.json gate.used); tempo-/content-blocked
            songs never read; MIDI from canonical_v5_reindexed/ only (MISSING_REINDEX otherwise).
  bars    = phase-shifted 16th grid (groove_v5_v2.phase_offset, READ-ONLY); per bar: 12-D beat-weighted PCP over
            bass+guitar+piano+other with the min(duration, 1 beat) cap; 48-D kick16/snare16/hat16 bits; 6-D per-stem
            onset density (drums, bass, guitar, piano, other, vocals / per-song max).
  blocks  = 8-bar blocks; block feature = concat of the three L2-normalized group means, each weighted 1/sqrt(3);
            cosine self-similarity; deterministic single-linkage agglomeration at 0.85; labels in first-appearance order.
  model   = length distribution round(bar_count/8) clipped [4,8]; first-order Markov over labels (songs with < 4 blocks
            contribute length only); per-label drum-density tercile + harmony-region (c84 chord_stream) targets;
            intro density quantile; boundary fill pool (top-quartile snare popcount of last bars before a label change).
  R1      = eligible focus songs (WIG, CG, Rome) each recover >= 3 labels AND a literal repeat; else the fixed template
            A A B A B C A A is recorded as the fallback for the generator (no threshold sweep — FD-1).
Outputs: data/v5/rules/form_plan_v5.json (--out for the x2 byte-det run). No PRNG anywhere.
Discipline: /usr/bin/python3 guard; no sidecar_nonfactor; no VST3 state APIs; READ-ONLY inputs; nothing under data/v4/**.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
import numpy as np  # noqa: E402
from scripts.v5 import groove_v5_v2 as G  # noqa: E402  READ-ONLY (onsets_slots / phase_offset / bar_patterns / bits)
from scripts.v5.harmony_v5 import read_notes, MissingReindexError  # noqa: E402  READ-ONLY
from scripts.v5.content_blocked import refuse_if_content_blocked  # noqa: E402

ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
PREREG = Path("data/v5/gen/form_prereg_c85.json")
CHAIN = Path("data/v5/rules/harmony_markov_v5_full.json")
PER_SONG_HARMONY = Path("data/v5/rules/per_song_c84")
HARMONY_STEMS = ("bass", "guitar", "piano", "other")
DENSITY_STEMS = ("drums", "bass", "guitar", "piano", "other", "vocals")
BARS_PER_BLOCK = 8
SIM_THRESHOLD = 0.85
LEN_MIN, LEN_MAX = 4, 8
LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
FOCUS_ELIGIBLE = ("252eb21ce7df7328", "31a164f845f8e27e", "51e433ade2a845e1")
FALLBACK_TEMPLATE = ("A", "A", "B", "A", "B", "C", "A", "A")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _norm(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def popcount(x: int) -> int:
    return bin(int(x)).count("1")


def bar_of_beat(beat: float, offset: int) -> int:
    return int(np.floor((beat - offset / 4.0) / 4.0))


def song_bars(sha16: str, corpus: Path) -> dict:
    """Per-bar features + drum patterns + chord roots for one song (all deterministic)."""
    d = corpus / sha16
    md = d / "canonical_v5_reindexed"
    if not (md / "reindex_manifest.json").exists():
        raise MissingReindexError(f"MISSING_REINDEX: {sha16}")
    tm = json.loads((d / "transcription_manifest.json").read_text())
    n_bars = int(np.floor(float(tm["bar_count_at_bpm_v5"])))
    drums = G.onsets_slots(md / "drums.mid") if (md / "drums.mid").exists() else []
    bass = G.onsets_slots(md / "bass.mid") if (md / "bass.mid").exists() else []
    ph = G.phase_offset(sha16, drums)
    o = ph["offset"]
    # drum patterns per bar (aligned); bars without drums -> all-zero patterns
    pats = {b["bar"]: b for b in G.bar_patterns(drums, bass, o)}
    drum48 = np.zeros((n_bars, 48))
    density_drum = np.zeros(n_bars)
    for k in range(n_bars):
        p = pats.get(k)
        if p:
            for j in G.bits(p["kick"], 8):
                drum48[k, 2 * j] = drum48[k, 2 * j + 1] = 1.0
            for pos in G.bits(p["snare"]):
                drum48[k, 16 + pos] = 1.0
            for pos in G.bits(p["hat"]):
                drum48[k, 32 + pos] = 1.0
            density_drum[k] = popcount(p["kick"]) + popcount(p["snare"]) + popcount(p["hat"])
    # per-stem onset density per bar
    dens6 = np.zeros((n_bars, 6))
    for si, stem in enumerate(DENSITY_STEMS):
        p = md / f"{stem}.mid"
        if not p.exists():
            continue
        for slot, _pitch in G.onsets_slots(p):
            k = (slot - o) // G.SLOTS
            if 0 <= k < n_bars:
                dens6[k, si] += 1
        mx = dens6[:, si].max()
        if mx > 0:
            dens6[:, si] /= mx
    # PCP per bar with the min(duration, 1 beat) cap
    pcp = np.zeros((n_bars, 12))
    for stem in HARMONY_STEMS:
        p = md / f"{stem}.mid"
        if not p.exists():
            continue
        for s, e, pitch, _v in read_notes(p):
            dur = e - s
            w = min(dur, 1.0)
            k0, k1 = bar_of_beat(s, o), bar_of_beat(e, o)
            for k in range(max(k0, 0), min(k1, n_bars - 1) + 1):
                b0, b1 = 4 * k + o / 4.0, 4 * k + 4 + o / 4.0
                ov = min(e, b1) - max(s, b0)
                if ov > 0:
                    pcp[k, pitch % 12] += w * ov / dur
    # chord roots per bar from the c84 per-song chord stream (relative roots)
    hp = PER_SONG_HARMONY / sha16 / "harmony_v5.json"
    roots_per_bar: dict[int, dict[int, int]] = {}
    if hp.exists():
        for e in json.loads(hp.read_text())["chord_stream"]:
            st = e["state"]
            if st == "N" or ":" not in st:
                continue
            k = bar_of_beat(float(e["beat"]), o)
            if 0 <= k < n_bars:
                r = int(st.split(":")[0])
                roots_per_bar.setdefault(k, {})[r] = roots_per_bar.setdefault(k, {}).get(r, 0) + 1
    feats = np.zeros((n_bars, 66))
    for k in range(n_bars):
        feats[k, :12] = _norm(pcp[k])
        feats[k, 12:60] = _norm(drum48[k])
        feats[k, 60:] = _norm(dens6[k])
    return {"title": tm.get("title"), "bpm_v5": float(tm["bpm_v5"]), "bar_count": float(tm["bar_count_at_bpm_v5"]), "n_bars": n_bars,
            "phase_offset": o, "feats": feats, "density_drum": density_drum, "pats": pats, "roots_per_bar": roots_per_bar,
            "has_harmony_stream": hp.exists()}


def block_features(feats: np.ndarray, n_blocks: int) -> np.ndarray:
    out = np.zeros((n_blocks, 66))
    w = 1.0 / np.sqrt(3.0)
    for j in range(n_blocks):
        m = feats[8 * j: 8 * j + 8].mean(axis=0)
        out[j, :12] = w * _norm(m[:12])
        out[j, 12:60] = w * _norm(m[12:60])
        out[j, 60:] = w * _norm(m[60:])
    return out


def cosine_matrix(bf: np.ndarray) -> np.ndarray:
    n = bf.shape[0]
    S = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            ni, nj = np.linalg.norm(bf[i]), np.linalg.norm(bf[j])
            S[i, j] = float(bf[i] @ bf[j] / (ni * nj)) if ni > 0 and nj > 0 else 0.0
    return np.round(S, 9)


def single_linkage(S: np.ndarray, thr: float) -> list[int]:
    """Deterministic single linkage; returns cluster id per block (ids arbitrary, relabelled by first appearance later)."""
    n = S.shape[0]
    cl = list(range(n))
    while True:
        best = None
        for i in range(n):
            for j in range(i + 1, n):
                if cl[i] == cl[j]:
                    continue
                s = S[i, j]
                if s >= thr and (best is None or s > best[0] or (s == best[0] and (i, j) < best[1])):
                    best = (s, (i, j))
        if best is None:
            break
        i, j = best[1]
        a, b = cl[i], cl[j]
        cl = [a if c == b else c for c in cl]
    return cl


def first_appearance_labels(cl: list[int]) -> str:
    seen: dict[int, str] = {}
    out = []
    for c in cl:
        if c not in seen:
            seen[c] = LABELS[len(seen)]
        out.append(seen[c])
    return "".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="c85 F1 corpus form-plan model")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--out", default="data/v5/rules/form_plan_v5.json")
    args = ap.parse_args(argv)
    corpus = Path(args.corpus_dir)
    out_p = Path(args.out)
    prereg_mtime = PREREG.stat().st_mtime
    if out_p.exists() and out_p.stat().st_mtime < prereg_mtime:
        raise SystemExit("PREREG_AFTER_OUTPUT")
    chain = json.loads(CHAIN.read_text())
    eligible = list(chain["gate"]["used"])
    blocked = set(json.loads((corpus / "recanonicalization_blocked.json").read_text())["blocked_songs"])
    assert not (set(eligible) & blocked), "tempo-blocked song in the eligible list"
    refuse_if_content_blocked(eligible, corpus, who="form_plan_v5")
    per_song, forms_for_transitions = {}, []
    all_block_dens, block_rows = [], []  # block_rows: (song, block idx, label, density, root)
    lengths: dict[int, int] = {}
    intro_dens = []
    boundary_bars = []  # (snare, hat, song order, bar)
    all_bars_snare = []  # (popcount snare, song order, bar, snare, hat)
    for si, s in enumerate(eligible):
        r = song_bars(s, corpus)
        n_blocks = r["n_bars"] // BARS_PER_BLOCK
        n_sec = max(LEN_MIN, min(LEN_MAX, int(round(r["bar_count"] / 8.0))))
        lengths[n_sec] = lengths.get(n_sec, 0) + 1
        bf = block_features(r["feats"], n_blocks) if n_blocks else np.zeros((0, 66))
        S = cosine_matrix(bf) if n_blocks else np.zeros((0, 0))
        cl = single_linkage(S, SIM_THRESHOLD) if n_blocks else []
        form = first_appearance_labels(cl)
        dens = [float(r["density_drum"][8 * j: 8 * j + 8].mean()) for j in range(n_blocks)]
        roots = []
        for j in range(n_blocks):
            cnt: dict[int, int] = {}
            for k in range(8 * j, 8 * j + 8):
                for root, c in r["roots_per_bar"].get(k, {}).items():
                    cnt[root] = cnt.get(root, 0) + c
            roots.append(min(cnt, key=lambda x: (-cnt[x], x)) if cnt else None)
        for j in range(n_blocks):
            all_block_dens.append(dens[j])
            block_rows.append((s, j, form[j], dens[j], roots[j]))
            if j + 1 < n_blocks and form[j] != form[j + 1]:
                p = r["pats"].get(8 * j + 7)
                boundary_bars.append((int(p["snare"]) if p else 0, int(p["hat"]) if p else 0, si, 8 * j + 7))
        for k, p in sorted(r["pats"].items()):
            all_bars_snare.append((popcount(p["snare"]), si, k, int(p["snare"]), int(p["hat"])))
        if n_blocks:
            intro_dens.append(dens[0])
        in_trans = n_blocks >= LEN_MIN
        if in_trans:
            forms_for_transitions.append(form)
        per_song[s] = {"title": r["title"], "bpm_v5": r["bpm_v5"], "bar_count_at_bpm_v5": r["bar_count"], "n_bars": r["n_bars"], "n_blocks": n_blocks,
                       "n_sections_for_length": n_sec, "phase_offset": r["phase_offset"], "form": form, "n_labels": len(set(form)),
                       "has_literal_repeat": any(form.count(c) >= 2 for c in set(form)), "in_transition_corpus": in_trans,
                       "block_density": [round(x, 6) for x in dens], "block_root": roots, "has_harmony_stream": r["has_harmony_stream"],
                       "similarity": S.tolist()}
        print(f"{s} {str(r['title'])[:28]:28s} bars={r['n_bars']:3d} blocks={n_blocks:2d} o={r['phase_offset']:2d} form={form}")
    # ---- model ----
    labels_seen = sorted({c for f in forms_for_transitions for c in f})
    start: dict[str, int] = {}
    trans: dict[str, dict[str, int]] = {}
    for f in forms_for_transitions:
        start[f[0]] = start.get(f[0], 0) + 1
        for a, b in zip(f, f[1:]):
            trans.setdefault(a, {})[b] = trans.setdefault(a, {}).get(b, 0) + 1
    trans_probs = {}
    for a in labels_seen:
        row = trans.get(a, {})
        tot = sum(row.values())
        trans_probs[a] = {b: (row.get(b, 0) / tot if tot else 1.0 / len(labels_seen)) for b in labels_seen}
    rep_a = trans_probs.get("A", {}).get("A")
    dens_arr = np.asarray(all_block_dens)
    t1, t2 = (float(np.percentile(dens_arr, 33.333)), float(np.percentile(dens_arr, 66.667))) if len(dens_arr) else (0.0, 0.0)

    def tercile(x: float) -> int:
        return 0 if x < t1 else (1 if x < t2 else 2)

    per_label: dict[str, dict] = {}
    for s, j, lab, dv, root in block_rows:
        e = per_label.setdefault(lab, {"n_blocks": 0, "density_tercile_counts": [0, 0, 0], "root_counts": {}})
        e["n_blocks"] += 1
        e["density_tercile_counts"][tercile(dv)] += 1
        if root is not None:
            e["root_counts"][str(root)] = e["root_counts"].get(str(root), 0) + 1
    for lab, e in per_label.items():
        n = sum(e["density_tercile_counts"])
        e["density_tercile_probs"] = [round(c / n, 6) if n else 1 / 3 for c in e["density_tercile_counts"]]
        e["harmony_region"] = int(min(e["root_counts"], key=lambda r_: (-e["root_counts"][r_], int(r_)))) if e["root_counts"] else None
    intro_q = None
    if intro_dens and len(dens_arr):
        qs = [float((dens_arr < d).mean()) for d in intro_dens]
        intro_q = float(np.median(qs))
    sn = [b[0] for b in boundary_bars]
    fill_pool, fallback = [], False
    if boundary_bars and max(popcount(x) for x in sn) > 0:
        q75 = float(np.percentile([popcount(x) for x in sn], 75))
        cnt: dict[tuple[int, int], int] = {}
        for snare, hat, _si, _k in boundary_bars:
            if popcount(snare) >= q75:
                cnt[(snare, hat)] = cnt.get((snare, hat), 0) + 1
        fill_pool = [{"snare": k[0], "hat": k[1], "count": v} for k, v in sorted(cnt.items())]
    if not fill_pool:
        fallback = True
        best = max(all_bars_snare, key=lambda x: (x[0], -x[1], -x[2]))
        fill_pool = [{"snare": best[3], "hat": best[4], "count": 1}]
    r1 = {s: {"n_labels": per_song[s]["n_labels"], "has_literal_repeat": per_song[s]["has_literal_repeat"], "form": per_song[s]["form"]} for s in FOCUS_ELIGIBLE}
    r1_pass = all(v["n_labels"] >= 3 and v["has_literal_repeat"] for v in r1.values())
    out = {"schema_version": 1, "cycle": 85, "agent": "worker", "run_id": "run-2026-09-06T000000Z", "milestone": "M-V5-GEN-1/F1-form-arrangement",
           "env_pin_sha256": ENV_PIN_SHA256, "prereg_path": str(PREREG), "prereg_sha256": _sha(PREREG), "chain_path": str(CHAIN), "chain_sha256": _sha(CHAIN),
           "eligible": eligible, "n_eligible": len(eligible), "excluded_disclosed": {"tempo_blocked": sorted(blocked), "landed_after_c84_rules_run": ["0e1e8f20592db366", "cc0693b4a24f64b2"]},
           "params": {"bars_per_block": BARS_PER_BLOCK, "similarity_threshold": SIM_THRESHOLD, "length_clip": [LEN_MIN, LEN_MAX], "pcp_duration_cap_beats": 1.0,
                      "feature_dims": {"pcp": 12, "drums": 48, "density": 6}, "group_weight": "1/sqrt(3)", "linkage": "single, deterministic"},
           "length_distribution": {str(k): v for k, v in sorted(lengths.items())}, "n_songs_in_transition_corpus": len(forms_for_transitions),
           "labels": labels_seen, "start_counts": dict(sorted(start.items())),
           "start_distribution": {k: round(v / sum(start.values()), 6) for k, v in sorted(start.items())} if start else {},
           "transition_counts": {a: dict(sorted(trans.get(a, {}).items())) for a in labels_seen}, "transition_probs": {a: {b: round(p, 6) for b, p in trans_probs[a].items()} for a in labels_seen},
           "repeat_A_probability": round(rep_a, 6) if rep_a is not None else None,
           "density_tercile_bounds": [round(t1, 6), round(t2, 6)], "n_blocks_total": len(all_block_dens), "per_label": per_label,
           "intro_density_quantile": round(intro_q, 6) if intro_q is not None else None,
           "boundary_fill_pool": fill_pool, "n_boundary_bars": len(boundary_bars), "fill_pool_fallback_used": fallback,
           "R1": {"focus_songs": r1, "pass": r1_pass, "fallback_template": list(FALLBACK_TEMPLATE) if not r1_pass else None},
           "per_song": per_song}
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    # c86 MINOR 2: the prereg gate is asserted on BOTH sides of the write (new output mtime must exceed the prereg mtime).
    assert out_p.stat().st_mtime > prereg_mtime, "PREREG_GATE: output mtime does not exceed the prereg mtime"
    print(f"lengths {out['length_distribution']}; labels {labels_seen}; start {out['start_distribution']}; repeat_A {out['repeat_A_probability']}; "
          f"terciles {out['density_tercile_bounds']}; intro_q {out['intro_density_quantile']}; fill pool {len(fill_pool)} (fallback {fallback}); R1 pass {r1_pass}")
    for lab, e in per_label.items():
        print(f"  {lab}: blocks {e['n_blocks']} terciles {e['density_tercile_probs']} region {e['harmony_region']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
