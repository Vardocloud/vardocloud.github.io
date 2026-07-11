#!/bin/bash
# Önce /tmp/security_score.txt varsa temizle
rm -f /tmp/security_score.txt 2>/dev/null
touch /tmp/security_score.txt 2>/dev/null
exec /home/ubuntu/.hermes/scripts/security_scan.sh --daily
