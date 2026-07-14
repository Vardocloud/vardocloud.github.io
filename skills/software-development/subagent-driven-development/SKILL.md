---
name: subagent-driven-development
description: "Execute plans via delegate_task subagents (2-stage review)."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [delegation, subagent, implementation, workflow, parallel]
    related_skills: [writing-plans, requesting-code-review, test-driven-development]
---

# Subagent-Driven Development

## Overview

Execute implementation plans by dispatching fresh subagents per task with systematic two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## When to Use

Use this skill when:
- You have an implementation plan (from writing-plans skill or user requirements)
- Tasks are mostly independent
- Quality and spec compliance are important
- You want automated review between tasks

**vs. manual execution:**
- Fresh context per task (no confusion from accumulated state)
- Automated review process catches issues early
- Consistent quality checks across all tasks
- Subagents can ask questions before starting work

## The Process

### 1. Read and Parse Plan

Read the plan file. Extract ALL tasks with their full text and context upfront. Create a todo list:

```python
# Read the plan
read_file("docs/plans/feature-plan.md")

# Create todo list with all tasks
todo([
    {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
    {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
    {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**Key:** Read the plan ONCE. Extract everything. Don't make subagents read the plan file — provide the full task text directly in context.

### 2. Per-Task Workflow

For EACH task in the plan:

#### Step 1: Dispatch Implementer Subagent

Use `delegate_task` with complete context:

```python
delegate_task(
    goal="Implement Task 1: Create User model with email and password_hash fields",
    context="""
    TASK FROM PLAN:
    - Create: src/models/user.py
    - Add User class with email (str) and password_hash (str) fields
    - Use bcrypt for password hashing
    - Include __repr__ for debugging

    FOLLOW TDD:
    1. Write failing test in tests/models/test_user.py
    2. Run: pytest tests/models/test_user.py -v (verify FAIL)
    3. Write minimal implementation
    4. Run: pytest tests/models/test_user.py -v (verify PASS)
    5. Run: pytest tests/ -q (verify no regressions)
    6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

    PROJECT CONTEXT:
    - Python 3.12, Flask app in src/app.py
    - Existing models in src/models/
    - Tests use pytest, run from project root
    - bcrypt already in requirements.txt
    """,
    toolsets=['terminal', 'file']
)
```

#### Step 2: Dispatch Spec Compliance Reviewer

After the implementer completes, verify against the original spec:

```python
delegate_task(
    goal="Review if implementation matches the spec from the plan",
    context="""
    ORIGINAL TASK SPEC:
    - Create src/models/user.py with User class
    - Fields: email (str), password_hash (str)
    - Use bcrypt for password hashing
    - Include __repr__

    CHECK:
    - [ ] All requirements from spec implemented?
    - [ ] File paths match spec?
    - [ ] Function signatures match spec?
    - [ ] Behavior matches expected?
    - [ ] Nothing extra added (no scope creep)?

    OUTPUT: PASS or list of specific spec gaps to fix.
    """,
    toolsets=['file']
)
```

**If spec issues found:** Fix gaps, then re-run spec review. Continue only when spec-compliant.

#### Step 3: Dispatch Code Quality Reviewer

After spec compliance passes:

```python
delegate_task(
    goal="Review code quality for Task 1 implementation",
    context="""
    FILES TO REVIEW:
    - src/models/user.py
    - tests/models/test_user.py

    CHECK:
    - [ ] Follows project conventions and style?
    - [ ] Proper error handling?
    - [ ] Clear variable/function names?
    - [ ] Adequate test coverage?
    - [ ] No obvious bugs or missed edge cases?
    - [ ] No security issues?

    OUTPUT FORMAT:
    - Critical Issues: [must fix before proceeding]
    - Important Issues: [should fix]
    - Minor Issues: [optional]
    - Verdict: APPROVED or REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**If quality issues found:** Fix issues, re-review. Continue only when approved.

#### Step 4: Mark Complete

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

### 3. Final Review

After ALL tasks are complete, dispatch a final integration reviewer:

```python
delegate_task(
    goal="Review the entire implementation for consistency and integration issues",
    context="""
    All tasks from the plan are complete. Review the full implementation:
    - Do all components work together?
    - Any inconsistencies between tasks?
    - All tests passing?
    - Ready for merge?
    """,
    toolsets=['terminal', 'file']
)
```

### 4. Verify and Commit

```bash
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## Task Granularity

**Each task = 2-5 minutes of focused work.**

**Too big:**
- "Implement user authentication system"

**Right size:**
- "Create User model with email and password fields"
- "Add password hashing function"
- "Create login endpoint"
- "Add JWT token generation"
- "Create registration endpoint"

## Known Issues & Workarounds

### Hermes Bug: delegate_task ignores delegation.model config

**Status:** KNOWN BUG — Issue [#12440](https://github.com/NousResearch/hermes-agent/issues/12440) (P1, OPEN as of May 2026), [#11999](https://github.com/NousResearch/hermes-agent/issues/11999) (CLOSED but fix incomplete), [#17685](https://github.com/NousResearch/hermes-agent/issues/17685).

**Symptom:** Subagents always inherit the parent model regardless of `delegation.model`, `delegation.provider`, `delegation.base_url`, `HERMES_MODEL` env var, or `acp_args` settings. All three configuration methods fail.

**Impact:** Delegated tasks that need a specific model (cheaper, faster, or different provider) will silently run on the parent's model instead. This breaks cost-tiering and model-routing strategies.

**Workaround:** Use terminal subprocess instead of `delegate_task`:
```bash
hermes -z "görev açıklaması" --model gpt-5.4-mini --provider pollinations
```
The `-z` (oneshot) flag runs a single prompt and exits — faster than `chat`. This correctly uses the specified model. Not automated but reliable.

**Bonus — Reduce payload for Pollinations models:** Pollinations doesn't support function calling. Set `inherit_mcp_toolsets: false` in config.yaml delegation section, and pass `toolsets: []` to delegate_task for writer/helper agents. For research/code agents, pass minimal toolsets like `['web']` or `['terminal', 'file']`.

**When fixed:** Check Hermes changelog for #12440 resolution. The fix for #11999 was committed April 18, 2026 but was incomplete — #12440 remains open.

Full research with alternative framework comparison: `references/delegation-bug-research.md`

## User Preference: Delegate code changes to AI coding tools

**When making code changes, PREFER delegating to an AI coding tool** (OpenCode CLI, Codex CLI, Claude Code) over manual find-and-replace `patch()` calls. The user explicitly prefers this workflow. Coding tools handle multi-file edits, syntax, and verification in one shot.

Use manual `patch()` ONLY when:
- The change is a single trivial line
- The coding tool is unavailable or malfunctioning
- The user explicitly asks for a quick manual fix

For the coding tool delegation pattern, see `references/coding-tool-delegation.md`.

## Red Flags — Never Do These

- Start implementation without a plan
- **Make multi-file or non-trivial code changes via manual `patch()` when an AI coding tool is available** — delegate to OpenCode/Codex/Claude Code instead
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks that touch the same files
- Make subagent read the plan file (provide full text in context instead)
- Skip scene-setting context (subagent needs to understand where the task fits)
- Ignore subagent questions (answer before letting them proceed)
- Accept "close enough" on spec compliance
- Skip review loops (reviewer found issues → implementer fixes → review again)
- Let implementer self-review replace actual review (both are needed)
- **Start code quality review before spec compliance is PASS** (wrong order)
- Move to next task while either review has open issues

## Handling Issues

### If Subagent Asks Questions

- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

### If Reviewer Finds Issues

- Implementer subagent (or a new one) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

### If Subagent Fails a Task

- Dispatch a new fix subagent with specific instructions about what went wrong
- Don't try to fix manually in the controller session (context pollution)

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review:**
- Spec review catches under/over-building early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early (cheaper than debugging compounded problems later)

## Integration with Other Skills

### With writing-plans

This skill EXECUTES plans created by the writing-plans skill:
1. User requirements → writing-plans → implementation plan
2. Implementation plan → subagent-driven-development → working code

### With test-driven-development

Implementer subagents should follow TDD:
1. Write failing test first
2. Implement minimal code
3. Verify test passes
4. Commit

Include TDD instructions in every implementer context.

### With requesting-code-review

The two-stage review process IS the code review. For final integration review, use the requesting-code-review skill's review dimensions.

### With systematic-debugging

If a subagent encounters bugs during implementation:
1. Follow systematic-debugging process
2. Find root cause before fixing
3. Write regression test
4. Resume implementation

## Example Workflow

```
[Read plan: docs/plans/auth-feature.md]
[Create todo list with 5 tasks]

--- Task 1: Create User model ---
[Dispatch implementer subagent]
  Implementer: "Should email be unique?"
  You: "Yes, email must be unique"
  Implementer: Implemented, 3/3 tests passing, committed.

[Dispatch spec reviewer]
  Spec reviewer: ✅ PASS — all requirements met

[Dispatch quality reviewer]
  Quality reviewer: ✅ APPROVED — clean code, good tests

[Mark Task 1 complete]

--- Task 2: Password hashing ---
[Dispatch implementer subagent]
  Implementer: No questions, implemented, 5/5 tests passing.

[Dispatch spec reviewer]
  Spec reviewer: ❌ Missing: password strength validation (spec says "min 8 chars")

[Implementer fixes]
  Implementer: Added validation, 7/7 tests passing.

[Dispatch spec reviewer again]
  Spec reviewer: ✅ PASS

[Dispatch quality reviewer]
  Quality reviewer: Important: Magic number 8, extract to constant
  Implementer: Extracted MIN_PASSWORD_LENGTH constant
  Quality reviewer: ✅ APPROVED

[Mark Task 2 complete]

... (continue for all tasks)

[After all tasks: dispatch final integration reviewer]
[Run full test suite: all passing]
[Done!]
```

## Lightweight Parallel Mode (Small Greenfield Projects)

For **small projects** (3-6 files, <500 lines total, no existing codebase), skip the full 2-stage review cycle:

### When to Use
- Greenfield project with 3-6 independent files
- Each file is self-contained (<250 lines)
- No shared mutable state between files
- Tight deadline or prototyping phase

### How It Works

**1. Pre-write requirements and architecture** — share the plan with the user and get approval before dispatching subagents.

**2. Dispatch ALL tasks in parallel** via `delegate_task(tasks=[...])`:

```python
delegate_task(tasks=[
    {"goal": "Write db.py + parser.py for receipt system...", "toolsets": ["terminal","file"], "context": "..."},
    {"goal": "Write ocr_engine.py — EasyOCR wrapper...", "toolsets": ["terminal","file"], "context": "..."},
    {"goal": "Write main.py — Telegram bot...", "toolsets": ["terminal","file"], "context": "..."},
])
```

**3. Cross-reference between subagents:** Each subagent's context should mention which files are being written by OTHER subagents, and instruct them to read those files if they need to understand the interface. Example: `Read /path/to/db.py first to understand the save_receipt() signature.`

**4. No review cycle** — accept subagent output directly. Subagents verify their own syntax.

**5. Retry individually** if a task times out or fails.

### Parallel vs Sequential Decision

| Factor | Sequential (2-stage) | Parallel (lightweight) |
|--------|---------------------|----------------------|
| Project size | 6+ files, 500+ lines | 3-6 files, <500 lines |
| Existing codebase | Yes (regression risk) | No (greenfield) |
| File dependencies | Tight coupling | Mostly independent |
| Quality bar | Production/PR | Prototype/internal tool |
| Time budget | Hours | Minutes |

### Pitfall: Subagent Timeout on Large Packages
When subagents need to install packages (e.g., `easyocr` → `torch` 444MB), `pip install` may time out. Use `uv pip install` instead — significantly faster resolution and download. If a subagent reports timeout on pip install, tell the controller to run `uv pip install` directly rather than retrying via subagent.

## Remember

```
Fresh subagent per task
Two-stage review every time (production path)
Lightweight parallel mode for small greenfield (prototype path)
Spec compliance FIRST
Code quality SECOND
Never skip reviews on production code
Catch issues early
```

**Quality is not an accident. It's the result of systematic process.**

## Further reading (load when relevant)

When the orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these references for the specific discipline:

- **`references/context-budget-discipline.md`** — Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. Load when a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).
- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.

Both references adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).
