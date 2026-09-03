#!/usr/bin/env python3
"""Stage-checkpointed unified driver — c24 sibling to c22 `recreate_v3.py`.

Composes c22 stage_* functions with the content-addressed cache in
`stage_cache.py`. See docs/v3_spine_stage_checkpointed_driver_spec.md.

The c22 driver + pipeline module are READ-ONLY anchors — this file imports
their stage_* callables verbatim and adds a cache-check/record wrapper.

Usage (mirrors c22):

    /usr/bin/python3 scripts/v3_spine/recreate_v3_checkpointed.py \
        --song 88d247468cb6d49f --section operator \
        --cycle 24 --verify-det \
        --out data/v3/deliveries/88d247468cb6d49f/cycle24/

Add `--no-cache` to force-invalidate every cache probe (reserved for the
ledger-required two-fresh-runs byte-determinism proof).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"interpreter guard: expected /usr/bin/python3, got {sys.executable}")

# Path-in imports for the c22 pipeline
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# Import c22 stage_* functions verbatim (READ-ONLY anchor)
import recreate_v3 as _c22  # noqa: E402
from v3_pipeline.env_pin import write_env_pin  # noqa: E402
import stage_cache  # noqa: E402


STAGE_ORDER = ["slice", "rehtdemucs", "muscriptor", "tempo_map",
               "canonicalize", "merge", "render", "mix_match", "panel"]


def _env_pin_sha(work_dir: Path) -> str:
    """Materialize env pins to a tmp file and return the manifest's self-anchor SHA."""
    ep = work_dir / "env_pin.json"
    write_env_pin(ep)
    body = json.loads(ep.read_text())
    return body["env_pin_sha256"]


def _rehydrate_stage_outputs(m: dict[str, Any], dst_root: Path) -> None:
    """Copy every file in the cached manifest's outputs/ back into work-dir layout."""
    src_root = m["_cache_dir"] / "outputs"
    for relpath in m["outputs"]:
        src = src_root / relpath
        dst = dst_root / relpath
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)


def run_pipeline_checkpointed(song_sha16: str, section: str, out_dir: Path,
                              cycle: int, verify_det: bool = True,
                              use_cache: bool = True) -> dict[str, Any]:
    facts = _c22.load_song_facts(song_sha16, section)
    work_dir = Path(f"data/v3_spine/{song_sha16}/operator_section_c{cycle}_checkpointed")
    work_dir.mkdir(parents=True, exist_ok=True)
    env_sha = _env_pin_sha(work_dir)

    report: dict[str, Any] = {
        "driver": "recreate_v3_checkpointed.py",
        "cycle": cycle,
        "song_sha16": song_sha16,
        "facts": facts,
        "verify_det": verify_det,
        "use_cache": use_cache,
        "env_pin_sha256": env_sha,
        "stages": {},
        "cache_summary": {"stages_hit": 0, "stages_miss": 0, "wall_saved_seconds": 0.0},
    }

    print(f"=== recreate_v3_checkpointed song={song_sha16} "
          f"section=[{facts['t_start_s']:.2f}..{facts['t_end_s']:.2f}]s "
          f"env_pin={env_sha[:12]} cache={'on' if use_cache else 'OFF'} ===")

    def _run_with_cache(stage_name: str, inputs: dict[str, Any],
                        run_fn, produced_layout: dict[str, Path]) -> tuple[Any, bool]:
        """Common wrapper: check cache, run if miss, record on success.

        Returns (stage_result_dict_or_none, cache_hit_bool). run_fn returns the
        stage's report dict directly. produced_layout maps relative-cache-path
        → absolute path where the stage writes its output.
        """
        m = stage_cache.check(stage_name, inputs, env_sha, work_dir) if use_cache else None
        if m is not None:
            print(f"[stage {stage_name}] CACHE HIT key={m['input_key'][:12]}"
                  f" ({len(m['outputs'])} outputs, saved ~{m.get('wall_seconds', 0.0):.1f}s)")
            _rehydrate_stage_outputs(m, work_dir)
            report["cache_summary"]["stages_hit"] += 1
            report["cache_summary"]["wall_saved_seconds"] += m.get("wall_seconds", 0.0)
            res = m.get("result")
            return (res if isinstance(res, dict) else m), True
        t0 = time.time()
        stage_out = run_fn()
        wall = time.time() - t0
        # Only cache when every produced file exists (defensive; do not cache partial)
        real = {k: v for k, v in produced_layout.items() if Path(v).is_file()}
        if real:
            stage_cache.record(stage_name, inputs, env_sha, work_dir, real, wall,
                               result=stage_out if isinstance(stage_out, dict) else None)
        report["cache_summary"]["stages_miss"] += 1
        return stage_out, False

    # 1. slice
    section_wav = work_dir / "section.wav"
    _, hit = _run_with_cache(
        "slice",
        {"audio_path": Path(facts["audio_path"]),
         "t_start_s": facts["t_start_s"], "t_dur_s": facts["t_dur_s"]},
        lambda: {"section_wav_sha256":
                 _c22.stage_slice(Path(facts["audio_path"]),
                                  facts["t_start_s"], facts["t_dur_s"], section_wav)},
        {"section.wav": section_wav},
    )
    report["stages"]["slice"] = {"cache_hit": hit,
                                  "section_wav_sha256": _c22.sha(section_wav)}

    # 2. rehtdemucs
    stem_dir = work_dir / "rc9_6stem"
    _, hit = _run_with_cache(
        "rehtdemucs",
        {"section_wav": section_wav},
        lambda: _c22.stage_rehtdemucs(section_wav, stem_dir,
                                       work_dir / "htdemucs_determinism.json",
                                       verify_det=verify_det),
        # 6-stem outputs: enumerate after run (cache-record only files that exist)
        {f"rc9_6stem/{n}.wav": stem_dir / f"{n}.wav"
         for n in ("drums", "bass", "other", "vocals", "guitar", "piano")},
    )
    report["stages"]["rehtdemucs"] = {"cache_hit": hit,
                                       "stems_present": sorted(
                                           p.name for p in stem_dir.glob("*.wav"))
                                       if stem_dir.is_dir() else []}

    # 3. muscriptor
    ms_dir = work_dir / "muscriptor"
    _, hit = _run_with_cache(
        "muscriptor",
        {**{f"stem_{n}": stem_dir / f"{n}.wav" for n in
            ("drums", "bass", "other", "vocals", "guitar", "piano")
            if (stem_dir / f"{n}.wav").is_file()},
         "section_wav": section_wav},
        lambda: _c22.stage_muscriptor(section_wav, stem_dir, ms_dir, verify_det=verify_det),
        # JSON outputs are small and content-addressed: cache them (2026-09-03 fix)
        {f"muscriptor/{n}.json": ms_dir / f"{n}.json"
         for n in ("drums", "bass", "other", "vocals", "guitar", "piano", "full_mix")},
    )
    report["stages"]["muscriptor"] = {"cache_hit": hit}

    # 4. tempo_map
    tempo_json = work_dir / "tempo_choice.json"
    tempo_result, hit = _run_with_cache(
        "tempo_map",
        {"section_wav": section_wav, "drums": stem_dir / "drums.wav"},
        lambda: _c22.stage_tempo_map(section_wav, stem_dir / "drums.wav", tempo_json),
        {"tempo_choice.json": tempo_json},
    )
    report["stages"]["tempo_map"] = {"cache_hit": hit}
    tempo = tempo_result if isinstance(tempo_result, dict) and "bpm" in tempo_result \
            else json.loads(tempo_json.read_text())

    # 5. canonicalize
    canon_dir = work_dir / "canonical_midi"
    _, hit = _run_with_cache(
        "canonicalize",
        {"muscriptor_dir_present": ms_dir.is_dir(), "tempo_bpm": tempo.get("bpm")},
        lambda: _c22.stage_canonicalize(ms_dir, tempo, canon_dir, verify_det=verify_det),
        {},  # produces many files; leave to freshness re-run if invalidated
    )
    canon = _ if isinstance(_, dict) else {"cache_hit": hit}
    report["stages"]["canonicalize"] = {"cache_hit": hit}

    # 6. merge
    merged_mid = work_dir / "merged.mid"
    merge_result, hit = _run_with_cache(
        "merge",
        {"canon_dir_present": canon_dir.is_dir(), "tempo_bpm": tempo.get("bpm")},
        lambda: _c22.stage_merge(canon_dir, tempo, merged_mid),
        {"merged.mid": merged_mid},
    )
    report["stages"]["merge"] = {"cache_hit": hit,
                                  "merged_mid_sha256": _c22.sha(merged_mid)
                                  if merged_mid.is_file() else None}
    # A cache hit from a pre-result-persistence record lacks the stage report;
    # stage_merge is cheap (<1s) and deterministic, so re-derive it in that case.
    if not (isinstance(merge_result, dict) and "merged_mid_sha256" in merge_result):
        merge_result = _c22.stage_merge(canon_dir, tempo, merged_mid)
    merge = merge_result

    # 7. render_per_track
    render_dir = work_dir / "render" / "per_track"
    _, hit = _run_with_cache(
        "render",
        {"merged_mid": merged_mid,
         "stems_present": sorted(p.name for p in stem_dir.glob("*.wav"))
         if stem_dir.is_dir() else []},
        lambda: _c22.stage_render(merged_mid, stem_dir, render_dir, verify_det=verify_det),
        {},  # per-track WAV set is variable
    )
    report["stages"]["render"] = {"cache_hit": hit}

    # 8. mix_match
    mix_wav = work_dir / "render" / "full_reconstruction.wav"
    _, hit = _run_with_cache(
        "mix_match",
        {"render_dir_present": render_dir.is_dir(),
         "stems_present": sorted(p.name for p in stem_dir.glob("*.wav"))
         if stem_dir.is_dir() else []},
        lambda: _c22.stage_mix_match(stem_dir, render_dir, mix_wav, verify_det=verify_det),
        {"render/full_reconstruction.wav": mix_wav},
    )
    report["stages"]["mix_match"] = {"cache_hit": hit,
                                      "full_reconstruction_sha256": _c22.sha(mix_wav)
                                      if mix_wav.is_file() else None}

    # 9. panel + delivery — delivery assembly is not cached (it copies into out_dir).
    manifest = _c22.assemble_delivery(facts, work_dir, out_dir, cycle,
                                        tempo, canon if isinstance(canon, dict) else {},
                                        merge)
    panel = _c22.stage_panel(out_dir / "original_ab.wav",
                              out_dir / "reconstruction_ab.wav",
                              out_dir / "panel.json", out_dir / "panel.tsv")
    report["stages"]["panel"] = {"cache_hit": False, "panel": panel}
    report["manifest"] = manifest
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Checkpointed unified v3 driver")
    ap.add_argument("--song", required=True, help="song_sha16 (16-hex)")
    ap.add_argument("--section", default="operator", choices=["operator", "auto"])
    ap.add_argument("--cycle", type=int, required=True)
    ap.add_argument("--out", type=Path, default=None,
                    help="delivery dir (default: data/v3/deliveries/<sha16>/cycle<N>/)")
    ap.add_argument("--verify-det", action="store_true",
                    help="enforce byte-determinism ×2 on stages that support it")
    ap.add_argument("--no-cache", action="store_true",
                    help="force-invalidate every cache probe (fresh full re-run)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report-json", type=Path, default=None,
                    help="write end-of-run report JSON here")
    args = ap.parse_args()

    if args.section == "auto":
        raise NotImplementedError("--section auto: deferred to a future cycle")

    out_dir = args.out or Path(f"data/v3/deliveries/{args.song}/cycle{args.cycle}/")
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(f"DRY RUN: would run checkpointed pipeline for song={args.song} "
              f"cycle={args.cycle} out={out_dir}")
        return 0

    report = run_pipeline_checkpointed(
        song_sha16=args.song, section=args.section,
        out_dir=out_dir, cycle=args.cycle,
        verify_det=args.verify_det, use_cache=not args.no_cache,
    )
    rjson = args.report_json or (out_dir / "checkpointed_run_report.json")
    rjson.write_text(json.dumps(report, sort_keys=True, indent=2, default=str))
    cs = report["cache_summary"]
    print(f"=== DONE stages_hit={cs['stages_hit']} stages_miss={cs['stages_miss']} "
          f"wall_saved~{cs['wall_saved_seconds']:.1f}s report={rjson} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
