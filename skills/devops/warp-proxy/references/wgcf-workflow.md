# wgcf Kurulum ve WARP+ Lisans Bağlama

## Oracle Cloud ARM64 Kurulum (İlk kurulum: 2026-05-27, Yeniden kurulum: 2026-06-09)

### 1. wgcf Kurulumu

```bash
curl -sLo /usr/local/bin/wgcf "https://github.com/ViRb3/wgcf/releases/download/v2.2.31/wgcf_2.2.31_linux_arm64"
chmod +x /usr/local/bin/wgcf
```

### 2. Hesap Oluşturma

```bash
cd /tmp && wgcf register --accept-tos
```

Çıktıda `Account type: free` görmelisin.

### 3. WARP+ Lisans Bağlama

```bash
wgcf update -l "LICENSE-KEY"
```

Kontrol: `Account type: unlimited` olmalı.

### 4. WireGuard Konfigürasyonu Oluşturma

```bash
wgcf generate  # → wgcf-profile.conf oluşur
```

Örnek çıktı:
```ini
[Interface]
PrivateKey = ...
Address = 172.16.0.2/32, 2606:4700:110:...
DNS = 1.1.1.1
MTU = 1280

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = engage.cloudflareclient.com:2408
```

### 5. WireGuard Konfigürasyonunu Sadeleştirme ve Başlatma

wgcf-profile.conf'u **düzenle** — sadece PrivateKey ve [Peer] bloğunu bırak:

```ini
[Interface]
PrivateKey = <private_key>

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = engage.cloudflareclient.com:2408
```

**⚠️ Silinmesi gerekenler:** `Address`, `DNS`, `MTU` satırları — `wg setconf` bunları tanımaz. MTU ayarı sonradan `ip link set mtu 1280 up dev wgcf` ile yapılır.

```bash
sudo cp wgcf-profile.conf /opt/warp-proxy/wgcf.conf
sudo chmod 600 /opt/warp-proxy/wgcf.conf
# wg setconf ile arayüzü başlat (wg-quick KULLANMA)
sudo ip link add dev wgcf type wireguard
sudo wg setconf wgcf /opt/warp-proxy/wgcf.conf
sudo ip addr add 172.16.0.2/32 dev wgcf
sudo ip link set mtu 1280 up dev wgcf
```

**⚠️ `wg-quick` KULLANMA:** Tüm sunucu trafiğini WARP'ten geçirir, SSH'ı koparır. production'da manuel `wg setconf` + fwmark routing kullan.

### 6. Test

```bash
# SOCKS5 proxy üzerinden test (production yöntemi)
curl -x "socks5h://127.0.0.1:1080" -s "https://www.cloudflare.com/cdn-cgi/trace" | grep -E "warp|colo|ip"
# warp=plus
# colo=FRA
# ip=<Cloudflare WARP IP'si>

curl -x "socks5h://127.0.0.1:1080" -s "https://ifconfig.me"  # IP değişmiş olmalı
```

### 7. YouTube Testi

```bash
# Metadata testi
yt-dlp --print title "https://youtu.be/O6p0CKYmBKs"
# → "TİBET'İN ÖLÜLER KİTABI..."

# Download testi (PO token gerekebilir)
yt-dlp -f "worstaudio" "https://youtu.be/O6p0CKYmBKs"
# Başarılı olursa: .webm dosyası oluşur
# 403 alırsan: PO token gerekli
```

### 8. Kapatma

```bash
sudo systemctl stop warp-proxy   # SOCKS5 proxy'yi ve WireGuard arayüzünü kapat
# Veya sadece WireGuard'ı kapat (proxy çalışmaya devam eder, ama WAPSSız):
# sudo wg setconf wgcf /dev/null
```

## docker-warp-socks Denemesi (Başarısız, 2026-05-27)

v5 imajı denendi, hem bridge hem host network ile:

- WireGuard el sıkışması başarılı
- DNS çözümleme çalışıyor
- SOCKS5 bağlantısı kuruluyor
- **TCP veri akışı yok** — timeout

Free WARP throttling yapıyor. v5'te WARP+ lisans desteği kaldırılmış. Sonuç: docker-warp-socks Oracle Cloud'da çalışmıyor, doğrudan wgcf kullan.

## Yeniden Kurulum (2026-06-09)

Eski dosyalar silinip yeni lisans ile sıfırdan kuruldu. Adımlar:
1. Eski servisi durdur: `sudo systemctl stop warp-proxy`
2. Eski dosyaları sil: `sudo rm -f /opt/warp-proxy/wgcf.conf /opt/warp-proxy/warp_proxy.py`
3. wgcf'i `/tmp`'ye indir (sudo gerekmez): `curl -sLo /tmp/wgcf ...`
4. `cd /tmp && wgcf register --accept-tos` → yeni hesap
5. `wgcf update -l "YENI-LISANS"` → unlimited olmalı
6. `wgcf generate` → config oluştur
7. Config'i sadeleştir (Address, DNS, **MTU** sil)
8. Deploy: `sudo cp /tmp/wgcf.conf /opt/warp-proxy/wgcf.conf`
9. Proxy scripti deploy et
10. Systemd servisini yeniden oluştur ve başlat

**Not:** WARP+ lisansı 5 cihazla sınırlı. Yeni `wgcf register` her cihaz slotu tüketir.

## PO Token Sorunu

YouTube, 2026 itibarıyla video indirme için PO (Proof of Origin) token zorunluluğu getirdi. WARP+ IP engelini aşar ama PO token ayrı bir katman:

```bash
# PO token ile indirme
yt-dlp --extractor-args "youtube:po_token=ios.gvs+TOKEN" "URL"
```

Rehber: https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide
