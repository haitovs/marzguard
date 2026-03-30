#!/bin/bash
set -e

echo "Starting MarzGuard..."

# Start nginx if TLS certs exist
if [ -f /etc/letsencrypt/live/default/fullchain.pem ]; then
    echo "TLS certificates found, starting nginx..."
    nginx
fi

# Run database migrations
cd /app
echo "Running database setup..."

# Start the application
exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-3004}" \
    --workers 1 \
    --log-level "${LOG_LEVEL:-info}"
