### Process: Don't Scatter — Research First

When integrating with a new API that has complex auth (OAuth2, device identity, multi-header requirements), resist the urge to start with trial-and-error. Do this instead:

1. **Pull the official auth docs** for the target API (web_search or web_extract the auth/identity docs)
2. **Check GitHub issues** for known workarounds (e.g., Bitwarden's device info in body came from a GitHub issue)
3. **Look at the Hermes source** — the agent already has `agent/secret_sources/bitwarden.py` which may have the answer
4. **Formulate ONE hypothesis at a time**, test it, then iterate. Running 5 combos simultaneously without reading the error messages is wasteful (and frustrates the user — "bir dur tekrar düşün" is the signal you've scattered).
5. **When stuck, explain what you've tried and what the blocker is** — the user may know the answer faster than your research loop.

This prevents the scattered approach that wastes time and frustrates the user.
