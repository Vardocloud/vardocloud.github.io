# NotebookLM Notebook ID'leri

## Hedef Notebook'lar

### 🛠️ Tech Tools Updates
- **ID:** `e263e756-c97f-440a-9f14-dd461ae894eb`
- **Kullanım:** Skool tarama özetleri, topluluk aktivitesi, post metadata
- **İçerik tipi:** text (özet), URL (post linki)

### 🎬 Medya Öğrenme (Reels)
- **ID:** `6ea985e1-aef3-4c6a-ba0b-fd80b5da32e6`
- **Kullanım:** YouTube transcript'leri, video içerik analizi
- **İçerik tipi:** text (transcript), URL (video)

## Kaynak Başlık Formatları

| İçerik Tipi | Format | Örnek |
|-------------|--------|-------|
| Günlük tarama özeti | `Skool — [TOPLULUK ADI] — [TARİH] Günlük Tarama` | `Skool — Yapay Zekâdan Gelire — 2026-06-07 Günlük Tarama` |
| Tek post (YouTube yok) | `Skool — [TOPLULUK] — [POST BAŞLIĞI]` | `Skool — Yapay Zekâdan Gelire — Podcast Otomasyon Videosu` |
| YouTube transcript | `YouTube — [VIDEO BAŞLIĞI] — [KAYNAK TOPLULUK]` | `YouTube — Claude 4 Opus Tanıtım — Yapay Zekâdan Gelire` |
| Topluluk erişim sorunu | `Skool — [TOPLULUK] — Erişim Sorunu — [TARİH]` | `Skool — Yapay Zeka Sistemleri — Erişim Sorunu — 2026-06-07` |

## Ekleme Yöntemi

### Ön Koşul: NotebookLM Auth Kontrolü (HER ÇALIŞMADA)

NotebookLM auth'u kontrol etmeden kaynak eklemeye başlama — auth stale olabilir:

```python
# 1. Auth durumunu kontrol et
mcp__notebooklm_mcp__server_info()
# auth_status = "stale" veya "not_configured" ise yenileme gerek

# 2. Auth yenile
# terminal("python3 ~/.nlm/refresh_cookies.py")
# Bu script headless CDP ile auth'u dener, başarısız olursa kullanıcı manuel login ister
# Çıktıda "Auth OK" veya "Manual login needed" ara

# 3. Tekrar kontrol et
mcp__notebooklm_mcp__server_info()
# auth_status = "configured" olmalı
```

**Not:** `refresh_cookies.py` her zaman çalıştırılabilir — auth zaten geçerliyse zarar vermez (63 cookies döner). Güvenli yenileme.

### Text tabanlı kaynak (özet, transcript)

```python
mcp__notebooklm_mcp__source_add(
    notebook_id="e263e756-c97f-440a-9f14-dd461ae894eb",
    source_type="text",
    text="<içerik markdown veya düz metin>",
    title="<başlık formatına göre>",
    wait=True,       # Cron'da kaynağın işlenmesini bekle — wait=False (varsayılan)
)                    # ready=false dönebilir ve cron bitince kaynak işlenmemiş kalır
```

### URL tabanlı kaynak (post linki, video linki)

```python
mcp__notebooklm_mcp__source_add(
    notebook_id="e263e756-c97f-440a-9f14-dd461ae894eb",
    source_type="url",
    url="https://www.skool.com/yapay-zekadan-gelire/podcast-otomasyon-videosu",
    title="<başlık formatına göre>"
)
```

## Çift Kayıt Önleme

NotebookLM kaynakları otomatik tekilleştirilmez. Aynı post birden fazla cron çalışmasında işlenebilir.

**Pratik kurallar:**

- **Aynı gün aynı post** → tekrar ekleme (önceki tarama zaten var, sadece özet güncelle)
- **Farklı gün aynı post** → yeni başlıkla eklenebilir (tarih başlıkta zaten var)
- **Güncelleme** → yeni kaynak aç, eskisini silme (geçmiş korunur)

**Başlık karşılaştırma:** Kaynak başlığı tam olarak aynıysa → atla. Tarih/numara içeriyorsa farklı kabul et.

## Rapor Formatı

Edel'e gönderilecek kısa Türkçe rapor:

```
🤖 Skool Gündem — [Tarih]
📝 X yeni post işlendi, Y video transcript çıkarıldı
💡 Öne çıkan: [1 cümle]
```

Erişilemez topluluk varsa ek satır:

```
⚠️ [Topluluk adı] erişilemez (PEND/BANNED/404)
```
