#!/bin/bash
# Vanitas Voice Test Reporter — cron job wrapper
# Reports test session summary to Edel

cd /home/ubuntu/vanitas-web/soniox-server
python3 voice_test_analyzer.py --hours 24 2>/dev/null || echo "❌ Test analizi çalışmadı"