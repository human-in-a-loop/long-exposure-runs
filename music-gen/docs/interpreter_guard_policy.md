# Interpreter Guard Policy (c15 codification)

**Authority**: c14 auditor RECOMMENDED item #5; formalizes the pre-c12
interpreter shebang variance surfaced during c14 test-debt cleanup.

**Scope**: applies to every Python script under `scripts/sound_match/`
and its siblings introduced by the v4 sound-matching layer campaign.

## Canonical shebang

New scripts (c13 onward) MUST use:

    #!/usr/bin/python3

Rationale: the project has used the absolute-path interpreter guard
since c1 (`coarse_sweep_sf2.py`) to make invocation explicit and to
avoid PATH-derived Python drift across cycles.

## Grandfathered exceptions (pre-c13 anchors)

The following pre-c13 anchor scripts use `#!/usr/bin/env python3` and
are grandfathered as READ-ONLY per FD-1 (never mutate an anchor):

- `scripts/sound_match/family2_stem_sampled_drums_spike.py` (c12)
- `scripts/sound_match/family2_stem_sampled_drums_builder.py` (c12)
- Any prior sibling that predates c13 with the `env`-variant shebang.

On this system both forms resolve to `/usr/bin/python3`, so
grandfathering is safe. Test enforcement in
`tests/test_sound_match_family2_drums.py` (c14) accepts both forms
for c12 anchors; tests for c13+ new code accept only the canonical
form.

## Test enforcement contract

- Tests targeting a c12-or-earlier anchor: accept both
  `/usr/bin/python3` AND `/usr/bin/env python3`.
- Tests targeting c13+ new code: reject anything other than
  `/usr/bin/python3`.

## Interaction with binding specs

Sits under FD-1 (no tuning/retry/fallback — anchor mutation banned) and
the c14-codified agent-picks selection invariants (a/b/c) + c15
invariant (d). Does NOT interact with FD-6 (operator ear = LANDS
authority) or FD-16 (env_pin / replay proof scoping) — this is a code
hygiene policy only.

## Version

- c15 (2026-09-04): initial codification.
