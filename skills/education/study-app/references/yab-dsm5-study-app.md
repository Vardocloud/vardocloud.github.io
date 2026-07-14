# YAB DSM-5 Study App — Reference Implementation (2 July 2026)

**Konu:** Yaygın Anksiyete Bozukluğu DSM-5 Tanı Kriterleri
**Hedef:** Klinik psikoloji çalışması (KP YL hazırlık)
**İçerik Kaynağı:** NotebookLM BDT notebook'u (256 kaynak)

## App Yapısı

```
┌─ HEADER ──────────────────────────┐
│ 🧠 YAB · DSM-5                   │
│ Yaygın Anksiyete Bozukluğu        │
├─ NAV ─────────────────────────────┤
│ [📖 Kriterler]  [❓ Quiz]         │
├─ BODY ────────────────────────────┤
│                                    │
│  ┌─ TIP KUTUSU ──────────────┐    │
│  │ ⭐ İpucu: "beynim susmuyor"│    │
│  └────────────────────────────┘    │
│                                    │
│  ┌─ KART A (Aşırı Kaygı) ────┐    │
│  │ 🔵 A  Aşırı Kaygı     ▾   │    │
│  │     En az 6 aydır...       │    │
│  │ ────────────────────────   │    │
│  │ [detay içeriği — açılır]   │    │
│  └────────────────────────────┘    │
│                                    │
│  ┌─ KART B (Kontrol Güçlüğü) ┐    │
│  │ 🟢 B  Kontrol Güçlüğü  ▾   │    │
│  └────────────────────────────┘    │
│  ... (A-F, 6 kart)                │
│                                    │
├─ QUIZ ────────────────────────────┤
│  ┌─ SKOR BAR ────────────────┐    │
│  │ 📊 [████████░░] 3/5  🔄   │    │
│  └────────────────────────────┘    │
│                                    │
│  ┌─ SORU 1 ──────────────────┐    │
│  │ Soru 1/5                   │    │
│  │ YAB için süre kriteri?     │    │
│  │                            │    │
│  │ A. 1 ay                    │    │
│  │ B. 3 ay                    │    │
│  │ C. 6 ay  ← [yeşil]        │    │
│  │ D. 12 ay                   │    │
│  │                            │    │
│  │ ✅ Doğru! A kriteri...     │    │
│  └────────────────────────────┘    │
│  ... (5 soru)                     │
│                                    │
│  ┌─ COMPLETE BADGE ───────────┐   │
│  │ 🎉 Tebrikler! 5/5 Mükemmel │   │
│  └────────────────────────────┘   │
└────────────────────────────────────┘
```

## Quiz Soruları (Türkçe)

| # | Soru | Doğru Cevap |
|---|------|-------------|
| 1 | YAB tanısı için kaygı ve kuruntunun en az ne kadar süredir var olması gerekir? | 6 ay (C) |
| 2 | YAB'da en ayırt edici bulgu hangisidir? | Endişeyi kontrol edememe (B) |
| 3 | Aşağıdakilerden hangisi YAB'ın C kriterindeki 6 belirtiden biri DEĞİLDİR? | Panik atak (B) |
| 4 | Sadece çok kahve içtiğinde kaygı yaşayan birine hangi tanı konur? | Kafeinin yol açtığı kaygı bozukluğu (C) |
| 5 | Hangi durum YAB'ın ayırıcı tanısında yer almaz? | Major Depresyon (C) |

## Teknik Detaylar

- **Dosya:** 15.2 KB, tek HTML
- **JS:** ~50 satır vanilla JS (tab switching, card toggle, quiz logic, score tracking)
- **CSS:** ~80 satır (dark tema, gradient, responsive, kart/quiz stilleri)
- **Renkler:** #0f0f1a bg, #1a1a2e kart, #a78bfa mor, #6ee7b7 yeşil
- **Responsive:** 480px breakpoint
- **Font:** System font stack (-apple-system, BlinkMacSystemFont, Segoe UI)
