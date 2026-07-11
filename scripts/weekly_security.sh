#!/bin/bash
# Önce /tmp/security_score.txt varsa temizle (eğer root'sa silinemeyebilir ama deneriz)
rm -f /tmp/security_score.txt 2>/dev/null
touch /tmp/security_score.txt 2>/dev/null
exec /home/ubuntu/.hermes/scripts/security_scan.sh --weekly
