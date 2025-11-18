from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant

from Megatron.bot import StreamBot
from Megatron.vars import Var

@StreamBot.on_callback_query(filters.regex(r"^(refreshmeh|ban_|unban_|noop)"))
async def button(bot, cmd: CallbackQuery):
    cb_data = cmd.data or ""
    if "refreshmeh" in cb_data:
        invite_link = None
        if Var.UPDATES_CHANNEL:
            try:
                invite_link = await bot.create_chat_invite_link(Var.UPDATES_CHANNEL)
                user = await bot.get_chat_member(Var.UPDATES_CHANNEL, cmd.message.chat.id)
                if user.status == "kicked":
                    await cmd.message.edit(
                        text="**✨ You are Banned due not to pay attention to the rules. Contact [Support Group](https://t.me/joinchat/riq-psSksFtiMDU8) for further information if interested.\n\n✨ شما به علت عدم رعایت قوانین بن شده اید. جهت اطلاع بیشتر در صورت تمایل می توانید با [گروه پشتیبانی](https://t.me/joinchat/riq-psSksFtiMDU8) در ارتباط باشید.",
                        parse_mode=enums.ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                    )
                    return
            except UserNotParticipant:
                fallback_slug = str(Var.UPDATES_CHANNEL).lstrip("@") if Var.UPDATES_CHANNEL else ""
                join_url = invite_link.invite_link if invite_link else f"https://t.me/{fallback_slug}"
                await cmd.message.edit(
                    text="**✨ You still haven't joined the updates channel. Only channel subscribers can use the bot.**\n\nAfter joining tap refresh button❗️**\n",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("✵ Join Updates Channel ✵", url=join_url)],
                            [InlineKeyboardButton("🔄 Refresh 🔄", callback_data="refreshmeh")],
                        ]
                    ),
                    parse_mode=enums.ParseMode.MARKDOWN,
                )
                return
            except Exception:
                await cmd.message.edit(
                    text="Something went Wrong. Contact [Support Group](https://t.me/joinchat/riq-psSksFtiMDU8).",
                    parse_mode=enums.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
                return
        await cmd.message.edit(
            text=f"""Hey Dear {cmd.from_user.mention(style="md")} 🙋🏻‍♂️\nI'm Telegram File to Link Generator Bot.\n\nSend me any file & get the fast direct download link!\n\n""",
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('✵ Updates Channel ✵', url='https://t.me/+FcsqT7u8gt1mMTdh'), InlineKeyboardButton('✵ Rules✵', url='https://t.me/highspeed_movies/7')],
                    [InlineKeyboardButton('✵ Donate! ✵', url='https://t.me/putsextrovert/7')],
                ]
            ),
            disable_web_page_preview=True,
        )
    elif cb_data.startswith("ban_"):
        if cmd.from_user.id != Var.OWNER_ID:
            await cmd.answer("❌ Only bot owner can ban users!", show_alert=True)
            return
        if Var.UPDATES_CHANNEL is None:
            await cmd.answer("❌ No Updates Channel configured!\nSet UPDATES_CHANNEL or use /fsub command.", show_alert=True)
            return
        try:
            user_id = int(cb_data.split("_", 1)[1])
            
            # Prevent owner from banning themselves
            if user_id == Var.OWNER_ID:
                await cmd.answer("❌ Cannot ban the bot owner!", show_alert=True)
                return
            
            # Get user info
            try:
                user = await bot.get_users(user_id)
                user_name = user.first_name
                username = f"@{user.username}" if user.username else "No username"
            except:
                user_name = "Unknown User"
                username = "N/A"
            
            # Ban the user
            await bot.ban_chat_member(chat_id=Var.UPDATES_CHANNEL, user_id=user_id)
            
            # Update message with ban info
            await cmd.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Unban User", callback_data=f"unban_{user_id}"),
                        InlineKeyboardButton("🚫 Already Banned", callback_data="noop")
                    ]
                ])
            )
            
            await cmd.answer(
                f"✅ User Banned Successfully!\n\n"
                f"👤 Name: {user_name}\n"
                f"🆔 ID: {user_id}\n"
                f"📝 Username: {username}",
                show_alert=True
            )
        except Exception as e:
            await cmd.answer(f"❌ Failed to ban user!\n\nError: {str(e)[:100]}", show_alert=True)
    elif cb_data.startswith("unban_"):
        if cmd.from_user.id != Var.OWNER_ID:
            await cmd.answer("❌ Only bot owner can unban users!", show_alert=True)
            return
        if Var.UPDATES_CHANNEL is None:
            await cmd.answer("❌ No Updates Channel configured!\nSet UPDATES_CHANNEL or use /fsub command.", show_alert=True)
            return
        try:
            user_id = int(cb_data.split("_", 1)[1])
            
            # Get user info
            try:
                user = await bot.get_users(user_id)
                user_name = user.first_name
                username = f"@{user.username}" if user.username else "No username"
            except:
                user_name = "Unknown User"
                username = "N/A"
            
            # Unban the user
            await bot.unban_chat_member(chat_id=Var.UPDATES_CHANNEL, user_id=user_id)
            
            # Update message with unban confirmation
            await cmd.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_{user_id}"),
                        InlineKeyboardButton("✅ Already Unbanned", callback_data="noop")
                    ]
                ])
            )
            
            await cmd.answer(
                f"✅ User Unbanned Successfully!\n\n"
                f"👤 Name: {user_name}\n"
                f"🆔 ID: {user_id}\n"
                f"📝 Username: {username}",
                show_alert=True
            )
        except Exception as e:
            await cmd.answer(f"❌ Failed to unban user!\n\nError: {str(e)[:100]}", show_alert=True)
    elif cb_data == "noop":
        await cmd.answer("✨ This action has already been performed.", show_alert=False)
