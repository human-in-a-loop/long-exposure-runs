# Final Audit — Delta Mode — Stage 1 (Explore)

**Run:** `run-2026-08-28T040704Z`
**Baseline committed:** 2026-09-02 05:24:25 UTC
**This audit scope:** post-baseline per-cycle deliverables only. The
committed baseline `audits/final/final_audit_report.md` and
`final_audit_summary.json` stand as canonical for cycles 1–63
(prior campaign) and are not re-verified here unless a new artifact
directly reopens them.

## §1. Boundary

Prior baseline covered cycles 1–63 of the pre-pivot campaign
(M-INGEST/M-CLASS/M-DAW-SPIKE/M-SEP/M-TRANS/M-SCORE/M-HEUR/M-EAR/
M-RULES/M-TEX/M-GEN + M-RECREATE-1/2). Everything past the baseline
mtime (2026-09-02 05:24:25) is delta:

- **v3-SPINE arc** (Chicken Grease per-stem doctrine): cycles c3–c22
  under M-V3-SPINE-1 → operator LANDS 2026-09-02 → M-V3-FOCUS-1
  three-clone fanouts (Rome, WIG, Disco A, Peach Dream) → palette
  proof (Chicken Grease Surge XT / sfizz) → M-V3-SPINE-2 unified
  driver → stage-checkpointed driver.
- **v4 closure campaign**: cycles c1–c20 under M-V4-CERT-1 (already
  green at c1 opening), M-V4-PROFILES-1 per-instrument sound
  matching arcs on Chicken Grease (bass / drums / guitar / piano /
  other / vocals), M-V4-SHOWCASE-1 CG A/B render, M-V4-RULES-1
  scaffold; WIG / Rome / Peach Dream / Disco A skeletons opened but
  gated on operator-authority metric-semantics escalation.
- **c61–63 fan-out merge report** (legacy c55 fork numbering — one
  post-baseline report that is a re-narration of already-validated
  work; treat as background, not new substance).

## §2. Delta reports enumerated

21 report files newer than the baseline mtime, split by arc:

**v3-SPINE cycle reports (post-baseline authoring):**
```
report_cycles_1-2_clone_1.md              (v3 spine early)
report_cycles_1-2_clone_2.md              (v3 spine early)
report_cycles_1-3.md                      (v3 spine c1-3)
report_cycles_1-3_clone_{0,1,2}.md        (v3 spine c1-3 fanout narrations)
report_cycles_4-4_clone_0.md              (v3 FOCUS Disco A terminal reverify)
report_cycles_4-4_clone_2.md              (v3 FOCUS Peach Dream)
report_cycles_4-6_clone_1.md              (v3 spine c4-6)
report_cycles_7-9_clone_1.md              (v3 spine c7-9)
report_cycles_10-10_clone_1.md            (v3 spine Peach Dream Hold)
report_cycles_11-13.md                    (v3 spine c11-13)
report_cycles_14-16.md                    (v3 spine c14-16 — first fully clean heartbeat audit)
report_cycles_17-19.md                    (v3 spine c17-19 — 9th/10th/11th heartbeat)
report_cycles_20-22.md                    (v3 SPINE operator LANDS + FOCUS fanout + palette proof + integration)
```

**v4 closure campaign reports:**
```
report_cycles_1-3.md                      (v4 CG-bass sf2 stage-1/stage-2)
report_cycles_4-6.md                      (v4 CG-bass STILL_INDETERMINATE + family-2 spec + replay CRITICAL fix)
report_cycles_7-9.md                      (v4 CG-bass arc closeout + wait-on-operator retired + OPT1+OPT3 accept)
report_cycles_10-12.md                    (v4 CG-drums arc: SF2_RULED_OUT + FAMILY2_RULED_OUT)
report_cycles_13-15.md                    (v4 CG-guitar arc + piano/other NULL grounded + drums OPT3)
report_cycles_16-18.md                    (v4 metric-semantics CRITICAL escalation + CG A/B render + WIG/Rome opened)
```

**Legacy:**
```
report_cycles_61-63.md                    (c55 fork-merge report; predates v3/v4 pivots; low delta content)
```

**Missing (no report on disk):** cycles 19–20 (v4) — c19 opened
Disco A + Peach Dream skeletons + LUFS FETCH_FAIL test; c20
scaffolded M-V4-RULES-1. No pre-authored .md yet; verify against
the plan-of-record + ledger rows directly.

## §3. Milestone triage (delta scope)

All milestones in this list either (a) landed after 2026-09-02
05:24:25 or (b) reference a rubric/spec first cited in a delta
cycle. Not re-audited: any milestone whose latest ledger event
predates the baseline mtime.

### V3-SPINE arc (parent: M-V3-SPINE-1; also new sibling M-V3-SPINE-2)

- `M-V3-SPINE-1/option-a-adopted` — c4, operator OPTION A verbatim.
- `M-V3-SPINE-1/canonical-serializer-spec-committed` — c4.
- `M-V3-SPINE-1/rubric-v2-committed` — c4, `rubric_hash_v2` chain
  (`c49db5a12e955f26…`).
- `M-V3-SPINE-1/canonical-serializer-implemented` — c4,
  `midi_from_json_events.py` 12/12 unit tests.
- `M-V3-SPINE-1/canonical-midi-determinism-verified` — c4, 7/7
  probes byte-deterministic ×2.
- `M-V3-SPINE-1/anchor-preservation-pre/post-{v2,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19}-verified` —
  17 anchor pairs, growing from 36 → 216 anchors byte-identical.
- `M-V3-SPINE-1/env-drift-audit-{spec-committed,completed}` — c5.
- `M-V3-SPINE-1/rehtdemucs-operator-section-{spec-committed,completed}` — c5.
- `M-V3-SPINE-1/muscriptor-operator-section-determinism-verified` — c5, 7/7 byte-det.
- `M-V3-SPINE-1/canonical-midi-operator-section-determinism-verified` — c5.
- `M-V3-SPINE-1/tempo-map-operator-section-chosen` — c5, 90.6661 BPM.
- `M-V3-SPINE-1/per-stem-midi-operator-section-merged` — c5, merged.mid SHA `2abfd6b98caa1043…`.
- `M-V3-SPINE-1/full-mix-reconciliation-operator-section-emitted` — c5.
- `M-V3-SPINE-1/render-plus-vocals-overlay-operator-section` — c5.
- `M-V3-SPINE-1/rc7-per-stem-loudness-operator-section-computed` — c5.
- `M-V3-SPINE-1/mix-match-operator-section-applied` — c5, full mix SHA `cc919559b4508b6b…`.
- `M-V3-SPINE-1/ab-delivery-operator-section-emitted` — c5.
- `M-V3-SPINE-1/panel-regression-operator-section-checked` — c5.
- `M-V3-SPINE-1/verdict-{operator-section,c6,c7,c8,c9,c10..c19}-emitted` —
  cycle-scoped `V3_SPINE_C<N>_..._pending_operator` verdicts with
  three-way `rubric_hash_v2` byte-equality.
- `M-V3-SPINE-1/env-drift-deep-dive-{spec-committed,completed}` — c6, torch 2.13.0+cpu on disk.
- `M-V3-SPINE-1/rc7-method-equivalence-{spec-committed,completed}` — c6, methods numerically differ.
- `M-V3-SPINE-1/rc7-v2-rerun-v3-paths-implemented` — c6.
- `M-V3-SPINE-1/torch213-reproduce-probe-{c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19}-completed` —
  thirteen dry-run liveness rolls, venv SHA byte-identical across.
- `M-V3-SPINE-1/rc7-canonicality-note-completed` — c7.
- `M-V3-SPINE-1/empty-stem-duration-sanity-completed` — c7,
  full-mix 30 s ok, empty stems ≈ 2 s tail flush.
- `M-V3-SPINE-1/verdict-c7-sha-drift-amended` — c8 amendment JSON.
- `M-V3-SPINE-1/operator-lands-2026-09-02` — c20 LANDS on
  Chicken Grease.
- `M-V3-FOCUS-1/chicken-grease-slot-accepted` — c20 mandatory fill.
- `M-V3-FOCUS-1/rome-{htdemucs-section,htdemucs-full-song,muscriptor,verdict}-completed` — c20 clone-1.
- `M-V3-FOCUS-1/wig-verdict-c20-emitted` — c20 clone-0 PARTIAL.
- `M-V3-SPINE-1/verdict-c20-peach-dream-emitted-partial-clone-2` — c20 clone-2 PARTIAL.
- `M-V3-FOCUS-1/rome-slot-accepted-internal-gate` — c20 D-A.
- `M-V3-FOCUS-1/wig-{muscriptor,canonical-midi,merge,render-mix,verdict-c21,anchor-preservation-c21}-completed` — c21 clone-1 restart LANDS.
- `M-V3-FOCUS-1/disco-a-{htdemucs-section,htdemucs-full-song,muscriptor,verdict}-emitted` — c21 clone-0 LANDS.
- `M-V3-FOCUS-1/disco-a-slot-accepted-internal-gate` — c21.
- `M-V3-FOCUS-1/wig-slot-operator-accepted-2026-09-02`,
  `.../disco-a-slot-operator-accepted-2026-09-02`,
  `M-V3-FOCUS-1/operator-satisfied-2026-09-02` — operator
  ear verdicts recorded 2026-09-02.
- `M-V3-SPINE-1/chicken-grease-palette-{render,/rubric-committed,/fetchability-probed,/per-stem-rendered,/panel-emitted,/delivery-emitted,/verdict-emitted}` — c21 clone-2 PALETTE_MOVES_PANEL.
- `M-V3-SPINE-1/chicken-grease-palette-proof-landed-c21` — closeout.
- `M-V3-SPINE-2/{unified-driver-spec-committed,unified-driver-implemented,env-pin-manifest-implemented,reproduce-proof-chicken-grease,reproduce-proof-rome,peach-dream-first-unified-driver-delivery}` — c22.
- `_infra/retire-oneoff-drivers-c22` — c22 catalog only, deferred deletion.
- `M-V3-SPINE-2/reproduce-proof-{chicken-grease,rome}/{rubric-committed,driver-invoked,verdict-emitted}` — c23 REPRODUCE_PANEL_ONLY.
- `M-V3-SPINE-2/reproduce-proof-authorizes-c24-retirement` — c23.
- `M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery/c23-partial-honest` — c23 clone-1 session-boundary termination.
- `M-V3-RULES-1/first-activation` + 7 sub-leaves — c23 clone-2 76 rules extracted, byte-deterministic ×2.
- `M-V3-SPINE-2/stage-checkpointed-driver` — c24 per-stage cache.
- `M-V3-FOCUS-1/peach-dream-resume-checkpointed` — c24 planned.

### V4 closure campaign

- `M-V4-CERT-1` — determinism certificate `E2E_DETERMINISM_HOLDS`
  under `env_pin_sha256 = 623df01f…6571d38d`. Reads as
  already-green on c1 opening; verify certificate on disk still
  reconstructs.
- `M-V4-PROFILES-1/cg-bass-sweep-{launched,completed}` — c1 (15
  presets, program 17 top-1, program 33 rank 8, spread 34 %).
- `M-V4-PROFILES-1/cg-bass-stage2-{launched,completed}` — c2 (180
  cells, top-1 prog 17, embedding_cos 0.141 below 0.40 floor).
- `M-V4-PROFILES-1/cg-bass-profile-v1-emitted` — c2 `bass.json`.
- `M-V4-PROFILES-1/cg-bass-sf2-replay-proof` — c2 REPLAY_PROOF_HOLDS.
- `M-V4-PROFILES-1/cg-bass-stage2b-{launched,completed}` — c3 (216
  cells, EQ-v2 no zero-mean; top-1 prog 33 by composite,
  emb_cos 0.204, top-emb prog 19 organ 0.495).
- `M-V4-PROFILES-1/cg-bass-family-verdict` — c4 STILL_INDETERMINATE.
- `M-V4-PROFILES-1/cg-bass-profile-v2-emitted` — c4 `bass_v2.json`
  program 33 top-composite.
- `M-V4-PROFILES-1/cg-bass-sf2-replay-proof-v2` — c4 same SHA as v1
  (revealed the c4 CRITICAL: replay silently ignores profile
  program because it reads program_change from the MIDI).
- `M-V4-PROFILES-1/profile-writer-canonical-replay-field-added` — c3.
- `M-V4-PROFILES-1/cg-bass-family2-stem-sampled` — c5 spec + spike.
- CRITICAL replay-program-invariance fix — c6, `replay.py` L82-83
  rewritten to strip incoming program_change and insert one per
  the profile.
- `M-V4-PROFILES-1/cg-bass-family2-verdict` — c6 FAMILY2_RULED_OUT
  at emb_cos 0.0896.
- `M-V4-PROFILES-1/cg-bass-arc-closeout` — c7
  CG_BASS_ARC_EXHAUSTED_NO_CONFIRMED.
- `_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy` — c7 escalation.
- Operator directive 2026-09-03 (in the report §Introduction of c7-9):
  wait-on-operator heartbeat BANNED for v4; heartbeat-only cycles
  are a discipline violation from c9 onward.
- `M-V4-PROFILES-1/cg-bass-showcase-accepted` — c9 OPT1+OPT3
  hybrid: accept `bass_v2` composite-relative winner; retire the
  0.60 CONFIRMED threshold, keep 0.40 RULED_OUT floor.
- `M-V4-SHOWCASE-1/cg-ab-driver-scaffolded` — c9,
  `deliver_cg_ab_v4.py` scaffold with 4 missing profiles expected.
- `M-V4-PROFILES-1/cg-drums-sweep-launched` — c9 launch deferred
  due to disk-check false positive.
- `M-V4-PROFILES-1/cg-drums-sweep-completed` — c11 (first-act
  closes c10 disclosure gap): 8 GM drum kits, top-1 program 48
  Orchestra Kit, program 0 rank 8.
- `M-V4-PROFILES-1/cg-drums-stage2-{launched,completed}` — c11 (216
  cells, top-1 prog 16 Power Kit, emb_cos 0.2374).
- `M-V4-PROFILES-1/cg-drums-profile-v1-emitted` — c11.
- `M-V4-PROFILES-1/cg-drums-sf2-replay-proof` — c11 (uses NEW
  channel-aware replay path in `replay.py`).
- `_infra/replay-channel-aware-fix-c11` — c11 CRITICAL fix.
- `M-V4-PROFILES-1/cg-drums-family-verdict` — c11 SF2_RULED_OUT.
- `M-V4-PROFILES-1/cg-drums-family2-{stem-sampled,verdict,replay-proof}` — c12 FAMILY2_RULED_OUT emb_cos 0.0372.
- `M-V4-PROFILES-1/cg-drums-arc-closeout` — c12.
- `_manager/M-V4-SHOWCASE-1-cg-drums-acceptance-policy` — c12.
- `_infra/replay-channel-aware-independent-reverify-c12` — c12 REPLAY_REGRESSION_HOLDS from fresh subprocess.
- `_manager/M-V4-SHOWCASE-1-cg-drums-acceptance-fork-c13`,
  `M-V4-PROFILES-1/cg-drums-showcase-accepted` — c13 initial OPT1
  (below-floor) selection later revised (see c14 revise below).
- `M-V4-PROFILES-1/cg-piano-null-finding` — c13 (later grounded c14).
- `M-V4-PROFILES-1/cg-guitar-sweep-{launched,completed}` — c13
  (8 GM programs, top-1 prog 24 Nylon Guitar, source-of-truth
  prog 27 Rock Guitar rank 2).
- `M-V4-SHOWCASE-1/cg-drums-acceptance-revised-c14` — c14
  CRITICAL closure of c13 audit findings; drums shifts to
  OPT3 (refuse showcase, use htdemucs stem).
- `_infra/agent-picks-selection-invariants-c14` — invariants (a)/(b)/(c).
- `M-V4-PROFILES-1/cg-piano-null-finding-grounded-c14` — RMS -81.53 dBFS.
- `M-V4-PROFILES-1/cg-other-null-finding-c14` — RMS -81.73 dBFS.
- `M-V4-PROFILES-1/cg-guitar-stage2-{launched,completed}` — c14
  (180 cells, top-1 prog 28 Muted Electric Guitar, emb_cos 0.2584).
- `M-V4-PROFILES-1/cg-guitar-profile-v1-emitted` — c14.
- `M-V4-PROFILES-1/cg-guitar-sf2-replay-proof` — c14.
- `M-V4-PROFILES-1/cg-guitar-family-verdict` — c14 SF2_RULED_OUT.
- `_infra/guitar-stage2-grid-deviation-disclosed-c15` — c15 retroactive
  disclosure of on-disk vs brief grid discrepancy.
- `_infra/interpreter-guard-policy-c15` — c15.
- `M-V4-PROFILES-1/cg-guitar-family2-{stem-sampled,replay-proof,verdict}` — c15
  FAMILY2_RULED_OUT emb_cos 0.0354.
- `M-V4-PROFILES-1/cg-guitar-arc-closeout` — c15.
- `M-V4-PROFILES-1/cg-guitar-showcase-accepted` — c15 OPT3
  auto-resolved via invariants.
- **CRITICAL escalation `_infra/embedding-metric-semantics-diagnosed-c16`,
  `_manager/M-V4-METRIC-SEMANTICS-c16`,
  `_plan/embedding-metric-semantics-operator-escalation-c16`** — c16
  probe verdict `metric_is=distance`; escalation is blocked-on-operator
  because path A (thresholds inverted) vs path B (`1 − distance` fix)
  changes every prior verdict.
- `_infra/pinned-profile-shape-invariant-e-c16` — c16.
- `M-V4-SHOWCASE-1/cg-ab-full-render` — c17 (`cg_ab_mix.wav` SHA
  `6e13e0075c5d8116…`, byte-det ×2 HOLDS).
- `_infra/deliver-cg-ab-v4-full` — c17.
- `M-V4-PROFILES-1/wig-opened`, `M-V4-PROFILES-1/rome-opened`,
  `M-V4-PROFILES-1/disco-a-opened`, `M-V4-PROFILES-1/peach-dream-opened` —
  c17 / c18 / c19 stem-manifests only, sweeps blocked on
  metric-semantics operator resolution.
- `M-V4-RULES-1/pinned-profile-schema-v1` — c17 draft-07 schema.
- `_infra/pinned-profile-schema-rationale-c18` — c18.
- `_infra/bass-gain-narrative-clarification-c18` — c18.
- `_infra/cg-ab-mix-lufs-diagnostic-c18` — c18 pyloudnorm probe
  (mix -15.32 LUFS-I).
- `_infra/adopt-cycle{18,19,20}-*-tests` — c18/c19/c20 test-debt fill.
- `M-V4-RULES-1/scaffold-c20` — c20 stubs; substantive Model A /
  Model B implementation queued c21+.

### Legacy / periodic

- Egress-probe rows for every cycle (`M-INGEST-1/egress-probe-cycle<N>`
  for c3..c22 v3-spine + and legacy `-cycle3..-cycle24` variants),
  all recording HTTP 429 + tv_embedded honestly. Non-blocking.
- `_plan/register-c<N>-*-sub-leaves`, `_archive/cycle-<N>-scratch`,
  `_infra/adopt-cycle<N>-tests`, `_run/cycle_<N>_closed` — the
  hardened housekeeping quartet emitted per cycle (v3 c8+, v4 c9+).

## §4. Verify slicing (5 passes)

- **Slice A (verify 1) — V3-SPINE heartbeat chain + operator LANDS.**
  M-V3-SPINE-1 sub-leaves c3–c19: rubric-v2 chain, canonical
  serializer, operator-section deliverables, thirteen-cycle
  torch-213 dry-run venv byte-identity, verdict backref chain,
  operator LANDS 2026-09-02.

- **Slice B (verify 2) — V3-FOCUS-1 fanout + palette proof.**
  Rome c20 LANDS; WIG c20 PARTIAL → c21 LANDS restart; Disco A
  c21 LANDS; Peach Dream c20 clone-2 PARTIAL Option 3 escape;
  operator ear satisfaction 2026-09-02; Chicken Grease palette
  render `PALETTE_MOVES_PANEL` c21 clone-2.

- **Slice C (verify 3) — V3-SPINE-2 unified driver + certificate + checkpointed driver.**
  c22 `recreate_v3.py` + env_pin.py + Peach Dream first delivery;
  c23 REPRODUCE_PANEL_ONLY for CG + Rome; c24
  stage-checkpointed driver; M-V4-CERT-1 certificate re-verify;
  M-V3-RULES-1 first activation c23 (76 rules artifact SHA
  `e19fb205b282dabb…`).

- **Slice D (verify 4) — V4 Chicken Grease bass + drums arcs.**
  M-V4-PROFILES-1 CG-bass c1–c9 (stage-1/2/2b + STILL_INDETERMINATE
  + family-2 + arc closeout + acceptance fork + OPT1+OPT3 accept +
  replay CRITICAL fix); CG-drums c9–c13 (SF2_RULED_OUT +
  FAMILY2_RULED_OUT + channel-aware replay fix + independent
  reverify + acceptance fork + c14 revise to OPT3).

- **Slice E (verify 5) — V4 CG-guitar + null findings + showcase + skeletons + metric-semantics escalation + rules scaffold.**
  CG-guitar c13–c15 arc, piano/other NULL grounded c14,
  CG-drums acceptance revised c14, invariants (a)–(e), metric-semantics
  CRITICAL escalation c16 (probe + escalation JSON + fork),
  CG A/B render c17, WIG/Rome/Disco A/Peach Dream v4 skeletons c17–c19,
  pinned-profile schema c17 + rationale c18, LUFS diagnostic c18,
  M-V4-RULES-1 scaffold c20.

## §5. First-pass concerns (verdict-pending)

Items I want the verify passes to press on:

1. **Metric-semantics distance-vs-similarity CRITICAL (c16).** If
   `metric_is = distance`, then every prior "emb_cos_vggish ≥ 0.60"
   / "≤ 0.40" gate has been read with inverted semantics. Every
   sf2 SF2_RULED_OUT verdict (drums c11, guitar c14, both because
   top-1 emb_cos below 0.40 floor) may have identified the closest
   preset rather than the furthest. Every FAMILY2_RULED_OUT
   likewise. bass_v2 acceptance (top-1 by composite prog 33
   emb_cos 0.204 low) becomes "closest to reference", not
   "worst of the sweep". The escalation is honestly blocked
   on operator; verify that no downstream cycle *silently*
   re-interprets under path A or path B.

2. **Missing v4 c19–c20 cycle reports.** The plan-of-record
   documents c19 (Disco A + Peach Dream v4 opens + LUFS
   FETCH_FAIL test) and c20 (M-V4-RULES-1 scaffold) but no
   `report_cycles_19-*.md` or `report_cycles_20-*.md` exists.
   Verify per-milestone artifacts on disk.

3. **Chicken Grease bass v2 acceptance path A (OPT1+OPT3
   hybrid).** c9 retired the 0.60 CONFIRMED threshold as a kill
   gate but kept 0.40 as absolute floor. Operator directive
   quoted verbatim in the c7-9 report. Under c16 distance
   diagnosis this rescue path itself may need re-interpretation.

4. **v3 SPINE cycle-c7 SHA drift.** c8 recorded that
   `rc7_canonicality_note.sha256` in c7 verdict.json disagreed
   with the on-disk note SHA. Amendment emitted append-only;
   verify the amendment JSON parses and cites both SHAs.

5. **v3 SPINE-2 unified driver retire-oneoffs deferral.**
   `_infra/retire-oneoff-drivers-c22` cataloged 37 per-song
   scripts but explicitly deferred deletion. Verify catalog on
   disk lists exactly 37 files under the expected paths and no
   files were prematurely deleted.

6. **Peach Dream v3 first-unified-driver delivery.** c22 stated
   "may land as partial with named block"; c23 recorded
   `c23-partial-honest` under `stage_3_of_9_muscriptor` session
   boundary. Verify c22 `verdict.json` on disk and c23
   PARTIAL delivery agree with the reported block point.

7. **c21 Chicken Grease palette proof.** `PALETTE_MOVES_PANEL`
   fires on 4-of-5 numeric-panel keys exceeding a 5 % relative
   threshold on Comparison B. Panel is never a LANDS gate per
   FD-6. Verify verdict.json rubric_hash_v2 chain and c5
   operator-blessed delivery byte-identical pre==post.

8. **Housekeeping-quartet coverage.** Verify each v3 c3..c22 and
   v4 c1..c20 cycle emits four housekeeping rows
   (`_run/cycle_<N>_closed`, `_archive/cycle-<N>-scratch`,
   `_infra/adopt-cycle<N>-tests`, `_plan/register-c<N>-*`) or
   documents the omission honestly.

9. **Post-baseline egress-probe registry.** Cycles c3..c22 v3
   and c1..c20 v4 should each carry one `M-INGEST-1/egress-probe-cycle<N>`
   row. Verify the registry is unbroken; any missing cycle is a
   reporting_gap under the c49 policy path B.

10. **V3-RULES-1 first activation determinism.** c23 clone-2
    rules artifact 76 rows byte-deterministic ×2 into fresh
    tempdirs. Verify SHA on disk == `e19fb205b282dabb…`.

## §6. Exit gates

- Critical path examined: v3 SPINE heartbeat + operator LANDS +
  focus fanout + palette proof + unified driver + certificate +
  v4 CG arcs + escalations. Yes.
- Findings classified by severity: deferred to verify slices;
  first-pass concerns above are candidates, not classifications.
  Yes.
- CRITICAL/MODERATE items to act on in verify: yes (metric-semantics
  escalation is a CRITICAL-in-waiting; several MODERATE
  reporting-gap and schema-drift candidates identified).

## §7. Transition

Advance to verify_1 (Slice A). Total stages = 12 (1 explore + 5 verify
+ 5 test + 1 document). No wall-cap concern. All READ-ONLY.
