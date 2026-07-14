# Sunucu Temizlik Workflow

Analist + NotebookLM ile sistematik temizlik. EKİP kullanır.

## Adımlar

### 1. Tara
```bash
df -h / && du -sh /home/ubuntu/* | sort -rh | head -20
find /home/ubuntu -type f -size +10M | head -30
ls -la ~/.hermes/scripts/
du -sh ~/.hermes/logs ~/wiki
```

### 2. Analist'e Kategorize Ettir
curl ile Analist'e (GLM-5.1, port 19998) dosya listesini ver, her biri için SIL/SAKLA/NB kararı iste.

### 3. NB'ye Taşı (SAKLA kararı olanları atla)
- `mcp_notebooklm_mcp_notebook_create` ile uygun başlıkta notebook aç
- `mcp_notebooklm_mcp_source_add` ile dosyaları ekle (source_type=file)
- `mcp_notebooklm_mcp_tag` ile etiketle

### 4. Temizle
- SIL kararlıları `rm -rf`
- NB'ye taşınanları `rm -rf`
- SAKLA kararlıları ve kritik altyapıyı (context-mode, hermes, proxy) elleme
- npm cache: `npm cache clean --force`
- Eski loglar: `find ~/.hermes/logs -type f -mtime +7 -delete`

### 5. Son Kontrol
```bash
df -h / && du -sh /home/ubuntu/* | sort -rh | head -10
```

## Önemli
- context-mode, hermes-agent, proxy'ler ASLA silinmez
- Büyük dizinlerde (100MB+) önce Edel'e sor
- NB'ye taşınan dosyaların teyitini al, sonra yerelden sil
