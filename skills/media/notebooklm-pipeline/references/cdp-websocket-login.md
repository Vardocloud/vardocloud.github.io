# CDP WebSocket Login + Anti-Detection

> Chrome DevTools Protocol ile otomatik Google login için CDP teknikleri.

## CDP Port Bulma

```bash
ps aux | grep remote-debugging-port
```

## input.insertText vs Per-Character

Şifre girerken her karakter için ayrı `Input.dispatchKeyEvent` yerine tek `Input.insertText` kullan:

```python
await ws.send(json.dumps({"id": 1, "method": "Input.insertText",
    "params": {"text": password}}))
```

## Anti-Detection Script

```javascript
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
window.navigator.chrome = {runtime: {}, loadTimes: function() {}, ...};
```

`Page.addScriptToEvaluateOnNewDocument` ile eklenir.

## Google React LI Click

`<li>` elemanları JS `.click()` çağrısına yanıt vermez. `Input.dispatchMouseEvent` gerekir:

```python
coords = Runtime.evaluate("document.querySelectorAll('li')[1].getBoundingClientRect()")
x = coords.x + coords.width/2
y = coords.y + coords.height/2
Input.dispatchMouseEvent(type="mousePressed", x=x, y=y)
Input.dispatchMouseEvent(type="mouseReleased", x=x, y=y)
```

LI index: 0="Use your passkey", 1="Enter your password", 2="Try another way"

## Auth Flow — Passkey Atlama

Container restart → tüm hesaplar "Signed out". Sıra:
1. `document.querySelector('[data-identifier="email"]').click()`
2. Passkey sayfası: "Try another way" tıkla (mouse event)
3. Selection: "Enter your password" tıkla (mouse event)
4. Şifre gir (bridge ile kullanıcı kendisi girsin)
5. Next butona tıkla

## CDP Password Bridge

`scripts/cdp-password-bridge.py` — Web formu → CDP → Chrome hattı. Kullanıcı kendi tarayıcısında web sayfasına şifresini girer, ben görmem.
