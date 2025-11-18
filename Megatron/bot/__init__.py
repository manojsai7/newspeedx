from pyrogram import Client

from ..vars import Var

# Import pyromod before creating client
try:
    import pyromod
    print("✓ Pyromod imported successfully")
except ImportError:
    print("⚠ Pyromod not available")

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

# Initialize pyromod listeners dict
try:
    from pyromod.listen import ListenerTypes
    # Initialize listeners as empty dict with all listener types
    if not hasattr(StreamBot, 'listeners'):
        StreamBot.listeners = {}
    for listener_type in ListenerTypes:
        if listener_type not in StreamBot.listeners:
            StreamBot.listeners[listener_type] = []
except (ImportError, AttributeError):
    # Fallback initialization
    if not hasattr(StreamBot, 'listeners'):
        StreamBot.listeners = {}
    for key in ['message', 'callback_query', 'inline_query', 'edited_message', 'chosen_inline_result', 'shipping_query']:
        if key not in StreamBot.listeners:
            StreamBot.listeners[key] = []

multi_clients = {}
work_loads = {}
