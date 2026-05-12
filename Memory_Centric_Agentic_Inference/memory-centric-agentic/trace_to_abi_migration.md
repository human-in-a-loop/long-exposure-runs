---
created: 2026-05-12T18:25:00Z
cycle: 44
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-TRACEABI-1
---

# Legacy Trace-to-ABI Migration Path

M-TRACEABI-1 adds a compatibility layer between conventional request/runtime/planner traces and the validated memory-object ABI. It does not modify the ABI validator. The compatibility layer emits candidate contracts, re-runs candidate objects through `scripts.validate_memory_object_abi.classify`, and blocks downstream placement, reuse, compression, migration, and retention actions unless the validator admits the candidate.

The current workspace does not contain `data/synthetic_trace_v2.csv`, `data/synthetic_trace_v3.csv`, or `data/security_trace_v3.csv`. That null result is preserved in `data/trace_to_abi_lift_results.csv` as `trace_source=no_canonical_trace_csv_found`; the harness therefore uses the validated `data/runtime_policy_decisions.csv`, `data/memory_plan_actions.csv`, and explicit legacy trace fixtures to model the migration boundary.

| Conventional trace signal | ABI field(s) | Derivation confidence | Fail-closed rule |
|---|---|---:|---|
| Request id, prompt/template id, runtime object id | `object_id`, `lineage_ids`, `producer_id` | high when stable ids exist | Missing lineage blocks ABI admission. |
| Tenant or isolation label | `tenant_id`, `security_label` | high only if emitted by runtime/security layer | Missing security label requires annotation or blocks reuse. |
| Runtime policy reuse decision | `reuse_scope` | medium; often ambiguous for KV/cache state | Unknown reuse scope requires annotation and emits zero actions. |
| Retrieval index id and source version | `freshness_source_id`, `lineage_ids` | high for RAG traces with index versioning | Missing source version blocks retrieved-context reuse. |
| Tool call output without tool-run provenance | `lineage_ids`, `freshness_source_id` | low | Missing provenance fails closed before reuse or retention. |
| Branch id and parent/dependency ids | `branch_id`, `parent_object_ids` | medium if DAG instrumentation exists | Dangling parent fails closed for Option C. |
| Verifier event | `checked_target_id`, integrity/security binding | low without verifier/runtime annotation | Missing checked target requires annotation and emits zero actions. |
| Workspace artifact path | `retention_policy_id`, durable lifetime bounds | low from request traces alone | Missing retention policy requires annotation and emits zero actions. |
| Residency preference | `residency_hint` | advisory | May default only after the existing ABI validator admits the object. |
| Opaque request envelope | no ABI fields | explicit fallback | Option A remains executable without ABI lifting. |

The migration result has four statuses. `abi_admissible` means the candidate passed the existing ABI validator and may enter the already validated ABI integration boundary. `annotation_required` means the trace has a plausible object but lacks mandatory developer/runtime annotation, such as reuse scope, verifier target, or retention policy. `fail_closed` means the trace is non-liftable as-is, such as missing provenance or dangling branch parents. `option_a_opaque_fallback` means no object contract is created and the conventional Option A path remains available.

The key negative finding is that conventional traces are enough for some prompt-prefix and retrieved-context candidates, but not enough for security-sensitive reuse, branch/DAG state, verifier integrity, tool provenance, or durable retention. Those fields must be emitted by the developer, runtime, compiler, security layer, or planner; silently defaulting them would violate the ABI boundary.

Trace lifting is a migration/control-plane mechanism, not production evidence. All outputs from this harness use synthetic/internal evidence labels and keep `production_calibrated=false`, `production_ready=false`, `threshold_success=false`, `causal_validity_granted=false`, and `claim_credit_allowed=false`.
