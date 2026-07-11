#!/bin/bash
# Hermes Daily Summary — stdout + Hermes delivers to Telegram
H="$HOME"

DISK_PCT=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
DISK_FREE=$(df -h / | tail -1 | awk '{print $4}')

DATA_PCT=$(df -h /data | tail -1 | awk '{print $5}' | tr -d '%')
DATA_FREE=$(df -h /data | tail -1 | awk '{print $4}')

MEM_PCT=$(free | awk '/Mem/{printf "%.0f", $3/$2*100}')
MEM_FREE=$(free -h | awk '/Mem/{print $7}')

GW_STATUS="OK"
curl -sf http://127.0.0.1:8642/health >/dev/null 2>&1 || GW_STATUS="DOWN"

UP=$(uptime -p | sed 's/up //')

echo "📊 Gunluk Durum"
echo "🖥️ Root /: ${DISK_FREE} bos (${DISK_PCT}%)"
echo "💾 /data: ${DATA_FREE} bos (${DATA_PCT}%)"
echo "🧠 RAM: ${MEM_PCT}% (${MEM_FREE} bos)"
echo "🌐 Gateway: ${GW_STATUS}"
echo "⏱️ Uptime: ${UP}"

# Critical alerts
if [ "$DISK_PCT" -gt 85 ]; then echo "🚨 Root disk kritik!"; fi
if [ "$DATA_PCT" -gt 85 ]; then echo "🚨 /data disk kritik!"; fi
if [ "$MEM_PCT" -gt 85 ]; then echo "🚨 RAM kritik!"; fi
if [ "$GW_STATUS" = "DOWN" ]; then echo "🚨 Gateway DOWN!"; fi
