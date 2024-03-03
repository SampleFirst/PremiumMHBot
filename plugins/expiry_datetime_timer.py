# expiry_datetime_timer.py
import asyncio
from info import ADMINS, LOG_CHANNEL 
from database.users_chats_db import db
from Script import script
from plugins.datetime import get_datetime 
from plugins.expiry_datetime import get_expiry_datetime, get_expiry_name
from plugins.get_name import get_bot_name, get_db_name
from plugins.status_name import get_status_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

async def add_expiry_date_timer(user_id, expiry_date):
    current_time = datetime.datetime.now()
    time_difference = expiry_date - current_time
    await asyncio.sleep(time_difference.total_seconds())
    await db.update_status_bot(user_id, bot_name, now_status, expiry_date, expiry_date)
    await client.send_message(user_id, "Your premium status for the bot has expired.")
