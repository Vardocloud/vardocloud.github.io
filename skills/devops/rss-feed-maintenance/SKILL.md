---
name: rss-feed-maintenance
category: devops
description: RSS feed bundle management for news-driven trading signals — blogwatcher-cli setup, refresh cadence, staleness detection, and fallback strategies.
tags: [rss, feeds, blogwatcher, news-signals, data-pipeline]
related_skills: [polymarket-ai-trading-system]
---

# RSS Feed Maintenance for Trading Signals

## Amaç
Haber-driven trading stratejileri için RSS feed'lerini canlı tutmak. Feed'ler düzenli taranmazsa kurur, haber akışı sıfırlanır ve sinyal üretilemez.

## Araç: blogwatcher-cli

### Kurulum (ARM64)
```bash
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_arm64.tar.gz -o /tmp/bw.tar.gz
tar xzf /tmp/bw.tar.gz -C /tmp blogwatcher-cli
sudo mv /tmp/blogwatcher-cli /usr/local/bin/
```

### Komut Referansı

| Amaç | Komut |
|------|-------|
| Feed'leri listele | `blogwatcher-cli blogs` |
| Yeni makaleleri çek | `blogwatcher-cli scan` |
| Makaleleri listele | `blogwatcher-cli articles` |
| Feed ekle | `blogwatcher-cli add "Name" "https://example.com" --feed-url "https://example.com/rss"` |
| Feed sil | `echo "y" \| blogwatcher-cli remove "Name"` |
| Özel DB yolu | `blogwatcher-cli --db /path/to/db.db scan` |

### Refresh Cadencesi

| Frekans | Ne Zaman | Amaç |
|---------|----------|------|
| Her scan öncesi | Master scan'dan hemen önce | Haberleri tazele, signal doğruluğu |
| Günde 1x | Sabah 09:00 UTC+3 | Günlük haber birikimini topla |
| Haftada 1x | Pazartesi 10:00 | Haftasonu biriken haberleri al |

### Feed Staleness Tespiti

Feed'lerin son taranma tarihini kontrol et:

```bash
# Son 5 makalenin tarihini göster
blogwatcher-cli articles --limit 5
# Çıktıda published_date en son ne zaman?
# 48 saatten eskiyse → STALE
```

**Belirtiler:**
- `articles_count = 0` scan çıktısında
- Son tarama tarihi > 48 saat önce
- Haber-driven stratejilerde sinyal üretilememesi

### Gerçek Hayat Örneği (1 Tem 2026)
14 RSS kaynağı 27 Haziran'da taranmış, 1 Temmuz'da hâlâ 0 makale dönüyordu. 4 günlük boşluk — `blogwatcher-cli scan` çalıştırılmadığı için feed'ler güncellenmemişti. Ders: **Scan öncesinde feed refresh otomatikleştirilmezse haber akışı sessizce ölür.**

### Kullanım Sırası
1. Feed'leri tazele: `blogwatcher-cli scan`
2. Makaleleri kontrol et: `blogwatcher-cli articles --limit 10`
3. Haber akışı varsa → trading stratejisine besle
4. Haber akışı yoksa → SearXNG veya Serper fallback

### Tips
- 14+ feed aboneliği olan bir sistemde scan ~5-10sn sürer
- `--db` flag'i ile farklı projeler için ayrı DB'ler tutulabilir
- Cronjob'da scan+analiz aynı anda yapılabilir (scan önce gelmeli)
- Master scan JSON çıktı şeması için: `references/polymarket-master-scan-schema.md`
