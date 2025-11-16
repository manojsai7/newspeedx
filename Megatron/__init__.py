import time
from pyrogram.errors import BadMsgNotification

from .vars import Var
from Megatron.bot.clients import StreamBot
from Megatron.utils import reset_stale_session

print("\n")
print("------------------- Initializing Telegram Bot -------------------")


def _start_stream_bot_with_guard(max_retries: int = 3) -> None:
	session_name = Var.SESSION_NAME
	workdir = getattr(StreamBot, "workdir", "Megatron")
	delay = 2

	for attempt in range(1, max_retries + 1):
		try:
			StreamBot.start()
			return
		except BadMsgNotification as exc:
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


_start_stream_bot_with_guard()

bot_info = StreamBot.get_me()
__version__ = 2.2
StartTime = time.time()
