#!/bin/bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
export NOTEBOOKLM_QUERY_TIMEOUT="120"
# Pin to pro profile (default)
nlm config set auth.default_profile pro --quiet 2>/dev/null
exec /home/ubuntu/.local/bin/notebooklm-mcp --transport stdio
