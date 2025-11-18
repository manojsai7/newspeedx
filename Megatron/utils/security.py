import base64
import hashlib
import hmac
import secrets
import time
from typing import Tuple


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def generate_download_token(
    *,
    message_id: int,
    file_unique_id: str,
    secret: str,
    ttl_seconds: int,
) -> Tuple[str, int]:
    """Create an HMAC-signed token for a specific file reference."""
    expires_at = int(time.time()) + max(ttl_seconds, 60)
    payload = f"{message_id}:{file_unique_id}:{expires_at}".encode()
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    token = _b64(digest)
    return token, expires_at


def verify_download_token(
    *,
    token: str,
    message_id: int,
    file_unique_id: str,
    secret: str,
    expires_at: int,
) -> bool:
    if expires_at <= int(time.time()):
        return False
    payload = f"{message_id}:{file_unique_id}:{expires_at}".encode()
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    expected = _b64(digest)
    return hmac.compare_digest(expected, token)


def generate_short_slug(length: int = 8) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))
