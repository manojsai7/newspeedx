from pyrogram import Client

from ..vars import Var

# Simple pyromod import - let it handle its own initialization
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

multi_clients = {}
work_loads = {}
