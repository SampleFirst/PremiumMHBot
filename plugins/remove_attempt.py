import os
import logging
import random
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.attempt_db import db
from info import ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS
from utils import is_subscribed, temp
from datetime import date, datetime
from Script import script
import pytz

logger = logging.getLogger(__name__)

@Client.on_message(filters.command('remove_attempts'))
async def update_attempts(bot, message):
    """Updates active attempts for the user who sent the command."""
    user_id = message.from_user.id

    try:
        await db.update_active_attempts(user_id)
        await message.reply_text("All active attempts have been updated.")
    except Exception as e:
        logger.error(f"Error updating attempts: {e}")
        await message.reply_text(f"An error occurred: {e}")
