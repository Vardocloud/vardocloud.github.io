# Podcast Generation Threshold & Decision Guide

> When to create (or skip) a NotebookLM Audio Overview from APA content.
> Established: 20 Temmuz 2026

## Core Principle

NotebookLM podcast üretimi 10-25 dakika sürer ve tool call bütçesi tüketir. Her yeni source için podcast oluşturmak anlamsız — içeriğin "podcast'i dolduracak" nitelikte olması gerekir.

## Decision Matrix

### ✅ PODCAST OLUŞTUR

| İçerik Türü | Neden | Örnek |
|-------------|-------|-------|
| Tam araştırma makalesi (500+ kelime) | Yeterli derinlik, tartışılacak bulgular | Monitor cover story, CE Corner, Editor's Choice |
| Uzun klinik rehber | Pratik çıkarımlar, adım adım protokol | Practice Update derin makale |
| Birden çok source (batch) | Tek podcast'te özetlenebilir | Günün tüm yeni makaleleri |
| Speaking of Psychology bölümü | Zaten podcast formatında | Ep. 389+ |

### ❌ PODCAST ATLA (sadece rapor)

| İçerik Türü | Neden | Alternatif |
|-------------|-------|------------|
| "By the Numbers" veri infografiği | 3-5 istatistik, uzun metin yok | Wiki kısa kayıt + raporda 2 cümle |
| Tek cümlelik haber snippet'i | Podcast'i dolduracak içerik yok | Raporda 1 satır |
| Promosyon/üyelik duyurusu | Zaten atlanacak içerik | Tamamen atla |
| Cron modu (her durumda) | 10-25 dk süre kısıtı, kullanıcı yok | Sadece wiki + rapor |

## Content Volume Heuristic

Şu soruyu sor: **"Bu içerikten 8-10 dakikalık, dinlenebilir, bilgilendirici bir podcast çıkar mı?"**

- Kaynak metin < 200 kelime → ❌ podcast atla
- Kaynak metin 200-500 kelime → ⚠️ ancak çoklu source varsa düşün
- Kaynak metin > 500 kelime → ✅ podcast yapılabilir
- Kaynak > 3 (aynı gün içinde) → 🎯 tek podcast'te topla

## Cron Mode (kesin kural)

Cron job'larda podcast üretimi her zaman atlanır:
- Süre kısıtı (10-25 dk → cron timeout riski)
- Kullanıcı yok (MEDIA gönderimi anlamsız)
- Tool call bütçesi (podcast üretimi 5-10 tool call tüketir)

İnteraktif modda Edel "podcast yapalım" veya "sesli özet" derse oluştur.

## Refs

- Content triage: `references/cron-content-triage.md` (📊 By the Numbers row)
- Podcast workflow: `references/audio-overview-workflow.md`
- Cron pipeline: SKILL.md → Cron Mode bölümü
