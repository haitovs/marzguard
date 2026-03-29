#!/bin/bash
set -e

echo "Starting MarzGuard..."

# Start nginx if TLS certs exist
if [ -f /etc/letsencrypt/live/default/fullchain.pem ]; then
    echo "TLS certificates found, starting nginx..."
    nginx
else
    echo "No TLS certificates found, skipping nginx (direct access on :8000)"
fi

# Run database migrations
cd /app
echo "Running database setup..."

# Start the application
exec uvicorn src.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 1 \
    --log-level "${LOG_LEVEL:-info}"
