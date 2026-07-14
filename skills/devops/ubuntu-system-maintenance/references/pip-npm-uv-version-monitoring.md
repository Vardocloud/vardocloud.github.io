# Pip / NPM / UV Araçları — Sürüm Takibi

> Keşif tarihi: 29 Haz 2026 — Edel'in "codegraph gibi yazılımları kontrol edip güncellemeleri takip eden mekanizma var mı?" sorusu üzerine.

## Boşluk: Otomatik Güncelleme Takibi Yok

Sistemde pip, npm ve uv ile kurulu araçların (codegraph-mcp, notebooklm-mcp-cli, pollinations-mcp, soniox-docs MCP vb.) güncellemelerini otomatik kontrol eden bir mekanizma **henüz yok**. Apt paketleri `unattended-upgrades` ile güncellenir ama pip/npm/uv araçları bu kapsamın dışında kalır.

## Etkilenen Araçlar

| Araç | Yönetici | Güncelleme kontrolü | 
|------|----------|---------------------|
| codegraph-mcp | npm (global) | ❌ |
| notebooklm-mcp-cli | uv + pip | ❌ |
| pollinations-mcp | npm? binary? | ❌ |
| soniox-docs MCP | (bilinmiyor) | ❌ |

## Manuel Kontrol Komutları

```bash
# npm global araçlar
npm outdated -g 2>/dev/null

# uv tool'ları
uv tool list 2>/dev/null

# pip araçlar (sisteme yüklü olanlar)
pip list --outdated 2>/dev/null

# notebooklm-mcp-cli özel
pip show notebooklm-mcp-cli 2>/dev/null | grep Version
```

## Neden Önemli?

- 29 Haz 2026: codegraph MCP server'ı process olarak çalışıyor ama Hermes client'ı "unreachable" hatası alıyor. Güncel olmayan bir sürümün bağlantı sorununa yol açması olası.
- Yeni özellikler, bug fix'leri ve güvenlik yamalarını kaçırma riski.
- Bağımlılık sürüm uyumsuzluklarından kaynaklanan gizli hatalar.

## Öneri

Haftalık bir cron job ile:
1. Tüm yüklü pip/npm/uv araçlarının sürümlerini kontrol et
2. Yeni sürüm varsa Home kanalına bildir (manuel update kararı)
3. Kritik güvenlik fix'leri için ayrıca alert
