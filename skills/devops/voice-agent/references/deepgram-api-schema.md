# Deepgram Voice Agent — Settings API Schema (2026-06-15)

Kaynak: `https://developers.deepgram.com/reference/voice-agent/voice-agent.md`

## ThinkSettingsV1 (agent.think)

```yaml
ThinkSettingsV1:
  type: object
  properties:
    provider:
      $ref: '#/components/schemas/ThinkSettingsV1Provider'
    endpoint:
      $ref: '#/components/schemas/ThinkSettingsV1Endpoint'
    functions:
      type: array
      items:
        $ref: '#/components/schemas/ThinkSettingsV1FunctionsItems'
    prompt:
      type: string
    context_length:
      type: integer
      description: Only configurable when custom think endpoint is used
  required:
    - provider
```

## ThinkSettingsV1Provider (oneOf)

```yaml
ThinkSettingsV1Provider:
  oneOf:
    - OpenAiThinkProvider
    - AwsBedrockThinkProvider
    - AnthropicThinkProvider
    - GoogleThinkProvider
    - GroqThinkProvider
```

## OpenAiThinkProvider

```yaml
OpenAiThinkProvider:
  type: object
  properties:
    type:
      type: string
      enum: [open_ai]
    version:
      type: string
    model:
      type: string
      enum: [gpt-5.5, gpt-5.4-nano, gpt-5.4-mini, gpt-5.4, gpt-5.3-chat-latest,
             gpt-5.2-chat-latest, gpt-5.2, gpt-5.1-chat-latest, gpt-5.1, gpt-5-nano,
             gpt-5-mini, gpt-5, gpt-4.1-nano, gpt-4.1-mini, gpt-4.1, gpt-4o-mini, gpt-4o]
    temperature:
      type: number
    reasoning_mode:
      type: string
  required:
    - type
    - model
```

## GroqThinkProvider

```yaml
GroqThinkProvider:
  type: object
  properties:
    type:
      type: string
      enum: [groq]
    version:
      type: string
    model:
      type: string
      enum: [llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768, ...]
    temperature:
      type: number
    reasoning_mode:
      type: string
  required:
    - type
    - model
```

## ThinkSettingsV1Endpoint

```yaml
ThinkSettingsV1Endpoint:
  type: object
  properties:
    url:
      type: string
      description: Custom LLM endpoint URL
    headers:
      type: object
      additionalProperties:
        type: string
      description: Custom headers for the endpoint
  description: Optional for non-Deepgram LLM providers
```

## Test Sonuçları (Python WebSocket, 2026-06-15)

| provider.type | provider.model | endpoint | Sonuç |
|---|---|---|---|
| `open_ai` | `gpt-4o-mini` | yok | ✅ SettingsApplied |
| `open_ai` | yok | var | ❌ UNPARSABLE_CLIENT_MESSAGE |
| `groq` | yok | var | ❌ UNPARSABLE_CLIENT_MESSAGE |
| `groq` | `llama-3.3-70b-versatile` | var | ✅ SettingsApplied |
| yok | yok | var | ❌ UNPARSABLE_CLIENT_MESSAGE |

**Sonuç:** `provider.model` tüm provider tipleri için **required**. 
BYO endpoint kullanırken geçerli bir model adı verilmeli (kullanılmasa bile).
`open_ai` BYO endpoint'i **reddediyor**, `groq` kabul ediyor.

## Geçersiz Alanlar

| Alan | Konum | Hata |
|------|-------|------|
| `timeout` | `think.timeout` | UNPARSABLE_CLIENT_MESSAGE (şemada yok) |
| `language` | `agent.language` | Deprecated (V1), uyarı verir |

## Deprecation

- `agent.language` → `agent.listen.provider.language` + `agent.speak.provider.language`
