#!/bin/bash
# WARP proxy günlük restart — child process birikmesini önler
systemctl restart warp-proxy 2>&1
echo "WARP restarted at $(date)"
