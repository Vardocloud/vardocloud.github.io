# Telegram Kanalı HTML Tabanlı İzleme — no_agent Cron Pattern

## Use Case

Bir Telegram kanalını (public) yeni mesajlar için düzenli kontrol etmek, tarayıcı/API kullanmadan.

## Pattern — no_agent + State File + HTML Parsing

### Çalışma Prensibi

1. `curl` veya `urllib` ile `https://t.me/s/KanalAdi` sayfasını çek
2. HTML'den mesajları regex ile ayrıştır:
   - Mesaj zamanı: `<time datetime="ISO-8601">` attribute'u
   - Mesaj metni: `<div class="tgme_widget_message_text js-message_text" dir="auto">`
3. State dosyasında (`~/.hermes/scripts/.kanal_state.json`) son görülen mesajın `datetime`'ını tut
4. Yeni mesaj varsa → stdout'a bas (no_agent: boş stdout = sessiz)
5. State'i güncelle

### Kritik Detaylar

**Telegram public preview HTML'de mesajlar statiktir** — JavaScript render'ı gerekmez. `curl -s "https://t.me/s/KanalAdi"` ile tüm mesajlar HTML'de gömülü gelir.

**HTML yapısı:**
```html
<div class="tgme_widget_message_wrap js-widget_message_wrap">
  <time datetime="2026-07-09T09:44:54+00:00">09:44</time>
  <div class="tgme_widget_message_text js-message_text" dir="auto">mesaj içeriği</div>
</div>
```

**Reply'li mesajlar:** Reply mesajlarında 2 tane `tgme_widget_message_text` div'i olur. İlki `js-message_reply_text` class'lıdır (küçük, alıntı), ikincisi asıl mesajdır. Regex ile ikinci text'i seç veya reply block'unu tespit et.

**HTML entity dönüşümleri:**
- `&#036;` → `$`
- `&#33;` → `!`
- `&#39;` → `'`
- `&amp;` → `&`

### Python Script Şablonu

```python
#!/usr/bin/env python3
"""Kanal izleme script'i — no_agent cron için."""
import json, os, re, sys, urllib.request

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.kanal_state.json")
CHANNEL_URL = "https://t.me/s/KanalAdi"

def parse_messages(html):
    """HTML'den mesajları datetime + text olarak çıkarır."""
    blocks = re.split(r'<div\s+class="tgme_widget_message_wrap', html)[1:]
    messages = []
    for block in blocks:
        dt_match = re.search(r'<time\s+[^>]*datetime="([^"]+)"', block)
        if not dt_match:
            continue
        
        # Reply'li mesajlarda ikinci text div'ini al
        all_texts = re.findall(
            r'<div\s+class="tgme_widget_message_text\s+js-message_text"\s+dir="auto">(.*?)</div>',
            block, re.DOTALL
        )
        # Reply varsa (block'ta tgme_widget_message_reply varsa) ikinci text'i al
        if 'tgme_widget_message_reply' in block and len(all_texts) > 1:
            raw_text = all_texts[1]
        else:
            raw_text = all_texts[0] if all_texts else ''
        
        text = re.sub(r'<br\s*/?>', '\n', raw_text)
        text = re.sub(r'<[^>]+>', '', text)
        for ent, char in [('&#036;', '$'), ('&#33;', '!'), ('&#39;', "'"),
                          ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                          ('&quot;', '"')]:
            text = text.replace(ent, char)
        text = re.sub(r'\n{3,}', '\n\n', text.strip())
        
        if text:
            messages.append({"datetime": dt_match.group(1), "text": text})
    return messages

def main():
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    else:
        sys.exit(0)  # İlk çalıştırma: state elle oluşturulmalı
    
    last_dt = state.get("last_datetime", "")
    html = urllib.request.urlopen(
        urllib.request.Request(CHANNEL_URL, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }), timeout=30
    ).read().decode("utf-8")
    
    messages = parse_messages(html)
    messages.sort(key=lambda m: m["datetime"])
    
    new_msgs = [m for m in messages if m["datetime"] > last_dt]
    if not new_msgs:
        sys.exit(0)  # sessiz
    
    # State güncelle
    state["last_datetime"] = max(m["datetime"] for m in messages)
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
    
    # Yeni mesajları yazdır
    for msg in new_msgs:
        print(f"[{msg['datetime']}] {msg['text'][:200]}")
        print("---")

if __name__ == "__main__":
    main()
```

### State Başlatma

İlk çalıştırmadan önce state dosyasını elle oluştur — kanaldaki en son mesajın datetime'ı ile:

```json
{"last_datetime": "2026-07-09T09:44:54+00:00"}
```

Böylece script ilk çalıştırmada tüm geçmişi değil, sadece o tarihten sonraki mesajları raporlar.

### Cron Kurulumu — deliver=local ile

⚠️ Bu cron'lar **`deliver=local`** ile kurulmalıdır. Aksi halde her yeni mesaj Telegram topic'ine düşer ve kullanıcının ana akışını gereksiz yere doldurur. Local çıktı `~/.hermes/cron/output/` altına kaydedilir.

```python
# Vanitas cronjob tool ile:
cronjob(action='create', schedule='0 12 * * *', name='Kanal izleme',
        script='kanal_izleme.py', no_agent=True, deliver='local')
```

### Sınırlamalar

1. **Sadece PUBLIC kanallar çalışır.** Private kanallar veya preview'ı kapalı kanallarda çalışmaz.
2. **Sayfada sadece son ~20 mesaj görünür.** Kanal uzun süre kontrol edilmezse ara mesajlar kaçabilir.
3. **t.me/s/ sayfası Cloudflare korumalıdır.** User-Agent header'ı gereklidir. Aşırı sık (dakikada 1'den fazla) sorguda bot detection tetiklenebilir.
4. **HTML yapısı değişebilir.** Telegram UI güncellemelerinde regex'leri güncellemek gerekebilir.
