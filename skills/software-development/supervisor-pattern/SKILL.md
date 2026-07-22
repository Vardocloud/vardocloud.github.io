---
name: supervisor-pattern
description: "Supervisor Pattern — multi-agent pipeline orchestration with validation layer, provenance logging (traceable execution), JSON schema check, targeted retry, and heartbeat monitoring. Integrates Build Explanation Into the Workflow framework for execution path transparency."
version: 2.0.0
metadata:
  hermes:
    tags: [supervisor, pattern, validation, provenance, traceable, delegate, quality, agent-orchestration, heartbeat]
    category: software-development
references:
  - "Build Explanation Into the Workflow — Jason Elam, Paul McDonald, Chetan Mishra (AI Automation Society, 12 Jul 2026)"
  - "Anti-Hallucination Protocol (Certainty Levels, Source Citation, Confidence Tags)"
---

# Supervisor Pattern — Provenance-Aware Multi-Agent Orchestration

> **Core principle:** Strong model as Supervisor + cheap models as Executors, with full execution path traceability.
> Every subagent output carries its provenance (source, confidence, assumptions, override points) as a first-class citizen.
>
> **Origin:** AI Automation Society (Skool) — Nate Herk (Supervisor Pattern, 2 Jul 2026)
> **Build Explanation integration:** Jason Elam, Paul McDonald, Chetan Mishra (12 Jul 2026)
> **Lighthouse alignment:** Anti-Hallucination Protocol, Layer 6 Write Rules

## What

A supervisor-worker architecture where:
- **Supervisor (Vanitas):** Plans tasks, defines schemas, validates outputs, records provenance, manages retries
- **Executor (delegate_task sub-agent):** Works independently on assigned tasks using cheaper models
- **Provenance Layer:** Every decision/result is tagged with source, confidence, assumptions, and override points
- **Validation Gate:** JSON schema + quality threshold + provenance completeness check
- **Heartbeat:** SQLite-based execution log for task visibility and debugging
- **Targeted Retry:** Only failed subtasks are retried, with specific feedback from validation errors

## When to Use

- 2+ parallel research or processing tasks (3-6 ideal)
- Subagent output must follow a specific format (JSON schema required)
- Output quality is critical and silent failures must be prevented
- Cost control needed (cheap model + supervisor validation + provenance logging)
- Task status tracking required (heartbeat for visibility)
- Auditability matters (client-facing or safety-critical automations)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      SUPERVISOR                          │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│  │   Plan   │→ │ Delegate │→ │ Validate  │→ │  Merge   │  │
│  │ +Schema  │  │ (tasks)  │  │ +Retry    │  │ +Proven  │  │
│  └─────────┘  └──────────┘  └──────────┘  └─────────┘  │
│       │            │              │             │       │
│       ▼            ▼              ▼             ▼       │
│  ┌─────────────────────────────────────────────────┐   │
│  │              PROVENANCE LAYER                    │   │
│  │  Source Tracking │ Confidence Tags │ Assumptions │   │
│  └─────────────────────────────────────────────────┘   │
│       │            │              │             │       │
│       ▼            ▼              ▼             ▼       │
│  ┌─────────────────────────────────────────────────┐   │
│  │              HEARTBEAT (SQLite Log)               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
  ┌──────────┐        ┌──────────┐
  │ Executor │  ...   │ Executor │
  │ (task 1) │        │ (task N) │
  └──────────┘        └──────────┘
```

## Core Components

### 1. Provenance Layer (NEW in v2.0)

**Source:** Build Explanation Into the Workflow framework (Jason Elam, AI Automation Society, 12 Jul 2026)

Every subagent result MUST include a provenance record alongside its data output. This prevents the "correct-looking trap" where output appears correct but was produced by a flawed process.

#### Provenance Record Format

```json
{
  "provenance": {
    "execution_method": "model_inference|db_query|web_search|file_retrieval|cache|human_input",
    "model_used": "deepseek-v4-flash|gpt-5.4-mini|...",
    "data_sources": [
      {"type": "web_search", "query": "...", "result_count": 5},
      {"type": "wiki_fts", "query": "...", "doc_count": 3},
      {"type": "session_search", "session_id": "..."}
    ],
    "confidence": {
      "overall": "high|medium|low",
      "per_field": {
        "field_name": {"value": "...", "confidence": "confirmed|likely|inferred|uncertain"}
      }
    },
    "decision_assumptions": [
      "Assumed data from web_search is current as of last crawl",
      "Used cached result from earlier session_search (TTL within limits)"
    ],
    "override_points": [
      "Human can override field X at step Y",
      "Auto-approved if confidence=high, blocked if confidence=low"
    ],
    "timestamp": "2026-07-12T18:30:00Z"
  },
  "result": { "... actual task output ..." }
}
```

#### Provenance Collection Steps

**Before delegation:**
1. Record what data sources are available for this task
2. Note the model being used (cheap/expensive)
3. Define expected output schema

**After delegation:**
1. For each output field, attach a confidence level (see Anti-Hallucination Protocol)
2. Record which data sources actually contributed to the result
3. List any assumptions made during processing
4. Identify override points where a human should review

**On failure:**
1. Record the failure in the provenance log with error details
2. Check if it's a "correct-looking trap" (output looks right but assumptions are wrong)
3. Log the exact validation error for targeted retry

### 2. Confidence Levels (Aligned with Anti-Hallucination Protocol)

| Tag | Meaning | Auto-Pass | Human Review |
|-----|---------|-----------|--------------|
| `[CONFIRMED]` | Directly verified from authoritative source | ✅ Yes | Optional |
| `[LIKELY]` | Strong evidence, multiple consistent sources | ✅ Yes | Optional |
| `[INFERRED]` | Logical deduction, no direct source | ⚠️ Conditional | If critical |
| `[UNCERTAIN]` | Weak or conflicting evidence | ❌ No | Required |
| `[UNKNOWN]` | No data available | ❌ No | Required |

The supervisor auto-passes [CONFIRMED] and [LIKELY] outputs.
[INFERRED] passes for non-critical fields but requires review for critical decisions.
[UNCERTAIN] and [UNKNOWN] always block and require human intervention.

### 3. Decision Assumptions Log

Every automated decision carries implicit assumptions. The provenance layer makes them explicit:

```json
{
  "assumptions": [
    {
      "rule": "Web search results are from the last 7 days",
      "impact": "If data is older, recommendations may be stale",
      "validated": true,
      "validation_method": "checked result timestamps"
    },
    {
      "rule": "Wiki content is accurate as of last edit",
      "impact": "If wiki hasn't been updated, may miss recent changes",
      "validated": false,
      "validation_method": "assumed without check — potential silent failure"
    }
  ]
}
```

**Checklist for common assumptions:**
- [ ] Data source freshness (how old is the data?)
- [ ] Model capability (is the model suitable for this task?)
- [ ] Context completeness (was all necessary context provided?)
- [ ] Output format compliance (does the output match the schema?)
- [ ] Cross-reference validity (do multiple sources agree?)

### 4. Override Points

Define where a human can intervene in the automation pipeline:

| Override Point | When | How |
|---------------|------|-----|
| **Schema definition** | Before delegation | Human adjusts task scope/format |
| **Confidence threshold** | After validation | Human overrides auto-pass/fail for [INFERRED] items |
| **Provenance review** | After execution | Human inspects execution path log |
| **Output merge** | Before final delivery | Human edits or rejects merged output |
| **Retry decision** | After validation failure | Human chooses to retry, bypass, or cancel |

**Implementation rule:** For safety-critical tasks (email automation, data deletion, financial decisions), set the default override point to "human review required." For routine research tasks, set it to "auto-approve with provenance log."

### 5. Correct-Looking Trap Detection

> "A correct-looking answer does not prove that the intended process occurred." — Chetan Mishra

**Detection patterns:**

| Pattern | Symptom | Detection |
|---------|---------|-----------|
| **Missing provenance** | Output looks good but no source trail | Reject if provenance is empty |
| **Stale data** | Result matches schema but uses old cached data | Check data source timestamps |
| **Hallucinated source** | Output cites a source that doesn't exist | Cross-reference source URLs |
| **Model overconfidence** | Output is fluent but unverifiable | Check confidence field |
| **Circular reasoning** | Source A cites B, B cites A | Trace source chains |

**Action on detection:**
1. Flag the output with `[SILENT_FAILURE_RISK]`
2. Add detection reason to provenance log
3. Route to human review (block auto-approval)
4. Do NOT retry with same parameters — adjust the prompt to force source verification

---

## Workflow (Updated)

### Step 1 — Define Schema + Provenance Requirements

```python
task_schema = {
    "type": "object",
    "required": ["field1", "field2"],
    "properties": {
        "features": {"type": "array", "minItems": 3},
        "score": {"type": "number", "minimum": 0}
    }
}

provenance_requirements = {
    "require_sources": True,        # Each claim must cite a source
    "min_confidence": "likely",     # Minimum confidence level
    "require_assumptions": True,    # Log decision assumptions
    "override_point": "human_if_uncertain"  # Override policy
}
```

### Step 2 — Heartbeat + Provenance Init + delegate_task

```python
from heartbeat import HeartbeatLog
hb = HeartbeatLog()

# Record task start with provenance context
hb.record("research-task", "running",
    schema_name="product-analysis",
    provenance={
        "sources_available": ["web_search", "wiki_fts", "session_search"],
        "model_assigned": "deepseek-v4-flash",
        "expected_confidence": "likely"
    }
)

# Define tasks with provenance requirements embedded in goal
tasks = [
    {
        "id": "task-1",
        "goal": "Research X. Return JSON with provenance. "
                "For each output field, include source and confidence level."
    },
    ...
]

# Delegate
results = delegate_task(tasks=tasks)

hb.record("research-task", "validating")
```

### Step 3 — Validate + Check Provenance

```python
all_errors = []
provenance_issues = []

for result in results:
    # JSON schema validation
    schema_errors = validate_schema(result.summary, task_schema)
    
    # Provenance completeness check (NEW)
    prov = extract_provenance(result.summary)
    if not prov or not prov.get("data_sources"):
        provenance_issues.append("Missing provenance record — possible silent failure")
    if prov and prov.get("confidence", {}).get("overall") == "uncertain":
        provenance_issues.append("Output confidence too low for auto-approval")
    if prov and prov.get("execution_method") == "model_inference" \
       and not prov.get("data_sources"):
        provenance_issues.append("Model inference without data sources — hallucination risk")
    
    all_errors.extend(schema_errors)
    all_errors.extend(provenance_issues)
```

### Step 4 — Heartbeat Update + Targeted Retry

```python
if not all_errors:
    hb.record("research-task", "completed",
        latency=12.4,
        provenance_summary="3 sources used, all [CONFIRMED], auto-approved"
    )
else:
    hb.record("research-task", "validation_failed",
        error_message="; ".join(all_errors)
    )
    retry_with_feedback(result, all_errors)
    hb.record("research-task", "retrying")
```

Only failed tasks are retried — with specific feedback about what went wrong.

### Step 5 — Provenance-Logged Merge

```python
# Before final delivery, compile the execution path summary
execution_summary = {
    "task_id": "research-20260712",
    "total_subtasks": 3,
    "passed": 2,
    "retried": 1,
    "retry_success": True,
    "provenance_complete": True,
    "confidence_distribution": {
        "confirmed": 5,
        "likely": 3,
        "inferred": 1,
        "uncertain": 0
    },
    "silent_failure_flags": 0,
    "decision_assumptions_logged": 4
}
```

---

## Heartbeat System

**Script:** `~/.hermes/scripts/heartbeat.py`
**Database:** `~/.hermes/data/supervisor_heartbeat.db` (SQLite)

### Statuses

| Status | Meaning |
|--------|---------|
| `running` | Task started |
| `completed` | Successfully completed (all validations + provenance passed) |
| `validation_failed` | Validation or provenance check failed |
| `retrying` | Being retried with specific feedback |
| `provenance_incomplete` | Missing provenance record flagged |
| `silent_failure_detected` | Correct-looking trap triggered |
| `blocked` | Human review required |
| `budget_exceeded` | Budget exceeded (future) |

### CLI Usage

```bash
python3 ~/.hermes/scripts/heartbeat.py record "task-id" "completed" --latency 3.2
python3 ~/.hermes/scripts/heartbeat.py query "task-id"
python3 ~/.hermes/scripts/heartbeat.py summary
python3 ~/.hermes/scripts/heartbeat.py failures
```

### Python Usage

```python
from heartbeat import HeartbeatLog
hb = HeartbeatLog()
hb.record("task-001", "running")
hb.record("task-001", "completed", latency=3.2)
print(hb.summary())
```

**CRITICAL:** Heartbeat only logs — it does not affect supervisor decisions. All decision logic (which tasks to retry, how many times, provenance checks) remains in the supervisor.

---

## Cost Comparison

| Metric | Without Supervisor | With Supervisor | With Supervisor + Provenance |
|--------|-------------------|-----------------|-----------------------------|
| 4 parallel tasks | ~200s, 4 calls | ~200s, 4 calls | ~205s, 4 calls |
| 1 failed + retry | ~400s, 8 calls | ~230s, 5 calls | ~235s, 5 calls |
| Time saved | — | ~42% | ~41% |
| Provenance overhead | — | — | **~+2.5%** (negligible, text tagging only) |

Provenance layer adds near-zero latency because it's just metadata tagging on existing outputs. No extra model calls.

---

## Provenance Log Storage (Lighthouse Alignment)

| Type | Store | TTL | Format |
|------|-------|-----|--------|
| Task execution paths | `~/.hermes/data/supervisor_heartbeat.db` | 60 days | SQLite (structured) |
| Provenance records | Attached to each heartbeat event | 60 days | JSON in SQLite |
| Silent failure flags | Heartbeat + separate log entry | 60 days | Text + severity |
| Override decisions | Heartbeat (blocked/completed events) | 60 days | JSON |

The provenance log is separate from the wiki (Layer 4) and NotebookLM (Layer 6). It lives in the operational database (heartbeat db) because it's transient execution metadata, not permanent knowledge.

Permanent knowledge (source reliability assessments, common assumption patterns, failure modes) should be promoted to the wiki periodically.

---

## Selenium Fairness (Cost-Benefit Gate)

> **Rule:** A system extension must justify its resource cost.
> Source: Edel, 5 Jul 2026 — rejecting meta-prompting audit proposal.

### Questions Before Adding Any Extension

1. **What will this cost?** Setup time, LLM calls/week, disk, CPU, maintenance.
2. **What will we gain?** What concrete problem does it solve? What do we lack without it?
3. **Is there a simpler alternative?** A thin layer on an existing system? (Like Heartbeat)
4. **Does it pass the value test?** Operating cost < benefit provided.

### Example: Provenance Layer vs Weekly Audit

| System | Setup | Weekly Operation | Benefit | **Pass?** |
|--------|-------|-----------------|---------|:---:|
| Provenance Layer | 30 min | $0 (metadata tagging) | Silent failure prevention | ✅ |
| Weekly Skill Audit | 1 hour | ~40 LLM calls | Quality metrics | ❌ |

**Lesson:** Thin, zero-operational-cost layers are always preferred over heavy audit systems. Every operational-cost extension must pass the Gate before implementation.

---

## Existing Components (Unchanged from v1.x)

### Validator Script

`references/validator.py` — Python JSON schema + threshold validator. Usage:
```bash
python3 references/validator.py --input result.json --schema '{"required":["field"]}'
```

### Skill Patch Cycle

For runtime errors during skill execution, use the Skill Patch Cycle (v1.2):

```python
from skill_patch_cycle import SkillPatchCycle
spc = SkillPatchCycle()
result = spc.evaluate(skill_name="supervisor-pattern", error="...")
proposal = spc.propose(result)
```

Only errored skills are evaluated. Working skills are not scanned. No auto-patch without Edel's approval.

### PoC Reports

- `references/poc-results.md` — All PoC results (v1.0 through v2.0):
  - **v1.0** (3 Jul): 3 parallel tasks, 55% speedup
  - **v2.0** (3 Jul): 4 tasks + trap + schema validation + targeted retry
  - **v3.0** (5 Jul): Heartbeat + supervisor integration, 3 tasks (2 normal + 1 trap)
  - **v4.0** (12 Jul): Provenance Layer integration — execution path logging, confidence tagging, assumption recording

## References

- `references/shared-state-store.md` — Shared State Store / Chief of Staff pattern: centralized coordination layer for multi-agent supervisor execution (22 Jul 2026). Extends v2.0 with inter-agent state sharing, dynamic priority queue, and mid-execution re-prioritization. Pull model vs current push model.

## Limitations

- Schema definition still manual — automatic inference is future work
- Cross-task provenance validation not yet implemented (consistency between tasks)
- Confidence thresholds are static — could be adaptive
- Provenance records are text-based — structured extraction is future work
- Heartbeat does not affect supervisor decisions (logging only)
- Silent failure detection is heuristic — may have false positives
