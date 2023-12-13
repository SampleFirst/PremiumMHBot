import random
import logging
import datetime
import pytz

from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import MessageNotModified, PeerIdInvalid

from info import ADMINS, PICS
from database.users_chats_db import db

from Script import script

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    is_admin = query.from_user.id in ADMINS
    if query.data == "close_data":
        await query.message.delete()

    elif query.data == "start":
        buttons = [
            [
                InlineKeyboardButton('Bots Premium', callback_data="bots"),
                InlineKeyboardButton('Database Premium', callback_data="database")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        caption = script.START_TXT.format(user=query.from_user.mention, bot=temp.B_LINK)

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

    elif query.data == "bots":
        buttons = [
            [
                InlineKeyboardButton('Movies Bot', callback_data='mbot'),
                InlineKeyboardButton('Anime Bot', callback_data='abot')
            ],
            [
                InlineKeyboardButton('Rename Bot', callback_data='rbot'),
                InlineKeyboardButton('Yt & Insta Bot', callback_data='yibot')
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
            text=script.BOTS.format(query.from_user.mention),
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
                InlineKeyboardButton('TV Show Database', callback_data='tvsdb'),
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
            text=script.DATABSE.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "mbot" or query.data == "abot" or query.data == "rbot" or query.data == "yibot":
        # Display monthly plan message for selected bot
        validity_date = datetime.datetime.now() + datetime.timedelta(days=30)
        validity_formatted = validity_date.strftime("%B %d, %Y")

        buttons = [
            [
                InlineKeyboardButton('Confirmed', callback_data=f'confirm_bot_{query.data}'),
                InlineKeyboardButton('Description', callback_data=f'description_{query.data}')
            ],
            [
                InlineKeyboardButton('Back', callback_data='bots')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        message_text = f"🍿 **{query.data.capitalize()} Premium Plan** 🍿\n\n"
        message_text += f"This plan is valid until {validity_date}.\n\n"
        message_text += "Make Payments And Then Select **Confirmed** Button:"
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )

    elif query.data.startswith("confirm_bot_"):
        # Handle user confirming bot subscription
        selected_bot = query.data.replace("confirm_bot_", "")
        # Add logic to save user subscription details and handle payment confirmation by admins
        confirmation_message = f"Subscription Confirmed for {selected_bot.capitalize()}!\n\n"
        confirmation_message += f"Please send a payment screenshot for confirmation to the admins."
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=confirmation_message
        )
    
    elif query.data.startswith("description_"):
        selected_bot_type = query.data.replace("description_", "")
        description_text = ""

        if selected_bot_type == "mbot":
            description_text = script.MOVIES_TEXT.format(query.from_user.mention)
        elif selected_bot_type == "abot":
            description_text = script.ANIME_TEXT.format(query.from_user.mention)
        elif selected_bot_type == "rbot":
            description_text = script.RENAME_TEXT.format(query.from_user.mention)
        elif selected_bot_type == "yibot":
            description_text = script.YT_TEXT.format(query.from_user.mention)

        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=description_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    elif query.data == "mdb" or query.data == "adb" or query.data == "tvsdb":
        # Display monthly plan message for selected bot
        validity_date = datetime.datetime.now() + datetime.timedelta(days=30)
        validity_formatted = validity_date.strftime("%B %d, %Y")

        buttons = [
            [
                InlineKeyboardButton('Confirmed', callback_data=f'confirm_db_{query.data}'),
                InlineKeyboardButton('Description', callback_data=f'description_db_{query.data}')
            ],
            [
                InlineKeyboardButton('Back', callback_data='bots')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        message_text = f"🍿 **{query.data.capitalize()} Premium Database** 🍿\n\n"
        message_text += f"This plan is valid until {validity_date}.\n\n"
        message_text += "Make Payments And Then Select **Confirmed** Button:"
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    elif query.data.startswith("confirm_db_"):
        # Handle user confirming bot subscription
        selected_bot = query.data.replace("confirm_db_", "")
        # Add logic to save user subscription details and handle payment confirmation by admins
        confirmation_message = f"Subscription Confirmed for {selected_bot.capitalize()}!\n\n"
        confirmation_message += f"Please send a payment screenshot for confirmation to the admins."
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=confirmation_message
        )
    
    elif query.data.startswith("description_db_"):
        selected_bot_type = query.data.replace("description_", "")
        description_text = ""

        if selected_bot_type == "mdb":
            description_text = script.MOVIESDB_TEXT.format(query.from_user.mention)
        elif selected_bot_type == "adb":
            description_text = script.ANIMEDB_TEXT.format(query.from_user.mention)
        elif selected_bot_type == "tvsdb":
            description_text = script.SERIESDB_TEXT.format(query.from_user.mention)
        
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=description_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
