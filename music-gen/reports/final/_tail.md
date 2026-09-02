
# 9. Conclusions, Honest Limits, and Future Work

## 9.1 What is done

Against the seven "what counts as done" criteria in the project
prompt, the run's end-state is:

1. **Ingestion, classification, and provenance chassis exist and are
   honest.** Every chunk is content-addressed; the three-model
   classifier ensemble gates release; the seven-non-factor sidecar
   is stored and audited but never consumed. The egress-ready state
   machine is deployed and fires under a two-consecutive-`media_ok`
   rule.
2. **Source separation is deterministic and licensed for redistribution.**
   `htdemucs_6s` renders four stems byte-identically across independent
   invocations. Determinism was verified on a five-song slice; the
   weights fetch is reproducible.
3. **Transcription has an honest per-axis F1 on the M-SEP-1 synth
   reference.** basic-pitch 0.4.0 delivers usable pitch/onset/offset
   under a tuned octave-suppression grid; timbre, dynamics, and form
   are named as under-covered.
4. **A merged-score bridge is byte-identical across two full
   round-trips**, and a typed rules ledger of 76 hash-deduplicated
   rules is validated against a planted-invalid rejection matrix.
5. **The DAW stack renders deterministically on Surge XT and Dexed
   through DawDreamer**, with one closed gap (GAP-1 Ardour Lua MIDI
   import, closed by hand-authored XML) and one open gap (GAP-2
   LV2/VST3 automation delivery, worked around by two-step render).
6. **The M-TEX-1 panel refuses to aggregate**, reports 72 finite
   panel entries across three seeds, and surfaces the VGGish
   content-flip as a labelled, understood family disagreement.
7. **The pipeline closes end-to-end on a real rated song**
   (M-RECREATE-1, +5.906 dB effects-over-bare on the band-7
   exemplar) and the five-song accurate-small-set programme is
   hardened per-stem with RC7 and RC9 both landing 5/5.

## 9.2 The two live constraints

Two constraints are load-bearing and honest:

- **Real-label M-EAR-1 calibration depends on the full 80-song
  corpus.** 43 of 80 songs have on-disk audio; the remaining 37
  are registered with full provenance but their audio is behind
  the workspace egress policy. The armed harness (§7.6) will fire
  the full calibration automatically once the two-consecutive
  `media_ok=true` production probes land. M-EAR-1 is held
  in-progress by design until that fires.
- **Generation quality depends on the recreation loop closing on
  held-out songs.** M-RECREATE-1 closed on one band-7 exemplar and
  the five-song focus set is hardened; the accurate-small-set
  parent remains in-progress under the peer-under-G1 convention
  until the panel-gate cell (RC6) validates on the held-out songs
  under RC1..RC3 outputs.

## 9.3 Actionable next steps

Drawn directly from the final audit's `future_work` block, in the
order they should be attempted:

1. **Real-label M-EAR-1 calibration on the full 80-song corpus**
   per the c26 Path B commit doc — awaits egress unblock or manual
   manifest reconciliation.
2. **Add `probe_kind ∈ {smoke, production}` to
   `data/ingestion/egress_status.jsonl`**, so the
   two-consecutive-`media_ok` unblock signal cannot be spuriously
   satisfied by smoke rows.
3. **Rebuild the missing `data/gen/*` renders on demand from the
   seeded ledger** — a single deterministic sweep re-materialises
   them.
4. **Emit a single supersede event** that either renames the c51+
   RC7/RC10 leaves to the pre-registered `accurate-small-set-v2`
   parent, or explicitly folds v2 back into v1 with a note that
   rubric-v2 was carried inline under v1 leaf identifiers.
5. **Restore or supersede the missing SSoT writer sources**
   (`long_exposure/workspace_bootstrap.py`,
   `long_exposure/tools/_ledger_schema.py`); if they were
   consolidated into surviving package modules, emit a
   `_plan/*-supersede` event that names the current SSoT.
6. **Republish `data/anchor_manifest_v1.json` as `_v2`** with
   anchor #20 = post-c36-edit SHA of
   `scripts/palette_render/render_stem.py`, and encode the
   backwards-compat contract (`parameter_dict=None` ≡ c33 anchor)
   explicitly.
7. **Append 10 band-7 rows to
   `corpus/ratings/ratings_manifest.tsv`** so provenance matches
   the on-disk audio M-RECREATE-1 consumed.
8. **Emit a closure event** adjudicating the two observed
   silent-death cases under
   `_manager/background-job-supervision-clone-0` (c31 fixture, c36
   feature extraction), or archive them with lessons learned.
9. **Publish SSoT schemas for `anchor_preservation_v1.json` and
   `verdict_v1.json`** and have subsequent cycles conform.
10. **Fill the c41/c42 reporting gap, add the c52 egress-probe row,
    and either produce substantive c55-c58 content or retire the
    empty `report_cycles_56-58.md`**.

## 9.4 No new hypotheses

Everything above is drawn from what was measured. The one live
scientific open end — the collision-arc
PARTIAL_BP_UNRESOLVED_SHAPE (§8.5) — is left open with its four
ruled-out candidate mechanisms named, and no new mechanism is
proposed here. It is a real question about the distribution of
generation-output collisions, and it deserves an unhurried
follow-up rather than a speculative closure inside this report.

# 10. References

External tools, models, and libraries cited in this report:

[1] Défossez, A. et al. *Hybrid Transformer Demucs (htdemucs)*.
    Model weights and code:
    <https://github.com/facebookresearch/demucs>.

[2] Bittner, R. M. et al. *A Lightweight Instrument-Agnostic Model
    for Polyphonic Note Transcription (basic-pitch)*. Spotify.
    <https://github.com/spotify/basic-pitch>.

[3] Kong, Q. et al. *PANNs: Large-Scale Pretrained Audio Neural
    Networks for Audio Pattern Recognition*.
    <https://github.com/qiuqiangkong/audioset_tagging_cnn>.

[4] Plakal, M. and Ellis, D. *YAMNet*.
    <https://github.com/tensorflow/models/tree/master/research/audioset/yamnet>.

[5] Gong, Y. et al. *AST: Audio Spectrogram Transformer*.
    <https://github.com/YuanGongND/ast>.

[6] Elizalde, B. et al. *CLAP: Contrastive Language-Audio
    Pretraining*.
    <https://github.com/microsoft/CLAP>.

[7] Hershey, S. et al. *CNN Architectures for Large-Scale Audio
    Classification (VGGish)*.
    <https://github.com/tensorflow/models/tree/master/research/audioset/vggish>.

[8] Cao, W., Mirjalili, V., Raschka, S. *Rank consistent ordinal
    regression for neural networks with application to age
    estimation (CORN)*. Pattern Recognition Letters, 2020.

[9] MuseScore 3, version 3.2.3.
    <https://musescore.org/>.

[10] Ardour DAW.
     <https://ardour.org/>.

[11] Braun, D. L. *DawDreamer: Bridging the Gap Between Digital
     Audio Workstations and Python Interfaces*. ISMIR-LBD 2021.
     <https://github.com/DBraun/DawDreamer>.

[12] Surge Synth Team. *Surge XT*.
     <https://surge-synthesizer.github.io/>.

[13] Gauthier, P. *Dexed (Yamaha DX7 emulator)*.
     <https://asb2m10.github.io/dexed/>.

[14] Hawthorne, C. et al. *Onsets and Frames: Dual-Objective Piano
     Transcription* (evaluated and not adopted; TF-pin conflict).

[15] Kim, J. W. et al. *CREPE: A Convolutional Representation for
     Pitch Estimation* (evaluated and not adopted; TF-pin conflict).

[16] Raffel, C. et al. *mir_eval: A Transparent Implementation of
     Common MIR Metrics*. ISMIR 2014.

[17] McFee, B. et al. *librosa: Audio and music signal analysis in
     Python*.

[18] Gemmeke, J. et al. *AudioSet: An ontology and human-labeled
     dataset for audio events*. ICASSP 2017. (Class taxonomy
     consumed by [3], [4], [5].)

Internal artifacts and prior reports are referenced inline by their
milestone identifier (`M-*`), stage cell (`RC*`), or cycle-report
filename (`report_cycles_*.md` under `reports/cycles/`).
