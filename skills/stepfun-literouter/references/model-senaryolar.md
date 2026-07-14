# LiteRouter Free Modelleri — Kullanım Senaryoları Analizi

> Analiz: Vanitas | Kaynak: OpenRouter, HuggingFace, resmi dökümanlar
> Tarih: 20 Haziran 2026

---

## 🏆 DEEPSEEK-V3.2:FREE — Çok Yönlü Ağır Siklet

**Boyut:** ~685B MoE | **Context:** 128K | **JSON:** ✅ Resmi | **Türkçe:** ⭐⭐⭐⭐

### Nerelerde Kullanılır?
| Senaryo | Görev Türü | Neden Bu Model? |
|---|---|---|
| **Sohbet kalitesi değerlendirme** (Vanitas stepfun) | Analitik + JSON | Non-thinking'de content dolu, JSON mode resmi destek |
| **Makale/rapor özetleme** | Uzun metin işleme | 128K context, GPT-5 seviyesi muhakeme |
| **Akademik kaynak sentezleme** | Araştırma | Derin reasoning, çoklu kaynak karşılaştırma |
| **Prompt mühendisliği/iyileştirme** | Analitik | "Thinking in Tool-Use" ile adım adım düşünme |
| **LinkedIn/akademik içerik yazımı** | Yaratıcı + Yapısal | Uzun form içerikte dengeli |

### Örnek: Psikoloji Makale Özeti
> "Şu makaleyi oku ve 5 maddede özetle: [link]. Akademik bir dille, APA referansla."
> → DeepSeek'in reasoning'i derinlemesine analiz yapar, non-thinking'de temiz çıktı verir.

---

## 🚀 GROK-4.1-FAST-REASONING:FREE — Hızlı Ajan

**Boyut:** ? (xAI) | **Context:** 2M | **JSON:** ✅ Structured Outputs | **Türkçe:** ❓

### Nerelerde Kullanılır?
| Senaryo | Görev Türü | Neden Bu Model? |
|---|---|---|
| **Uzun doküman analizi** | Uzun context | 2M token — kitap boyutunda metin işleme |
| **Çok adımlı ajan görevleri** | Agentic | Grok 4.1 "agentic tool calling"de #1 |
| **Müşteri desteği otomasyonu** | Diyalog | Duygusal zeka + hızlı yanıt |
| **Büyük kod tabanında hata ayıklama** | Teknik | Tüm projeyi contexte sığdırır |
| **Veri analizi + raporlama** | Analitik | Tool calling ile veri çekip yorumlama |

### Örnek: Repository Dokümantasyonu
> "Şu repo'nun tüm kodunu tara, mimariyi çıkar ve README yaz."
> → 2M context ile tüm repoyu tek seferde işler, tool calling ile dosyaları tarar.

---

## 🌍 GEMMA-3-27B-IT:FREE — Çok Dilli Güç

**Boyut:** 27B | **Context:** 131K | **JSON:** ✅ Structured Outputs | **Türkçe:** ✅ 140+ dil

### Nerelerde Kullanılır?
| Senaryo | Görev Türü | Neden Bu Model? |
|---|---|---|
| **Çeviri + transkripsiyon** | Multilingual | 140+ dil, Google altyapısı |
| **Çok dilli içerik üretimi** | Yaratıcı | Her dilde doğal metin |
| **Görsel + metin analizi** | Multimodal | Vision-language input |
| **Eğitim materyali hazırlama** | Eğitim | 140 dilde ders notu, quiz |
| **Kültürlerarası iletişim** | Adaptasyon | Google'ın geniş dil modellemesi |

### Örnek: Çok Dilli Blog
> "Bu İngilizce blog'u Türkçe, Almanca ve İspanyolca'ya çevir, kültürel farkları gözet."
> → 140 dil desteği ile en geniş kapsam.

---

## 🧠 GPT-OSS-120B:FREE — Muhakeme Devi

**Boyut:** 117B MoE (5.1B aktif) | **Context:** 131K | **JSON:** ✅ Native | **Türkçe:** ❓

### Nerelerde Kullanılır?
| Senaryo | Görev Türü | Neden Bu Model? |
|---|---|---|
| **Karmaşık mantık problemleri** | Reasoning | o4-mini seviyesi, configurable reasoning |
| **Structured data çıkarma** | JSON/API | En düşük structured output error rate |
| **Hukuk/mevzuat analizi** | Uzman metin | Derin muhakeme, uzun doküman |
| **Kod üretimi + code review** | Teknik | Tool calling + geniş context |
| **Finansal modelleme** | Analitik | Sayısal muhakeme, fonksiyon çağırma |

### Örnek: JSON Veri Dönüşümü
> "Bu PDF'deki tabloyu oku ve JSON array olarak çıkar: [schema]"
> → En düşük structured output error rate ile güvenilir.

---

## 🎭 MYTHOMAX-L2-13B:FREE — Hikaye Anlatıcısı

**Boyut:** 13B | **Context:** 4K | **Türkçe:** ❌ İngilizce | **Özel:** Roleplay #1

### Nerelerde Kullanılır?
| Senaryo | Görev Türü | Neden Bu Model? |
|---|---|---|
| **İnteraktif hikaye yazımı** | Yaratıcı | En iyi roleplay modellerinden |
| **Karakter diyaloğu yazma** | Yaratıcı | Tutarlı persona, zengin betimleme |
| **Oyun senaryosu** | Tasarım | NPC diyalogları, quest metinleri |
| **Kurgusal içerik** | Yaratıcı | Roman bölümü, kısa hikaye |
| **Rol yapma oyunları** | Eğlence | Kişilik taklidi, doğaçlama |

### Örnek: Oyun NPC Diyaloğu
> "Bir Orta Çağ han sahibesi NPC'si yaz. Müşterilere nasıl davranır?"
> → MythoMax'in doğal betimleme ve karakter tutarlılığı.

---

## 🎪 L3-8B-LUNARIS:FREE — Yaratıcı Generalist

**Boyut:** 8B | **Context:** 8K | **Türkçe:** ❌ İngilizce | **Özel:** Generalist + RP

### Nerelerde Kullanılır?
| Senaryo | Görev Türü | Neden Bu Model? |
|---|---|---|
| **Yaratıcı yazarlık** | Yaratıcı | Mantık + yaratıcılık dengesi |
| **Chatbot kişiliği tasarlama** | Tasarım | Birden çok modelin merge'i |
| **Sosyal medya içeriği** | Yaratıcı | Kısa, etkili, yaratıcı metinler |
| **Beyin fırtınası** | Yaratıcı | Fikir üretme, alternatif senaryolar |
| **Hikaye taslağı** | Planlama | Yapı + yaratıcılık bir arada |

### Örnek: Instagram Post Serisi
> "Bir psikoloji hesabı için 7 günlük post serisi yaz: bağlanma stilleri üzerine."
> → Lunaris'in generalist yapısı hem bilgiyi hem yaratıcılığı birleştirir.

---

## 🦉 OWL-ALPHA:FREE:FULL-CONTEXT — Kesintisiz Ajan

**Boyut:** ? | **Context:** 1M | **JSON:** ✅ Structured Output (%0.34 hata) | **Özel:** Agentic

### Nerelerde Kullanılır?
| Senaryo | Görev Türü | Neden Bu Model? |
|---|---|---|
| **Uzun süreli ajan görevleri** | Agentic | 1M context ile oturum boyunca bağlam koruma |
| **Full-context kod projesi** | Teknik | Tüm projeyi contexte tutup işlem |
| **Büyük veri seti analizi** | Veri | Uzun log/CSV dosyalarını bağlamda işleme |
| **Claude Code/OpenClaw entegrasyonu** | Araç | Claude Code ile uyumlu |
| **Belge tarama + sorgulama** | Araştırma | Kitap boyutunda belgeyi contextte tutar |

### Örnek: Tüm Projeyi Refactor
> "Şu 500 dosyalık projeyi analiz et, mimariyi çıkar, refactor öner."
> → 1M context ile her şeyi tek seferde görür.

---

## 🔧 MISTRAL-SMALL-24B-2501:FREE — Hızlı İşçi

**Boyut:** 24B | **Context:** 32K | **Hız:** 150 t/s | **Türkçe:** ⭐⭐⭐⭐ 12+ dil

### Nerelerde Kullanılır?
| Senaryo | Görev Türü | Neden Bu Model? |
|---|---|---|
| **Gerçek zamanlı sohbet** | Sohbet | En hızlı modellerden (150 t/s) |
| **Hızlı içerik üretimi** | Üretim | Çok dilli, düşük gecikme |
| **API entegrasyonları** | Teknik | Hassas instruction following |
| **Günlük asistan görevleri** | Genel | Hızlı, verimli, yeterli kalite |
| **Not alma/özetleme** | Verimlilik | Anlık yanıt gereken işler |

### Örnek: Canlı Transkripsiyon Özeti
> "Bu 10 dk'lık toplantı kaydını özetle, aksiyon maddelerini çıkar."
> → 150 t/s ile neredeyse gerçek zamanlı.

---

## ✨ GERİ KALAN MODELLER — ÖZEL GÖREVLER

| Model | Uzmanlık | Örnek Senaryo |
|---|---|---|
| **gpt-oss-20b:free** (21B MoE) | Edge cihaz, düşük kaynak | "Bu modeli Raspberry Pi'de çalıştır, basit REST API yap" |
| **llama-3.1-8b-instruct-turbo:free** | Uncensored, hızlı | "Sansürsüz bir karakter sohbeti yaz" |
| **llama-3.1-8b-instruct:free** (Uncensored) | Genel, sansürsüz | "Hassas bir konuda tarafsız analiz yap" |
| **llama-3-8b-instruct:free** (Uncensored) | Llama 3 tabanı | "Eski bir modelle uyumlu olması gereken görev" |
| **devstral-small-2507:free** (Uncensored) | Agentic coding | "Karmaşık bir GitHub issue'sunu çöz, PR aç" |
| **llama-3.2-3b-instruct:free** | Çok küçük, hızlı | "Basit bir sınıflandırma modeli olarak kullan" |
| **ministral-3b-2512:free** | En küçük, vision | "Mobil cihazda görsel + metin işleme" |
| **trinity-mini:free** (26B MoE) | Function calling, ABD yapımı | "GDPR uyumlu, ABD merkezli bir AI servisi" |
| **mistral-nemo-2407:free** (12B) | Çok dilli, Nvidia destekli | "Nvidia GPU'da optimize çalışması gereken görev" |
| **openrouter:free:full-context** | 25 free model arasında routing | "Hangi modelin iyi olduğunu bilmiyorum, OpenRouter karar versin" |
| **llama-3.3-70b-instruct-turbo:free** | 70B, structured output %0 hata | "Hataya tahammülü olmayan JSON çıktısı gereken görev" |

---

## 🎯 STRATEJİK ÖNERİLER

### StepFun Değerlendirme İçin Sıralama
1. **deepseek-v3.2:free** — ✅ Çalışıyor, Türkçesi iyi, JSON mode var
2. **grok-4.1-fast-reasoning:free** — Test edilmeli, structured output var
3. **gemma-3-27b-it:free** — Test edilmeli, 140 dil + structured output

### Diğer Vanitas Görevleri İçin
- **LinkedIn post üretimi** → deepseek-v3.2 veya gemma-3-27b
- **YouTube içerik özeti** → gemma-3-27b (multilingual) veya owl-alpha (1M context)
- **Sohbet kalitesi iyileştirme** → deepseek-v3.2
- **Yaratıcı içerik** → l3-8b-lunaris veya mythomax
- **Hızlı cevap gereken** → mistral-small-24b (150 t/s)
- **Büyük doküman** → grok-4.1-fast (2M) veya owl-alpha (1M)

### Hangi Model Ne Zaman Kullanılır? (Karar Ağacı)
```
Görev JSON çıktısı gerektiriyor mu?
  ├─ Evet → GPT-OSS-120B (en düşük hata) veya deepseek-v3.2 (Türkçe)
  │
  └─ Hayır → Ne kadar context gerek?
       ├─ >500K → Grok 4.1 Fast (2M) veya Owl Alpha (1M)
       ├─ >100K → DeepSeek V3.2 veya Gemma 3 27B
       │
       └─ <100K → Ne kadar hız gerek?
            ├─ Çok hızlı → Mistral Small 24B (150 t/s)
            ├─ Yaratıcı → L3 Lunaris veya MythoMax
            └─ Dengeli → DeepSeek V3.2
```
