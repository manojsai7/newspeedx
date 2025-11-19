import asyncio
import logging

from pyrogram import enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Megatron.utils.database import Database
from Megatron.vars import Var

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


async def force_subscribe(bot, cmd):
    """Ensure user joined configured updates channel before proceeding."""
    # Skip fsub check for owner
    if cmd.from_user.id == Var.OWNER_ID:
        return 200
    
    try:
        await db.ensure_user(cmd.from_user)
    except Exception as e:
        logging.error(f"[FSUB] Failed to ensure user {cmd.from_user.id}: {e}")
        # Continue anyway, don't block user
    
    # Security: Check if user is banned first
    try:
        is_banned = await db.is_user_banned(cmd.from_user.id)
        if is_banned:
            await bot.send_message(
                cmd.from_user.id,
                "🚫 **You are banned from using this bot.**\n\nContact the bot owner if you believe this is a mistake.",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
            return 400
    except Exception as e:
        logging.error(f"[FSUB] Failed to check ban status for {cmd.from_user.id}: {e}")
        # Continue if database check fails
    
    # Get force subscribe channel
    try:
        fsub_channel = await db.get_force_subscribe_channel()
    except Exception as e:
        logging.error(f"[FSUB] Failed to get fsub channel from database: {e}")
        fsub_channel = None
    
    if fsub_channel is None:
        fsub_channel = Var.UPDATES_CHANNEL

    # If no force subscribe channel configured, allow access
    if fsub_channel is None:
        return 200

    try:
        invite_link = await bot.create_chat_invite_link(fsub_channel)
    except FloodWait as exc:
        logging.warning(f"[FSUB] FloodWait {exc.x}s while creating invite link for {fsub_channel}")
        await asyncio.sleep(exc.x)
        return 400
    except Exception as e:
        logging.error(f"[FSUB] Failed to create invite link for {fsub_channel}: {e}")
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
    except Exception as e:
        logging.error(f"[FSUB] Unexpected error checking membership for {cmd.from_user.id} in {fsub_channel}: {e}", exc_info=True)
        await bot.send_message(
            cmd.from_user.id,
            "Something went wrong while verifying your subscription. Please try again in a moment.\n\n"
            "If this persists, contact the bot owner.",
        )
        return 400
