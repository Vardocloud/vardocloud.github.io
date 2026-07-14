# Oracle Cloud Block Volume — Always Free Tier

Sunucu: Oracle Cloud ARM64, Ubuntu 22.04, boot volume 46.6GB (düz ext4, LVM YOK).

## Always Free Limitleri

- Toplam block storage: 200GB (boot dahil)
- Boot volume: ~47GB kullanımda
- Eklenebilir: ~150GB daha
- Ücret: 200GB'a kadar sıfır (Always Free)
- Volume sayısı: 2'ye kadar

## OCI Console Adımları (Telefon Dostu)

### Block Volume Oluştur

Menü → Storage → Block Volumes → Create Block Volume

Kritik ayarlar:
- Name: herhangi bir isim
- Availability Domain: Instance ile aynı AD olmalı (yanlış AD → attach listesinde görünmez)
- Size: 50-150 GB (200GB toplam limit dahilinde)
- Backup Policy: None (ücretli seçeneklerden kaçın)
- Encryption: Oracle-managed keys (varsayılan, ücretsiz, açık kalsın)
- Performance: Balanced (10 VPUs/GB) — çoğu iş yükü için yeterli

### Volume'ü Instance'a Bağla

Volume detay sayfası → Attach to Instance
- Attachment Type: **Paravirtualized** (iSCSI'den daha basit)
- Access: Read/Write

## Sunucu Tarafı (SSH ile Elle)

Bu adımlar Hermes ajanı tarafından çalıştırılamaz — disk formatlama güvenlik blocklist'inde. SSH ile elle yapılmalı:

1. Diski gör (genelde /dev/sdb): `lsblk`
2. ext4 olarak formatla
3. Mount noktası oluştur: `/data`
4. Geçici bağla
5. fstab'a kalıcı mount satırı ekle: `/dev/sdb /data ext4 defaults,noatime 0 2`

## Veri Taşıma Stratejisi

Projeleri /data'ya taşı, orijinal konumda symlink bırak:

```
/data/projects/fis-asistani  → ~/fis-asistani (symlink)
/data/projects/hermes-workspace → ~/hermes-workspace (symlink)
```

## Pitfall'lar

- **AD uyuşmazlığı:** Instance'ın AD'sini kontrol etmeden volume oluşturma.
- **LVM yok:** Bu sunucuda LVM yok (düz ext4). Volume root'a merge edilemez — ayrı mount noktası gerekir.
- **mv timeout:** Dosya sistemleri arası taşıma (`mv`) büyük dizinlerde (2GB+) timeout verebilir. Alternatif: önce kopyala (`cp -a`), sonra kaynağı sil (`rm -rf`).
- **node_modules:** Taşıma sırasında en büyük dizin (1.8GB). Gerekirse silip yeniden kurulabilir.
- **Disk formatlama:** Hermes ajanı bu komutu çalıştıramaz — kullanıcı SSH ile elle yapmalı.

## Doğrulama Komutları

```bash
df -h / /data           # İki disk de görünmeli
lsblk -f /dev/sdb       # Formatlanmış olmalı (FSTYPE: ext4)
grep sdb /etc/fstab     # fstab'da kalıcı mount satırı
```

## 5 Haz 2026 — Başarılı Kurulum

- Volume: 100GB, Balanced (10 VPUs/GB), Paravirtualized
- Mount: `/data` (ext4, noatime)
- Taşınan: `fis-asistani` (.venv silindi, kod /data'da), `hermes-workspace` (node_modules silindi)
- Sonuç: Root %74 (12GB boş), /data başlangıçta 93GB boş
