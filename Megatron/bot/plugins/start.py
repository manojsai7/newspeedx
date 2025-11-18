from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from Megatron.bot import StreamBot
from Megatron.vars import Var
from Megatron.utils.database import Database
from Megatron.handlers.fsub import force_subscribe
 
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


@StreamBot.on_message(filters.command('start') & filters.private)
async def start(b, m: Message):
    # Add user to database if new
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await b.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started the bot."
        )
    
    # Check force subscribe
    if Var.UPDATES_CHANNEL:
        fsub = await force_subscribe(b, m)
        if fsub == 400:
            return
    
    # Parse command for file links
    usr_cmd = m.text.split("_")[-1]
    
    if usr_cmd == "/start":
        # Regular start message
        await m.reply(
            text=f"""Hey Dear {m.from_user.mention(style="md")} 🙋🏻‍♂️

I'm Telegram File to Link Generator Bot.

Send me any file & get the fast direct download link!

⚠ **Don't forget to Join Channel first!**""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('✵ Updates Channel ✵', url='https://t.me/+uW4Saio7cmYwNjk1'), 
                 InlineKeyboardButton('😊 Donate 😊', url='https://t.me/TG_FatherBoT?start=donate')],
                [InlineKeyboardButton('🧧 Contact Admin 🧧', url='https://t.me/TG_FatherBoT')]
            ]),
            disable_web_page_preview=True
        )
    else:
        # Handle file link access (usr_cmd contains file ID)
        u = await b.get_chat_member(Var.UPDATES_CHANNEL, m.from_user.id)
        if u.status in {"kicked", "banned"}:
            await b.send_message(
                chat_id=m.from_user.id,
                text="✨ You're Banned due to not following the [rules](https://t.me/+uW4Saio7cmYwNjk1). Contact [Support](https://t.me/TG_FatherBoT) if you think you've been banned wrongly.\n\n✨",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )


@StreamBot.on_message(filters.command('help') & filters.private)
async def help_handler(bot, message):
    # Add user to database if new
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!"
        )
    
    # Check force subscribe
    if Var.UPDATES_CHANNEL:
        fsub = await force_subscribe(bot, message)
        if fsub == 400:
            return
    
    await message.reply_text(
        text="✨ Send me any file, I'll give you its direct download link\n\nAlso I'm supported in channels. Add me to channel as admin to make me workable\n\n✨",
        parse_mode=enums.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✵ Main Channel ✵", url="https://t.me/+uW4Saio7cmYwNjk1"), 
             InlineKeyboardButton("✵ Network ✵", url="https://t.me/highpeed_movies")],
            [InlineKeyboardButton("✵ Developer ✵", url="https://t.me/TG_FatherBoT")]
        ])
    )
