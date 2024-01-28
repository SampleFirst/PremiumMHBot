import os
import logging
import pyrogram
from pyrogram import Client, filters
from info import ADMINS, LOG_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import time  # Added for timestamping

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@Client.on_message(filters.group & (filters.regex("@") | filters.regex("https|http") | filters.regex("t.me")))
async def warning(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Skip actions for admins
    if user_id in ADMINS:
        return

    # Track rule breaks for each user
    user_data = await client.get_chat_member(chat_id, user_id)
    try:
        rule_breaks = int(user_data.until_date)
    except ValueError:
        rule_breaks = 0

    # Determine warning message and ban duration based on rule breaks
    if rule_breaks == 0:
        duration = 600  # 10 minutes
        if "@" in message.text:
            warning_text = "Rule Violation Alert!!\n\nPlease do not mention other users in this group."
        elif "http" in message.text or "https" in message.text:
            warning_text = "Rule Violation Alert!!\n\nThird-party links are not allowed in this group."
        else:
            warning_text = "Rule Violation Alert!!\n\nTelegram links are not allowed in this group."
    elif rule_breaks == 1:
        duration = 3600  # 1 hour
        warning_text = "Second Rule Violation!!\n\nYou are being banned for 1 hour."
    else:
        duration = None  # Permanent ban
        warning_text = "Permanent Ban\n\nYou have been banned from this group due to repeated rule violations."

    # Send warning message and ban user if necessary
    await client.delete_messages(chat_id, message.id)
    await client.reply_message(chat_id, warning_text)

    # Log violation to LOG_CHANNEL
    log_message = f"**Rule Violation**\n\nChat ID: {chat_id}\nUser ID: {user_id}\nUsername: {message.from_user.mention}\nRule Broken: {warning_text[:warning_text.find('\n')]}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
    await client.send_message(LOG_CHANNEL, log_message)

    if duration is not None:
        try:
            await client.restrict_chat_member(chat_id, user_id, can_send_messages=False, until_date=int(time.time()) + duration)
            logger.info(f"Banned user {user_id} in chat {chat_id} for {duration} seconds")
        except Exception as e:
            logger.error(f"Failed to ban user: {e}")

    # Send message to LOG_CHANNEL when ban ends
    if duration is not None:
        await asyncio.sleep(duration)
        unban_message = f"**Ban Ended**\n\nChat ID: {chat_id}\nUser ID: {user_id}\nUsername: {message.from_user.mention}\nRule Breaks: {rule_breaks + 1}"
        await client.send_message(LOG_CHANNEL, unban_message)
