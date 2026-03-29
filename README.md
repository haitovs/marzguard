# MarzGuard

Self-hosted IP limit management for [Marzban](https://github.com/Gozargah/Marzban) proxy panels.

## Features

- **Per-user IP limiting** with 3-tier cascade: user override > policy group > global default
- **Real-time monitoring** via Marzban Xray log streaming (WebSocket)
- **Auto-enforcement** — disables users exceeding limits, re-enables after cooldown
- **Web dashboard** with live connection tracking
- **Policy groups** — assign IP limits to groups of users
- **Audit logging** — full history of enforcement actions
- **Telegram notifications** — alerts on violations and enforcement
- **Multi-node support** — monitors main server + all connected nodes
- **IPv6 support** — normalizes to /64 prefix (same device = same subnet)
- **Docker deployment** — single container with TLS

## Quick Start

### Docker (recommended)

```bash
cp .env.example .env
# Edit .env with your Marzban credentials and settings
docker compose up -d
```

Access dashboard at `https://your-server:8443`

### Development

```bash
# Backend
pip install -e ".[dev]"
cp .env.example .env
python -m src.main

# Frontend
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
pip install -e ".[dev]"
pytest
```

## Configuration

All settings via `.env` file. See `.env.example` for all options.

| Variable | Default | Description |
|----------|---------|-------------|
| `MARZBAN_BASE_URL` | - | Marzban panel URL |
| `MARZBAN_USERNAME` | - | Marzban admin username |
| `MARZBAN_PASSWORD` | - | Marzban admin password |
| `ADMIN_USERNAME` | admin | MarzGuard admin username |
| `ADMIN_PASSWORD` | - | MarzGuard admin password |
| `DEFAULT_IP_LIMIT` | 2 | Global default IP limit |
| `IP_TTL_SECONDS` | 300 | Seconds before an IP is considered inactive |
| `TELEGRAM_BOT_TOKEN` | - | Telegram bot token (optional) |
| `TELEGRAM_CHAT_ID` | - | Telegram chat ID for notifications |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## API

See [docs/API.md](docs/API.md) for the full API reference.
