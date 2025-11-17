from pyromod import listen  # type: ignore

from pyrogram import Client

from ..vars import Var

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

# Initialize pyromod listeners dictionary to prevent KeyError
# The key must be the ListenerTypes enum, not the string value
try:
    from pyromod.listen.listen import ListenerTypes
    
    if not hasattr(StreamBot, 'listeners'):
        StreamBot.listeners = {}
    
    # Initialize with enum objects as keys
    for listener_type in ListenerTypes:
        if listener_type not in StreamBot.listeners:
            StreamBot.listeners[listener_type] = []
except (ImportError, AttributeError):
    # Fallback if import fails
    if not hasattr(StreamBot, 'listeners'):
        StreamBot.listeners = {}

multi_clients = {}
work_loads = {}
