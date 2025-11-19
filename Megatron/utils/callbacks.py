import logging
from pyrogram import enums, filters
from pyrogram.errors import RPCError
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from Megatron.bot import StreamBot
from Megatron.handlers.fsub import force_subscribe
from Megatron.utils.database import Database
from Megatron.vars import Var

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


def _settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔁 Link Lifetime", callback_data="settings:not_implemented"),
                InlineKeyboardButton("🔒 Password", callback_data="settings:not_implemented"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="settings:back")],
        ]
    )


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


async def _require_owner(cmd: CallbackQuery) -> bool:
    if cmd.from_user.id != Var.OWNER_ID:
        await cmd.answer("❌ Only the bot owner can perform this action.", show_alert=True)
        return False
    return True


async def _resolve_fsub_channel() -> int | str | None:
    channel = await db.get_force_subscribe_channel()
    return channel if channel else Var.UPDATES_CHANNEL


@StreamBot.on_callback_query(filters.regex(r"^(refreshmeh|settings:|ban_|unban_|noop)"))
async def button(bot, cmd: CallbackQuery) -> None:
    data = cmd.data or ""

    if data == "refreshmeh":
        check = await force_subscribe(bot, cmd)
        if check == 200:
            await cmd.answer("You're good to go!", show_alert=False)
            await cmd.message.edit_text(
                "Thanks for confirming your subscription. Use /start again to continue.",
                reply_markup=_home_keyboard(),
                disable_web_page_preview=True,
            )
        else:
            await cmd.answer("Join the channel and tap refresh again.", show_alert=True)
        return

    if data.startswith("settings:"):
        action = data.split(":", 1)[1]
        
        # Owner-only check for settings
        if cmd.from_user.id != Var.OWNER_ID:
            await cmd.answer("❌ Only the bot owner can access settings.", show_alert=True)
            return

        if action == "open":
            # Redirect to /settings command
            await cmd.answer("⚙️ Use /settings command to access the control panel.", show_alert=True)
            return
        
        elif action == "refresh_stats":
            try:
                import psutil
                import time
                from datetime import timedelta
                
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used = memory.used / (1024 ** 3)
                memory_total = memory.total / (1024 ** 3)
                
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                disk_used = disk.used / (1024 ** 3)
                disk_total = disk.total / (1024 ** 3)
                
                import Megatron.bot as bot_module
                if hasattr(bot_module, 'start_time'):
                    uptime_seconds = time.time() - bot_module.start_time
                else:
                    bot_module.start_time = time.time()
                    uptime_seconds = 0
                
                uptime_str = str(timedelta(seconds=int(uptime_seconds)))
                
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
                
                from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
                
                await cmd.message.edit_text(
                    settings_text,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=settings_keyboard,
                )
                await cmd.answer("✅ Statistics refreshed!", show_alert=False)
                
            except ImportError:
                await cmd.answer("⚠️ psutil not installed. Cannot show stats.", show_alert=True)
            except Exception as e:
                logging.error(f"[CALLBACK] Failed to refresh stats: {e}")
                await cmd.answer("❌ Failed to refresh statistics", show_alert=True)
        
        elif action == "users":
            await cmd.answer("👥 User management coming soon!", show_alert=True)
        
        elif action == "files":
            await cmd.answer("📁 File management coming soon!", show_alert=True)
        
        elif action == "close":
            try:
                await cmd.message.delete()
                await cmd.answer("Settings closed", show_alert=False)
            except Exception as e:
                logging.error(f"[CALLBACK] Failed to close settings: {e}")
                await cmd.answer("Failed to close", show_alert=True)
        
        elif action == "back":
            # Legacy support
            await cmd.answer("Use /start to return to home", show_alert=False)
        else:
            await cmd.answer("⚠️ This feature is under development!", show_alert=True)
        return

    if data.startswith("ban_"):
        if not await _require_owner(cmd):
            return

        try:
            target_id = int(data.split("_", 1)[1])
            if target_id == Var.OWNER_ID:
                await cmd.answer("You cannot ban yourself.", show_alert=True)
                return

            await db.set_user_status(target_id, "banned", reason="Manual ban", actor_id=cmd.from_user.id)
            channel = await _resolve_fsub_channel()
            if channel:
                try:
                    await bot.ban_chat_member(channel, target_id)
                except RPCError:
                    pass

            await cmd.message.edit_reply_markup(
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("✅ Unban User", callback_data=f"unban_{target_id}"),
                            InlineKeyboardButton("🚫 Already Banned", callback_data="noop"),
                        ]
                    ]
                )
            )

            await cmd.answer("User banned successfully.", show_alert=True)
        except Exception as exc:  # pragma: no cover - defensive path
            await cmd.answer(f"Failed to ban user: {exc}", show_alert=True)
        return

    if data.startswith("unban_"):
        if not await _require_owner(cmd):
            return

        try:
            target_id = int(data.split("_", 1)[1])
            await db.set_user_status(target_id, "active", reason=None, actor_id=cmd.from_user.id)
            channel = await _resolve_fsub_channel()
            if channel:
                try:
                    await bot.unban_chat_member(channel, target_id)
                except RPCError:
                    pass

            await cmd.message.edit_reply_markup(
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_{target_id}"),
                            InlineKeyboardButton("✅ Already Unbanned", callback_data="noop"),
                        ]
                    ]
                )
            )

            await cmd.answer("User unbanned successfully.", show_alert=True)
        except Exception as exc:  # pragma: no cover - defensive path
            await cmd.answer(f"Failed to unban user: {exc}", show_alert=True)
        return

    if data == "noop":
        await cmd.answer("Nothing to do here.", show_alert=False)
