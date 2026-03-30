# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm ci
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# Stage 2: Python backend
FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy backend
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy built frontend (vite outputs to ../src/ui/dist/ relative to frontend/)
COPY --from=frontend-build /app/src/ui/dist/ ./src/ui/dist/

# Copy nginx config
COPY configs/nginx.conf /etc/nginx/sites-available/default

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 3004

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://127.0.0.1:3004/health || exit 1

# Startup script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
