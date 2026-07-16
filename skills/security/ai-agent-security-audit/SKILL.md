---
name: ai-agent-security-audit
title: AI Agent Security Audit
description: >-
  Structured methodology for assessing the security posture of AI agent
  runtimes (Hermes Agent, OpenClaw, etc.). 7-layer defense-in-depth
  evaluation adapted from the RAK (Root/Agency/Keys) framework and
  the OpenClaw-Security notebook. Combined external threat radar +
  internal posture assessment for recurring audit cycles.
trigger: >-
  User asks for a security assessment, audit, or hardening review.
  Setting up a new AI agent system. Recurring monthly/weekly
  security review. After discovering a security issue (leaked keys,
  777 permissions, exposed gateway). Evaluating a new provider or
  service integration for the agent.
---
# AI Agent Security Audit

## Overview

Security assessment for AI agent systems (Hermes Agent, OpenClaw, Claude Code, etc.) follows a **7-layer defense-in-depth model** adapted from the RAK (Root/Agency/Keys) threat framework.

## The RAK Threat Model

Every AI agent system has three fundamental risk categories:

| Risk | Description | Example |
|------|-------------|---------|
| **Root** | Agent compromises host via shell/RCE | Hidden instruction in untrusted content leads to host compromise |
| **Agency** | Agent takes unintended actions in connected apps | "Clean up inbox" misinterpreted as delete all emails |
| **Keys** | Agent leaks credentials via context/logs | API key exposed through verbose error messages to public dashboards |

## 7-Layer Assessment Framework

### Layer 1 — Network / Gateway
- Gateway bound to loopback (127.0.0.1) only?
- No exposed public ports? (verify with UFW or firewall rules)
- Remote access via VPN/Zero-Trust only (Tailscale)?
- WebSocket origin validation enabled?
- Gateway hardening at maximum (strict mode)?
- TLS enabled for remote transport?

**Verification:** Run listener scan + check gateway config section.

### Layer 2 — Identity & Secrets
- Gateway tokens strong (>32 chars, random)?
- API keys in .env with restrictive permissions (600)?
- BWS/Bitwarden SM available for secrets?
- Plaintext key files hardened to 600?
- .git-credentials excluded from version control?
- OAuth tokens at minimum required scope?
- File permissions checked on all credential files?

**Verification:** Use `find` with `-perm /o+r` to detect world-readable credential files.

### Layer 3 — Runtime / Sandbox
- Agent runs as non-root user?
- Read-only filesystem where possible?
- Docker: capabilities dropped (cap_drop=ALL)?
- Container memory/CPU limits set?
- Advanced isolation (gVisor/Firecracker) for agent systems?
- Workspace access restricted (not full filesystem)?

### Layer 4 — Tool Policy
- Least-privilege tool scoping active?
- Dangerous tools (exec, spawn, write to sensitive paths) blocked?
- Human-in-the-loop for critical operations?
- Tool profiles configured per agent role?

### Layer 5 — Execution Control
- Command allowlist/denylist defined?
- Approval gate enforcing human-in-the-loop?
- Fallback behavior = deny when user unreachable?
- Session isolation per channel/user?
- Spending circuit breaker for LLM costs?

### Layer 6 — Audit & Monitoring
- Centralized audit logs (tamper-resistant storage)?
- All LLM calls and tool calls logged?
- Rate limiting on all endpoints?
- Security scan runs daily and weekly?
- Watchdog process for agent health?
- Token keepalive/refresh cron active?

### Layer 7 — Supply Chain
- Third-party skills/repos reviewed before install?
- Staging environment for changes?
- Backup + restore tested recently?
- Incident response playbook documented?

## Combined External + Internal Audit Pattern

For recurring audits (e.g. monthly 1st), combine two passes:

1. **External Radar** — search web for recent AI security developments (new CVEs, agent attacks, prompt injection techniques, AI + clinical-psychology intersection)
2. **Internal Assessment** — run all 7 layers above, report status changes since last audit

## File Permission Hardening Procedure

After any credential/key/token file operations, restrict permissions:
```bash
# Secrets directory
chmod 600 ~/.hermes/secrets/* 2>/dev/null
# Key files
chmod 600 ~/.hermes/soniox_api_key.txt ~/.hermes/soniox_password.txt 2>/dev/null
chmod 600 ~/.hermes/serper_key.txt ~/.hermes/tavily_key.txt ~/.hermes/brave_key.txt 2>/dev/null
chmod 600 ~/.hermes/google_client_secret.json 2>/dev/null
```

## Common Findings (July 2026)

| Finding | Severity | Fix |
|---------|----------|------|
| secrets/ directory files world-readable | CRITICAL | chmod 600 on all credential files |
| Key files 777 (soniox, serper, tavily, brave) | CRITICAL | chmod 600 on each |
| gateway strict mode disabled | MEDIUM | Enable in gateway config |
| BWS installed but plaintext keys persist | MEDIUM | Migrate to BWS, delete plaintexts |
| no-new-privileges not set in Docker | LOW | Add Docker security-opt flag |

## Pitfalls

- **Don't confuse Hermes Agent with OpenClaw.** RAK framework applies to both, but OpenClaw has sandbox/exec approval features Hermes lacks. Adapt layers to what's running.
- **File permissions compound.** A single 777 file in a 700 directory is still world-readable. Check both directory and file permissions.
- **BWS availability does not equal adoption.** Bitwarden SM may be installed but secrets still in plaintext. Active migration is required.
- **Default security scan skips file permissions.** The typical security_scan.sh checks ports, disk, memory, services, and Docker health — but NOT file permissions. Add this step separately.
- **Config changes require service restart.** Changing gateway or security settings needs `systemctl --user restart hermes-gateway` to take effect.
- **Secrets leak through backups.** 600-permission files may be included in backup archives with broader permissions. Exclude credential paths from backup scripts.

## References

- `references/rak-framework-assessment.md` — Detailed RAK evaluation checklist
- `references/file-permission-audit.md` — File permission scanning and known findings
