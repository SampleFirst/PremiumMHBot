# pm_filter.py
import random
import logging
import asyncio

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

from info import ADMINS, PICS, LOG_CHANNEL
from database.users_chats_db import db

from Script import script
from plugins.datetime import get_datetime 
from plugins.expiry_datetime import get_expiry_datetime, get_expiry_name
from plugins.get_name import get_bot_name, get_db_name
from plugins.status_name import get_status_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

async def add_expiry_date_timer(user_id, bot_name, expiry_date):
    while True:
        current_time = get_datetime(format_type=21)
        if current_time >= expiry_date:
            user = await client.get_users(user_id)
            await client.send_message(user_id, f"Hey {user.username}, your attempt for {bot_name} has expired.")
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=f"Expiry message sent to user {user.username} for bot {bot_name}."
            )
            break
        await asyncio.sleep(20)  # Check every 20 seconds for expiry

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    if query.data == "close_data":
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
        await query.message.edit_text("Processing...")
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

    elif data == "bots":
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
        await query.message.edit_text("Processing...")
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

    elif data == "database":
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
        await query.message.edit_text("Processing...")
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
        user_id = query.from_user.id
        user_name = query.from_user.username
        bot_name = get_bot_name(query.data)
        now_status = get_status_name(status_num=1)
        now_date = get_datetime(format_type=21)
        expiry_date = get_expiry_datetime(format_type=21, expiry_option="now_to_1m")

        if await check_status_bot(client, user_id, bot_name):
            await query.answer(f"Hey {user_name}! Sorry For This But You already have an active request for {bot_name}.", show_alert=True)
            return
        else:
            return 
        
        buttons = [
            [
                InlineKeyboardButton('Description', callback_data='botdis'),
            ],
            [
                InlineKeyboardButton('Go Back', callback_data='bots')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SELECT_BOT.format(user=query.from_user.mention, bot_name=bot_name),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=script.LOG_DB.format(
                a=user_name,
                b=user_id,
                c=bot_name,
                d=now_status,
                e=now_date,
                f=expiry_date
            )
        )
   
    elif query.data == "mdb" or query.data == "adb" or query.data == "sdb" or query.data == "bdb":
        user_id = query.from_user.id
        user_name = query.from_user.username
        db_name = get_db_name(query.data)
        now_status = get_status_name(status_num=1)
        now_date = get_datetime(format_type=21)
        expiry_date = get_expiry_datetime(format_type=21, expiry_option="now_to_5m")
    
        if await db.is_status_exist_db(user_id, db_name, now_status):
            await query.answer(f"Hey {user_name}! Sorry For This But You already have an active request for {db_name}.", show_alert=True)
            return
        else:
            await query.message.edit_text("Processing...")
            
        buttons = [
            [
                InlineKeyboardButton('Description', callback_data='dbdis'),
            ],
            [
                InlineKeyboardButton('Go Back', callback_data='database')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await db.update_status_db(user_id, db_name, now_status, now_date, expiry_date)
        try:
            await add_expiry_date_timer(client, user_id, db_name, expiry_date)
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=script.LOG_DB.format(
                    a=user_name,
                    b=user_id,
                    c=db_name,
                    d=now_status,
                    e=now_date,
                    f=expiry_date
                )
            )
        except Exception as e:
            print(e)
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=str(e)
            )
        await client.edit_message_media(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            media=InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SELECT_DB.format(user=query.from_user.mention, db_name=db_name),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "botpre":
        await query.message.edit_text(
            text=script.BUY_BOT_PREMIUM.format(user=query.from_user.mention),
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "dbpre":
        await query.message.edit_text(
            text=script.BUY_DB_PREMIUM.format(user=query.from_user.mention),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "botdis":
        await query.answer(
            text=script.CONSTRUCTION.format(user=query.from_user.mention),
            show_alert=True
        )

    elif query.data == "dbdis":
        await query.answer(
            text=script.CONSTRUCTION.format(user=query.from_user.mention),
            show_alert=True
        )
        
