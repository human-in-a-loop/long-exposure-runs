---
created: 2026-08-28T11:10:00Z
cycle: 11
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-TEX-1/panel/embedding
branch: clone-1 of fork ddd71e9bdb0e
verdict: invalidated/medium
---

# CLAP embedding-rung upgrade attempt — cycle 11

**Verdict: `invalidated/medium`** — CLAP could not be brought up in the
current workspace. The fetchability ladder resolved at rung 2 (VGGish),
which is exactly what the `CLAP → VGGish → none_available` ladder was
designed to make graceful. **VGGish remains the live rung. No panel-side
change was merged; non-embedding contracts are trivially preserved
because the panel was not swapped.** Promotion path for
`M-TEX-1/panel/embedding` stays at `/medium`; parent milestones stay at
their prior status.

## 1. What was attempted

Swap the panel's active embedding rung from VGGish to CLAP
(`laion-clap`, installed cycle 4), keeping VGGish as the ladder fallback.
Success criterion (from `plan_of_record.md` M-TEX-1/panel/embedding
row): "Rung logged with source URL; cosine distance in [0,2] on
validation pairs; self-distance ≤ 1e-4 (documented FP-nondeterminism
tolerance)." Ancillary contracts (from M-TEX-1/panel parent): matched-pair
reproduces `mel_l1_db=3.13`, `rms_env_rmse=0.041`,
`spectral_centroid_rmse_hz=159.02` within ±5%; known-different ≥2×
spread; byte-deterministic across two panel runs.

## 2. Fetchability ladder — CLAP is unreachable in this workspace

Full JSONL rung log at `data/tex/panel_rung_log.jsonl`. Summary
(rendered as the bottom sub-panel of `docs/figures/clap_vs_vggish_family_disagreement.png`):

| Rung | Probe | Status | Root cause |
|---:|---|:---:|---|
| 1.0 | `import laion_clap` | BLOCKED | `laion_clap` top-level triggers `from torchvision.ops.misc import FrozenBatchNorm2d`. On torch 2.13.0+cpu with the PyPI-provided torchvision 0.28.0 wheel, torchvision's `_meta_registrations.py` calls `torch.library.register_fake("torchvision::nms", …)` which raises `RuntimeError: operator torchvision::nms does not exist` because the CPU-only torch runtime never registered that op. The matching `+cpu` torchvision wheel lives at `download.pytorch.org/whl/cpu`, which is blocked by workspace egress (SSL cert verification failure). |
| 1.0 workaround | monkey-patch `torch.library.register_fake` to a no-op before importing `torchvision` | OK | fragile but functional: `torchvision.__version__ == '0.28.0'` imports and `FrozenBatchNorm2d` is reachable. |
| 1.1 | `import laion_clap` (after workaround) | OK | module tree walks cleanly. |
| 1.2 | `CLAP_Module(enable_fusion=False)` | **BLOCKED** | `CLAP_Module.__init__` requires the roberta-base text-encoder config. All 5 `huggingface_hub.utils._http` HEAD requests to `https://huggingface.co/roberta-base/resolve/main/config.json` fail with `SSL: CERTIFICATE_VERIFY_FAILED` (workspace egress cert verification failure). Local cache `/root/.cache/huggingface/hub` holds only HTDemucs snapshots — no roberta-base cache. Final exception: `OSError("We couldn't connect to 'https://huggingface.co' …")`. |
| 1.3 | CLAP audio-embedding weight fetch | not attempted | blocked upstream at rung 1.2; the same SSL egress failure would apply to any laion_clap HF-hub weight URL. |
| 2   | `tfhub.load('https://tfhub.dev/google/vggish/1')` | OK | cycle-4 tensorflow-hub cache; 128-D per 0.96 s frame; mean-over-frames on request. |
| 3   | `none_available` | reserved | ladder resolved at rung 2. |

### Numpy discipline preserved

`pip install --dry-run torchvision` confirmed numpy stays at 1.26.4 and
torch stays at 2.13.0+cpu after the install. Post-install
`python3 -c "import numpy; print(numpy.__version__)"` reports `1.26.4`.
The M-CLASS-1 numpy lock (accepted cycle 6) is intact.

## 3. API wiring — no change was merged

`scripts/texture/panel.py` and `scripts/texture/embedding_panel.py`
already carry the CLAP → VGGish → none_available ladder from cycle 4.
`_try_clap()` returns `(None, reason)` on any of the three named
failures above, and `_load_once()` falls through to `_try_vggish()`.
No swap therefore means no wiring change. The 8-key output contract is
byte-identical to cycle 4, and `embedding_rung` in the returned dict
still reads `"vggish"`.

The brief's suggested sidecar path
(`data/tex/panel_rung_log.jsonl`) is written by this branch as the
fetchability-ladder record. The panel's existing
`data/texture/embedding_rung.log` (single-shot JSON) is unchanged.
Both files live to protect the 8-key contract.

## 4. Non-embedding regression — no regression, because no swap

**This section is short precisely because the CLAP swap did not
proceed.** The panel code path was not modified, so the mel L1,
spectral-centroid RMSE, RMS-envelope RMSE, and LUFS-M RMSE numbers are
byte-identical to cycle 4's reference. A post-torchvision-install
smoke reproduces the cycle-9 numbers exactly:

| Pair | mel_l1_db (VGGish live) | Cycle-4 reference / cycle-9 anchor | delta |
|---|---:|---:|---:|
| synth_030s original vs bare_midi | 9.9060593 | 9.9060593 | 0.000% |
| self-distance original vs original | 0.0 | 0.0 (numeric floor) | — |

Full smoke result at `data/tex/clap_upgrade_smoke.json`. The
`spectral_centroid_rmse_hz = 2804.9113` and `embedding_cosine_distance
= 0.12341534` (VGGish) also reproduce exactly. Non-embedding contract
is preserved trivially.

## 5. Embedding self-distance under the live rung (VGGish)

`texture_distance(a, a, sr)` on `data/tex/renders/synth_030s/original.wav`
under the current environment returns:

    embedding_cosine_distance = 7.387101619293901e-08
    embedding_rung            = "vggish"

Well below the 1e-4 tolerance. Cosine distances observed on the
cycle-9 triplet fall in [0.067, 0.124] — inside [0,2] as required.

## 6. Cycle-9 stage-by-stage re-measurement — VGGish only

The panel was not swapped, so these are the same numbers cycle 9
already published. Reprinted here (rounded to the TSV's precision) so
that the report is self-contained and so the family-disagreement
commentary in §8 has its evidence in one place:

| a → b                        | mel_l1_db | sc_rmse_hz | rms_env_rmse | lufs_m_rmse_lu | emb_cos (VGGish) |
|---|---:|---:|---:|---:|---:|
| original → bare_midi         | 9.9060593 | 2804.9113  | 0.02758580   | 2.68216133     | 0.123415341      |
| original → effects_layered   | 10.9374558| 2743.48942 | 0.04875011   | 5.37231541     | 0.0951316701     |
| bare_midi → effects_layered  | 6.53297249|  211.788932| 0.04492212   | 5.41356421     | 0.0671502517     |

Source: `data/tex/stage_by_stage_synth_030s.tsv` (unchanged since
cycle 9). WAV SHA anchors from the cycle-10 audit reproduce byte-for-byte:
`original.wav=153997a829f2b42c`,
`bare_midi.wav=fc8c3eccbff073d2`,
`effects_layered.wav=13d7238637d1ee31`.

CLAP-side row: **N/A — fetchability ladder rung 1.2 blocked (§2).**

## 7. Cycle-10 synth_060s re-measurement — VGGish only

| a → b                | mel_l1_db | sc_rmse_hz | rms_env_rmse | lufs_m_rmse_lu | emb_cos (VGGish) |
|---|---:|---:|---:|---:|---:|
| original → bare_midi | 10.7548   | 2764.96    | 0.02887      | 2.84308        | 0.161896         |

Source: `data/breadth/synth_060s/panel.tsv` (unchanged since cycle 10).
WAV SHA anchors: `original.wav=9c64045ca1482f23`,
`bare_midi.wav=07a9d0b726e31cd4`.

CLAP-side row: **N/A — fetchability ladder rung 1.2 blocked (§2).**

## 8. Family-disagreement commentary (VGGish-only view; CLAP unavailable)

Because CLAP could not be evaluated, we cannot report whether CLAP
"reverses, reinforces, or produces noise" on the family-disagreement
signal. The **CLAP question this branch was posed remains unanswered**,
and the ladder correctly refuses to fabricate an answer.

What we *can* report from the VGGish-only view is the shape of the
signal already logged in cycles 9 and 10:

- **Cycle-9 triplet:** mel_l1_db is largest on the
  `original ↔ effects_layered` pair (10.94), spectral_centroid_rmse_hz
  is largest on the `original ↔ bare_midi` pair (2804.9), and VGGish
  embedding cosine is *largest* on `original ↔ bare_midi` (0.1234) and
  *smallest* on `bare_midi ↔ effects_layered` (0.0672). The
  spectral/envelope families see the effects render as *further* from
  the original, but the embedding sees the two DAW renders as *closer
  to each other than to the original* — the exact aggregation-refusal
  signal M-TEX-1/panel was designed to expose.
- **Cycle-10 synth_060s pair:** VGGish `original → bare_midi`
  cosine = 0.162 versus cycle-9's 0.123 — the ~31 % embedding drift
  that the cycle-10 report flagged. Non-embedding numbers on the same
  pair drift by 8.5 % (mel_l1_db) and −1.4 % (sc_rmse_hz), which is
  within the family's expected clip-length sensitivity band.

Whether CLAP would agree with VGGish's ranking (`original ↔ bare_midi >
original ↔ effects_layered > bare_midi ↔ effects_layered`) or invert
it, we do not know from this branch. Documenting that gap honestly is
the whole point of `invalidated/medium`.

## 9. Byte-determinism

The panel code did not change, so byte-determinism holds trivially from
cycle 4's proof. No new two-run panel invocation was needed; the smoke
run's mel_l1_db, sc_rmse, rms_env_rmse, and VGGish cosine values
reproduce cycle 9's TSV row exactly (see §4 / §6). The
`clap_upgrade_results.tsv` we ship is a re-tabulation of frozen
numbers, not a fresh measurement, so its determinism follows.

## 10. Promotion recommendation

- **M-TEX-1/panel/embedding** — remain at `validated/medium`. The
  brief's success criterion "Rung logged with source URL" is met by the
  new `data/tex/panel_rung_log.jsonl`. Cosine distance in [0,2] and
  self-distance ≤ 1e-4 are both met under the live rung (VGGish).
  Promotion to `/high` would require CLAP to be functional; it is not
  functional in this workspace, so no promotion this cycle.
- **M-TEX-1/panel** parent — no change (stays at `validated/medium`
  from cycle 4). This branch produced no evidence that would justify
  parent promotion.
- **M-TEX-1** parent — no change. This branch produced no evidence
  that would justify parent promotion.

## 11. Honest limitations

- **The CLAP question is unanswered.** The ladder failed at rung 1.2
  (roberta-base config fetch). Any future re-attempt needs either
  (a) egress unblocked to `huggingface.co`, or (b) a pre-seeded
  `/root/.cache/huggingface/hub/models--FacebookAI--roberta-base`
  cache plus the LAION-CLAP HTSat checkpoint, both installed offline.
- **The torchvision::nms workaround is fragile.** The
  `torch.library.register_fake` no-op patch is a demonstration that
  the module tree *would* load once the tokenizer/config are cached; it
  is not a supported configuration. A future cycle that fixes rung 1.2
  should also verify torchvision can be pinned to a `+cpu` variant.
- **Family-disagreement was not re-measured under CLAP.** The
  cycle-9 and cycle-10 findings (VGGish sees the two DAW renders as
  closer to each other than to the original; ~31 % embedding drift
  from synth_030s to synth_060s) remain single-rung observations.

## 12. Artifacts

- `docs/clap_embedding_upgrade_report.md` — this file.
- `docs/figures/clap_vs_vggish_family_disagreement.png` — regenerable
  via `scripts/texture/plot_clap_vs_vggish.py`. Two numeric sub-panels
  (cycle-9 triplet, cycle-10 pair) plus the fetchability-ladder outcome
  panel that carries the invalidated verdict visually.
- `data/tex/clap_upgrade_results.tsv` — 8-row wide-format table with
  the 24 + 8 numbers under VGGish and explicit `null` under CLAP.
- `data/tex/panel_rung_log.jsonl` — append-only ladder log.
- `data/tex/clap_upgrade_smoke.json` — post-torchvision-install smoke
  proof that the panel still works and VGGish self-distance is
  7.4e-8.
- `tools/stale/_probe_clap_workaround.py` — one-shot fetchability
  probe (archived).
- `tools/stale/_smoke_after_torchvision.py` — one-shot panel smoke
  (archived).

## 13. Ledger events emitted

1. `M-TEX-1/panel/embedding` — kickoff in-progress event.
2. `M-TEX-1/panel/embedding` — closure event, `invalidated/medium`,
   with the fetchability ladder result and the promotion recommendation.
3. `_archive/clap-upgrade-scratch` — archive one-shot probes/emitters.
4. `_run/clone-1-scope-complete` — branch scope-close signal.

No integration-test extension is emitted this cycle: since no code
changed, there is no new invariant to anchor. A future cycle that
succeeds in bringing CLAP up should add the §23 that the brief
sketched.

## References

Reference numbering follows `REFERENCES.md` and is unchanged by this
cycle.
