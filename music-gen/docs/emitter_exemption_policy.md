# Emitter Exemption Policy — `tools/_emit_c*_ledger_events.py` chain

Created: 2026-09-05T07:00:00Z
Cycle: 34
Run: run-2026-09-05T070000Z
Agent: worker
Milestone: `_infra/emitter-writer-boundary-exemption-c34`

## Purpose

Codifies a formal exemption for the per-cycle ledger emitter chain
(`tools/_emit_c30_ledger_events.py` through `tools/_emit_c33_ledger_events.py`,
plus this cycle's `tools/_emit_c34_ledger_events.py`) from routing through
`long_exposure.workspace_bootstrap.append_ledger_event`. The exemption is
narrow: it applies ONLY to the per-cycle emitter chain, not to arbitrary
new code that writes to `promise_ledger.jsonl`.

## Rationale

The workspace does NOT contain the `long_exposure/` package. `ls
long_exposure/` returns `No such file or directory`. The c14+
`append_ledger_event` helper — which enforces validation, UUID5
content-hash derivation, `_STATUS_ENUM`, and `supersedes_path` typing —
lives in an out-of-workspace orchestrator that is not importable from
this run's Python environment.

Under this constraint, OPT_A of the c34 brief (route c34 emitter through
`append_ledger_event`) is not executable this cycle. Per the c34 brief's
auto-resolve rule — "If `long_exposure/` importable in workspace → OPT_A.
If not → OPT_B (document formal exemption)" — the fork lands on OPT_B.

## Contract the exempted emitter chain honors

Each `_emit_c*_ledger_events.py` script must, without importing
`long_exposure.workspace_bootstrap`:

1. Compute `event_id` as `uuid.uuid5(uuid.NAMESPACE_URL, canonical_json)`
   over the event body minus `event_id` and `ts` (the same content-hash
   contract `append_ledger_event` uses).
2. Emit `status` in the c14+ `_STATUS_ENUM`
   (`in-progress | validated | invalidated | superseded | action_required`).
3. Emit `supersedes_path` as `str` or `null`, never `list`, per the c14
   lemma.
4. Emit `confidence` as a nested object `{level, rationale, assessor}`,
   with `level` in `low | medium | high`.
5. Emit `narrative` (not `summary`) as the free-text field.
6. Pin `run_id`, `env_pin_sha256`, and `cycle`.
7. Serialize each event via `json.dumps(ev, sort_keys=True,
   separators=(",", ":"))` so canonical-JSON round-trip is stable.
8. Guard idempotency via a sentinel file
   (`tools/.c<N>_ledger_emitted`) that prevents double-emission on
   re-run within the same cycle.

Every emitter in the c30-c33 chain honors 1-8. This cycle's
`tools/_emit_c34_ledger_events.py` extends the pattern verbatim.

## What the exemption does NOT cover

- Any NEW code path that writes to `promise_ledger.jsonl` from outside
  the per-cycle emitter chain (e.g., a hypothetical driver that logs
  live ledger events during a sweep). Such code MUST route through
  `append_ledger_event` when `long_exposure/` becomes importable.
- Any emitter that skips the UUID5 content-hash computation or that
  serializes with non-canonical JSON. Baseline stability (16 pre-existing
  `promise_check` ERRORs, zero c30-c33-introduced) is contingent on the
  chain's disciplined adherence to items 1-8.

## Re-open trigger

If `long_exposure/` is later added to the workspace, this exemption is
retired. The c35+ emitter should route through `append_ledger_event` and
this policy doc should be updated with a supersede event pointing at the
substitute policy (`supersedes_path` as `str` per the c14 lemma).

## Cross-references

- c14 lemma on `supersedes_path` typing: `docs/ledger_schema_hardening_v2.md`
  (referenced by `long_exposure/tools/_ledger_schema.validate_event`
  contract).
- c33 auditor MODERATE #2 finding: the writer-boundary drift observation.
- c34 brief Priority 1: this exemption is the OPT_B branch of the
  three-option fork; the fork is recorded in
  `data/v4/_selection/c34-emitter-writer-boundary.json`.

## Invariant compliance

Invariants (a)-(e) from `docs/agent_picks_selection_invariants.md`
applied to the c34 Priority 1 fork:

- (a) no operator-scope extension — OPT_B does not extend operator scope;
  it documents a status-quo exemption grounded in a workspace fact.
- (b) prefer above-line — OPT_B closes a c33 auditor MODERATE finding
  (above-line); OPT_C would leave the debt (below-line). Not applicable
  as tie-breaker here since OPT_A is unreachable.
- (c) do not reject an option based on misreading its own definition —
  OPT_A is rejected because `long_exposure/` is absent, not because of
  a definitional error.
- (d) on-disk-vs-brief divergence — the c34 brief presumed `long_exposure/`
  MIGHT be importable; on-disk it is not. This divergence is disclosed
  here per invariant (d).
- (e) cross-cycle exemption-shape stability — no on-disk pinned-profile
  or verdict shape is mutated; the exemption is a documentation-only
  artifact.
