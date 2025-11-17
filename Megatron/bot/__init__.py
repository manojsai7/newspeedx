from pyrogram import Client

from ..vars import Var

# Monkey-patch Client to ensure listeners dict is always initialized
_original_client_init = Client.__init__

def _patched_client_init(self, *args, **kwargs):
    _original_client_init(self, *args, **kwargs)
    # Ensure listeners attribute exists and is a dict
    if not hasattr(self, 'listeners'):
        self.listeners = {}

Client.__init__ = _patched_client_init

# Now import pyromod to patch the Client class with listener methods
try:
    from pyromod import listen  # type: ignore
    pyromod_available = True
except Exception as e:
    print(f"Warning: Could not import pyromod: {e}")
    pyromod_available = False

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

# Initialize all listener types as empty dicts
if pyromod_available:
    try:
        from pyromod.listen.listen import ListenerTypes
    except ImportError:
        try:
            from pyromod.listen import ListenerTypes
        except ImportError:
            try:
                import pyromod
                ListenerTypes = pyromod.listen.listen.ListenerTypes
            except:
                ListenerTypes = None
    
    if ListenerTypes:
        # Ensure listeners is a dict
        if not hasattr(StreamBot, 'listeners'):
            StreamBot.listeners = {}
        elif not isinstance(StreamBot.listeners, dict):
            StreamBot.listeners = {}
        
        # Initialize each listener type as empty dict
        for listener_type in ListenerTypes:
            if listener_type not in StreamBot.listeners:
                StreamBot.listeners[listener_type] = {}
        print(f"[Pyromod] Initialized {len(StreamBot.listeners)} listener types as dicts")

multi_clients = {}
work_loads = {}
