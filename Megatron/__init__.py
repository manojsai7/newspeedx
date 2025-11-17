import time
from pyrogram.errors import (
    AccessTokenExpired,
    BadMsgNotification,
    ChannelInvalid,
    ChatAdminRequired,
    ChatWriteForbidden,
    FloodWait,
    PeerIdInvalid,
    UserNotParticipant,
)

from .vars import Var
from Megatron.bot.clients import StreamBot
from Megatron.utils import reset_stale_session

print("\n")
print("------------------- Initializing Telegram Bot -------------------")


def _is_clock_skew_error(error: BadMsgNotification) -> bool:
    description = str(error).lower()
    return "client time" in description or "msg_id is too low" in description


def _start_stream_bot_with_guard(max_retries: int = 3) -> None:
    session_name = Var.SESSION_NAME
    workdir = getattr(StreamBot, "workdir", "Megatron")
    delay = 2

    for attempt in range(1, max_retries + 1):
        try:
            # CRITICAL: Initialize pyromod listeners before starting
            # This is a last-chance safety net before bot.start()
            print("[PYROMOD_INIT] Verifying listeners initialization...")
            
            if not hasattr(StreamBot, 'listeners'):
                print("[PYROMOD_INIT] WARNING: listeners attribute missing! Creating now...")
                StreamBot.listeners = {}
            
            if not StreamBot.listeners or len(StreamBot.listeners) == 0:
                print("[PYROMOD_INIT] WARNING: listeners dict is empty! Initializing now...")
                try:
                    from pyromod.listen.listen import ListenerTypes
                    for listener_type in ListenerTypes:
                        StreamBot.listeners[listener_type] = []
                    print(f"[PYROMOD_INIT] ✓ Initialized {len(StreamBot.listeners)} listener types")
                except ImportError:
                    try:
                        from pyromod.listen import ListenerTypes
                        for listener_type in ListenerTypes:
                            StreamBot.listeners[listener_type] = []
                        print(f"[PYROMOD_INIT] ✓ Initialized {len(StreamBot.listeners)} listener types (alt import)")
                    except Exception as e:
                        print(f"[PYROMOD_INIT] ✗ Failed to import ListenerTypes: {e}")
                        print("[PYROMOD_INIT] ✗ This will likely cause KeyError issues!")
            else:
                print(f"[PYROMOD_INIT] ✓ Listeners already initialized: {list(StreamBot.listeners.keys())}")
            
            StreamBot.start()
            return
        except BadMsgNotification as exc:
            if _is_clock_skew_error(exc):
                print(
                    "[StreamBot] Telegram rejected the login because the host clock is out of sync. "
                    "Checking again after a short delay. Please ensure the server time is accurate (enable NTP)."
                )
                if attempt == max_retries:
                    raise RuntimeError(
                        "Telegram keeps rejecting the connection due to an unsynchronized clock. "
                        "Synchronize the host time (e.g., via chrony/ntp) and try again."
                    ) from exc
                time.sleep(delay)
                delay = min(delay * 2, 10)
                continue

            removed_files = reset_stale_session(session_name=session_name, workdir=workdir)
            print(
                f"[StreamBot] Telegram reported unsynchronized msg_id ({exc}). "
                f"Cleared {len(removed_files)} session artifact(s)."
            )
            if removed_files:
                for file_path in removed_files:
                    print(f"  └─ removed {file_path}")

            if attempt == max_retries:
                raise

            print(f"Retrying StreamBot start in {delay} second(s)...")
            time.sleep(delay)
            delay = min(delay * 2, 10)
        except FloodWait as exc:
            wait_time = getattr(exc, "value", None) or getattr(exc, "x", None) or 60
            if wait_time > Var.MAX_LOGIN_FLOODWAIT:
                raise RuntimeError(
                    "Telegram is throttling bot logins aggressively (FloodWait). "
                    f"Wait {wait_time} seconds before restarting, or increase MAX_LOGIN_FLOODWAIT if you understand the risk."
                ) from exc
            cooldown = wait_time + Var.LOGIN_FLOODWAIT_PADDING
            print(f"[StreamBot] FloodWait: Telegram asked to wait {wait_time}s before logging in. Sleeping for {cooldown}s...")
            time.sleep(cooldown)
        except AccessTokenExpired as exc:
            raise RuntimeError(
                "Telegram rejected the configured BOT_TOKEN (expired/revoked). "
                "Generate a fresh token via @BotFather, update the BOT_TOKEN environment variable, "
                "and redeploy."
            ) from exc


def _ensure_bin_channel_binding(bot_id: int) -> None:
    if getattr(Var, "SKIP_BIN_VALIDATION", False):
        print("[StreamBot] SKIP_BIN_VALIDATION is set; proceeding without verifying BIN_CHANNEL access.")
        return
    channel = Var.BIN_CHANNEL
    print(f"[BIN_CHANNEL] Validating access to channel ID: {channel}")
    
    try:
        chat_info = StreamBot.get_chat(channel)
        print(f"[BIN_CHANNEL] ✓ Chat accessible: {chat_info.title} (type={chat_info.type})")
    except (PeerIdInvalid, ChannelInvalid, ValueError) as exc:
        print(f"[BIN_CHANNEL] ✗ Chat lookup failed: {exc}")
        raise RuntimeError(
            f"BIN_CHANNEL={channel} is invalid or inaccessible. Double-check the numeric ID (must start with -100). "
            "Use @userinfobot or @RawDataBot in the channel to confirm."
        ) from exc

    try:
        member = StreamBot.get_chat_member(channel, bot_id)
        print(f"[BIN_CHANNEL] Bot membership status: {member.status}")
    except UserNotParticipant as exc:
        print(f"[BIN_CHANNEL] ✗ Bot is not a participant: {exc}")
        raise RuntimeError(
            f"The bot (ID={bot_id}) isn't a member of BIN_CHANNEL={channel}. "
            "Add it to the channel and promote it to admin with 'Post Messages' permission."
        ) from exc
    except ChatAdminRequired as exc:
        print(f"[BIN_CHANNEL] ✗ Admin check failed: {exc}")
        raise RuntimeError(
            "Megatron needs admin privileges in BIN_CHANNEL to forward files. Grant Post Messages permission."
        ) from exc

    # PyroBlack 2.x returns ChatMemberStatus enums; convert to string for comparison
    status_str = str(member.status).split(".")[-1].lower() if hasattr(member.status, "name") else str(member.status).lower()
    if status_str not in ("administrator", "creator"):
        print(f"[BIN_CHANNEL] ✗ Insufficient privileges: current status is '{member.status}', need 'administrator' or 'creator'")
        raise RuntimeError(
            f"Megatron must be an admin in BIN_CHANNEL={channel}. Current status: {member.status}. "
            "Promote the bot to administrator with 'Post Messages' enabled."
        )

    print(f"[BIN_CHANNEL] ✓ Bot has {member.status} privileges. Testing post capability...")
    try:
        ping = StreamBot.send_message(
            channel,
            "🛠 Megatron verified BIN_CHANNEL access (message auto-deleted).",
            disable_notification=True,
        )
        msg_id = ping.id  # PyroBlack 2.x uses .id instead of .message_id
        print(f"[BIN_CHANNEL] ✓ Test message posted (msg_id={msg_id})")
        try:
            StreamBot.delete_messages(channel, msg_id)
            print("[BIN_CHANNEL] ✓ Test message deleted. Validation complete.")
        except ChatAdminRequired:
            print("[BIN_CHANNEL] ⚠ Could not delete test message (missing delete permission), but post works.")
    except ChatWriteForbidden as exc:
        print(f"[BIN_CHANNEL] ✗ Cannot post messages: {exc}")
        raise RuntimeError(
            "Megatron cannot post in BIN_CHANNEL. Ensure 'Post Messages' permission is enabled and retry."
        ) from exc


_start_stream_bot_with_guard()

bot_info = StreamBot.get_me()
_ensure_bin_channel_binding(bot_info.id)
__version__ = 2.2
StartTime = time.time()
