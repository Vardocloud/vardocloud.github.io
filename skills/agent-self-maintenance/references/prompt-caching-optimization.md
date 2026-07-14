# DeepSeek Prompt Caching — Davranış ve Optimizasyon (10 Tem 2026)

## Özet

DeepSeek prompt caching **çalışır** ama prompt'un **byte 0'dan itibaren birebir aynı** olmasını gerektirir. Başta 1 dakikalık timestamp farkı bile cache hit oranını %71'den %0'a düşürür.

## Nasıl Çalışır

- **Prefix matching:** Prompt'u byte 0'dan başlayarak cache'ler. Prefix'teki herhangi bir değişiklik sonrasındaki HER ŞEYİ invalidate eder.
- **Fiyatlandırma:** Cache hit = $0.014/M token, Cache miss = $0.14/M token (%90 indirim).
- **Minimum:** 64+ token blokları cache'e girer.
- **Otomatik:** Özel header gerekmez — DeepSeek sunucu tarafında yönetir.
- **İzleme:** API yanıtında `prompt_cache_hit_tokens` ve `prompt_cache_miss_tokens` alanları.

## Kritik Bulgu (10 Tem 2026)

```
Test 1: system prompt (timestamp YOK)     → cache_hit: %71 ✅
Test 2: "Conversation started: 14:30" +   → cache_hit: %0  ❌
Test 3: "Conversation started: 14:31" +   → cache_hit: %0  ❌
```

**Kök neden:** DeepSeek byte 0'dan itibaren tam eşleşme ister. Pozisyon 0'da timestamp varsa, her mesajda cache kırılır.

## Optimizasyon Stratejisi

### 1. Stabil Önce, Değişken Sonra

Prompt'taki içerik sıralaması: sabit bilgiler ([CONFIRMED], altyapı, kalıcı kurallar) **başta**, değişken bilgiler ([ERROR] günlükleri, tarihli notlar) **sonda** olmalı.

```
✅ İYİ:
[CONFIRMED] Gmail API (3Tem): token path, scopes, keepalive
API key sırası: BWS→BW→.env
[ERROR] LinkedIn (6Tem): kuyruk limiti düzeltmesi  ← SONDA

❌ KÖTÜ:
Bugünün işleri: mail kontrol, wiki güncelle      ← DEĞİŞKEN BAŞTA
[CONFIRMED] Gmail API...                         ← sabit ama sonra
```

### 2. System Prompt Başlangıcı Sabit Kalmalı

System prompt'un ilk satırı her zaman aynı olmalı. Başa asla timestamp, session ID, veya dinamik içerik EKLENMEMELİ.

### 3. İdeal Prompt Yapısı

```
[SABİT KATMAN — asla değişmez]
  Sistem dokümanları (COMPASS, PERSONA)

[YARI-SABİT KATMAN — nadiren değişir]
  Skill'ler (aynı skill'ler = aynı içerik)
  Kullanıcı profili

[DEĞİŞKEN KATMAN — sık değişir]
  Kısa süreli hafıza (stabil önce, değişken sonra)
  Konuşma geçmişi (her turda büyür)

[ANLIK KATMAN — asla cache'lenmez]
  Güncel kullanıcı mesajı
```

### 4. Cache Kıran Unsurlar (Bunları Prompt Başından Uzak Tut)

- Byte 0'da `Conversation started: <timestamp>`
- Pozisyon 0'da session ID, request ID, UUID
- Her gün değişen günlük notlar (bunları sona taşı)
- Dinamik model adı veya provider bilgisi

## Test Metodolojisi

OpenAI-compatible proxy endpoint'ine iki istek atarak test edilir:

```python
# İstek 1 — cache miss
payload = {"model": "...", "messages": [
    {"role": "system", "content": "Sabit sistem prompt'u..."},
    {"role": "user", "content": "Soru 1"}
]}

# İstek 2 — cache hit (aynı system prompt, farklı user mesajı)
payload2 = {"model": "...", "messages": [
    {"role": "system", "content": "Sabit sistem prompt'u..."},
    {"role": "user", "content": "Soru 2"}
]}

# Yanıtta usage.prompt_cache_hit_tokens > 0 ise cache çalışıyor
```

## Maliyet Etkisi (V4 Pro)

| Senaryo | Cache Hit | Tur Başına | Aylık (50 msg/gün) |
|---------|-----------|------------|---------------------|
| Cache yok (timestamp başta) | %0 | $0.00112 | $1.68 |
| Kısmi (MEMORY optimize) | %40 | $0.00078 | $1.17 |
| Tam (stabil prefix) | %70 | $0.00047 | $0.70 |

## İlgili Konfigürasyon

- `prompt_caching.cache_ttl`: 5 dakika
- `response_cache`: aktif
- `response_cache_ttl`: 300 saniye
- Provider proxy cache davranışı: kendi TTL'si ile çalışır, DeepSeek caching'den bağımsız

## Kaynaklar

- DeepSeek API prompt caching dokümantasyonu: https://api-docs.deepseek.com/guides/prompt_caching
- Config ayarları: `prompt_caching` bloğu altında `cache_ttl`, `response_cache`, `response_cache_ttl`
