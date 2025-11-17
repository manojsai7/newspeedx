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


# Patch pyromod's own helper to avoid KeyError guards deep inside the library
try:  # pragma: no cover - only runs when pyromod is installed
    from pyromod.listen import client as _pyromod_listen_client  # type: ignore[import]

    _original_get_listener = _pyromod_listen_client.Client.get_listener_matching_with_data

    def _patched_get_listener_matching_with_data(self, data, listener_type):
        store = _ensure_listener_store(self)
        listeners = store[listener_type]  # defaultdict will auto-initialize
        if not listeners:
            # Lazy log to help debugging rare edge-cases
            print(f"[PYROMOD_FIX] Auto-created listener bucket for {listener_type}")
        return _original_get_listener(self, data, listener_type)

    _pyromod_listen_client.Client.get_listener_matching_with_data = _patched_get_listener_matching_with_data
except Exception as patch_err:  # pragma: no cover - best-effort patching
    print(f"[PYROMOD_FIX] Could not patch pyromod listener lookup: {patch_err}")

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
