#!/usr/bin/env python3
"""
notebooklm-mcp wrapper with authentication fix for v2.0.11.

The installed notebooklm-mcp v2.0.11 has a bug: _ensure_client() starts the
browser but never calls authenticate(), so _is_authenticated stays False and
all tool calls fail with "Not authenticated or browser not ready".

This wrapper monkey-patches _ensure_client to call authenticate() after start.
"""
import sys
import os

# --- Monkey-patch before importing the server module ---
from notebooklm_mcp import server as server_module
from notebooklm_mcp.client import NotebookLMClient
from notebooklm_mcp.exceptions import NotebookLMError

original_ensure_client = server_module.NotebookLMFastMCP._ensure_client

async def patched_ensure_client(self):
    """Patched version that actually authenticates after starting the browser."""
    try:
        if self.client is None:
            self.client = NotebookLMClient(self.config)
            await self.client.start()
            # Patch: call authenticate() so _is_authenticated is set
            auth_success = await self.client.authenticate()
            if auth_success:
                import logging
                logging.getLogger("notebooklm_mcp").info(
                    "✅ NotebookLM client initialized and authenticated (patched)"
                )
            else:
                import logging
                logging.getLogger("notebooklm_mcp").warning(
                    "⚠️  Browser started but authentication check failed (patched)"
                )
    except Exception as e:
        import logging
        logging.getLogger("notebooklm_mcp").error(f"Failed to initialize client: {e}")
        raise NotebookLMError(f"Client initialization failed: {e}")

server_module.NotebookLMFastMCP._ensure_client = patched_ensure_client

# --- Run original server CLI ---
from notebooklm_mcp.cli import cli

if __name__ == "__main__":
    # Remove this wrapper from argv so click doesn't get confused
    cli()
