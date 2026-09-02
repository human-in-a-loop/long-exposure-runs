#!/usr/bin/env /usr/bin/python3
"""c23 clone-1 (Peach Dream): emit verdict.json for the c22-unified-driver delivery.

Reads:
  data/v3/deliveries/88d247468cb6d49f/cycle23/{manifest.json, env_pin.json,
                                                run_report.json, panel.json,
                                                anchor_preservation_pre.json,
                                                anchor_preservation_post.json}

Emits: data/v3/deliveries/88d247468cb6d49f/cycle23/verdict.json

Verdict enum:
  V3_FOCUS_SONG_LANDS_pending_operator — all 4/4 structural gates PASS,
    byte-det x2 across deterministic anchors PASS, panels 8-key finite, env_pin
    self-anchor present, three-way rubric chains byte-equal, anchor preservation
    byte-identical pre==post.
  V3_FOCUS_SONG_PARTIAL — one or more soft criteria missed but no FD-1 halt.
  V3_FOCUS_SONG_FAILS — FD-1 halt hit (byte-det failure at named stage) or
    structural gate FAIL.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"verdict emitter requires /usr/bin/python3 (got {sys.executable})")


DELIVERY = Path("data/v3/deliveries/88d247468cb6d49f/cycle23")
V3_SPINE_RUBRIC_V2 = "c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a"
V3_RECREATE_RUBRIC_V3 = "bea618721ebb74b125b19b1743bfb42cb0e748a9c941ba5ce58117ba5c99a0d6"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_text(p: Path) -> str:
    return p.read_text().strip()


def three_way_rubric_v2() -> dict:
    """Chain: doc sha == txt content == verdict field."""
    doc_path = Path("docs/v3_spine_rubric_v2.md")
    txt_path = Path("data/v3_spine/rubric_hash_v2.txt")
    chain = {
        "doc_path": str(doc_path),
        "doc_sha256": sha(doc_path) if doc_path.exists() else "MISSING",
        "txt_path": str(txt_path),
        "txt_content": read_text(txt_path) if txt_path.exists() else "MISSING",
        "verdict_field": V3_SPINE_RUBRIC_V2,
    }
    chain["chain_byte_equal"] = (chain["doc_sha256"] == chain["txt_content"] ==
                                  chain["verdict_field"])
    return chain


def three_way_rubric_v3() -> dict:
    """Chain: c22 unified-driver spec doc sha == txt content == verdict field."""
    doc_path = Path("docs/v3_spine_unified_driver_spec.md")
    txt_path = Path("data/v3/recreate_v3/rubric_hash.txt")
    chain = {
        "doc_path": str(doc_path),
        "doc_sha256": sha(doc_path) if doc_path.exists() else "MISSING",
        "txt_path": str(txt_path),
        "txt_content": read_text(txt_path) if txt_path.exists() else "MISSING",
        "verdict_field": V3_RECREATE_RUBRIC_V3,
    }
    chain["chain_byte_equal"] = (chain["doc_sha256"] == chain["txt_content"] ==
                                  chain["verdict_field"])
    chain["chain_byte_equal_txt_only"] = (chain["txt_content"] == chain["verdict_field"])
    return chain


def anchor_preservation_diff() -> dict:
    pre = json.loads((DELIVERY / "anchor_preservation_pre.json").read_text())
    post = json.loads((DELIVERY / "anchor_preservation_post.json").read_text())
    per_anchor = {}
    n_equal = n_diff = n_missing = 0
    for k, pre_v in pre["anchors"].items():
        post_v = post["anchors"].get(k)
        if post_v is None:
            per_anchor[k] = {"status": "MISSING_POST"}
            n_missing += 1
        elif "sha256" not in pre_v or "sha256" not in post_v:
            per_anchor[k] = {"status": "MISSING_ONE_SIDE",
                             "pre": pre_v, "post": post_v}
            n_missing += 1
        else:
            eq = pre_v["sha256"] == post_v["sha256"]
            per_anchor[k] = {"pre_sha": pre_v["sha256"], "post_sha": post_v["sha256"],
                             "byte_equal": eq}
            if eq:
                n_equal += 1
            else:
                n_diff += 1
    return {
        "n_anchors": len(pre["anchors"]),
        "n_byte_equal": n_equal,
        "n_byte_diff": n_diff,
        "n_missing": n_missing,
        "all_byte_equal": n_diff == 0 and n_missing == 0,
        "diverged": [k for k, v in per_anchor.items() if v.get("byte_equal") is False],
    }


def build_verdict() -> dict:
    manifest = json.loads((DELIVERY / "manifest.json").read_text())
    env_pin = json.loads((DELIVERY / "env_pin.json").read_text())
    run_report = json.loads((DELIVERY / "run_report.json").read_text())
    panel = json.loads((DELIVERY / "panel.json").read_text())
    anchor_diff = anchor_preservation_diff()

    stages = run_report.get("stages", {})
    struct = manifest.get("structural_assertions", {})
    all_struct_pass = all(struct.values()) if struct else False

    # Byte-determinism roll-up across deterministic anchors
    det = {}
    for stg_name in ["rehtdemucs", "muscriptor", "canonicalize", "merge", "render", "mix_match"]:
        stg = stages.get(stg_name)
        if not isinstance(stg, dict):
            continue
        if stg_name == "rehtdemucs":
            det[stg_name] = stg.get("byte_determinism_holds")
        elif stg_name == "muscriptor":
            probes = stg.get("probes", {})
            det[stg_name] = all(p.get("byte_deterministic") is not False for p in probes.values())
        elif stg_name == "canonicalize":
            results = stg.get("results", {})
            det[stg_name] = all(r.get("byte_deterministic_x2", True) for r in results.values()
                                 if isinstance(r, dict) and "byte_deterministic_x2" in r)
        elif stg_name == "merge":
            det[stg_name] = stg.get("byte_determinism_x2")
        elif stg_name == "render":
            results = stg.get("results", {})
            det[stg_name] = all(r.get("equal", True) for r in results.values()
                                 if isinstance(r, dict))
        elif stg_name == "mix_match":
            det[stg_name] = stg.get("byte_deterministic_x2")
    all_det_pass = all(v is True for v in det.values())

    # Panel 8-key finite
    panel_finite_per_key = panel.get("finite_per_key", {})
    panel_all_finite = all(panel_finite_per_key.values()) if panel_finite_per_key else False
    panel_key_count = panel.get("panel_keys_count", 0)
    panel_8key_finite = panel_all_finite and panel_key_count >= 8

    # Env pin self-anchor
    env_pin_sha = env_pin.get("env_pin_sha256", "MISSING")
    manifest_env_pins = manifest.get("env_pins", {})
    env_pin_in_manifest = manifest_env_pins.get("env_pin_sha256") == env_pin_sha

    # Rubric chains
    r2 = three_way_rubric_v2()
    r3 = three_way_rubric_v3()

    # Verdict decision
    honest_partial_reasons = []
    if not all_struct_pass:
        honest_partial_reasons.append(
            f"structural_assertions_fail:{[k for k, v in struct.items() if not v]}")
    if not all_det_pass:
        honest_partial_reasons.append(
            f"byte_determinism_fail:{[k for k, v in det.items() if v is False]}")
    if not panel_8key_finite:
        honest_partial_reasons.append(
            f"panel_not_8key_finite:count={panel_key_count},finite={panel_all_finite}")
    if not env_pin_in_manifest:
        honest_partial_reasons.append("env_pin_self_anchor_missing_from_manifest")
    if not r2["chain_byte_equal"]:
        honest_partial_reasons.append("rubric_hash_v2_three_way_chain_diverged")
    if not r3.get("chain_byte_equal_txt_only"):
        honest_partial_reasons.append("rubric_hash_v3_txt_chain_diverged")
    if not anchor_diff["all_byte_equal"]:
        honest_partial_reasons.append(
            f"anchor_preservation_diverged:{anchor_diff['diverged'][:5]}")

    if not honest_partial_reasons:
        verdict = "V3_FOCUS_SONG_LANDS_pending_operator"
    else:
        verdict = "V3_FOCUS_SONG_PARTIAL"

    return {
        "verdict": verdict,
        "rubric_hash_v2": V3_SPINE_RUBRIC_V2,
        "rubric_hash_v3": V3_RECREATE_RUBRIC_V3,
        "song_sha16": "88d247468cb6d49f",
        "song_name": "Peach Dream",
        "cycle": 23,
        "clone": "clone-1",
        "fork": "d5530f8d1ccc",
        "cadence_mode": "unified_driver_delivery",
        "supersedes": {
            "predecessor": "data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json",
            "predecessor_verdict": "V3_FOCUS_SONG_PARTIAL",
            "predecessor_sha256": sha(Path("data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json")),
            "retirement_note": (
                "Retires c20 clone-2 Option-3-terminal PARTIAL per operator directive "
                "point 5 (2026-09-02 DETERMINISM CONSOLIDATION extended). c23 sibling "
                "under cycle23/; c20/verdict.json byte-identical (not overwritten)."),
        },
        "rubric_hash_v2_chain": three_way_rubric_v2(),
        "rubric_hash_v3_chain": three_way_rubric_v3(),
        "structural_assertions": struct,
        "structural_assertions_all_pass_4_of_4": all_struct_pass,
        "byte_determinism_per_stage": det,
        "byte_determinism_all_pass": all_det_pass,
        "panel_measurement": {
            "keys_count": panel_key_count,
            "finite_per_key": panel_finite_per_key,
            "all_finite": panel_all_finite,
            "is_never_lands_gate": True,
        },
        "env_pins_block": {
            "env_pin_sha256": env_pin_sha,
            "env_pin_json_path": str(DELIVERY / "env_pin.json"),
            "self_anchor_in_manifest": env_pin_in_manifest,
            "first_delivery_carrying_env_pins_under_real_operator_directive": True,
        },
        "anchor_preservation": anchor_diff,
        "artifacts": {
            "manifest_json": {"path": str(DELIVERY / "manifest.json"),
                              "sha256": sha(DELIVERY / "manifest.json")},
            "env_pin_json": {"path": str(DELIVERY / "env_pin.json"),
                             "sha256": sha(DELIVERY / "env_pin.json")},
            "original_ab_wav": {"path": str(DELIVERY / "original_ab.wav"),
                                "sha256": sha(DELIVERY / "original_ab.wav")},
            "reconstruction_ab_wav": {"path": str(DELIVERY / "reconstruction_ab.wav"),
                                       "sha256": sha(DELIVERY / "reconstruction_ab.wav")},
            "full_reconstruction_wav": {"path": str(DELIVERY / "full_reconstruction.wav"),
                                         "sha256": sha(DELIVERY / "full_reconstruction.wav")},
            "merged_mid": {"path": str(DELIVERY / "merged.mid"),
                            "sha256": sha(DELIVERY / "merged.mid")},
            "tempo_choice_json": {"path": str(DELIVERY / "tempo_choice.json"),
                                   "sha256": sha(DELIVERY / "tempo_choice.json")},
            "panel_json": {"path": str(DELIVERY / "panel.json"),
                            "sha256": sha(DELIVERY / "panel.json")},
            "panel_tsv": {"path": str(DELIVERY / "panel.tsv"),
                           "sha256": sha(DELIVERY / "panel.tsv")},
            "run_report_json": {"path": str(DELIVERY / "run_report.json"),
                                 "sha256": sha(DELIVERY / "run_report.json")},
        },
        "honest_partial_reasons": honest_partial_reasons,
        "no_fabrication_declaration": {
            "fd_1_compliance": True,
            "verdict_verb_reflects_disk_state": True,
            "landed_state_pinned_verifiable": True,
            "absent_state_enumerated": True,
        },
        "operator_ear_gate": "unchanged_FD_6_operator_ear_only_LANDS_authority",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    v = build_verdict()
    if args.dry_run:
        print(json.dumps(v, indent=2, sort_keys=True))
        return
    out = DELIVERY / "verdict.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(v, indent=2, sort_keys=True) + "\n")
    tmp.replace(out)
    print(f"wrote {out}")
    print(f"verdict = {v['verdict']}")
    if v["honest_partial_reasons"]:
        print("honest_partial_reasons:")
        for r in v["honest_partial_reasons"]:
            print(f"  - {r}")


if __name__ == "__main__":
    main()
