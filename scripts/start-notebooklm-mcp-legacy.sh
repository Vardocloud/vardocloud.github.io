#!/bin/bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
export NOTEBOOKLM_QUERY_TIMEOUT="120"
# Pin to legacy profile
nlm config set auth.default_profile legacy --quiet 2>/dev/null
exec /home/ubuntu/.local/bin/notebooklm-mcp --transport stdio
