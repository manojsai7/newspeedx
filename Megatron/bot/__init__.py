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

# Initialize pyromod listeners BEFORE importing pyromod to prevent KeyError
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
    if not hasattr(StreamBot, 'listeners'):
        StreamBot.listeners = {}
    for listener_type in ListenerTypes:
        if listener_type not in StreamBot.listeners:
            StreamBot.listeners[listener_type] = {}  # Initialize as dict, not list

# Now import pyromod listen to attach handlers
try:
    from pyromod import listen  # type: ignore
except Exception as e:
    print(f"Warning: Could not initialize pyromod: {e}")

multi_clients = {}
work_loads = {}
