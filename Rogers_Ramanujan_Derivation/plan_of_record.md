---
created: 2026-05-14T23:23:11Z
run_id: run-2026-05-14T232311Z
agent: researcher
---

# Plan of Record — # Long-Exposure Prompt: Derive the Rogers-Ramanujan Identiti

**Created:** 2026-05-14T23:23:11Z
**Run id:** run-2026-05-14T232311Z

## Directive (verbatim)

# Long-Exposure Prompt: Derive the Rogers-Ramanujan Identities from First Principles

You are running an autonomous long-exposure mathematics demonstration. Your task is to derive and prove the two Rogers-Ramanujan identities from first principles, without looking up the proof, without using web search for the mathematical content, and without copying a known proof from memory as an unexplained artifact.

The target identities are:

\[
\sum_{n \ge 0} \frac{q^{n^2}}{(q;q)_n}
=
\prod_{m \ge 0} \frac{1}{(1-q^{5m+1})(1-q^{5m+4})}
\]

and

\[
\sum_{n \ge 0} \frac{q^{n^2+n}}{(q;q)_n}
=
\prod_{m \ge 0} \frac{1}{(1-q^{5m+2})(1-q^{5m+3})}.
\]

Here \((q;q)_n=\prod_{k=1}^{n}(1-q^k)\). Work in the formal power series setting where possible; analytic convergence arguments may be added later, but the core proof should not depend on numerical evidence.

## Core Ask

Produce a rigorous, self-contained derivation and proof. The run should decide its own strategy, but it must keep the work derivational: build lemmas, prove finite identities, test conjectured recurrences symbolically, and only promote a result when the proof chain is explicit.

## Constraints

- Do not use web search or external lookup to retrieve the proof or a textbook exposition.
- You may use Wolfram Language through the local `wolfram-bridge` skill/tool and through `wolfram-batch` for symbolic manipulation, recurrence discovery, coefficient checks, finite polynomial experiments, and sanity checks.
- You may use Python/SymPy as a secondary check, but the final proof must be mathematical, not just computational.
- If a route fails, preserve the failed route and pivot explicitly.
- Avoid treating many coefficient checks as proof. Use them only to discover or falsify candidate lemmas.

## Suggested Starting Routes

These are suggestions, not requirements. Long-exposure should refine or replace them as it learns.

1. Finite polynomial approximants:
   Define finite sums and finite products, compute recurrences, and search for a pair of finite identities whose limit gives the target identities.

2. q-difference equations:
   Show that the series side and product side satisfy the same coupled q-difference system with the same initial data.

3. Partition interpretation:
   Build a formal bridge between partitions with adjacent difference at least two and partitions into parts congruent to selected residues modulo five, but do not rely on a memorized bijection unless it is derived and verified.

4. Bailey-pair or q-binomial route:
   If a Bailey-style transformation emerges, derive the needed special case rather than citing it.

## Expected Artifacts

- A plan of record with proof milestones.
- Wolfram notebooks or `.wls` scripts that test finite recurrences and coefficient expansions.
- A catalogue of lemmas with proof status: conjectured, experimentally verified, proved, or rejected.
- A final proof document that states assumptions, definitions, lemmas, and the proof chain.
- A validation document separating symbolic experiments from actual proof steps.

## Success Criteria

A successful run produces a readable proof skeleton or complete proof in which each major identity is justified by explicit algebraic, formal power series, or limiting arguments. Partial success is acceptable if it identifies a hard bottleneck precisely and leaves a reproducible symbolic trail for future work.

This is intended to be a difficult, multi-day reasoning benchmark. Continue autonomously; no user ratification or guidance will be provided to unblock decisions during the live run.

## Goals

| Goal ID | Goal | Owner |
|---------|------|-------|
| G1 | Establish a formal-power-series framework and reproducible experiment harness for Rogers-Ramanujan derivation. | researcher/worker/auditor |
| G2 | Derive a proof-bearing route from finite identities, q-difference systems, or an explicitly derived transformation. | researcher/worker/auditor |
| G3 | Produce a self-contained final proof and validation record distinguishing experiments from proved lemmas. | researcher/worker/auditor |

## Milestones

| Milestone ID | Goal | Description | Success criteria (falsifiable) | Dependencies |
|--------------|------|-------------|--------------------------------|--------------|
| M0 | G1 | Formal setup and notation ledger: define rings, truncation semantics, q-Pochhammer conventions, and acceptable limit operations. | `docs/lemmas/lemma_catalogue.md` contains definitions and at least the formal coefficientwise convergence lemmas needed to pass from finite/truncated statements to infinite series/products. | — |
| M1 | G1/G2 | Finite approximant exploration: compute and compare bounded sum/product candidates, recurrences, and coefficient tables without treating checks as proof. | Reproducible scripts in `scripts/rr/` write finite data to `data/finite_experiments/`; validation notes state at least two candidate finite recurrences/identities with proof status. | M0 |
| M2 | G2 | Discover and prove a transfer mechanism linking the series side to a modular product side: finite polynomial recurrence, q-difference system, or derived Bailey/q-binomial transformation. | At least one mechanism is stated as lemmas with algebraic proof, falsification tests, and no unexplained invocation of a named Rogers-Ramanujan proof. | M0, M1 |
| M3 | G2 | Product-side formalization: prove the selected mechanism yields residues 1,4 and 2,3 modulo 5 products by coefficientwise formal arguments. | `docs/proof/product_side.md` proves the product identities from the mechanism and documents any finite-to-infinite limiting step. | M2 |
| M4 | G3 | Final proof synthesis and validation separation. | `docs/proof/final_proof.md` is self-contained; `docs/validation.md` lists every computational experiment and marks it as discovery, sanity check, or proof-supporting symbolic verification. | M0-M3 |

## Out of scope (explicit)

- Web search or external lookup of textbook proofs.
- Numerical coefficient agreement as a substitute for proof.
- Analytic convergence arguments unless clearly secondary to a formal-power-series proof.

## Pointer to ledger

Every milestone status, history, and judgment lives in `promise_ledger.jsonl`,
filtered by `milestone_id`. Run `promise_check` to materialize the current
state for the human; agents call it via Bash:

    python3 -m long_exposure.tools.promise_check .

The directive section above is **immutable** after creation. Goals and
milestones tables are mutable, but every edit must emit a ledger event with
`milestone_id: "_plan/<descriptive-change-name>"` so the audit trail is
complete.
