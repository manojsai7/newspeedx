from pyrogram import Client
from pyromod import listen  # type: ignore - this patches Client class

from ..vars import Var

# CRITICAL FIX: Initialize listeners dict for pyromod BEFORE creating Client
# Pyromod's 'listen' import patches the Client class, but we need to ensure
# the listeners dict is properly initialized with all ListenerTypes

print("[PYROMOD_FIX] Patching Client to auto-initialize listeners...")

# Store the original __init__
_original_client_init = Client.__init__

def _patched_client_init(self, *args, **kwargs):
    """Patched __init__ that ensures listeners dict is initialized"""
    # Call original init
    _original_client_init(self, *args, **kwargs)
    
    # Force initialize listeners dict
    if not hasattr(self, 'listeners'):
        self.listeners = {}
    
    # Import and initialize all ListenerTypes
    try:
        # Try the most common import path first
        try:
            from pyromod.listen.listen import ListenerTypes
        except (ImportError, AttributeError, ModuleNotFoundError):
            # Fallback: try getting from pyromod.helpers
            try:
                from pyromod.helpers import ListenerTypes
            except:
                # Last resort: manually define the enum
                from enum import Enum
                class ListenerTypes(str, Enum):
                    MESSAGE = "message"
                    CALLBACK_QUERY = "callback_query"
                    INLINE_QUERY = "inline_query"
                    CHOSEN_INLINE_RESULT = "chosen_inline_result"
                    SHIPPING_QUERY = "shipping_query"
                    PRE_CHECKOUT_QUERY = "pre_checkout_query"
                    POLL = "poll"
                    POLL_ANSWER = "poll_answer"
                    MY_CHAT_MEMBER = "my_chat_member"
                    CHAT_MEMBER = "chat_member"
                    CHAT_JOIN_REQUEST = "chat_join_request"
        
        # Initialize all listener types
        for listener_type in ListenerTypes:
            if listener_type not in self.listeners:
                self.listeners[listener_type] = []
        
        print(f"[PYROMOD_FIX] ✓ Initialized {len(self.listeners)} listener types for client '{self.name}'")
    except Exception as e:
        print(f"[PYROMOD_FIX] ✗ Error initializing listeners: {e}")
        # Even if we fail, create an empty dict to prevent KeyError
        self.listeners = {}

# Apply the patch
Client.__init__ = _patched_client_init

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

multi_clients = {}
work_loads = {}
