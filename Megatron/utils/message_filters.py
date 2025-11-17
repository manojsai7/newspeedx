from pyrogram import filters
from pyrogram.types import Message


def _not_edited(_: object, __: object, message: Message) -> bool:
    """Return True when the incoming message was not edited."""
    return getattr(message, "edit_date", None) is None


not_edited = filters.create(_not_edited)
"""Reusable filter that only matches messages that have never been edited."""
