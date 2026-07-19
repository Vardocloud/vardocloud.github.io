# session_search FTS5 Fallback — SQLite Doğrudan Erişim

## Sorun

`session_search` aracı FTS5 index üzerinde çalışır. Ancak bazı durumlarda FTS5 index'i sorguyu yakalayamaz ve boş döner — oysa veri `state.db`'de mevcuttur.

**Tespit edilen vaka (19 Tem 2026):** `state.db` (919MB, 1,621 oturum), içinde "sohbethakkindahersey11T" session'ı var. FTS5 index'inde veri var, sorgu da çalışıyor, ama `session_search` tool'u her sorguyu yakalamıyor. Bu teknik bir sınırlama, veri kaybı değil.

## Çözüm: SQLite Fallback

session_search 2-3 farklı query ile boş döndüğünde ve Edel "daha önce konuştuk" diyorsa:

```bash
# state.db'de sessions tablosu ve messages tablosu var
# sessions: id, source, model, started_at, ended_at
# messages: id, session_id, role, content, timestamp, ...

# Session ID ara:
sqlite3 ~/.hermes/state.db "SELECT id, source, model, datetime(started_at, 'unixepoch') FROM sessions WHERE id LIKE '%anahtar%' LIMIT 10;"

# Mesaj içeriğinde ara:
sqlite3 ~/.hermes/state.db "SELECT m.id, m.role, substr(m.content, 1, 300), datetime(m.timestamp, 'unixepoch') FROM messages m JOIN sessions s ON m.session_id = s.id WHERE m.content LIKE '%anahtar%' AND m.role = 'user' ORDER BY m.timestamp DESC LIMIT 10;"
```

## session_search Alternatifleri (Terk Etme Zinciri)

1. **session_search** — birincil araç (FTS5 + BM25)
2. **session_search 2. query** — farklı anahtar kelimelerle
3. **session_search 3. query** — daha geniş/dar terimlerle
4. **SQLite fallback** — `sqlite3 ~/.hermes/state.db` ile doğrudan sorgu
5. **Edel'e sor** — "hatırlayamadım, tekrar anlatır mısın?"

## Ne Zaman Kullanılır

- session_search 2+ farklı query ile boş döndüğünde
- Edel "ama daha önce konuşmuştuk, niye bulamıyorsun?" dediğinde
- Edel "session'da araştırdım buldum" deyip senin bulamadığın bir şeyi referans verdiğinde
- Eski (>30 gün) session'lar aranırken (FTS5 index'ten düşmüş olabilir)

## Asla Yapma

- "Session'larda yok" diye varsayıp sıfırdan araştırmaya başlama
- "Bulamadım" deyip konuyu kapatma — SQLite fallback'i mutlaka dene
- Edel "orada" dediğinde "yok" diye ısrar etme — SQLite'dan kontrol et
