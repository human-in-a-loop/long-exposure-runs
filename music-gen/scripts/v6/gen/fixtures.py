#!/usr/bin/python3
"""v6 Phase 2 — SMALL SYNTHETIC models in the exact v5 rule-file schemas + the single loader used for real files.

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

The corpus-trained files (data/v5/rules/harmony_markov_v5_full.json, groove_v5_v2_full.json, bass_pitch_v5.json,
melody_vomm_v5.json, velocity_profiles_v5.json, comping_v5.json, form_plan_v5.json, per_song_c84/<sha16>/harmony_v5.json)
do not exist yet (transcription pending). `build_fixtures()` returns in-memory models with the same keys the v5 scripts
write, so every composer module is testable now; `load_models()` reads the real files when present and falls back to the
fixtures per model only when asked (--fixtures). Fixture content is a plausible pop/soul language: a 13-state chain
(ii-V-I, IV-V-I, vi-IV-I-V tendencies, bVII, N), a backbeat groove, a root-heavy bass interval model and a stepwise melody
VOMM on degrees 0..6. Everything is deterministic (SHA-256 tags, no PRNG).
"""
from __future__ import annotations

from pathlib import Path

from scripts.v6.gen.common import WS, u, draw_from, read_json, sha_file, sha_text, canonical_json

FIXTURE_STATES = ["0:maj", "0:maj7", "10:maj", "2:min", "2:min7", "4:min", "5:maj", "5:maj7", "7:7", "7:maj", "9:min", "9:min7", "N"]
# segment-level (change-only) tendencies: from -> {to: count}
_TEND = {
    "0:maj": {"5:maj": 14, "9:min": 10, "7:maj": 8, "2:min": 6, "5:maj7": 4, "4:min": 4, "10:maj": 3, "0:maj7": 2, "7:7": 3, "N": 1},
    "0:maj7": {"2:min7": 8, "9:min7": 6, "5:maj7": 6, "4:min": 3, "7:7": 2},
    "10:maj": {"0:maj": 10, "5:maj": 5, "9:min": 2},
    "2:min": {"7:maj": 12, "7:7": 10, "5:maj": 3, "0:maj": 2, "9:min": 2},
    "2:min7": {"7:7": 14, "7:maj": 4, "0:maj7": 2, "9:min7": 2},
    "4:min": {"9:min": 8, "5:maj": 5, "2:min": 3, "0:maj": 2},
    "5:maj": {"7:maj": 12, "0:maj": 10, "7:7": 6, "2:min": 3, "9:min": 3, "4:min": 2},
    "5:maj7": {"7:7": 8, "0:maj7": 6, "2:min7": 3, "9:min7": 2},
    "7:7": {"0:maj": 20, "9:min": 5, "0:maj7": 4, "5:maj": 2, "2:min": 1},
    "7:maj": {"0:maj": 18, "9:min": 6, "5:maj": 4, "4:min": 2, "2:min": 1},
    "9:min": {"5:maj": 12, "2:min": 6, "0:maj": 4, "7:maj": 3, "4:min": 2, "10:maj": 2},
    "9:min7": {"2:min7": 8, "5:maj7": 6, "7:7": 2, "0:maj7": 2},
    "N": {"0:maj": 6, "5:maj": 2, "9:min": 2},
}
_HOLD_BEATS = {"0:maj": 6.0, "0:maj7": 5.0, "10:maj": 3.0, "2:min": 3.0, "2:min7": 3.0, "4:min": 3.0, "5:maj": 4.0, "5:maj7": 4.0,
               "7:7": 3.0, "7:maj": 3.0, "9:min": 4.0, "9:min7": 4.0, "N": 2.0}
FIXTURE_DONORS = {"fixture_a": {"tonic": 0, "mode": "major", "bpm": 100.0}, "fixture_b": {"tonic": 5, "mode": "major", "bpm": 120.0},
                  "fixture_c": {"tonic": 9, "mode": "major", "bpm": 152.0}}
FIXTURE_FILL_POOL = [{"snare": 0xF000, "hat": 0x5555, "count": 3}, {"snare": 0xD400 | 0x0010, "hat": 0x1111, "count": 2},
                     {"snare": 0xA800 | 0x1010, "hat": 0x5555, "count": 1}]


def _stationary(P: list, n_iter: int = 2000) -> list:
    n = len(P)
    pi = [1.0 / n] * n
    for _ in range(n_iter):
        nxt = [sum(pi[i] * P[i][j] for i in range(n)) for j in range(n)]
        s = sum(nxt)
        pi = [x / s for x in nxt]
    return pi


def fixture_chain() -> dict:
    states = list(FIXTURE_STATES)
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    Cs = [[0] * n for _ in range(n)]
    for a, row in _TEND.items():
        for b, c in row.items():
            Cs[idx[a]][idx[b]] = int(c)
    # beat-level counts: self-transitions scaled by the mean hold, plus the change counts
    C = [[0] * n for _ in range(n)]
    for i, s in enumerate(states):
        chg = sum(Cs[i])
        C[i][i] = int(round(chg * (_HOLD_BEATS[s] - 1.0)))
        for j in range(n):
            C[i][j] += Cs[i][j]
    P = [[(C[i][j] / sum(C[i])) if sum(C[i]) else 1.0 / n for j in range(n)] for i in range(n)]
    pi = _stationary(P)
    per_song = {d: {"key": {"tonic": m["tonic"], "mode": m["mode"], "tonic_name": None, "method": "fixture"}, "title": d, "n_beats": 128}
                for d, m in FIXTURE_DONORS.items()}
    return {"schema_version": 1, "kind": "fixture_harmony_chain", "states": states, "beat_level_counts": C,
            "beat_level_row_normalized": [[round(x, 6) for x in r] for r in P], "segment_level_counts": Cs,
            "stationary_distribution": {s: round(pi[idx[s]], 6) for s in states},
            "max_stationary_state": states[max(range(n), key=lambda i: (pi[i], -i))], "qualities": ["maj", "min", "7", "min7", "maj7", "9", "sus"],
            "chain_definition": "beat-level functional states (self-transitions included); unseen rows uniform; stationary by power iteration (2000 steps)",
            "gate": {"used": sorted(FIXTURE_DONORS)}, "per_song": per_song}


def fixture_chord_streams(chain: dict, n_beats: int = 128) -> dict:
    """Synthetic per-song beat-level chord streams (schema of per_song_c84/<sha16>/harmony_v5.json chord_stream)."""
    P = chain["beat_level_row_normalized"]
    states = chain["states"]
    out = {}
    for d in sorted(FIXTURE_DONORS):
        s = "0:maj"
        stream = []
        for b in range(n_beats):
            stream.append({"beat": b, "state": s})
            row = {t: P[states.index(s)][j] for j, t in enumerate(states)}
            s = draw_from(row, f"fixture_stream|{d}|{b}|{s}")
        out[d] = {"chord_stream": stream, "key": chain["per_song"][d]["key"]}
    return out


def _table(pairs: list, alpha: float = 0.5) -> dict:
    counts: dict = {}
    for ctx, out, c in pairs:
        counts.setdefault(ctx, {})
        counts[ctx][str(out)] = counts[ctx].get(str(out), 0) + int(c)
    vocab = sorted({o for row in counts.values() for o in row}, key=int)
    probs = {}
    for ctx, row in counts.items():
        n = sum(row.values())
        probs[ctx] = {o: (row.get(o, 0) + alpha) / (n + alpha * len(vocab)) for o in vocab}
    return {"counts": {k: dict(sorted(v.items())) for k, v in sorted(counts.items())}, "probs": {k: probs[k] for k in sorted(probs)},
            "vocab": vocab, "alpha": alpha, "n_contexts": len(counts), "n_singleton_contexts": 0, "n_pairs": sum(sum(r.values()) for r in counts.values())}


def fixture_groove() -> dict:
    """kick8 marginal + snare16|kick8 + hat16|kick8,snare16 + bass16|kick8 — a backbeat language (as groove_v5_v2_full.json)."""
    K1, K2, K3, K4 = 0x11, 0x19, 0x91, 0x55  # 1+3 / 1+and-of-2+3 / 1+3+4.5 / four on the floor
    SB, SBG, SB2 = 0x1010, 0x1010 | 0x0400, 0x1010 | 0x0080  # backbeat / +ghost on 3.5 / +pickup on 2.75
    H8, H4, H16 = 0x5555, 0x1111, 0xFFFF
    kick = [("*", K1, 10), ("*", K2, 8), ("*", K3, 5), ("*", K4, 6)]
    snare = [(str(K1), SB, 8), (str(K1), SBG, 3), (str(K2), SB, 6), (str(K2), SB2, 3), (str(K3), SB, 4), (str(K3), SBG, 2), (str(K4), SB, 5), (str(K4), SB2, 2)]
    hat = []
    for k in (K1, K2, K3, K4):
        for s in (SB, SBG, SB2):
            hat += [(f"{k}|{s}", H8, 6), (f"{k}|{s}", H4, 2), (f"{k}|{s}", H16, 2)]
    bass = [(str(K1), 0x0101, 6), (str(K1), 0x4101, 4), (str(K1), 0x1111, 3), (str(K2), 0x0109, 5), (str(K2), 0x4109, 3),
            (str(K3), 0x8101, 5), (str(K3), 0x0101, 3), (str(K4), 0x1111, 6), (str(K4), 0x5555, 2)]
    return {"schema_version": 1, "kind": "fixture_groove", "grid": {"slots_per_bar": 16, "kick_alphabet": "8-bit 8th-note mask", "other_alphabets": "16-bit 16th-note masks"},
            "model": {"kick_marginal": _table(kick), "snare_given_kick": _table(snare), "hat_given_kick_snare": _table(hat), "bass_given_kick": _table(bass)},
            "per_song": {}}


def fixture_bass_model() -> dict:
    order = ["root", "fifth", "octave", "third", "approach", "other"]
    base = {0: {"root": 40, "fifth": 6, "octave": 6, "third": 3, "approach": 1, "other": 2},
            1: {"root": 10, "fifth": 8, "octave": 6, "third": 4, "approach": 2, "other": 4},
            2: {"root": 16, "fifth": 10, "octave": 6, "third": 4, "approach": 2, "other": 3},
            3: {"root": 8, "fifth": 8, "octave": 6, "third": 3, "approach": 3, "other": 4}}
    cond, marg = {}, {c: 0 for c in order}
    for slot in range(4):
        for chg in (0, 1):
            cnt = dict(base[slot])
            if chg:
                cnt["approach"] += 12
            n = sum(cnt.values())
            cond[f"{slot}|{chg}"] = {"n": n, "counts": {c: cnt[c] for c in order}, "probs": {c: round((cnt[c] + 0.5) / (n + 3.0), 9) for c in order}}
            for c in order:
                marg[c] += cnt[c]
    n = sum(marg.values())
    return {"schema_version": 1, "kind": "fixture_bass_pitch_model", "class_order": order, "alpha": 0.5, "conditional": cond,
            "marginal": {"n": n, "counts": marg, "probs": {c: round((marg[c] + 0.5) / (n + 3.0), 9) for c in order}},
            "register": {"corpus": {"n": 0, "median": 38.0, "iqr_lo": 33.0, "iqr_hi": 43.0}}, "per_song": {}}


def fixture_melody_vomm() -> dict:
    """Order-3 VOMM over '<deg>|<ioi>' tokens trained on synthetic stepwise degree walks (scripts.v5.melody_vomm_v5.train_counts)."""
    from scripts.v5.melody_vomm_v5 import train_counts  # READ-ONLY pure helper
    seqs = []
    for k in range(12):
        deg, seq = 0, []
        for i in range(48):
            x = u(f"fixture_vomm|{k}|{i}")
            step = -1 if x < 0.36 else (1 if x < 0.72 else (2 if x < 0.82 else (-2 if x < 0.92 else 0)))
            deg = max(0, min(6, deg + step))
            ioi = (2, 4, 2, 4, 2, 2, 4, 8, 2, 4, 1, 2)[int(u(f"fixture_vomm|ioi|{k}|{i}") * 12) % 12]
            seq.append(f"{deg}|{ioi}")
        seqs.append(seq)
    counts = train_counts(seqs)
    return {"schema_version": 1, "kind": "fixture_melody_vomm", "max_order": 3, "counts": counts,
            "model": {"max_order": 3, "counts": counts}, "token": {"format": "<deg>|<ioi>"}}


def build_fixtures() -> dict:
    chain = fixture_chain()
    return {"chain": chain, "chord_streams": fixture_chord_streams(chain), "groove": fixture_groove(), "bass": fixture_bass_model(),
            "melody": fixture_melody_vomm(), "velocity": None, "comping": None, "form_plan": None, "fill_pool": FIXTURE_FILL_POOL,
            "sources": {k: "fixture" for k in ("chain", "chord_streams", "groove", "bass", "melody")}}


def fixtures_sha256() -> str:
    """Content hash of the in-memory fixtures (recorded in manifests for provenance)."""
    return sha_text(canonical_json(build_fixtures(), compact=True))


def load_models(rules_dir: Path | None, fixtures: bool, form_plan: Path | None = None, per_song_dir: Path | None = None) -> dict:
    """Real files from rules_dir; with `fixtures=True` the SYNTHETIC models are used for everything (hermetic, test-only),
    regardless of what exists on disk — pass fixtures=False (the CLI default) to compose on corpus-trained rules."""
    rd = Path(rules_dir) if rules_dir else WS / "data/v5/rules"
    files = {"chain": rd / "harmony_markov_v5_full.json", "groove": rd / "groove_v5_v2_full.json", "bass": rd / "bass_pitch_v5.json",
             "melody": rd / "melody_vomm_v5.json", "velocity": rd / "velocity_profiles_v5.json", "comping": rd / "comping_v5.json"}
    fx = build_fixtures() if fixtures else None
    out = {"sources": {}, "input_sha256": {}}
    for k, p in files.items():
        if fx is not None and fx.get(k) is not None:  # hermetic: fixtures win over disk when requested
            out[k] = fx[k]
            out["sources"][k] = "fixture"
        elif p.exists():
            out[k] = read_json(p)
            out["sources"][k] = str(p.relative_to(WS)) if p.is_absolute() and str(p).startswith(str(WS)) else str(p)
            out["input_sha256"][k] = sha_file(p)
        elif fx is not None and fx.get(k) is not None:
            out[k] = fx[k]
            out["sources"][k] = "fixture"
        else:
            out[k] = None
            out["sources"][k] = "absent"
    missing = [k for k in ("chain", "groove", "bass", "melody") if out[k] is None]
    if missing:
        raise FileNotFoundError(f"required models missing under {rd}: {missing} (pass --fixtures to use synthetic models)")
    fp = Path(form_plan) if form_plan else rd / "form_plan_v5.json"
    if fixtures and not form_plan:
        fp = Path("/nonexistent/fixture-mode-form-plan")  # fixed AABA in fixture mode unless --form-plan is explicit
    out["form_plan"] = read_json(fp) if fp.exists() else None
    out["sources"]["form_plan"] = str(fp) if fp.exists() else "absent (fixed AABA, 8 bars/section)"
    if fp.exists():
        out["input_sha256"]["form_plan"] = sha_file(fp)
    psd = Path(per_song_dir) if per_song_dir else rd / "per_song_c84"
    streams = {}
    if fixtures and not per_song_dir:
        psd = Path("/nonexistent/fixture-mode-per-song")
    if psd.exists():
        for hp in sorted(psd.glob("*/harmony_v5.json")):
            d = read_json(hp)
            streams[hp.parent.name] = {"chord_stream": [{"beat": e["beat"], "state": e["state"]} for e in d.get("chord_stream", [])], "key": d.get("key")}
        out["sources"]["chord_streams"] = str(psd)
    elif fx is not None:
        streams = fx["chord_streams"]
        out["sources"]["chord_streams"] = "fixture"
    else:
        out["sources"]["chord_streams"] = "absent (harmonic-rhythm prior)"
    out["chord_streams"] = streams
    out["fill_pool"] = (out["form_plan"] or {}).get("boundary_fill_pool") or FIXTURE_FILL_POOL
    out["fixtures_sha256"] = fixtures_sha256() if fixtures else None
    return out
