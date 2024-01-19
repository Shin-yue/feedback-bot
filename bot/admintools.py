"""This module contains bot admin commands."""
from typing import cast

from telegram import Chat, Bot, Message, Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from bot.const import strings
from bot.helpers import get_user_id
from bot.models.database import Database


async def bans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Ban a users in private chat, this command is only for the bot admins.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    message = cast(Message, update.effective_message)
    chat = cast(Chat, update.effective_chat)
    bot = cast(Bot, context.bot)

    user_id = await get_user_id(message, strings)
    user = (await bot.get_chat(user_id)).to_dict()

    if await Database().user_is_banned(user["id"]):
        await message.reply_text(
            strings["user-is-banned"].format(user["first_name"])
        )
    else:
        await Database().ban_user(user["id"])
        await message.reply_text(
            strings["ban-user"]
        )
        await bot.send_message(user["id"], strings["got-banned"])


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Unban a users if the user has been banned.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    message = cast(Message, update.effective_message)
    chat = cast(Chat, update.effective_chat)
    bot = cast(Bot, context.bot)

    user_id = await get_user_id(message, strings)
    user = (await bot.get_chat(user_id)).to_dict()

    if not await Database().user_is_banned(user["id"]):
        await message.reply_text(
            strings["user-is-not-banned"].format(user["first_name"])
        )
    else:
        await Database().unban_user(user["id"])
        await message.reply_text(
            strings["unban-user"]
        )
        await bot.send_message(user["id"], strings["has-unbanned"])


async def list_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get the list of banned users.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """ 
    list_banned = []
    message = cast(Message, update.effective_message)
    bot = cast(Bot, context.bot)

    text = "🚷 <b><u>List Banned Users</u></b>"
    
    user_has_banned = await Database().get_banned_users()
    for user_id in user_has_banned:
        try:
            user = await bot.get_chat(user_id)
        except BadRequest as excp:
            text = "\n" + excp.message
            pass

        name = user.first_name
        id = user.id
        mention = f"@{user.username}" if user.username else \
                  f"<a href='tg://user?id={id}'>{name[:25]}</a>"

        list_banned.append(f" <b>├</b> {mention} [<code>{id}</code>]")
        
    if len(list_banned) > 0:
        res_user = list_banned[-1].replace("├", "└")
        list_banned.pop(-1)
        list_banned.append(res_user)
        result = text + "\n" + "\n".join(list_banned)
    elif len(list_banned) == 0:
        result = text
    else:
        res_user = list_banned[-1].replace("├", "└")
        list_banned.pop(-1)
        list_banned.append(res_user)
        result = text + "\n" + "\n".join(list_banned)

    await message.reply_text(text=result)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get the count of users that started the bot.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    await cast(Message, update.effective_message).reply_text(
        strings["count-of-users"].format(
            len(await Database().get_all_users())
        )
    )
