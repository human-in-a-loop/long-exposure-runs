# Final Audit — Stage 45 (test 21/23)

## Target verdict node
`M-RECREATE-2/accurate-small-set/rc7-mix-balance-match` (c53 Branch A, clone-0) — RC7 v2 rerun on substantive c51 Branch A+B per-stem MIDIs at `data/recreate_v2/rc7_out_v2/verdict.json`. Explicitly supersedes c51 Branch C `data/recreate_v2/rc7_out/verdict.json` (RC7_FAILS).

## Coverage delta
RC7 v2 rerun node was not directly probed by any earlier final-audit stage. Prior coverage was limited to inference from the c51 Branch C RC7_FAILS narrative (which honestly declared its root cause as placeholder-MIDI data starvation, not a structural bug). This stage lifts RC7 v2 to directly-probed status and closes the mix-balance-match arc.

## Probe results (7/7 PASS)

**Probe 1 — three-way `rubric_hash` chain.** `docs/rc7_v2_rerun_rubric.md` SHA-256 == `data/recreate_v2/rc7_out_v2/rubric_hash.txt` content == `verdict.json.rubric_hash` == `9f24e6d9240f1eaf80f6fb20bf0ce5a2e8e235e2ddcc1064dfa271bff404dde4`. Byte-equal.

**Probe 2 — verdict enum + coverage.** `verdict == "RC7_v2_LANDS"`; `n_songs_passing_a7 = 5/5`; `n_stem_accepts = 20/20`. Per-song table:

| song_id | per_stem_pass | song_pass |
| --- | --- | --- |
| 31a164f845f8e27e | 4/4 | true |
| cdd2717e52820ff6 | 4/4 | true |
| 51e433ade2a845e1 | 4/4 | true |
| 252eb21ce7df7328 | 4/4 | true |
| 88d247468cb6d49f | 4/4 | true |

Chicken Grease (`88d247468cb6d49f`) — mandatory per operator UPDATE — passes 4/4 stems (drums+bass+other_guitar+other_piano). Acceptance criterion: per-stem RMS ≤ 3 dB vs baseline over 4 stems; LUFS-S report-only. `eq_curve_method = iirpeak_12band_log_spaced_Q1.4`.

**Probe 3 — byte-determinism × 2.** `byte_determinism.json.byte_determinism_holds = true`; 226/226 common files SHA-equal across `/tmp/rc7v2_run5_trioy36g` and `/tmp/rc7v2_run6_30kgxg05`; `mismatch_files = []`. Env pins recorded verbatim (PYTHONHASHSEED=0, SOURCE_DATE_EPOCH=1756463424, TZ=UTC, LC_ALL=C.UTF-8, single-thread BLAS).

**Probe 4 — anchor preservation.** `anchor_preservation_v2.json.preservation_holds = true`; c51 Branch C anchor root `data/recreate_v2/rc7_out/` snapshotted 182 files pre-run, re-hashed post-run: pre_count=post_count=182, `sha_diff_after_run=[]`, `missing_after_run=[]`, `new_after_run=[]`.

**Probe 5 — `render_stem.py` c51-invariant SHA lock.** Live re-hash of `scripts/palette_render/render_stem.py` = `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` — byte-equal to c51 Branch C additive-kwargs pin (also matches stage-43 and stage-44 audits — three-stage-independent lock).

**Probe 6 — hygiene (PRNG / sidecar_nonfactor / interpreter guard).** `scripts/recreate_v2/rc7_v2_rerun.py`: PRNG matches = 0; `sidecar_nonfactor` matches = 0; 6 interpreter-guard hits (`/usr/bin/python3` and/or `sys.executable`) present. Clean.

**Probe 7 — test suite.** `tests/test_rc7_v2_rerun.py` — 20 numbered test cases per rubric §h test-suite ≥19 gate (rubric-anticipated; 19 direct + 1 disk-post-run). Coverage includes rubric mtime pre-registration, three-way rubric-hash chain, render_stem SHA lock, no-PRNG grep, VST3 lock, CLAP anti-pattern, `/usr/bin/python3` guard, c48 env-flag default-OFF, focus_set_v2 consumption, A7 4-stem gate, EQ band pinning, RMS clamp, MIDI split fidelity, verdict shape, anchor preservation, READ-ONLY helper imports, EQ zero-mean normalization, `pretty_midi` round-trip, render_stem signature, on-disk verdict.

## Structural finding: c51 RC7_FAILS reconciled
`verdict.json.supersedes_verdict = "data/recreate_v2/rc7_out/verdict.json"`. The c51 Branch C RC7_FAILS anti-verdict was honestly emitted (0/5 songs, 8/15 stems) and structurally sound; c53 rerun substitutes c33-anchor placeholder MIDIs with c51 Branch A (RC1+RC9 vocals+guitar+piano) + Branch B (RC2+RC3 drums+bass) substantive MIDIs and delivers 5/5-song / 20/20-stem PASS. Supersession chain is well-formed and preserves the c51 verdict on disk as diagnostic anchor.

## Findings appended this stage
None. All seven probes cleared; supersession chain is well-formed; hygiene clean; test suite sized to rubric. No CRITICAL / MODERATE / MINOR findings warrant append.

## Below-MINOR observations (not appended)
- `verdict.json.acceptance_criterion` names 4 stems `{drums, bass, other_guitar, other_piano}` (RC9 first-class-parts flavor); RC7-v2 rubric documents this expansion vs c51's 3-stem `{drums, bass, other}`. Rubric-anticipated.
- Only one script under `scripts/recreate_v2/rc7_v2_*` (`rc7_v2_rerun.py`) — monolithic dispatch consistent with c53 substantive-branch pattern (contrast c53 clone-1 guitar_piano which shards into 4 files under a package dir).

[OUTPUT: final_audit_stage]
Stage 45: c53 Branch A RC7 v2 rerun directly probed — 7/7 PASS (three-way rubric_hash chain byte-equal; RC7_v2_LANDS 5/5 songs including Chicken Grease all 20/20 stems; byte-det × 2 226/226; anchor preservation 182/182 c51 files; render_stem c51 SHA lock byte-equal; 0 PRNG / 0 sidecar_nonfactor / 6 guard hits; 20-case test suite); c51 RC7_FAILS supersession chain well-formed.
File: /home/user/long-exposure-runs/music-gen/audits/final/stages/test_21of23.md
Findings appended: 0
[END OUTPUT]
