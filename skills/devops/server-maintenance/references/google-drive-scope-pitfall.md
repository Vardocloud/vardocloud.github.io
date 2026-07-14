# Google Drive Upload — OAuth Scope Pitfall

5 Haz 2026'da tespit edildi: Bu sunucudaki `google_token.json` sadece Calendar ve Gmail scope'larına sahip. 
Dosya yükleme (multipart upload) `drive.file` scope'u olmadan başarısız.

## Hata

```json
{"error": {"code": 403, "status": "PERMISSION_DENIED",
 "details": [{"reason": "ACCESS_TOKEN_SCOPE_INSUFFICIENT"}]}}
```

## Çözüm

1. Token'ı iptal et: `python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --revoke`
2. `--services calendar,gmail,drive` ile yeniden auth
3. Auth URL'sini onayla, kodu değiştir

## Alternatif

- `drive.file` scope'u yeterli — tam Drive erişimi gerekmez
- `gws` CLI: `pip install gws` (daha geniş kapsam)

## Multipart Upload (Drive API v3)

```python
# ALL_PROXY="" zorunlu — Google API'leri WARP proxy üzerinden çalışmaz
metadata = {"name": "dosya.tar.gz", "mimeType": "application/gzip"}
boundary = "boundary_hermes"
body = f"--{boundary}\r\nContent-Type: application/json\r\n\r\n{json.dumps(metadata)}\r\n--{boundary}\r\nContent-Type: application/gzip\r\n\r\n".encode() + file_bytes + f"\r\n--{boundary}--\r\n".encode()
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": f"multipart/related; boundary={boundary}"}
resp = requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart", headers=headers, data=body)
```
