#!/bin/bash
# Chromium Cleanup — 30dk + CPU idle (<%1) ise kapat
# Cron ile her 15dk çalışır
# Zoom/Meet kaydı için remote-debugging-port Chrome'ları atla

IDLE_MINUTES=30
CPU_THRESHOLD=1.0
LOG="/home/ubuntu/.hermes/logs/chromium-cleanup.log"

killed=0

ps -eo pid,etime,pcpu,comm,args --no-headers | grep -iE 'chrom|puppeteer' | while read pid etime pcpu comm args; do
    # Skip Chrome instances with remote debugging port (Zoom/Meet kaydı)
    if echo "$args" | grep -q 'remote-debugging-port'; then
        continue
    fi
    
    # Parse elapsed time to minutes
    mins=$(echo "$etime" | awk -F'[-:]' '{
        if (NF==5) print $2*1440 + $3*60 + $4     # DD-HH:MM:SS
        else if (NF==4) print $1*1440 + $2*60 + $3
        else if (NF==3) print $1*60 + $2
        else print $1
    }')
    
    # Only kill if old AND idle
    if [[ "$mins" -gt "$IDLE_MINUTES" ]] && (( $(echo "$pcpu < $CPU_THRESHOLD" | bc -l 2>/dev/null) )); then
        kill "$pid" 2>/dev/null && {
            echo "$(date): Killed $comm (pid=$pid, ${mins}dk, CPU=${pcpu}%)" | tee -a "$LOG"
            killed=$((killed + 1))
        }
    fi
done

[[ "$killed" -eq 0 ]] || echo "$(date): Toplam $killed Chromium kapatıldı" >> "$LOG"
