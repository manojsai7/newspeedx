from requests import post

from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Megatron.vars import Var
from Megatron.bot import StreamBot

@StreamBot.on_message(filters.command("nim") & filters.private)
async def nimdownloader(c: Client, m: Message):
    if Var.UPDATES_CHANNEL is not None:
        invite_link = None
        try:
            invite_link = await c.create_chat_invite_link(Var.UPDATES_CHANNEL)
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="Sorry, You are Banned to use me. Contact me [Admin](https://t.me/filmyxbot).",
                    parse_mode=enums.ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            fallback_slug = str(Var.UPDATES_CHANNEL).lstrip("@") if Var.UPDATES_CHANNEL else ""
            join_url = invite_link.invite_link if invite_link else f"https://t.me/{fallback_slug}" if fallback_slug else None
            await c.send_message(
                chat_id=m.chat.id,
                text="**Please join updates channel to use me**\nOnly channel subscribers can use the bot\nAfter joining tap help button\n\n✨.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("✵ Join Updates Channel ✵", url=join_url or "https://t.me")
                        ]
                    ]
                ),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        except Exception:
            await c.send_message(
                chat_id=m.chat.id,
                text="Something went Wrong. Contact my [Support Group](https://t.me/joinchat/riq-psSksFtiMDU8).",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True)
            return
    # Determine URL from command argument or replied message
    txt = None
    if len(m.command) > 1:
        txt = m.text.split(maxsplit=1)[1].strip()
    elif m.reply_to_message:
        if m.reply_to_message.text:
            txt = m.reply_to_message.text.strip()
        elif m.reply_to_message.caption:
            txt = m.reply_to_message.caption.strip()

    if not txt:
        await m.reply_text(
            "برای دریافت لینک نیم‌بها، دستور را به شکل `/nim <url>` ارسال کنید یا روی پیامی که حاوی لینک است ریپلای و سپس دستور `/nim` را بزنید.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        return

    if txt.startswith("/") or "http" not in txt.lower():
        await m.reply_text("لطفا یک لینک معتبر ارسال کنید.")
        return
    try:
        url = "https://www.digitalbam.ir/DirectLinkDownloader/Download"
        data = {"downloadUri":txt}
        request = post(url,data).json()["fileUrl"]
        #url = f"https://rimon.ir/api/?url={txt}"
        #requests = post(url).json()
        #link1 = requests["dl1"] 
        #link2 = requests["dl2"] 
        #link3 = requests["dl3"] 
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        await log_msg.reply_text(text=f"Requested by [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User ID:** `{m.from_user.id}`\n**Requested Link:** {txt}\n**Download Link:**\n✨ {request}", disable_web_page_preview=True, parse_mode=enums.ParseMode.MARKDOWN, quote=True)
        msg = "**لینک نیم بهای شما ایجاد شد 😄**\n\n⚜️ **لینک درخواستی شما** : [لینک]({})\n\n⚜️ **لینک نیم بهای شما :**\n✨ سرور نیم بها : [لینک]({})\n\n✨ @FiletoLinkTelegramBot ✨"
        await m.reply_text(
            text=msg.format(txt, request),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✵ Download Now ✵", url=request)]]),
            quote=True
        )
    except Exception as e:
        await c.send_message(m.chat.id, "**اروری رخ داده است. لطفا بعد 1 دقیقه مجددا امتحان نمایید. در صورت رخداد مجدد مشکل را در چنل پشتیبانی بیان نمایید. با تشکر 🌺**")
        return
