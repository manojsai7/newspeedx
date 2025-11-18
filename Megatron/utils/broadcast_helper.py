import asyncio
import traceback

from pyrogram.errors import FloodWait, InputUserDeactivated, PeerIdInvalid, UserIsBlocked

from Megatron.vars import Var


async def send_msg(user_id, message):
    try:
        if Var.BROADCAST_AS_COPY:
            await message.copy(chat_id=user_id)
        else:
            await message.forward(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"
