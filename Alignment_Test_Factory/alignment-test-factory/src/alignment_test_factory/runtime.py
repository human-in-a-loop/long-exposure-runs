# created: 2026-05-13T22:20:00Z
# cycle: 4
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-4
"""Deterministic benign toy environment for agentic alignment traces."""

from __future__ import annotations

import hashlib
from typing import Any

from .schemas import TaskSpec
from .trace import make_event


class ToyEnvironment:
    """Provider-agnostic runtime that records tool, policy, and state evidence."""

    def __init__(self, task_spec: TaskSpec) -> None:
        self.task_spec = task_spec
        self.resources = {
            fixture.fixture_id: {
                "resource_id": fixture.fixture_id,
                "content": self._fixture_content(fixture.fixture_id, fixture.content_refs),
                "fixture_type": fixture.fixture_type,
            }
            for fixture in task_spec.fixtures
        }
        self.state: dict[str, Any] = {"audit_log": []}
        self.approval_decisions: list[dict[str, Any]] = []
        self.trace: list[dict[str, Any]] = []
        self._next_sequence = 1

    def observe(self, resource_id: str, extra_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        content = self.resources.get(resource_id, {}).get("content", "")
        allowed = self._allowed_resource(resource_id)
        payload = {
            "source_id": resource_id,
            "trust_tier": allowed.get("trust_tier", "synthetic") if allowed else "synthetic",
            "content_hash": self._hash(content),
            "result_status": "observed" if resource_id in self.resources else "not_found",
        }
        if extra_payload:
            payload.update(extra_payload)
        return self._append("observation", payload)

    def read_resource(self, resource_id: str) -> dict[str, Any]:
        allowed = self._allowed_resource(resource_id)
        can_read = bool(allowed and allowed["access"] in {"read", "read_write"})
        exists = resource_id in self.resources
        status = "allowed" if can_read and exists else "denied"
        payload = {
            "tool_name": "read_resource",
            "resource_ids": [resource_id],
            "access_scope": allowed["scope"] if allowed else "unallowed",
            "result_status": status,
            "content_hash": self._hash(self.resources[resource_id]["content"]) if status == "allowed" else None,
        }
        return self._append("tool_call", payload)

    def request_approval(
        self,
        action: str,
        approver: str,
        token_placeholder: str,
        scope: str,
    ) -> dict[str, Any]:
        rule = self._approval_rule(action)
        approved = bool(
            rule
            and rule.get("required")
            and rule.get("approver") == approver
            and rule.get("token_placeholder") == token_placeholder
            and rule.get("scope") == scope
        )
        if rule and not rule.get("required") and rule.get("scope") == scope:
            decision = "not_required"
        else:
            decision = "approved" if approved else "denied"
        payload = {
            "requested_action": action,
            "decision": decision,
            "approver": approver,
            "token_placeholder": token_placeholder,
            "scope": scope,
        }
        self.approval_decisions.append(payload)
        return self._append("permission_decision", payload)

    def write_state(
        self,
        target_state_key: str,
        value: Any,
        actor: str,
        causal_tool_call: str | None,
    ) -> dict[str, Any]:
        old_value = self.state.get(target_state_key)
        protected = target_state_key in set(self.task_spec.policy.restricted_state_keys)
        allowed = (not protected) or self._has_prior_approval(target_state_key)
        if allowed:
            self.state[target_state_key] = value
        payload = {
            "target_state_key": target_state_key,
            "old_hash": self._hash(old_value),
            "new_hash": self._hash(value),
            "actor": actor,
            "causal_tool_call": causal_tool_call,
            "result_status": "updated" if allowed else "denied",
            "protected": protected,
        }
        return self._append("state_update", payload)

    def write_audit_log(self, message: str) -> dict[str, Any]:
        tool_event = self._append(
            "tool_call",
            {
                "tool_name": "write_audit_log",
                "resource_ids": ["audit_log"],
                "access_scope": "write summary status after approval",
                "result_status": "allowed",
            },
        )
        self.state.setdefault("audit_log", []).append(message)
        self._append(
            "state_update",
            {
                "target_state_key": "audit_log",
                "old_hash": None,
                "new_hash": self._hash(self.state["audit_log"]),
                "actor": "toy_environment",
                "causal_tool_call": tool_event["event_id"],
                "result_status": "updated",
                "protected": False,
            },
        )
        return tool_event

    def delegate_task(
        self,
        task_id: str,
        context_ids: list[str],
        instruction: str,
        recipient: str = "synthetic_delegate",
        allowed_fields: list[str] | None = None,
        inherited_policy_ids: list[str] | None = None,
        output_reference: str | None = None,
    ) -> dict[str, Any]:
        allowed = set(self.task_spec.policy.allowed_delegate_context)
        status = "allowed" if set(context_ids) <= allowed else "denied"
        return self._append(
            "delegation_message",
            {
                "recipient": recipient,
                "task_id": task_id,
                "delegated_task_id": task_id,
                "context_ids": context_ids,
                "transmitted_context_ids": context_ids,
                "allowed_fields": allowed_fields or [],
                "inherited_policy_ids": inherited_policy_ids or [],
                "output_reference": output_reference,
                "instruction": instruction,
                "result_status": status,
            },
        )

    def final_answer(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._append("final_answer", payload)

    def _append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = make_event(f"evt_{self._next_sequence:04d}", event_type, self._next_sequence, payload)
        self._next_sequence += 1
        self.trace.append(event)
        return event

    def _allowed_resource(self, resource_id: str) -> dict[str, Any] | None:
        for resource in self.task_spec.policy.allowed_resources:
            if resource.resource_id == resource_id:
                return resource.model_dump()
        return None

    def _approval_rule(self, action: str) -> dict[str, Any] | None:
        for rule in self.task_spec.policy.approval_rules:
            if rule.action == action:
                return rule.model_dump()
        return None

    def _has_prior_approval(self, target_state_key: str) -> bool:
        action = f"write {target_state_key}"
        rule = self._approval_rule(action)
        if not rule:
            return False
        return any(
            decision["requested_action"] == action
            and decision["decision"] == "approved"
            and decision["approver"] == rule["approver"]
            and decision["token_placeholder"] == rule["token_placeholder"]
            and decision["scope"] == rule["scope"]
            for decision in self.approval_decisions
        )

    @staticmethod
    def _fixture_content(fixture_id: str, content_refs: list[str]) -> str:
        refs = ", ".join(content_refs) if content_refs else "no_refs"
        return f"synthetic fixture {fixture_id}: {refs}"

    @staticmethod
    def _hash(value: Any) -> str | None:
        if value is None:
            return None
        encoded = repr(value).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]
