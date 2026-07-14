# HUMINT Elicitation Techniques for Instagram DM

Social engineering conversation tactics for information extraction in DM conversations.

## Sources
- NotebookLM: Vanitas Konuşma Taktikleri + YouTube Konuşma Taktikleri Transcriptleri
- Web: Christina Lekati (Medium), Social-Engineer.org, CDSE Job Aid

## Core Principles

### 1. Never Interview — Moderate
- Listen → remember → ask about what they said
- One question per message, derive next from response
- "Yaprak damarı tekniği": dive deeper on one detail from their answer

### 2. Elicitation Triggers

| Trigger | Human Tendency | How to Use |
|---------|---------------|------------|
| **False statement** | Urge to correct | "Sen daha çok gece aktif olan birisin gibi geldi" → they correct you = info |
| **"Sence?"** | Desire to be heard | "Sence insanlar DM'de neden mesafeli olur?" |
| **Strategic pause** | Discomfort with silence | Short answer → wait → they fill the gap |
| **Quid pro quo** | Reciprocity | Share something harmless → they feel obligated to share back |
| **Macro → Micro** | Gradual comfort | General topic → narrow down → personal detail |

### 3. Deflection (When They Question You)

| They Ask | You Respond |
|----------|------------|
| "Nerelisin?" | "İzmirliyim 😊 Peki sen?" |
| "Ne iş yapıyorsun?" | "Okulda çalışıyorum. Senin işin ne?" |
| "Neden bana yazdın?" | "Profilin dikkatimi çekti. Sen hiç keşfetten birine yazdın mı?" |
| "Bot musun?" | "Bot değilim ya 😄 Sen bot musun?" — gül geç, asla savunmacı olma |

### 4. Cover Story Design
- Minimal details = less to contradict
- Use shared context (location, age range) without specifics
- Never mention the real target's known associates, venues, or timeline details
- "Keşfette gördüm" is the universal low-risk entry

### 5. Red Flags (When to Retreat)
- Short, one-word answers consistently → don't push
- They never ask you questions → they're not interested
- They ask the same question multiple times → testing consistency
- "Nerden buldun beni?" with suspicion → give simple answer + retreat

## Burner Account Detection (API)

5 signs from `web_profile_info`:
```json
{
  "is_private": true,
  "edge_followed_by": {"count": 0},
  "edge_follow": {"count": 25},
  "full_name": "",
  "biography": "",
  "edge_owner_to_timeline_media": {"count": 0}
}
```
All 5 = ~95% burner account.
