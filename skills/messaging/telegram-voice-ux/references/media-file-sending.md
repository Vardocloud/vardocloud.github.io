# Telegram MEDIA File Sending

> `send_message` ile `MEDIA:` etiketi kullanarak dosya gönderme rehberi.

## İzinli Dizinler

`MEDIA:` yalnızca gateway tarafından izin verilen dizinlerden çalışır:

**Varsayılan izinli dizinler:**
- `~/.hermes/audio_cache/`
- `~/.hermes/image_cache/`
- `~/.hermes/video_cache/`
- `~/.hermes/document_cache/`

**Ek dizin eklemek için:**
`.env` dosyasına `HERMES_MEDIA_ALLOW_DIRS` değişkeni eklenir (örn: `/home/ubuntu/.hermes/notebooklm`). Ardından `systemctl --user restart hermes-gateway` ile gateway yeniden başlatılır.

## Debugging

Gateway loglarında hata kontrolü:
```
tail -50 ~/.hermes/logs/gateway.log | grep "unsafe MEDIA"
```
`"Skipping unsafe MEDIA directive path outside allowed roots"` → dosya izinli dizinde değil.

## Format Desteği

| Format | Telegram'da | Not |
|--------|------------|-----|
| `.mp3` | Ses dosyası | En güvenilir |
| `.ogg` | Sesli mesaj baloncuğu | Her zaman görünmeyebilir |
| `.m4a` | Ses dosyası | Bazı istemcilerde sorun |
| `.txt` | Döküman | Sorunsuz |
| `.md` | Desteklenmez | `.txt`'ye çevir |
| `.jpg/.png/.webp` | Fotoğraf | Sorunsuz |
| `.mp4` | Video | Sorunsuz |

## NotebookLM Ses Dosyası İndirme

NotebookLM MCP'den podcast/ses indirirken dikkat edilecekler:

1. **MCP download aracını kullan.** `studio_status` ile görünen `audio_url` (ör: `lh3.googleusercontent.com/...`) thumbnail'dır — doğrudan `curl` ile indirirsen Google sign-in HTML'i gelir. `mcp_notebooklm_mcp_download_artifact` ile indir.
2. **Uzantıyı `.m4a` yap.** NotebookLM AAC sesi MP4 konteynerda verir — `.mp3` uzantısı reddedilir.
3. **Telegram için `.mp3`'e çevir:** `ffmpeg -i podcast.m4a -c:a libmp3lame -b:a 64k podcast.mp3`
4. **Sesli mesaj baloncuğu için `.ogg`:** `ffmpeg -i podcast.m4a -c:a libopus -b:a 32k podcast.ogg` (her zaman çalışmaz, `.mp3` daha güvenli)

`send_message` "success" dönebilir ama dosya Telegram'da görünmez. Gateway loglarını kontrol etmeden başarılı sayma. "success" her zaman dosyanın ulaştığı anlamına gelmez.

## MEDIA Etiketi Kullanımı

```
send_message(
    message="Açıklama metni\nMEDIA:/path/to/file.mp3",
    target="telegram"
)
```

**Kritik:** `MEDIA:` etiketinden önce en az bir satır metin olmalı — boş mesaj + MEDIA çalışmaz. `"No deliverable text or media remained"` hatası verir.
