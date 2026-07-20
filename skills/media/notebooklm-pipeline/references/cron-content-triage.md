# APA Pipeline — Content Quality Triage (14 Tem 2026)

5 kanal taraması bittiğinde, bulunan içeriğin türüne göre ne kadar işlem yapılacağını belirle.

## Triage Matrix

| İçerik Türü | Örnek | Pipeline Seviyesi |
|-------------|-------|-------------------|
| **🔬 Araştırma makalesi** | Monitor dergisi makalesi, Editor's Choice, Press Release (yeni çalışma) | **TAM**: wiki kaydı (İngilizce, yapılandırılmış) → NBLM source → podcast → rapor |
| **📊 By the Numbers / Data infographic** | Monitor'daki kısa veri sayfaları — 3-5 istatistik, uzun metin yok | **HAFİF+T**: wiki kısa kayıt → NBLM source (best-effort) → rapor. **Podcast atlanır** — 3 istatistikten 10 dk podcast anlamsız. |
| **🧠 Klinik rehber/CE** | Practice Update'teki derin rehber, CE Corner, klinik protokol | **TAM** (aynı) |
| **🎧 Podcast bölümü** | Yeni Speaking of Psychology | **ORTA**: NBLM source (text özet) → rapor, podcast oluşturma |
| **📋 Bülten roundup'ı (ikincil haber)** | Media Watch, Six Things (haber odaklı), Member Update | **HAFİF**: rapora kısa not ekle, wiki/NBLM/podcast yapma |
| **📅 Ücretsiz etkinlik** | Essential Science Conversations, ücretsiz webinar | **HAFİF**: rapora ekle, varsa `apa-etkinlikler/` dosyasına satır |
| **📰 Kısa bülten snippet** | "Psikologlar Haberlerde", IN BRIEF, "At APA" | **YOK** (atla, rapora bile ekleme) |
| **💰 Promosyon/üyelik** | CE Roundup, üyelik hatırlatma, reklam, "Refer a Colleague" | **YOK** (atla) |

## Pipeline Seviyeleri

### TAM Pipeline
```
wiki kaydı (İngilizce, yapılandırılmış ~/wiki/apa-articles/)
→ index.md güncelleme
→ NBLM source (best-effort, 1 deneme)
→ podcast (opsiyonel — sadece interaktif modda)
→ anlaşılır rapor (Türkçe, 5 başlık formatı veya v4.0 numerik)
```

### ORTA Pipeline
```
NBLM source (text özet, podcast'i NBLM kendisi üretsin diye)
→ rapor
→ podcast oluşturma (sadece Edel isterse)
```

### HAFİF Pipeline
```
Raporda 1-3 cümle not + kaynak linki
→ wiki/NBLM/podcast YOK
```

## Karar Kuralı

İçerik bir APA yayınından **ALINTILANMIŞ orijinal araştırma/inceleme/kılavuz** mu, yoksa APA'nın başka yayınlardan derlediği **HABER ÖZETİ** mi?

- **İkincil kaynak** (APA bir haber sitesinde alıntılanmış, APA üyesi bir haber makalesinde konuşulmuş) → HAFİF
- **Birincil kaynak** (APA'nın kendi dergisinde yayımlanmış araştırma, APA'nın kendi rehberi, APA podcast'i) → TAM

Bu kararı **kanal bazında değil, içerik BAZINDA** ver. Aynı bültende (örn. Practice Update) bir haber özeti (Hawaii yetki yasası) HAFİF olabilirken, aynı bültendeki ölçüme dayalı bakım rehberi TAM seviyesine yaklaşabilir.

## Örnekler

| Gelen İçerik | Kanal | Tür | Seviye |
|-------------|-------|-----|--------|
| "AI reshapes thinking" (Monitor cover) | Monitor web | Araştırma makalesi | TAM |
| "Hawaii prescriptive authority" | Gmail Practice Update | Haber özeti | HAFİF |
| "Measurement-based care guide" | Gmail Practice Update | Klinik rehber | TAM |
| "Kean depression disclosure" (CNN) | Gmail Media Watch | İkincil haber | HAFİF |
| "APA Labs Digital Badge" (JMIR) | Gmail Media Watch | İkincil haber | HAFİF |
| "Sleep & Mental Health" podcast | Speaking of Psych | Podcast | ORTA |
| "CE Roundup: New webinars" | Gmail CE Roundup | Promosyon | YOK |

## Neden Önemli?

Media Watch gibi bültenler haftada bir gelir ve çoğunlukla HAFİF içeriktir. Bunları TAM işlemek:
- Tool call bütçesini boşa harcar (wiki + NBLM + podcast = 10-15 tool call)
- Index.md'yi gereksiz entry'lerle şişirir
- Podcast üretimi 10-25 dk sürer, cron'da timeout riski
- Kullanıcı ikincil haberler için podcast dinlemek istemez

## Cron Akışı (Güncellenmiş)

```
Hafta sonu kontrolü → çık (hafta sonuysa)
→ Pre-check (diğer pipeline output)
→ 5 kanal tara (paralel)
→ Duplicate kontrolü (index.md cross-check)
→ İçerik Triage (TAM / HAFİF / YOK)
   → TAM varsa: işle, raporla
   → Sadece HAFİF varsa: kısa rapor, [SILENT] olma ama ağır işlem yapma
   → HİÇBİR ŞEY yoksa: [SILENT]
```
