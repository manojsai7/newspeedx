import logging
import os
import time
import string
import random
import asyncio
import aiofiles  # type: ignore
import datetime

from pyrogram import filters, Client, enums
from pyrogram.types import Message

from Megatron.bot import StreamBot
from Megatron.vars import Var
from Megatron.utils import not_edited
from Megatron.utils.broadcast_helper import send_msg
from Megatron.utils.database import Database
 

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

broadcast_ids = {}


@StreamBot.on_message(filters.command("ban") & filters.private & filters.user(Var.OWNER_ID) & not_edited)
async def ban_user_command(c: Client, m: Message):
    """
    Ban a user by ID or username
    Usage: /ban <user_id or @username> [reason]
    """
    try:
        args = m.text.split(maxsplit=2)
        
        if len(args) < 2:
            await m.reply_text(
                "**Ban User Command**\n\n"
                "**Usage:**\n"
                "`/ban <user_id>` - Ban user by ID\n"
                "`/ban <user_id> <reason>` - Ban with reason\n"
                "`/ban @username` - Ban by username (if known)\n\n"
                "**Example:**\n"
                "`/ban 123456789 Spam`\n"
                "`/ban 123456789`",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        user_input = args[1].strip()
        reason = args[2] if len(args) > 2 else "Banned by admin"
        
        # Try to parse user ID
        user_id = None
        username = None
        
        if user_input.startswith('@'):
            username = user_input[1:]
            await m.reply_text(
                "❌ **Username lookup not supported!**\n\n"
                "Please use the numeric user ID instead.\n\n"
                "**Tip:** Forward a message from the user to get their ID.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        else:
            try:
                user_id = int(user_input)
            except ValueError:
                await m.reply_text(
                    "❌ **Invalid user ID!**\n\n"
                    "User ID must be a number.\n\n"
                    "**Example:** `/ban 123456789`",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return
        
        # Check if trying to ban owner
        if user_id == Var.OWNER_ID:
            await m.reply_text(
                "❌ **Cannot ban the bot owner!**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        # Check if user exists in database
        try:
            user_doc = await db.users.find_one({"id": user_id})
            if not user_doc:
                await m.reply_text(
                    f"⚠️ **User not found in database!**\n\n"
                    f"**User ID:** `{user_id}`\n\n"
                    f"This user may not have started the bot yet.\n"
                    f"Banning anyway...",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
        except Exception as e:
            logging.warning(f"Failed to check user existence: {e}")
        
        # Ban the user
        try:
            await db.set_user_status(
                user_id=user_id,
                status="banned",
                reason=reason,
                actor_id=m.from_user.id
            )
            
            # Try to ban from channel if force subscribe is enabled
            try:
                fsub_channel = await db.get_force_subscribe_channel()
                if not fsub_channel:
                    fsub_channel = Var.UPDATES_CHANNEL
                
                if fsub_channel:
                    try:
                        await c.ban_chat_member(fsub_channel, user_id)
                        channel_info = " and banned from channel"
                    except Exception as e:
                        logging.warning(f"Failed to ban from channel: {e}")
                        channel_info = " (couldn't ban from channel)"
                else:
                    channel_info = ""
            except Exception as e:
                logging.warning(f"Failed to get fsub channel for ban: {e}")
                channel_info = ""
            
            user_name = user_doc.get('first_name', 'Unknown') if user_doc else 'Unknown'
            
            await m.reply_text(
                f"✅ **User Banned Successfully!**\n\n"
                f"**User ID:** `{user_id}`\n"
                f"**Name:** {user_name}\n"
                f"**Reason:** {reason}\n"
                f"**Banned by:** {m.from_user.mention(style='md')}\n\n"
                f"User has been banned from the bot{channel_info}.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            logging.info(f"User {user_id} banned by {m.from_user.id}. Reason: {reason}")
            
        except Exception as e:
            await m.reply_text(
                f"❌ **Failed to ban user!**\n\n"
                f"Error: {str(e)[:200]}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            logging.error(f"Failed to ban user {user_id}: {e}")
            
    except Exception as e:
        await m.reply_text(
            f"❌ **Error processing ban command!**\n\n"
            f"Error: {str(e)[:200]}",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        logging.error(f"Error in ban command: {e}")


@StreamBot.on_message(filters.command("unban") & filters.private & filters.user(Var.OWNER_ID) & not_edited)
async def unban_user_command(c: Client, m: Message):
    """
    Unban a user by ID
    Usage: /unban <user_id>
    """
    try:
        args = m.text.split(maxsplit=1)
        
        if len(args) < 2:
            await m.reply_text(
                "**Unban User Command**\n\n"
                "**Usage:**\n"
                "`/unban <user_id>` - Unban user by ID\n\n"
                "**Example:**\n"
                "`/unban 123456789`",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        user_input = args[1].strip()
        
        # Parse user ID
        try:
            user_id = int(user_input)
        except ValueError:
            await m.reply_text(
                "❌ **Invalid user ID!**\n\n"
                "User ID must be a number.\n\n"
                "**Example:** `/unban 123456789`",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        # Check if user exists in database
        try:
            user_doc = await db.users.find_one({"id": user_id})
            if not user_doc:
                await m.reply_text(
                    f"⚠️ **User not found in database!**\n\n"
                    f"**User ID:** `{user_id}`\n\n"
                    f"This user may not have started the bot yet.\n"
                    f"Unbanning anyway...",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            elif user_doc.get('status') != 'banned':
                await m.reply_text(
                    f"ℹ️ **User is not banned!**\n\n"
                    f"**User ID:** `{user_id}`\n"
                    f"**Current Status:** {user_doc.get('status', 'active')}\n\n"
                    f"Proceeding with unban anyway...",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
        except Exception as e:
            logging.warning(f"Failed to check user status: {e}")
        
        # Unban the user
        try:
            await db.set_user_status(
                user_id=user_id,
                status="active",
                reason=None,
                actor_id=m.from_user.id
            )
            
            # Try to unban from channel if force subscribe is enabled
            try:
                fsub_channel = await db.get_force_subscribe_channel()
                if not fsub_channel:
                    fsub_channel = Var.UPDATES_CHANNEL
                
                if fsub_channel:
                    try:
                        await c.unban_chat_member(fsub_channel, user_id)
                        channel_info = " and unbanned from channel"
                    except Exception as e:
                        logging.warning(f"Failed to unban from channel: {e}")
                        channel_info = " (couldn't unban from channel)"
                else:
                    channel_info = ""
            except Exception as e:
                logging.warning(f"Failed to get fsub channel for unban: {e}")
                channel_info = ""
            
            user_name = user_doc.get('first_name', 'Unknown') if user_doc else 'Unknown'
            
            await m.reply_text(
                f"✅ **User Unbanned Successfully!**\n\n"
                f"**User ID:** `{user_id}`\n"
                f"**Name:** {user_name}\n"
                f"**Unbanned by:** {m.from_user.mention(style='md')}\n\n"
                f"User can now use the bot{channel_info}.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            logging.info(f"User {user_id} unbanned by {m.from_user.id}")
            
        except Exception as e:
            await m.reply_text(
                f"❌ **Failed to unban user!**\n\n"
                f"Error: {str(e)[:200]}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            logging.error(f"Failed to unban user {user_id}: {e}")
            
    except Exception as e:
        await m.reply_text(
            f"❌ **Error processing unban command!**\n\n"
            f"Error: {str(e)[:200]}",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        logging.error(f"Error in unban command: {e}")


@StreamBot.on_message(filters.command("status") & filters.private & filters.user(Var.OWNER_ID) & not_edited)
async def sts(c: Client, m: Message):
    total_users = await db.total_users_count()
    await m.reply_text(text=f"**Total Users in Database:** `{total_users}`", parse_mode=enums.ParseMode.MARKDOWN, quote=True)


@StreamBot.on_message(filters.command("userinfo") & filters.private & filters.user(Var.OWNER_ID) & not_edited)
async def user_info_command(c: Client, m: Message):
    """
    Get detailed information about a user
    Usage: /userinfo <user_id>
    """
    try:
        args = m.text.split(maxsplit=1)
        
        if len(args) < 2:
            await m.reply_text(
                "**User Info Command**\n\n"
                "**Usage:**\n"
                "`/userinfo <user_id>` - Get user details\n\n"
                "**Example:**\n"
                "`/userinfo 123456789`",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        try:
            user_id = int(args[1].strip())
        except ValueError:
            await m.reply_text(
                "❌ **Invalid user ID!**\n\n"
                "User ID must be a number.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        # Get user from database
        user_doc = await db.users.find_one({"id": user_id})
        
        if not user_doc:
            await m.reply_text(
                f"❌ **User not found!**\n\n"
                f"**User ID:** `{user_id}`\n\n"
                f"This user has not started the bot yet.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        # Format user info
        stats = user_doc.get('stats', {})
        flags = user_doc.get('flags', {})
        settings = user_doc.get('settings', {})
        
        joined_date = user_doc.get('joined_at', 'Unknown')
        if isinstance(joined_date, datetime.datetime):
            joined_date = joined_date.strftime('%Y-%m-%d %H:%M:%S')
        
        last_seen = user_doc.get('last_seen_at', 'Unknown')
        if isinstance(last_seen, datetime.datetime):
            last_seen = last_seen.strftime('%Y-%m-%d %H:%M:%S')
        
        banned_at = flags.get('banned_at', 'N/A')
        if isinstance(banned_at, datetime.datetime):
            banned_at = banned_at.strftime('%Y-%m-%d %H:%M:%S')
        
        info_text = (
            f"**👤 User Information**\n\n"
            f"**ID:** `{user_doc.get('id')}`\n"
            f"**Name:** {user_doc.get('first_name', 'Unknown')} {user_doc.get('last_name', '') or ''}\n"
            f"**Username:** @{user_doc.get('username')} " if user_doc.get('username') else "**Username:** None\n"
        )
        info_text += (
            f"**Status:** {user_doc.get('status', 'active')}\n"
            f"**Joined:** {joined_date}\n"
            f"**Last Seen:** {last_seen}\n\n"
            f"**📊 Statistics:**\n"
            f"• Uploads: {stats.get('uploads', 0)}\n"
            f"• Downloads: {stats.get('downloads', 0)}\n"
            f"• Bytes Uploaded: {stats.get('bytes_uploaded', 0)}\n"
            f"• Bytes Downloaded: {stats.get('bytes_downloaded', 0)}\n\n"
        )
        
        if user_doc.get('status') == 'banned':
            info_text += (
                f"**🚫 Ban Details:**\n"
                f"• Reason: {flags.get('banned_reason', 'No reason')}\n"
                f"• Banned At: {banned_at}\n"
                f"• Banned By: {flags.get('banned_by', 'Unknown')}\n\n"
            )
        
        info_text += (
            f"**⚙️ Settings:**\n"
            f"• Short Links: {settings.get('short_links', True)}\n"
            f"• Password Required: {settings.get('password_required', False)}"
        )
        
        await m.reply_text(
            info_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await m.reply_text(
            f"❌ **Error getting user info!**\n\n"
            f"Error: {str(e)[:200]}",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        logging.error(f"Error in userinfo command: {e}")


@StreamBot.on_message(filters.command("admin") & filters.private & filters.user(Var.OWNER_ID) & not_edited)
async def admin_help(c: Client, m: Message):
    """Show admin commands"""
    help_text = (
        "**🛠️ Admin Commands**\n\n"
        "**User Management:**\n"
        "`/ban <user_id> [reason]` - Ban a user\n"
        "`/unban <user_id>` - Unban a user\n"
        "`/userinfo <user_id>` - Get user details\n\n"
        "**Force Subscribe:**\n"
        "`/fsub on @channel` - Enable force subscribe\n"
        "`/fsub off` - Disable force subscribe\n"
        "`/fsub status` - Check fsub status\n\n"
        "**Broadcasting:**\n"
        "`/broadcast` (reply to message) - Broadcast to all users\n\n"
        "**Statistics:**\n"
        "`/status` - Get total user count\n"
        "`/admin` - Show this help message\n\n"
        "**Tips:**\n"
        "• Use ban/unban buttons in BIN_CHANNEL\n"
        "• Forward messages from users to see their IDs\n"
        "• All commands work in bot DM only"
    )
    
    await m.reply_text(
        help_text,
        parse_mode=enums.ParseMode.MARKDOWN
    )


@StreamBot.on_message(filters.private & filters.command("broadcast") & filters.user(Var.OWNER_ID) & filters.reply)
async def open_broadcast_handler(bot, message):
	await broadcast_handler(c=bot, m=message)


async def broadcast_handler(c, m):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text=f"Broadcast Started! You will be notified with log file when all the users are notified."
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total=total_users,
        current=done,
        failed=failed,
        success=success
    )
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(
                user_id=int(user['id']),
                message=broadcast_msg
            )
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(
                        current=done,
                        failed=failed,
                        success=success
                    )
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    os.remove('broadcast.txt')
