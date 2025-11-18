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
    from pyromod.listen.listen import ListenerTypes
    pyromod_available = True
except Exception as e:
    print(f"Warning: Could not import pyromod: {e}")
    pyromod_available = False
    ListenerTypes = None

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

# Initialize all listener types as empty lists in the dict
if pyromod_available and ListenerTypes:
    # Ensure listeners is a regular dict
    if not hasattr(StreamBot, 'listeners'):
        StreamBot.listeners = {}
    elif not isinstance(StreamBot.listeners, dict):
        StreamBot.listeners = {}
    
    # Initialize each listener type as an empty list
    for listener_type in ListenerTypes:
        if listener_type not in StreamBot.listeners:
            StreamBot.listeners[listener_type] = []
    print(f"[Pyromod] Initialized {len(StreamBot.listeners)} listener types as empty lists")

multi_clients = {}
work_loads = {}
