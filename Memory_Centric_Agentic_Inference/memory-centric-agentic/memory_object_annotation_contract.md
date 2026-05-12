---
created: 2026-05-12T22:15:00Z
cycle: 45
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-ANNOT-1
---

# Memory-Object Annotation Contract

`M-TRACEABI-1` showed that conventional request/runtime traces can safely infer some ABI fields, but not reuse authorization, tool provenance, branch dependencies, verifier target integrity, durable retention, compression safety, or evidence-label boundaries. `M-ANNOT-1` adds a narrow developer/runtime annotation layer for those gaps. The annotation layer does not modify the ABI validator; it produces completed ABI candidates that must still pass `scripts.validate_memory_object_abi.classify` before runtime or planner actions are emitted.

## Annotation Schema

The schema in `data/memory_object_annotation_schema.csv` defines eight annotation classes: `reuse_scope_annotation`, `tenant_security_annotation`, `tool_provenance_annotation`, `branch_dependency_annotation`, `verifier_integrity_annotation`, `compression_safety_annotation`, `retention_policy_annotation`, and `evidence_label_annotation`. Each class names the ABI fields it can complete and the constraint that must be checked against trace/security/provenance context. The examples in `data/memory_object_annotation_examples.jsonl` include valid and invalid fixtures for every class.

## Constraints, Not Trust

Annotations are constraints, not trust. A reuse annotation cannot widen from tenant-local evidence to global reuse; a tenant/security annotation cannot switch tenant or lower confidentiality; a tool provenance annotation must bind lineage and freshness to observed provenance; a branch annotation must resolve known parents; a verifier annotation must name an observed checked target; lossy compression cannot be forced onto correctness-critical state; durable retention must name a policy; and synthetic/internal evidence cannot be relabeled `production_target`.

## Merge and Conflict Rules

Merge precedence is deterministic: trace-derived fields provide the base candidate, annotations fill only the fields named by their annotation class, then the completed candidate is submitted to the existing ABI validator. If annotation content conflicts with trace/security/provenance context, the merge fails closed before ABI integration. If the annotation is internally valid but the completed contract still violates the ABI, the candidate also fails closed.

## Migration Path

The implementation path is: trace lift -> annotation requirements -> annotation merge -> ABI validation -> integration replay -> action gating. Completed KV, tool-output, branch, verifier, and durable-artifact fixtures become ABI-admissible only after validated annotations resolve mandatory fields. Scope-widening, provenance-breaking, dangling-branch, unsafe-compression, missing-retention, or production-upgrade attempts emit zero placement, reuse, compression, migration, or retention actions.

## Boundary

Option A remains executable for opaque conventional requests and for failed annotation merges. The annotation mechanism is migration/control-plane evidence only: all rows preserve `production_calibrated=false`, `production_ready=false`, `threshold_success=false`, `causal_validity_granted=false`, and `claim_credit_allowed=false`.
