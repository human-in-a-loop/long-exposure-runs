# Codex Fan-Out Session Inheritance Bug

Created: 2026-05-18T12:59:41Z

## Summary

The live PhytoGraph run exposed a Codex-specific failure mode in long-exposure fan-out session handling. The root researcher session was inherited by fan-out clones, so several independent clone turns resumed and wrote into the same Codex thread as the root researcher. That shared thread then exceeded Codex's effective context window and became unrecoverable through repeated remote compaction failures.

This does not appear to hurt Claude in the same way because the original clone-inheritance design was built around Claude's session semantics. Codex `exec resume` behaves differently: resuming the same thread from multiple clone processes is not an isolated fork. It appends clone activity into the same thread, contaminating the root researcher context and eventually exhausting the session.

## Observed Evidence

- The live run was Codex-only after restart.
- Researcher failures began at cycle 18 and persisted through cycle 45.
- The persistent failing researcher session was `019e3971-f13c-7d42-a0f7-eb10c0557193`.
- The clone state files for fork `cc044bf40be3` inherited that same researcher session:
  - `clone-0`: `researcher = 019e3971-f13c-7d42-a0f7-eb10c0557193`
  - `clone-1`: `researcher = 019e3971-f13c-7d42-a0f7-eb10c0557193`
  - `clone-2`: `researcher = 019e3971-f13c-7d42-a0f7-eb10c0557193`
- The Codex session JSONL for that session contained fan-out clone assignments and clone tool output inside the same thread.
- Token growth in telemetry showed the researcher thread progressing from normal usage into over-context territory:
  - cycle 15: about 71k total context tokens
  - cycle 16: about 185k total context tokens
  - clone activity pushed the same session beyond the Codex context window
- From cycle 18 onward, the researcher repeatedly failed with:
  - `Codex ran out of room in the model's context window. Start a new thread or clear earlier history before retrying.`
  - later `codex_core::compact_remote: remote compaction failed`
- long-exposure did not evict the bad Codex session after these errors, so every later cycle retried the same poisoned researcher thread.

## Single Root Cause

Provider-native session inheritance is unsafe for Codex fan-out.

The clone seeding path preserves `parent_agent_sessions` when the parent and clone account directory match. Under Codex, that means each clone can resume the exact same provider-native thread as the root researcher. That is not a true fork. It is shared-thread mutation.

The result is:

1. Root researcher creates or resumes Codex thread A.
2. Fan-out clones inherit thread A in their seeded state.
3. Multiple clones resume thread A with different branch assignments.
4. Thread A accumulates branch-local tool calls, branch reasoning, and branch outputs.
5. Root researcher later resumes thread A.
6. Codex sees an oversized mixed root/clone history and fails before producing a new research brief.
7. long-exposure retries the same bad session because context-window and remote-compaction errors are not classified as session-poisoning errors.

## Why This Is Codex-Specific

The problematic behavior depends on Codex `exec resume` semantics. The current fan-out inheritance design assumes that a provider-native session can be inherited by a clone as useful context. With Codex, inheriting the same thread ID gives the clone access to the same mutable conversation, not an isolated branch.

Claude may tolerate or intentionally support the original pattern better, and this run's failure should not be generalized as a Claude bug without separate evidence. The fix should be provider-aware.

## Minimal Fix Direction

Two robust, simple fixes should be considered together:

1. Do not inherit Codex `agent_sessions` into fan-out clones.
   - In `_seed_clone_state`, if the active provider is Codex, seed clones with `agent_sessions = {}` even when the account directory matches.
   - Preserve `agent_summaries`, `parent_results`, workspace artifacts, assignment files, and run id.
   - This keeps continuity through deterministic state and summaries while preventing shared-thread mutation.

2. Evict Codex sessions on deterministic over-context failures.
   - In `_call_exploration_agent`, when a Codex `ClaudeCliError` contains either:
     - `ran out of room in the model's context window`
     - `compact_remote: remote compaction failed`
   - remove `agent_sessions[agent_name]` so the next cycle starts a fresh Codex thread with restored summaries/workspace context.
   - This prevents infinite retries against a poisoned native thread.

## Could A Codex `/fork` Hook Preserve Inheritance?

Possibly, but only if Codex exposes a real fork primitive with isolation semantics.

A usable `/fork`-style hook would need to guarantee:

- The child thread receives a snapshot of the parent context.
- Child turns do not append to or mutate the parent thread.
- Multiple children can run concurrently without sharing the same mutable history.
- The parent can continue from its own thread after fan-out collapse.
- The parent receives only the explicit merge artifacts, not the full child transcripts.

If Codex has or gains such a primitive, long-exposure could map fan-out clone creation to:

1. Root researcher thread A reaches fan-out.
2. long-exposure creates child threads A.0, A.1, A.2 from A using the fork hook.
3. Each clone resumes only its child thread.
4. The root never resumes child threads directly.
5. The barrier collapses clone artifacts into a bounded merge synthesis.

That would preserve the useful part of inheritance without contaminating the root. Until such semantics are verified, long-exposure should treat Codex provider-native session IDs as non-inheritable across fan-out clones.

## Operational Recovery For This Run

The live run was stopped gracefully after the issue was identified. The stop should let long-exposure exit through final auditor, final reporter, and curator. The final output should be treated as covering substantive work up through the last healthy research cycles; later cycle reports after the Codex session poisoning are mostly continuity/bookkeeping reports rather than new research progress.

