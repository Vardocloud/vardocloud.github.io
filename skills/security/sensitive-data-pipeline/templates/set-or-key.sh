#!/bin/bash
# OpenRouter / Zenmux API Key Storage Script
# Run via SSH: bash /tmp/set_or_key.sh
# Writes key to /tmp/.or_key with chmod 600
# Key never enters any AI model context — goes directly to disk

read -s -p "🔑 OpenRouter API Key: " OR_KEY
echo ""
if [ -z "$OR_KEY" ]; then
    echo "❌ Key boş, işlem iptal."
    exit 1
fi
echo "$OR_KEY" > /tmp/.or_key
chmod 600 /tmp/.or_key
echo "✅ Key kaydedildi → /tmp/.or_key (chmod 600)"
echo "📋 Kontrol: $(wc -c < /tmp/.or_key) byte yazıldı"
