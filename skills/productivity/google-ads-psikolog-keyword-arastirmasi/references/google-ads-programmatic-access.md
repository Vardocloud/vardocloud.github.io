# Google Ads Programatik Erişim

Google Ads hesabına programatik erişim seçenekleri ve karşılaştırma.

## Seçenek 1: Google Ads MCP Server (Resmi)

- **Repo:** https://github.com/googleads/google-ads-mcp
- **Lisans:** Apache 2.0 (açık kaynak)
- **Yıldız:** 629⭐
- **Durum:** READ-ONLY (resmi dokümanda belirtilmiş)
- **Dil:** Python (FastMCP)
- **Transport:** stdio (MCP)

### Tools (3 adet)
1. `search` — GAQL sorguları çalıştırır
2. `list_accessible_customers` — yetkili müşteri hesaplarını listeler
3. `get_resource_metadata` — API resource metadata'sını döndürür

### Gerekenler
- Google Cloud Project ID
- Google Ads Developer Token (22 karakter)
- OAuth Client ID + Client Secret (Google Cloud Console'dan)
- Google Ads Müşteri ID

### Kurulum
```bash
pipx run --spec git+https://github.com/googleads/google-ads-mcp.git google-ads-mcp
```

### Hermes Config (config.yaml)
```yaml
mcp_servers:
  google-ads-mcp:
    command: pipx
    args:
      - run
      - --spec
      - git+https://github.com/googleads/google-ads-mcp.git
      - google-ads-mcp
    env:
      GOOGLE_PROJECT_ID: "[PROJECT_ID]"
      GOOGLE_ADS_DEVELOPER_TOKEN: "[DEVELOPER_TOKEN]"
      GOOGLE_ADS_MCP_OAUTH_CLIENT_ID: "[CLIENT_ID]"
      GOOGLE_ADS_MCP_OAUTH_CLIENT_SECRET: "[CLIENT_SECRET]"
      GOOGLE_ADS_MCP_BASE_URL: "http://localhost:8080"
    enabled: true
```

### Auth
- OAuth 2.0 veya Service Account
- Developer token + OAuth credentials ortam değişkeni olarak verilir
- İlk çalıştırmada OAuth consent sayfası açar (bir kereye mahsus)

## Seçenek 2: Composio Connect

- **Site:** https://composio.dev
- **Pricing:** Free (20K call/ay), Pro ($29/ay, 200K call), Business ($229/ay, 2M call)

### Tools (9 adet)
1. AddOrRemoveToCustomerList
2. Create customer list
3. Get Campaign By Id
4. Get campaign by name
5. Get customer lists
6. List Accessible Customers
7. Mutate Ad Groups (create/update/remove)
8. Mutate Campaigns (create/update/remove)
9. Search Stream GAQL

### Auth
- Composio üzerinden OAuth (token yönetimi Composio'da)
- Google Ads hesabına tek seferlik izin

### Kurulum
```bash
# 1. Composio CLI kurulumu (resmi kurulum scripti ile)
# https://composio.dev/hermes adresindeki talimatlar izlenir

# 2. Google Ads bağlantısı
composio connect google-ads

# 3. Alternatif: MCP config (config.yaml)
# mcp_servers:
#   composio:
#     url: "https://connect.composio.dev/mcp"
#     headers:
#       x-consumer-api-key: "[COMPOSIO_KEY]"
```

## Karar Tablosu

| Özellik | Google Ads MCP Server | Composio |
|---------|----------------------|----------|
| Fiyat | 🆓 Ücretsiz | Free / $29-229/ay |
| Yazma Desteği | ❌ Hayır (read-only) | ✅ Evet |
| Tool Sayısı | 3 | 9 |
| Kurulum Süresi | ~15 dk (OAuth + token) | ~5 dk (Composio OAuth) |
| Kontrol | Tam (kendi sunucun) | Üçüncü taraf platform |
| Veri Gizliliği | Veriler Google'da kalır | Composio üzerinden geçer |
| Açık Kaynak | ✅ Evet (Apache 2.0) | ❌ Hayır |
| Ek Özellikler | Sadece Google Ads | 1000+ uygulama entegrasyonu |

## Kullanım Senaryoları

### Sadece İzleme ve Raporlama ✅ Google Ads MCP Server
- Günlük performans raporu
- Haftalık harcama analizi
- Campaign bazında metrikler
- Anomali tespiti (ani harcama artışı)
- GAQL ile özel sorgular

### Reklam Yönetimi (Campaign CRUD) → Composio
- Campaign açma/kapama
- Bütçe değiştirme
- Ad group oluşturma/düzenleme
- Customer list yönetimi
- Teklif ayarlama

## Reklamcı AI Tasarımı

İki yaklaşım:

### Yaklaşım 1: Vanitas + MCP Server (Mevcut)
- Google Ads MCP server config'e eklenir
- Vanitas doğrudan GAQL sorguları çalıştırır
- Cron job ile günlük/haftalık raporlama
- Edel istediği an "harcama ne durumda?" diye sorabilir

### Yaklaşım 2: Kanban Worker Profili (İzole AI)
- Ayrı bir Kanban profili oluşturulur (ör. "google-ads-analist")
- Profile Google Ads MCP server + özel skill tanımlanır
- Periyodik task'lerle kampanya takibi yapar
- Anomali tespitinde Vanitas'a rapor gönderir

Yaklaşım 1 şimdilik yeterli. İhtiyaç artarsa Yaklaşım 2'ye geçilir.
