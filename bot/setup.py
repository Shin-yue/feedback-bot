"""The module contains functions that register the handlers."""
import os

from telegram import BotCommandScopeAllPrivateChats
from telegram.ext import (
    Application, 
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from bot.errorhandler import error_handler
from bot.admintools import bans, list_ban, stats, unban
from bot.callbacks import back, handle, info, start, reply


async def setup_application(application: Application) -> None:
    """
    Registers the different handlers, and etc.

    Args:
        application: The application.
    """
    admin_id = int(os.environ.get("ADMINS"))
    
    application.add_handler(
        CommandHandler(
            ["start", "info", "help"], info, filters=filters.ChatType.PRIVATE
        )
    )
    # Commands that are only for bot admins.
    application.add_handler(CommandHandler("ban", bans, filters=(filters.ChatType.PRIVATE & filters.User(admin_id))))
    application.add_handler(CommandHandler("unban", unban, filters=(filters.ChatType.PRIVATE & filters.User(admin_id))))
    application.add_handler(CommandHandler("listBanned", list_ban,  filters=(filters.ChatType.PRIVATE & filters.User(admin_id))))
    application.add_handler(CommandHandler("subs", stats, filters.User(admin_id)))
    # telegram.ext.CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(start, pattern="start-message"))
    application.add_handler(CallbackQueryHandler(back, pattern="back-start"))
    # telegram.ext.MessageHandler
    application.add_handler(MessageHandler(filters.ALL & filters.ChatType.PRIVATE & ~filters.User(admin_id), handle))
    application.add_handler(
        MessageHandler(
            filters.ALL
            & filters.ChatType.PRIVATE
            & filters.User(admin_id)
            & ~filters.COMMAND,
            reply,
            block=False,
        ),
        group=1
    )

    base_commands = [("start", "Display general information.")]
    await application.bot.set_my_commands(
        commands=base_commands,
        scope=BotCommandScopeAllPrivateChats()
    )
    # Error handler
    application.add_error_handler(error_handler)
