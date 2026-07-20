---
name: transkript-raporlama
description: >-
  Raw Whisper/Groq transcript → yapılandırılmış seminer/webinar raporu.
  Audio→text aşaması bittikten sonraki POST-PROCESSING adımını kapsar:
  dosya envanteri, temizlik, başlıklandırma, format uygulama, rapor yazma.
version: 1.0.0
metadata:
  hermes:
    tags: [transcript, report, seminar, webinar, formatting, post-processing]
    category: productivity
---

# Transkript Raporlama — Post-Processing Workflow

## Ne Zaman Kullanılır

- Ham Whisper/Groq çıktısı (`.md` içinde tek uzun satır) yapılandırılmış rapora dönüştürülecekse
- Edel "şu transkripti işle / raporla / formata sok" dediğinde
- Birden çok transkript toplu işlenecekse (delegate_task ile parallel)

## Önce Envanter Çıkar

```bash
# Tüm transkript dosyalarını bul
find ~/recordings -name "*.md" -type f -ls
# Sadece ham transkriptleri ayırt et (işlenmiş raporlar genelde -report.md ile biter)
find ~/recordings -name "*.md" ! -name "*-report.md" ! -name "rapor_*" -type f
# Ses dosyalarını kontrol et (transkript edilmemiş olanlar)
find ~/recordings -name "*.mp3" -o -name "*.mp4" -o -name "*.m4a" | sort
```

**Ham transkript belirtileri:**
- Head: `# Başlık` + `**Tarih:**` + `**Chunk Sayısı:**` + `---` + tek uzun metin satırı
- Alt: `*Transkript Groq Whisper (whisper-large-v3) ile oluşturulmuştur.*`
- Boyut: 5-50KB arası, tek satırda tüm içerik

**İşlenmiş rapor belirtileri:**
- Head: `# 📘 ...` formatında emoji başlık
- Yapı: `## 1. ...` numaralı bölümler + `## 🔑 Anahtar Noktalar` + `## 💡 ... Çıkarımlar`
- Dosya adı: `*-report.md`

## Post-Processing Workflow

### 1. Formatı Belirle (şablon)

```
# 📘 [Etkinlik Adı]

**📅 Tarih:** [GG AAYYYY YYYY]
**⏱ Süre:** ~[XX dakika]
**👤 Konuşmacı(lar):** [İsimler]

---

## 1. [Ana Konu Başlığı]
[Temiz, akıcı metin — dolgu kelimeleri ayıklanmış, önemli terimler **kalın**]

## 2. [Ana Konu Başlığı]
[...]

---

## 🔑 Anahtar Noktalar
- [madde madde]

## 💡 [Klinik/Kariyer] Çıkarımlar
- [uygulama önerileri]

## 📚 Öğrenilmesi Gerekenler
- [temel çıkarımlar]

---

*Rapor [tarih] tarihinde oluşturulmuştur.*
```

### 2. Temizlik Kuralları (evrensel-transkript-donusturucu.md)

Prompt dosyası: `~/.hermes/prompts/evrensel-transkript-donusturucu.md`

- **KALDIR:** dolgu kelimeleri (ee, yani, şey, hani, işte, aslında), hitaplar, teknik arıza diyalogları, meta-konuşmalar, tekrarlayan cümleler
- **KORU:** konuşmacının anlatım tarzı, mizah, anekdotlar
- **SIRAYA SADIK KAL:** konuları yeniden kategorize etme, sırayı değiştirme
- **PROSE FORMATI:** düz yazı paragraflar; madde işareti sadece konuşmacının saydığı öğeler için
- **KALIN:** önemli kavramlar ve ilk kez tanımlanan terimler
- **ALINTI:** doğrudan aktarımlar `>` blok alıntı
- **EKSİK KISIMLAR:** uydurma. `[Ses bozuk - bağlamdan tahmin]` veya `[Ses anlaşılmıyor]` notu bırak

### 3. Parallel İşleme

5-10 dk sürecek transkriptleri `delegate_task` ile parallel işle:

```python
# Her bir transkript için ayrı subagent
# Context içinde: format şablonu, temizlik kuralları, çıktı yolu
```

### 4. Doğrulama

- [ ] Çıktı dosyası oluştu mu? (`-report.md`)
- [ ] Format şablona uygun mu? (emoji başlık, metadata, bölümler)
- [ ] Ham transkriptteki tüm ana konular raporda var mı?
- [ ] Dolgu/tekrar temizliği yapılmış mı?

## Pitfalls & Dikkat Edilecekler

### 🔴 Dosya Kopyalama/Kesme Bozulması
`transkript_yt.md` → `2026-07-10-xxx.md` gibi yeniden adlandırmalarda dosya TRUNCATE olabilir.
**Çözüm:** Her rename/copy sonrası `wc -c <dosya>` ile kaynak ve hedef boyutunu karşılaştır.
**Yedek:** Orijinal `transkript_*.md` dosyaları silinmeden önce bir süre saklanmalı.

### 🔴 Whisper Çift Dil Bozulması
İngilizce+Türkçe karışık içerikte Whisper anlamsız çıktı üretebilir.
**Çözüm:** Raporu oluştururken çok bozuk bölümleri `[Transkripsiyon bozuk]` ile işaretle. Alternatif transkripsiyon motoru (Deepgram, AssemblyAI) düşünülebilir.

### 🔴 Subagent Dosya Etkileşimi
Birden çok subagent aynı anda çalışırken aynı dosyalara yazma/yazma riski var.
**Çözüm:** Her subagent'a ayrı çıktı dosyası ver. Girdi dosyalarını read-only kullan.

### 🔴 Büyük Dosyalar
> 50KB transkriptlerde read_file limit aşılabilir. `cat` veya `head -c` kullan.
Tek satırlık dev transkriptlerde `read_file` bazen sadece ilk N karakteri döndürür — `wc -c` ile gerçek boyutu kontrol et.

## Referans Dosyaları

- `references/seminer-rapor-formati.md` — Kullanılacak rapor şablonu detaylı açıklaması
- Prompt: `~/.hermes/prompts/evrensel-transkript-donusturucu.md`
