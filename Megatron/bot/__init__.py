from collections import defaultdict

from pyrogram import Client
from pyromod import listen  # type: ignore - this patches Client class

from ..vars import Var

# CRITICAL FIX: Initialize listeners dict for pyromod BEFORE creating Client
# Pyromod's 'listen' import patches the Client class, but we need to ensure
# the listeners dict is properly initialized with all ListenerTypes

print("[PYROMOD_FIX] Hardening Client listener registry...")

def _ensure_listener_store(obj):
    """Ensure a client has a defaultdict(list) listeners store."""
    current = getattr(obj, "listeners", None)
    if isinstance(current, defaultdict):
        return current

    store = defaultdict(list)
    if isinstance(current, dict):
        for key, value in current.items():
            store[key] = list(value) if isinstance(value, (list, tuple)) else []
    obj.listeners = store
    return store


# Store the original __init__
_original_client_init = Client.__init__


def _patched_client_init(self, *args, **kwargs):
    """Patched __init__ that ensures listeners dict is initialized"""
    _original_client_init(self, *args, **kwargs)
    store = _ensure_listener_store(self)
    # Populate known listener types (optional but nice for logging)
    try:
        from pyromod.listen.listen import ListenerTypes as PyromodListenerTypes  # type: ignore[import]
    except Exception:  # pragma: no cover - import varies per environment
        PyromodListenerTypes = ()

    count_before = len(store)
    for listener_type in PyromodListenerTypes:
        _ = store[listener_type]  # defaultdict ensures key creation

    if PyromodListenerTypes:
        print(
            f"[PYROMOD_FIX] ✓ Listener store ready for '{self.name}' with {len(store)} slots (was {count_before})"
        )


# Apply the patch only once
if Client.__init__ is not _patched_client_init:
    Client.__init__ = _patched_client_init
    print("[PYROMOD_FIX] ✓ Client.__init__ patched successfully")

StreamBot = Client(
    name=Var.SESSION_NAME,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    workdir="Megatron",
    plugins={"root": "Megatron/bot/plugins"},
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS,
)
_ensure_listener_store(StreamBot)

multi_clients = {}
work_loads = {}
