# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES
# ---
"""v4 sound-matching satellite (M-V4-PROFILES).

Pure programs. No PRNG in production code paths. Interpreter guard is
/usr/bin/python3. The winning profile and its replay are strictly
deterministic; the search step may be stochastic per the two-phase policy.
"""
