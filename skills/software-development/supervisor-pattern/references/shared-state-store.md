# Shared State Store / Chief of Staff Pattern

> **Source:** AI Automation Society (Skool) — 22 Jul 2026. Community discussion sparked by a post about "What If Every AI Team Needed a Chief of Staff" — centralized coordination agent for multi-agent systems.
> **Wiki:** `~/wiki/skool/2026-07-22-chief-of-staff-shared-state.md`

## What

A shared state store is a centralized data layer that sub-agents read/write to during execution. Instead of each sub-agent working with its own isolated state (and the supervisor merging results at the end), all agents share a single mutable state that the supervisor can inspect, modify, or redistribute mid-execution.

This is distinct from the current supervisor-pattern (v2.0) which uses:
- **Isolated sub-agent state** — each delegate_task returns its own result
- **Post-hoc merge** — supervisor collects and validates after all tasks complete
- **No mid-execution coordination** — agents can't see each other's progress

## How It Extends the Supervisor Pattern

```
Current (v2.0):           With Shared State Store:
┌─ Supervisor ─┐          ┌─ Supervisor ──────────┐
│ Plan →        │          │ Plan →                 │
│ Delegate →    │          │ Init Shared Store →    │
│ Collect →     │          │ Delegate (agents read/ │
│ Validate →    │          │   write store) →       │
│ Merge         │          │ Mid-execution inspect →│
└───────────────┘          │ Validate → Merge       │
                           └────────────────────────┘
                                    │
                           ┌────────┴────────┐
                           │  Shared State    │
                           │  Store (JSON)    │
                           │  • task_queue    │
                           │  • results_pool  │
                           │  • agent_status  │
                           └─────────────────┘
```

### Key Differences

| Aspect | Current (v2.0) | With Shared State Store |
|--------|----------------|------------------------|
| Agent isolation | Full — no visibility between agents | Partial — agents see shared task queue |
| State location | Per-agent return values | Centralized mutable store |
| Supervisor role | Plan → Collect → Validate | Plan → Init → Monitor → Coordinate |
| Failure handling | Detect after return, retry individual | Reassign from shared queue immediately |
| Scalability | Linear with agent count | Sub-linear — agents pull work when ready |
| Complexity | Low | Medium — needs conflict resolution |

## When to Use

- **3+ agents that produce interdependent results** (Agent B needs Agent A's output before starting)
- **Dynamic task allocation** — agents pick from a queue rather than being assigned statically
- **Progressive refinement** — early results change the priority of remaining tasks
- **Mid-execution supervision** — supervisor adjusts task priorities based on partial results

When NOT to use:
- 1-2 simple parallel tasks (current model is simpler and sufficient)
- Each agent produces fully independent output (merge is trivial)
- The supervisor decision logic is simpler than the coordination overhead

## Implementation Approach (Sketch)

```python
# 1. Define shared state schema
shared_state = {
    "task_queue": [],        # Priority queue of pending tasks
    "results_pool": {},      # Completed results by task_id
    "agent_status": {},      # busy/idle/done per agent
    "metadata": {}           # Supervisor annotations
}

# 1a. How agents read the store:
# Each agent receives the shared state as part of its context.
# When agent reads task_queue, it sees ALL pending tasks, not just its own.

# 1b. How agents write to the store:
# Agent returns {"result": ..., "provenance": ..., "state_updates": {...}}
# Supervisor applies state_updates to the shared store before next delegation round.

# 2. Supervisor cycle
while has_pending_tasks(shared_state):
    # Inspect current state
    ready_agents = get_idle_agents()
    next_tasks = prioritize(shared_state["task_queue"])
    
    # Delegate with full state context
    results = delegate_task(
        tasks=[prepare_task(t, shared_state) for t in next_tasks[:ready_agents]],
        context={"shared_state": shared_state}  # agents see current state
    )
    
    # Apply updates from each agent
    for r in results:
        if r.get("state_updates"):
            merge_state_updates(shared_state, r["state_updates"])
        
        # Record completed tasks
        shared_state["results_pool"][r["task_id"]] = r["result"]
        shared_state["task_queue"] = [t for t in shared_state["task_queue"] if t["id"] != r["task_id"]]
    
    # Re-prioritize based on partial results
    shared_state = supervisor_repairoritize(shared_state)
```

### Priority Queue (Deterministic, No LLM Judgment)

Unlike the current supervisor pattern (which uses LLM reasoning to decide what to do next), the shared state store uses a deterministic priority queue:

```python
def prioritize(task_queue):
    return sorted(task_queue, key=lambda t: (
        -t.get("priority", 0),      # Higher priority first
        t.get("dependency_count", 0),  # Fewer dependencies first
        t.get("created_at", 0)        # Older tasks first
    ))
```

This means:
- No LLM cost for routing decisions
- Predictable behavior (same input → same output)
- Agents consume work as they become available (pull model)
- Failed tasks go back to the queue with retry metadata

## Relationship to Heartbeat (Current v2.0)

| Feature | Heartbeat (current) | Shared State Store (proposed) |
|---------|-------------------|-------------------------------|
| Purpose | Observability (log) | Coordination (active) |
| Data flow | Write-only (agent → log) | Read-write (agent ↔ store) |
| Supervisor role | Audit after execution | Adjust during execution |
| State scope | Single task | All concurrent tasks |
| Overhead | ~2.5% (metadata tagging) | Higher — state serialization + conflict resolution |

**Recommendation:** Start with the current heartbeat + provenance model. Add shared state store only when a concrete use case demonstrates the need — e.g., 5+ interdependent agents where coordination cost exceeds the benefit of isolation.

## Source

- AI Automation Society community post (22 Jul 2026): "What If Every AI Team Needed a Chief of Staff" — centralized coordination agent pattern
- Wiki page: `~/wiki/skool/2026-07-22-chief-of-staff-shared-state.md`
- Related: Paperclip orchestrator (CEO agent pattern, 4 Jul 2026) — `references/paperclip-open-source-orchestrator.md`
