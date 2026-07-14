---
name: kanban
description: "Hermes Kanban — durable multi-agent worktree dispatch system. Architecture, configuration, worker lifecycle, profile setup, and proper usage patterns. NOT the same as delegate_task or cron."
category: devops
tags: [kanban, worker, dispatch, multi-agent, task-management, durable-execution]
---

# Hermes Kanban — Durable Task Dispatch

## When to Use

Kanban is for **durable, multi-step tasks that must survive gateway restarts.** Each worker runs as a separate `hermes chat -q` subprocess.

| Tool | Use Case | Durability | Cost |
|------|----------|:----------:|:----:|
| **delegate_task** | Quick parallel work within one session | ❌ Dies with parent | 🟢 Low |
| **Kanban** | Long-running, restart-safe tasks | ✅ Survives restart | 🔴 High |
| **Cron** | Scheduled recurring jobs | ✅ Scheduled | 🟡 Medium |

Use Kanban when:
- Research takes multiple steps and might span hours
- Work must continue if the agent session ends
- You need dependency tracking (parent-child task relationships)
- You want visible task progression on a board

DO NOT use Kanban for:
- Quick searches or single tool calls (use delegate_task)
- Scheduled recurring work (use cron)
- Interactive chat (just talk directly)

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  GATEWAY                          │
│  ┌──────────────────────────────────────────┐    │
│  │  DISPATCHER (every N seconds)            │    │
│  │  • Scans board for READY tasks           │    │
│  │  • Spawns: hermes -p <profile> chat -q   │    │
│  │  • Passes HERMES_KANBAN_TASK env var    │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              KANBAN BOARD (SQLite)               │
│  States: ready → running → blocked/done/archived │
│  Path: ~/.hermes/kanban/boards/<board>/kanban.db │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              WORKER (subprocess)                 │
│  1. kanban_show() → read task                    │
│  2. Work using normal Hermes tools               │
│  3. kanban_complete() / kanban_block()           │
│  4. kanban_heartbeat() during long ops           │
└─────────────────────────────────────────────────┘
```

## Worker Lifecycle

1. **Dispatcher** checks board every `dispatch_interval_seconds` (default: 60)
2. Finds `ready` tasks and spawns workers
3. Worker starts as: `hermes -p <assignee> chat -q "<task body>"`
4. Worker calls `kanban_show()` to read its task (title, body, prior attempts, context)
5. Worker uses normal tools (web_search, web_extract, etc.)
6. Worker reports back via:
   - `kanban_complete(summary="...", metadata={...})` — success
   - `kanban_block(reason="...")` — needs human input
   - `kanban_comment(task_id, body="...")` — progress update
7. For long operations: `kanban_heartbeat(note="...")` prevents timeout

## Configuration

```yaml
kanban:
  dispatch_in_gateway: true           # Run dispatcher inside gateway
  dispatch_interval_seconds: 120      # Check every 2 minutes (default: 60)
  failure_limit: 3                    # Retries before blocking (default: 2)
  orchestrator_profile: default       # Profile for root tasks
  default_assignee: ''                # Fallback when no assignee specified
  max_in_progress_per_profile: null   # No limit on concurrent workers
  auto_decompose: true                # Auto-split tasks (when useful)
  auto_decompose_per_tick: 1          # Max 1 decomposition per tick
  dispatch_stale_timeout_seconds: 14400  # 4h timeout for stale tasks
```

### Key Settings Explained

- **`auto_decompose: true`** — Dispatcher asks decomposer LLM to break complex tasks into sub-tasks. Use `auto_decompose_per_tick: 1` to limit token cost.
- **`dispatch_interval_seconds: 120`** — Less frequent checks reduce gateway load. Tasks wait 2 minutes before spawning.
- **`failure_limit: 3`** — More retries before marking a task as blocked/failed.

## Profiles (Assignees)

Each Kanban profile can use a different model for cost optimization:

```yaml
profiles:
  researcher:           # Free model for research
    model: mimo-v2.5-free
    provider: opencode-zen
  writer:               # Economical for content
    model: deepseek-v4-flash
    provider: deepseek
  reviewer:             # Strong model only for critical decisions
    model: deepseek-v4-pro
    provider: deepseek
```

The dispatcher runs: `hermes -p <assignee> chat -q "<task body>"` — whatever model the profile has configured is what the worker uses.

## Creating Tasks

### From CLI
```bash
hermes kanban create "Title" --body "Instructions" --assignee researcher
```

### From Agent (Orchestrator)
```
kanban_create(
    title="Research APA sleep article",
    assignee="researcher",
    body="Extract and summarize the sleep article from apa.org/monitor/2026/06/sleep-brain-mental-health",
    skills=["firecrawl"]              # Extra skills for this worker
)
```

### With Dependencies
```
kanban_create(title="Research", assignee="researcher-a")     # → t_r1
kanban_create(title="Write draft", assignee="writer",
    parents=["t_r1"])                                         # Waits for t_r1
```

### Goal Mode (Auto-Judge)
```
kanban_create(
    title="Translate docs to Turkish",
    assignee="linguist",
    goal_mode=True,
    goal_max_turns=15,
    body="Acceptance: every page translated, no English left"
)
```

## Board Management

```bash
# Init board
hermes kanban init

# Create/switch boards
hermes kanban boards create research --name "Research Tasks" --switch
hermes kanban boards switch research

# Monitor
hermes kanban watch          # Live activity
hermes kanban list           # All tasks
hermes kanban stats          # Board statistics

# Lifecycle
hermes kanban complete t_xxx
hermes kanban block t_xxx --reason "Need input"
hermes kanban comment t_xxx --body "Progress update"
```

## Important Distinctions

### Kanban vs delegate_task

| Aspect | delegate_task | Kanban |
|--------|:------------:|:------:|
| Process | Subagent in parent session | Separate hermes chat -q process |
| Durability | Dies if parent interrupted | Survives gateway restart |
| Cost | Subagent model calls | Full Hermes session per worker |
| Dependencies | Manual | Built-in via parents=[] |
| Visibility | None | Board with states |
| Best for | Quick parallel work | Long-running, restart-safe tasks |

### Kanban vs Cron
- **Cron**: Time-based recurring execution (APA daily scan at 09:00)
- **Kanban**: Event-based, on-demand task execution (deep research when requested)
- They complement each other — cron feeds tasks, Kanban executes them

## Decomposer (Auto Task Splitting)

The decomposer is **text-only** — it receives task title + body as plain text. It uses `get_text_auxiliary_client("kanban_decomposer")`, not a vision/multimodal client. Multimodal models (MiniMax M3, etc.) provide NO benefit here because image/video attachments never reach the decomposer.

**System prompt language:** The decomposer's `_SYSTEM_PROMPT` in `kanban_decompose.py` must include an explicit English-output instruction (`"IMPORTANT: ALL output MUST be in English"`) so it produces English task titles/bodies even when the input task is in Turkish.

**Model selection for decomposer:**
- Text-only reasoning model is sufficient (no multimodal needed)
- Strong structured JSON output capability required
- Language quality matters for task bodies
- DeepSeek V4 Flash (NVIDIA free tier) is a good candidate — MIT license, 13B active, strong reasoning, English output confirmed by testing
- Avoid overkill (don't put 284B full models on this lightweight task)

## Pitfalls

- **High cost:** Each worker is a full Hermes session. Only use for tasks that genuinely need durability.
- **auto_decompose overhead:** When enabled, the decomposer LLM runs every tick on every ready task. Keep `auto_decompose_per_tick: 1` to limit.
- **Profile must exist:** Dispatcher silently fails on unknown assignee names. Always check profiles with `hermes profile list`.
- **Gateway required:** Without running gateway, tasks stay in `ready` forever.
- **Worker skills:** Extra skills loaded via `skills=["name"]` on kanban_create must be installed on the assignee's profile.
- **Session isolation:** Workers see NO conversation history — pass all context in the task body.
