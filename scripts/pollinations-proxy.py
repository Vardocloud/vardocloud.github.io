#!/usr/bin/env python3
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request, json

TARGET = 'https://gen.pollinations.ai'
PORT = 19999
BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

# API key .env'den okunur
import os
API_KEY = None
env_path = os.path.expanduser('~/.hermes/.env')
if os.path.exists(env_path):
    for line in open(env_path):
        if line.startswith('POLLINATIONS_API_KEY'):
            API_KEY = line.split('=',1)[1].strip().strip('"').strip("'")
            break

class Handler(BaseHTTPRequestHandler):
    def do_POST(s):
        # OpenCode /v1/responses → /v1/chat/completions dönüşümü
        if s.path == '/v1/responses':
            s.path = '/v1/chat/completions'
        s._fw('POST')
    def do_GET(s):
        # Hermes'in sorguladığı ama Pollinations'ın desteklemediği endpoint'lere sahte yanıt
        import json as _json
        fake_responses = {
            '/api/tags': {'models': [{'name': 'openai'}, {'name': 'gemma'}, {'name': 'minimax'}, {'name': 'glm'}, {'name': 'gpt-5.4-mini'}]},
            '/v1/models': {'object': 'list', 'data': [{'id': 'openai'}, {'id': 'gemma'}, {'id': 'minimax'}, {'id': 'glm'}, {'id': 'gpt-5.4-mini'}]},
            '/api/v1/models': {'object': 'list', 'data': [{'id': 'openai'}]},
            '/v1/props': {'pollinations': True, 'supports_tools': True},
            '/props': {'pollinations': True},
            '/version': {'version': '1.0.0'},
            '/api/show': {'license': 'MIT', 'modelfile': '', 'parameters': '', 'template': ''},
        }
        # /api/show?name=X formatını da yakala
        if s.path.startswith('/api/show'):
            s.send_response(200)
            s.send_header('Content-Type', 'application/json')
            s.end_headers()
            s.wfile.write(_json.dumps({'license': 'MIT', 'modelfile': '', 'parameters': '', 'template': ''}).encode())
            print(f"[PROXY] GET {s.path} → FAKE 200", file=sys.stderr, flush=True)
            return
        if s.path in fake_responses:
            s.send_response(200)
            s.send_header('Content-Type', 'application/json')
            s.end_headers()
            s.wfile.write(_json.dumps(fake_responses[s.path]).encode())
            print(f"[PROXY] GET {s.path} → FAKE 200", file=sys.stderr, flush=True)
        else:
            s.send_response(404)
            s.end_headers()
            print(f"[PROXY] GET {s.path} → 404", file=sys.stderr, flush=True)
    def do_OPTIONS(s):
        s.send_response(200)
        s.send_header('Access-Control-Allow-Origin', '*')
        s.end_headers()
    def log_message(s, *a): 
        import sys
        print(f"[PROXY] {s.command} {s.path} -> {s.headers.get('Authorization','no-auth')[:20]}...", file=sys.stderr, flush=True)

    def _fw(s, method):
        import sys, json as _json
        cl = int(s.headers.get('Content-Length', 0))
        body = s.rfile.read(cl) if cl else None
        
        # Responses API → Chat Completions dönüşümü
        if body and b'"input"' in body:
            try:
                data = _json.loads(body)
                if 'input' in data:
                    # input → messages, developer → system
                    data['messages'] = []
                    for msg in data.pop('input'):
                        role = msg.get('role', 'user')
                        if role == 'developer':
                            role = 'system'
                        data['messages'].append({'role': role, 'content': msg.get('content', '')})
                    # Responses API'ye özel alanları temizle
                    for key in ['text', 'store', 'include', 'prompt_cache_key', 'reasoning']:
                        data.pop(key, None)
                    body = _json.dumps(data).encode()
                    print(f"[PROXY] Responses→Chat transform | {len(body)}b", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"[PROXY] Transform error: {e}", file=sys.stderr, flush=True)
        
        # DEBUG LOG
        import sys
        body_preview = body[:300].decode('utf-8','ignore') if body else '(empty)'
        print(f"[PROXY] {method} {s.path} | body={body_preview}", file=sys.stderr, flush=True)
        req = urllib.request.Request(TARGET + s.path, data=body, method=method)
        for h, v in s.headers.items():
            if h.lower() in ('host', 'content-length', 'user-agent', 'authorization'): continue
            req.add_header(h, v)
        req.add_header('User-Agent', BROWSER_UA)
        # Always use our own API key - replace any client Authorization
        if API_KEY:
            req.add_header('Authorization', f'Bearer {API_KEY}')
        try:
            resp = urllib.request.urlopen(req, timeout=300)
            s.send_response(resp.status)
            for rh, rv in resp.getheaders():
                if rh.lower() not in ('transfer-encoding', 'connection'):
                    s.send_header(rh, rv)
            s.end_headers()
            full_body = b''
            while True:
                chunk = resp.read(65536)
                if not chunk: break
                full_body += chunk
                s.wfile.write(chunk)
            print(f"[PROXY] ← {resp.status} | {len(full_body)}b | {full_body[:200]}", file=sys.stderr, flush=True)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            s.send_response(e.code)
            s.end_headers()
            s.wfile.write(err_body)

if __name__ == '__main__':
    print(f'Transparent UA proxy :{PORT} -> {TARGET}', flush=True)
    HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()