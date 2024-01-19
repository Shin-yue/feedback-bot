"""The module contains some bots functionality."""
import os
import re
from typing import cast
from logging import getLogger

from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram import (
    Bot,
    Chat,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
    Update
)

from bot.const import strings
from bot.helpers import button_parser, get_user_id, message_content
from bot.constants import MessageType, UserState
from bot.models import Database

logger = getLogger(__name__)

URL = "https://telegra.ph/file/0be5e826d1bc2f49d919d.jpg"
"""The media url in start messages."""


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Returns some info about the bot.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    message = cast(Message, update.effective_message)
    user = cast(User, update.effective_user)   
    language = "id" if user.language_code == "id" else "en"

    if await Database().user_is_banned(user.id):
        await message.reply_text(strings[language]["not-allowed"])
        return
        
    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                strings[language]["start-button"], callback_data="start-message"
            )
        ]
    )
    await Database().register_user_by_dict(user.to_dict())
    await message.reply_text(
        text=strings[language]["start"].format(URL, user.first_name),
        reply_markup=keyboard
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Returns to start the conversation.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    if context.user_data.get("state", UserState.IDLE) != UserState.IDLE:
        return

    query = cast(CallbackQuery, update.callback_query)
    language = "id" if query.from_user.language_code == "id" else "en"
    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(strings[language]["back-button"], callback_data="back-start")
        ]
    )
    await query.message.edit_text(
        text=strings[language]["start-conversation"].format(URL),
        reply_markup=keyboard
    )
    context.user_data["state"] = UserState.COMMENTING


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Returns to ends the conversation.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    query = cast(CallbackQuery, update.callback_query)
    language = "id" if query.from_user.language_code == "id" else "en"
    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                strings[language]["start-button"], callback_data="start-message"
            )
        ]
    )
    await query.message.edit_text(
        strings[language]["start"].format(URL, query.from_user.first_name),
        reply_markup=keyboard
    )
    context.user_data["state"] = UserState.IDLE


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Returns to handle all messages from user.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    if context.user_data.get("state", None) != UserState.COMMENTING:
        return 
        
    message = cast(Message, update.effective_message)        
    user = cast(User, update.effective_user)
    if await Database().user_is_banned(user.id):
        return 
    
    user = await bot.get_chat(user.id) 
    
    if message:  
        chat = cast(Chat, update.effective_chat)  
        bot = cast(Bot, context.bot)
        fw = await bot.forward_message(
            chat_id=int(os.environ.get("ADMINS")),
            from_chat_id=chat.id,
            message_id=message.message_id
        )      
        if user.has_private_forwards:
            await bot.send_message(
                chat_id=int(os.environ.get("ADMINS")),
                text=strings["has-private-forwards"].format(user.id),
                reply_to_message_id=fw.message_id,
            )
            return


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Returns to reply the user messages.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    message = cast(Message, update.effective_message)    
    bot = cast(Bot, context.bot)
    TYPE = {
        MessageType.ANIMATION: bot.send_animation,
        MessageType.AUDIO: bot.send_audio,
        MessageType.DOCUMENT: bot.send_document,
        MessageType.PHOTO: bot.send_photo,
        MessageType.STICKER: bot.send_sticker,
        MessageType.VIDEO: bot.send_video,
        MessageType.VIDEO_NOTE: bot.send_video_note,
        MessageType.VOICE: bot.send_voice,
        MessageType.TEXT: bot.send_message,
    } 
    
    user_id = await get_user_id(message, strings)      
    content = message_content(message)     
    data = button_parser(content[0])   
    
    try:
        if TYPE[content[1]] in [
            bot.send_audio,
            bot.send_voice,
            bot.send_document,
        ]:
            await TYPE[content[1]](
                user_id,
                content[2],
                caption=data[0],
                reply_markup=InlineKeyboardMarkup(data[1]) if len(data[1]) != 0 else None
            )            
        elif TYPE[content[1]] in [bot.send_sticker, bot.send_video_note]:
            await TYPE[content[1]](
                user_id, 
                content[2]
            )
        elif TYPE[content[1]] == bot.send_message:
            await TYPE[content[1]](
                user_id, 
                data[0],
                reply_markup=InlineKeyboardMarkup(data[1]) if len(data[1]) != 0 else None
            )
        else:
            await TYPE[content[1]](
                user_id,
                content[2],
                caption=data[0],
                has_spoiler=True,
                reply_markup=InlineKeyboardMarkup(data[1]) if len(data[1]) != 0 else None
            )
    except BadRequest as exception:
        logger.info(
            "The message couldn't be sent to user_id %s, due to: %s", 
            user_id, 
            exception.message
        )
