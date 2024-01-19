"""The script that runs the bot."""
import functools
import os
from logging import basicConfig, getLogger, WARNING, INFO

from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, Defaults
from telegram import Update

from bot.setup import setup_application

# Enable logging
basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=INFO,
)
getLogger("apscheduler").setLevel(WARNING)
getLogger("httpx").setLevel(WARNING)

logger = getLogger(__name__)


def main() -> None:
    """Start the bot."""
    defaults = Defaults(parse_mode=ParseMode.HTML)
    application = (
        ApplicationBuilder()
        .token(os.environ.get("TOKEN"))
        .defaults(defaults)
        .post_init(setup_application)
        .concurrent_updates(True)
        .build()
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()            
