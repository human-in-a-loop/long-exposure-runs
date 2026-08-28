#!/usr/bin/env -S /usr/bin/python3
"""Evaluate the classifier on the M-CLASS-1 validation set.

Outputs:
  data/classifier/predictions.jsonl
  data/classifier/confusion_matrix.tsv
  data/classifier/per_class_metrics.tsv
  data/classifier/confusion_matrix.png
  data/classifier/binary_music_metrics.tsv
"""
from __future__ import annotations
from . import _interp  # noqa: F401

import csv, json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import soundfile as sf

from .taxonomy import TAXONOMY_CLASSES, TaxonomyMapper
from .tagger import Tagger, MODEL_ID
from .classify_clip import AUDIOSET_CSV, TAX_YAML


VALSET_DIR = Path("data/classifier/valset")
OUT_DIR = Path("data/classifier")
MUSIC_CLASSES = {"MUSIC_LIVE", "MUSIC_RECORDED"}


def load_manifest() -> List[dict]:
    p = VALSET_DIR / "valset_manifest.tsv"
    with open(p) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def run() -> Tuple[list, dict]:
    tagger = Tagger()
    mapper = TaxonomyMapper(AUDIOSET_CSV, TAX_YAML)
    manifest = load_manifest()

    preds_path = OUT_DIR / "predictions.jsonl"
    preds_path.parent.mkdir(parents=True, exist_ok=True)
    predictions = []
    with preds_path.open("w") as fp:
        for i, row in enumerate(manifest):
            wav = VALSET_DIR / "clips" / f"{row['clip_id']}.wav"
            audio, sr = sf.read(str(wav), dtype="float32", always_2d=False)
            if audio.ndim == 2: audio = audio.mean(axis=1)
            dist = tagger.tag(audio, sr=sr)
            dec = mapper.reduce(dist)
            rec = {
                "clip_id": row["clip_id"],
                "label_true": row["label"],
                "label_pred": dec.verdict,
                "class_probs": dec.class_probs,
                "music_mass": dec.music_mass,
                "applause_mass": dec.applause_mass,
                "live_leaf_mass": dec.live_leaf_mass,
                "low_confidence": dec.low_confidence,
                "top_audioset": dec.top_audioset,
            }
            fp.write(json.dumps(rec) + "\n")
            predictions.append(rec)
            if (i + 1) % 10 == 0:
                print(f"[eval] {i+1}/{len(manifest)}")

    metrics = compute_metrics(predictions)
    write_confusion(predictions, metrics)
    write_metrics(metrics)
    plot_confusion(predictions, metrics)
    return predictions, metrics


def compute_metrics(preds: list) -> dict:
    classes = list(TAXONOMY_CLASSES)
    idx = {c: i for i, c in enumerate(classes)}
    K = len(classes)
    cm = np.zeros((K, K), dtype=int)  # rows=true, cols=pred
    for r in preds:
        i = idx[r["label_true"]]; j = idx[r["label_pred"]]
        cm[i, j] += 1

    per_class = {}
    for c, i in idx.items():
        tp = int(cm[i, i])
        fn = int(cm[i, :].sum() - tp)
        fp = int(cm[:, i].sum() - tp)
        support = int(cm[i, :].sum())
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_class[c] = dict(support=support, tp=tp, fp=fp, fn=fn,
                            precision=precision, recall=recall, f1=f1)

    total = cm.sum(); correct = int(np.trace(cm))
    acc = correct / total if total else 0.0

    # Binary music vs non-music.
    m_true = np.array([1 if r["label_true"] in MUSIC_CLASSES else 0 for r in preds])
    m_pred = np.array([1 if r["label_pred"] in MUSIC_CLASSES else 0 for r in preds])
    tp = int(((m_true == 1) & (m_pred == 1)).sum())
    tn = int(((m_true == 0) & (m_pred == 0)).sum())
    fp = int(((m_true == 0) & (m_pred == 1)).sum())
    fn = int(((m_true == 1) & (m_pred == 0)).sum())
    b_acc = (tp + tn) / max(1, len(preds))
    b_prec = tp / (tp + fp) if (tp + fp) else 0.0
    b_rec = tp / (tp + fn) if (tp + fn) else 0.0
    b_f1 = 2 * b_prec * b_rec / (b_prec + b_rec) if (b_prec + b_rec) else 0.0

    return dict(
        classes=classes, cm=cm.tolist(),
        per_class=per_class,
        accuracy_5class=acc,
        binary=dict(accuracy=b_acc, precision=b_prec, recall=b_rec, f1=b_f1,
                    tp=tp, tn=tn, fp=fp, fn=fn),
    )


def write_confusion(preds, metrics):
    classes = metrics["classes"]; cm = metrics["cm"]
    p = OUT_DIR / "confusion_matrix.tsv"
    with open(p, "w") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["true\\pred", *classes, "row_total"])
        for i, c in enumerate(classes):
            row_total = sum(cm[i])
            w.writerow([c, *cm[i], row_total])
        col_totals = [sum(cm[i][j] for i in range(len(classes))) for j in range(len(classes))]
        w.writerow(["col_total", *col_totals, sum(col_totals)])
    print(f"[eval] wrote {p}")


def write_metrics(metrics):
    p = OUT_DIR / "per_class_metrics.tsv"
    with open(p, "w") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["class", "support", "tp", "fp", "fn",
                    "precision", "recall", "f1"])
        for c in metrics["classes"]:
            m = metrics["per_class"][c]
            w.writerow([c, m["support"], m["tp"], m["fp"], m["fn"],
                        f"{m['precision']:.3f}", f"{m['recall']:.3f}", f"{m['f1']:.3f}"])
        # Bottom line rows.
        w.writerow([])
        w.writerow(["accuracy_5class", f"{metrics['accuracy_5class']:.3f}"])
        b = metrics["binary"]
        w.writerow(["binary_music_accuracy", f"{b['accuracy']:.3f}"])
        w.writerow(["binary_music_precision", f"{b['precision']:.3f}"])
        w.writerow(["binary_music_recall", f"{b['recall']:.3f}"])
        w.writerow(["binary_music_f1", f"{b['f1']:.3f}"])
    print(f"[eval] wrote {p}")

    p2 = OUT_DIR / "binary_music_metrics.tsv"
    b = metrics["binary"]
    with open(p2, "w") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["metric", "value"])
        for k in ("accuracy", "precision", "recall", "f1", "tp", "tn", "fp", "fn"):
            w.writerow([k, b[k]])
    print(f"[eval] wrote {p2}")


def plot_confusion(preds, metrics):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    classes = metrics["classes"]; cm = np.array(metrics["cm"])
    # Normalize by row (recall view).
    row_sums = cm.sum(axis=1, keepdims=True); row_sums[row_sums == 0] = 1
    cm_norm = cm / row_sums

    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(cm_norm, cmap="viridis", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(classes))); ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=30, ha="right")
    ax.set_yticklabels(classes)
    ax.set_xlabel("predicted"); ax.set_ylabel("true")
    ax.set_title(f"Confusion matrix (row-normalized)\n"
                 f"model={MODEL_ID}, 5-class acc={metrics['accuracy_5class']:.2f}, "
                 f"binary music acc={metrics['binary']['accuracy']:.2f}")
    for i in range(len(classes)):
        for j in range(len(classes)):
            v = cm[i, j]
            txt = f"{v}\n({cm_norm[i,j]:.2f})"
            color = "white" if cm_norm[i, j] < 0.5 else "black"
            ax.text(j, i, txt, ha="center", va="center", color=color, fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    out = OUT_DIR / "confusion_matrix.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"[eval] wrote {out}")


if __name__ == "__main__":
    preds, metrics = run()
    print(json.dumps({
        "n": len(preds),
        "accuracy_5class": metrics["accuracy_5class"],
        "binary": metrics["binary"],
    }, indent=2))
