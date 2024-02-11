import logging
from pyrogram import Client

from info import ADMINS, LOG_CHANNEL
from database.users_chats_db import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

MONTHLY = False 
BOT_NAME = False 

# Define quotas
MONTHLY_TOTAL_COUNT = 1000
DAILY_TOTAL_COUNT = 1

MONTHLY_SPECIFIC_COUNT = {
    "Movies Bot": 200,
    "Anime Bot": 300,
    "Rename Bot": 150,
    "YT Downloader": 250,
}

DAILY_SPECIFIC_COUNT = {
    "Movies Bot": 1,
    "Anime Bot": 1,
    "Rename Bot": 1,
    "YT Downloader": 1,
}

MONTHLY_QUOTAS = {
    "total": MONTHLY_TOTAL_COUNT,
    "Movies Bot": MONTHLY_SPECIFIC_COUNT["Movies Bot"],
    "Anime Bot": MONTHLY_SPECIFIC_COUNT["Anime Bot"],
    "Rename Bot": MONTHLY_SPECIFIC_COUNT["Rename Bot"],
    "YT Downloader": MONTHLY_SPECIFIC_COUNT["YT Downloader"],
}

DAILY_QUOTAS = {
    "total": DAILY_TOTAL_COUNT,
    "Movies Bot": DAILY_SPECIFIC_COUNT["Movies Bot"],
    "Anime Bot": DAILY_SPECIFIC_COUNT["Anime Bot"],
    "Rename Bot": DAILY_SPECIFIC_COUNT["Rename Bot"],
    "YT Downloader": DAILY_SPECIFIC_COUNT["YT Downloader"],
}

# Function to check if monthly quota is reached
def is_monthly_quota_reached(bot_name=None):
    if not BOT_NAME:
        return (
            db.total_premiums_monthly() >= MONTHLY_QUOTAS["total"]
            or db.total_confirms_monthly() >= MONTHLY_QUOTAS["total"]
            or db.total_attempts_monthly() >= MONTHLY_QUOTAS["total"]
        )
    else:
        return (
            db.total_premiums_monthly(bot_name) >= MONTHLY_QUOTAS[bot_name]
            or db.total_confirms_monthly(bot_name) >= MONTHLY_QUOTAS[bot_name]
            or db.total_attempts_monthly(bot_name) >= MONTHLY_QUOTAS[bot_name]
        )

# Function to check if daily quota is reached
def is_daily_quota_reached(bot_name=None):
    if not BOT_NAME:
        return (
            db.total_premiums_daily() >= DAILY_QUOTAS["total"]
            or db.total_confirms_daily() >= DAILY_QUOTAS["total"]
            or db.total_attempts_daily() >= DAILY_QUOTAS["total"]
        )
    else:
        return (
            db.total_premiums_daily(bot_name) >= DAILY_QUOTAS[bot_name]
            or db.total_confirms_daily(bot_name) >= DAILY_QUOTAS[bot_name]
            or db.total_attempts_daily(bot_name) >= DAILY_QUOTAS[bot_name]
        )

# Function to send a quota-reached message
async def send_quota_reached_message(user_name, bot_name=None):
    message = (
        f"Hi {user_name}, your monthly quota for {bot_name if BOT_NAME else 'all bots'} "
        "has been reached. Please try again next month or contact admin."
    )
    await client.send_message(LOG_CHANNEL, message)

# Function to check user's limit (monthly or daily)
async def get_user_limit(user_name, bot_name=None):
    if MONTHLY:
        if is_monthly_quota_reached(bot_name):
            await send_quota_reached_message(user_name, bot_name)
            return True
    else:
        if is_daily_quota_reached(bot_name):
            await send_quota_reached_message(user_name, bot_name)
            return True
