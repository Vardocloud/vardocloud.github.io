---
name: opencode
description: "Delegate coding to OpenCode CLI (features, PR review)."
version: 1.4.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, OpenCode, Autonomous, Refactoring, Code-Review]
    related_skills: [claude-code, codex, hermes-agent]
---

# OpenCode CLI

Use [OpenCode](https://opencode.ai) as an autonomous coding worker orchestrated by Hermes terminal/process tools. OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI.

## When to Use

- User explicitly asks to use OpenCode
- You want an external coding agent to implement/refactor/review code
- You need long-running coding sessions with progress checks
- You want parallel task execution in isolated workdirs/worktrees

## Prerequisites

- OpenCode installed: `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`
- Auth configured: `opencode auth login` or set provider env vars (OPENROUTER_API_KEY, etc.)
  - **Exception:** `opencode-zen` (built-in free models like `deepseek-v4-flash-free`, `mimo-v2.5-free`) needs NO API key — the CLI carries a built-in key. Just install the CLI and use `opencode run -m deepseek-v4-flash-free "prompt"` directly.
- Verify: `opencode auth list` should show at least one provider
- Git repository for code tasks (recommended)
- `pty=true` for interactive TUI sessions

### Container / Docker Environment

⚠️ **Global npm packages do NOT survive container rebuilds.** If the Hermes container is rebuilt or migrated (e.g. Oracle VPS → Docker), `opencode-ai` must be reinstalled.

**Installation in containers without `sudo` (common in Docker):**

```bash
# 1. Set npm prefix to user home (avoids EACCES on /usr/lib/node_modules)
npm config set prefix ~/.npm-global

# 2. Create dir and install with allow-scripts (postinstall links the binary)
mkdir -p ~/.npm-global
npm install -g --allow-scripts=opencode-ai opencode-ai@latest

# 3. Add to PATH persistently
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.npm-global/bin:$PATH"

# 4. Verify
opencode --version
```

Config (`~/.config/opencode/`) and session data (`~/.local/share/opencode/`) are also lost unless mounted via persistent volume. After install, reconfigure auth via `/connect` or manual provider setup.

**Why `--allow-scripts=opencode-ai`?** The `opencode-ai` npm package has a `postinstall` script that symlinks the CLI binary. Without this flag, the binary won't be linked after install — `which opencode` returns empty even though the package is in `node_modules`.

### Installation Check (Diagnostic)

To verify opencode CLI is actually installed (separate from the opencode-go proxy which runs independently on port 19998):

```bash
# Binary check
which opencode

# npm global check
npm list -g opencode-ai

# Config/session directories
ls ~/.config/opencode/
ls ~/.local/share/opencode/

# Proxy check (separate concern — runs even without CLI)
ss -tlnp | grep 19998
```

The opencode-go proxy (`python3 scripts/opencode-go-proxy.py`) is a **separate component** — it proxies API requests to `https://opencode.ai/zen/go` for Hermes' `opencode-go` provider. It does NOT require the opencode CLI binary to function. Conversely, installing the CLI does not affect the proxy. See `references/opencode-go-proxy-architecture.md` and `references/hermes-provider-health.md` for provider health and selection guidance.

## Key Config Options (from opencode.ai/docs)

- `model`: default primary model (e.g. `opencode-go/deepseek-v4-flash`)
- `small_model`: lightweight model for simple tasks (e.g. `pollinations/gemma`)
- `compaction`: `auto` (auto-compact on full context) or `prune` (remove old tool outputs)
- `snapshot`: enabled by default, disable for large repos (`"snapshot": false`)
- `attachment.image`: auto_resize, max_width/height, max_base64_bytes
- `{env:VAR_NAME}` and `{file:path/to/file}` for dynamic values
- Config precedence: Remote → Global (~/.config/opencode/) → ENV → Project → .opencode/ → Inline → Managed

## Built-in Agents (from opencode.ai/docs)

| Agent | Mode | Description |
|-------|------|-------------|
| **Build** | primary | Default. Full file/bash access. |
| **Plan** | primary | Restricted. Edits/bash = ask. |
| **General** | subagent | Research/multi-step. Full tools except todo. |
| **Explore** | subagent | Read-only. Fast codebase search. |
| **Scout** | subagent | Read-only. External doc/dependency research. |

## Agent Config Options (from opencode.ai/docs)

- **`steps`**: Max iterations before auto-summary (cost control)
- **`hidden: true`**: Hide from `@` autocomplete
- **`color`**: UI color (Hex or `accent`, `success`, `error`)
- **`top_p`**: Alternative to temperature
- **`prompt`**: Path to external prompt file via `{file:...}`
- Create via CLI: `opencode agent create`

## Custom Commands (from opencode.ai/docs)

- Markdown files in `~/.config/opencode/commands/` or `.opencode/commands/`
- Template variables: `$ARGUMENTS`, `$1`, `$2`, ...
- Shell injection: `` !`command` `` for dynamic output
- File references: `@filename`
- `subtask: true` forces subagent execution (clean context)

## Custom OpenAI-Compatible Providers

OpenCode supports any OpenAI-compatible API (Pollinations, Ollama, LM Studio, etc.) via the `@ai-sdk/openai-compatible` npm package. This is essential for using free/cheap models as sub-agents.

### Config Pattern (`~/.config/opencode/opencode.json`)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Display Name",
      "options": {
        "baseURL": "http://127.0.0.1:19999/v1"
      },
      "models": {
        "model-id": {
          "name": "Model Display Name",
          "limit": { "context": 128000, "output": 4096 }
        }
      }
    }
  }
}
```

### API Key

Set `<PROVIDER>_API_KEY` env var (uppercased provider name). For proxy setups that auto-inject the key, any non-empty value works:
```bash
export MYPROVIDER_API_KEY=***
```

### Proxy Requirement (Pollinations)

Pollinations uses Cloudflare that blocks default Python User-Agent (error 1010). A local proxy that adds browser UA is required:
- Adds `User-Agent: Mozilla/5.0...`
- Auto-injects API key if client doesn't send one
- Translates `/v1/responses` → `/v1/chat/completions` for OpenCode compatibility
- See `references/pollinations-proxy.md` for the proxy script, lifecycle commands, and pitfalls.

### Verifying Provider

```bash
opencode run -m myprovider/model-id "Say: test" --format json
```
Check the SQLite DB for response: `~/.local/share/opencode/opencode.db` (see Debugging section).

## Binary Resolution (Important)

Shell environments may resolve different OpenCode binaries. If behavior differs between your terminal and Hermes, check:

```
terminal(command="which -a opencode")
terminal(command="opencode --version")
```

If needed, pin an explicit binary path:

```
terminal(command="$HOME/.opencode/bin/opencode run '...'", workdir="~/project", pty=true)
```

## One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:

```
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Attach context files with `-f`:

```
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example", workdir="~/project")
```

Show model thinking with `--thinking`:

```
terminal(command="opencode run 'Debug why tests fail in CI' --thinking", workdir="~/project")
```

Force a specific model:

```
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

## Interactive Sessions (Background)

For iterative work requiring multiple exchanges, start the TUI in background:

```
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# Returns session_id

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send follow-up input
process(action="submit", session_id="<id>", data="Now add error handling for token expiry")

# Exit cleanly — Ctrl+C
process(action="write", session_id="<id>", data="\x03")
# Or just kill the process
process(action="kill", session_id="<id>")
```

**Important:** Do NOT use `/exit` — it is not a valid OpenCode command and will open an agent selector dialog instead. Use Ctrl+C (`\x03`) or `process(action="kill")` to exit.

### TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

### Resuming Sessions

After exiting, OpenCode prints a session ID. Resume with:

```
terminal(command="opencode -c", workdir="~/project", background=true, pty=true)  # Continue last session
terminal(command="opencode -s ses_abc123", workdir="~/project", background=true, pty=true)  # Specific session
```

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--session <id>` / `-s` | Continue a specific session |
| `--agent <name>` | Choose OpenCode agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output/events |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to a running opencode server |

## Procedure

1. Verify tool readiness:
   - `terminal(command="opencode --version")`
   - `terminal(command="opencode auth list")`
2. For bounded tasks, use `opencode run '...'` (no pty needed).
3. For iterative tasks, start `opencode` with `background=true, pty=true`.
4. Monitor long tasks with `process(action="poll"|"log")`.
5. If OpenCode asks for input, respond via `process(action="submit", ...)`.
6. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.
7. Summarize file changes, test results, and next steps back to user.

## PR Review Workflow

OpenCode has a built-in PR command:

```
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

Or review in a temporary clone for isolation:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')", pty=true)
```

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```
terminal(command="opencode run 'Fix issue #101 and commit'", workdir="/tmp/issue-101", background=true, pty=true)
terminal(command="opencode run 'Add parser regression tests and commit'", workdir="/tmp/issue-102", background=true, pty=true)
process(action="list")
```

## Sub-Agent Architecture (Multi-Agent Teams)

OpenCode agents can be created as `mode: subagent` with specific models, permissions, and system prompts. This enables multi-agent "team" architectures where a primary agent delegates to specialized workers.

### Creating Sub-Agents

Agent files go in `~/.config/opencode/agents/` (global) or `.opencode/agents/` (project). Markdown format:

```markdown
---
description: Brief purpose summary
mode: subagent
model: provider/model-id
temperature: 0.3
permission:
  edit: deny
  bash: deny
  write: deny
  task: deny
  todowrite: deny
---
System prompt here. Define the agent's role, language, and constraints.
```

### Critical: Sub-Agent Tool Behavior (Issue #26394)

When a primary agent delegates via the `task` tool, OpenCode sends **zero tools** in the sub-agent's API call — even if permissions allow tools. This is a known bug (GitHub issue #26394).

**This is BENEFICIAL for models that don't support function calling** (Pollinations, Ollama, etc.):
- Payload stays small (no 68KB tool definition list)
- Model just generates text without attempting tool calls
- Sub-agent responds with plain text that the primary agent reads

**Pattern**: For reasoning/writing/analysis sub-agents, deny all write tools anyway — they'll never get tools regardless, so they can only produce text. For coding sub-agents that NEED tools, use a different backend (e.g., `hermes -z` with Deepseek/Claude).

### Invoking Sub-Agents

From TUI:
```
@agent_name do this task...
```

From `opencode run`:
```bash
opencode run '@agent_name do this task...'
```

### Example Team Setup

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| analist | pollinations/glm | ❌ denied | Research, analysis |
| yazar | pollinations/gpt-5.4-mini | ❌ denied | Creative writing |
| yardimci | pollinations/gemma | ❌ denied | General help |
| kodcu | deepseek (via hermes -z) | ✅ allowed | Code changes |

For full team architecture, model quality comparisons, and Go fallback setup, see `references/pollinations-integration.md`.

For CodeGraph setup (MCP knowledge graph that optimizes OpenCode token usage), see `references/codegraph-setup.md`. CodeGraph auto-detects OpenCode and wires itself into `~/.config/opencode/opencode.json`.

For OpenCode Go proxy architecture (port 19998), model discovery, reasoning-model token budgeting, and systemd setup, see `references/opencode-go-proxy-architecture.md`.

List past sessions:

```
terminal(command="opencode session list")
```

Check token usage and costs:

```
terminal(command="opencode stats")
terminal(command="opencode stats --days 7 --models anthropic/claude-sonnet-4")
```

## `oc_wrapper.py` — Silent Output Workaround

`opencode run` writes model responses only to the SQLite DB, not stdout. Use the bundled wrapper script to get readable output:

```bash
python3 ~/.hermes/scripts/oc_wrapper.py <rol> "<prompt>"
# Roller: kodcu (minimax), analist (glm), yazar (gpt-5.4-mini), yardimci (gemma)
```

The script: (1) runs `opencode run -m pollinations/<model>`, (2) waits for DB write, (3) extracts text parts from the latest session, (4) prints to stdout. See `scripts/oc_wrapper.py`.

## Pitfalls

- Interactive `opencode` (TUI) sessions require `pty=true`. The `opencode run` command does NOT need pty.
- `/exit` is NOT a valid command — it opens an agent selector. Use Ctrl+C to exit the TUI.
- PATH mismatch can select the wrong OpenCode binary/model config.
- If OpenCode appears stuck, inspect logs before killing:
  - `process(action="log", session_id="<id>")`
- Avoid sharing one working directory across parallel OpenCode sessions.
- Enter may need to be pressed twice to submit in the TUI (once to finalize text, once to send).
- **`opencode run` is silent for text-only responses.** The command writes headers to stderr but model text responses only appear in the SQLite database (`~/.local/share/opencode/opencode.db`), not stdout. `--format json` only emits tool-related events. **Use `scripts/oc_wrapper.py`** to extract responses programmatically.
- **`--agent <subagent>` falls back to build agent.** Sub-agents (mode: subagent) cannot be used as primary agents with `--agent`. OpenCode prints a warning and uses the build agent with the specified model instead. Use `@agent_name` from TUI or `opencode run '@agent_name task'` for delegation.
- **TUI model override with `-m` works.** `opencode -m pollinations/minimax` launches the TUI with that model as primary agent. Use this to test sub-agent models directly in interactive mode.
- **Custom providers + tools = large payloads.** OpenCode sends all tool definitions even to models that don't support function calling. For free/cheap models without tools, create sub-agents with all permissions set to `deny` and rely on the #26394 bug (sub-agents get no tools anyway).
- **Pollinations models cannot delegate to sub-agents.** Models without function calling support (minimax, glm, gpt-5.4-mini, gemma) ignore the `task` tool. When used as primary agent, `@agent_name` mentions silently fail — no error, no session created. **Solution**: Use a tool-capable primary agent (OpenCode Go/Zen free models, deepseek-v4-flash-free, or Deepseek via `hermes -z`) + Pollinations sub-agents. Verify: check `opencode.db` for new session creation after `@agent_name` invocation.
- **Sub-agent model override may be ignored** (GitHub issue #18615). When passing both `agent` and `model`, the agent's built-in fallback chain can override the model. Verify with `opencode --version` >= 1.15.
- **OpenCode Go API key requires interactive `/connect` or manual auth.json.**

## Formatters (from opencode.ai/docs)
- DISABLED by default. `ruff`: `["ruff", "format", "$FILE"]` for `.py, .pyi`
- Ours: `/home/ubuntu/.hermes/hermes-agent/venv/bin/ruff`, xclip installed

## Troubleshooting (from opencode.ai/docs)
- Logs: `~/.local/share/opencode/log/`, Debug: `opencode --log-level DEBUG`
- Linux needs `xclip`/`xsel`/`wl-clipboard` (headless: Xvfb)
- Provider errors: `<providerId>/<modelId>` format, check `opencode models`
- Config reset: `rm -rf ~/.local/share/opencode` then `/connect`

## Verification

Smoke test (TUI mode — most reliable for non-coding verification):

```bash
# Start OpenCode in background TUI
terminal(command="opencode", background=true, pty=true)
process(action="submit", session_id="<id>", data="Just say: OPENCODE_SMOKE_OK")
process(action="log", session_id="<id>")
```

For coding tasks, `opencode run` smoke test still works if the task involves file changes:
```bash
terminal(command="opencode run 'Create /tmp/smoke_test.txt with content SMOKE_OK'")
```

**DB verification** — when `opencode run` output is silent, check the SQLite DB:
```bash
python3 -c "
import sqlite3, json
db = sqlite3.connect('$HOME/.local/share/opencode/opencode.db')
rows = db.execute(\"SELECT p.data FROM part p JOIN message m ON p.message_id = m.id WHERE m.session_id = '<session_id>' ORDER BY p.rowid\").fetchall()
for r in rows: print(json.loads(r[0]).get('text','')[:200])
"
```

Success criteria:
- Output includes expected text (in DB or TUI log)
- Command exits without provider/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `opencode run` for one-shot automation — it's simpler and doesn't need pty.
2. Use interactive background mode only when iteration is needed.
3. Always scope OpenCode sessions to a single repo/workdir.
4. For long tasks, provide progress updates from `process` logs.
5. Report concrete outcomes (files changed, tests, remaining risks).
6. Exit interactive sessions with Ctrl+C or kill, never `/exit`.
