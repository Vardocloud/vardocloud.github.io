#!/usr/bin/env python3
"""LinkedIn OAuth Callback Server — auth code yakalar, token alir.

KULLANIM (ihtiyac halinde):
  sudo ~/.hermes/hermes-agent/venv/bin/python3 \
      ~/.hermes/scripts/linkedin_callback_server.py

Port 80 root gerektirir. Sadece LinkedIn OAuth gerektiginde calisir.
"""
import http.server
import urllib.parse
import json
import sys
import os
import requests

# Load from .env
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.hermes/secrets/linkedin.env"))

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "")
TOKEN_FILE = os.path.expanduser("/home/ubuntu/.hermes/secrets/linkedin_token.json")
LOG_FILE = os.path.expanduser("/home/ubuntu/.hermes/secrets/linkedin_callback.log")
EXPECTED_STATE = os.urandom(32).hex()

def log(msg):
    """Hem print et hem dosyaya yaz."""
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
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"<h1>{msg}</h1>".encode())
                return
            
            if not code:
                log("❌ Code gelmedi!")
                self.send_response(400)
                self.end_headers()
                return
            
            if state != EXPECTED_STATE:
                log(f"❌ State eşleşmedi! Beklenen: {EXPECTED_STATE}, Gelen: {state}")
                self.send_response(400)
                self.end_headers()
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
                timeout=30
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
                
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    "<h1>✅ LinkedIn bağlantısı başarılı!</h1>"
                    "<p>Bu pencereyi kapatabilirsin.</p>".encode()
                )
            else:
                log(f"❌ Token hatası ({token_response.status_code}): {token_response.text}")
                self.send_response(500)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    f"<h1>❌ Token alınamadı</h1><p>{token_response.status_code}: {token_response.text[:200]}</p>".encode()
                )
        
        elif parsed.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        log(f"[HTTP] {args[0]}")

if __name__ == "__main__":
    log(f"🔊 Callback server başlatıldı: http://0.0.0.0:80/callback")
    log(f"   Beklenen state: {EXPECTED_STATE}")
    log(f"   Log dosyası: {LOG_FILE}")
    server = http.server.HTTPServer(("0.0.0.0", 80), CallbackHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        log("🔇 Server kapatıldı.")
