#!/bin/sh

echo "⏳ Czekam aż Ollama zacznie poprawnie obsługiwać POST na /api/chat..."

until [ "$(curl -s -o /dev/null -w "%{http_code}" -X POST http://ollama:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3", "messages": [{"role": "user", "content": "Cześć!"}]}')" -eq 200 ]; do
    echo "🕐 Ollama jeszcze niegotowa..."
    sleep 2
done

echo "✅ Ollama jest gotowa do obsługi POST /api/chat!"
exec "$@"