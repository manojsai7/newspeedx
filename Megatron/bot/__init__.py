from pyrogram import Client
from pyromod import listen  # type: ignore
from pyromod.listen.listen import ListenerTypes

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

# Initialize listeners properly for pyromod
if not hasattr(StreamBot, 'listeners'):
    StreamBot.listeners = {listener_type: {} for listener_type in ListenerTypes}

multi_clients = {}
work_loads = {}
