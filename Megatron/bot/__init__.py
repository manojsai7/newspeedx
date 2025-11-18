import logging
from pyrogram import Client

from ..vars import Var

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

StreamBot = Client(
    name=Var.SESSION_NAME,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    workdir="Megatron",
    plugins={"root": "bot/plugins"},
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS,
    max_concurrent_transmissions=3,  # Limit concurrent uploads/downloads for stability
)

multi_clients = {}
work_loads = {}

# Explicit imports ensure handlers register even if Pyrogram skips plugin autoloading in certain environments.
from .plugins import start, stream, admin, nim, fsub_control  # noqa: F401,E402

logging.info("[BOT] StreamBot client initialized successfully")
