# 3 Katmanlı Hafıza Mimarisi

Vanitas'ın bilgiyi unutmaması için 3 katman:

```
KATMAN 1: Memory (~2.2KB)
├── Her prompt'ta otomatik enjekte edilir
├── Sadece en kritik bilgiler (güvenlik, temel kurallar)
└── Limiti aşınca → Katman 3'e (NotebookLM) arşivlenir

KATMAN 2: Skill'ler
├── Tetiklendiğinde yüklenir
├── notebook_fallback alanı ile Katman 3'e bağlanır
└── Bilgi eksikse → cross_notebook_query() ile arşivden çeker

KATMAN 3: NotebookLM Arşiv
├── "🧠 Vanitas Hafıza Arşivi" notebook'u
├── 7 kaynak, 3 etiketli kategoride
├── Etiketler: Dijital Platformlar, Yapay Zeka Araçları, Eğitim & Akademik
└── Sorgulanabilir, cross-referans yapabilir
```

## Kurulum

1. NotebookLM notebook: `6c7f3daa-1640-4fad-9917-ec44bc432e58`
2. Skill'lere fallback: `notebook_fallback: "6c7f3daa..."`
3. Sorgu: `cross_notebook_query("konu", notebook_names="6c7f3daa")`

## Örnek

```
"LinkedIn post at" → linkedin skill → yetmedi → cross_notebook_query("post kuralları")
→ "Onaysız ASLA post atma, Hakan Türkçapar üslubu" ✅
```

**Oluşturulma:** 29 Mayıs 2026, Vanitas Dönüşümü.
