"""
Compute SI-SDR/SIR/SAR per (separator, mix, stem) against the M-SEP-1
synth ground truth, plus vocals false-positive energy and a naive-copy
baseline row.

Metric: mir_eval.separation.bss_eval_sources on mono-collapsed pairs,
length-aligned to min(len(ref), len(est)); labelled `sdr_db` in the TSV
per the fanout brief's column contract.

Interpreter: /usr/bin/python3.

Outputs:
    data/separation/results.tsv
    data/separation/results_bar_chart.png
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mir_eval
import numpy as np
import soundfile as sf

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = Path("/home/user/long-exposure-runs/music-gen")
MANIFEST = ROOT / "data/separation/synth_mix/manifest.json"
RUNS_ROOT = ROOT / "data/separation/runs"
RESULTS_TSV = ROOT / "data/separation/results.tsv"
RESULTS_PNG = ROOT / "data/separation/results_bar_chart.png"

SEPARATORS = ["htdemucs", "openunmix"]
STEMS = ["drums", "bass", "other", "vocals"]


def to_mono(y: np.ndarray) -> np.ndarray:
    return y.mean(axis=1) if y.ndim > 1 else y


def read_wav(path: Path) -> tuple[np.ndarray, int]:
    y, sr = sf.read(str(path), always_2d=True)
    return y.astype(np.float64), sr


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2) + 1e-30))


def energy_dbfs(x: np.ndarray) -> float:
    return 20.0 * np.log10(rms(x) + 1e-12)


def bss_scalar(ref_mono: np.ndarray, est_mono: np.ndarray) -> tuple[float, float, float]:
    if np.max(np.abs(ref_mono)) < 1e-9 or np.max(np.abs(est_mono)) < 1e-9:
        return float("nan"), float("nan"), float("nan")
    sdr, sir, sar, _ = mir_eval.separation.bss_eval_sources(
        ref_mono[np.newaxis, :], est_mono[np.newaxis, :]
    )
    return float(sdr[0]), float(sir[0]), float(sar[0])


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    rows: list[dict] = []

    for mix in manifest["mixes"]:
        mix_id = mix["mix_id"]
        gt_stems = {
            "drums": ROOT / mix["stems"]["drums"]["path"],
            "bass":  ROOT / mix["stems"]["bass"]["path"],
            "other": ROOT / mix["stems"]["other"]["path"],
            "vocals": ROOT / mix["stems"]["vocals"]["path"],
        }
        mix_wav_path = ROOT / mix["mix"]["path"]
        mix_y, sr = read_wav(mix_wav_path)
        assert sr == 44100
        mix_mono = to_mono(mix_y)

        # Naive-copy baseline: est = mix / 3 (unrelated to vocals; GT vocals is zeros).
        naive_est_mono = mix_mono / 3.0
        for stem in STEMS:
            ref_y, sr_ref = read_wav(gt_stems[stem])
            assert sr_ref == sr
            ref_mono = to_mono(ref_y)
            n = min(len(ref_mono), len(naive_est_mono))
            if stem == "vocals":
                # GT zero — energy of naive est is meaningful, SI-SDR undefined
                sdr, sir, sar = float("nan"), float("nan"), float("nan")
                edbfs = energy_dbfs(naive_est_mono[:n])
            else:
                sdr, sir, sar = bss_scalar(ref_mono[:n], naive_est_mono[:n])
                edbfs = energy_dbfs(naive_est_mono[:n])
            rows.append(dict(separator="naive_copy_third", mix_id=mix_id, stem=stem,
                             sdr_db=sdr, sir_db=sir, sar_db=sar, est_energy_dBFS=edbfs))

        # Each real separator
        for sep in SEPARATORS:
            run_dir = RUNS_ROOT / sep / mix_id
            for stem in STEMS:
                est_path = run_dir / f"{stem}.wav"
                est_y, sr_est = read_wav(est_path)
                assert sr_est == sr, f"{est_path} sr {sr_est} != {sr}"
                est_mono = to_mono(est_y)
                ref_y, _ = read_wav(gt_stems[stem])
                ref_mono = to_mono(ref_y)
                n = min(len(ref_mono), len(est_mono))
                if stem == "vocals":
                    sdr, sir, sar = float("nan"), float("nan"), float("nan")
                    edbfs = energy_dbfs(est_mono[:n])
                else:
                    sdr, sir, sar = bss_scalar(ref_mono[:n], est_mono[:n])
                    edbfs = energy_dbfs(est_mono[:n])
                rows.append(dict(separator=sep, mix_id=mix_id, stem=stem,
                                 sdr_db=sdr, sir_db=sir, sar_db=sar, est_energy_dBFS=edbfs))

    # Write TSV
    RESULTS_TSV.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_TSV.open("w") as fh:
        fh.write("separator\tmix_id\tstem\tsdr_db\tsir_db\tsar_db\test_energy_dBFS\n")
        for r in rows:
            def fmt(v: float) -> str:
                return f"{v:.3f}" if np.isfinite(v) else "nan"
            fh.write(f"{r['separator']}\t{r['mix_id']}\t{r['stem']}\t"
                     f"{fmt(r['sdr_db'])}\t{fmt(r['sir_db'])}\t{fmt(r['sar_db'])}\t"
                     f"{fmt(r['est_energy_dBFS'])}\n")

    # Print summary
    print(f"\nWrote {len(rows)} rows -> {RESULTS_TSV.relative_to(ROOT)}\n")
    hdr = f"{'separator':<18}{'mix':<12}{'stem':<8}{'sdr_dB':>10}{'sir_dB':>10}{'sar_dB':>10}{'est_dBFS':>10}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        def fmt(v: float) -> str:
            return f"{v:>10.2f}" if np.isfinite(v) else f"{'nan':>10}"
        print(f"{r['separator']:<18}{r['mix_id']:<12}{r['stem']:<8}"
              f"{fmt(r['sdr_db'])}{fmt(r['sir_db'])}{fmt(r['sar_db'])}{fmt(r['est_energy_dBFS'])}")

    # Bar chart: per-stem sdr_db grouped by separator, averaged across mixes.
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_stems = ["drums", "bass", "other"]  # vocals excluded (GT=0, SDR nan)
    seps = SEPARATORS + ["naive_copy_third"]
    x = np.arange(len(plot_stems))
    w = 0.25
    for i, sep in enumerate(seps):
        vals = []
        for stem in plot_stems:
            xs = [r["sdr_db"] for r in rows if r["separator"] == sep and r["stem"] == stem and np.isfinite(r["sdr_db"])]
            vals.append(float(np.mean(xs)) if xs else float("nan"))
        ax.bar(x + (i - 1) * w, vals, w, label=sep)
    ax.set_xticks(x)
    ax.set_xticklabels(plot_stems)
    ax.set_ylabel("SDR (dB) — mean across {30, 60, 90}s mixes")
    ax.set_title("M-SEP-1: per-stem SDR by separator (higher is better; naive-copy = mix/3)")
    ax.axhline(0, color="k", lw=0.5)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_PNG, dpi=120)
    print(f"\nWrote bar chart -> {RESULTS_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
