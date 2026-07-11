#!/usr/bin/env bash
# Wrapper for markitdown-mcp with restricted safe directories
# Only allows access to /home/ubuntu and /tmp
export MARKITDOWN_SAFE_DIRS="/home/ubuntu:/tmp"
exec /home/ubuntu/.local/bin/markitdown-mcp "$@"
