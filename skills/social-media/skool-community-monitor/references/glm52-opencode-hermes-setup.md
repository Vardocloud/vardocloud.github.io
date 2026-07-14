# GLM 5.2 + OpenCode + Hermes Agent Setup (Community Discovery)

> Bu referans, AI Automation Society community taramasında keşfedilen GLM 5.2 / OpenCode / Hermes
> Agent konfigürasyon bilgilerini içerir. Keşif tarihi: 2026-06-30.

## GLM 5.2 Inside OpenCode (Mike Holp)

**Post URL:** https://www.skool.com/ai-automation-society/glm-52-inside-opencode-go-in-minutes
**Video süresi:** 8:44
**Başlık:** "Learn how to set up GLM 5.2 inside OpenCode and connect it to Hermes Agent using a simple, cost-effective method."

### Ne Keşfedildi
- GLM 5.2 (z-ai/glm-5.2) bir reasoning modeldir
- OpenCode CLI içinde çalıştırılabilir
- OpenCode, Hermes Agent'a bağlanabilir (delegation target olarak)
- Yöntem "simple, cost-effective" olarak tanımlanmış — pahalı API key'leri gerektirmez

### Vanitas İçin Önemi
- Hermes Agent + OpenCode + GLM 5.2 kombinasyonu, Vanitas için daha ucuz reasoning model erişimi sağlayabilir
- OpenCode'u delegation backend olarak kullanma potansiyeli

## Claude Code Skill Builder — Best Practice Audit (Prajwal Bista)

**Post URL:** https://www.skool.com/ai-automation-society/i-found-out-my-ai-skill-was-broken-and-it-was-working-the-whole-time

### Üç Kritik Bulgu

| Bulgu | Sorun | Çözüm |
|-------|-------|-------|
| **Description çok uzun** | 12 satırlık description, Claude'un skill description budget'ını tüketiyor | Kısa tut (3-4 satır) |
| **Argument hint yok** | Slash menüde hiçbir şey göstermiyor | `arg_hint` frontmatter alanı ekle |
| **disable-model-invocation eksik** | Claude kullanıcı sormadan 10 web search yapabiliyor | Information-only skill'lerde `disable-model-invocation: true` set et |

### Ne Öğrenildi
- "Working ≠ well-built" — skill çalışıyor görünse de best practice ihlalleri olabilir
- Skills are "mini software" — maintenance gerektirir
- Vanitas mevcut skill'leri bu üç kriterle periyodik audit edilmeli

## GLM 5.2 redacted_thinking Error (Zachary Bradley)

**Post URL:** https://www.skool.com/ai-automation-society/glm-52-on-vs-code-issue

### Hata
```
unsupported content type: redacted_thinking
```
GLM-5.2 + OpenRouter + Claude Code VS Code extension kombinasyonunda görülür.

### Kök Sebep (Tahmini)
1. Claude Code extended thinking talep ediyor
2. OpenRouter model reasoning'ini `redacted_thinking` bloğu olarak döndürüyor
3. VS Code extension bu content type'ı render edemiyor

### Workaround'lar
- `export CLAUDE_CODE_EFFORT=low` — extended thinking'i kapatır
- Reasoning olmayan model varyantına geç (`z-ai/glm-5.2` → non-reasoning model)
- OpenCode CLI kullan (VS Code extension yerine)
