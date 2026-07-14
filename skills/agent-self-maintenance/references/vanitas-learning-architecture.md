# Vanitas Öğrenme Mimarisi: Fine-Tune Olmadan Öğrenme

**Date:** 17 Haz 2026
**Context:** Edel sordu: "Vanitas fine-tune edilmeden nasıl öğrenebilir?"

## Temel İçgörü

**Model aynı kalır, context değişir.** Yapay sinir ağırlıklarına dokunmadan, Vanitas'ın her seansta gördüğü bilgi zenginleşir. Literatürdeki karşılığı: **in-context learning + persistent memory (RAG)**.

---

## Mevcut Mekanizmalar (Hermes'te Aktif)

| Mekanizma | Depolama | Erişim | Ne Yapar |
|-----------|----------|--------|----------|
| **MEMORY.md** | ~/.hermes/memories/ | Her oturum başı context injection | Uzun süreli hafıza — kritik gerçekler |
| **USER.md** | ~/.hermes/memories/ | Her oturum başı context injection | Kullanıcı profili, tercihler, yasaklar |
| **Session Search** | SQLite FTS5 | session_search aracı | Geçmiş konuşmaları anlamsal arama |
| **Wiki (~/wiki/)** | Markdown dosyaları | grep / llm-wiki skill | Yapılandırılmış bilgi tabanı |
| **Skills** | ~/.hermes/skills/ | skill_view ile yükleme | Tekrar eden iş akışları |
| **Memory Index** | memory_index.json | grep ile hızlı erişim | Sesli asistan için hafif context |

---

## Teoride Eklenebilecekler

| Mekanizma | Fayda | Uygulama |
|-----------|-------|----------|
| **Oturum Özetleme → Memory** | Her konuşma sonu otomatik özet, MEMORY.md güncellemesi | LLM tabanlı extraction pipeline |
| **Pattern Hunter** | Oturumlar arası tekrar eden desenleri yakalama | Skill olarak mevcut (`pattern-hunter`) |
| **Duygu Durumu Takibi** | Konuşma tonundan ruh hali çıkarımı | Sentiment analysis + zaman serisi |
| **Bilgi Boşluğu Tespiti** | Wiki'de `[?]` işaretli bilinmeyenleri proaktif sorma | Wiki taraması |
| **İlişki Derinlik Skoru** | Kaç seansta konuşulduğu, hangi konular tekrar ettiği | Session count + topic clustering |
| **Gradual Prompt Zenginleştirme** | Edel düzelttikçe SOUL.md/SOUL_CORE otomatik güncelleme | Feedback loop |

---

## Memory Dolması → Wiki'ye Taşma

Memory sınırlı (~2200 char). Dolduğunda:

```
Az kullanılan bilgi → Wiki'ye taşı
Sadece aktif/önemli bilgi → Memory'de kal
Eski bilgiler → Compression ile özetle
```

Memory = sıcak önbellek. Wiki = soğuk depolama (sınırsız).

### 4-Çözüm Çerçevesi (17 Haz 2026)

Edel'in "oturum özetleme yapalım ama memory dolarsa naparız?" sorusuna pratik çerçeve:

| # | Çözüm | Mekanizma |
|---|-------|-----------|
| 1 | **Compact** | Eski/önemsiz anıları temizle, sadece kritik olanları tut |
| 2 | **Wiki'ye taşı** | Detaylı bilgiler `~/wiki/`'e, memory'de sadece pointer (`Skill: X`) |
| 3 | **Oturum özetleme** | Her konuşma sonunda 1-2 cümle özet → memory; ham transkript değil |
| 4 | **Treshold tetikleyici** | %90 dolulukta otomatik compact; proaktif, reaktif değil |

**Kritik içgörü:** Oturum özetleme memory'yi şişirmez — aksine düzenler. Her şeyi değil, sadece "bu seansta ne öğrenildi"yi kaydeder. Ham log'lar context-mode FTS5'te kalır, memory sadece pointer tutar.

---

## Fine-Tune vs RAG Karşılaştırması

| | Fine-Tune | RAG (bizim yaklaşım) |
|---|---|---|
| Maliyet | Yüksek (GPU saat) | Düşük (depolama) |
| Güncelleme | Her değişiklikte yeniden eğitim | Anında (dosyaya yaz) |
| Bilgi tazeliği | Eğitim tarihiyle sınırlı | Her zaman güncel |
| Halüsinasyon | Azalır ama yok olmaz | Kaynak gösterilebilir |
| Özelleştirme | Model davranışı değişir | Bilgi eklenir, davranış aynı |
