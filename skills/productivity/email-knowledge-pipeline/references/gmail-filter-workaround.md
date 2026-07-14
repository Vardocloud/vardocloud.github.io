# Gmail Filtre Sınırlaması ve Cron Pipeline Workaround

## Problem
Gmail'den belirli göndericileri otomatik bloklamak/filtrelemek için Gmail API üzerinden
filter oluşturmak istenebilir. Ancak mevcut OAuth token'ı `gmail.settings.basic` scope'una
sahip değildir (sadece `gmail.modify` vardır), bu nedenle programatik filter oluşturma
şu hatayla başarısız olur:

```
Request had insufficient authentication scopes.
```

## Workaround: Cron Pipeline "Atlanacak Mailler" Listesi
Gmail filter'ı oluşturulamadığında, aynı etkiyi **cron job pipeline'ının prompt'una**
göndericiyi "atlanacak" olarak ekleyerek elde edebiliriz:

1. `email-knowledge-pipeline` skill'indeki **Atlanacak Mailler** bölümüne göndericiyi ekle
2. Cron job bir sonraki çalışmasında bu maili görür → içeriğini işlemeden archive/trash yapar
3. Var olan mailler el ile trash'e atılır (mevcutları temizlemek için)

### Adımlar
```bash
# 1. Var olan mailleri bul
ALL_PROXY="" python3 google_api.py gmail search "from:GONDERICI --max 20"

# 2. ID'leri al, trash'e at
# Her mail için:
python3 google_api.py gmail modify MSG_ID --remove-labels "UNREAD,INBOX" --add-labels "TRASH"

# 3. email-knowledge-pipeline SKILL.md'de "Atlanacak Mailler" bölümüne ekle
# - **Gönderici Adı** (`adres@domain.com`) — bloklandı. Mail gelirse archive/trash yap.
```

### Dezavantaj
- Cron pipeline'ı çalışana kadar mail gelen kutusunda kalır
- Gmail filter'ı kadar anlık değildir (pipeline 10/16/22 saatlerinde çalışır)
- Kullanıcıya manuel filtre önerilebilir: Gmail Ayarlar → Filtreler → Yeni Filtre → adres gir → Sil

## Örnekler
| Tarih | Bloklanan | Yöntem |
|-------|-----------|--------|
| 11 Haz 2026 | Timeleft (`hello@timeleft.com`) | Atlanacak Mailler + mevcutlar trash |
| 11 Haz 2026 | Julian Goldie (tüm varyasyonlar) | Atlanacak Mailler + wiki/NBLM temizliği |
