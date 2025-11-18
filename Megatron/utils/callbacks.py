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
        await db.ensure_user(cmd.from_user)

        if action == "open":
            await cmd.message.edit_text(
                "⚙️ **Personal settings**\nMore controls are coming soon – stay tuned!",
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=_settings_keyboard(),
            )
        elif action == "back":
            await cmd.message.edit_text(
                "Use /start to send files or manage your uploads.",
                reply_markup=_home_keyboard(),
            )
        else:
            await cmd.answer("Settings panel is under construction.", show_alert=False)
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
