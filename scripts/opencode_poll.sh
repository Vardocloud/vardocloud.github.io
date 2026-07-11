#!/bin/bash
source ~/.hermes/.env
export OPENAI_BASE_URL="http://127.0.0.1:19999/v1"
export OPENAI_API_KEY="$POLLINATIONS_API_KEY"
exec opencode "$@"
