"""M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization — c36 Branch C.

Peer sub-milestone under M-DAW-SPIKE-1 (per c29 lemma). Analytical
characterization of the c35 Branch A VST3-binary-internal
nondeterminism finding. Small-perturbation vs structural-drift verdict
under the frozen `SMALL_PERTURBATION_TOLERABLE / STRUCTURAL_DRIFT /
MIXED` rubric committed BEFORE any script under this package landed
(rubric doc: docs/vst3_nondeterminism_characterization_rubric.md;
rubric SHA at data/vst3_nondeterminism/rubric_hash.txt).

Anti-pattern discipline: the c31 STILL_GAP + c35 A state-extraction
surface (five call names) is AST-forbidden throughout this package;
see tests/test_vst3_nondeterminism_characterization.py for the
enforced list.
"""
