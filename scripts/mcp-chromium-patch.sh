#!/bin/bash
# MCP Chromium Patch — Re-apply executablePath override after npm update
# Vanitas — 5 Tem 2026
#
# Ensures MCP v2.0.0 uses system Chromium (/usr/bin/chromium) instead of
# bundled Playwright Chromium, so cookie encryption keys match keepalive.
#
# Run after: npm install -g notebooklm-mcp@latest
# Or manually: bash ~/.hermes/scripts/mcp-chromium-patch.sh

PATCH_TARGET="/home/ubuntu/.npm-global/lib/node_modules/notebooklm-mcp/dist/session/shared-context-manager.js"
WRAPPER="/home/ubuntu/.local/bin/notebooklm-mcp-wrapper.sh"
CHROMIUM_PATH="/usr/bin/chromium"

# 1. Check if patch already applied
if grep -q "Vanitas patch" "$PATCH_TARGET" 2>/dev/null; then
    echo "✅ Patch zaten uygulanmış — atlanıyor"
else
    echo "🔧 Patch uygulanıyor: executablePath → $CHROMIUM_PATH"
    
    # Backup original
    cp "$PATCH_TARGET" "${PATCH_TARGET}.bak.$(date +%s)"
    
    # Apply patch via sed
    sed -i 's/const baseLaunchOptions = {/\/\/ Vanitas patch: use system Chromium for cookie compat\nconst nbChromiumPath = process.env.NOTEBOOKLM_CHROMIUM_PATH;\nconst baseLaunchOptions = {\n            ...(nbChromiumPath \&\& { executablePath: nbChromiumPath }),/' "$PATCH_TARGET"
    
    if grep -q "Vanitas patch" "$PATCH_TARGET"; then
        echo "✅ Patch uygulandı"
    else
        echo "❌ Patch başarısız — manuel müdahale gerek"
        exit 1
    fi
fi

# 2. Check wrapper env var
if grep -q "NOTEBOOKLM_CHROMIUM_PATH" "$WRAPPER" 2>/dev/null; then
    echo "✅ Wrapper env var zaten var"
else
    echo "🔧 Wrapper güncelleniyor..."
    sed -i "s|NOTEBOOKLM_PERSISTENT_SESSION=\"true\"|NOTEBOOKLM_PERSISTENT_SESSION=\"true\"\nexport NOTEBOOKLM_CHROMIUM_PATH=\"$CHROMIUM_PATH\"|" "$WRAPPER"
    echo "✅ Wrapper güncellendi"
fi

# 3. Verify chromium exists
if [ -x "$CHROMIUM_PATH" ]; then
    echo "✅ Chromium binary mevcut: $CHROMIUM_PATH"
else
    echo "⚠️  Uyarı: $CHROMIUM_PATH bulunamadı — patch çalışmaz"
fi

echo ""
echo "📋 Durum:"
echo "  MCP binary wrapper → $(readlink -f ~/.local/bin/notebooklm-mcp 2>/dev/null || echo 'symlink bozuk')"
echo "  Chromium path     → $CHROMIUM_PATH"
echo "  Env var           → NOTEBOOKLM_CHROMIUM_PATH=$CHROMIUM_PATH"
echo ""
echo "Sonraki adım: VNC'den re_auth yapılacak"
echo "  noVNC: http://localhost:6080 (veya cloudflared tunnel)"
