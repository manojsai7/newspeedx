import asyncio

from pyrogram import enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Megatron.vars import Var
from Megatron.utils.database import Database
from Megatron.utils.callbacks import *

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

async def force_subscribe(bot, cmd):
    """
    Force subscribe handler - supports both static (env var) and dynamic (database) channels
    Priority: Database settings > Environment variable
    """
    # Check database settings first (dynamic fsub)
    fsub_channel = await db.get_fsub_channel()
    
    # Fall back to environment variable if database not configured
    if fsub_channel is None:
        fsub_channel = Var.UPDATES_CHANNEL
    
    # If no channel configured anywhere, skip fsub
    if fsub_channel is None:
        return 200
    
    try:
        invite_link = await bot.create_chat_invite_link(fsub_channel)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return 400
    try:
        user = await bot.get_chat_member(fsub_channel, cmd.from_user.id)
        if user.status == "kicked":
            await bot.send_message(
                chat_id=cmd.from_user.id,
                text="✨ You are Banned due not to pay attention to the rules !. Contact [Support Group](https://t.me/+5vcBlhrleuMwNThh) if you think you've banned wrongly.\n\n✨.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return 400
    except UserNotParticipant:
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="**✨ ⚡️Dᴜᴇ ᴛᴏ Oᴠᴇʀʟᴏᴀᴅ, Oɴʟʏ Cʜᴀɴɴᴇʟ Sᴜʙsᴄʀɪʙᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜᴇ Bᴏᴛ✔️.\n\n⚽️Jᴏɪɴ Our ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ  acess the bot❤️.**\n\nAfter joining tap refresh button.\n\n**✨.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✵ Join Updates Channel ✵", url=invite_link.invite_link)
                    ],
                    [
                        InlineKeyboardButton("🔄 Refresh 🔄", callback_data="refreshmeh")
                    ]
                ]
            ),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return 400
    except Exception:
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="Something went Wrong. Contact [Support](https://t.me/filmyxbot).",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return 400
