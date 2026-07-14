# Golden Config — Post-Update Resilience

When `hermes update` runs, it does `git pull` on the Hermes repo.  
Config in `~/.hermes/` is outside the git repo, but updates can still  
trigger config migrations or container restarts that reset settings.

The golden_config system protects against this.

## Architecture

```
hermes update
    ↓
post-update.sh (hooks/post-update.sh)
    ↓
restore_config.py --post-update
    ├── Step 1: Snapshot (backup_snapshot.sh)
    ├── Step 2: Sync golden with current config
    ├── Step 3: Check config drift
    ├── Step 4: Restore golden values to config
    ├── Step 5: Restart gateway
    └── Step 6: System verification (verify_system.sh)
```

## Files

| File | Purpose |
|---|---|
| `~/.hermes/scripts/golden_config.yaml` | Single Source of Truth — snapshot of all config settings |
| `~/.hermes/scripts/restore_config.py` | Engine: sync, check, restore, post-update modes |
| `~/.hermes/hooks/post-update.sh` | Triggers restore after each `hermes update` |
| `~/.hermes/scripts/backup_snapshot.sh` | Creates pre-restore timestamped snapshots |
| `~/.hermes/scripts/verify_system.sh` | Post-restore system health check |

## restore_config.py Modes

```
--check:       Dry-run, show diff, exit 0=aligned 1=drift detected
--sync:        Read current config, add new entries to golden_config.yaml
--restore:     Sync first, then apply golden values to config.yaml
--post-update: Full pipeline: snapshot → sync → restore → restart → verify
--force:       (with --restore) Also overwrite _config_version
```

## Key Design Rules

1. **golden_config.yaml is the Single Source of Truth** — never edit config.yaml directly for settings you want to persist. Edit golden, then `--restore` applies it.
2. **`_config_version` is NEVER overwritten** — Hermes uses this for internal migrations. `--restore` preserves it automatically (unless `--force`).
3. **API key values are NOT in golden** — only placeholders. Keys come from `.env` or Bitwarden SM. golden stores `api_key: ''` for auxiliary model configs.
4. **Config version 23** — current `_config_version` on this server (2026-06-11).

## When to Sync

Run `restore_config.py --sync` after adding new:
- Custom providers (`custom_providers`)
- Model aliases (`model_aliases`)
- MCP servers (`mcp_servers`)
- Auxiliary model configs (`auxiliary.*`)
- Plugins
- Toolsets
- Fallback providers

The sync MERGES — it adds what's new, doesn't remove what's golden.

## Config Drift Detection

```bash
python3 ~/.hermes/scripts/restore_config.py --check
```

Exit code 0 = all aligned. Exit code 1 = drift detected.

## Fixing golden_config.yaml Directly

When golden has a stale value (e.g. `secrets.bitwarden.enabled: false` → should be `true`):

1. Edit `scripts/golden_config.yaml` directly (ruamel.yaml preserves comments/ordering)
2. Run `python3 scripts/restore_config.py --restore` to apply to config.yaml
3. Gateway automatically restarts if changes were applied

## Relationship with Bitwarden SM\n\n- **API keys:** Bitwarden holds the actual values. Golden config holds the config structure (provider names, model names, auxiliary settings). They are complementary.\n- **Post-update flow:** Bitwarden keys survive update naturally (outside server). Golden config restores config.yaml. Together they provide full update resilience.\n- **override_existing: true:** `secrets.bitwarden.override_existing: true` means Bitwarden values always win over `.env` values. This is set in config.yaml (and protected by golden config).
