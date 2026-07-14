# Codegraph MCP Server — Reinstall & Crash Recovery

## Reinstall Procedure (root yetkisi yoksa)

1. Eski kurulumu temizle: `rm -rf ~/.codegraph ~/.hermes/.codegraph`
2. User-level npm'e kur: `npm install -g @astudioplus/codegraph-mcp`
3. Config'i güncelle:
   - `hermes config set mcp_servers.codegraph.command /home/ubuntu/.npm-global/bin/codegraph-mcp`
   - `hermes config set mcp_servers.codegraph.timeout 600`
4. Test et: `hermes mcp test codegraph` → 42 tool, 764ms

## Crash Recovery

MCP server index çağrısında timeout yerse:
- `hermes mcp test <server>` başarılı olsa bile session MCP client'ı crash kalır
- Tool'lar `ClosedResourceError` veya "unreachable after N failures" döner
- **Çözüm: Yeni session/konsuşma açmak** — gateway restart yetmez
- İndex timeout'u önlemek için: timeout≥600sn, workspace küçük, exclude ekle

## Data Dizinleri
- `/home/ubuntu/.codegraph/` — graph.db, embedding cache
- `/home/ubuntu/.hermes/.codegraph/` — proje config
