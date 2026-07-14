#!/usr/bin/env python3
"""LinkedIn OAuth Callback Server — authorization code'u yakalar ve token alır.

🥇 Localhost redirect yöntemi öncelikli — bu server sadece YEDEK.
🥈 Port 80 kullan (Oracle Cloud VCN Security List'te 8888 kapalı).
"""
import http.server
import urllib.parse
import json
import sys
import os
import requests

CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "7780feuhqlkxe0")
CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("LINKEDIN_REDIRECT_URI", "http://127.0.0.1:8888/callback")
TOKEN_FILE = os.path.expanduser("~/.hermes/secrets/linkedin_token.json")
LOG_FILE = os.path.expanduser("~/.hermes/secrets/linkedin_callback.log")

# State env var'dan veya argument'ten alınır
EXPECTED_STATE = os.environ.get("LINKEDIN_OAUTH_STATE", "")
PORT = int(os.environ.get("LINKEDIN_OAUTH_PORT", "80"))


def log(msg):
    """Hem print et hem dosyaya yaz. flush=True buffer sorununu çözer."""
    print(msg, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        log(f"[REQUEST] {self.path}")

        if parsed.path == "/callback":
            code = params.get("code", [None])[0]
            state = params.get("state", [None])[0]
            error = params.get("error", [None])[0]

            if error:
                msg = f"❌ LinkedIn hatası: {error} — {params.get('error_description', [''])[0]}"
                log(msg)
                self._respond(400, f"<h1>{msg}</h1>")
                return

            if not code:
                log("❌ Code gelmedi!")
                self._respond(400, "<h1>❌ Authorization code bulunamadı</h1>")
                return

            if EXPECTED_STATE and state != EXPECTED_STATE:
                log(f"❌ State eşleşmedi! Beklenen: {EXPECTED_STATE}, Gelen: {state}")
                self._respond(400, "<h1>❌ State mismatch</h1>")
                return

            log(f"✅ Code alındı: {code[:20]}... Token isteniyor...")

            # Token exchange
            token_response = requests.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )

            if token_response.status_code == 200:
                token_data = token_response.json()
                os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
                with open(TOKEN_FILE, "w") as f:
                    json.dump(token_data, f, indent=2)
                os.chmod(TOKEN_FILE, 0o600)

                log(f"\n✅ TOKEN ALINDI!")
                log(f"   access_token: {token_data.get('access_token', '')[:30]}...")
                log(f"   expires_in: {token_data.get('expires_in')} saniye")
                log(f"   scope: {token_data.get('scope')}")
                log(f"   Token kaydedildi: {TOKEN_FILE}")

                self._respond(
                    200,
                    "<h1>✅ LinkedIn bağlantısı başarılı!</h1>"
                    "<p>Bu pencereyi kapatabilirsin.</p>",
                )
            else:
                log(f"❌ Token hatası ({token_response.status_code}): {token_response.text}")
                self._respond(
                    500,
                    f"<h1>❌ Token alınamadı</h1>"
                    f"<p>{token_response.status_code}: {token_response.text[:200]}</p>",
                )

        elif parsed.path == "/health":
            self._respond(200, "OK")

        else:
            self._respond(404, "Not Found")

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        log(f"[HTTP] {args[0]}")


if __name__ == "__main__":
    log(f"🔊 Callback server başlatıldı: http://0.0.0.0:{PORT}/callback")
    log(f"   Beklenen state: {EXPECTED_STATE}")
    log(f"   Log dosyası: {LOG_FILE}")
    server = http.server.HTTPServer(("0.0.0.0", PORT), CallbackHandler)
    try:
        server.serve_forever()  # handle_request() değil — tek istekte kapanmasın
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        log("🔇 Server kapatıldı.")
