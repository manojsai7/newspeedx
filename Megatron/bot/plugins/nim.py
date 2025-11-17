import asyncio
from requests import post

from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Megatron.vars import Var
from Megatron.bot import StreamBot

@StreamBot.on_message(filters.command("nim") & filters.private)
async def nimdownloader(c: Client, m: Message):
    if Var.UPDATES_CHANNEL is not None:
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
            await c.send_message(
                chat_id=m.chat.id,
                text="**Please join updates channel to use me**\nOnly channel subscribers can use the bot\nAfter joining tap help button\n\n✨.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("✵ Join Updates Channel ✵", url=invite_link.invite_link)
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
    chat = m.chat
    while True:
        url = await StreamBot.ask(chat.id, "⚠️This part is only for Iranian users⚠️\n\n**")
        if not url.text:
            continue
        txt = url.text.strip()
        if txt.startswith("/"):
            continue
        if "http" in url.text.lower():
            break
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
        #await StreamBot.send_message(chat.id, f"**ERROR:** `{str(e)}`")
        await StreamBot.send_message(chat.id, "**اروری رخ داده است. لطفا بعد 1 دقیقه مجددا امتحان نمایید. در صورت رخداد مجدد مشکل را در چنل پشتیبانی بیان نمایید. با تشکر 🌺**")
        return
