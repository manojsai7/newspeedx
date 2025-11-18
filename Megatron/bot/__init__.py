from pyrogram import Client

from ..vars import Var

StreamBot = Client(
    name=Var.SESSION_NAME,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    workdir="Megatron",
    plugins={"root": "bot/plugins"},
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS,
)

multi_clients = {}
work_loads = {}

# Explicit imports ensure handlers register even if Pyrogram skips plugin autoloading in certain environments.
from .plugins import start, stream, admin, nim, fsub_control  # noqa: F401,E402
