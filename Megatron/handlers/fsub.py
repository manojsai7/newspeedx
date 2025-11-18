import asyncio

from pyrogram import enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Megatron.utils.database import Database
from Megatron.vars import Var

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


async def force_subscribe(bot, cmd):
    """Ensure user joined configured updates channel before proceeding."""
    await db.ensure_user(cmd.from_user)
    
    # Security: Check if user is banned first
    is_banned = await db.is_user_banned(cmd.from_user.id)
    if is_banned:
        await bot.send_message(
            cmd.from_user.id,
            "🚫 **You are banned from using this bot.**\n\nContact the bot owner if you believe this is a mistake.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        return 400
    
    fsub_channel = await db.get_force_subscribe_channel()
    if fsub_channel is None:
        fsub_channel = Var.UPDATES_CHANNEL

    if fsub_channel is None:
        return 200

    try:
        invite_link = await bot.create_chat_invite_link(fsub_channel)
    except FloodWait as exc:
        await asyncio.sleep(exc.x)
        return 400
    except Exception:
        invite_link = None

    try:
        member = await bot.get_chat_member(fsub_channel, cmd.from_user.id)
        status = getattr(member, "status", "")
        if str(status).lower() == "kicked":
            await db.set_user_status(cmd.from_user.id, "banned", reason="Channel ban")
            await bot.send_message(
                cmd.from_user.id,
                "✨ You are banned from the updates channel and cannot use the bot.",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
            return 400
        await db.mark_user_fsub_state(cmd.from_user.id, "clear", channel=fsub_channel)
        return 200
    except UserNotParticipant:
        fallback_slug = str(fsub_channel).lstrip("@") if isinstance(fsub_channel, str) else ""
        join_url = invite_link.invite_link if invite_link else f"https://t.me/{fallback_slug}" if fallback_slug else "https://t.me"
        await db.mark_user_fsub_state(cmd.from_user.id, "pending", channel=fsub_channel)
        await bot.send_message(
            cmd.from_user.id,
            "⚠️ **Join our updates channel to unlock downloads.**\n\nAfter joining, tap refresh!",
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("✵ Join Updates Channel ✵", url=join_url)],
                    [InlineKeyboardButton("🔄 Refresh", callback_data="refreshmeh")],
                ]
            ),
        )
        return 400
    except Exception:
        await bot.send_message(
            cmd.from_user.id,
            "Something went wrong while verifying your subscription. Please try again in a moment.",
        )
        return 400
