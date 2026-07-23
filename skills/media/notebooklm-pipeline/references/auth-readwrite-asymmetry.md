# Auth Read/Write Asymmetry (8 Haz 2026)

`nlm login --check` "Authentication valid!" dese bile, yazma işlemleri farklı bir auth seviyesi gerektirebilir. Google yazma token'ını okuma token'ından ayrı doğrular.

## Operation Types

| Type | Operations | Reliability |
|------|-----------|-------------|
| **Read (✅ genelde çalışır)** | notebook_list, notebook_get, notebook_query, source_get_content, studio_status | Yüksek — auth stale olsa bile çalışabilir |
| **source_add (⚠️ sınırlı)** | URL ve text source ekleme | Auth tamamen ölü olduğunda (stale değil, kopuk) başarısız olabilir |
| **Write (❌ bloke olabilir)** | studio_create, source_delete, bazı notebook_create | Düşük — ayrı write token'ı gerekir |

## Doğrulama Prosedürü

```bash
nlm login --check                           # Auth var mı?
nlm report create NOTEBOOK_ID --format "Briefing Doc" --confirm -y  # Write yetkisi var mı?
```

PERMISSION_DENIED (API code 7) alırsan yazma kapalıdır.

## Çözümler

### Owned Notebook
`notebook_list`'te `ownership: "owned"` olan notebook'larda CLI write işlemleri çalışır. `shared_with_me` olanlarda PERMISSION_DENIED alınır.

### Manuel Cookie Export (En Kesin)
Edel kendi tarayıcısından (Google'ın güvendiği bir IP'den) cookie export edip atarsa, direkt Chrome profiline yazılır.

### Best-Effort Pattern
Wiki asıl teslimat, NotebookLM bonus. NotebookLM başarısız olursa pipeline'ı bloke etme.
