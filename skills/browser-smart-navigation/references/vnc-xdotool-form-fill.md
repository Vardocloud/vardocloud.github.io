# VNC + xdotool ile Form Doldurma

VNC'de browser açıkken klavye çalışmadığında (noVNC klavye sorunu, tuş haritası hatası) veya
manuel giriş gerektiğinde xdotool ile VNC display'ine klavye/fa komutu gönderme.

## Ön Koşul

```bash
sudo apt-get install -y xdotool wmctrl
```

## VNC Pencere ID'sini Bulma

```bash
DISPLAY=:1 wmctrl -l
# Çıktı: 0x01c00003  0  hostname  Upwork Login — Mozilla Firefox
```

## Pencereyi Aktifleştirip Form Doldurma

```bash
# Pencereyi aktifleştir
DISPLAY=:1 xdotool windowactivate 0x01c00003

# Input alanına git (Tab ile)
DISPLAY=:1 xdotool key Tab Tab

# Metin yaz
DISPLAY=:1 xdotool type "email@example.com"

# Sonraki alana geç
DISPLAY=:1 xdotool key Tab

# Şifre yaz
DISPLAY=:1 xdotool type "password123"

# Enter'a bas (submit)
DISPLAY=:1 xdotool key Return
```

## Cloudflare Challenge Sonrası Kullanım

Bu yöntem özellikle Cloudflare managed challenge sayfasında işe yarar:
1. Puppeteer MCP ile form doldur (email + password)
2. Login submit'te Cloudflare challenge çıkarsa
3. VNC'ye geç, kullanıcı challenge'ı manuel geçsin
4. Veya xdotool ile browser'a müdahale et

## Firefox'u VNC'de Başlatma

```bash
DISPLAY=:1 snap run firefox --new-instance https://example.com
```

## Pratik İpuçları

- `wmctrl -l` ile pencere listesini al, doğru pencereyi bul
- `xdotool search --name "Firefox"` ile de pencere bulunabilir
- Her `type` komutundan önce `sleep 1` koy — sayfanın tepki vermesi için
- `xdotool key Tab` yerine `xdotool key Alt+Tab` farklı davranabilir
