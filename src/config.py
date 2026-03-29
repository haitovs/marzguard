from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Marzban
    marzban_base_url: str = "https://panel.example.com:8443"
    marzban_username: str = "admin"
    marzban_password: str = "changeme"

    # MarzGuard Admin
    admin_username: str = "admin"
    admin_password: str = "changeme"

    # JWT
    jwt_secret: str = "change_this_to_a_random_secret_key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/marzguard.db"

    # IP Tracking
    default_ip_limit: int = 0
    ip_ttl_seconds: int = 300
    enforcement_interval: int = 30
    reenable_check_interval: int = 60
    default_reenable_delay: int = 300

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Webhook
    webhook_secret: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
