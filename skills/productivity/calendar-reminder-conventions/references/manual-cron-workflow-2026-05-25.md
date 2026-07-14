# Manual Cron Workflow — 2026-05-25

**Context:** `cronjob` tool was unavailable. Fallback to shell scripts + crontab.

## Session Snapshot

Edel asked for tomorrow's calendar check. Calendar returned one event:
- **Cafe mesai** — 2026-05-26 17:00-23:00 (+03:00)

## Created Files

### Reminder Script
`~/.hermes/cron/reminder_cafe_mesai_2026-05-26.sh`
- Schedule: 16:30 (30 min before event)
- Message: "Cafe mesain 1 saat sonra başlıyor ☕️ Hazır mısın? Bugün yoğun olur mu sence?"
- Delivery: `curl -X POST http://localhost:8642/api/chat/send` to gateway

### Follow-up Script
`~/.hermes/cron/followup_cafe_mesai_2026-05-26.sh`
- Schedule: 23:15 (15 min after event end)
- Message: "Cafe mesain bitti mi? Nasıl geçti bugün? Yoğun muydu yoksa rahat mıydı?"

### Crontab Entries Added
```
# Cafe mesai reminder 26 May (16:30)
30 16 * * * /home/ubuntu/.hermes/cron/reminder_cafe_mesai_2026-05-26.sh >> /home/ubuntu/.hermes/logs/cron_reminders.log 2>&1
# Cafe mesai follow-up 26 May (23:15)
15 23 * * * /home/ubuntu/.hermes/cron/followup_cafe_mesai_2026-05-26.sh >> /home/ubuntu/.hermes/logs/cron_followups.log 2>&1
```

## Lesson
- Gateway health check (`/health`) returned `{"status": "ok"}` — confirm before relying on it.
- Log files must exist before cron runs: `mkdir -p ~/.hermes/logs && touch cron_reminders.log cron_followups.log`
- Script permissions: `chmod +x` required.
