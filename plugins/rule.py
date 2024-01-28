import os, logging, asyncio
from pyrogram import Client, filters
from info import ADMINS, LOG_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.group & (filters.regex("@") | filters.regex("https|http") | filters.regex("t.me")))
async def warning(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id in ADMINS: return

    user_data = await client.get_chat_member(chat_id, user_id)
    try: rule_breaks = int(user_data.until_date)
    except ValueError: rule_breaks = 0

    if rule_breaks == 0:
        duration = 600
        if "@" in message.text: warning_text = f"Rule Violation Alert!! Please do not mention other users in this group. You are being banned for 10 Minutes."
        elif "http" in message.text or "https" in message.text: warning_text = f"Rule Violation Alert!! Third-party links are not allowed in this group. You are being banned for 10 Minutes."
        else: warning_text = f"Rule Violation Alert!! Telegram links are not allowed in this group. You are being banned for 10 Minutes."
    elif rule_breaks == 1:
        duration = 3600
        if "@" in message.text: warning_text = f"Rule Violation Alert!! Please do not mention other users in this group. You are being banned for 1 Hour."
        elif "http" in message.text or "https" in message.text: warning_text = f"Rule Violation Alert!! Third-party links are not allowed in this group. You are being banned for 1 Hour."
        else: warning_text = f"Rule Violation Alert!! Telegram links are not allowed in this group. You are being banned for 1 Hour."
    else:
        duration = None
        warning_text = f"Permanent Ban You have been banned from this group due to repeated rule violations."

    await client.delete_messages(chat_id, message.id)
    await client.reply_message(chat_id, warning_text)

    log_message = (
        f"**Rule Violation** Chat ID: {chat_id} User ID: {user_id} Username: {message.from_user.mention} Rule Broken: {warning_text[:warning_text.find('\\n')]} Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
    )
    await client.send_message(LOG_CHANNEL, log_message)

    if duration is not None:
        try:
            await client.restrict_chat_member(chat_id, user_id, can_send_messages=False, until_date=int(time.time()) + duration)
            logger.info(f"Banned user {user_id} in chat {chat_id} for {duration} seconds")
        except Exception as e:
            logger.error(f"Failed to ban user: {e}")

    if duration is not None:
        await asyncio.sleep(duration)
        unban_message = (
            f"**Ban Ended** Chat ID: {chat_id} User ID: {user_id} Username: {message.from_user.mention} Rule Breaks: {rule_breaks + 1}"
        )
        await client.send_message(LOG_CHANNEL, unban_message)
