import logging
from pyrogram import Client

from info import ADMINS, LOG_CHANNEL
from database.users_chats_db import db
from interval_functions import get_date_range

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
    **{bot: MONTHLY_SPECIFIC_COUNT[bot] for bot in MONTHLY_SPECIFIC_COUNT},
}

DAILY_QUOTAS = {
    "total": DAILY_TOTAL_COUNT,
    **{bot: DAILY_SPECIFIC_COUNT[bot] for bot in DAILY_SPECIFIC_COUNT},
}

# Function to check if monthly quota is reached
def is_monthly_quota_reached(interval='monthly', bot_name=None):
    if not BOT_NAME:
        return (
            db.total_active_premium_sorted('monthly') >= MONTHLY_QUOTAS["total"]
            or db.total_active_confirms_sorted('monthly') >= MONTHLY_QUOTAS["total"]
            or db.total_active_attempts_sorted('monthly') >= MONTHLY_QUOTAS["total"]
        )
    else:
        return (
            db.total_active_premium_sorted('monthly', bot_name) >= MONTHLY_QUOTAS.get(bot_name, 0)
            or db.total_active_confirms_sorted('monthly', bot_name) >= MONTHLY_QUOTAS.get(bot_name, 0)
            or db.total_active_attempts_sorted('monthly', bot_name) >= MONTHLY_QUOTAS.get(bot_name, 0)
        )

# Function to check if daily quota is reached
def is_daily_quota_reached(interval='daily', bot_name=None):
    if not BOT_NAME:
        return (
            db.total_active_premium_sorted('daily') >= DAILY_QUOTAS["total"]
            or db.total_active_confirms_sorted('daily') >= DAILY_QUOTAS["total"]
            or db.total_active_attempts_sorted('daily') >= DAILY_QUOTAS["total"]
        )
    else:
        return (
            db.total_active_premium_sorted('daily', bot_name) >= DAILY_QUOTAS.get(bot_name, 0)
            or db.total_active_confirms_sorted('daily', bot_name) >= DAILY_QUOTAS.get(bot_name, 0)
            or db.total_active_attempts_sorted('daily', bot_name) >= DAILY_QUOTAS.get(bot_name, 0)
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

# Function to count premium, confirm, and attempt totals
async def count_totals(interval='', bot_name=None):
    if MONTHLY:
        if BOT_NAME:
            return {
                "premiums": db.total_active_premium_sorted('monthly', bot_name),
                "confirms": db.total_active_confirms_sorted('monthly', bot_name),
                "attempts": db.total_active_attempts_sorted('monthly', bot_name)
            }
        else:
            return {
                "premiums": db.total_active_premium_sorted('monthly'),
                "confirms": db.total_active_confirms_sorted('monthly'),
                "attempts": db.total_active_attempts_sorted('monthly')
            }
    else:
        if BOT_NAME:
            return {
                "premiums": db.total_active_premium_sorted('daily'),
                "confirms": db.total_active_confirms_sorted('daily'),
                "attempts": db.total_active_attempts_sorted('daily')
            }
        else:
            return {
                "premiums": db.total_active_premium_sorted('daily', bot_name),
                "confirms": db.total_active_confirms_sorted('daily', bot_name),
                "attempts": db.total_active_attempts_sorted('daily', bot_name)
            }
            

