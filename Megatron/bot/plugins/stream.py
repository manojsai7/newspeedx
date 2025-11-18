import asyncio
import logging
from urllib.parse import quote_plus

from pyrogram import filters, Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Megatron.bot import StreamBot
from Megatron.utils import get_hash, get_name, not_edited
from Megatron.utils.database import Database
from Megatron.handlers.fsub import force_subscribe
from Megatron.vars import Var 
from Megatron.utils.human_readable import humanbytes

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


def detect_type(m: Message):
    if m.document:
        return m.document
    elif m.video:
        return m.video
    elif m.photo:
        return m.photo
    elif m.audio:
        return m.audio
    else:
        return

@StreamBot.on_message(
    filters.private
    & (
        filters.document
        | filters.video
        | filters.audio
        | filters.animation
        | filters.voice
        | filters.video_note
        | filters.photo
        | filters.sticker
    ),
    group=4,
)
async def media_receive_handler(c: Client, m: Message):
    try:
        # Log to verify this handler is triggered
        logging.debug(f"[PRIVATE] Received media from user {m.from_user.id} - {m.from_user.first_name}")
        
        try:
            _, created = await db.ensure_user(m.from_user)
        except Exception as e:
            logging.error(f"[DATABASE] Failed to ensure user: {e}")
            await m.reply_text("⚠️ Database temporarily unavailable. Please try again.")
            return
        if created:
            try:
                await c.send_message(
                    Var.BIN_CHANNEL,
                    f"#NEW_USER: \n\nNew User [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started the bot."
                )
            except Exception as e:
                logging.warning(f"[NOTIFICATION] Failed to send new user notification: {e}")
        else:
            try:
                await db.mark_user_seen(m.from_user.id)
            except Exception as e:
                logging.warning(f"[DATABASE] Failed to mark user seen: {e}")
        
        # Check force subscribe (dynamic or static)
        try:
            fsub_channel = await db.get_force_subscribe_channel()
        except Exception as e:
            logging.warning(f"[DATABASE] Failed to get fsub channel, using static: {e}")
            fsub_channel = Var.UPDATES_CHANNEL
        
        if fsub_channel is None:
            fsub_channel = Var.UPDATES_CHANNEL
        
        if fsub_channel:
            fsub = await force_subscribe(c, m)
            if fsub != 200:
                return
        
        file_size = None
        if m.video:
            file_size = f"{humanbytes(m.video.file_size)}"
        elif m.document:
            file_size = f"{humanbytes(m.document.file_size)}"
        elif m.audio:
            file_size = f"{humanbytes(m.audio.file_size)}"
        elif m.photo:
            file_size = f"{humanbytes(m.photo.file_size)}"
        
        file_name = None
        if m.video:
            file_name = f"{m.video.file_name}"
        elif m.document:
            file_name = f"{m.document.file_name}"
        elif m.audio:
            file_name = f"{m.audio.file_name}"
        elif m.photo:
            file_name = f"{m.photo.file_id}"
        
        file = detect_type(m)
        file_name = ''
        if file:
            file_name = file.file_name
        
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(m))}?hash={get_hash(log_msg)}"
        short_link = f"{Var.URL}{get_hash(log_msg)}{log_msg.id}"
        logging.info(f"Generated link: {stream_link} for {m.from_user.first_name}")
        msg_text = f"Your Link Generated!😄\n\n📂 **File Name:** `{file_name}`\n\n**✨ File Size:** `{file_size}`\n\n📥 **Download/Stream Link:** `{stream_link}`\n\n📥 **Short Link:** `{short_link}`"
        
        # Reply to the forwarded message in BIN_CHANNEL with user info and controls
        await log_msg.reply_text(
            text=f"Requested by [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User ID:** `{m.from_user.id}`\n**Download Link:** {stream_link}\n**Short Link:** {short_link}",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_{m.from_user.id}"),
                InlineKeyboardButton("✅ Unban User", callback_data=f"unban_{m.from_user.id}")
            ]])
        )
        
        await m.reply_text(
            text=msg_text, 
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("࿋ Direct/Stream Link ࿋", url=stream_link)],
                    [InlineKeyboardButton("࿋ Short Link ࿋", url=short_link)],
                ],
            ),
            quote=True, 
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except FloodWait as e:
        logging.warning(f"[FLOODWAIT] Sleeping for {e.x}s")
        await asyncio.sleep(e.x)
        try:
            await c.send_message(
                chat_id=Var.BIN_CHANNEL, 
                text=f"Got FloodWait of {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**User ID:** `{str(m.from_user.id)}`", 
                disable_web_page_preview=True, 
                parse_mode=enums.ParseMode.MARKDOWN
            )
        except Exception as notify_err:
            logging.error(f"[NOTIFICATION] Failed to send FloodWait notification: {notify_err}")
    except Exception as e:
        logging.error(f"[ERROR] Failed to process media from user {m.from_user.id}: {e}", exc_info=True)
        try:
            await m.reply_text(
                "⚠️ An error occurred while processing your file. Please try again or contact support.",
                quote=True
            )
        except Exception:
            pass  # Fail silently if we can't even send error message


@StreamBot.on_message(filters.channel & ~filters.chat(Var.BIN_CHANNEL) & ~filters.bot & (filters.document | filters.video | filters.photo) & not_edited & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    # Log to verify if this handler is triggered incorrectly
    logging.debug(f"[CHANNEL] Received media from channel {broadcast.chat.id} - {broadcast.chat.title}")
    
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        try:
            await bot.leave_chat(broadcast.chat.id)
        except Exception as e:
            logging.warning(f"[CHANNEL] Failed to leave banned channel {broadcast.chat.id}: {e}")
        return
    
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}{log_msg.message_id}/{quote_plus(get_name(broadcast))}?hash={get_hash(log_msg)}"
        
        await log_msg.reply_text(
            text=f"**Channel Name:** `{broadcast.chat.title}`\n**Channel ID:** `{broadcast.chat.id}`\n**Link:** {stream_link}",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.message_id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📥 Direct Download Link ࿋", url=f"{stream_link}")]
                ]
            )
        )
    except FloodWait as w:
        logging.warning(f"[FLOODWAIT] Sleeping for {w.x}s from channel {broadcast.chat.title}")
        await asyncio.sleep(w.x)
        try:
            await bot.send_message(
                chat_id=Var.BIN_CHANNEL,
                text=f"Got FloodWait of {str(w.x)}s from {broadcast.chat.title}\n\n**Channel ID:** `{str(broadcast.chat.id)}`",
                disable_web_page_preview=True, 
                parse_mode=enums.ParseMode.MARKDOWN
            )
        except Exception as notify_err:
            logging.error(f"[NOTIFICATION] Failed to send FloodWait notification: {notify_err}")
    except Exception as e:
        logging.error(f"[ERROR] Channel handler error for {broadcast.chat.id}: {e}", exc_info=True)
        try:
            await bot.send_message(
                chat_id=Var.BIN_CHANNEL, 
                text=f"#ERROR_TRACEBACK: `{e}`", 
                disable_web_page_preview=True, 
                parse_mode=enums.ParseMode.MARKDOWN
            )
        except Exception:
            pass  # Fail silently
