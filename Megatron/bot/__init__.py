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
    if not hasattr(StreamBot, 'listeners'):
        StreamBot.listeners = {}
    elif not isinstance(StreamBot.listeners, dict):
        StreamBot.listeners = {}
    
    # Initialize each listener type as an empty list
    if ListenerTypes:
        for listener_type in ListenerTypes:
            if listener_type not in StreamBot.listeners:
                StreamBot.listeners[listener_type] = []
        print(f"[Pyromod] Initialized {len(StreamBot.listeners)} listener types as empty lists")
    else:
        # If ListenerTypes couldn't be imported, initialize common ones manually
        common_types = ["message", "callback_query", "inline_query", "edited_message"]
        for lt in common_types:
            if lt not in StreamBot.listeners:
                StreamBot.listeners[lt] = []
        print(f"[Pyromod] Initialized {len(StreamBot.listeners)} fallback listener types")

multi_clients = {}
work_loads = {}
