# Dinamik Model Yönlendirme (Dynamic Brain)

5 Haz 2026 — Edel'in talebi: basit sohbet için ucuz model, karmaşık işler için pro model. "Dinamik beyin".

## Mevcut Durum

Vanitas (ana ajan) HER görev için DeepSeek V4 Pro kullanıyor. Basit "günaydın" da, karmaşık araştırma da aynı pahalı modelden geçiyor.

## Hermes'te Zaten Var Olan Altyapı

### 1. `/model` Komutu (Runtime Switching)

Gateway'de `/model <alias>` ile anlık model değiştirme:

```
/model hizli    → ucuz modele geç
/model derin    → pro modele geç
/model mini     → hafif modele geç
```

### 2. model_aliases Konfigürasyonu

```yaml
model_aliases:
  hizli:
    model: gpt-5.4-mini     # EKLENDİ (5 Haz — önceden eksikti)
    provider: pollinations
  derin:
    model: deepseek-v4-pro
    provider: deepseek
  mini:
    model: gpt-5.4-mini
    provider: pollinations
```

Değişiklik: `hermes config set model_aliases.hizli.model gpt-5.4-mini`

### 3. Delegation Routing

Alt ajanlar (delegate_task) ana modelden bağımsız çalışabilir:

```yaml
delegation:
  model: gpt-5.4-mini
  provider: pollinations
```

### 4. Auxiliary Routing

Arka plan işleri (vision, web_extract, compression) ayrı modellerde:

```yaml
auxiliary:
  vision.provider: pollinations
  web_extract.provider: pollinations
```

## Henüz YOK: Otomatik Akıllı Routing

Hermes'te görev karmaşıklığına göre OTOMATİK model seçimi yok. Çözüm seçenekleri:

### Seçenek A: Manuel (çalışıyor)
Edel `/model hizli` veya `/model derin` yazarak elle geçiş yapar.

### Seçenek B: Akıllı Proxy (inşa edilebilir)
Gateway önüne mesaj analizi yapan bir proxy:
- "nasılsın", "günaydın", "teşekkürler" → hizli
- "araştır", "yap", "kur", "temizle" → derin

### Seçenek C: Çift Profil
İki Hermes profili, farklı modellerle.

## Model Maliyet Karşılaştırması

| Model | Kullanım Alanı | Maliyet |
|-------|---------------|--------|
| gpt-5.4-mini (pollinations) | Sohbet, özet, basit sorular | ~$0 |
| deepseek-v4-pro | Araştırma, kod, sistem yönetimi | Ücretli |
| gemma-4-26b (pollinations) | Çok hafif görevler | ~$0 |
| minimax-m2.7 (opencode) | Kod, analiz | ~$0 |

## EKİP Model Atamaları

| Ajan | Model | Kullanım |
|------|-------|----------|
| Analist | mimo-v2.5-free (Zen) | Web araştırma |
| Kodcu | minimax-m2.7 (OpenCode Go) | Kod |
| Yazar | gpt-5.4-mini (Pollinations) | Türkçe metin |
| Yardımcı | gemma-4-26b (Pollinations) | Basit görevler |
