# NotebookLM MCP Direct CLI Usage

When MCP tools aren't loaded in the current session (e.g. newly installed MCP server, or session started before server was added), you can still interact with NotebookLM via the MCP binary directly using JSON-RPC over stdio.

## Quick Reference

```python
import subprocess, json

MCP_BINARY = "/home/ubuntu/.npm-global/bin/notebooklm-mcp"

def call_mcp(method, arguments, timeout=120):
    """Call a notebooklm-mcp tool via JSON-RPC stdio."""
    req = {
        "jsonrpc": "2.0", "id": 1,
        "method": "tools/call",
        "params": {"name": method, "arguments": arguments}
    }
    proc = subprocess.Popen(
        [MCP_BINARY],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True
    )
    out, err = proc.communicate(input=json.dumps(req) + "\n", timeout=timeout)
    result = json.loads(out)
    inner = json.loads(result["result"]["content"][0]["text"])
    return inner
```

## Common Operations

### 1. Check Health
```python
health = call_mcp("get_health", {}, timeout=10)
# {"success": true, "data": {"authenticated": true/false, ...}}
```

### 2. Add a Notebook to Library
```python
call_mcp("add_notebook", {
    "name": "APA Bilgi",
    "url": "https://notebooklm.google.com/notebook/NOTEBOOK_ID",
    "description": "..."
})
```

### 3. Ask Question
```python
result = call_mcp("ask_question", {
    "question": "Yazıyı yeniden yaz...",
    "notebook_name": "APA Bilgi"
}, timeout=300)
# result["data"]["response"] contains the answer
```

### 4. List Notebooks
```python
notebooks = call_mcp("list_notebooks", {}, timeout=10)
```

### 5. Select Active Notebook
```python
call_mcp("select_notebook", {"name": "APA Bilgi", "id": "apa-bilgi"})
```

## Timeout Notes

| Operation | Typical Timeout |
|-----------|----------------|
| `get_health` | 10s |
| `list_notebooks` | 10s |
| `add_notebook` | 15s |
| `ask_question` | 180-300s (browser launch + Gemini 2.5 processing) |
| `setup_auth` | N/A (headed mode, interactive) |

- First `ask_question` call after install may take 3-5 minutes (Playwright browser first launch)
- Subsequent calls are faster (browser stays warm)

## Binary Path

```
Real binary: /home/ubuntu/.npm-global/bin/notebooklm-mcp
  → symlink to: ../lib/node_modules/notebooklm-mcp/dist/index.js

Wrapper: ~/.local/bin/notebooklm-mcp-wrapper.sh
  → exec ~/.local/bin/notebooklm-mcp (DON'T use — binary may be missing there)
```

## Data Locations

- Config: `~/.config/notebooklm-mcp/`
- Data: `~/.local/share/notebooklm-mcp/`
- Library: `~/.local/share/notebooklm-mcp/library.json`
- Chrome profile: `~/.local/share/notebooklm-mcp/chrome_profile`
