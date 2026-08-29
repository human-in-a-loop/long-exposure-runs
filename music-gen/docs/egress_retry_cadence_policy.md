# Egress-retry cadence policy (c49-formalized)

**Author**: c49 worker, linear cycle.
**Precedent**: ambient practice since c33; formalized c49 per c48 auditor
Priority 3 handoff.

## The obligation

The campaign directive requires "periodic retry of
`workspace/harvest_playlists.sh` in case the network policy changes." This
is a **persistent** obligation across the campaign's lifetime; egress
remains blocked (HTTP 429 + tv_embedded, unchanged since c45).

## The policy

**One probe row per branch per cycle**, honoring the retry obligation
independently of the branch's substantive work surface.

### Path A — fanout cycles

Each of the 2–3 clone branches emits its own probe row with a suffixed
milestone id:

```
M-INGEST-1/egress-probe-cycle<N>-clone-<k>
```

Milestone id follows the c32 fanout-namespace convention (leading
`M-INGEST-1/*` egress probes are pragmatically suffixed even though the
c32 convention formally exempts substantive `M-*` labels; the per-cycle
probe is bookkeeping-shaped, so the suffix is honored to avoid
LedgerConcatError on shared substantive-milestone labels emitted from
sibling clones on the same cycle).

Emission timing: top-of-cycle OR bookkeeping-tail per clone; auditor
accepts either.

### Path B — linear cycles

The single worker emits one probe row per cycle:

```
M-INGEST-1/egress-probe-cycle<N>
```

Emission timing: bookkeeping-tail immediately after `_run/cycle_<N>_closed`.

### Row payload

Every probe row appends one line to `data/ingestion/egress_status.jsonl`
recording the observed failure mode. Current stable mode: `HTTP 429 +
tv_embedded` (yt-dlp Innertube tv_embedded client rejected upstream).

## The unblock signal

Two consecutive fresh `media_ok=true` rows trigger
`scripts/egress_ready/*` state-machine transition per M-INGEST-1/egress-
ready-automation (c8). This has never fired.

## What this policy retires

- Ad-hoc `"honored via bookkeeping"` justifications when a clone did not
  touch the harvester surface (used c47 clones 1+2). Under this policy
  those are compliant, not exceptional.
- The temptation to fabricate probe results without running the check:
  the row must reflect an actual probe attempt (harvest_playlists.sh
  invocation OR the yt-dlp+range-request probe pair).

## What this policy does NOT change

- The two-consecutive-`media_ok=true` unblock condition (M-INGEST-1/
  egress-probe success criteria).
- The M-INGEST-1/egress-ready-automation state machine (c8, READ-ONLY).
- The rated-audio corpus expansion 43→80 (blocked on egress-unblock).

## Cadence audit

Per-cycle grep target for compliance:

```bash
grep -c '"milestone_id":"M-INGEST-1/egress-probe-cycle<N>' promise_ledger.jsonl
```

Expect ≥1 (linear) or =N_branches (fanout).
