#!/bin/bash
# Post-Update Servis Bütünlük Kontrolü
# hermes update sonrası otomatik çalışır
# Tüm servis ExecStart binary'lerini kontrol eder — eksikse disable + uyarı

LOG="/home/ubuntu/.hermes/logs/post-update.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

send_alert() {
    local msg="$1"
    /home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -c "
import requests
requests.post('https://api.telegram.org/bot7927784182:AAHes4QI2vR6m5mTJyJFfpyFOpEgoFH7Miyk/sendMessage', json={'chat_id': '6306976553', 'text': '🔧 POST-UPDATE: ${msg}'})
" 2>/dev/null
}

failed=0

log "Post-update integrity check starting..."

while IFS= read -r unit_file; do
    [[ -z "$unit_file" ]] && continue
    
    unit_name=$(basename "$unit_file")
    
    exec_start=$(grep -E '^ExecStart=' "$unit_file" 2>/dev/null | head -1 | sed 's/ExecStart=//')
    [[ -z "$exec_start" ]] && continue
    
    binary=$(echo "$exec_start" | awk '{print $1}')
    
    if ! command -v "$binary" &>/dev/null && ! test -f "$binary"; then
        log "MISSING BINARY: $unit_name → $binary"
        
        systemctl --user stop "$unit_name" 2>/dev/null
        systemctl --user disable "$unit_name" 2>/dev/null
        
        failed=$((failed + 1))
        send_alert "⚠️ Servis DISABLE edildi: ${unit_name}\nBinary bulunamadı: ${binary}"
    fi
done < <(find /home/ubuntu/.config/systemd/user/ -name '*.service' 2>/dev/null)

log "Check done. ${failed} failed services disabled."
exit 0
