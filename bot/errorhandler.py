"""The module contains the error handler."""
import html
import io
import json
import uuid
import traceback

from logging import getLogger
from telegram import Update
from telegram.ext import ContextTypes

logger = getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre><code class='language-python'>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</code></pre>\n\n"
        f"<pre><code class='language-python'>{html.escape(tb_string)}</code></pre>"
    )

    if len(message) > 4096:
        with io.BytesIO(str.encode(
            message.replace("&quot;", "").replace("<pre>", "").replace("</pre>", "").replace("<code>", "").replace("</code>", "").replace("<code class='language-python'>", "")
        )) as out_file:
            out_file.name = str(uuid.uuid4()).split("-")[0].upper() + ".txt"
            await context.bot.send_document(
                chat_id=int(-1001929613454),
                document=out_file,
                caption="An exception was raised while handling an update.",
            )
            return

    # Finally, send the message
    await context.bot.send_message(chat_id=int(-1001929613454), text=message)
