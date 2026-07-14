# VNC Headless Server Setup

Kullanıcının bot detection'ı manuel geçmesi gerektiğinde (Cloudflare managed challenge, reCAPTCHA vb.).

## Ön Koşullar

Headless sunucuda kurulu olması gerekenler:

```
tigervnc-standalone-server  → VNC server
fluxbox                     → hafif pencere yöneticisi
xvfb                        → sanal X server
novnc                       → web tabanlı VNC istemcisi
chromium (snap)             → browser (puppeteer MCP için de gerekli)
```

## Kurulum

```bash
sudo apt install -y tigervnc-standalone-server fluxbox xvfb novnc
sudo snap install chromium
```

## VNC Başlatma

```bash
# Şifre
mkdir -p ~/.vnc
echo "gecici_sifre" | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

# Eski sessionları temizle
vncserver -kill :1 2>/dev/null

# Yeni session
vncserver :1 -localhost no -geometry 1440x900 -depth 24 \
  -SecurityTypes VncAuth -PasswordFile ~/.vnc/passwd

# Pencere yöneticisi + browser
DISPLAY=:1 fluxbox &
DISPLAY=:1 chromium-browser --no-first-run --no-default-browser-check \
  --disable-blink-features=AutomationControlled \
  --window-size=1440,900 --start-maximized https://hedef-sayfa.com

# noVNC (opsiyonel — browser'dan bağlanmak için)
websockify --web /usr/share/novnc 6080 localhost:5901 &
```

## Bağlantı Bilgileri

| Yöntem | Adres |
|--------|-------|
| noVNC (browser) | `http://tailscale-ip:6080/vnc.html` → Connect + şifre |
| VNC Viewer | `tailscale-ip:5901` |

## Güvenlik

UFW aktifse:

```bash
sudo ufw allow from 100.64.0.0/10 to any port 5901 proto tcp
```

Tailscale IP: `tailscale ip -4` ile öğren.

## Kullanım Akışı

1. Kullanıcıya bağlantı bilgilerini ver
2. Kullanıcı browser'da "Verify you are human" gibi challenge'ı geçer
3. Kullanıcı haberi verince sen oturumu devral (Puppeteer MCP ile login vs.)
4. İşlem bitince `vncserver -kill :1` ile kapat

## Hibrit Kullanım: VNC Chrome + Puppeteer MCP

Chrome'u `--remote-debugging-port` ile başlat, sonra Puppeteer MCP ile `puppeteer_connect_active_tab(debugPort=...)` ile bağlan. Böylece form doldurma gibi işlemleri Puppeteer yapar, kullanıcı sadece Cloudflare challenge'ını geçer.

**Adımlar:**

1. VNC'yi başlat
2. Fluxbox'ı başlat: `DISPLAY=:1 fluxbox &`
3. Chrome'u remote debugging portu ile başlat:
   ```
   DISPLAY=:1 chromium-browser --remote-debugging-port=9224 \
     --window-size=1440,900 --start-maximized https://hedef-sayfa.com
   ```
4. noVNC'yi başlat: `websockify --web /usr/share/novnc 6080 localhost:5901 &`
5. Puppeteer MCP ile bağlan: `puppeteer_connect_active_tab(debugPort=9224)`
6. Puppeteer ile formu doldur (puppeteer_fill/evaluate ile)
7. Kullanıcı VNC'den challenge'ı geçer veya security question'ı cevaplar
8. Puppeteer ile devam et

**Önemli:** Puppeteer MCP `puppeteer_connect_active_tab` parametre olarak `debugPort` alır. Eğer yeni bir browser başlatmaya çalışırsa snap chromium bulamayabilir → önce `sudo snap install chromium` kur.

## Pitfalls

- **Snap Chromium çalışmazsa:** `chromium-browser` snap transitional package. `sudo snap install chromium` ile kur.
- **VNC port:** display :1 → 5901, :2 → 5902
- **UFW inaktifse** portlar zaten açıktır — Tailscale IP ile bağlan yeter.
- Geçici şifre kullan, işlem sonrası temizle.
