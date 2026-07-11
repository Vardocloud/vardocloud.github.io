#!/usr/bin/env python3
"""OpenCode Go transparent proxy — port 19998 → https://opencode.ai/zen/go

v3: Dynamic API key — per-request env/auth.json check.
    Bitwarden/Dashboard key changes take effect IMMEDIATELY.
    All credential pool entries checked (status-agnostic).
"""
import sys, os, json as _json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

TARGET = 'https://opencode.ai/zen/go'
PORT = 19998
BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

HERMES_AUTH_PATH = os.path.expanduser('~/.hermes/auth.json')
OPENCODE_AUTH_PATH = os.path.expanduser('~/.local/share/opencode/auth.json')


def get_api_key():
    """Resolve API key dynamically per-request.
    
    Priority (checks every call so Dashboard/Bitwarden updates take effect immediately):
    1. ~/.hermes/.env → OPENCODE_GO_API_KEY line (bypasses Bitwarden override)
    2. OPENCODE_GO_API_KEY env var (set by Bitwarden — may be stale)
    3. auth.json credential_pool → opencode-go entries → source env var
    4. auth.json credential_pool → custom:opencode-go entries
    5. ~/.local/share/opencode/auth.json
    """
    def _valid_key(key):
        return bool(key and len(key) > 10 and key.startswith('sk-'))
    
    # 1. Read directly from .env file (Bitwarden can't override this)
    if os.path.exists(ENV_PATH):
        try:
            for line in open(ENV_PATH):
                if line.startswith('OPENCODE_GO_API_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"\'').strip()
                    if _valid_key(key):
                        return key
        except Exception:
            pass
    
    # 2. OPENCODE_GO_API_KEY env var
    key = os.environ.get('OPENCODE_GO_API_KEY', '')
    if _valid_key(key):
        return key
    
    # 3. auth.json credential pools
    def _from_pool(pool_name):
        if not os.path.exists(HERMES_AUTH_PATH):
            return ''
        try:
            with open(HERMES_AUTH_PATH) as f:
                auth = _json.load(f)
            for entry in auth.get('credential_pool', {}).get(pool_name, []):
                source = entry.get('source', '')
                if source.startswith('env:'):
                    env_var = source.split(':', 1)[1]
                    k = os.environ.get(env_var, '')
                    if _valid_key(k):
                        return k
        except Exception:
            pass
        return ''
    
    key = _from_pool('opencode-go')
    if key:
        return key
    key = _from_pool('custom:opencode-go')
    if key:
        return key
    
    # 4. Local opencode auth.json
    if os.path.exists(OPENCODE_AUTH_PATH):
        try:
            with open(OPENCODE_AUTH_PATH) as f:
                data = _json.load(f)
            key = data.get('opencode-go', '')
            if _valid_key(key):
                return key
        except Exception:
            pass
    
    # 5. Final fallback
    return os.environ.get('OPENCODE_GO_API_KEY', '')


# Model list for fake endpoints (from actual API discovery)
OPENCODE_GO_MODELS = [
    {'id': 'deepseek-v4-flash'}, {'id': 'deepseek-v4-pro'},
    {'id': 'glm-5'}, {'id': 'glm-5.1'},
    {'id': 'minimax-m2.7'}, {'id': 'minimax-m2.5'},
    {'id': 'minimax-m3'},
    {'id': 'kimi-k2.6'}, {'id': 'kimi-k2.5'},
    {'id': 'mimo-v2.5'}, {'id': 'mimo-v2.5-pro'},
    {'id': 'qwen3.7-max'}, {'id': 'qwen3.7-plus'}, {'id': 'qwen3.6-plus'},
]


ENV_PATH = os.path.expanduser('~/.hermes/.env')

def _write_key_to_env(new_key):
    try:
        lines = []
        found = False
        if os.path.exists(ENV_PATH):
            with open(ENV_PATH) as f:
                for line in f:
                    if line.startswith('OPENCODE_GO_API_KEY='):
                        lines.append('OPENCODE_GO_API_KEY=' + new_key + '\n')
                        found = True
                    else:
                        lines.append(line)
        if not found:
            lines.append('OPENCODE_GO_API_KEY=' + new_key + '\n')
        with open(ENV_PATH, 'w') as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"[PROXY] _write_key_to_env ERROR: {e}", file=sys.stderr, flush=True)
        return False


def _resp_json(s, code, data):
    s.send_response(code)
    s.send_header('Content-Type', 'application/json')
    s.end_headers()
    s.wfile.write(_json.dumps(data).encode())


class Handler(BaseHTTPRequestHandler):
    def do_POST(s):
        if s.path == '/key':
            cl = int(s.headers.get('Content-Length', 0))
            body = s.rfile.read(cl) if cl else b''
            try:
                data = _json.loads(body)
                new_key = data.get('key', '')
                if not new_key.startswith('sk-'):
                    _resp_json(s, 400, {'error': 'invalid key format'})
                    return
                ok = _write_key_to_env(new_key)
                _resp_json(s, 200 if ok else 500, {'status': 'ok' if ok else 'error', 'key_len': len(new_key)})
                print(f"[PROXY] POST /key -> {'OK' if ok else 'FAIL'} ({len(new_key)} chars)", file=sys.stderr, flush=True)
            except Exception as e:
                _resp_json(s, 400, {'error': str(e)})
            return
        if s.path == '/v1/responses':
            s.path = '/v1/chat/completions'
        s._fw('POST')

    def do_GET(s):
        if s.path == '/key':
            key = get_api_key()
            _resp_json(s, 200, {'key_exists': bool(key), 'key_prefix': key[:10]+'...' if key else '', 'key_len': len(key)})
            return
        fake_responses = {
            '/api/tags': {'models': [{'name': m['id']} for m in OPENCODE_GO_MODELS]},
            '/v1/models': {'object': 'list', 'data': OPENCODE_GO_MODELS},
            '/api/v1/models': {'object': 'list', 'data': OPENCODE_GO_MODELS},
            '/v1/props': {'opencode_go': True, 'supports_tools': True, 'supports_streaming': True},
            '/props': {'opencode_go': True},
            '/version': {'version': 'go-1.0'},
            '/api/show': {'license': 'MIT', 'modelfile': '', 'parameters': '', 'template': ''},
        }
        if s.path.startswith('/api/show'):
            s.send_response(200)
            s.send_header('Content-Type', 'application/json')
            s.end_headers()
            s.wfile.write(_json.dumps({'license': 'MIT', 'modelfile': '', 'parameters': '', 'template': ''}).encode())
            print(f"[PROXY] GET {s.path} -> FAKE 200", file=sys.stderr, flush=True)
            return
        if s.path in fake_responses:
            s.send_response(200)
            s.send_header('Content-Type', 'application/json')
            s.end_headers()
            s.wfile.write(_json.dumps(fake_responses[s.path]).encode())
            print(f"[PROXY] GET {s.path} -> FAKE 200", file=sys.stderr, flush=True)
        else:
            s.send_response(404)
            s.end_headers()
            print(f"[PROXY] GET {s.path} -> 404", file=sys.stderr, flush=True)

    def do_OPTIONS(s):
        s.send_response(200)
        s.send_header('Access-Control-Allow-Origin', '*')
        s.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        s.send_header('Access-Control-Allow-Headers', '*')
        s.end_headers()

    def log_message(s, *a):
        print(f"[PROXY] {s.command} {s.path}", file=sys.stderr, flush=True)

    def _fw(s, method):
        cl = int(s.headers.get('Content-Length', 0))
        body = s.rfile.read(cl) if cl else None

        # Responses API -> Chat Completions transform
        if body and b'"input"' in body:
            try:
                data = _json.loads(body)
                if 'input' in data:
                    data['messages'] = []
                    for msg in data.pop('input'):
                        role = msg.get('role', 'user')
                        if role == 'developer':
                            role = 'system'
                        data['messages'].append({'role': role, 'content': msg.get('content', '')})
                    for key in ['text', 'store', 'include', 'prompt_cache_key', 'reasoning']:
                        data.pop(key, None)
                    body = _json.dumps(data).encode()
            except Exception:
                pass

        # Ensure max_tokens
        if body:
            try:
                data = _json.loads(body)
                current_mt = data.get('max_tokens')
                if current_mt is None or current_mt < 4096:
                    data['max_tokens'] = 32768
                    body = _json.dumps(data).encode()
            except Exception:
                pass

        # Get fresh API key on every request (supports Dashboard/Bitwarden updates without restart)
        api_key = get_api_key()
        if body:
            try:
                req_data = _json.loads(body)
                model = req_data.get('model', '?')
                key_preview = api_key[:12] + '...' if api_key else 'NONE'
                print(f"[PROXY] POST {s.path} | model={model} | key={key_preview} | {len(body)}b", file=sys.stderr, flush=True)
            except:
                print(f"[PROXY] POST {s.path} | body={len(body)}b", file=sys.stderr, flush=True)

        req = urllib.request.Request(TARGET + s.path, data=body, method=method)
        for h, v in s.headers.items():
            if h.lower() in ('host', 'content-length', 'user-agent', 'authorization'):
                continue
            req.add_header(h, v)
        req.add_header('User-Agent', BROWSER_UA)
        if api_key:
            req.add_header('Authorization', f'Bearer {api_key}')

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
                if not chunk:
                    break
                full_body += chunk
                s.wfile.write(chunk)
            print(f"[PROXY] ← {resp.status} | {len(full_body)}b | {full_body[:120]}", file=sys.stderr, flush=True)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            s.send_response(e.code)
            s.end_headers()
            s.wfile.write(err_body)
            print(f"[PROXY] ← HTTP {e.code} | {err_body[:200]}", file=sys.stderr, flush=True)
        except Exception as e:
            s.send_response(502)
            s.end_headers()
            s.wfile.write(_json.dumps({'error': str(e)}).encode())
            print(f"[PROXY] ← ERROR: {e}", file=sys.stderr, flush=True)


if __name__ == '__main__':
    # Spawn BWS -> .env sync watcher (Dashboard key entry integration)
    _ws = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'watch_bws_sync.py')
    _wl = os.path.expanduser('~/.hermes/logs/watch_bws_sync.log')
    if os.path.exists(_ws):
        try:
            _cmd = '/usr/bin/nohup /usr/local/bin/python3 %s >> %s 2>&1 &' % (_ws, _wl)
            os.system(_cmd)
        except Exception as e:
            pass
    key = get_api_key()
    print(f'OpenCode Go proxy :{PORT} -> {TARGET} | key={"FOUND" if key else "MISSING"} ({len(key)} chars)', flush=True)
    HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
