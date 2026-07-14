# Project State Audit — 1 Temmuz 2026

Cross-session session_search + filesystem audit of the Vanitas Voice project.

## Dosyalar (Gerçek Durum)

| Dosya | İçerik | Durum |
|-------|--------|-------|
| `vanitas_ses.py` | v11: soniox-python SDK, PCM-based dual-path (Groq + Hermes) | ✅ Current, tested |
| `vanitas_ses_v12.py` | v12: soniox-js arch, text-only WS, Edge TTS | ❌ Untested |
| `vanitas_ses_v11_backup.py` | v11 backup | ✅ |
| `vanitas_ses_v10.10_backup.py` | v10.10 backup | ✅ |
| `vanitas_hermes_proxy.py` | Proxy :8767 → Hermes :8642 | ✅ |
| `voiceprint_enroll.py` | MFCC-based voice enrollment | ✅ Script hazır |
| `edel_voiceprint.npy` | Ses parmak izi | 📁 Var, kullanılmıyor |
| `edel_voiceprint.json` | Metadata | 📁 Var |
| `~/vanitas-web/` | Next.js UI (Stage 3) | ❌ **YOK — hiç kurulmadı** |
| `v12-stage3-plan.md` | Plan | ✅ Yazıldı |
| `soul_core.md` | 336B compressed prompt | ✅ |
| `memory_index.json` | Flat string list | ✅ |
| `.groq_key` | Groq API key | ✅ |

## Skill'deki Hatalar (Şimdi Fix'lendi)

1. ~~"Current (v13)"~~ → v13 planlandı, hiç build edilmedi
2. ~~"Also current (v12)"~~ → v12 yazıldı, test edilmedi
3. ~~"✅ CURRENT (UI)"~~ v13 tabloda → ❌ Planned
4. ~~"✅ CURRENT (API)"~~ v12 tabloda → ⚠️ Written (untested)
5. ~~"Stage 3 ✅ COMPLETED"~~ → ❌ Planned — `vanitas-web/` yok
6. ~~"Priority: Stage 3 ✅"~~ → ❌ Planned
7. ~~"Key Files: vanitas_ses.py CURRENT text-only"~~ → v11, PCM-based

## TTS Araştırma Durumu

| TTS | Durum | Yorum |
|-----|-------|-------|
| Edge TTS (tr-TR-EmelNeural) | ✅ Kullanımda | Edel robotik buldu |
| Meta MMS-TTS | ✅ Test edildi | Edel değerlendirmedi |
| MiniMax | ⏳ Web demo | Edel test etmedi |
| Fish Audio S2 | ⏳ Araştırıldı | Denenmedi |

## Bir Sonraki Adım İçin

1. v12'yi test et: `python3 vanitas_ses_v12.py` → curl health check
2. TTS kararı ver: Meta MMS beğenildi mi? Edge TTS yeterli mi?
3. Stage 3: `create-next-app vanitas-web` ile başla
