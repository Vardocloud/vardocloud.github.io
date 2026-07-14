---
name: notification-routing
description: Hermes platform notification routing — cron job delivery vs gateway system notifications. Diagnosis and fix for messages appearing in wrong channels.
tags: [notifications, routing, delivery, cron, gateway, telegram, diagnosis]
---

# Notification Routing — Hermes Mesaj Yönlendirme

Hermes'te mesajlar iki bağımsız sistem tarafından gönderilir. Bir mesaj yanlış yerde göründüğünde, önce hangi sistemin gönderdiğini belirlemek gerekir.

## İki Sistem

### 1. Cron Job (Zamanlanmış Görev)
- **Ne gönderir:** LLM çıktısı (doğal dil, sohbet tonu)
- **Yapılandırma:** `cronjob` tool'u ile her job'ın `deliver` alanı
- **Hedef:** Job bazlı — her job farklı kanala gidebilir
- **İçerik:** LLM tarafından üretilir, genelde emoji/kişisel ton içerir
- **Listelenebilir:** Evet — `cronjob(action='list')` ile tüm job'lar görünür
- **Log:** Cron scheduler delivery log'u

### 2. Gateway Sistem Bildirimi
- **Ne gönderir:** Health alert, hata raporu, sistem uyarısı
- **Yapılandırma:** Tek bir ortam değişkeni
- **Hedef:** Tüm bildirimler aynı hedefe gider
- **İçerik:** Genelde prefix: "Health Alert", uyarı emojileri
- **Listelenebilir:** Hayır — cron listesinde görünmez
- **Log:** Gateway servis log'u

## Teşhis: Mesaj Nereden Geldi?

1. **İçeriğe bak:** "Health Alert" / "DOWN" / "🚨" başlıklı → gateway bildirimi
2. **Cron listesini kontrol et:** Prompt içeriği eşleşiyor mu?
3. **Dil tonu:** Doğal/kişisel/sohbet → cron job. Düz/metin/formatlı → no_agent cron veya gateway
4. **Zamanlama:** Schedule'a uyuyor mu? Gateway anlık tetiklenir.

## Ne Zaman Ne Yapmalı

| Durum | Hangisi? | Çözüm |
|:------|:---------|:-------|
| Cron job yanlış topic'te görünüyor | Cron | `deliver` alanını düzelt, veya `send_message` bypass kullan |
| Sistem uyarısı DM'de görünüyor, kanalda olmalı | Gateway | HOME_CHANNEL ayarını değiştir |
| Mesaj cron listesinde yok ama geliyor | Gateway | Cron değil, gateway ayarına bak |
| Mesaj cron listesinde var ama farklı yerde | Cron | `deliver` ve `origin.thread_id` uyumunu kontrol et |

## Classification Örnekleri

| Gerçek Mesaj | Kaynak | Sebep |
|:-------------|:-------|:------|
| "Günaydın Edel! Bugün nasılsın?" + takvim bilgisi | Cron (morning_greeting) | Doğal dil, kişisel ton, emoji |
| "Hermes Health Alert — Open WebUI DOWN" | Gateway | "Health Alert" prefix, sistem dili |
| "📊 Gunluk Durum — Root /: X bos (Y%)" | Cron no_agent (DailyStatus) | Script çıktısı formatı, cron listesinde var |
| "🌙 Rüya tamamlandı" | Cron no_agent (Vanitas Rüya) | Script çıktısı, cron listesinde var |

## İlgili Skill'ler

- `hermes-cron-troubleshooting` — Cron job teslimat sorunları (yanlış topic, thread fallback, truncation)
- `server-maintenance` — Sunucu sağlığı, watchdog, sistem monitörü
