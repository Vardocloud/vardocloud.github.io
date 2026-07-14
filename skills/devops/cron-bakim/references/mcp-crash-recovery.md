# MCP Server Crash Recovery

Bu referans, bir MCP server crash yediğinde uygulanacak teşhis ve kurtarma adımlarını içerir.

## Belirtiler

- `ClosedResourceError` — MCP server process'i düşmüş
- `MCP server 'X' is unreachable after N consecutive failures` — auto-retry tükenmiş
- Araç çağrısı önce timeout, sonra unreachable

## Kurtarma

1. **Test:** `hermes mcp test <server>` — yeni bir connection açar (geçicidir)
2. **Zombie temizlik:** `ps aux | grep <server>` ile eski process'leri bul, `pkill -f <server>` ile öldür
3. **Kalıcı çözüm:** Yeni bir agent session'ı (yeni Telegram konuşması) başlatmak veya `hermes gateway restart`

⚠️ `hermes mcp test` geçici bir connection'dır. Agent session'ındaki MCP araçları etkilenmez.

## Önleme

Uzun MCP işlemleri (index_directory) için timeout'u artır:
```
hermes config set mcp_servers.<server>.timeout 600
```

## args format pitfall

`hermes config set mcp_servers.X.args '["a", "b"]'` YAML list'ini string'e çevirir:
```yaml
# ❌ hatalı
args: '["a", "b"]'
# ✅ doğru
args:
- a
- b
```
Düzeltme: `hermes config set` ile boş string ata, sonra Python ile config.yaml'ı düzelt.
