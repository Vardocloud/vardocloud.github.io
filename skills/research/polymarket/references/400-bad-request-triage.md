# Polymarket HTTP 400 — Hızlı Triage (Gamma/CLOB)

## Tipik sebepler
1) **Yanlış parametre tipi / alan ismi**
   - Price history için `market` parametresi **conditionId** olmalı (hex string, genelde `0x...` ön ekli).
   - Orderbook/price için `token_id` **clobTokenIds** içindeki tokenlardan biri olmalı.

2) **Double-encoded alanların parse edilmemesi**
   - Gamma response’larında `outcomePrices`, `outcomes`, `clobTokenIds` genelde **JSON string** döner.
   - `json.loads(...)` yapılmazsa token/price dizisi yerine string gidip endpoint’i 400’e sürükleyebilir.

3) **Boş/eksik token_id veya conditionId**
   - Bazı yeni/kapalı marketlerde `clobTokenIds` veya history için `conditionId` beklenen formatta olmayabilir.
   - Boşsa CLOB endpoint’ler 400 döndürebilir.

4) **Endpoint path/parametre uyumsuzluğu**
   - Bu skill’de kullanılan örnekler:
     - `GET https://clob.polymarket.com/price?token_id=TOKEN_ID&side=buy|sell`
     - `GET https://clob.polymarket.com/book?token_id=TOKEN_ID`
     - `GET https://clob.polymarket.com/prices-history?market=CONDITION_ID&interval=all&fidelity=N`

## Reprodüksiyon mini-prosedürü
1) Gamma’dan gelen market objesini al:
   - `conditionId` alanı
   - `clobTokenIds` alanı
2) Aşağı kontrolleri yap:
   - `conditionId` string mi? `0x` ile başlıyor mu?
   - `clobTokenIds` JSON string mi? önce `json.loads` ile listeye dönüyor mu?
   - Liste uzunluğu >= 2 mi?
3) Sonra yalnızca doğru endpoint’i çağır (tek variable ile):
   - token ile `price` veya `book`
   - conditionId ile `prices-history`
4) 400 devam ederse request query string’ini kaydet (log’da URL’yi yazdır) ve hata cevabındaki `reason` metnini yakala.

## Not (skill/entegrasyon)
Bu skill okuma-onlydır; hata durumunda **trade/parametre imzası yoktur**. 400 her zaman API parametre formatından veya alan parse edilmemesinden olma eğilimindedir.
