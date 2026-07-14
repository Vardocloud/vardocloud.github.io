#!/usr/bin/env python3
"""
Secure password capture server — one-time use.
Starts an HTTP form on a specified port; password written to /tmp/pw_val.txt (chmod 600).
Password NEVER goes through Telegram or any LLM context.

Usage:
  python3 pw_server.py [PORT]
  # Opens an HTML form. User types password, submits -> saved to /tmp/pw_val.txt

Port auto-selection: omit PORT arg to use a random available port.
Edel access: needs port mapping from host. If unreachable, use cloudflared tunnel.

Created: 21 Haz 2026 (Upwork password entry session)
"""
import http.server, socket, urllib.parse, os, threading, sys

PW = [""]

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/done':
            if PW[0]:
                with open('/tmp/pw_val.txt', 'w') as f: f.write(PW[0])
                os.chmod('/tmp/pw_val.txt', 0o600)
                self.send_response(200); self.end_headers()
                self.wfile.write(b'<h2>alindi, kapatabilirsin</h2>')
                threading.Timer(1.0, lambda: exit(0)).start()
            else:
                self.send_response(200); self.end_headers()
                self.wfile.write(b'<h2>henuz sifre girilmedi</h2>')
            return
        self.send_response(200); self.end_headers()
        html = b'''
        <html><body style="font-family:sans-serif;padding:40px">
        <h2>Upwork sifreni gir</h2>
        <form action="/" method="post">
        <input type="password" name="pw" size="40" style="font-size:18px;padding:8px" autofocus>
        <br><br>
        <input type="submit" value="Kaydet" style="font-size:16px;padding:8px 24px">
        </form>
        <p style="color:#666">sifre diska yazilacak, Telegram'a dusmeyecek</p>
        </body></html>
        '''
        self.wfile.write(html)
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode()
        params = urllib.parse.parse_qs(body)
        if 'pw' in params and params['pw'][0]:
            PW[0] = params['pw'][0].strip()
        self.send_response(303); self.send_header('Location', '/done'); self.end_headers()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 0
if port == 0:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 0))
    port = sock.getsockname()[1]; sock.close()

print(f"PORT:{port}", flush=True)
httpd = http.server.HTTPServer(('0.0.0.0', port), Handler)
httpd.serve_forever()
