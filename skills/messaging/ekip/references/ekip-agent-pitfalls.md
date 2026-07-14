# EKİP Agent Pitfalls (güncelleme: 7 Haz 2026)

## GLM-5.1 Haftalık Kota Tükenmesi (YENİ — 7 Haz 2026)

### Belirti
GLM-5.1 API çağrısına quota/rate-limit aşıldığına dair **açık hata mesajı** döner. Bu "seçici boş dönme" ve "timeout exit 28"den FARKLI bir hata modudur.

### Sebep
OpenCode Go üzerinden GLM-5.1'in haftalık kullanım kotası dolmuştur.

### Çözüm
- GLM-5.1'i limit sıfırlanana kadar TEKRAR DENEME.
- Hemen GPT-5.4-mini (port 19999) ile fallback yap:
  ```bash
  curl -s --max-time 45 http://127.0.0.1:19999/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-5.4-mini","messages":[...],"max_tokens":1500}'
  ```

### Karşılaştırma Tablosu

| Hata Modu | Belirti | GLM-5.1 Tekrar Dene? |
|-----------|---------|----------------------|
| Seçici boş dönme | content boş, 1 byte yanıt, finish_reason yok | ✅ Dene |
| Timeout (exit 28) | curl 60sn timeout | ✅ Dene |
| **Quota exhausted** | **Açık hata mesajı, limit aşıldı** | **❌ DENEME — bugün çalışmaz** |

## Görsel Üretimi Fallback (LinkedIn Pipeline)

### Belirti
Pollinations image generation (kontext model) `/tmp/pk.txt` bulamazsa veya HTTP 401/502 dönerse.

### Çözüm
1. Görseli atla
2. Metin post ile devam et
3. Post'u arşive kaydet
4. Edel'e görselsiz sun, "sonradan eklenebilir" notuyla

### Ön Kontrol
```bash
if [ ! -f /tmp/pk.txt ]; then
    echo "UYARI: /tmp/pk.txt yok. Görsel atlanıyor."
fi
```
