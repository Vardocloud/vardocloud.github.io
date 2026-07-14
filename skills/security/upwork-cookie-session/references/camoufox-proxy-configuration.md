## Camoufox Proxy Configuration

### Proxy Options
- **WARP+ proxy** (`127.0.0.1:1080` SOCKS5) — partially works for navigation but Cloudflare blocks WARP IP ranges on form submit
- **Proxychains4** — successfully routes Camoufox through WARP:
  ```bash
  sudo apt-get install proxychains4
  # /etc/proxychains4.conf: replace socks4 line with socks5
  sudo sed -i 's/socks4.*127.0.0.1.*9095/socks5\t127.0.0.1 1080/' /etc/proxychains4.conf
  # Run camoufox through proxychains
  cd ~/.hermes && proxychains4 -q node upw_session_refresh.cjs
  ```
- **Camoufox + proxychains4 ile job search:** `~/.hermes/upw_job_search.cjs` script'i mevcut (2026-06-14). Cookie'leri load edip WARP üzerinden Camoufox açar. Çalıştırma:
  ```bash
  cd ~/.hermes && proxychains4 -q node upw_job_search.cjs
  ```
  ⚠️ Job search sayfaları (`freelance-jobs/`, `search/jobs/`) Cloudflare challenge gösterir — WARP IP'si bu sayfalarda bot algılanır. Ana sayfa (`/nx/create-profile/*`) çalışır.
- Residential proxy NOT tested — would need BrightData/IPRoyal etc.

### Proxychains4 Pitfalls
- `geoip: false` zorunlu — aksi halde Camoufox IP servisine bağlanamaz
- `-q` flag sessiz mod (gereksiz proxy loglarını gizler)
- proxychains4'ün DNS proxy özelliği (proxy_dns) WARP üzerinden DNS çözümlemesi yapar
- WARP IP'si Cloudflare'e ait olduğu için Cloudflare korumalı sayfalarda challenge alınabilir