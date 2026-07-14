# Security/Circuit Breaker Phase — Prompt Template

For autonomous operations where Vanitas manages budget, APIs, or systems without human oversight.

## Prompt Template

12 Tavily deep queries across circuit breaker, monitoring, and audit patterns.
Output: guardrail architecture, kill switch design, approval flow, and skill template.

## Key design principles

- Never auto-delete: Soft pause, never hard delete campaigns/keywords
- Budget circuit breaker: If daily spend exceeds 150 percent of expected, pause ALL activity
- Approval gates: Budget changes over 20 percent ask Edel; keyword changes auto; new campaigns ask Edel
- Audit log: Every change logged with timestamp plus reason plus before/after values
- Kill switch: Single command Edel can send via Telegram to halt all autonomous operations
