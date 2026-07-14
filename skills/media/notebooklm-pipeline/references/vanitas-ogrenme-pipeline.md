# Vanitas Öğrenme Pipeline'ı

## Sorun

Cron job'lar (Gmail, APA, Skool) bilgi topluyor, Telegram topic'lerine ve NotebookLM'e gönderiyor — ama Vanitas bu bilgileri otomatik olarak "öğrenmiyor". Bilgiler boru hattından geçip arşivleniyor, Vanitas sadece Edel sorunca `session_search` veya `cross_notebook_query` ile bakıyor.

## Çözüm Mimarisi

```
Gmail/APA/Skool cron job'ları (MEVCUT, değişiklik yok)
              ↓
      Çıktılar Telegram topic'lerine (MEVCUT)
              ↓
   🆕 Günlük Sentez Cron'u (her gece 23:00)
              ↓
   ┌──────────┼──────────┐
   ▼          ▼           ▼
 Özet       Memory      NotebookLM
(ucuz      kaydı       Hafıza Arşivi
 model)                 (text source)
              ↓
   Sabah selamına entegrasyon
   (morning_greeting memory'deki
    "dünün önemli bulguları"nı kontrol eder)
```

## Adımlar

### 1. Günlük Sentez Cron Job'u (yeni)
- Saat: Her gece 23:00
- Model: `deepseek-flash` (V4 Pro'dan ~8x ucuz)
- EKİP: Analist (Zen, ücretsiz) + Yazar (GPT-5.4-mini)
- Ne yapar: Son 24 saatteki Gmail/APA/Skool çıktılarını `session_search` ile toplar, EKİP'e özetletir

### 2. Memory'ye Kayıt
- Önemli bulguları `memory` aracına yazar
- Sınır: 400 karakter (memory %92 dolu)
- Eski/önemsiz memory'leri temizleyerek yer açar

### 3. NotebookLM Arşivi
- Özeti `🧠 Vanitas Hafıza Arşivi` notebook'una text source olarak ekler

### 4. Sabah Selamına Entegrasyon
- `morning_greeting` cron'u memory'deki "dünün önemli bulguları"nı kontrol eder
- Sohbete doğal şekilde yedirir (rapor formatında DEĞİL)

## Maliyet

| İşlem | Model | Günlük |
|-------|-------|--------|
| Günlük Sentez | Flash + Zen(free) | ~$0.001 |
| **TOPLAM aylık** | | **~$0.03** |

## Kaynaklar

- APA Bilgi notebook: c44469fe-a69a-4a86-8dd8-756c2f365109 (20 source)
- Vanitas Hafıza Arşivi: 6c7f3daa-1640-4fad-9917-ec44bc432e58 (10 source)
- İlgili cron job'lar: d4e5348f059f (APA), f4ea19bb906a (Gmail), 50002951d6bc (Skool)

## Durum

4 Haziran 2026: Plan onaylandı, henüz kurulmadı. Edel gelişim planını istedi, mimari çizildi.
