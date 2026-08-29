# ---
# created: 2026-08-29T09:07:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v4
# ---
"""M-GEN-1/palette-driven-batch-v4 — deeper-perturbation extension of c36 v3.

Ships the sfizz opcode-file-rewrite fallback deferred from c36, an 8×8
parameter_dict table (5 fluidsynth params + 3 sfizz params × 8 values each),
and an 8-salt batch (salts 0..7).

Anti-patterns locked: no PRNG, no sidecar_nonfactor, VST3 branches raise
NotImplementedError, c33 anchor SHAs preserved under parameter_dict=None.
"""
