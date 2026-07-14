# Hermes delegate_task Limitleri

## delegate_task: Per-task model override YOK

Test edildi (30 Mayıs 2026, v0.15.1):

```python
delegate_task(tasks=[
    {"goal": "Write code", "model": "minimax", "provider": "pollinations"},
    {"goal": "Write text", "model": "gpt-5.4-mini", "provider": "pollinations"}
])
```

Sonuç: Her iki task da `deepseek` (ana model) kullandı. Per-task override çalışmıyor.

## Kanban Workers: Per-task model override VAR

v0.15.0 sürüm notu: "Per-task model overrides"
Git commit: `f01ee0b57 feat: per-task model override for kanban workers`

## PR #35033

`feat(delegate): per-task model/provider overrides` — GitHub'da merge edildi ama stable sürüme (v0.15.1) girmemiş. v0.15.2 veya sonrasında beklemede.

## Workaround (aktif çözüm)

`light_agent.py` ile direkt Pollinations API çağrısı + ThreadPoolExecutor paralelliği.

## hermes -z sorunu

`hermes -z "prompt" -m MODEL --provider pollinations --yolo` → exit 0 ama boş stdout. `hermes chat` çalışıyor ama `-z` oneshot modu güvenilmez.
