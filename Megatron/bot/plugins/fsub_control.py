import logging
from pyrogram import filters, enums
from pyrogram.types import Message
from pyrogram.errors import ChannelInvalid, UsernameInvalid, ChatAdminRequired

from Megatron.bot import StreamBot
from Megatron.vars import Var
from Megatron.utils.database import Database
from Megatron.utils import not_edited

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


@StreamBot.on_message(filters.command("fsub") & filters.private & filters.user(Var.OWNER_ID) & not_edited)
async def fsub_control(_, m: Message):
    """
    Dynamic force subscribe control
    Usage:
        /fsub on @channel_username
        /fsub on -1001234567890
        /fsub off
        /fsub status
    """
    try:
        args = m.text.split(maxsplit=2)
        
        if len(args) == 1:
            # Show usage
            await m.reply_text(
                "**Force Subscribe Control**\n\n"
                "**Usage:**\n"
                "`/fsub on @channel_username` - Enable fsub with channel username\n"
                "`/fsub on -1001234567890` - Enable fsub with channel ID\n"
                "`/fsub off` - Disable force subscribe\n"
                "`/fsub status` - Check current status\n\n"
                "**Note:** Bot must be admin in the channel!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        action = args[1].lower()
        
        if action == "status":
            # Show current status
            settings = await db.get_force_subscribe_settings()
            if settings['enabled'] and settings['channel']:
                try:
                    chat = await StreamBot.get_chat(settings['channel'])
                    await m.reply_text(
                        f"**Force Subscribe Status**\n\n"
                        f"**Status:** ✅ Enabled\n"
                        f"**Channel:** {chat.title}\n"
                        f"**Channel ID:** `{settings['channel']}`\n"
                        f"**Channel Username:** @{chat.username if chat.username else 'None'}",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                except Exception as e:
                    await m.reply_text(
                        f"**Force Subscribe Status**\n\n"
                        f"**Status:** ✅ Enabled\n"
                        f"**Channel ID:** `{settings['channel']}`\n"
                        f"**Error:** Can't fetch channel info - {e}",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await m.reply_text(
                    "**Force Subscribe Status**\n\n"
                    "**Status:** ❌ Disabled",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            return
        
        if action == "off":
            # Disable force subscribe
            await db.set_force_subscribe(False, None)
            await m.reply_text(
                "✅ **Force Subscribe Disabled!**\n\n"
                "Users can now use the bot without joining any channel.\n\n"
                "**Note:** Restart not required - changes apply immediately!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            logging.info(f"Force subscribe disabled by {m.from_user.id}")
            return
        
        if action == "on":
            # Enable force subscribe
            if len(args) < 3:
                await m.reply_text(
                    "❌ **Missing channel!**\n\n"
                    "Usage: `/fsub on @channel_username` or `/fsub on -1001234567890`",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return
            
            channel_input = args[2].strip()
            
            try:
                # Try to get the chat
                channel_id = None
                
                # Check if it's a numeric ID
                if channel_input.startswith('-'):
                    try:
                        channel_id = int(channel_input)
                    except ValueError:
                        await m.reply_text(
                            "❌ **Invalid channel ID format!**\n\n"
                            "Channel IDs must be numeric (e.g., -1001234567890)",
                            parse_mode=enums.ParseMode.MARKDOWN
                        )
                        return
                else:
                    # Remove @ if present
                    if channel_input.startswith('@'):
                        channel_input = channel_input[1:]
                
                # Try to get the chat
                try:
                    chat = await StreamBot.get_chat(channel_input if not channel_id else channel_id)
                except (ChannelInvalid, UsernameInvalid) as e:
                    await m.reply_text(
                        f"❌ **Cannot find channel!**\n\n"
                        f"Input: `{channel_input if not channel_id else channel_id}`\n"
                        f"Error: {str(e)}\n\n"
                        f"**Make sure:**\n"
                        f"• Channel exists\n"
                        f"• Bot has access to the channel\n"
                        f"• Username is correct (no spaces)\n"
                        f"• Channel ID starts with -100",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                    logging.error(f"Failed to find channel {channel_input if not channel_id else channel_id}: {e}")
                    return
                except Exception as e:
                    await m.reply_text(
                        f"❌ **Unexpected error!**\n\n"
                        f"Error: {str(e)[:200]}\n\n"
                        f"Please try again or contact support.",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                    logging.error(f"Unexpected error getting chat {channel_input if not channel_id else channel_id}: {e}")
                    return
                
                # Check if it's a channel (handle both string and enum)
                from pyrogram.enums import ChatType
                chat_type_str = str(chat.type).split('.')[-1].lower() if hasattr(chat.type, 'name') else str(chat.type).lower()
                
                if chat_type_str not in ["channel", "supergroup"]:
                    await m.reply_text(
                        f"❌ **Invalid channel!**\n\n"
                        f"The provided ID/username must be a channel or supergroup.\n"
                        f"Current type: {chat.type}",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                    return
                
                # Check if bot is admin
                try:
                    bot_member = await StreamBot.get_chat_member(chat.id, "me")
                    # Handle both string status and enum status
                    status_str = str(bot_member.status).split('.')[-1].lower() if hasattr(bot_member.status, 'name') else str(bot_member.status).lower()
                    
                    if status_str not in ["administrator", "creator"]:
                        await m.reply_text(
                            f"❌ **Bot is not admin!**\n\n"
                            f"Please make the bot an admin in **{chat.title}** with:\n"
                            f"• Ban users permission\n"
                            f"• Invite users permission\n\n"
                            f"**Current status:** {status_str}",
                            parse_mode=enums.ParseMode.MARKDOWN
                        )
                        logging.warning(f"Bot is not admin in channel {chat.id} ({chat.title}). Current status: {status_str}")
                        return
                    
                    # Verify required permissions
                    if status_str == "administrator":
                        if not (bot_member.privileges and 
                                bot_member.privileges.can_restrict_members and 
                                bot_member.privileges.can_invite_users):
                            await m.reply_text(
                                f"❌ **Bot lacks required permissions!**\n\n"
                                f"Please ensure the bot has:\n"
                                f"• Ban users permission (can_restrict_members)\n"
                                f"• Invite users permission (can_invite_users)\n\n"
                                f"**Current permissions:**\n"
                                f"  - Restrict members: {getattr(bot_member.privileges, 'can_restrict_members', False)}\n"
                                f"  - Invite users: {getattr(bot_member.privileges, 'can_invite_users', False)}",
                                parse_mode=enums.ParseMode.MARKDOWN
                            )
                            logging.warning(f"Bot lacks required permissions in channel {chat.id} ({chat.title})")
                            return
                            
                except ChatAdminRequired:
                    await m.reply_text(
                        f"❌ **Bot is not admin!**\n\n"
                        f"Please make the bot an admin in **{chat.title}** with:\n"
                        f"• Ban users permission\n"
                        f"• Invite users permission",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                    logging.error(f"ChatAdminRequired error for channel {chat.id} ({chat.title})")
                    return
                except Exception as e:
                    await m.reply_text(
                        f"❌ **Can't check bot permissions!**\n\n"
                        f"Error: {str(e)[:200]}\n\n"
                        f"Make sure bot is admin in the channel.",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                    logging.error(f"Error checking bot permissions in channel {chat.id}: {e}")
                    return
                
                # Enable force subscribe
                await db.set_force_subscribe(True, chat.id)
                
                await m.reply_text(
                    f"✅ **Force Subscribe Enabled!**\n\n"
                    f"**Channel:** {chat.title}\n"
                    f"**Channel ID:** `{chat.id}`\n"
                    f"**Username:** @{chat.username if chat.username else 'None'}\n\n"
                    f"Users must now join this channel to use the bot.\n\n"
                    f"**Note:** No restart needed - changes apply immediately!",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                logging.info(f"Force subscribe enabled for channel {chat.id} by {m.from_user.id}")
                
            except (ChannelInvalid, UsernameInvalid):
                await m.reply_text(
                    "❌ **Invalid channel!**\n\n"
                    "Make sure:\n"
                    "• Channel ID is correct (starts with -100)\n"
                    "• Bot has access to the channel\n"
                    "• Channel username is correct (without @)",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            except ChatAdminRequired:
                await m.reply_text(
                    "❌ **Bot needs admin rights!**\n\n"
                    "Please make the bot an admin in the channel with:\n"
                    "• Ban users permission\n"
                    "• Invite users permission",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            except Exception as e:
                await m.reply_text(
                    f"❌ **Error enabling force subscribe!**\n\n"
                    f"Error: {e}",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                logging.error(f"Error enabling fsub: {e}")
            return
        
        # Invalid action
        await m.reply_text(
            "❌ **Invalid action!**\n\n"
            "Use: `/fsub on @channel`, `/fsub off`, or `/fsub status`",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await m.reply_text(
            f"❌ **Error processing command!**\n\n"
            f"Error: {e}",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        logging.error(f"Error in fsub_control: {e}")
