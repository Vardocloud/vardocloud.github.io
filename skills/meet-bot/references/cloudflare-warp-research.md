# Cloudflare WARP — Oracle Cloud Google Engeli Çözüm Araştırması

27 Mayıs 2026'da Google'ın Oracle Cloud IP'lerini engellemesine karşı Cloudflare WARP çözümü araştırıldı.

## Motivasyon

Google servisleri (YouTube, Meet) Oracle Cloud IP'lerinden gelen otomatik trafiği engelliyor:
- `"Sign in to confirm you're not a bot"` (YouTube)
- `"Couldn't sign you in — This browser or app may not be secure"` (Meet)

## Araştırılan Çözüm: docker-warp-socks

**Repo:** `ghcr.io/mon-ius/docker-warp-socks` — Cloudflare WARP'i SOCKS5 proxy olarak sunan Docker konteyneri.

### v5 (güncel)

- ARM64 desteği var, tek komutla kurulum
- **WARP+ lisans desteği YOK** — "Due to the Cloudflare Policy"
- WireGuard handshake başarılı, DNS çalışıyor, SOCKS5 bağlantısı kuruluyor
- **Ancak TCP veri akışı zaman aşımına uğruyor** — free WARP Oracle Cloud'da throttling yapıyor
- Sonuç: ❌ ÇALIŞMADI

### v4 (eski)

- WARP+ lisans desteği var
- Artık güncellenmiyor, denenmedi

## Alternatif: wgcf

`wgcf` ile doğrudan WireGuard konfigürasyonu oluşturup WARP+ lisansını gömmek.

## Diğer Çözümler

| Çözüm | Maliyet | Durum |
|-------|---------|-------|
| Cloudflare WARP (wgcf + WARP+) | $0 (+WARP+ üyeliği) | Denenmedi |
| Browserbase (Hermes plugin) | API ücretli | Cloud tarayıcı, stealth |
| Residential proxy (Evomi) | $0.49/GB | Kesin çalışır |
| Tailscale + ev IP'si | $0 | Evde cihaz gerekir |
| Cookie export | $0 | Manuel, süreli |
