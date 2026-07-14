# Skill-Cron Prompt Senkronizasyonu (6 Tem 2026)

## Problem

Cron job prompt'ları ile skill'ler arasında **çift yönlü kopukluk** vardır:
- Skill güncellendiğinde cron prompt'u **otomatik güncellenmez**
- Cron prompt'undaki kurallar skill'e **yansımaz**
- Sonuç: Kural skill'de var sanılır ama cron'da yoktur (veya tersi)

## 6 Temmuz 2026 Vakası: LinkedIn Kuyruk Besleme Kuralı

**Kural:** Kuyrukta 2'den fazla konu biriktiğinde besleme (yeni içerik taraması) durmalı.

**Neredeydi?** Sadece `linkedin_kuyruk_besle` cron prompt'unda (`status == "pending"` kayıt sayısı 3'ten azsa besle).
**Nerede değildi?** `linkedin` skill'inde. Ayrıca cron sadece `pending` sayıyor, `pending_approval`'ları saymıyordu.
**Sonuç:** Kuyrukta 7 pending_approval + 3 pending = 10 kayıt birikti.

## Kök Neden

1. Cron oluşturulurken kural skill'e yazılmadı (sadece cron prompt'una yazıldı)
2. Skill güncellenince cron prompt'u güncellenmedi
3. Cron prompt'u `pending` + `pending_approval` ikisini birden saymıyordu

## Zorunlu Kontrol Listesi

**Her cron job oluştururken:**
- [ ] Prompt'taki kurallar skill'e de eklendi mi?
- [ ] Skill'deki kurallar cron prompt'una da yazıldı mı?
- [ ] İkisi arasında çelişki var mı?

**Her skill güncellemesinde:**
- [ ] Bu skill'i kullanan cron job'ları hangileri? (`cronjob action='list'`)
- [ ] Cron prompt'ları da güncellenmeli mi?
- [ ] `cronjob action='update'` ile prompt'ları güncelle

**Kural konumu kararı:**
| Kural Türü | Nereye Yazılır |
|------------|---------------|
| İçerik/üslup kuralları (hashtag, ton, uzunluk) | Skill |
| Workflow kuralları (önce X yap, sonra Y) | Skill |
| Eşik değerleri, limitler (3'ten azsa, 2'den fazlaysa) | Skill + Cron prompt (İKİSİNE DE) |
| Provider/model ayarları | Cron config |
| Delivery hedefi | Cron config |
| Sadece cron'a özel (zamanlama, tekrar) | Cron config |

## Önlem

`linkedin` skill'ine **KONU BİRİKME LİMİTİ** bölümü eklendi ve cron prompt'u güncellendi.
Artık: `pending + pending_approval >= 2` ise besleme susar.
