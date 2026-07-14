# Telegram MEDIA Dosya Gönderimi

> Pitfall'lar ve çözümler. Hermes Gateway MEDIA etiketiyle dosya gönderimi.

## Kritik Pitfall: MEDIA path outside allowed roots

Gateway `MEDIA:/path/to/file` etiketini işlerken sadece belirli dizinlerden dosya gönderebilir:

**Varsayılan izinli dizinler:**
- `~/.hermes/audio_cache/`
- `~/.hermes/image_cache/`
- `~/.hermes/video_cache/`
- `~/.hermes/document_cache/`
- `~/.hermes/cache/screenshots/`

**Hata belirtisi:** Gateway log'da `Skipping unsafe MEDIA directive path outside allowed roots` uyarısı. Send başarılı görünür ama dosya Telegram'a ulaşmaz.

**Çözüm 1 (hızlı):** Dosyayı izinli dizine kopyala:
```bash
cp dosya.mp3 ~/.hermes/audio_cache/dosya.mp3
```

**Çözüm 2 (kalıcı):** `.env` dosyasına `HERMES_MEDIA_ALLOW_DIRS` değişkenini ekle. Dizinleri `:` veya `,` ile ayır. Sonra gateway'i restart et.
Örnek ek: `HERMES_MEDIA_ALLOW_DIRS=/home/ubuntu/.hermes/notebooklm`

**Gateway restart:** `systemctl --user restart hermes-gateway`

## Format Uyumluluğu

| Format | Telegram Desteği | Not |
|--------|-----------------|-----|
| `.mp3` | ✅ Ses dosyası | Tam destek |
| `.ogg` | ⚠️ Sesli mesaj | Voice note olarak farklı işlenir, dosya olarak gelmeyebilir |
| `.m4a` | ❌ | Telegram göndermez, MP3'e çevir |
| `.md` | ❌ | Markdown dosyası gelmez, `.txt` yap |
| `.txt` | ✅ Döküman | Tam destek |
| `.png` | ✅ Fotoğraf | Tam destek |

## Dönüştürme Komutları

```bash
# M4A → MP3
ffmpeg -i dosya.m4a -c:a libmp3lame -b:a 64k dosya.mp3

# M4A → OGG (sesli mesaj)
ffmpeg -i dosya.m4a -c:a libopus -b:a 32k dosya.ogg

# MD → TXT
cp dosya.md dosya.txt
```

## Doğrudan Google Drive Linkleri

`lh3.googleusercontent.com/notebooklm/...` gibi URL'ler authentication gerektirir — curl ile indirince HTML login sayfası gelir. MCP `download_artifact` ile indir, sonra dönüştür.

## İlk Denemede Gelmezse

Gateway restart sonrası MEDIA etiketi çalışmazsa:
1. `journalctl --user -u hermes-gateway --since "2 min ago" | grep -i unsafe` ile log kontrol et
2. Dosyanın izinli dizinde olduğundan emin ol
3. Formatı kontrol et (`.m4a` → `.mp3`, `.md` → `.txt`)
