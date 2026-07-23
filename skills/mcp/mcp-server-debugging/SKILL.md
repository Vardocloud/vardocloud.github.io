---
name: mcp-server-debugging
description: "Debug MCP server startup issues — slow imports, health check timeouts, connection failures, lazy initialization patterns."
version: 1.0.0
---

# MCP Server Debugging

Troubleshooting MCP server connection, health check, and startup issues.

## Slow Import / Health Check Timeout

**Symptom:** `hermes mcp add` connects but tool discovery times out.

**Cause:** Server does `from heavy_lib import HeavyClass` at module level, taking 10-20s.

### Diagnosis

Test the server directly:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize",\
  "params":{"protocolVersion":"2024-11-05","capabilities":{},\
  "clientInfo":{"name":"test","version":"1.0.0"}}}' | \
  timeout 10 /path/to/mcp-server 2>&1
```

Trace imports to find the bottleneck:
```bash
timeout 30 python3 -v -c "import heavy_package" 2>&1 | tail -40
```

For editable installs, find the source:
```bash
python3 -c "import heavy_package; print(heavy_package.__file__)"
find /home/ubuntu/.local -path "*server*" -name "*.py" 2>/dev/null
# Editable installs: look for __editable__*.pth files
cat /home/ubuntu/.local/lib/python3.11/site-packages/__editable__*.pth
```

### Fix: Lazy Import Pattern

**1 — Add `from __future__ import annotations`** at the top of `server.py`. This defers all type hints to strings so they don't trigger imports at module level.

**2 — Replace module-level import with lazy property:**
```python
class MCPServer:
    def __init__(self):
        self._heavy = None  # defer import
    
    @property
    def heavy_lib(self):
        if self._heavy is None:
            from heavy_package import HeavyClass  # loads on first use
            self._heavy = HeavyClass()
        return self._heavy
```

**3 — Replace all `self.heavy` references** with the property access (already works if named consistently).

**4 — Fix `NameError` in function signatures:**
If the type hint `markitdown_instance: HeavyClass` appears in a function signature, `from __future__ import annotations` makes it a string automatically. No other changes needed.

### Fix: Remove Unused Dependencies

For editable installs where the server imports cloud SDKs you don't need:

**Common heavy deps that can be removed (with approval):**
- `azure-*` packages → whole Azure SDK, only needed if you have Azure credentials
- Large ML models (magika) → check if file-type detection is essential

**How to check if a dependency is used:**
```bash
grep -r "Azure\|DocumentIntelligence\|ContentUnderstanding" /path/to/server/
# If only in imports and __init__, not called in any function, it's removable
```

**⚠️ CRITICAL RULE — Always ask the user before removing:**
> "Found X dependency. It does Y. We don't have credentials for it, so it'll always fail at runtime. Remove for ~N seconds faster startup, or keep for future use?"

Removing dependencies without understanding them or asking the user breaks trust. The user must approve any such change.

### Verification

After fix, test:
```bash
# Initialize (should be instant)
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":...}' | timeout 5 /path/to/mcp-server 2>/dev/null

# First tool call (slow import expected on first use)
# May take 15-20s depending on packages
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"some_tool","arguments":{...}}}' | timeout 30 /path/to/mcp-server 2>/dev/null
```

Then add to Hermes:
```bash
hermes mcp add <name> --command /path/to/wrapper.sh
```

## Wrapper Script Pattern

Always use a wrapper script for environment config:
```bash
#!/usr/bin/env bash
export CUSTOM_ENV="value"
exec /path/to/original-server "$@"
```

## NotebookLM MCP Auth Recovery

When `notebooklm-mcp` reports `authenticated: false` / `needs_auth`:

1. **Check keepalive Chrome ports** — NotebookLM açık Chrome'ları bul (port 49537/52065)
2. **Extract fresh cookies** — `Network.getAllCookies` ile taze cookie'leri çek
3. **Write to MCP profiles** — `~/.notebooklm-mcp-cli/profiles/legacy/pro/cookies.json`
4. **Restart gateway** — yeni MCP server taze cookie'lerle başlasın

Full prosedür: **`notebooklm-cdp-recovery` skill'ine bak**.

**Critical distinction**: Gateway restart vs MCP server kill:
- `pkill -f "notebooklm-mcp"` → MCP server ölür ama gateway RESTART ETMEZ. Tools'lar disconnect kalır.
- Gateway restart (`kill $(cat ~/.hermes/gateway.pid)`) → Yeni MCP server ayağa kalkar. Session kesilir.
- Recovery flow'da her zaman GATEWAY RESTART kullan, MCP kill kullanma.

**Cookie injection workaround** (gateway restart istenmiyorsa):
Canlı Chrome'dan cookie'leri `Network.setCookie` ile MCP'nin Chrome'una enjekte et. Ama bu geçici çözüm — MCP server hala auth yapmaz çünkü kendi CDP bağlantısı yok.

## Real Example: markitdown-mcp

Server: `trsdn/markitdown-mcp` v1.2.2 (editable install at `/tmp/markitdown-mcp/`)
- `from markitdown import MarkItDown` took ~15s at module level
- Azure `DocumentIntelligenceConverter` + `ContentUnderstandingConverter` added ~5s
- Both were unused (no Azure credentials), removable

**Fix applied:**
1. `from __future__ import annotations` added
2. Module-level `from markitdown import MarkItDown` removed
3. Lazy `@property` added in `MarkItDownMCPServer.__init__`
4. Azure converters removed from `converters/__init__.py` and `_markitdown.py` (with user approval)

**Result:** Server init 0.33s, first conversion ~19s, subsequent instant.

## MCP Tool Visibility Across Sessions

### Session vs Subagent Tool Registry

When you add an MCP server mid-session via `hermes mcp add`, the tools become available in config.yaml but are **NOT loaded into the current session's tool registry**. They require a new session to appear.

**Workaround:** Spawn a `delegate_task` subagent — subagents load tools fresh from config, so they CAN see the newly-added MCP tools even in the same parent session.

```python
# Current session: tools NOT visible
# Subagent: tools ARE visible
delegate_task(
    goal="Use notebooklm-mcp ask_question to...",
    toolsets=["terminal", "file", "search"]  # MCP tools auto-included
)
```

This is useful for testing MCP servers or running one-off queries without restarting the conversation.

## `hermes mcp test` Succeeds but Tools Return "MCP Server is not connected"

**Symptom:** `hermes mcp test <server>` reports `✓ Connected` and discovers tools, but when you try to use the MCP tools in-context (e.g. `mcp_<server>_ask_question`), they return `"MCP server '<server>' is not connected"`.

**Root cause:** `hermes mcp test` spawns a fresh one-shot connection — it proves the server binary starts and responds to `initialize`. But the Hermes MCP *client* (the persistent connection that feeds tools into your current session) maintains its own lifecycle. If the server process was killed and restarted, or if the MCP client's transport broke, the client does NOT auto-reconnect mid-session.

**Diagnostic chain:**
```bash
# 1. Server binary exists and works in isolation
hermes mcp test <server>

# 2. Check which binary Hermes is actually configured to use
hermes mcp list
# → Check the "Transport" column for the actual command path

# 3. Check if a server process is already running
ps aux | grep <server-name> | grep -v grep

# 4. Check if there's a version mismatch (common for notebooklm-mcp)
file /path/to/mcp-binary        # Python vs Node.js?
head -3 /path/to/mcp-binary     # First line reveals interpreter
```

**Resolutions (in order of preference):**

1. **Restart the Hermes MCP client** — The permanent fix is to force the client to re-establish its connection:
   ```bash
   # Option A: Remove and re-add the server (if re-configuration is safe)
   hermes mcp remove <server>
   hermes mcp add <server> --command /actual/path/to/binary
   
   # Option B: Restart the Hermes gateway process
   # The MCP client connections are managed by the gateway; a gateway restart
   # reconnects all MCP servers fresh.
   ```

2. **Use `delegate_task` for one-off queries** — Subagents load tools fresh from config, so they can use the MCP server even when the parent session's client is disconnected:
   ```python
   delegate_task(
       goal="Use notebooklm-mcp to query...",
       context="...",
       toolsets=["terminal", "file"]
   )
   ```

3. **Kill + restart pattern** — If you killed the MCP process and need it back:
   ```bash
   # Kill existing process
   pkill -f "notebooklm-mcp" 2>/dev/null
   sleep 1
   # Test connection (this spawns a fresh process)
   hermes mcp test notebooklm-mcp
   # If test passes but tools still unreachable:
   # → A new session or delegate_task is needed to pick up the fresh connection
   ```

**Prevention:** Avoid killing MCP process directly. If the server is stuck, prefer restarting via the Hermes MCP management layer rather than raw `pkill`.

## Node-Based MCP Server Recovery

### Scoped npm Packages (Binary Name ≠ Package Name)

Some MCP servers are published as **scoped npm packages** (`@scope/package-name`) but expose a binary with a different name. This means:
- `npm install -g @scop/name` installs to `~/.npm-global/lib/node_modules/@scop/name/`
- The binary symlink goes to `~/.npm-global/bin/<binary-name>` (not `@scope/name`)
- `which <binary>` may fail if npm-global is in PATH but the binary name isn't obvious

**Known examples:**

| Binary | Package | Install Command |
|--------|---------|----------------|
| `codegraph` | `@colbymchenry/codegraph` | `npm install -g @colbymchenry/codegraph` |
| `context-mode` | `context-mode` | `npm install -g context-mode` |

**Finding the binary:**
```bash
# List all globally installed binaries
ls ~/.npm-global/bin/ | sort

# Check what npm package provides a specific binary
readlink -f ~/.npm-global/bin/<binary>
# → resolves to ~/.npm-global/lib/node_modules/@scope/package/...

# If binary exists but 'which' fails, use full path
/home/ubuntu/.npm-global/bin/<binary> --version
```

### npm `--allow-scripts` Flag

When npm's `allow-scripts` config blocks postinstall scripts, the package installs but its native addons or postinstall hooks never run:

```
npm warn allow-scripts   <package>@<version> (postinstall: node scripts/postinstall.mjs)
```

**Fix — allow the blocked scripts:**
```bash
# One-time allow
npm install -g --allow-scripts=<package-name>,better-sqlite3,<other-addons> <package>

# Or permanent (adds to npm config)
npm config set allow-scripts=<package-name>,<other> --location=user
```

**Signs you need this:** Binary symlink exists but binary crashes silently, or `--version` returns no output.

### Symptom: `notebooklm-mcp` binary missing or `Connection closed`

The binary path may differ between npm prefix locations:
- `~/.local/bin/` — expected location (wrapper scripts often point here)
- `~/.npm-global/bin/` — actual location (where npm installs globals)

**Recovery steps:**

1. Check both locations:
   ```bash
   ls -la ~/.local/bin/<binary> 2>/dev/null
   ls -la ~/.npm-global/bin/<binary> 2>/dev/null
   ```

2. If missing, reinstall — check if it's a scoped package:
   ```bash
   npm install -g <package-name>  # might be @scope/name
   ```

3. If Playwright browser binary missing:
   ```bash
   npx playwright install chromium
   # Or from the package dir:
   cd $(npm root -g)/notebooklm-mcp && npx playwright install chromium
   ```

4. Add to Hermes (use the actual binary path):
   ```bash
   hermes mcp add <name> --command /home/ubuntu/.npm-global/bin/<binary>
   ```

5. Verify health:
   - Current session → subagent ile dene (see "MCP Tool Visibility Across Sessions" above)
   - Yeni session → tools directly visible

### MCP Binary in npm-global but Still "Command Not Found"

**Symptom:** Binary exists at `~/.npm-global/bin/<binary>` but `which <binary>` fails from Hermes terminal.

**Cause:** The `~/.npm-global/bin` directory is in the PATH that Hermes uses, but only for commands run AFTER login shell init. Some Hermes invocations use a clean PATH.

**Diagnostic:**
```bash
# Check if npm-global is in current PATH
echo "$PATH" | tr ':' '\n' | grep npm-global

# Test via non-interactive bash (Hermes mode)
bash -c 'which <binary>'

# Test with explicit full path
/home/ubuntu/.npm-global/bin/<binary> --version
```

**Fix options (in order):**
1. Use full path in MCP command config: `/home/ubuntu/.npm-global/bin/<binary> serve --mcp`
2. Add npm-global to bashrc before non-interactive guard (see `cli-tool-installation` skill)
3. Symlink from ~/.local/bin: `ln -s /home/ubuntu/.npm-global/bin/<binary> /home/ubuntu/.local/bin/<binary>`

### "Failed to connect: Connection closed"
The server process starts but crashes before completing the MCP handshake. Check:
```bash
# Run the wrapper directly to see the error
/path/to/wrapper.sh 2>&1 | head -20
```
Common causes: missing imports, syntax errors, missing `Main` in `pyproject.toml`.

### "Failed to connect: Timeout"
Server process started but didn't respond to `initialize` in time. Usually the slow import issue above.
Check: `connect_timeout: 120` in your MCP config to give more time for initialization.
