# Vanitas Podcast Fabrikası — Prompt Şablonları

## Aşama 1: İçerik Planlayıcı (Zen API — mimo-v2.5-free, 0 reasoning)

### Şablon (JSON çıktı için)

```
Sen bir podcast yapımcısısın. Şu konuda bir podcast akış planı çıkar.

KONU: {konu}
HEDEF KİTLE: {hedef_kitle}
HEDEF SÜRE: {sure_dk} dakika

Aşağıdaki JSON formatında dön:

{
  "podcast_adi": "string (Türkçe, yaratıcı bir isim)",
  "host1": {
    "isim": "string",
    "rol": "string (örn: uzman psikolog, araştırmacı)",
    "ton": "string (örn: sakin, akademik, meraklı)"
  },
  "host2": {
    "isim": "string",
    "rol": "string (örn: meraklı dinleyici, gazeteci)",
    "ton": "string (örn: enerjik, sorgulayıcı, samimi)"
  },
  "ortam": "string (stüdyo tasviri)",
  "bolumler": [
    {
      "baslik": "string",
      "sure_dk": number,
      "ana_noktalar": ["string", "string"]
    }
  ]
}

ÖNEMLİ:
- Bardo teması: psikoloji, felsefe, nörobilim odaklı
- Akademik dili sohbet diline çevir
- Host1 uzman, Host2 meraklı/öğrenen tarafta
- 3 ana bölüm + giriş + kapanış (toplam 5 bölüm)
- Türkçe yanıt ver
- Sadece JSON dön, açıklama ekleme
```

### curl çağrısı (jq ile Türkçe güvenli):

```bash
jq -n --arg system "$(cat <<'SYS'
Sen bir podcast yapımcısısın. Verilen konu için JSON formatında podcast akış planı çıkar.
SYS
)" \
  --arg user "$(cat <<'USER'
KONU: Bilinç Akışı ve Yaratıcılık
HEDEF KİTLE: Üniversite öğrencileri
HEDEF SÜRE: 8 dakika
USER
)" \
  '{
    "model": "mimo-v2.5-free",
    "messages": [
      {"role": "system", "content": $system},
      {"role": "user", "content": $user}
    ],
    "temperature": 0.7
  }' | curl -s -X POST "https://opencode.ai/zen/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d @-
```

### Kısa şablon (tek satırda hızlı çağrı):

```bash
jq -n \
  --arg konu "Bilinç Akışı ve Yaratıcılık" \
  --arg kitle "Üniversite öğrencileri" \
  --arg sure "8" \
  '{
    "model": "mimo-v2.5-free",
    "messages": [
      {"role": "system", "content": "Sen bir podcast yapımcısısın. JSON formatında akış planı çıkar."},
      {"role": "user", "content": ("KONU: " + $konu + "\nHEDEF KİTLE: " + $kitle + "\nHEDEF SÜRE: " + $sure + " dakika\n\nJSON formatında dön: {podcast_adi, host1: {isim, rol, ton}, host2: {isim, rol, ton}, ortam, bolumler: [{baslik, sure_dk, ana_noktalar}]}")}
    ],
    "temperature": 0.7
  }' | curl -s -X POST "https://opencode.ai/zen/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d @-
```

---

## Aşama 2: Diyalog Yazarı (Pollinations — gpt-5.4-mini)

### Şablon

```
Sen bir podcast diyalog yazarısın. Aşağıdaki podcast planını al ve doğal, akıcı bir
Türkçe karşılıklı konuşma metni yaz.

PODCAST PLANI:
{podcast_plani_json}

YAZIM KURALLARI:
- Her hostun ayrı ses tonu ve karakteri olmalı
- Doğal geçişler, espriler, "aa gerçekten mi?" anları ekle
- Hedef süre: ~{sure_dk} dakika (yaklaşık {kelime_sayisi} kelime)
- Akademik kavramları günlük dille açıkla
- Host1 (uzman): derinlemesine bilgi verir, sakin ve açıklayıcı
- Host2 (meraklı): sorular sorar, şaşırır, basitleştirilmesini ister

FORMAT:
Her satır "Host1:" veya "Host2:" ile başlasın.
Konuşma akışı: Giriş selamı → 3 bölüm → Kapanış
```

### curl çağrısı (plan.json dosyasından oku):

```bash
PLAN=$(cat output/plan.json)
jq -n \
  --arg plan "$PLAN" \
  --arg sure "8" \
  --arg kelime "1000" \
  '{
    "model": "gpt-5.4-mini",
    "messages": [
      {"role": "system", "content": "Sen bir podcast diyalog yazarısın. Doğal Türkçe karşılıklı konuşma yaz."},
      {"role": "user", "content": ("PODCAST PLANI:\n" + $plan + "\n\nYAZIM KURALLARI:\n- Her hostun ayrı ses tonu ve karakteri olmalı\n- Doğal geçişler, espriler, \"aa gerçekten mi?\" anları ekle\n- Hedef süre: ~" + $sure + " dakika (yaklaşık " + $kelime + " kelime)\n- Akademik kavramları günlük dille açıkla\n- Host1 (uzman): derinlemesine bilgi verir, sakin ve açıklayıcı\n- Host2 (meraklı): sorular sorar, şaşırır, basitleştirilmesini ister\n\nFORMAT:\nHer satır \"Host1:\" veya \"Host2:\" ile başlasın.\nKonuşma akışı: Giriş selamı → 3 bölüm → Kapanış")}
    ],
    "temperature": 0.8,
    "max_tokens": 2048
  }' | curl -s -X POST "http://127.0.0.1:19999/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d @-
```

### Doğrudan Aşama 1 + Aşama 2 zinciri:

```bash
# Aşama 1: Plan al
PLAN_RESPONSE=$(jq -n \
  --arg konu "Sibernetik Bilinç" \
  --arg kitle "Teknoloji meraklıları" \
  --arg sure "10" \
  '{
    "model": "mimo-v2.5-free",
    "messages": [
      {"role": "system", "content": "Sen bir podcast yapımcısısın. JSON formatında akış planı çıkar."},
      {"role": "user", "content": ("KONU: " + $konu + "\nHEDEF KİTLE: " + $kitle + "\nHEDEF SÜRE: " + $sure + " dakika\n\nJSON formatında dön.")}
    ],
    "temperature": 0.7
  }' | curl -s -X POST "https://opencode.ai/zen/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d @-)

PLAN=$(echo "$PLAN_RESPONSE" | jq -r '.choices[0].message.content')

# Aşama 2: Diyalog yaz
jq -n \
  --arg plan "$PLAN" \
  --arg sure "10" \
  '{
    "model": "gpt-5.4-mini",
    "messages": [
      {"role": "system", "content": "Sen bir podcast diyalog yazarısın."},
      {"role": "user", "content": ("PODCAST PLANI:\n" + $plan + "\n\nDoğal Türkçe konuşma yaz.")}
    ],
    "temperature": 0.8
  }' | curl -s -X POST "http://127.0.0.1:19999/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d @-
```

---

## Aşama 3: Görsel + Ses (Opsiyonel)

### nanobanana-2 — Thumbnail Prompt

```
Bir podcast kapağı konsepti. Psikedelik ama sofistike.
Konu: {konu}
Hostlar: {host1} ve {host2}
Ortam: {ortam}
Renk paleti: Koyu mor, altın, gece mavisi
Stil: Dijital çizim, neon vurgular, gizemli atmosfer
```

### ElevenLabs — Seslendirme Prompt

```
Ses: Bella (ElevenLabs)
Dil: Türkçe
Ton: Doğal sohbet, samimi, akıcı
Hız: Normal
Dosya: output/diyalog.txt → Host1 ve Host2 satırlarına göre ayır
```

---

## Bardo Teması — Prompt Varyasyonları

### Akademik → Sohbet Dönüşümü

```
Şu akademik kavramı açıkla: {kavram}
Hedef kitle: {kitle}
İstek: Kavramı bir arkadaşına anlatır gibi açıkla.
Metafor kullan, günlük hayattan örnek ver.
Akademik terimleri en aza indir.
```

### Psikoloji Odaklı Giriş

```
Bu podcast bölümü {konu} hakkında.
Ama psikoloji merceğinden bakıyoruz.
Girişte dinleyiciyi içine çekecek bir soru sor:
"Sence {günlük_deneyim} aslında {psikolojik_kavram} olabilir mi?"
```
