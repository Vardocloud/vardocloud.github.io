#!/bin/bash
# MCP Chromium Patch — Re-apply executablePath override + selector fix after npm update
# Vanitas — 5 Tem 2026 (v2: selector fix eklendi)
#
# 1. executablePath: MCP'nin bundled Chromium yerine sistem Chromium'unu kullanmasını sağlar
#    → cookie şifreleme anahtarları uyumlu olur
# 2. Selector fix: NotebookLM arayüzü güncellendi (query-box-input → query-box-textarea)
#    → MCP chat input'u bulabilir
#
# Run after: npm install -g notebooklm-mcp@latest
# Or manually: bash ~/.hermes/scripts/mcp-chromium-patch.sh

SHARED_CTX="/home/ubuntu/.npm-global/lib/node_modules/notebooklm-mcp/dist/session/shared-context-manager.js"
BROWSER_SESSION="/home/ubuntu/.npm-global/lib/node_modules/notebooklm-mcp/dist/session/browser-session.js"
WRAPPER="/home/ubuntu/.local/bin/notebooklm-mcp-wrapper.sh"
CHROMIUM_PATH="/usr/bin/chromium"

NEED_WRAPPER_UPDATE=false

# 1. executablePath override (shared-context-manager.js)
if [ -f "$SHARED_CTX" ]; then
    if grep -q "Vanitas patch" "$SHARED_CTX" 2>/dev/null; then
        echo "✅ executablePath patch zaten uygulanmış"
    else
        echo "🔧 executablePath patch uygulanıyor..."
        cp "$SHARED_CTX" "${SHARED_CTX}.bak.$(date +%s)"
        sed -i 's|const baseLaunchOptions = {|// Vanitas patch: use system Chromium for cookie compat\nconst nbChromiumPath = process.env.NOTEBOOKLM_CHROMIUM_PATH;\nconst baseLaunchOptions = {\n            ...(nbChromiumPath \&\& { executablePath: nbChromiumPath }),|' "$SHARED_CTX"
        if grep -q "Vanitas patch" "$SHARED_CTX"; then
            echo "✅ executablePath patch uygulandı"
            NEED_WRAPPER_UPDATE=true
        else
            echo "❌ executablePath patch başarısız"
        fi
    fi
fi

# 2. Selector fix: query-box-input → query-box-textarea (browser-session.js)
if [ -f "$BROWSER_SESSION" ]; then
    if grep -q "query-box-input" "$BROWSER_SESSION" 2>/dev/null; then
        echo "🔧 Selector fix uygulanıyor (query-box-input → query-box-textarea)..."
        cp "$BROWSER_SESSION" "${BROWSER_SESSION}.bak.$(date +%s)"
        sed -i 's/textarea\.query-box-input/textarea.query-box-textarea/g' "$BROWSER_SESSION"
        if grep -q "query-box-input" "$BROWSER_SESSION"; then
            echo "⚠️ Bazı selector'lar değişmedi, manuel kontrol et"
        else
            echo "✅ Selector fix uygulandı"
        fi
    else
        echo "✅ Selector fix zaten uygulanmış (query-box-input bulunamadı)"
    fi
fi

# 3. Wrapper env var
if grep -q "NOTEBOOKLM_CHROMIUM_PATH" "$WRAPPER" 2>/dev/null; then
    echo "✅ Wrapper env var zaten var"
else
    echo "🔧 Wrapper güncelleniyor..."
    sed -i 's|NOTEBOOKLM_PERSISTENT_SESSION="true"|NOTEBOOKLM_PERSISTENT_SESSION="true"\nexport NOTEBOOKLM_CHROMIUM_PATH="'"$CHROMIUM_PATH"'"|' "$WRAPPER"
    echo "✅ Wrapper güncellendi"
fi

# 4. Verify
if [ -x "$CHROMIUM_PATH" ]; then
    echo "✅ Chromium binary: $CHROMIUM_PATH"
else
    echo "⚠️ $CHROMIUM_PATH bulunamadı"
fi

echo ""
echo "📋 Durum:"
echo "  executablePath → $([ -f "$SHARED_CTX" ] && grep -c 'Vanitas patch' "$SHARED_CTX" 2>/dev/null || echo 0) patch"
echo "  Selector fix  → $([ -f "$BROWSER_SESSION" ] && grep -c 'query-box-input' "$BROWSER_SESSION" 2>/dev/null || echo 0) eski selector kaldı"
echo "  Wrapper       → $([ -f "$WRAPPER" ] && grep -c 'NOTEBOOKLM_CHROMIUM_PATH' "$WRAPPER" 2>/dev/null || echo 0) env var"
echo ""
echo "Sonraki adım: re_auth (VNC) veya keepalive CDP kullan"
