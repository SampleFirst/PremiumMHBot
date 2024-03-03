# get_limit.py
import logging
from typing import Union

from database.users_chats_db import db
from pyrogram import Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define variables for attempt limits
MONTHLY_TOTAL_COUNT = 4
MONTHLY_SPECIFIC_COUNT = 4

DAILY_TOTAL_COUNT = 4
DAILY_SPECIFIC_COUNT = 4

async def get_users_limit(limit_type, username, userid, bot_name):
    if limit_type == 1:
        total_count = await total_attempt()
        if total_count >= MONTHLY_TOTAL_COUNT:
            await client.send_message("hii {username} This Monthly Premium limit is exceeded, try next calendar month or contact Admin! send  /help...")
            await client.send_message(LOG_CHANNEL, text=f"He ADMINS Monthly limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
            await client.send_message(ADMINS, text=f"He ADMINS Monthly limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
    elif limit_type == 2:
        bot_count = await specific_attempt(bot_name)
        if bot_count >= MONTHLY_SPECIFIC_COUNT:
            await client.send_message(f"hii {username} This {bot_name} This Month Premium limit is exceeded, try next calendar month or contact Admin! send  /help...")
            await client.send_message(LOG_CHANNEL, text=f"He ADMINS Monthly limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
            await client.send_message(ADMINS, text=f"He ADMINS Monthly limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
    elif limit_type == 3:
        total_count = await total_attempt()
        if total_count >= DAILY_TOTAL_COUNT:
            await client.send_message(f"hii {username} This Today Premium limit is exceeded, try next Tomorrow or contact Admin! send message with /send {{text message}}...")
            await client.send_message(LOG_CHANNEL, text=f"He ADMINS daily limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
            await client.send_message(ADMINS, text=f"He ADMINS daily limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
    elif limit_type == 4:
        bot_count = await specific_attempt(bot_name)
        if bot_count >= DAILY_SPECIFIC_COUNT:
            await client.send_message(f"hii {username} This {bot_name} Today Premium limit is exceeded, try Tomorrow or contact Admin! send message with /send {{text message}}...")
            await client.send_message(LOG_CHANNEL, text=f"He ADMINS Today limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
            await client.send_message(ADMINS, text=f"He ADMINS Today  limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
    else:
        raise ValueError("Invalid limit_type. Please choose a number between 1 and 4.")
