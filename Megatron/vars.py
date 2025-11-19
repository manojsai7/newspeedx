from os import environ
from typing import Optional, Union

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            "Create your own credentials via @BotFather / my.telegram.org and set them before starting Megatron."
        )
    return value


def _optional(name: str, default: Optional[str] = None) -> Optional[str]:
    value = environ.get(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def _as_int(value: Optional[str], default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(value)


def _as_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_channel(value: str, *, field_name: str = "BIN_CHANNEL") -> int:
    cleaned = value.strip()
    if not cleaned:
        raise RuntimeError(f"{field_name} cannot be empty.")
    is_negative = cleaned.startswith("-")
    digits = cleaned[1:] if is_negative else cleaned
    if not digits.isdigit():
        raise RuntimeError(
            f"{field_name} must be a numeric Telegram channel ID (e.g. -100xxxx). "
            "Public usernames are not accepted in this deployment."
        )
    channel_id = int(cleaned)
    if not str(channel_id).startswith("-100"):
        raise RuntimeError(
            f"{field_name} must start with -100 (supergroup/channel IDs). Got {channel_id}."
        )
    return channel_id


def _parse_optional_channel(name: str) -> Optional[int]:
    raw = _optional(name)
    if raw is None:
        return None
    try:
        return _parse_channel(raw, field_name=name)
    except RuntimeError as exc:
        raise RuntimeError(str(exc))


class Var(object):
    MULTI_CLIENT = False
    API_ID = _as_int(_require("API_ID"))
    API_HASH = _require("API_HASH")
    SESSION_NAME = _optional('SESSION_NAME', 'AvishkarPatil')
    BOT_TOKEN = _require("BOT_TOKEN")
    BROADCAST_AS_COPY = _as_bool(_optional("BROADCAST_AS_COPY"))
    SLEEP_THRESHOLD = _as_int(_optional("SLEEP_THRESHOLD", "60"), 60)
    WORKERS = _as_int(_optional("WORKERS", "6"), 6)
    BIN_CHANNEL = _parse_channel(_require("BIN_CHANNEL"))  # mandatory for uploads
    PORT = _as_int(_optional("PORT", "8000"), 8000)
    BIND_ADDRESS = _optional("WEB_SERVER_BIND_ADDRESS", "0.0.0.0")
    PING_INTERVAL = _as_int(_optional("PING_INTERVAL", "240"), 240)  # Default 4 minutes (Koyeb sleeps after 5min)
    HAS_SSL = _as_bool(_optional("HAS_SSL"))
    OWNER_ID = _as_int(_require('OWNER_ID'))
    NO_PORT = _as_bool(_optional("NO_PORT"))
    MAX_LOGIN_FLOODWAIT = _as_int(_optional("MAX_LOGIN_FLOODWAIT", "900"), 900)
    LOGIN_FLOODWAIT_PADDING = _as_int(_optional("LOGIN_FLOODWAIT_PADDING", "5"), 5)
    
    # Detect platform
    if "DYNO" in environ:
        ON_HEROKU = True
        ON_KOYEB = False
        APP_NAME = _optional("APP_NAME", "megatron")
    elif "KOYEB_PUBLIC_DOMAIN" in environ or "KOYEB_DEPLOYMENT_ID" in environ:
        ON_HEROKU = False
        ON_KOYEB = True
        APP_NAME = _optional("APP_NAME")  # Optional for Koyeb
    else:
        ON_HEROKU = False
        ON_KOYEB = False
        APP_NAME = None
    DATABASE_URL = _require('DATABASE_URL')
    APP_SECRET = _optional("APP_SECRET") or BOT_TOKEN
    LINK_TTL_SECONDS = _as_int(_optional("LINK_TTL_SECONDS", "43200"), 43200)
    SHORT_LINK_TTL_SECONDS = _as_int(_optional("SHORT_LINK_TTL_SECONDS", "604800"), 604800)
    USER_RATE_LIMIT = _as_int(_optional("USER_RATE_LIMIT", "12"), 12)
    USER_RATE_WINDOW = _as_int(_optional("USER_RATE_WINDOW", "60"), 60)
    USER_DAILY_QUOTA = _as_int(_optional("USER_DAILY_QUOTA", "0"), 0)
    MAX_FILE_SIZE_MB = _as_int(_optional("MAX_FILE_SIZE_MB", "2048"), 2048)
    UPDATES_CHANNEL = _parse_optional_channel("UPDATES_CHANNEL")
    BANNED_CHANNELS = list(
        set(
            int(x)
            for x in str(_optional("BANNED_CHANNELS", "-100")).split()
            if x
        )
    )
    # Auto-detect FQDN based on platform
    if ON_KOYEB:
        # Koyeb provides KOYEB_PUBLIC_DOMAIN automatically
        FQDN = _optional("FQDN") or _optional("KOYEB_PUBLIC_DOMAIN") or _optional("KOYEB_APP_DOMAIN") or BIND_ADDRESS
        if not HAS_SSL and FQDN != BIND_ADDRESS:
            HAS_SSL = True  # Koyeb always uses HTTPS
        if not NO_PORT and FQDN != BIND_ADDRESS:
            NO_PORT = True  # Koyeb handles port mapping
    elif ON_HEROKU:
        FQDN = _optional("FQDN") or (f"{APP_NAME}.herokuapp.com" if APP_NAME else BIND_ADDRESS)
    else:
        FQDN = _optional("FQDN", BIND_ADDRESS)
    
    # Build URL based on platform
    if ON_HEROKU or ON_KOYEB:
        URL = f"https://{FQDN}/"
    else:
        URL = "http{}://{}{}/".format(
            "s" if HAS_SSL else "", FQDN, "" if NO_PORT else ":" + str(PORT)
        )
