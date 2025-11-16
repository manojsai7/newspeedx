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


def _parse_channel(value: str) -> Union[int, str]:
    cleaned = value.strip()
    if not cleaned:
        raise RuntimeError("BIN_CHANNEL cannot be empty.")
    if cleaned.startswith("@"):
        return cleaned
    if cleaned.startswith("-") and cleaned[1:].isdigit():
        return int(cleaned)
    if cleaned.isdigit():
        return int(cleaned)
    raise RuntimeError(
        "BIN_CHANNEL must be either a numeric Telegram channel ID (starting with -100) "
        "or a public username beginning with @"
    )


class Var(object):
    MULTI_CLIENT = False
    API_ID = _as_int(_require("API_ID"))
    API_HASH = _require("API_HASH")
    SESSION_NAME = _optional('SESSION_NAME', 'MegatronBot')
    BOT_TOKEN = _require("BOT_TOKEN")
    BROADCAST_AS_COPY = _as_bool(_optional("BROADCAST_AS_COPY"))
    SLEEP_THRESHOLD = _as_int(_optional("SLEEP_THRESHOLD", "60"), 60)
    WORKERS = _as_int(_optional("WORKERS", "6"), 6)
    BIN_CHANNEL = _parse_channel(_require("BIN_CHANNEL"))  # mandatory for uploads
    PORT = _as_int(_optional("PORT", "8080"), 8080)
    BIND_ADDRESS = _optional("WEB_SERVER_BIND_ADDRESS", "0.0.0.0")
    PING_INTERVAL = _as_int(_optional("PING_INTERVAL", "1200"), 1200)
    HAS_SSL = _as_bool(_optional("HAS_SSL"))
    OWNER_ID = _as_int(_require('OWNER_ID'))
    NO_PORT = _as_bool(_optional("NO_PORT"))
    if "DYNO" in environ:
        ON_HEROKU = True
        APP_NAME = _optional("APP_NAME", "megatron")
    else:
        ON_HEROKU = False
        APP_NAME = None
    DATABASE_URL = _optional('DATABASE_URL')
    UPDATES_CHANNEL = _optional("UPDATES_CHANNEL")
    BANNED_CHANNELS = list(
        set(
            int(x)
            for x in str(_optional("BANNED_CHANNELS", "-100")).split()
            if x
        )
    )
    FQDN = (
        str(_optional("FQDN", BIND_ADDRESS))
        if not ON_HEROKU or _optional("FQDN")
        else f"{APP_NAME}.herokuapp.com"
    )
    if ON_HEROKU:
        URL = f"https://{FQDN}/"
    else:
        URL = "http{}://{}{}/".format(
            "s" if HAS_SSL else "", FQDN, "" if NO_PORT else ":" + str(PORT)
        )
