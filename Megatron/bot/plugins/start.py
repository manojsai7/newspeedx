import logging
from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Megatron.bot import StreamBot
from Megatron.handlers.fsub import force_subscribe
from Megatron.vars import Var
from Megatron.utils.database import Database

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


def _home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✵ Updates Channel ✵", url="https://t.me/+uW4Saio7cmYwNjk1"),
                InlineKeyboardButton("😊 Donate 😊", url="https://t.me/TG_FatherBoT?start=donate"),
            ],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings:open")],
        ]
    )


@StreamBot.on_message(filters.command("start") & filters.private)
async def start_handler(bot, message: Message) -> None:
    try:
        user_doc, created = await db.ensure_user(message.from_user)
    except Exception as e:
        logging.error(f"[DATABASE] Failed to ensure user {message.from_user.id}: {e}")
        await message.reply_text(
            "⚠️ Service temporarily unavailable. Please try again in a moment.",
            disable_web_page_preview=True,
        )
        return

    try:
        is_banned = await db.is_user_banned(message.from_user.id)
    except Exception as e:
        logging.error(f"[DATABASE] Failed to check ban status for {message.from_user.id}: {e}")
        is_banned = False  # Fail open on database errors
    
    if is_banned:
        await message.reply_text(
            "🚫 **You are banned from using this bot.**\n\n"
            "You cannot use any bot features or generate links.\n\n"
            "Contact the bot owner if you believe this is a mistake.",
            disable_web_page_preview=True,
        )
        return

    if created:
        try:
            await bot.send_message(
                Var.BIN_CHANNEL,
                f"#NEW_USER\n\n[{message.from_user.first_name}](tg://user?id={message.from_user.id}) started the bot.",
            )
        except Exception as e:
            logging.warning(f"[NOTIFICATION] Failed to send new user notification: {e}")

    # Ensure force-subscribe requirement is satisfied
    fsub_result = await force_subscribe(bot, message)
    if fsub_result != 200:
        return

    stats = user_doc.get("stats", {})
    uploads = stats.get("uploads", 0)
    downloads = stats.get("downloads", 0)

    text = (
        f"Hey {message.from_user.mention(style='md')} 🙋‍♂️\n\n"
        "• Send me a file to receive a secure streaming/download link.\n"
        "• Use /settings to tweak link lifetime, passwords, and privacy.\n"
        "• Use /myfiles to revisit your recent uploads.\n\n"
        f"📊 You have shared **{uploads}** files and generated **{downloads}** downloads so far."
    )

    await message.reply_text(
        text,
        reply_markup=_home_keyboard(),
        disable_web_page_preview=True,
    )


@StreamBot.on_message(filters.command("help") & filters.private)
async def help_handler(bot, message: Message) -> None:
    try:
        await db.ensure_user(message.from_user)
    except Exception as e:
        logging.error(f"[DATABASE] Failed to ensure user in help handler: {e}")
    
    # Security: Check if user is banned
    try:
        is_banned = await db.is_user_banned(message.from_user.id)
        if is_banned:
            await message.reply_text(
                "🚫 **You are banned from using this bot.**\n\n"
                "Contact the bot owner if you believe this is a mistake.",
                disable_web_page_preview=True,
            )
            return
    except Exception as e:
        logging.error(f"[SECURITY] Failed to check ban status in help handler: {e}")

    fsub_result = await force_subscribe(bot, message)
    if fsub_result == 400:
        return

    help_text = (
        "✨ **How to use the bot**\n\n"
        "1. Upload a file or forward from another chat.\n"
        "2. Receive one secure link (full) and one short link.\n"
        "3. Share links safely – they expire automatically.\n\n"
        "Useful commands:\n"
        "• /settings – manage personal preferences\n"
        "• /myfiles – list your recent uploads\n"
        "• /help – display this message again"
    )

    await message.reply_text(
        help_text,
        parse_mode=enums.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=_home_keyboard(),
    )
