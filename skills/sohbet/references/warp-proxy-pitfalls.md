# WARP SOCKS5 API Engeli

WARP SOCKS5 proxy'si (warp:1080) şu servisleri ENGELLİYOR:

| Servis | Engel | Çözüm |
|--------|-------|-------|
| Google OAuth | Connection reset | `ALL_PROXY=""` |
| Gmail API | Connection reset | `ALL_PROXY=""` |
| Google Calendar | Connection reset | `ALL_PROXY=""` |
| LinkedIn API | Connection reset | `ALL_PROXY=""` |
| PyPI (pip install) | Connection reset | `ALL_PROXY=""` |
| PubMed Entrez | Connection reset | `ALL_PROXY=""` |

**Kalıcı çözüm:** Her harici API çağrısında `ALL_PROXY=""` prefix'i.
WARP sadece Google/YouTube tarayıcı erişimi için gerekli.
API çağrıları Oracle Cloud IP'sinden zaten çalışıyor.

**Keşfedildi:** 29 Mayıs 2026, Vanitas Dönüşümü sırasında.
