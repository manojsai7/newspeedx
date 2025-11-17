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
    try:
        StreamBot.get_chat(channel)
    except (PeerIdInvalid, ChannelInvalid, ValueError) as exc:
        raise RuntimeError(
            "BIN_CHANNEL is invalid. Double-check the numeric ID (it must start with -100) "
            "or use @userinfobot / @RawDataBot to fetch the correct value."
        ) from exc

    try:
        member = StreamBot.get_chat_member(channel, bot_id)
    except UserNotParticipant as exc:
        raise RuntimeError(
            "The bot isn't a member of BIN_CHANNEL. Add it to the channel and promote it to admin."
        ) from exc
    except ChatAdminRequired as exc:
        raise RuntimeError(
            "Megatron needs admin privileges in BIN_CHANNEL to forward files. Grant Post Messages permission."
        ) from exc

    if member.status not in ("administrator", "creator"):
        raise RuntimeError(
            "Megatron must be an admin in BIN_CHANNEL. Promote it or update BIN_CHANNEL to a channel where it is admin."
        )

    try:
        ping = StreamBot.send_message(
            channel,
            "🛠 Megatron verified BIN_CHANNEL access (message auto-deleted).",
            disable_notification=True,
        )
        try:
            StreamBot.delete_messages(channel, ping.message_id)
        except ChatAdminRequired:
            pass
    except ChatWriteForbidden as exc:
        raise RuntimeError(
            "Megatron cannot post in BIN_CHANNEL. Allow Post Messages permission and retry."
        ) from exc


_start_stream_bot_with_guard()

bot_info = StreamBot.get_me()
_ensure_bin_channel_binding(bot_info.id)
__version__ = 2.2
StartTime = time.time()
