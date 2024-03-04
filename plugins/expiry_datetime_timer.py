import logging
import asyncio
from datetime import datetime
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.errors import MessageNotModified
from info import ADMINS, LOG_CHANNEL
from database.users_chats_db import db
from plugins.datetime import get_datetime
from plugins.expiry_datetime import get_expiry_datetime, get_expiry_name
from plugins.get_name import get_bot_name, get_db_name
from plugins.status_name import get_status_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

async def add_expiry_date_timer(client: Client, user_id, bot_name, expiry_date):
    expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()  # Assign current time here
    
    time_difference = expiry_date - current_time
    await asyncio.sleep(time_difference.total_seconds())
    
    user_id = user_id
    bot_name = bot_name
    now_status = get_status_name(status_num=7)
    now_date = get_datetime(format_type=21)
    
    try:
        await db.update_status_bot(user_id, bot_name, now_status, now_date, None)
        await client.send_message(user_id, f"Your attempt status for the {bot_name} has expired.")
        await client.send_message(LOG_CHANNEL, f"{user_id} attempt status for the {bot_name} has expired. and new Status {now_status}")
    except MessageNotModified:
        logger.error("Message was not modified")
