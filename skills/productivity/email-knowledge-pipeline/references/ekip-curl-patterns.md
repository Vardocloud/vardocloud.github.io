# EKİP cURL Patterns — Working vs Failing

## Analist (GLM-5.1, port 19998)

### FAILED — complex inline JSON with special chars
```bash
curl -s --max-time 45 http://127.0.0.1:19998/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.1","messages":[{"role":"user","content":"Bu email listesini siniflandir... '"$(cat /tmp/email_list.json)"'"}],"max_tokens":2000}'
# Result: {"type":"error","error":{"type":"error","message":"Internal server error"}}
# Cause: Turkish chars + inline JSON escaping in bash subshell
```

### FAILED — max_tokens too low (reasoning overflow)
```bash
curl ... max_tokens=1000
# Result: finish_reason="length", content="" (all tokens went to reasoning_content)
```

### WORKING — plain text list, max_tokens=4000, SADECE çıktı direktifi
```bash
curl -s --max-time 45 http://127.0.0.1:19998/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.1",
    "messages": [{
      "role": "user",
      "content": "SADECE çıktıyı ver, düşünme sürecini atla. Su email listesini kategorize et... \n\n#1 Sender: Subject\n#2 Sender: Subject"
    }],
    "max_tokens": 4000,
    "temperature": 0.1
  }'
# Result: reasoning_content dolar, content de dolar — 4000 minimum
# 500-2000 arası: finish_reason="length", content="" riski yüksek
```

## Yazar (GPT-5.4-mini, port 19999)

### Always working — simple pattern
```bash
curl -s --max-time 30 http://127.0.0.1:19999/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.4-mini","messages":[{"role":"user","content":"Su emaili 2 cumleyle Turkce ozetle: ICERIK"}],"max_tokens":300}'
# Stable, always returns content, no reasoning_content
```
