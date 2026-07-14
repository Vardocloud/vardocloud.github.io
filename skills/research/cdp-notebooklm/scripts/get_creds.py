#!/usr/bin/env python3
"""bw-serve HTTP API'sinden NotebookLM Google credentials çeker."""
import urllib.request, json

ITEM_ID = '75750341-e3ca-43b7-a'
BW_SERVE = 'http://127.0.0.1:8087'

data = json.loads(urllib.request.urlopen(f'{BW_SERVE}/object/item/{ITEM_ID}').read())
login = data.get('data', {}).get('login', {})
print(login.get('username', ''))
print(login.get('password', ''))
print(login.get('totp', ''))
