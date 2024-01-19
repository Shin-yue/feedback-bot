"""This module contains convenience helper functions."""
import re
from typing import List, Optional, Tuple, Union
from telegram import InlineKeyboardButton, Message, Update

from bot.constants import MessageType

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\(buttonurl:(?:/{0,2})(.+?)(:same)?\))")


def button_parser(text_note: str) -> Tuple[str, List[InlineKeyboardButton]]:
    """Parse a string and return the parsed string and buttons.

    Parameters
    ----------
    markdown_note: str
        The string to parse

    Returns
    -------
    Tuple[str, List[InlineKeyboardButton]]
        The parsed string and buttons
    """
    note_data = ""
    buttons = []
    if text_note is None:
        return note_data, buttons
    prev = 0
    for match in BTN_URL_REGEX.finditer(text_note):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            if bool(match.group(4)) and buttons:
                buttons[-1].append(
                    InlineKeyboardButton(text=match.group(2), url=match.group(3))
                )
            else:
                buttons.append(
                    [InlineKeyboardButton(text=match.group(2), url=match.group(3))]
                )
            note_data += text_note[prev : match.start(1)]
            prev = match.end(1)

        else:
            note_data += text_note[prev:to_check]
            prev = match.start(1) - 1

    note_data += text_note[prev:]

    return note_data, buttons


def message_content(union: Union["Message", "Update"]):
    if isinstance(union, Message):
        message = union
    elif isinstance(union, Update):
        message = union.effective_message

    if message.animation:
        """:obj:`str`: Messages with :attr:`telegram.Message.animation`."""
        msg_data = (
            message.caption_html 
            if message.caption is not None
            else None
        )
        types = MessageType.ANIMATION
        file_id = message.animation.file_id
    elif message.audio:
        """:obj:`str`: Messages with :attr:`telegram.Message.audio`."""
        msg_data = (
            message.caption_html 
            if message.caption is not None
            else None
        )
        types = MessageType.AUDIO
        file_id = message.audio.file_id
    elif message.document:
        """:obj:`str`: Messages with :attr:`telegram.Message.document`."""
        msg_data = (
            message.caption_html 
            if message.caption is not None
            else None
        )
        types = MessageType.DOCUMENT
        file_id = message.document.file_id
    elif message.photo:
        """:obj:`str`: Messages with :attr:`telegram.Message.photo`."""
        msg_data = (
            message.caption_html 
            if message.caption is not None
            else None
        )
        types = MessageType.PHOTO
        file_id = message.photo[-1].file_id
    elif message.sticker:
        """:obj:`str`: Messages with :attr:`telegram.Message.sticker`."""
        msg_data = ""
        types = MessageType.STICKER
        file_id = message.sticker.file_id
    elif message.video:
        """:obj:`str`: Messages with :attr:`telegram.Message.video`."""
        msg_data = (
            message.caption_html 
            if message.caption is not None
            else None
        )
        types = MessageType.VIDEO
        file_id = message.video.file_id
    elif message.video_note:
        """:obj:`str`: Messages with :attr:`telegram.Message.video_note`."""
        msg_data = ""
        types = MessageType.VIDEO_NOTE
        file_id = message.video_note.file_id
    elif message.voice:
        """:obj:`str`: Messages with :attr:`telegram.Message.voice`."""
        msg_data = (
            message.caption_html 
            if message.caption is not None
            else None
        )
        types = MessageType.VOICE
        file_id = message.voice.file_id
    elif message.text:
        msg_data = message.text_html if message.text_html else message.text
        types = MessageType.TEXT
        file_id = ""

    return msg_data, types, file_id


async def get_user_id(m: Message, strings):
    if m.reply_to_message and m.reply_to_message.forward_from:
        user_id = m.reply_to_message.forward_from.id
        
    elif m.reply_to_message and m.reply_to_message.text:
        user = re.search(r'\d+', m.reply_to_message.text)
        if user:
            user_id = user.group()
        else:
            await m.reply_text(strings["user-not-found"])
            return
            
    else:
        await m.reply_text(strings["no-message"])
        return
        
    return user_id
