#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:15:00Z
# cycle: 30
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-semantic-cluster-overlap
# ---
"""Extract per-rule structural fingerprints from both rules ledgers.

For each rule row, emit a per-rule_type numeric feature vector suitable
for L2-normalization + cosine distance downstream. Vectors are
concatenations of typed fields per the frozen rubric.

Deterministic. No PRNG. SHA-256 tiebreak on any downstream ordering.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER_76 = ROOT / "data" / "rules" / "ledger.jsonl"
LEDGER_86 = ROOT / "data" / "rules" / "ledger_i3_dminor.jsonl"
OUT_TSV = ROOT / "data" / "collision_model" / "rule_structural_fingerprints.tsv"

RULE_TYPE_SHORT = {
    "harmonic": "H", "rhythmic": "R", "melodic": "M",
    "form": "F", "arrangement": "A",
}

# --- Fixed vocabularies (locked before any threshold computation). ---
ROMAN_VOCAB = ("I", "i", "II", "ii", "III", "iii", "IV", "iv",
               "V", "v", "VI", "vi", "VII", "vii")
CADENCE_VOCAB = ("none", "PAC", "IAC", "HC", "DC", "PC", "other")
PATTERN_VOCAB = ("kick", "snare", "hihat", "cymbal", "tom", "rest")
CONTOUR_VOCAB = ("arch", "ascending", "descending", "static", "undulating")
INSTR_VOCAB = ("drums", "bass", "other")

TONIC_PC = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10, "B": 11,
}


def _bag(tokens, vocab):
    counts = [0.0] * len(vocab)
    for t in tokens:
        tt = str(t)
        if tt in vocab:
            counts[vocab.index(tt)] += 1.0
    return counts


def _onehot(value, vocab):
    v = [0.0] * len(vocab)
    if value in vocab:
        v[vocab.index(value)] = 1.0
    return v


def _parse_key(key_str):
    """'F_major' → (pc, mode). Unknown → (-1, 'unknown')."""
    s = str(key_str)
    if "_" in s:
        tonic, mode = s.split("_", 1)
    else:
        tonic, mode = s, "major"
    pc = TONIC_PC.get(tonic, -1)
    mode = mode.lower()
    return pc, mode


def fp_harmonic(params):
    key = params.get("key", "C_major")
    pc, mode = _parse_key(key)
    tonic_oh = [0.0] * 12
    if 0 <= pc <= 11:
        tonic_oh[pc] = 1.0
    mode_oh = [1.0 if mode == "major" else 0.0,
               1.0 if mode == "minor" else 0.0]
    roman = list(params.get("chord_progression") or [])
    roman_bag = _bag(roman, ROMAN_VOCAB)
    cadence = str(params.get("cadence", "none"))
    cad_oh = _onehot(cadence if cadence in CADENCE_VOCAB else "other",
                     CADENCE_VOCAB)
    return tonic_oh + mode_oh + roman_bag + cad_oh


def fp_rhythmic(params):
    meter = str(params.get("meter", "4/4"))
    try:
        num, den = meter.split("/", 1)
        num_i, den_i = int(num), int(den)
    except Exception:
        num_i, den_i = 4, 4
    tempo = float(params.get("tempo_bpm", 120.0))
    tempo_r = float(round(tempo))
    pattern = list(params.get("pattern") or [])
    pat_bag = _bag(pattern, PATTERN_VOCAB)
    return [float(num_i), float(den_i), tempo_r] + pat_bag


def fp_melodic(params):
    contour = str(params.get("contour", "static"))
    cont_oh = _onehot(contour, CONTOUR_VOCAB)
    rng = float(params.get("range_semitones", 0))
    pch = list(params.get("pitch_class_histogram") or [0.0] * 12)
    # PCH already L1-normalized per schema; keep as-is.
    if len(pch) != 12:
        pch = (list(pch) + [0.0] * 12)[:12]
    return cont_oh + [rng] + [float(x) for x in pch]


def _canonicalize_labels(labels):
    """First-occurrence integer canonicalization: A,B,A,C → 0,1,0,2."""
    mapping = {}
    canon = []
    for lab in labels:
        if lab not in mapping:
            mapping[lab] = len(mapping)
        canon.append(mapping[lab])
    return canon


def fp_form(params):
    sections = list(params.get("sections") or [])
    n_sec = float(len(sections))
    starts = [float(s.get("start_measure", 0)) for s in sections]
    ends = [float(s.get("end_measure", 0)) for s in sections]
    labels = [str(s.get("label", "")) for s in sections]
    canon = _canonicalize_labels(labels)
    total_span = float(ends[-1] - starts[0]) if sections else 0.0
    mean_len = (sum(e - s for s, e in zip(starts, ends)) / len(sections)
                if sections else 0.0)
    # Distinct-label count.
    n_distinct = float(len(set(labels))) if sections else 0.0
    # Canonical-label histogram (first 8 slots — schema-typical section
    # counts are ≤ 8; overflow collapses to slot 7).
    hist = [0.0] * 8
    for c in canon:
        idx = c if c < 8 else 7
        hist[idx] += 1.0
    return [n_sec, total_span, mean_len, n_distinct] + hist


def _resample_L_inf(vec, n_out=8):
    """Piecewise-constant resample to n_out, then normalize by max
    (L∞). Deterministic; no PRNG."""
    if not vec:
        return [0.0] * n_out
    L = len(vec)
    if L == n_out:
        out = [float(x) for x in vec]
    else:
        out = []
        for i in range(n_out):
            # Nearest neighbor mapping i∈[0,n_out) → j∈[0,L).
            j = min(L - 1, (i * L) // n_out)
            out.append(float(vec[j]))
    m = max(abs(x) for x in out) if out else 0.0
    if m > 0:
        out = [x / m for x in out]
    return out


def fp_arrangement(params):
    instr = list(params.get("instrumentation") or [])
    instr_oh = [1.0 if k in instr else 0.0 for k in INSTR_VOCAB]
    density = list(params.get("density_over_time") or [])
    density_8 = _resample_L_inf(density, n_out=8)
    events = list(params.get("layer_events") or [])
    n_events = float(len(events))
    # per-op counts
    n_add = float(sum(1 for e in events if e.get("op") == "add"))
    n_rem = float(sum(1 for e in events if e.get("op") == "remove"))
    return instr_oh + density_8 + [n_events, n_add, n_rem]


FP_DISPATCH = {
    "harmonic": fp_harmonic,
    "rhythmic": fp_rhythmic,
    "melodic": fp_melodic,
    "form": fp_form,
    "arrangement": fp_arrangement,
}


def _read_ledger(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_all():
    outputs = []
    for source, path in (("76row", LEDGER_76), ("86row_i3", LEDGER_86)):
        rows = _read_ledger(path)
        for r in rows:
            rt = r["rule_type"]
            fn = FP_DISPATCH.get(rt)
            if fn is None:
                continue
            vec = fn(r.get("parameters", {}))
            outputs.append({
                "source_ledger": source,
                "rule_id": r["rule_id"],
                "rule_type": rt,
                "rule_type_short": RULE_TYPE_SHORT[rt],
                "fingerprint_vec": vec,
            })
    return outputs


def write_tsv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ("source_ledger\trule_type\trule_type_short\trule_id\t"
              "fingerprint_dim\tfingerprint_vec_json\n")
    lines = [header]
    # Sort by (source_ledger, rule_type, rule_id) for determinism.
    for r in sorted(rows, key=lambda x: (x["source_ledger"],
                                          x["rule_type"],
                                          x["rule_id"])):
        vec_json = json.dumps(r["fingerprint_vec"],
                              separators=(",", ":"))
        lines.append(
            f"{r['source_ledger']}\t{r['rule_type']}\t"
            f"{r['rule_type_short']}\t{r['rule_id']}\t"
            f"{len(r['fingerprint_vec'])}\t{vec_json}\n"
        )
    path.write_text("".join(lines))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = build_all()
    sha = write_tsv(rows, OUT_TSV)
    print(f"WROTE {OUT_TSV.relative_to(ROOT)}")
    print(f"rows={len(rows)} sha256={sha[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
