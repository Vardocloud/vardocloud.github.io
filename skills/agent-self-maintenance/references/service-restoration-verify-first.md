# Service Restoration: Verify Before Restoring

**Date:** 17 Haz 2026
**Root cause:** Agent auto-restored OpenWebUI when Edel reported a gateway access issue, without checking if the service was still in use.

## The Rule

When a user reports an access issue:

1. **Diagnose first** — `systemctl`, `ss -tlnp`, health check endpoints
2. **Check context** — does the user actually use this service?
3. **Ask if unsure** — never assume which services to restore
4. **Restore only what's needed** — not every missing container

## Anti-Pattern

```
User: "X'e erişemiyorum"
Agent: [checks] → X çalışıyor, ama Y container'ı yok → [restores Y] → "Y'yi de kurdum"
User: "Y'yi neden kurdun? Onu bilerek silmiştik!"
```

## Correct Pattern

```
User: "X'e erişemiyorum"
Agent: [checks] → X çalışıyor, Y container'ı yok
Agent: "X çalışıyor. Bu arada Y durmuş — kullanıyor musun, geri yükleyeyim mi?"
User: "Hayır, Y'yi bilerek silmiştik"
Agent: "Tamam, Y'ye dokunmuyorum"
```
