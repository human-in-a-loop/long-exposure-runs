# Sweep-Driver Family Policy — Other-Family Sibling Authoring Plan (c60)

**Author:** worker (c60)
**Milestone:** _plan/sweep-driver-other-authoring-plan-c60
**Parent policy:** `docs/sweep_driver_family_policy.md` sha
`1546a6fc01e141a0bfdad41672a3f659083c1adf543e78761f9beb2206c73269`
(c59 P4 codification)
**Scope:** Pre-register c61+ `scripts/sound_match/coarse_sweep_sf2_other.py`
sibling per parent-policy steps 1–4. Parallel to c60 P1 authoring of
`coarse_sweep_sf2_piano.py`. Advances operator directive #5(c) queue
(piano → **other** → vocals SKIP → guitar SKIP).

---

## §1 Parent-policy step 1: OPT_A audit

**Question:** Does `scripts/sound_match/coarse_sweep_sf2.py` (bass-anchor
driver, sha `3f8bfa08…4129`) contain hardcoded assumptions blocking
"other"-family reuse via a threaded `--instrument` kwarg?

**Answer:** **Yes** — same three call sites already documented for the
piano case at c59 P3 (which surfaced the OPT_A → OPT_B pivot):

| Line | Symbol | Hardcode | Blocks other-family reuse? |
|---|---|---|---|
| L178 | `_extract_bass_midi` | `t.name == "bass"` string literal | **Yes** — must match `"other"` |
| L96  | `_rewrite_bass_midi_with_program` | `channel=0` in three msg constructors | **No** (other is pitched, same as bass/piano) |
| L266 | `main()` | unconditional call to `_extract_bass_midi` | **Yes** — no dispatch on args.instrument |

**Verdict:** OPT_A (additive `--instrument` kwarg thread) requires
touching the READ-ONLY anchor to change `_extract_bass_midi`'s track-name
selector or add a dispatch layer. This violates parent-policy rule 3
("do not modify existing per-instrument drivers"). **OPT_B required**:
author sibling driver `coarse_sweep_sf2_other.py`.

Same conclusion as c59 P3 for piano. The OPT_A → OPT_B pattern is
structurally invariant across pitched-family siblings; anchor policy
means every new pitched-family sibling ships as its own driver.

---

## §2 Parent-policy step 2: sibling authoring shape

Copy `scripts/sound_match/coarse_sweep_sf2.py` (bass anchor, READ-ONLY)
to `scripts/sound_match/coarse_sweep_sf2_other.py` (new sibling). Apply
the same minimal-diff shape used for c60 piano:

1. Rename `_extract_bass_midi` → `_extract_other_midi`; change
   `t.name == "bass"` → `t.name == "other"`.
2. Rename `_rewrite_bass_midi_with_program` →
   `_rewrite_other_midi_with_program`. **Preserve `channel=0`** (other
   is pitched-family, same as bass/piano/guitar; drum ch10 does not
   apply).
3. Update docstring: cite parent policy sha `1546a6fc…` and this plan's
   file sha at authoring time.
4. Update all filename/reference strings: `bass_excerpt.mid` →
   `other_excerpt.mid`; `bass_with_program.mid` →
   `other_with_program.mid`; `no 'bass' track found` →
   `no 'other' track found`.
5. Update `main()` help text and description strings.
6. Update `run_manifest.json` payload `driver` field to
   `"coarse_sweep_sf2_other"` and `instrument` default via `--stem
   other`.

---

## §3 GM "other"-family program recommendation

Operator directive #5(c) names "other" as the **residual-content family**.
GM programs that best cover residual-timbre content (pads, string beds,
choir textures, sweep synths):

| Program | Name | Rationale |
|---|---|---|
| 48 | String Ensemble 1 | Sustained string beds common in residuals |
| 49 | String Ensemble 2 | Alternative string voicing |
| 52 | Choir Aahs | Vocal-adjacent residual textures |
| 88 | New Age Pad | Sustain pad, low-attack |
| 89 | Warm Pad | Warm sustain pad |
| 90 | Polysynth Pad | Poly-envelope pad |
| 95 | Halo Pad | Bright halo texture |
| 96 | Sweep Pad | Attack-sweep pad |

Default `--presets` in the c61 authoring:

    bank0:programs=48,49,52,88,89,90,95,96

**Operator confirmation:** RECOMMENDED but not required before c61
landing. Per anti-stall rule + c47 OPT1-extended, composite objective
ranks best-of-available across families; if the frozen composite selects
a non-source-of-truth program (e.g. pad ranking above strings on a
string-heavy other-residual stem), c60 P1 piano-sibling test coverage +
c11 systematic-pattern precedent (5 arcs where composite ranks non-SoT
ahead of SoT) tell us this is content-specific characterization, not a
defect.

---

## §4 Parent-policy step 3: test-coverage bar

Minimum 8-case regression suite `tests/test_sound_match_coarse_sweep_sf2_other.py`
mirroring `tests/test_sound_match_coarse_sweep_sf2_piano.py` (c60 P1)
verbatim per c13 guitar sweep precedent. Slots:

| # | Test | Contract |
|---|------|----------|
| 01 | script authored with `/usr/bin/python3` shebang | file exists + shebang |
| 02 | `--help` shows both `--song` and `--song-sha16` | argparse dest alias |
| 03 | AST-grep confirms no PRNG imports | random/numpy.random forbidden |
| 04 | AST-grep confirms no `sidecar_nonfactor` import | AST-only, prose OK |
| 05 | `--dry-run` (via `--help`) smoke test PASS | rc=0 + "other" mention |
| 06 | sweep-storage hygiene flags wired | 4 flags present |
| 07 | env_pin canonical 7-key subset in `_PINS` | 7 required keys |
| 08 | `sweep_driver_family_policy.md` sha cited | `1546a6fc…` present |

Substring probe on `sidecar_nonfactor` deliberately AST-scoped (not
grep-substring) per c60 P1 lesson: prose mentions in module docstrings
are the DOCUMENTED discipline, not a violation of it.

---

## §5 Parent-policy step 4: discipline gates

Non-negotiables for the c61+ sibling:

- **No PRNG** in production code paths (AST-grep clean).
- **No `sidecar_nonfactor`** imports (AST-grep clean).
- **`/usr/bin/python3`** interpreter guard on module + wrapping launch
  script.
- **No `--verify-det`** flag (per parent policy).
- **No VST3 state APIs** (`get_state`, `save_state`, `set_state(bytes)`,
  etc.) — SF2 only.
- **Sweep-storage hygiene** wired: `--score-and-delete --keep-top 3
  --max-audio-mb 500 --disk-abort-pct 90` per c27 canonical module.
- **env_pin canonical 7-key subset** recorded in `run_manifest.json`.
- **SF2 sha `74594e8f…1cb0`** verified in-run.

---

## §6 Deferred to c61+ (SHA-drift disclosure obligation)

Per invariant (d) (on-disk-vs-brief divergence disclosure norm), c61
authoring MUST record the new script SHA in a c61 SHA-drift closing-
summary section and disclose the sha for:

- `scripts/sound_match/coarse_sweep_sf2_other.py` — new.
- `tests/test_sound_match_coarse_sweep_sf2_other.py` — new.
- `docs/sweep_driver_family_policy_other_c60.md` — this file
  (READ-ONLY anchor at c61 open).

The bass driver (sha `3f8bfa08…4129`), drums driver (sha
`3466fe2e…` post c48 alias), guitar driver (sha `d6c54f21…` post c28
hygiene integration), and piano driver (this cycle's new sibling; sha
recorded in c60 closing summary) all remain READ-ONLY per parent-policy
rule 3.

---

## §7 Post-c61 downstream queue

Operator directive #5(c) after "other" arc closes:

1. **Vocals SKIP** per FD-6: operator ear is LANDS authority; the c15
   non-CG guitar family-1 SF2_RULED_OUT precedent applies to vocals
   substitution via htdemucs stem passthrough (OPT3 pattern from c14
   CG-drums acceptance). Do **not** auto-close vocals `SF2_RULED_OUT`;
   defer to operator listening.
2. **Guitar SKIP** family-1 per c15 SF2_RULED_OUT precedent per c58
   stem prioritization; use htdemucs stem substitution (OPT3 pattern).

Only piano (c60 P1) and other (this plan, c61+) require sibling drivers
under OPT_B; vocals + guitar do not.

---

## §8 Wall-budget estimate

Based on c60 P1 authoring wall time (piano sibling + 8 tests, ~30 min
including anchor reads + test-fix iteration for docstring-substring
false positive): c61 "other" sibling authoring should complete in ~30
min. Stage-1 launch (8 programs × 1 preset each) at ~2 s/program under
c48 alias precedent = ~16 s wall + hygiene checks. Stage-2 fine fit
per c11 drums stage-2 (216 cells × ~0.5 s each) = ~110 s wall.
Total c61 wall: ~50 min authoring + all sweeps. Fits within a single
cycle wall budget when disk ≤82%.

---

## §9 Provenance

- Parent policy: `docs/sweep_driver_family_policy.md` sha `1546a6fc…`
  (c59 P4).
- Piano sibling precedent: `scripts/sound_match/coarse_sweep_sf2_piano.py`
  (c60 P1) + `tests/test_sound_match_coarse_sweep_sf2_piano.py` (8/8 PASS).
- Bass anchor (READ-ONLY): `scripts/sound_match/coarse_sweep_sf2.py`
  sha `3f8bfa0822b62cc99ffcdb8cecfe950f4ccb0f5e1665cbeabfed782d27454129`.
- Operator directives: 2026-09-03 part 2 (anti-stall), 2026-09-03 part 3
  (drums scope), #5(c) queue codification via c59 P4.
- Invariants (a)-(f) from `docs/agent_picks_selection_invariants.md`
  sha `7df72aee18726dea37c3857f61bb58da04c615f4cd76eeef79a8d07dddabb499`.
