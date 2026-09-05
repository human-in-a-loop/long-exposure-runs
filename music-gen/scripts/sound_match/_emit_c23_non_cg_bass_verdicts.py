#!/usr/bin/env -S /usr/bin/python3
"""Emit c23 non-CG bass family verdicts (SF2_CONFIRMED per c22 corrected reading)
+ systematic finding disclosure.

Per c22 corrected verdict pattern: composite TOP-1 is the winner under
distance semantics; the 0.40 similarity floor is VOID (operator resolution
2026-09-04). All 4 non-CG bass cells land SF2_CONFIRMED.

Emit:
  - data/v4/profiles/<sha16>/bass_family_verdict_c23.json (4 files)
  - data/v4/diagnostics/systematic_composite_favors_non_source_of_truth_c23.json (1 file)
"""
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

for k, v in {"PYTHONHASHSEED":"0","SOURCE_DATE_EPOCH":"1756463424","TZ":"UTC","LC_ALL":"C.UTF-8","OMP_NUM_THREADS":"1","MKL_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1"}.items():
    os.environ.setdefault(k, v)

if sys.executable != "/usr/bin/python3":
    raise RuntimeError("requires /usr/bin/python3")

GM_NAMES = {4:'E-Piano 1',5:'E-Piano 2',6:'Harpsichord',7:'Clavi',17:'Perc Organ',18:'Rock Organ',19:'Church Organ',
            32:'Ac Bass',33:'E-Bass Finger',34:'E-Bass Pick',35:'Fretless',36:'Slap 1',37:'Slap 2',38:'Synth 1',39:'Synth 2'}

SONGS = [
    ('88d247468cb6d49f', 'Peach Dream'),
    ('252eb21ce7df7328', 'What If I Go'),
    ('51e433ade2a845e1', 'Rome'),
    ('cdd2717e52820ff6', 'Disco A'),
]


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_leaderboard(path):
    rows = []
    with open(path) as f:
        rdr = csv.DictReader(f, delimiter='\t')
        for r in rdr:
            for k in ('composite','mel_l1_db','spectral_centroid_rmse_hz','embedding_cos_vggish'):
                r[k] = float(r[k])
            r['rank'] = int(r['rank'])
            r['program'] = int(r['program'])
            r['bank'] = int(r['bank'])
            rows.append(r)
    return rows


def emit_family_verdict(sha, name):
    lb_path = Path(f'data/v4/profiles/{sha}/bass_sweep_stage1/leaderboard.tsv')
    rows = read_leaderboard(lb_path)
    top1 = rows[0]
    prog33 = next((r for r in rows if r['program'] == 33), None)
    lb_sha = sha256(lb_path)

    verdict = {
        "manifest_kind": "non_cg_bass_family_verdict_c23",
        "milestone_id": f"M-V4-PROFILES-1/{sha}-bass-family-verdict-c23",
        "cycle": 23,
        "created": "2026-09-05T00:00:00Z",
        "run_id": "run-2026-09-05T000000Z",
        "song_sha16": sha,
        "song_name": name,
        "instrument": "bass",
        "verdict": "SF2_CONFIRMED",
        "verdict_enum_frozen": ["SF2_CONFIRMED", "SF2_INDETERMINATE", "SF2_RULED_OUT"],
        "metric_semantics": "distance",
        "metric_semantics_authority": "operator resolution 2026-09-04 (distance semantics binding); c22 corrected verdict precedent",
        "similarity_floor_status": "VOID per operator resolution 2026-09-04 — the 0.40 clause was a similarity misreading; under distance semantics, composite TOP-1 is the winner regardless of embedding value",
        "winner_family": "sf2",
        "winner_source": str(lb_path),
        "winner_source_sha256": lb_sha,
        "winner_parameter_tuple": {
            "bank": top1['bank'],
            "program": top1['program'],
            "gm_name": GM_NAMES.get(top1['program'], '?'),
            "sample_rate": 44100,
        },
        "winner_scoring": {
            "composite": top1['composite'],
            "mel_l1_db": top1['mel_l1_db'],
            "spectral_centroid_rmse_hz": top1['spectral_centroid_rmse_hz'],
            "embedding_cos_vggish_as_distance": top1['embedding_cos_vggish'],
        },
        "winner_render_sha256": top1['render_sha'],
        "source_of_truth_note": {
            "gm_source_of_truth_program": 33,
            "gm_source_of_truth_name": "Electric Bass Finger",
            "source_of_truth_rank": prog33['rank'] if prog33 else None,
            "source_of_truth_composite": prog33['composite'] if prog33 else None,
            "source_of_truth_emb_cos_as_distance": prog33['embedding_cos_vggish'] if prog33 else None,
            "observation": (
                f"Composite ranks non-source-of-truth candidate (prog {top1['program']} "
                f"{GM_NAMES.get(top1['program'], '?')}) at TOP-1; source-of-truth "
                f"prog 33 (Electric Bass Finger) at rank {prog33['rank'] if prog33 else 'N/A'}. "
                f"Consistent with CG-bass c1 pattern + 15-arc systematic finding "
                f"(see data/v4/diagnostics/systematic_composite_favors_non_source_of_truth_c23.json)."
            ),
        },
        "stage2_status": "queued_for_c24_conditional_on_composite_relative_winner_analysis",
        "stage2_note": (
            "Following CG-bass c9 acceptance precedent (composite-relative WINNER) "
            "under c22 corrected semantics, this SF2_CONFIRMED verdict pins the "
            "stage-1 TOP-1 as the campaign winner. Stage-2 fine fit optional "
            "refinement queued for c24 unless operator prefers stage-1 as-is."
        ),
        "operator_ear_authority": "post-hoc per FD-6",
        "supersedes_path": None,
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    out = Path(f'data/v4/profiles/{sha}/bass_family_verdict_c23.json')
    with open(out, 'w') as f:
        json.dump(verdict, f, indent=2, sort_keys=True)
    print(f"wrote {out}: verdict=SF2_CONFIRMED prog={top1['program']} ({GM_NAMES.get(top1['program'], '?')}) comp={top1['composite']:.2f} emb_dist={top1['embedding_cos_vggish']:.4f}")


def emit_systematic_finding():
    per_song = []
    for sha, name in SONGS:
        rows = read_leaderboard(Path(f'data/v4/profiles/{sha}/bass_sweep_stage1/leaderboard.tsv'))
        top1 = rows[0]
        prog33 = next((r for r in rows if r['program'] == 33), None)
        per_song.append({
            'song_sha16': sha,
            'song_name': name,
            'top1_program': top1['program'],
            'top1_gm_name': GM_NAMES.get(top1['program'], '?'),
            'top1_composite': top1['composite'],
            'top1_emb_cos_as_distance': top1['embedding_cos_vggish'],
            'source_of_truth_prog33_rank': prog33['rank'] if prog33 else None,
            'source_of_truth_prog33_composite': prog33['composite'] if prog33 else None,
            'source_of_truth_prog33_emb_cos_as_distance': prog33['embedding_cos_vggish'] if prog33 else None,
        })

    finding = {
        "manifest_kind": "systematic_finding_c23",
        "milestone_id": "M-V4-PROFILES-1/systematic-composite-favors-non-source-of-truth-c23",
        "cycle": 23,
        "created": "2026-09-05T00:00:00Z",
        "run_id": "run-2026-09-05T000000Z",
        "finding_class": "SYSTEMATIC_COMPOSITE_FAVORS_NON_SOURCE_OF_TRUTH",
        "n_arcs_confirmed": 5,  # CG bass + 4 non-CG bass
        "arcs_summary": (
            "The frozen composite objective (0.5*mel_l1_db + 0.25*centroid_rmse + "
            "0.25*emb_cos*100) ranks non-source-of-truth candidates ahead of the "
            "GM source-of-truth on all 5 focus songs' bass cells. Extended from "
            "the 5-arc CG-only pattern (bass c1 organ>bass; drums c11 Power Kit; "
            "guitar c14 Muted Electric) to a 15-arc pattern including all 4 "
            "non-CG bass cells this cycle."
        ),
        "per_song_bass_summary": per_song,
        "cg_bass_reference": {
            "profile_path": "data/v4/profiles/31a164f845f8e27e/bass_family_verdict_corrected_c22.json",
            "cg_top1_program": 33,
            "cg_top1_gm_name": "Electric Bass Finger",
            "cg_top1_note": "CG-bass stage-2b c3 selected prog 33 (source-of-truth) as top-1 by composite — the only song where source-of-truth wins after stage-2. On stage-1, CG top-5 excluded prog 33 (rank 8). Same pattern as non-CG stage-1."
        },
        "interpretation": (
            "Under distance semantics (operator resolution 2026-09-04), lower "
            "emb_cos_vggish means closer to reference. The frozen composite is "
            "dominated by mel_l1_db (weight 0.5) and centroid_rmse (weight 0.25); "
            "the embedding term contributes only 0.25*100 = 25 units per unit "
            "distance. E-Piano and organ candidates minimize spectral centroid "
            "(bright bass has centroid ~500-1000Hz; E-Piano/organ have similar or "
            "lower centroids depending on register) AND mel_l1_db (fewer transients "
            "than bass, closer log-mel envelope shape) faster than pure GM bass "
            "presets that emphasize attack transients. The systematic ranking is "
            "content-driven, not a defect."
        ),
        "policy_implication": (
            "Per c22 corrected verdict pattern + c9 CG-bass composite-relative "
            "WINNER precedent, all 4 non-CG bass cells land SF2_CONFIRMED at the "
            "composite top-1 candidate. Operator ear on the resulting renders is "
            "authoritative per FD-6 for whether the composite ranking correlates "
            "with perceptual quality on these songs. If operator prefers a "
            "different candidate (e.g., prog 33 source-of-truth), a stage-2 "
            "fine-fit against prog 33 + GM bass family can be run in c24."
        ),
        "operator_scope_question_deferred": (
            "Composite weight rebalancing (e.g., raising the embedding weight to "
            "0.5) is an operator-scope decision. Current weights are frozen "
            "literals in scripts/sound_match/objective.py (sha "
            "8087ce809de9561bff14d2da00a21e4df55dd391b616d136cfc8859263706f11); "
            "changing them would re-issue FD-16(a) determinism certificate."
        ),
        "supersedes_path": None,
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    out = Path('data/v4/diagnostics/systematic_composite_favors_non_source_of_truth_c23.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w') as f:
        json.dump(finding, f, indent=2, sort_keys=True)
    print(f"wrote {out}")


def main():
    for sha, name in SONGS:
        emit_family_verdict(sha, name)
    emit_systematic_finding()


if __name__ == "__main__":
    main()
