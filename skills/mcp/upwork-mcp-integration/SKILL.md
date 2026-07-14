---
name: upwork-mcp-integration
description: "Upwork MCP Server kurulumu — Developer Portal uygulama oluşturma, OAuth2 token, MCP Server entegrasyonu."
version: 1.0.0
metadata:
  hermes:
    tags: [upwork, mcp, freelance, integration]
    category: mcp
    related_skills: [native-mcp, sensitive-data-pipeline]
---

# Upwork MCP Integration

Upwork freelance marketplace için MCP Server entegrasyonu. İş arama, proposal yönetimi, sözleşme takibi, mesajlaşma.

## MCP Server

fieldjoshua/upwork-mcp-server (GitHub, v1.0.0). OAuth2 access token gerektirir.

## Kurulum Adımları

### 1. Developer Portal'da Uygulama Oluştur

Kullanıcı kendi tarayıcısından https://www.upwork.com/developer/keys adresine gider:

| Alan | Değer |
|---|---|
| Title | Vanilla |
| Callback URL | http://localhost |
| Description | Personal AI assistant integration for Upwork automation |
| API Usage | 200/hour |
| Rotation Period | 12 Months |
| Permissions | Full access |

Oluşturulan access token → Bitwarden'a kaydet.

### 2. Repo'yu Kur

Repoyu clone et, npm install + build yap, çalıştığından emin ol.

### 3. MCP Server'ı Aktive Et

Token'ı `UPWORK_ACCESS_TOKEN` env variable olarak ayarla, MCP server'ı Hermes config'inde tanımla, gateway'i restart et.

## Bot Detection

**UPDATE (June 2026):** Cloudflare blocks ALL direct access from Oracle Cloud datacenter IPs — not just browser automation. GET requests, POST requests, RSS feeds, and curl all return Cloudflare challenge pages. No browser engine (Chrome, Firefox, Camoufox, nodriver, puppeteer-real-browser) can bypass this IP-level block.

**Çözüm:** Developer Portal'a kullanıcı kendi tarayıcısından girer, Vanitas rehberlik eder. OAuth token ile API kullanılır. API endpoint (`api.upwork.com`) farklı altyapı kullanır ve Cloudflare engeli yoktur.

## Kullanıcı Rehberliği

Developer Portal İngilizce arayüzü:
- Her alan için Türkçe net talimat ver
- Neden o değerin seçildiğini açıkla
- Kararsız kalacağı noktalarda alternatif sun

## Güvenlik

- Access token → Bitwarden (asla düz metin konuşmada)
- Upwork kullanıcı bilgileri: Bitwarden'da www.upwork.com
- Alias: Vanilla (Vanitas değil)
