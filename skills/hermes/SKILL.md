---
name: hermes
description: Class-level umbrella for consolidating Hermes domain skills into a reusable library.
umbrella: true
category: hermes
---

# Hermes Umbrella

This umbrella consolidates a family of Hermes domain skills into a single class-level knowledge base. It provides labeled subsections for absorbed skills to allow a maintainer to navigate and reuse their shared patterns without creating dozens of micro-skills.

## Absorbed Skills (umbrella)

- hermes-agent
- hermes-api-performance
- hermes-config-resilience
- hermes-cron-troubleshooting
- hermes-custom-ui
- hermes-delegation-debugging
- hermes-s6-container-supervision

### hermes-agent

Core integration patterns: provider resolution, delegation routing, session lifecycle, and agent orchestration. See the absorbed skill for deeper details.

### hermes-api-performance

Pattern: latency diagnostics, provider comparison, and throughput considerations; tests can be run against Hermes providers to measure end-to-end latency.

### hermes-config-resilience

Pattern: preserve Hermes Agent config across updates; golden_config.yaml, restore_config.py, drift checks.

### hermes-cron-troubleshooting

Pattern: diagnose Hermes cron job failures — delivery paths, topic routing, model/provider selection, and common failure modes.

### hermes-custom-ui

Pattern: building and embedding Hermes UI surfaces; API contracts, UI state management, and authentication guards.

### hermes-delegation-debugging

Pattern: diagnosing delegation/subagent failures — provider resolution, base_url inheritance, content filter blocks, and reconciliation steps.

> 📎 **Supervisor Pattern PoC:** `references/supervisor-pattern-poc.md` — delegate_task ile paralel sub-agent yönetimi, validation layer ve targeted retry pattern'inin proof-of-concept analizi. (3 Tem 2026)

### hermes-s6-container-supervision

Pattern: supervising services inside container using s6-overlay; lifecycle, health checks, and debugging tips.
