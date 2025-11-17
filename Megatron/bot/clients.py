import asyncio

from pyrogram import Client
from pyrogram.errors import FloodWait

from Megatron.utils import TokenParser
from . import multi_clients, work_loads, StreamBot
from ..vars import Var

async def initialize_clients():
    multi_clients[0] = StreamBot
    work_loads[0] = 0
    
    # Initialize pyromod listeners for the main client if not already done
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
        elif not isinstance(StreamBot.listeners, dict):
            StreamBot.listeners = {}
            
        for listener_type in ListenerTypes:
            if listener_type not in StreamBot.listeners:
                StreamBot.listeners[listener_type] = {}  # DICT not list!
    
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return
    for client_id, token in all_tokens.items():
        instance = Client(
            name=f"multi_{client_id}",
            api_id=Var.API_ID,
            api_hash=Var.API_HASH,
            bot_token=token,
            workdir="Megatron",
            in_memory=True,
            sleep_threshold=Var.SLEEP_THRESHOLD,
            no_updates=True,
        )
        
        # Initialize pyromod listeners for each client instance
        if ListenerTypes:
            if not hasattr(instance, 'listeners'):
                instance.listeners = {}
            elif not isinstance(instance.listeners, dict):
                instance.listeners = {}
                
            for listener_type in ListenerTypes:
                if listener_type not in instance.listeners:
                    instance.listeners[listener_type] = {}  # DICT not list!
        
        try:
            multi_clients[client_id] = await instance.start()
        except FloodWait as exc:
            wait_time = getattr(exc, "value", None) or getattr(exc, "x", None) or 60
            if wait_time > Var.MAX_LOGIN_FLOODWAIT:
                print(
                    f"Skipping Client - {client_id}; Telegram asked to wait {wait_time}s which exceeds the configured MAX_LOGIN_FLOODWAIT={Var.MAX_LOGIN_FLOODWAIT}."
                )
                continue
            cooldown = wait_time + Var.LOGIN_FLOODWAIT_PADDING
            print(f"Client {client_id} hit FloodWait ({wait_time}s). Sleeping for {cooldown}s and retrying once...")
            await asyncio.sleep(cooldown)
            try:
                multi_clients[client_id] = await instance.start()
            except Exception as retry_err:
                print(f"Failed starting Client - {client_id} after FloodWait retry; Error: {retry_err}")
                continue
        except Exception as e:
            print(f"Failed starting Client - {client_id}; Error: {e}")
            continue
        work_loads[client_id] = 0
        print(f"Started - Client {client_id}")
    if len(multi_clients) != 1:
        Var.MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")
