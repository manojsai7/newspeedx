from collections import defaultdict

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

# Initialize pyromod listeners dict as defaultdict(list) for safe lookups
try:
    from pyromod.listen import ListenerTypes
    initial = getattr(StreamBot, "listeners", {}) or {}
    StreamBot.listeners = defaultdict(list, initial)
    for listener_type in ListenerTypes:
        _ = StreamBot.listeners[listener_type]
except (ImportError, AttributeError):
    initial = getattr(StreamBot, "listeners", {}) or {}
    StreamBot.listeners = defaultdict(list, initial)
    for key in [
        "message",
        "callback_query",
        "inline_query",
        "edited_message",
        "chosen_inline_result",
        "shipping_query",
    ]:
        _ = StreamBot.listeners[key]

multi_clients = {}
work_loads = {}
