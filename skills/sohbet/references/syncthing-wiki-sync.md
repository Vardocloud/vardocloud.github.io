# Syncthing Wiki Sync (31 Mayıs 2026)

## Amaç
Sunucudaki `~/wiki/` klasörünü Edel'in Windows/telefonuna anlık senkronize etmek.
Logseq veya Obsidian ile graph görünümünde okumak için.

## Sunucu
- Syncthing 1.27.2 (apt), user systemd service
- Device ID: `KA34NKW-G7E7IUV-O7WGWPR-NIBM6UL-WGQZE44-SBFDWSQ-S3MEAFZ-5XA6ZQN`
- Device name: `hermes`
- Klasör: `vanitas-wiki` → `/home/ubuntu/wiki`

## Edel Windows Kurulumu
1. https://syncthing.net/downloads/ → Windows 64-bit
2. syncthing.exe çalıştır → `127.0.0.1:8384`
3. Add Remote Device → yukarıdaki Device ID'yi yapıştır
4. Add Folder → Folder ID: `vanitas-wiki`, Path: `C:\Users\Edel\wiki`
5. Hermes Server'ı Share with devices'a ekle

## Logseq
- Syncthing ile gelen `~/wiki/` klasörünü Logseq'te vault olarak aç
- Graph görünümü: interaktif, düğümler tutup çekilebilir, yan paneller
