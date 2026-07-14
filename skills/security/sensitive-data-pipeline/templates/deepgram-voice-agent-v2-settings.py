#!/usr/bin/env python3
"""
Deepgram Voice Agent v2 — Relay Server Template
Browser WS → This server → Deepgram Agent WS (STT+LLM+TTS in one)

KEY INSIGHT: model MUST be inside provider, NOT at think level.
"""

# ─── Settings (the CORRECT format) ───
SETTINGS = {
    "type": "Settings",
    "audio": {
        "input": {"encoding": "linear16", "sample_rate": 24000},
        "output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"},
    },
    "agent": {
        "language": "en",
        "listen": {"provider": {"type": "deepgram", "model": "nova-3"}},
        "think": {
            "provider": {
                "type": "open_ai",
                "model": "gpt-4o-mini",  # ← MUST be inside provider!
            },
            "endpoint": {  # optional — omit for Deepgram managed LLM
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "headers": {
                    "Authorization": "Bearer $OPENROUTER_KEY",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://hermes.local",
                    "X-Title": "Vanitas Voice",
                },
            },
            "prompt": "You are Vanitas, a warm AI companion. Keep answers 1-2 sentences.",
            "temperature": 0.8,
        },
        "speak": {"provider": {"type": "deepgram", "model": "aura-2-asteria-en"}},
        "greeting": "Hey there! This is Vanitas. How's your day going?",
    },
}

# ─── Connection ───
# ws_url = "wss://api.eu.deepgram.com/v1/agent/converse"
# headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
# connect → send settings → forward browser audio bytes → receive ConversationText + audio bytes

# Full server: /home/ubuntu/voice-agent-venv/voice_agent_v2.py
