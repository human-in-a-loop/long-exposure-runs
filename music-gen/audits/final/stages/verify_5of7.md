# Verify 5/7 — M-V4-EAR-1 c76 chain (v2 wider-linear calibration + L119 infeasibility proof + band-4 v2 spot check)

Stage 6 of 16 · delta-audit mode · baseline `final_audit_report.md` canonical.

## Slice

Substantive c76 M-V4-EAR-1 chain, closing the EAR-1 milestone at
HALT-HONEST via monotone-infeasibility of the campaign L119 mandate:

- `M-V4-EAR-1/v2-wider-linear-calibration-c76` (validated/high)
- `M-V4-EAR-1/l119-infeasibility-proof-c76` (validated/high)
- `_selection/band4-spot-check-v2-c76` (str-supersede of c75 spot check)

## Anchor verification (SHA pins vs on-disk)

All POR-pinned SHAs match on-disk state byte-identically. New c76 script
SHAs recorded honestly (POR narratives cite paths, not SHAs, for the new
substantive scripts).

| Anchor | POR pin | On-disk | Match |
|---|---|---|---|
| `data/v4/ear/l119_infeasibility_proof_c76.json` | `ada44349…b15a68a` | `ada44349…b15a68a` | PASS |
| `data/v4/ear/band4_spot_check_v2_c76.json` | `d8fcea2a…743b30a7` | `d8fcea2a…743b30a7` | PASS |
| `data/v4/ear/exemplar_set.json` | `31c10dfb…d25f7f5f6` | `31c10dfb…d25f7f5f6` | PASS |
| `scripts/ear/v4_ear.py` (READ-ONLY per c76 P1a) | `e775621b…9336878` | `e775621b…9336878` | PASS |
| `scripts/ear/v4_ear_v2.py` (NEW c76 sibling) | (path only) | `7d81e5f5…9aae7ef6` | recorded |
| `scripts/ear/probe_l119_infeasibility_c76.py` (NEW) | (path only) | `88263f98…2ec1fdbf` | recorded |
| `scripts/ear/band4_spot_check_v2_c76.py` (NEW) | (path only) | `08ec7454…8ea7ce319` | recorded |

## Verdict-content coherence

### L119 monotone-infeasibility proof (`l119_infeasibility_proof_c76.json`)

- `all_three_statistics_raw_inverted=true` — 3/3 statistics (max-over-windows-c74, mean-over-all-windows, mean-of-per-ex-max) show `raw_separation < 0` (band4_max_raw > exemplar_min_raw).
- Per-statistic raw separations: `−0.0706 / −0.1057 / −0.1225`.
- Monotone-calibration lemma stated verbatim in `infeasibility_verdict.monotone_calibration_lemma`.
- 3×3 statistic × calibration matrix: **0 of 9 cells pass both L119 gate AND sanity gate**.
- Wider-linear-c76 × mean-over-all-windows cell reports `sanity_gate=false` (loo_min=4.936 < 5.5) — honestly disclosed edge case, not concealed.
- `backbone: vggish_only`, `env_pin_sha256: 2ac444c3…922ca` (canonical 7-key subset unchanged).
- Conclusion clause: FD-6 delegation of M-V4-GEN-1 passer gate to operator ear per c47 OPT1 standing precedent — matches POR narrative for `M-V4-GEN-1/batch-score-still-blocked-c76`.

### V2 wider-linear calibration (`v4_ear_v2.py` sibling)

- Sibling to c74 `v4_ear.py` (READ-ONLY anchor byte-identical pre==post).
- 5/5 exemplar LOO under wider-linear-c76 × max-over-windows-c74:
  - chicken_grease=6.694, peach_dream=6.780, molasses=6.691, essence=6.831, desire=6.209.
  - Range [6.209, 6.831] matches POR narrative "[6.21, 6.83]" exactly.
  - 0/5 clipped at 7.0 (vs c74 linear: 4/5 clipped — saturation eliminated).
- Sanity gate PASSES: 5/5 ≥6.0, 0 <5.5.
- Chain-supersede via `supersedes_path=M-V4-EAR-1/substantive-implementation` (str per c14 lemma).

### Band-4 v2 spot check (`band4_spot_check_v2_c76.json`)

- band4_scores under v2: aguanile=4.836/5.704 (depends on statistic), stay_live=6.720, wagon_wheel=6.187.
- `band4_max = 6.720` (stay_live).
- `loo_min = 6.209` (desire).
- Mandate threshold = loo_min − 0.5 = 5.709.
- `gate_passes = false` (6.720 > 5.709) — HONEST FAIL correctly recorded.
- `halt_honest_finding` narrative pins root cause: raw VGGish cosine similarity of stay_live (band-4) exceeds desire (band-7) at the exemplar bank — a resolution ceiling of VGGish, not a calibration bug.
- `supersedes_path = _selection/band4-spot-check-halt-honest-c75` (str per c14 lemma).

## Discipline audit

- No PRNG imports (`import random`, `numpy.random`, `torch.rand*`) in any c76 script — grep clean.
- No `sidecar_nonfactor` imports — grep clean.
- No VST3 state APIs (`get_state`, `save_state`, `save_preset`, `load_state`, `set_state`) — grep clean.
- `/usr/bin/python3` interpreter guard present on all three c76 scripts (via `/usr/bin/env /usr/bin/python3` form per c15 interpreter-guard-policy; equivalent).
- `env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` (canonical 7-key subset) unchanged in both sidecars — FD-16(a) cert re-issue trigger did NOT fire.
- Str-supersede lemma (c14) respected: both new-in-c76 selection events carry `supersedes_path` as `str`, never `list`.
- READ-ONLY anchors byte-identical pre==post: `v4_ear.py` (c74) + `exemplar_set.json` (c74) + VGGish embedding caches (`exemplar_embeddings.npz`, `band4_embeddings.npz` per POR — not re-hashed this stage, downstream anchors).

## Findings this stage

None. All POR/ledger claims for the c76 M-V4-EAR-1 chain match on-disk
state; verdict content is coherent with narratives; discipline gates
green.

## Notes for downstream stages

- c76 closes M-V4-EAR-1 at HALT-HONEST via first-class negative finding (L119 monotone-infeasibility). This is the operative gate blocking any automated M-V4-GEN-1 passer count and legitimates the FD-6 operator-ear delegation carried into c77 close.
- The c76 methodology (3×3 sweep across statistics × calibrations under a monotone-calibration lemma) is a lesson-candidate class: honest infeasibility proofs prevent the campaign from oscillating on calibration tweaks that cannot resolve a raw-data separation problem. Flag for consideration in document stage.
- Post-c77 causal-summary carries `M-V4-GEN-1/interpolation-demo-delivered-c78 validated/high` — outside c77 close scope but worth verifying in a later stage if slice remains.
