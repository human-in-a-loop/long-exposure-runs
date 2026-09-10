# Music-Gen v4 closure campaign — MANIFEST

## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include these; other
files are supporting or exploratory.

- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` — the
  Chicken Grease A/B showcase mix cited in §9.4 (SHA prefix
  `6e13e0075c5d8116…`, LUFS-I −15.32).
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.manifest.json` —
  inputs manifest for the showcase mix (§9.4).
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.replay_proof.json`
  — byte-identity replay proof for the showcase mix (§9.4).
- `scripts/sound_match/deliver_cg_ab_v4.py` — the delivery script
  whose smoke test reports every Chicken Grease cell terminal
  (§9.3, §9.4).
- `scripts/sound_match/pinned_profile_schema_v1.json` — the
  pinned-profile JSON schema validated as load-bearing for
  replay discipline (§9.3, §9.6).
- `scripts/sound_match/profile_validator.py` — validator for the
  pinned-profile schema (§9.3, §9.6).
- `scripts/sound_match/objective.py` — composite objective; the
  emission point named in the Path B remediation option for the
  metric-semantics escalation (§9.5, §10.3 item 1).
- `scripts/sound_match/embedding_panel.py` — embedding-cosine
  computation (`1 − cos(u, v)`) referenced in the same
  escalation (§9.5).
- `scripts/v4_rules/extract_v4.py` — the substantive v4-rules
  extractor whose audit-trail rows are the housekeeping gap
  named in §9.6 and §10.3 item 2.
- `scripts/v4_rules/__init__.py` — package init for the
  extractor above (§9.6).

Snapshot at on-disk cycle 90 close (harness report range 140–141; the
workers labelled c89/c90 as harness c133/c134 under an assumed offset of
44 — the counters are disclosed, not reconciled). Scope: the v5 arc files
produced or modified during on-disk cycles 89–90 (F5 interpolation demo,
F7 close documents). Earlier v5 files are listed only where a c89–c90
file consumes them; the "Key Files" section above is preserved verbatim
from the v4 close-out. The v5 arc re-closed at c90 (`V5_CLOSE_LANDS`).

## Scripts (cycles 89–90)

### `scripts/v5/` — generator and F5 blend

| file | lines | cycle | purpose |
|---|---|---|---|
| `generate_v5.py` | 1114 (969 at c88 close) | 89 (additive) | groove-first generator; c89 adds `--f5` (default off) with sub-flags `--interp-a/--interp-b/--interp-t/--f5-prereg`; with `--f5` one demo spec is appended after the 5 regular songs; manifest `f5` block (raw-render RMS per stem, density + Hamming statistics vs A-only / B-only compositions); sha pre `3d0f3a24…` → post `94c8ba99…`; no edit at c90 |
| `interpolate_v5.py` | 190 | 89 | F5 model-parameter blend of two donor-conditioned models (groove conditional tables over the union vocabulary; harmony segment rows over the 81 n=23 states with n=23 backoff); imported only under `--f5`; sha `177ac5c6…` |
| `repo_root.py` | 42 | 89 | shared marker walk-up (`promise_ledger.jsonl` + `scripts/v5/`) so plot scripts under `data/` need no `parents[N]` literal; sha `d012e510…` |
| `runners/run_from_launch_json.py` | 110 | 90 | generic re-executor of any pinned launch / byte-det command (dry-run default; `/usr/bin/python3` guard; refuses `--execute` on a drifted generator or without a fresh `--out`); sha `9c6f464e…` |
| `runners/README.md` | — | 90 | runners decision (a) rationale + SHAs of the ten c89 runners; sha `10c72355…` |
| `runners/c89/*.py` (10 files) | 413 total | 89 (copied in-tree at 90) | verbatim copies of the c89 pipeline runners (prune, pins/prereg, smoke, launch, independent process, flag-off, deliver, byte-det assembly, tests); historical record, not maintained tools |

Read-only consumers unchanged this range: `comping_gen_v5.py` (103), `velocity_v5.py` (377), `bass_pitch_v5.py` (385), `melody_vomm_v5.py` (352), `harmony_v5.py` (411), `groove_v5_v2.py` (338), `form_plan_v5.py` (346), `comping_v5.py` (325), `score_gen_batch_v5.py` (154), `deliver_v5_listening.py` (71), `midi_from_json_events_v5.py` (123).

### `data/v5/` (figure scripts co-located with data; each takes `--out`)

| file | lines | cycle | figure |
|---|---|---|---|
| `data/v5/gen/plot_iter05_parts_c89.py` | 83 | 89 | `data/v5/gen/fig_iter05_parts_c89.png` — iteration-5 comping-part note_on counts (6 renders), demo raw-render RMS per stem vs the −60 dBFS floor, demo groove density vs the A-only / B-only line with the ±2.0 band; uses `repo_root` |

### `tools/` (one-shot emitters / registrars, run)

| file | lines | cycle | purpose |
|---|---|---|---|
| `_emit_c89_ledger_events.py` / `_register_c89_por_rows.py` | 229 / 115 | 89 | cycle-89 ledger events (14) + plan rows; F5 row amended additively with the `c89 LANDED` clause |
| `_emit_c90_ledger_events.py` / `_register_c90_por_rows.py` | 354 / 110 | 90 | cycle-90 ledger events (19, incl. the 280-path adopt event and the close enum computed from disk) + plan rows; `c90 CLOSED` clauses on the close rows |

## Tests (cycles 89–90)

| file | tests | status |
|---|---|---|
| `tests/test_c89_landing.py` | 11 | 11/11 (prereg mtime gate, flag guards, byte-det ×2 + independent process, F5-off reproduces iteration 4, audibility statistics recomputed, expected-output count, repo_root scan, stall 5/12, delivery SHAs, verdict/POR consistency, anchors) |
| `tests/test_c90_close.py` | 9 | 9/9 (prefix byte-equality of the three docs, v3 first-8 KB header, F1–F7 table + every quoted SHA resolves, F5 caveat sentences, validators ERROR == 156, runners dry-run byte-for-byte, no render tree newer than cycle open, READ-ONLY pins, c90 event shape) |
| c86/c87/c88 suites | — | generator-sha pins re-pinned at c89 to the chain (c88 post-edit == c89 pre-edit); `test_c88_landing::test_09` stall pin `== 4` → `>= 4`; no re-pins at c90 |

Adopted-suite regression: c89 close 11 files / 84 PASS lines, all rc 0 (`data/v5/logs/test_results_c89.json`); c90 close 12 files / 93 PASS lines, all rc 0 (`data/v5/logs/test_results_c90.json`). The c90 auditor re-ran 12 files (105 PASS lines by its count), all rc 0, and re-rendered iteration 5 (flag-on) and iteration 4 (flag-off) reproducing every SHA.

## Data artefacts (cycles 89–90)

- `data/v5/gen/f5_prereg_c89.json` (`fb614843…`, 03:14:04Z — precedes every iteration-5 file and the F5 code edit).
- `data/v5/gen/iteration_05/` — 5 regular renders (seed 4, `--f2 --f3 --tempo-overrides`) + the demo `gen_v5_interp_CG_PD_t050_donor_31a164f845f8e27e/` (adds `f5_blend.json`); 248 files; `iteration_rollup.json` (`4787a346…`, F5_LANDS_pending_bytedet → F5_LANDS in byte-det); replay proofs 6/6.
- `data/v5/gen/byte_determinism_c89.json` (`476269f3…`) — in-process replay ×6, independent second process ×6 (188.1 s), iteration-4 flag-off 5/5 (151.9 s), score table ×2; `f5_enum_final = F5_LANDS`.
- `data/v5/gen/byte_determinism_c90.json` — turn-start pins for the close cycle (44 pins; 40 byte-identical at audit, the 4 that moved are the three appended docs + `plan_of_record.md`).
- `data/v5/gen/gen_v5_iter05_ear_scores_c89.json` — informational scores 6/6 ≥ 6; `data/v5/gen/stall_counter.json` (`4b87958f…`) — 5/12, passers 0, iteration-5 F6 entry.
- `data/v4/generated/v5_iter_05/` (6 listening copies + manifest `d8647e7a…`); `data/v4/generated/f5_interp_CG_PD_t050_c89/` (demo trio + `f5_blend.json` + prereg copy; `delivery_manifest.json` `7cddb63a…`).
- `data/v5/logs/` — `gen_iter05_c89.launch.json` + logs, `indep_c89.log`, `flagoff_c89.log`, `bytedet_c89.log`, `deliver_*_c89.log`, `score_gen_v5_iter05_c89_run{1,2}.log`, `c89_prune.json` (565 MB), `c90_prune.json` (596 MB), `validators_c90.json` (open 156/8960 → after adopt 156/8731), `validators_c90_close.json` (final 156/8714; post-close 156/8707; after split 156/8708), `runners_decision_c90.json`, `test_results_c89.json`, `test_results_c90.json`.
- `docs/v4_completion_report_v3.md` — v5 section appended (20497 → 54331 B; prefix byte-identical); `docs/OPERATOR_DECISIONS.md` — entry #21 (16147 → 19655 B); `docs/CODEBASE_GUIDE.md` — v5 layer section (4536 → 12997 B).
- `plan_of_record.md` — F5 row `c89 LANDED` clause; `M-V5-CLOSE-1` and `M-V5-GEN-1/F7-close` rows `c90 CLOSED` clauses; c89/c90 sub-leaves.
- `promise_ledger.jsonl` — 2138 → 2171 (c89: 14 events; c90: 19 events).

## Cumulative stats (cycles 89–90)

- New scripts: 2 under `scripts/v5/` (232 lines) + 1 runner module (110) + 10 copied runners (413) + 1 figure script (83) + 4 under `tools/` (808); `generate_v5.py` 969 → 1114 lines.
- New tests: 2 files, 20 test functions; adopted suite 93/93 PASS lines at c90 close.
- Figures: 1 new (`fig_iter05_parts_c89.png`), with `--out` plot script.
- Ledger: 33 events across the range; validators promise_check 156 ERROR (flat since c85) / 8708 WARN after the c90 split; org_check 0 / 54.
- Env pin `2ac444c36298d6ad…922ca` unchanged (c22 → c90); disk never ≥ 90 % (c89 86 → 84 %; c90 87 → 85 %).
- v5 arc closed: `M-V5-CLOSE-1 = V5_CLOSE_LANDS`; parent roll-ups CORPUS / RULES / EAR / GEN recorded at c90.

## Cross-references

- `f5_prereg_c89.json` (`fb614843…`) → `generate_v5.py --f5 --f5-prereg` → pinned into every iteration-5 manifest `rules_sha256.f5_prereg` and the stall-counter history.
- Donor canonical MIDI (`data/v5/corpus/31a164f845f8e27e/canonical_v5_reindexed/`, `data/v5/corpus/88d247468cb6d49f/canonical_v5c_reindexed/` at 122.197271 BPM) → `interpolate_v5.py` (read-only imports of `groove_v5_v2.load_song/table` and `harmony_v5.analyse_song`) → blended groove model `dcf0af85…` + harmony chain `bab58797…` → demo `ab_mix.wav` `947b348a…`; blend record `0bc6f353…` (compact canonical JSON hash; file bytes `72d9cdcd…`).
- n=23 chain `330b9d46…` + groove `57072025…` + comping `01024254…` + tempo overrides `ef52f2a0…` → the 5 regular iteration-5 songs (unblended); the same chain supplies the harmony back-off rows for the blend (A 12 / B 26 states).
- Flag-off chain: post-edit `generate_v5.py` (`94c8ba99…`) without `--f5` reproduces iteration 4 (`a501df3c…` … `313b98bd…`) 5/5.
- `data/v5/logs/gen_iter05_c89.launch.json` / `byte_determinism_c89.json` commands → `scripts/v5/runners/run_from_launch_json.py` dry-run (byte-for-byte; asserted by `test_c90_close.py`).
- `validators_c90.json` (`9f0db6e2…`) is quoted by the v5 section's deliverable index; the later `final`/`post_close` phases therefore live in `validators_c90_close.json` (no ledger event adopts it — the c90 audit's one disclosure-class finding).
