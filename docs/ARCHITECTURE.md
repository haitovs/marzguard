# MarzGuard Architecture

## Overview

MarzGuard is a self-hosted IP limit management system for Marzban proxy panels. It provides per-user and per-policy IP limiting with a web dashboard.

## Components

### Core Engine
- **IPTracker** (`src/core/tracker.py`): Thread-safe in-memory TTL dict tracking active IPs per user
- **LogConsumer** (`src/core/log_consumer.py`): Async WebSocket consumer for Marzban Xray log streams
- **LogParser** (`src/core/log_parser.py`): Regex-based parser for Xray access log lines
- **Enforcer** (`src/core/enforcer.py`): Violation detection + disable/re-enable pipeline
- **Scheduler** (`src/core/scheduler.py`): APScheduler jobs for periodic enforcement

### Services
- **MarzbanClient** (`src/services/marzban.py`): Async httpx client for Marzban REST API
- **NotificationDispatcher** (`src/services/notify.py`): Multi-channel notification system
- **TelegramNotifier** (`src/services/telegram.py`): Telegram Bot API integration

### API
- FastAPI REST endpoints under `/api/v1/`
- WebSocket endpoint at `/ws/live` for real-time dashboard
- JWT authentication with bcrypt password hashing

### Frontend
- React 18 SPA with Vite and TailwindCSS
- Pages: Dashboard, Users, Policies, Settings, Audit Log
- Real-time updates via WebSocket

### Data Flow

```
Marzban Xray Logs (WebSocket)
    → LogConsumer (parses each line)
    → IPTracker (records username + IP with TTL)
    → Enforcer (periodic check every 30s)
    → Marzban API (disable/enable users)
    → AuditLog (database) + Telegram (notifications)
```

### Limit Resolution (3-tier cascade)

```
user.ip_limit (if set) → user.policy.default_ip_limit → global DEFAULT_IP_LIMIT
```

## Deployment

Single Docker container running:
- Nginx (TLS termination on :8443)
- Uvicorn (FastAPI on :8000, internal only)
- 1 worker (required: tracker is in-memory)

SQLite database stored in Docker volume.
