# Voice Agent vs Voice Supervisor — Architectural Distinction

> Session: 5 Temmuz 2026 — Edel, Yusuf İpek videosu üzerinden Sesli Supervisor Pattern'i sorguladı.

## Tanımlar

**Voice Agent (mevcut — v13.1):**
- Amaç: **Reaktif sesli sohbet** — kullanıcıyla doğal dilde konuşmak
- Akış: Konuş → Web Speech VAD/STT → Groq LLM (sohbet) → edge-tts → sesli cevap
- Yönelim: Vanitas kişiliğiyle günlük muhabbet
- Tool call: Opsiyonel, konuşma akışında ihtiyaç halinde

**Voice Supervisor (önerilen — supervisor-pattern + heartbeat):**
- Amaç: **Proaktif sistem yönetimi** — task'ları sesle kontrol etmek
- Akış: "Son task durumu?" → STT → Heartbeat sorgulama → TTS
- Yönelim: Task state yönetimi + heartbeat + budget + routine
- Tool call: Merkezde — her şey structured tool call

## Temel Farklar

| Boyut | Voice Agent | Voice Supervisor |
|-------|-------------|------------------|
| **Hafıza** | Konuşma geçmişi (sohbet) | Task state + heartbeat log (operasyonel) |
| **HF** Kimlik | Vanitas (kişilik, duygu, üslup) | Supervisor (yönetici, metrik, rapor) |
| **Tool kullanımı** | İsteğe bağlı, konuşma akışında | Merkezi, her yanıt tool call'a dayalı |
| **Output** | Doğal dil, duygusal, kişilikli | Structured rapor, metrik, özet |
| **LLM Modeli** | Sohbet için optimize (Groq llama) | Task analizi için optimize |
| **Ek maliyet** | $ (STT + TTS + LLM) | $ (STT + TTS, LLM heartbeat sorgulama minimal) |

## Neden İkisi Ayrı?

1. **Farklı amaç, farklı optimizasyon:**
   - Voice Agent sohbet kalitesi için optimize edilir (düşük gecikme, doğal TTS)
   - Voice Supervisor operasyonel doğruluk için optimize edilir (structured çıktı, log tutarlılığı)

2. **Ama aynı altyapıyı paylaşabilir:**
   - STT/TTS pipeline'ı ortak kullanılır
   - Voice Agent, Supervisor tool'larını çağırabilir (tool call olarak)
   - Supervisor raporları TTS ile seslendirilebilir

3. **Paperclip Pattern ile ilişkisi:**
   - Paperclip'teki CEO agent = Voice Supervisor (task yönetimi)
   - Paperclip'teki worker agent'lar = Voice Agent benzeri sohbet ajanları
   - Heartbeat + budget + skills + routines = Supervisor'ın yönetim araçları

## Örnek Kullanım Senaryoları

| Komut | Voice Agent | Voice Supervisor |
|-------|-------------|------------------|
| "Nasılsın?" | "İyiyim, sen nasılsın?" | — (sohbet cevabı yok) |
| "Son task durumu ne?" | "Hmm bilmiyorum, bakar mısın?" | "Son 3 task: 2 tamam, 1 validation failed" |
| "Yeni bir tarama başlat" | "Nasıl bir tarama?" | "Routine tanımlanıyor. Budget ve skills set'i belirle." |
| "Neden hata verdi?" | "Hangi hata?" | "Task-003'te schema'daki 'findings' alanı eksik." |

## Implementation Notları

- Supervisor heartbeat sorgulama = Voice Agent'a tek tool call eklenerek yapılabilir
- Ayrı bir supervisor LLM session'ı gerekmez (mevcut LLM tool call olarak heartbeat'e erişir)
- İkisi aynı anda çalışabilir: Agent sohbet ederken Supervisor task yönetir
- Budget ve routine yönetimi için cron + heartbeat entegrasyonu gerekir
