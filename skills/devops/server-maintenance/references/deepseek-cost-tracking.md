# DeepSeek V4 Pro Maliyet Takibi

## Fiyatlandırma

| | $/1M token |
|:-|:-|
| Input (cache miss) | $0.435 |
| Output | $0.87 |
| Reasoning tokens | Output ile aynı |

## Günlük maliyet sorgusu

```sql
-- Sadece sohbet oturumları (cron hariç)
SELECT source, COUNT(*) as sessions,
       SUM(input_tokens) as total_input,
       SUM(output_tokens) as total_output,
       SUM(reasoning_tokens) as total_reasoning,
       SUM(estimated_cost_usd) as total_est_cost
FROM sessions
WHERE started_at > unixepoch() - 86400
  AND model LIKE '%deepseek%'
  AND source != 'cron'
GROUP BY source;
```

## Manuel maliyet hesaplama

```python
cost = (input_tokens / 1_000_000 * 0.435) + (output_tokens / 1_000_000 * 0.87)
```

## Normal aralıklar

- **Hafif gün:** 1-2M input, $0.50-1.00
- **Normal gün:** 3-5M input, $1.50-2.50
- **Yoğun gün:** 5-10M input, $3-6
- **Aylık tahmin:** $30-70 (çoğunlukla normal/hafif)

## Thinking modu etkisi

`reasoning_effort: high` aktifse output token 2-3x artar.
Aylık maliyet $150+'a çıkabilir. Config'de kontrol: `hermes config model.reasoning_effort`
