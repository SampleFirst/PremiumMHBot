# callback.py
import random
import asyncio
import logging
from datetime import datetime

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

from info import ADMINS, PICS, LOG_CHANNEL
from database.users_chats_db import db

from Script import script
from utils import temp
from plugins.datetime import get_datetime 
from plugins.expiry_datetime import get_expiry_datetime, get_expiry_name
from plugins.get_name import get_bot_name, get_db_name
from plugins.premium_limit import get_user_limit, count_totals

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Define a dictionary to store user states (locked or not)
USER_STATS = {}
USER_SELECTED = {}
VERIFIED_ONLY = True

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if VERIFIED_ONLY
        try:
            chatIDx = message.chat.id
            lazy_chatIDx = await db.get_chat(int(chatIDx))
            if lazy_chatIDx['is_verified']:
                k = await manual_filters(client, message)
        except Exception as e:
            logger.error(f"Chat not verifeid : {e}") 
    
        if k == False:
            try:
                chatID = message.chat.id
                lazy_chatID = await db.get_chat(int(chatID))
                if lazy_chatID['is_verified']:
                    await auto_filter(client, message)
            except Exception as e:
                logger.error(f"Chat Not verified : {e}") 
    else:
        k = await manual_filters(client, message)
        if k == False:
            await auto_filter(client, message)
    

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "cancel":
        await query.message.delete()

    elif data.startswith("verify_chat"):
        _, chatTitle, chatID = data.split(":")
        try:
            await client.send_message(chatID, text="Hello users! From now I will provide you contents 24X7 💘")
            await db.verify_chat(int(chatID))
            temp.VERIFIED_CHATS.append(int(chatID))
            btn = [
                [InlineKeyboardButton(text="🚫 BAN Chat 🤐", callback_data=f"banchat:{chatTitle}:{chatID}")],
                [InlineKeyboardButton(text="❌ Close ❌", callback_data="close_data")]
            ]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.edit_message_text(f"**🍁 Chat successfully verified 🧡**\n\n**Chat ID**: {chatID}\n**Chat Title**: {chatTitle}", reply_markup=reply_markup)
        except Exception as e:
            await query.edit_message_text(f"Got a Lazy error:\n{e}")
            logger.error(f"Please solve this Error Lazy Bro: {e}")

    elif data.startswith("banchat"):
        _, chatTitle, chatID = data.split(":")
        try:
            await client.send_message(chatID, text="Oops! Sorry, Let's Take a break\nThis is my last and Good Bye message to you all.\n\nContact my admin for more info")
            await db.disable_chat(int(chatID))
            temp.BANNED_CHATS.append(int(chatID))
            btn = [
                [InlineKeyboardButton(text="⚡ Enable Chat 🍁", callback_data=f"enablechat:{chatTitle}:{chatID}")],
                [InlineKeyboardButton(text="❌ Close ❌", callback_data="close_data")]
            ]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.edit_message_text(f"**Chat successfully disabled ✅**\n\n**Chat ID**: {chatID}\n**Chat Title**: {chatTitle}", reply_markup=reply_markup)
        except Exception as e:
            await query.edit_message_text(f"Got a Lazy error:\n{e}")
            logger.error(f"Please solve this Error Lazy Bro: {e}")

    elif data.startswith("enablechat"):
        _, chatTitle, chatID = data.split(":")
        try:
            sts = await db.get_chat(int(chatID))
            if not sts:
                return await query.answer("Chat Not Found In DB!", show_alert=True)
            if not sts.get('is_disabled'):
                return await query.answer('This chat is not yet disabled.', show_alert=True)
            await db.re_enable_chat(int(chatID))
            temp.BANNED_CHATS.remove(int(chatID))
            btn = [
                [InlineKeyboardButton(text="😜 BAN Again 😂", callback_data=f"banchat:{chatTitle}:{chatID}")],
                [InlineKeyboardButton(text="❌ Close ❌", callback_data="close_data")]
            ]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.edit_message_text(f"**Chat successfully Enabled 💞**\n\n**Chat ID**: {chatID}\n**Chat Title**: {chatTitle}", reply_markup=reply_markup)
        except Exception as e:
            await query.edit_message_text(f"Got a Lazy error:\n{e}")
            logger.error(f"Please solve this Error Lazy Bro: {e}")

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
        user_id = query.from_user.id
        user_name = query.from_user.username
        bot_name = get_bot_name(query.data)
        type = "Bot"
        now_date = get_datetime(format_type=1)
        now_time = get_datetime(format_type=3)
        expiry_date, _ = get_expiry_datetime(format_type=1, expiry_option="today_to_30d")
        _, expiry_time = get_expiry_datetime(format_type=3, expiry_option="today_to_30d")
        expiry_name = get_expiry_name("today_to_30d")
        totals = await count_totals()

        # Check if an attempt is already active for the user with the same bot_name
        if await db.is_attempt_active(user_id, bot_name, type):
            await query.answer(f"Hey {user_name}! Sorry For This But You already have an active request for {bot_name}.", show_alert=True)
            return
        else:
            # Add attempt to the database
            await db.add_attempt(user_id, bot_name, type, now_date, expiry_date)

            today = datetime.now().date()
            month = datetime.now().month
            year = datetime.now().year
            
            total_daily_attempt = await db.daily_attempts_count(today)
            total_monthly_attempt = await db.monthly_attempts_count(month, year)
            total_daily_bot_attempt = await db.daily_attempts_count(today, bot_name)
            total_monthly_bot_attempt = await db.monthly_attempts_count(month, year, bot_name)

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
            caption = f"""✦ Hey {user_name}, Best Choice!\n\n✦ Bot Name: {bot_name}\n✦ Today's Date: {now_date}\n✦ Current Time: {now_time}\n✦ Expiry Date: {expiry_date}\n✦ Expiry Time: {expiry_time}\n✦ Expires on: {expiry_name}"""
            caption += f"""\n\n✦ Today Total Attempts: {total_daily_attempt}\n✦ Month Total Attempts: {total_monthly_attempt}\n✦ Total {bot_name} Daily Attempts: {total_daily_bot_attempt}\n✦ Total {bot_name} Monthly Attempts: {total_monthly_bot_attempt}"""
            caption += f"""\n\n🏅 Premiums: {totals["premiums"]}\n🥈 Confirms: {totals["confirms"]}\n🥇 Attempts: {totals["attempts"]}"""
            caption += f"""\n\nToday: {today}\nMonth: {month}\nYear: {year}"""
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
        
    elif query.data == "mdb" or query.data == "adb" or query.data == "sdb" or query.data == "bdb":
        db_name = get_db_name(query.data)
        now_date = get_datetime(1)
        now_time = get_datetime(3)
        expiry_date, _ = get_expiry_datetime(format_type=1, expiry_option="today_to_30d")
        _, expiry_time = get_expiry_datetime(format_type=3, expiry_option="today_to_30d")
        expiry_name =  get_expiry_name("today_to_30d")
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
        reply_markup = InlineKeyboardMarkup(buttons)
        caption = f"""✦ Hey {query.from_user.mention}, Best Choice!\n\n✦ Db Name: {db_name}\n✦ Today's Date: {now_date}\n✦ Current Time: {now_time}\n✦ Expiry Date: {expiry_date}\n✦ Expiry Time: {expiry_time}\n✦ Expires on: {expiry_name}"""
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
        
