import os
from dotenv import load_dotenv

load_dotenv()

def _env_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, default))
    except Exception:
        return float(default)

def _env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except Exception:
        return int(default)

class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    chat_id: str = os.getenv("CHAT_ID", "")
    service_port: int = _env_int("SERVICE_PORT", 8000)
    poll_interval_sec: int = _env_int("POLL_INTERVAL_SEC", 5)
    threshold_pct: float = _env_float("THRESHOLD_PCT", 0.5)
    min_trade_usdt: float = _env_float("MIN_TRADE_USDT", 100)

settings = Settings()
