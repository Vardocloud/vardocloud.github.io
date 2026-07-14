# LiteRouter Free Modelleri — Kullanım Senaryoları Analizi

> Analiz: Vanitas | Kaynak: OpenRouter, HuggingFace, resmi dökümanlar
> Tarih: 20 Haziran 2026

---

## 🏆 DEEPSEEK-V3.2:FREE — Çok Yönlü Ağır Siklet

**Context:** 128K | **JSON:** ✅ Resmi | **Türkçe:** ⭐⭐⭐⭐

| Senaryo | Görev Türü |
|---|---|
| Sohbet kalitesi değerlendirme | Analitik + JSON |
| Makale/rapor özetleme | Uzun metin işleme |
| Akademik kaynak sentezleme | Araştırma |
| LinkedIn/akademik içerik yazımı | Yaratıcı + Yapısal |

## 🚀 GROK-4.1-FAST-REASONING:FREE — Hızlı Ajan

**Context:** 2M | **JSON:** ✅ Structured Outputs

| Senaryo | Görev Türü |
|---|---|
| Uzun doküman analizi | 2M token — kitap boyutunda |
| Çok adımlı ajan görevleri | Agentic (#1) |
| Büyük kod tabanında hata ayıklama | Teknik |
| Veri analizi + raporlama | Analitik |

## 🌍 GEMMA-3-27B-IT:FREE — Çok Dilli Güç

**Context:** 131K | **JSON:** ✅ Structured Output | **Dil:** 140+

| Senaryo | Görev Türü |
|---|---|
| Çeviri + transkripsiyon | Multilingual |
| Çok dilli içerik üretimi | Yaratıcı |
| Görsel + metin analizi | Multimodal |

## 🧠 GPT-OSS-120B:FREE — Muhakeme Devi

**Context:** 131K | **JSON:** ✅ Native (en düşük hata)

| Senaryo |
|---|
| Karmaşık mantık problemleri |
| Structured data çıkarma |
| Finansal modelleme |

## 🎭 MYTHOMAX-L2-13B:FREE — Hikaye Anlatıcısı

**Context:** 4K | **Dil:** EN | **Özel:** Roleplay #1

| Senaryo |
|---|
| İnteraktif hikaye yazımı |
| Karakter diyaloğu |
| Oyun NPC senaryosu |

## 🦉 OWL-ALPHA:FREE:FULL-CONTEXT — Kesintisiz Ajan

**Context:** 1M | **JSON:** %0.34 hata

| Senaryo |
|---|
| Uzun süreli ajan görevleri |
| Full-context kod projesi |
| Claude Code/OpenClaw entegrasyonu |

## 🔧 MISTRAL-SMALL-24B-2501:FREE — Hızlı İşçi

**Context:** 32K | **Hız:** 150 t/s | **Dil:** 12+

| Senaryo |
|---|
| Gerçek zamanlı sohbet |
| Hızlı içerik üretimi |
| API entegrasyonları |

## ✨ DİĞER MODELLER

| Model | Uzmanlık | Örnek |
|---|---|---|
| `gpt-oss-20b:free` | Edge cihaz (16GB) | Raspberry Pi'de REST API |
| `devstral-small-2507:free` | Agentic coding (%53.6 SWE) | Karmaşık issue çözümü |
| `llama-3.3-70b-turbo:free` | Structured output %0 hata | Kritik JSON çıktısı |
| `trinity-mini:free` | 128 expert MoE, ABD yapımı | GDPR uyumlu servis |
| `ministral-3b-2512:free` | 3B, vision | Mobil görsel+metin |
| `l3-8b-lunaris:free` | Generalist + RP | Yaratıcı yazarlık |
| `openrouter:free:full-context` | 25 model routing | Hangisi iyi bilmiyorum |

## 🎯 KARAR AĞACI

```
Görev ne?
├─ JSON çıktısı şart mı?
│  ├─ Evet → GPT-OSS-120B (en güvenilir) / deepseek-v3.2 (Türkçe)
│  └─ Hayır → Context ne kadar?
│     ├─ >500K → Grok 4.1 (2M) / Owl Alpha (1M)
│     ├─ >100K → DeepSeek V3.2 / Gemma 3 27B
│     └─ <100K → Hızlı mı?
│        ├─ Evet → Mistral Small 24B (150 t/s)
│        ├─ Yaratıcı → L3 Lunaris / MythoMax
│        └─ Dengeli → DeepSeek V3.2
└─ Türkçe gerekli mi?
   ├─ Evet → deepseek-v3.2 veya gemma-3-27b
   └─ Hayır → İngilizce araç kutusu (en-arac-kutusu.md)
```
