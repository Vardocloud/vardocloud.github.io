# BWS'den Frontend'e Güvenli API Key Servis Etme Pattern'i

## Problem
Frontend (browser) bir API key'e ihtiyaç duyar (örn: Soniox, Deepgram). Key'i `.env` veya `config.js`'de hardcode etmek güvenlik riskidir. Frontend'in doğrudan BWS'ye erişmesi mümkün değildir.

## Çözüm: Backend Proxy Pattern

```
BWS (Bitwarden Secrets Manager)
  ↓ bws secret read
Backend (server.mjs) → `/api/config` endpoint
  ↓ HTTP GET (same-origin)
Frontend (index.html)
  ↓ SonioxClient({ apiKey })
Soniox WebSocket API
```

### Backend (server.mjs)

```javascript
const { execSync } = require('child_process');

function getBwsSecret(keyName) {
  try {
    const cmd = `bws secret read "SONIOX_API_KEY"`;
    return execSync(cmd, { encoding: 'utf-8' }).trim();
  } catch (e) {
    console.error(`BWS secret '${keyName}' okunamadı:`, e.message);
    return null;
  }
}

app.get('/api/config', (req, res) => {
  const sonioxKey = getBwsSecret('SONIOX_API_KEY');
  if (!sonioxKey) return res.status(500).json({ error: 'Key not found' });
  res.json({ sonioxKey });
});
```

### Frontend (index.html)

```javascript
let sonioxKey = null;

async function loadConfig() {
  const resp = await fetch('/api/config');
  const config = await resp.json();
  sonioxKey = config.sonioxKey;
}

// Kullanım
const client = new SonioxClient({
  apiKey: sonioxKey,
  model: 'stt-rt-v5',
  language: 'tr',
  sampleRate: 16000
});
```

## Avantajlar

- **Key asla git'e gitmez** — `.env` dosyası yok, hardcode yok
- **BWS yetkisiz erişime kapalı** — sadece Hermes container'ından erişilebilir
- **Tek noktadan yönetim** — key değişirse sadece BWS'de güncelle, tüm frontend'ler anında alır
- **Audit log** — BWS tüm secret okumalarını loglar

## Uyarılar

- `/api/config` endpoint'i **kimlik doğrulamasız** — eğer tüm dünyaya açıksa, key herkes tarafından görülebilir. Cloudflare tunnel geçici URL olduğu için risk düşüktür.
- Üretim ortamında rate-limit veya IP kısıtlaması eklenmeli
- Key browser'a geldikten sonra browser memory'sinde kalır, sayfa yenilenince kaybolur (hardcode değil)
