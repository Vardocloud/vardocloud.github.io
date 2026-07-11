#!/bin/bash
# LiteRouter modellerini listele
source /home/ubuntu/.hermes/.env

echo "=== LITEROUTER API TEST ==="
echo "Key length: ${#LITEROUTER_API_KEY}"

echo ""
echo "=== Available Models ==="
curl -s https://api.literouter.com/v1/models \
  -H "Authorization: Bearer $LITER...EY" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
models = data.get('data', [])
print(f'Total: {len(models)}')
free = [m['id'] for m in models if ':free' in m['id']]
other = [m['id'] for m in models if ':free' not in m['id']]

print(f'\n🆓 FREE ({len(free)}):')
for m in sorted(free):
    print(f'  • {m}')

print(f'\n🔸 OTHER ({len(other)}):')
for m in other:
    print(f'  • {m}')
" 2>&1

echo ""
echo "=== Chat Test (deepseek-v3.2:free) ==="
curl -s https://api.literouter.com/v1/chat/completions \
  -H "Authorization: Bearer $LITER...EY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v3.2:free","messages":[{"role":"user","content":"say hello in 2 words"}],"max_tokens":10}' \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
if 'choices' in d:
    print('✅ Response:', d['choices'][0]['message']['content'])
elif 'error' in d:
    print('❌ Error:', d['error'])
else:
    print('❌:', str(d)[:200])
" 2>&1