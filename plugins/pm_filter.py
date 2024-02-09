# callback.py
import random
import logging
from datetime import datetime

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

from info import ADMINS, PICS, LOG_CHANNEL
from database.users_chats_db import db

from Script import script
from utils import temp
from plugins.datetime import get_datetime 
from plugins.expiry_datetime import get_expiry_datetime
from plugins.get_name import get_bot_name, get_db_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

         
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "cancel":
        await query.message.delete()

    elif query.data == "start":
        buttons = [
            [
                InlineKeyboardButton('My Plan', callback_data="plan"),
                InlineKeyboardButton('Status', callback_data="status")
            ],
            [
                InlineKeyboardButton('Bots Premium', callback_data="bots"),
                InlineKeyboardButton('Database Premium', callback_data="database")
            ],
            [
                InlineKeyboardButton('Bots Pack', callback_data="botspack"),
                InlineKeyboardButton('Database Pack', callback_data="dbpack")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.START_TXT.format(user=query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "plan":
        await query.answer(
            text=script.CONSTRUCTION.format(user=query.from_user.mention),
            show_alert=True
        )

    elif query.data == "status":
        await query.answer(
            text=script.CONSTRUCTION.format(user=query.from_user.mention),
            show_alert=True
        )

    elif query.data == "bots":
        buttons = [
            [
                InlineKeyboardButton('Movies Bot', callback_data='mbot'),
                InlineKeyboardButton('Anime Bot', callback_data='abot')
            ],
            [
                InlineKeyboardButton('Rename Bot', callback_data='rbot'),
                InlineKeyboardButton('YT Downloader', callback_data='dbot')
            ],
            [
                InlineKeyboardButton('Back', callback_data='start')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.BOTS.format(user=query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "database":
        buttons = [
            [
                InlineKeyboardButton('Movies Database', callback_data='mdb'),
                InlineKeyboardButton('Anime Database', callback_data='adb')
            ],
            [
                InlineKeyboardButton('TV Show Database', callback_data='sdb'),
                InlineKeyboardButton('Audio Books', callback_data='bdb')
            ],
            [
                InlineKeyboardButton('Back', callback_data='start')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.DATABASE.format(user=query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "botspack":
        await query.answer(
            text=script.CONSTRUCTION.format(user=query.from_user.mention),
            show_alert=True
        )

    elif query.data == "dbpack":
        await query.answer(
            text=script.CONSTRUCTION.format(user=query.from_user.mention),
            show_alert=True
        )

    elif query.data == "mbot" or query.data == "abot" or query.data == "rbot" or query.data == "dbot":
        bot_name = get_bot_name(query.data)
        buttons = [
            [
                InlineKeyboardButton('Confirmed Premium', callback_data='botpre'),
            ],
            [
                InlineKeyboardButton('Go Back', callback_data='bots'),
            ],
            [
                InlineKeyboardButton('Cancel', callback_data='cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.BOT_SELECTED.format(user=query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "mdb" or query.data == "adb" or query.data == "sdb" or query.data == "bdb":
        db_name = get_db_name(query.data)
        now_date = get_datetime(1)
        now_time = get_datetime(3)
        base_datetime, base_date, base_time, expiry_date, expiry_time, expiry_name = get_expiry_datetime(2, None, "today_to_30d")
        buttons = [
            [
                InlineKeyboardButton('Confirmed Premium', callback_data='dbpre'),
            ],
            [
                InlineKeyboardButton('Go Back', callback_data='database'),
            ],
            [
                InlineKeyboardButton('Cancel', callback_data='cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        caption = f"""Hey {query.from_user.mention}, Good Choice!
            Bot Name: {db_name}
            Today's Date: {now_date}
            Current Time: {now_time}
            Expiry Date: {expiry_date}
            Expiry Time: {expiry_time}
            Expires on: {expiry_name}
            """
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "botpre":
        await query.message.edit_text(
            text=script.BUY_BOT_PREMIUM.format(user=query.from_user.mention),
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "dbpre":
        await query.message.edit_text(
            text=script.BUY_DB_PREMIUM.format(user=query.from_user.mention),
            parse_mode=enums.ParseMode.HTML
        )
        
