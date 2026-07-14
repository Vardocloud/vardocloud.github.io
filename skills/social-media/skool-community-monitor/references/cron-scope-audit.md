# Cron Kapsam Denetimi — Skool + Ek Skill Etkileşimleri

Bu referans, skool-community-monitor skill'inin cron job içinde diğer skill'lerle birlikte kullanıldığında ortaya çıkan kapsam kayması (scope creep) riskini belgeler.

## Keşfedilen Durum (28 Haziran 2026)

Skool Günlük Rapor cron'u (`job_id: 40448623b352`) şu skill'leri yükler:
- `skool-community-monitor`
- `email-knowledge-pipeline`
- `llm-wiki`
- `sohbet`
- `google-workspace`

**Cron prompt'u şöyle tanımlanmıştı:**
```
Gmail'den SKool bildirimlerini, GitHub trend'lerini tara. İşle. Raporla.
```

**Gözlemlenen davranış:** Cron, APA haberlerini de işledi (28 Haziran çıktısında 3 APA maddesi). APA, cron prompt'unda tanımlı olmamasına rağmen `email-knowledge-pipeline` skill'i sayesinde Gmail'den çekildi.

## Neden Olur?

- `email-knowledge-pipeline` — Gmail'deki TÜM bilgilendirici mailleri işler (APA, Skool, bültenler vb.)
- `skool-community-monitor` — SADECE Skool bildirimlerini işlemek ister
- İkisi aynı cron'da yüklendiğinde, cron `email-knowledge-pipeline`'ın geniş kapsamı nedeniyle Skool dışı içerikleri de çeker

## Çözüm

### Seçenek A: Cron prompt'una net kapsam sınırı ekle
```
## KAPSAM (ZORUNLU)
- SADECE Skool bildirimlerini ve GitHub trend'lerini işle.
- APA, bülten, duyuru maillerini İŞLEME — onlar ayrı cron'da.
- email-knowledge-pipeline sadece Skool mail'lerinden post URL'si çıkarmak için yüklendi, genel posta işleme için değil.
```

### Seçenek B: email-knowledge-pipeline'ı cron skill listesinden çıkar
- Skool mail'lerinden URL çıkarmak için `google-workspace` doğrudan Gmail API ile de çalışabilir
- `email-knowledge-pipeline` olmadan cron sadece kendi prompt'una odaklanır

## Test Yöntemi

Cron çıktılarını `~/.hermes/cron/output/40448623b352/` altında kontrol et:
- Çıktıda APA maddesi varsa → kapsam kayması var
- Çıktıda sadece Skool/GitHub maddeleri varsa → kapsam doğru

## Skill Etkileşim Haritası

```
skool-community-monitor
  ├── SADECE Skool post'ları + GitHub
  ├── Gmail'den sadece Skool bildirimlerini çeker
  └── email-knowledge-pipeline ile birlikte kullanılırsa:
       └── ⚠️ APA, bülten, diğer mail içerikleri de çekilir (scope creep)
```
