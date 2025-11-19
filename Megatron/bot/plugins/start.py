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

    stats = user_doc.get('stats', {})
    uploads = stats.get('uploads', 0)
    downloads = stats.get('downloads', 0)

    text = (
        f"👋 **Welcome, [{message.from_user.first_name}](tg://user?id={message.from_user.id})!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **What I Can Do:**\n\n"
        "📤 **File Sharing** - Send any file, get instant streaming links\n"
        "🔗 **Smart Links** - Secure, time-limited download URLs\n"
        "⚡ **Direct Streaming** - No downloads needed, stream directly\n"
        "🔐 **Password Protection** - Optional password-secured links\n"
        "📊 **Analytics** - Track your uploads and downloads\n"
        "🚀 **High Speed** - Lightning-fast file processing\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 **Your Commands:**\n\n"
        "• /myfiles - View your recent uploads\n"
        "• /help - Detailed usage guide\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📈 **Your Stats:** {uploads} files shared • {downloads} downloads generated\n\n"
        "💡 Just send me any file to get started!"
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


@StreamBot.on_message(filters.command("myfiles") & filters.private)
async def myfiles_handler(bot, message: Message) -> None:
    """Show user's recent uploaded files"""
    try:
        await db.ensure_user(message.from_user)
    except Exception as e:
        logging.error(f"[DATABASE] Failed to ensure user in myfiles handler: {e}")
        await message.reply_text(
            "⚠️ Database error. Please try again.",
            disable_web_page_preview=True,
        )
        return
    
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
        logging.error(f"[SECURITY] Failed to check ban status in myfiles handler: {e}")
    
    # Check force subscribe
    fsub_result = await force_subscribe(bot, message)
    if fsub_result == 400:
        return
    
    try:
        # Get recent files
        recent_files = await db.get_recent_files(message.from_user.id, limit=10)
        
        if not recent_files:
            await message.reply_text(
                "📂 **Your Files**\n\n"
                "You haven't uploaded any files yet.\n\n"
                "Send me a file to get started!",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
            return
        
        # Format file list
        files_text = "📂 **Your Recent Files**\n\n"
        
        from datetime import datetime
        from Megatron.utils.human_readable import humanbytes
        
        for idx, file_doc in enumerate(recent_files, 1):
            file_name = file_doc.get('file_name', 'Unknown')
            file_size = humanbytes(file_doc.get('file_size', 0))
            created_at = file_doc.get('created_at')
            access_count = file_doc.get('access_count', 0)
            message_id = file_doc.get('message_id')
            token = file_doc.get('token')
            
            if isinstance(created_at, datetime):
                created_str = created_at.strftime('%Y-%m-%d %H:%M')
            else:
                created_str = 'Unknown'
            
            files_text += (
                f"**{idx}. {file_name[:30]}**\n"
                f"   Size: `{file_size}` | Views: {access_count}\n"
                f"   Uploaded: {created_str}\n"
            )
            
            # Add link if available
            if message_id and token:
                from urllib.parse import quote_plus
                link = f"{Var.URL}{message_id}/{quote_plus(file_name)}?hash={token[:6]}"
                files_text += f"   [📥 Download]({link})\n"
            
            files_text += "\n"
        
        files_text += "\n💡 Showing your 10 most recent files."
        
        await message.reply_text(
            files_text,
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        
    except Exception as e:
        logging.error(f"[ERROR] Failed to get user files: {e}", exc_info=True)
        await message.reply_text(
            "❌ **Error retrieving your files.**\n\n"
            "Please try again later.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )


@StreamBot.on_message(filters.command("settings") & filters.private)
async def settings_handler(bot, message: Message) -> None:
    """Show bot settings and statistics (Owner Only)"""
    # Owner-only check
    if message.from_user.id != Var.OWNER_ID:
        await message.reply_text(
            "🔒 **Access Denied**\n\n"
            "This command is restricted to the bot owner only.\n\n"
            "Use /help to see available commands.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return
    
    try:
        # Get system statistics
        import psutil
        import time
        from datetime import datetime, timedelta
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used / (1024 ** 3)  # GB
        memory_total = memory.total / (1024 ** 3)  # GB
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = disk.used / (1024 ** 3)  # GB
        disk_total = disk.total / (1024 ** 3)  # GB
        
        # Bot uptime
        import Megatron.bot as bot_module
        if hasattr(bot_module, 'start_time'):
            uptime_seconds = time.time() - bot_module.start_time
        else:
            # Store start time if not exists
            bot_module.start_time = time.time()
            uptime_seconds = 0
        
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))
        
        # Database stats
        try:
            total_users = await db.get_total_users()
            total_files = await db.get_total_files()
            banned_users = await db.get_banned_count()
        except:
            total_users = "N/A"
            total_files = "N/A"
            banned_users = "N/A"
        
        settings_text = (
            "⚙️ **Bot Control Panel**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📊 **System Statistics**\n\n"
            f"🖥 **CPU Usage:** {cpu_percent}%\n"
            f"🧠 **RAM Usage:** {memory_percent}% ({memory_used:.2f}/{memory_total:.2f} GB)\n"
            f"💾 **Disk Usage:** {disk_percent}% ({disk_used:.2f}/{disk_total:.2f} GB)\n"
            f"⏱ **Uptime:** {uptime_str}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👥 **Database Statistics**\n\n"
            f"👤 **Total Users:** {total_users}\n"
            f"📁 **Total Files:** {total_files}\n"
            f"🚫 **Banned Users:** {banned_users}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔧 **Quick Actions:**\n"
            "• /admin - Admin commands\n"
            "• /broadcast - Send message to all users\n"
            "• /fsub - Manage force subscribe\n\n"
            "💡 Use the buttons below for more options."
        )
        
        # Settings keyboard with statistics button
        settings_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📊 Refresh Stats", callback_data="settings:refresh_stats"),
                ],
                [
                    InlineKeyboardButton("👥 User Management", callback_data="settings:users"),
                    InlineKeyboardButton("📁 File Management", callback_data="settings:files"),
                ],
                [
                    InlineKeyboardButton("⬅️ Close", callback_data="settings:close"),
                ],
            ]
        )
        
        await message.reply_text(
            settings_text,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=settings_keyboard,
            disable_web_page_preview=True,
        )
        
    except ImportError:
        # If psutil not installed, show basic settings
        await message.reply_text(
            "⚙️ **Bot Control Panel**\n\n"
            "⚠️ System monitoring unavailable (psutil not installed)\n\n"
            "To enable full statistics, add to requirements.txt:\n"
            "`psutil>=5.9.0`\n\n"
            "🔧 **Available Commands:**\n"
            "• /admin - Admin commands\n"
            "• /broadcast - Send message to all users\n"
            "• /fsub - Manage force subscribe",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logging.error(f"[ERROR] Failed to get settings: {e}", exc_info=True)
        await message.reply_text(
            "❌ **Error retrieving settings.**\n\n"
            "Please try again later.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
