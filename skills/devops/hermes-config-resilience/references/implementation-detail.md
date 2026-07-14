# Golden Config Detail — Hermes Update Resilience

## File Locations

All files under Hermes home. Key paths:
- `scripts/golden_config.yaml` — 700+ lines, full config snapshot
- `scripts/restore_config.py` — v2, uses ruamel.yaml (preserves comments/order)
- `hooks/post-update.sh` — calls `restore_config.py --post-update`
- `scripts/backup_snapshot.sh` — directory copy before restore
- `scripts/verify_system.sh` — health check after restore

## restore_config.py Internals

### Dependencies
- `ruamel.yaml` — preserves comments and key ordering. Install: `pip install ruamel.yaml`
- Uses `yaml.preserve_quotes = True` and `yaml.default_flow_style = False`

### Key Design Decisions

1. **`_config_version` sacred**: golden carries the value but merge_config() explicitly skips it. Hermes uses this for migration tracking.

2. **API keys excluded**: `api_key` fields in `auxiliary.*` are stored as `''` (empty string). Real values from `.env` or Bitwarden SM.

3. **Section merge for SOUL/AGENTS**: Uses `parse_sections()` regex-based section splitter. Old content = snapshot backup. Sections present in old but not new = appended at end. Existing sections = new content wins.

4. **Named-list sync for `custom_providers`**: Identified by `name` field. Only NEW providers (names not in golden) are added during sync. Existing providers are NOT updated — golden wants the current config's version.

5. **Dict-entry sync for `model_aliases`, `mcp_servers`, `platform_toolsets`**: New sub-keys added, existing ones untouched.

6. **Toolsets**: JSON string comparison. Parses both config and golden, diffs the sets, merges new items.

## Config Merge Algorithm

merge_config() walks golden keys and applies them to config:
- `REPLACE_KEYS` (`custom_providers`, `model_aliases`, etc.): full list replacement
- `auxiliary.vision`, `web_extract`, etc.: full subsection replacement (12 named subs)
- Other auxiliary keys: dict-level merge (update sub-keys individually)
- `plugins`: dict merge with list merge for enabled/disabled
- Top-level dict keys: individual key replacement
- Other top-level: direct assignment

## Environment

- Server: Oracle Cloud ARM64
- Hermes source: `/data/ubuntu/hermes-agent/`
- Config version at time of writing: 23
- Bitwarden project: `hermes-api-keys` (10 secrets migrated)
