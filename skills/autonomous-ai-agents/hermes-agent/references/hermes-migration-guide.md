---
name: hermes-migration
description: "Full Hermes Agent migration between machines — zero data loss checklist, migration package creation, and post-migration verification."
platforms: [linux]
---

# Hermes Agent Full Migration

Comprehensive migration of Hermes Agent from one host to another. Covers all data paths (config, skills, scripts, wiki, sessions, cron, MCP, Chrome profiles) and post-migration reconfiguration.

## When to Use

- Moving Hermes to a VDS (virtual dedicated server)
- Migrating from cloud to local (or vice versa)
- Setting up a secondary/worker instance from primary
- Rebuilding on a new host after hardware change

## Critical Rules (Read First)

1. **Sensitive data (API keys, SSH private keys, secret tokens) stays with the HUMAN.** Never embed them in the migration tarball. The human must transfer them manually.
2. **BWS/BW auth must be re-authenticated on new host.** Session tokens are machine-bound.
3. **Generate new SSH keys on new host.** Never copy private keys across machines.
4. **Memory taint:** After migration, update MEMORY.md to remove stale host-specific facts (old IPs, proxy configs, cloud references).

---

## Phase 1: Inventory (Source Machine)

Count what's being moved: Hermes home size, wiki file count, skill count, script count, cron job count. Note any paths with special content (Chrome profiles, NotebookLM cookies, MCP configs).

**Checklist:**
- Hermes config (config.yaml)
- Environment file (the human moves this — see Rule 1)
- Skills directory
- Scripts directory
- Cron job definitions
- Profile data (memories, sessions)
- Session database (FTS5 message store)
- Wiki files
- NotebookLM auth cookies (JSON profiles)
- Chrome profiles (optional — large)

---

## Phase 2: Migration Package

Create a tarball excluding sensitive paths. Use rsync or tar with explicit excludes:

```
EXCLUDE: .env, ssh/, backup-*, audio_cache, cache, checkpoints
INCLUDE: skills/, scripts/, cron/, profiles/, data/, wiki/, notebooklm profiles/
```

Package the sensitive-data manifest as a separate file so the human knows what to transfer manually.

---

## Phase 3: Install on Target

1. Install Hermes Agent on target (follow official docs: https://hermes-agent.nousresearch.com/docs)
2. Extract migration package
3. Restore Hermes data directories
4. Restore NotebookLM cookie profiles
5. **Human step:** Place environment file manually
6. Re-index wiki: `hermes wiki index --rebuild`
7. Restore cron jobs: `hermes cron restore`

---

## Phase 4: Post-Migration Reconfiguration

Settings that change per-host:

| Setting | What to Update |
|---|---|
| Hostname | `/etc/hostname` |
| Gateway bind address | In config.yaml → `gateway.host` |
| SSH port | In config.yaml → `gateway.ssh_port` |
| Telegram webhook URL | In config.yaml → `telegram.webhook_url` |
| Voice agent host | Voice config IP/port |
| Tailscale node | Register as new node |
| MEMORY.md | Remove stale host facts |

---

## Phase 5: Verification Checklist

- Hermes version runs correctly
- All skills visible
- All cron jobs restored
- Wiki search works (FTS5)
- Memory entries accessible
- Test Telegram message sent to user: "New host online ✅"
- NotebookLM auth works
- BWS secret list returns data
- Voice agent connects
- Old host references removed from memory

---

## Architecture Patterns

### Single Instance
One Hermes, all services on one machine.

### Primary + Worker
Primary (decision-maker + Telegram + sensitive data) on trusted machine. Worker (Chrome/CDP, voice, cron) on operation machine. Communication via Tailscale SSH tunnel.

### 3-Node (Primary + Worker + Proxy)
- Primary: Trusted PC (BWS, sensitive configs, core agent)
- Worker: VDS (7/24 services, scraping, heavy compute, cron)
- Proxy: Local machine with residential IP (bot bypass via Chrome)
- All three connected via Tailscale mesh

---

## Security

- Vault machine holds all secrets; worker/proxy nodes call vault via TLS
- Assume any VDS/hosted provider can read RAM and disk
- No plaintext secrets on non-vault machines
- Migration tarball must not contain private keys or API tokens
