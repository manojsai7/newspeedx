from pyrogram import Client

from ..vars import Var

# Monkey-patch Client to ensure listeners dict is always initialized BEFORE pyromod
_original_client_init = Client.__init__

def _patched_client_init(self, *args, **kwargs):
    _original_client_init(self, *args, **kwargs)
    # Ensure listeners is a regular dict (not defaultdict - pyromod doesn't like that)
    if not hasattr(self, 'listeners'):
        self.listeners = {}
    elif not isinstance(self.listeners, dict):
        self.listeners = {}

Client.__init__ = _patched_client_init


def _ensure_listeners_dict(client):
    listeners = getattr(client, "listeners", None)
    if not isinstance(listeners, dict):
        listeners = {}
        client.listeners = listeners
    return listeners


def _ensure_listener_bucket(client, listener_type):
    listeners = _ensure_listeners_dict(client)
    if listener_type not in listeners:
        listeners[listener_type] = []
    return listeners[listener_type]

# Now import pyromod to patch the Client class with listener methods
try:
    from pyromod import listen  # type: ignore
    pyromod_available = True
except Exception as e:
    print(f"Warning: Could not import pyromod: {e}")
    pyromod_available = False

# Import ListenerTypes with multiple fallback attempts
ListenerTypes = None
if pyromod_available:
    try:
        from pyromod.listen import ListenerTypes
    except (ImportError, AttributeError):
        try:
            import pyromod.listen.listen as pyromod_listen
            ListenerTypes = pyromod_listen.ListenerTypes
        except (ImportError, AttributeError):
            try:
                import pyromod
                ListenerTypes = pyromod.ListenerTypes
            except (ImportError, AttributeError):
                print("[Pyromod] Could not import ListenerTypes, using fallback initialization")
                # Create a fallback enum with common listener types
                from enum import Enum
                class ListenerTypes(str, Enum):
                    MESSAGE = "message"
                    CALLBACK_QUERY = "callback_query"
                    INLINE_QUERY = "inline_query"
                    EDITED_MESSAGE = "edited_message"

    # Patch pyromod's helper methods to auto-create missing listener buckets
    original_get_listener = getattr(Client, "get_listener_matching_with_data", None)
    if callable(original_get_listener):
        def _safe_get_listener_matching_with_data(self, data, listener_type, *args, **kwargs):
            _ensure_listener_bucket(self, listener_type)
            return original_get_listener(self, data, listener_type, *args, **kwargs)

        Client._original_get_listener_matching_with_data = original_get_listener  # type: ignore[attr-defined]
        Client.get_listener_matching_with_data = _safe_get_listener_matching_with_data  # type: ignore[assignment]

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

# Initialize all listener types as empty lists in the dict - ALWAYS do this if pyromod loaded
if pyromod_available:
    # Ensure listeners is a regular dict
    _ensure_listeners_dict(StreamBot)
    
    # Initialize each listener type as an empty list
    if ListenerTypes:
        for listener_type in ListenerTypes:
            _ensure_listener_bucket(StreamBot, listener_type)
        print(f"[Pyromod] Initialized {len(StreamBot.listeners)} listener types as empty lists")
    else:
        # If ListenerTypes couldn't be imported, initialize common ones manually
        common_types = ["message", "callback_query", "inline_query", "edited_message"]
        for lt in common_types:
            _ensure_listener_bucket(StreamBot, lt)
        print(f"[Pyromod] Initialized {len(StreamBot.listeners)} fallback listener types")

multi_clients = {}
work_loads = {}
