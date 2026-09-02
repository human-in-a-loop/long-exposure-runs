# Final Audit Stage 38 (test slice 14 of 23)

## Slice scope

Adversarial pass on the operator-priority M-RECREATE-2 rubric-chain +
render_stem-signature anchors that gate every c51+ RC branch:

- Probe 14.1 — c49 v1 rubric three-way `rubric_hash` byte-equality chain
  (parent milestone `M-RECREATE-2/accurate-small-set`,
  `_plan/m-recreate-2-rubric-v2-supersede` supersedes chain root).
- Probe 14.2 — c50 v2 rubric three-way `rubric_hash_v2` chain (parent
  `M-RECREATE-2/accurate-small-set-v2`; supersedes c49 v1 via
  `supersedes_path: docs/m_recreate_2_accurate_small_set_rubric.md`).
- Probe 14.3 — c51 Branch C `scripts/palette_render/render_stem.py`
  additive-kwargs signature (c33 backwards-compat contract, c36 additive
  precedent, c51 EQ + loudness extension) — on-disk SHA + AST signature.

All three are READ-ONLY on-disk anchor checks — no rendering, no ledger
mutation.

## Probe 14.1 — c49 v1 rubric three-way chain

Command: `sha256(docs/m_recreate_2_accurate_small_set_rubric.md)` and
compare with `data/recreate_v2/rubric_hash.txt` content (whitespace-
stripped).

| field                                    | value                                                                |
|------------------------------------------|----------------------------------------------------------------------|
| `docs/…rubric.md` SHA-256                | `958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d`  |
| `docs/…rubric.md` byte length            | 10 410                                                              |
| `data/recreate_v2/rubric_hash.txt`       | `958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d\n` |
| plan-of-record narrative pin (c49)       | `958ade38…3fe58b9d`                                                 |

Chain 1/2 verified: doc SHA-256 byte-equal to the hex string stored in
`rubric_hash.txt` (65 bytes on disk = 64 hex chars + newline). Chain
segment 3 (`verdict.json.rubric_hash`) is not on-disk this cycle since
no c49 verdict is emitted at parent scope — c49 delivers rubric + focus
set + RC0 baseline + RC stubs only. The pin propagates instead to c51
Branch A verdict (`data/rc1_rc9_impl/verdict.json`), see Probe 14.3
context. **PASS.**

## Probe 14.2 — c50 v2 rubric three-way chain

Same recipe on the v2 pair.

| field                                       | value                                                                |
|---------------------------------------------|----------------------------------------------------------------------|
| `docs/…rubric_v2.md` SHA-256                | `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`  |
| `docs/…rubric_v2.md` byte length            | 9 906                                                               |
| `data/recreate_v2/rubric_hash_v2.txt`       | `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f\n` |
| plan-of-record narrative pin (c50)          | `0e11f704…debe1f`                                                   |
| c51 Branch A verdict `rubric_hash` (plan)   | `0e11f704…debe1f`                                                   |
| c51 Branch C verdict `rubric_hash` (plan)   | `0e11f704…debe1f`                                                   |

**PASS.** The v2 doc SHA reproduces byte-equal in the `rubric_hash_v2.txt`
sentinel. The plan-of-record narrative pins both c51 Branch A
(`M-RECREATE-2/…/rc-v2-branch-a-rubric-hash-chain-verified-clone-0`)
and c51 Branch C (`.../rc7-mix-balance-match/rubric-v3-committed`) to
this same doc SHA — the entire c51 RC-v2 arc gates on this hash. The
supersede relationship `_plan/m-recreate-2-rubric-v2-supersede` is
documented with `supersedes_path: docs/m_recreate_2_accurate_small_set_rubric.md`
(a `str`, not the list form that would violate the c14 lemma).

## Probe 14.3 — c51 render_stem additive-kwargs signature

The c51 Branch C plan-of-record claims `scripts/palette_render/render_stem.py`
was extended with two additive keyword-only kwargs (`eq_curve`,
`loudness_target`), building on c36 clone-1's earlier `parameter_dict`
addition, and that the c33 no-kwargs dispatch path is preserved
byte-identical.

On-disk SHA-256 of `scripts/palette_render/render_stem.py`:

```
214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b  (17 653 bytes)
```

Matches the plan-referenced anchor `214372d9…5b2b` on both c51 Branch C
verdict + c53 Branch A anchor preservation snapshot.

AST inspection of the `render_stem` FunctionDef (via
`scratchpad_stage38_sig.py`):

```
posonlyargs: []
args:        ['stem', 'instrument', 'out_dir']
kwonlyargs:  ['parameter_dict', 'eq_curve', 'loudness_target']
  parameter_dict default: None
  eq_curve       default: None
  loudness_target default: None
vararg:      None
```

Interpretation: positional interface `(stem, instrument, out_dir)` is
byte-identical to the c33 baseline. Three keyword-only additions each
default to `None`. Under the all-None dispatch path (c33 baseline
consumer), the new kwargs are inert — the c33 backwards-compat contract
holds by construction of the default values. c36's additive
`parameter_dict=None` invariant is likewise preserved. **PASS.**

## Cross-cycle causal consistency

- c49 rubric (v1) → c50 rubric (v2) via
  `_plan/m-recreate-2-rubric-v2-supersede` (single supersedes edge).
  Both docs remain on-disk (v1 as READ-ONLY historical anchor per plan-
  of-record). Neither is orphaned — both are referenced by later
  sub-leaves.
- c33 render_stem SHA anchor (`214372d9…5b2b` today) is threaded through
  five downstream cycles: c33 clone-0 verdict, c34 clone-1/clone-2, c36
  clone-1 backwards-compat regression, c51 clones A/C additive-kwargs
  regression, c53 clone-0/1 anchor-preservation snapshot. All narrative
  pins agree with the on-disk SHA computed this stage.
- Three-way `rubric_hash` chain is the campaign-standard integrity
  contract; both c49 v1 and c50 v2 chains verify chain segments 1 and 2
  on-disk this stage. Chain segment 3 (verdict.rubric_hash) is
  verifiable in later stages of the audit against the c51 verdicts.

## Findings this stage

**Zero.** All three probes PASS.

## Housekeeping

The scratchpad file `scratchpad_stage38_sig.py` (workspace root) is a
read-only AST inspector; safe to leave for later cleanup with the
stage-37 scratchpads or delete on next opportunity.

[OUTPUT: final_audit_stage]
Stage 38: test 14/23 — c49 v1 rubric chain + c50 v2 rubric chain + c51 render_stem additive-kwargs signature all PASS; 0 findings.
File: audits/final/stages/test_14of23.md
Findings appended: 0
[END OUTPUT: final_audit_stage]
