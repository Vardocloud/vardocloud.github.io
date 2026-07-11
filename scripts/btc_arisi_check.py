#!/usr/bin/env python3
"""Bitcoin Arısı kanalı yeni mesaj kontrolü — no-agent cron script'i.

Çalışma mantığı:
- t.me/s/BitcoinArisi sayfasını HTML olarak çeker
- Son görülen mesajın datetime'ını state dosyasından okur
- Daha yeni mesaj varsa bunları stdout'a basar (no-agent: boş stdout = sessiz)
- State'i günceller
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.btc_arisi_state.json")
CHANNEL_URL = "https://t.me/s/BitcoinArisi"


class MessageExtractor(HTMLParser):
    """Telegram public preview HTML'sinden mesajları çıkarır."""

    def __init__(self):
        super().__init__()
        self.messages = []
        self._in_msg_wrap = False
        self._in_text_div = False
        self._in_time = False
        self._current_dt = None
        self._current_text_parts = []
        self._tag_stack = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "")

        if "tgme_widget_message_wrap" in classes:
            self._in_msg_wrap = True
            self._current_dt = None
            self._current_text_parts = []
            self._tag_stack = []

        if self._in_msg_wrap:
            self._tag_stack.append(tag)
            if "tgme_widget_message_text" in classes and "js-message_reply_text" not in classes:
                self._in_text_div = True
            if tag == "time" and self._in_msg_wrap:
                self._in_time = True

    def handle_endtag(self, tag):
        if self._in_msg_wrap and self._tag_stack:
            self._tag_stack.pop()
            if tag == "div" and self._in_text_div:
                self._in_text_div = False
                # Mesaj tamamlandı
                text = "".join(self._current_text_parts).strip()
                text = re.sub(r'\s+', ' ', text)
                text = text.replace('&#036;', '$')
                text = text.replace('&#33;', '!')
                text = text.replace('&amp;', '&')
                text = text.replace('<br/>', '\n')
                text = text.replace('<br>', '\n')
                text = text.replace('&#39;', "'")
                if self._current_dt and text:
                    self.messages.append({
                        "datetime": self._current_dt,
                        "text": text
                    })
        if tag == "time":
            self._in_time = False

    def handle_data(self, data):
        if self._in_time and self._in_msg_wrap:
            # time etiketi datetime attribute'unda asıl değer var
            pass
        if self._in_text_div and self._in_msg_wrap:
            self._current_text_parts.append(data)

    def handle_entityref(self, name):
        if self._in_text_div and self._in_msg_wrap:
            self._current_text_parts.append(f"&{name};")


def fetch_channel_page():
    """Kanal sayfasını indirir."""
    req = urllib.request.Request(
        CHANNEL_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def extract_messages(html):
    """HTML'den mesajları çıkarır."""
    extractor = MessageExtractor()
    # time'ların datetime attribute'unu da çekmek için ek regex
    # Telegram HTML'inde: <time datetime="2026-07-09T09:44:54+00:00">
    time_matches = list(re.finditer(
        r'<time\s+[^>]*datetime="([^"]+)"', html
    ))
    
    extractor.feed(html)
    
    # time'ları extractor'daki mesajlarla eşleştir
    # Aslında daha basit bir yaklaşım: sadece HTML'den time + text çek
    return extractor.messages


def parse_messages_simple(html):
    """HTML'den time'ları ve mesaj metinlerini basit regex ile çıkarır."""
    # Her bir mesaj bloğunu bul
    # Telegram'da her mesaj: ... <time datetime="..."> ... <div class="tgme_widget_message_text ..."> ...
    
    msg_pattern = r'<time\s+[^>]*datetime="([^"]+)"[^>]*>.*?</time>.*?(?:<div\s+class="tgme_widget_message_text\s+js-message_text"\s+dir="auto">(.*?)</div>)'
    
    # Daha güvenilir: mesaj wrap'lerini bul
    blocks = re.split(r'<div\s+class="tgme_widget_message_wrap', html)[1:]  # ilk bölüm header
    
    messages = []
    for block in blocks:
        # datetime
        dt_match = re.search(r'<time\s+[^>]*datetime="([^"]+)"', block)
        if not dt_match:
            continue
        dt_str = dt_match.group(1)
        
        # text (reply text değil, ana mesaj text'i)
        text_match = re.search(
            r'<div\s+class="tgme_widget_message_text\s+js-message_text"\s+dir="auto">(.*?)</div>',
            block, re.DOTALL
        )
        if not text_match:
            continue
        
        raw_text = text_match.group(1)
        # reply text'ini ayıkla (eğer reply varsa, ilk text reply olabilir)
        # Reply içeren mesajlarda iki tane tgme_widget_message_text vardır
        # js-message_reply_text olanı atla
        if 'tgme_widget_message_reply' in block[:block.find('<div class="tgme_widget_message_text')]:
            # reply var, ikinci text'i bul
            all_texts = re.findall(
                r'<div\s+class="tgme_widget_message_text\s+js-message_text"\s+dir="auto">(.*?)</div>',
                block, re.DOTALL
            )
            if len(all_texts) > 1:
                raw_text = all_texts[1]  # reply değil, asıl mesaj
            else:
                raw_text = all_texts[0]
        
        # HTML entity'leri temizle
        text = raw_text
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)  # tüm HTML tag'lerini kaldır
        text = text.replace('&#036;', '$')
        text = text.replace('&#33;', '!')
        text = text.replace('&amp;', '&')
        text = text.replace('&#39;', "'")
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = '\n'.join(line.strip() for line in text.split('\n'))
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        if text:
            messages.append({
                "datetime": dt_str,
                "text": text
            })
    
    return messages


def is_newer(dt_str, last_dt_str):
    """dt_str, last_dt_str'den daha yeni mi?"""
    try:
        dt = datetime.fromisoformat(dt_str)
        last_dt = datetime.fromisoformat(last_dt_str)
        return dt > last_dt
    except (ValueError, TypeError):
        return True  # parse hatası varsa güvenli tarafta kal


def load_state():
    """State dosyasını yükler."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_state(last_datetime, last_message_id=None):
    """State dosyasını kaydeder."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    state = {"last_datetime": last_datetime}
    if last_message_id:
        state["last_message_id"] = last_message_id
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def format_message(msg):
    """Mesajı okunabilir formata dönüştürür."""
    dt = msg["datetime"]
    text = msg["text"]
    # Kısa tarih formatı
    try:
        dt_obj = datetime.fromisoformat(dt)
        date_str = dt_obj.strftime("%d %B %H:%M")
    except:
        date_str = dt
    
    # İlk satırı başlık olarak al
    first_line = text.split('\n')[0][:80]
    
    return f"[{date_str}] {first_line}"


def main():
    state = load_state()
    
    if state is None:
        # İlk çalıştırma: state dosyası yoksa sessiz çık
        # State dosyası elle oluşturulacak (en son mesaj datetime'ı ile)
        sys.exit(0)
    
    last_dt = state.get("last_datetime", "")
    
    html = fetch_channel_page()
    messages = parse_messages_simple(html)
    
    # Tarihe göre sırala (en eskiden en yeniye)
    messages.sort(key=lambda m: m["datetime"])
    
    new_messages = [m for m in messages if is_newer(m["datetime"], last_dt)]
    
    if not new_messages:
        sys.exit(0)  # sessiz
    
    # En yeniyi state'e kaydet
    latest_dt = max(m["datetime"] for m in messages)
    save_state(latest_dt)
    
    # Yeni mesajları yazdır
    for msg in new_messages:
        print(format_message(msg))
        print("---")


if __name__ == "__main__":
    main()
