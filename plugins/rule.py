import os
import logging
import asyncio
import time
from pyrogram import Client, filters
from info import ADMINS, LOG_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    rule_breaks = user_data.warn_level or 0

    # Determine warning message and ban duration based on rule breaks
    if rule_breaks == 0:
        duration = 600  # 10 minutes
        violation_text = (
            "Please do not mention other users in this group." 
            if "@" in message.text else
            "Third-party links are not allowed in this group." 
            if "http" in message.text or "https" in message.text else
            "Telegram links are not allowed in this group."
        )
        warning_text = (
            f"Rule Violation Alert!!\n\n{violation_text}\n\n"
            f"You are being banned for 10 Minutes."
        )

    elif rule_breaks == 1:
        duration = 3600  # 1 hour
        violation_text = (
            "Please do not mention other users in this group." 
            if "@" in message.text else
            "Third-party links are not allowed in this group." 
            if "http" in message.text or "https" in message.text else
            "Telegram links are not allowed in this group."
        )
        warning_text = (
            f"Rule Violation Alert!!\n\n{violation_text}\n\n"
            f"You are being banned for 1 Hour."
        )

    else:
        duration = None  # Permanent ban
        warning_text = (
            "Permanent Ban\n\nYou have been banned from this group "
            "due to repeated rule violations."
        )

    # Send warning message and ban user if necessary
    await client.delete_messages(chat_id, message.message_id)
    await client.send_message(
        chat_id, 
        warning_text, 
        reply_to_message_id=message.message_id
    )

    # Log violation to LOG_CHANNEL
    log_message = (
        f"**Rule Violation**\n\nChat ID: {chat_id}\nUser ID: {user_id}\n"
        f"Username: {message.from_user.mention}\nRule Broken: {warning_text}\n"
        f"Date: {time.strftime('%Y-%m-%d')}\nTime: {time.strftime('%H:%M:%S')}"
    )
    await client.send_message(LOG_CHANNEL, log_message)

    if duration is not None:
        try:
            await client.restrict_chat_member(
                chat_id, 
                user_id, 
                can_send_messages=False, 
                until_date=int(time.time()) + duration
            )
            logger.info(
                f"Banned user {user_id} in chat {chat_id} for {duration} seconds"
            )
        except Exception as e:
            logger.error(f"Failed to ban user: {e}")

        # Schedule unban message
        await asyncio.sleep(duration)
        unban_message = (
            f"**Ban Ended**\n\nChat ID: {chat_id}\nUser ID: {user_id}\n"
            f"Username: {message.from_user.mention}\n"
            f"Rule Breaks: {rule_breaks + 1}"
        )
        await client.send_message(
            chat_id, 
            "Your ban has ended. Please refrain from violating group rules."
        )
        await client.send_message(LOG_CHANNEL, unban_message)
