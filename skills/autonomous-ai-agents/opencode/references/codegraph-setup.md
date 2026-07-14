# CodeGraph Setup — MCP Knowledge Graph for OpenCode

> GitHub: [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) (46k★)
> npm: `@colbymchenry/codegraph`
> Video: Emrullah Yaprak — "Büyük Projelerde AI Maliyetlerini Yönetmenin En İyi Yolu"

## What It Is

CodeGraph is an **MCP server** that parses your codebase into a typed knowledge graph (SQLite + FTS5). OpenCode (and other agents) query the graph instead of grep/glob/Read — saving tokens, time, and money. Works with Claude Code, Codex, Cursor, OpenCode, Hermes Agent, and more.

**Benchmarks (7 OSS repos avg, Claude Opus 4.8):**
- 16% cheaper · 47% fewer tokens · 22% faster · 58% fewer tool calls
- Best on large repos (e.g. VS Code 10k files: 18% cheaper, 81% fewer tool calls)

## Installation

### Prerequisites
- Node.js v18+ (`node --version`)
- npm (`npm --version`)

### Step 1: Global Install
```bash
npm i -g @colbymchenry/codegraph
```
Verify: `codegraph --version`

### Step 2: Wire Up Agents
```bash
codegraph install -y
```
- `-y` = non-interactive, auto-detect + configure all detected agents
- Writes MCP config into OpenCode (`~/.config/opencode/opencode.json`) and Hermes Agent
- After install: restart agents for MCP changes to take effect

### Step 3: Initialize Per-Project
```bash
cd your-project
codegraph init -i
```
- Creates `.codegraph/` directory in project root
- `-i` = build initial graph immediately

### Important: `.codegraphignore`
Place in project root to exclude unwanted dirs:
```
node_modules/
.git/
__pycache__/
*.pyc
.env/
.venv/
dist/
build/
.cache/
*.log
```
Without this, indexing may scan 19k+ files and take 60s+.

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `codegraph_explore` | Primary — NL query returns source + relationship map + blast radius |
| `codegraph_search` | Quick symbol search by name (locations only) |
| `codegraph_node` | Full symbol details: signature, callers/callees, verbatim body |
| `codegraph_callees` | Functions a symbol calls |
| `codegraph_callers` | Functions that call a symbol |
| `codegraph_impact` | Blast radius for refactoring |
| `codegraph_files` | Indexed file tree with language + symbol counts |
| `codegraph_status` | Index health |

## When to Use

**Kazandırır:** Medium models (Sonet-level), deep/"how does X work" questions, large codebases, direct graph queries
**Kazandırmaz:** Strong models (Opus — already efficient), flat "who calls" queries, external service flows (webhook, Stripe)

## Pitfalls

- **First init without `.codegraphignore` crawls for minutes.** Always add ignore file first (19k+ files otherwise).
- **`codegraph init` uses current directory.** No `--path` flag; cd to project first.
- **Restart agents after `codegraph install`.** Running agents won't pick up file-based config changes.
- **Verify MCP tools exist** before relying: check Hermes startup logs or run a quick explore query.
