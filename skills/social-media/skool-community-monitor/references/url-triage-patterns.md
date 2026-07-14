# URL Slug Triage Patterns

İçerik yüklemeden post türünü tahmin etmek için URL slug pattern'ları. browser_console ile post linklerini çektikten sonra, web_extract ile yüklemeden ÖNCE bu pattern'larla triage yap.

## AI Automation Society

| URL Slug Pattern | Post Türü | Öncelik | Aksiyon |
|-----------------|-----------|---------|---------|
| `new-video-*` | Nate Herk video post'u | 🔴 YÜKSEK | web_extract ile çek |
| `weekly-wins-*` | Haftalık özet | 🟡 Orta | web_extract ile çek (topluluk trend'i) |
| `ais-live-*` | Event duyurusu (Nate) | 🔴 YÜKSEK | web_extract ile çek |
| `*-ais-challenge-*`, `aischallenge-*` | Challenge post'u | ⚪ En Düşük | Toplu ekle, içerik çekme |
| `day-*-challenge*`, `day-*ais*` | Challenge günlük post'u | ⚪ En Düşük | Toplu ekle, içerik çekme |
| `day-*-completed*`, `day-*-complete*` | Challenge tamamlama | ⚪ En Düşük | Toplu ekle, içerik çekme |
| `welcome-*`, `please-read-*`, `rules-*` | Pinned/sabit post | ⚪ Skip | URL'i varsa processed'a ekle |
| `*-agent-*`, `*-orchestrat*`, `*-pipeline*` | Teknik içerik | 🟡 Orta | web_extract ile çek |
| `*-hermes-*` | Hermes agent içeriği | 🟡 Orta | web_extract ile çek |
| `*-mcp-*`, `*-tool-*` | Araç/tool keşfi | 🟡 Orta | web_extract ile çek |
| `*-voice-*`, `*-stt-*`, `*-tts-*` | Ses pipeline'ı | 🟡 Orta | web_extract ile çek |
| `help-*`, `help-needed-*`, `urgent-*` | Üye sorusu | 🟢 Düşük | Sadece URL kaydet |
| `*-hire-*`, `*-partner-*`, `*-pricing-*` | İş/işbirliği | 🟢 Düşük | Sadece URL kaydet |
| `aios-*`, `*-ai-os-*` | AI OS tartışması | 🟡 Orta | İçerik çek (supervisor pattern) |
| `fable-5-*`, `fable5-*` | Fable 5 içeriği | 🟡 Orta | İçerik çek |
| `claude-*` | Claude içeriği | 🟡 Orta | İçerik çek |
| `gpt-*`, `*-sol-*` | GPT/Sol içeriği | 🟡 Orta | İçerik çek |
| Diğer tüm üye post'ları | Genel | 🟢 Düşük | Sadece URL kaydet |

## Yapay Zekâdan Gelire

| URL Slug Pattern | Post Türü | Öncelik | Aksiyon |
|-----------------|-----------|---------|---------|
| `hos-geldin*`, `tanisma*` | Hoş geldin / tanışma | ⚪ Skip | Processed'a ekle |
| `*animasyon*` | AI animasyon gösterimi | 🟢 Düşük | Sadece URL kaydet |
| `*video*`, `*videom*`, `*shorts*` | AI video gösterimi | 🟢 Düşük | Sadece URL kaydet |
| `*muzik*`, `*sarki*`, `*sark*` | AI müzik üretimi | 🟢 Düşük | Sadece URL kaydet |
| `*reklam*` | AI reklam gösterimi | 🟢 Düşük | Sadece URL kaydet |
| `*yasa*`, `*onemli*` | Admin duyurusu | 🟡 Orta | İçerik çek |
| `*otomasyon*` | AI otomasyon içeriği | 🟡 Orta | İçerik çek |
| Diğer tüm post'lar | Üye AI içerik gösterimi | 🟢 Düşük | Sadece URL kaydet |

## Triage Akışı

1. browser_console ile tüm post linklerini çek (başlık + URL)
2. processed_urls'te olmayanları filtrele
3. URL slug'ındaki pattern'a bak → öncelik belirle
4. Yüksek/Orta → web_extract ile çek (public community) veya browser'da aç (private)
5. Düşük/En Düşük → sadece processed_urls'e ekle, içerik çekme

## İstisnalar

- Bir post birden fazla pattern'a uyabilir (örn. `new-video-fable-5-just-built-me-a-business` = hem `new-video-*` hem `fable-5-*`). En yüksek öncelikli pattern'ı kullan.
- Nate Herk post'ları genelde `new-video-*` ile başlar. Emin değilsen yazar adını kontrol et (browser_console çıktısında link text'inde "@NateHerk" veya "Nate Herk" geçer).
- Challenge dönemlerinde çok sayıda `day-*`, `aischallenge-*` post'u çıkar — hepsini toplu ekle, teker teker inceleme.
