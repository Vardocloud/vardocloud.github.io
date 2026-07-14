# LiteRouter Free Models — EN Araç Kutusu (Vanitas için)

> İngilizce görevlerde kullanılacak ücretsiz modeller.
> Tarih: 20 Haziran 2026

---

## 📦 KAPSAM

Bu modeller **Türkçe bilgisi kanıtlanmamış** veya **İngilizce odaklıdır**. 
Vanitas'ın İngilizce gerektiren işlerinde (kod, araştırma, data, yaratıcı yazarlık) kullanılır.

## ⚡ KOD & TEKNİK

### devstral-small-2507:free
- **Uzmanlık:** Agentic coding | SWE-Bench %53.6 (#1 open)
- **Uncensored:** ✅
- **Kullanım:** Karmaşık GitHub issue, PR, kod refactor

### gpt-oss-120b:free
- **Uzmanlık:** Reasoning + structured output (o4-mini eşdeğeri)
- **JSON hata:** En düşük
- **Kullanım:** Code review, algoritma analizi

### trinity-mini:free
- **Uzmanlık:** Function calling, multi-step agent
- **Context:** 131K, 128 expert MoE, ABD yapımı
- **Kullanım:** API zincirleri, GDPR uyumlu

## 🧠 ARAŞTIRMA & ANALİZ

### grok-4.1-fast-reasoning:free
- **Uzmanlık:** Uzun doküman, çok adımlı ajan
- **Context:** 2M token (en geniş)
- **Kullanım:** Kitap analizi, repo-wide refactor

### owl-alpha:free:full-context
- **Uzmanlık:** Full-context agentic
- **Context:** 1M token, JSON hata %0.34
- **Kullanım:** Claude Code entegrasyonu, büyük projeler

## 🎭 YARATICI

### mythomax-l2-13b:free
- **Uzmanlık:** Roleplay, storytelling (EN)
- **Kullanım:** NPC diyalogları, interaktif hikaye

### l3-8b-lunaris:free
- **Uzmanlık:** Generalist + RP dengesi
- **Kullanım:** Yaratıcı yazarlık, beyin fırtınası

## ⚡ HIZLI API

### mistral-small-24b-2501:free
- **Hız:** 150 t/s | **Dil:** 12+
- **Kullanım:** Gerçek zamanlı EN sohbet, API

### llama-3.3-70b-turbo:free
- **Context:** 131K | **JSON:** %0 hata
- **Kullanım:** Kritik doğruluk gereken EN görevler

## 🧩 KÜÇÜK

### ministral-3b-2512:free
- 3B, vision | **Kullanım:** Mobil, sınıflandırma

### llama-3.2-3b:free
- 3B, 131K context, 143 t/s | **Kullanım:** Hızlı etiketleme

## 🎯 KARAR AĞACI (EN)

```
Görev ne?
├─ Kod → devstral-small-2507
├─ Araştırma
│  ├─ >500K token → grok/owl-alpha
│  ├─ JSON kritik → gpt-oss-120b
│  └─ Hızlı özet → mistral-small-24b
├─ Yaratıcı yazarlık
│  ├─ Roleplay → mythomax
│  └─ Genel → lunaris
├─ API/tool → trinity-mini
└─ Sınıflandırma → llama-3.2-3b
```
