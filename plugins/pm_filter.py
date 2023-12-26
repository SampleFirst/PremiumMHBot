import random
import logging
import datetime
import pytz

from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, Message
from pyrogram import Client, filters, enums
from pyrogram.errors import MessageNotModified, PeerIdInvalid

from info import ADMINS, PICS, LOG_CHANNEL, PAYMENT_CHAT, TOTAL_MEMBERS, MOVIES_DB, ANIME_DB, SERIES_DB
from database.users_chats_db import db

from Script import script
from utils import temp

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Define a dictionary to store user states (locked or not)
user_states = {}
USER_SELECTED = {}

@Client.on_message(filters.photo & filters.private)
async def payment_screenshot_received(client, message):
    user_id = message.from_user.id
    file_id = str(message.photo.file_id)

    # Check if the user has made a selection before sending the screenshot
    if user_id not in user_states or not user_states[user_id]:
        await message.reply_text("Please select Bot or Database before sending the screenshot.")
        return

    selected_type = USER_SELECTED.get(user_id, "")

    if not selected_type:
        await message.reply_text("Invalid selection. Please start the process again.")
        return

    # Update if and elif conditions for selected_type
    if selected_type in {"mbot", "abot", "rbot", "yibot"}:
        await handle_bot_screenshot(client, message, user_id, file_id)
    elif selected_type in {"mdb", "adb", "tvsdb"}:
        await handle_db_screenshot(client, message, user_id, file_id)
    else:
        await message.reply_text("Invalid selection. Start the process again.")


async def handle_bot_screenshot(client, message, user_id, file_id):
    latest_attempt = await db.get_latest_attempt_dot(user_id)

    if not latest_attempt:
        await message.reply_text("Unable to retrieve latest attempt details. Please try again.")
        return

    user_name = latest_attempt['user_name']
    selected_bot = latest_attempt.get('selected_bot', '')
    attempt_number = latest_attempt['attempt_number']
    current_date_time = latest_attempt['current_date_time']
    validity_date = latest_attempt['validity_date']

    caption_bot = f"User ID: {user_id}\n" \
              f"User Name: {user_name}\n" \
              f"Selected Bot: {selected_bot.capitalize()}\n" \
              f"Attempt Number: {attempt_number}\n" \
              f"Date and Time: {current_date_time}\n" \
              f"Validity: {validity_date}\n"

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✅ Confirmed", callback_data=f"payment_confirmed_bot"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"payment_cancel_bot")
        ]]
    )

    await client.send_photo(chat_id=LOG_CHANNEL, photo=file_id, caption=caption_bot, reply_markup=keyboard)
    await message.reply_text(f"Hey {user_name}!\n\nYour Payment Screenshot Received. Wait for Confirmation by Admin.\n\nSending Confirmation Message Soon...")
    user_states[user_id] = False

async def handle_db_screenshot(client, message, user_id, file_id):
    latest_attempt = await db.get_latest_attempt_db(user_id)

    if not latest_attempt:
        await message.reply_text("Unable to retrieve latest attempt details. Please try again.")
        return

    user_name = latest_attempt['user_name']
    selected_db = latest_attempt.get('selected_db', '')
    attempt_number = latest_attempt['attempt_number']
    current_date_time = latest_attempt['current_date_time']
    validity_date = latest_attempt['validity_date']

    caption_db = f"User ID: {user_id}\n" \
              f"User Name: {user_name}\n" \
              f"Selected DB: {selected_db.capitalize()}\n" \
              f"Attempt Number: {attempt_number}\n" \
              f"Date and Time: {current_date_time}\n" \
              f"Validity: {validity_date}\n"

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✅ Confirmed", callback_data=f"payment_confirmed_db"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"payment_cancel_db")
        ]]
    )

    await client.send_photo(chat_id=LOG_CHANNEL, photo=file_id, caption=caption_db, reply_markup=keyboard)
    await message.reply_text(f"Hey {user_name}!\n\nYour Payment Screenshot Received. Wait for Confirmation by Admin.\n\nSending Confirmation Message Soon...")
    user_states[user_id] = False

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
                ],
                [
                    InlineKeyboardButton('Cancel', callback_data="close_data")
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
                InlineKeyboardButton('YT Downloader', callback_data='yibot')
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
                InlineKeyboardButton('TV Show Database', callback_data='tvsdb'),
                InlineKeyboardButton('Audio Books', callback_data='abdb')
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
            text=script.DATABSE.format(user=query.from_user.mention),
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
                InlineKeyboardButton('Description', callback_data=f'description_bot_{query.data}')
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
        user_name = query.from_user.username
        user_id = query.from_user.id

        bot_name = selected_bot.capitalize()
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        validity_date = datetime.datetime.now() + datetime.timedelta(days=30)
        validity_formatted = validity_date.strftime("%B %d, %Y")

        await db.add_attempt_dot(user_id, user_name, selected_bot, 1, current_date_time, validity_date)
        USER_SELECTED[user_id] = selected_bot
        
        confirmation_message = f"Subscription Confirmed for {selected_bot.capitalize()}!\n\n"
        confirmation_message += f"Please send a payment screenshot for confirmation to the admins."

        admin_confirmation_message = (
            f"Subscription Confirmed:\n\n"
            f"User: {user_name}\n"
            f"Bot: {selected_bot.capitalize()}\n"
            f"Date: {current_date_time}\n"
            f"Validity: {validity_formatted}\n\n"
            f"Please verify and handle the payment."
        )

        # Send Log about successful subscription
        await client.send_message(chat_id=LOG_CHANNEL, text=admin_confirmation_message)

        # Notify user about successful subscription
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=confirmation_message
        )
        user_states[user_id] = True
        
        
    
    elif query.data.startswith("description_bot_"):
        selected_bot_type = query.data.replace("description_bot_", "")
        description_text = ""

        if selected_bot_type == "mbot":
            description_text = script.MOVIES_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "abot":
            description_text = script.ANIME_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "rbot":
            description_text = script.RENAME_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "yibot":
            description_text = script.YT_TEXT.format(user=query.from_user.mention)

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
        selected_db = query.data.replace("confirm_db_", "")
        user_name = query.from_user.username
        user_id = query.from_user.id

        db_name = selected_db.capitalize()
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        validity_date = datetime.datetime.now() + datetime.timedelta(days=30)
        validity_formatted = validity_date.strftime("%B %d, %Y")

        await db.add_attempt_db(user_id, user_name, selected_db, 1, current_date_time, validity_date)
        USER_SELECTED[user_id] = selected_db

        confirmation_message = f"Subscription Confirmed for {selected_db.capitalize()}!\n\n"
        confirmation_message += f"Please send a payment screenshot for confirmation to the admins."
    
        admin_confirmation_message = (
            f"Subscription Confirmed:\n\n"
            f"User: {user_name}\n"
            f"Database: {selected_db.capitalize()}\n"
            f"Date: {current_date_time}\n"
            f"Validity: {validity_formatted}\n\n"
            f"Please verify and handle the payment."
        )
        # Send Log about successful subscription
        await client.send_message(chat_id=LOG_CHANNEL, text=admin_confirmation_message)
    
        # Notify user about successful subscription
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=confirmation_message
        )
        user_states[user_id] = True
        
    
    elif query.data.startswith("description_db_"):
        selected_bot_type = query.data.replace("description_", "")
        description_text = ""

        if selected_bot_type == "mdb":
            description_text = script.MOVIESDB_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "adb":
            description_text = script.ANIMEDB_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "tvsdb":
            description_text = script.SERIESDB_TEXT.format(user=query.from_user.mention)
        
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=description_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )

    elif query.data == "payment_confirmed_bot":
        if is_admin:
            # Handle payment confirmation by admins
            user_id = query.message.caption.split('\n')[0].split(': ')[1]
            selected_bot = query.message.caption.split('\n')[2].split(': ')[1].lower()
            latest_attempt = await db.get_latest_attempt_dot(user_id)

            if selected_bot == 'mbot':
                await client.send_message(PAYMENT_CHAT, f"/add {user_id}")
            elif selected_bot == 'abot':
                await client.send_message(PAYMENT_CHAT, f"/pre {user_id}")
            elif selected_bot == 'rbot':
                await client.send_message(PAYMENT_CHAT, f"/try {user_id}")
            elif selected_bot == 'yibot':
                await client.send_message(PAYMENT_CHAT, f"/pro {user_id}")
                
            # Add user to premium database
            await db.add_premium_user_dot(user_id, latest_attempt['user_name'], selected_bot, current_date_time, latest_attempt['validity_months'])

            # Display message for active premium plan
            validity_formatted = validity_date.strftime("%B %d, %Y")
            active_plan_message = f"🌟 **Active Premium Plan** 🌟\n\n"
            active_plan_message += f"User: {latest_attempt['user_name']}\n"
            active_plan_message += f"Bot: {selected_bot.capitalize()}\n"
            active_plan_message += f"Valid Until: {validity_formatted}"

            await query.answer(active_plan_message, show_alert=True)
        else:
            await query.answer('This Button Only For ADMINS', show_alert=True)

    elif query.data == "payment_cancel_bot":
        if is_admin:
            # Handle payment confirmation by admins
            user_id = query.message.caption.split('\n')[0].split(': ')[1]
            selected_bot = query.message.caption.split('\n')[2].split(': ')[1].lower()
            latest_attempt = await db.get_latest_attempt_dot(user_id)

            # Add user to premium database
            await db.add_cancel_user_dot(user_id, user_name, selected_bot, current_date_time)
            
            # Notify ADMINS about the payment cancellation
            admin_message = f"❌ Payment Cancelled for user ID: {user_id}"
            admin_message += f"User: {latest_attempt['user_name']}\n"
            admin_message += f"Bot: {selected_bot.capitalize()}"
            
            await client.send_message(chat_id=ADMINS, text=admin_message)

            # Notify the user about the payment cancellation
            user_message = "Your payment Screenshot Not Valid Send Again Valid Payment Screenshot..."
            await client.edit_message_media(
                query.message.chat.id,
                query.message.id,
                InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(text=user_message)
    
    

    elif query.data == "payment_confirmed_db":
        if is_admin:
            # Handle payment confirmation by admins
            user_id = query.message.caption.split('\n')[0].split(': ')[1]
            selected_db = query.message.caption.split('\n')[2].split(': ')[1].lower()
            latest_attempt = await db.get_latest_attempt_db(user_id)

            # Check which database is selected and send invite link to the appropriate channel
            if selected_db == 'mdb':
                channel_name = MOVIES_DB
            elif selected_db == 'adb':
                channel_name = ANIME_DB
            elif selected_db == 'tvsdb':
                channel_name = SERIES_DB
            else:
                # Handle invalid database selection
                await query.answer('Invalid database selection', show_alert=True)
                return

            # Get the current total members of the channel
            current_members = await client.get_chat_members_count(channel_name)

            # Check if the channel is almost full (last 5 seats)
            if TOTAL_MEMBERS - current_members <= 5:
                admin_notification = f"Attention! {selected_db.capitalize()} channel has only 5 seats left."
                await client.send_message(chat_id=ADMINS, text=admin_notification)

            # Check if the channel is full, if yes, find the next available channel
            while current_members >= TOTAL_MEMBERS:
                channel_name = get_next_channel(channel_name)  # Implement a function to get the next channel
                current_members = await client.get_chat_members_count(channel_name)

            try:
                # Create a temporary invite link with the user ID as a parameter
                invite_link = await client.create_chat_invite_link(
                    chat_id=int(channel_name),
                    member_id=user_id,
                    expire_date=int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp())
                )
            except ChatAdminRequired:
                logger.error("Make sure Bot is admin in Forcesub channel")
                return

            btn = [
                [
                    InlineKeyboardButton("Join Channel", url=invite_link.invite_link)
                ]
            ]

            await client.send_message(
                chat_id=message.from_user.id,
                text=f"**Hello {message.from_user.mention}, Join {selected_db.capitalize()}",
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN,
            )

            # Save data in users_chats_db
            await db.add_premium_user_db(user_id, latest_attempt['user_name'], selected_db, current_date_time, latest_attempt['validity_months'])

            # Notify the user about successful subscription and provide the invite link
            user_message = f"Subscription Confirmed for {selected_db.capitalize()}!\n\n{invite_message}"
            await client.send_message(user_id, user_message)

            # Send Log about successful subscription
            admin_message = f"Subscription Confirmed for user ID: {user_id}\nUser: {latest_attempt['user_name']}\nDatabase: {selected_db.capitalize()}"
            await client.send_message(chat_id=ADMINS, text=admin_message)

    elif query.data == "payment_cancel_db":
        if is_admin:
            # Handle payment confirmation by admins
            user_id = query.message.caption.split('\n')[0].split(': ')[1]
            selected_db = query.message.caption.split('\n')[2].split(': ')[1].lower()
            latest_attempt = await db.get_latest_attempt_db(user_id)

            # Add user to premium database
            await db.add_cancel_user_db(user_id, user_name, selected_db, current_date_time)
            
            # Notify ADMINS about the payment cancellation
            admin_message = f"❌ Payment Cancelled for user ID: {user_id}"
            admin_message += f"User: {latest_attempt['user_name']}\n"
            admin_message += f"Bot: {selected_db.capitalize()}"
            
            await client.send_message(chat_id=ADMINS, text=admin_message)

            # Notify the user about the payment cancellation
            user_message = "Your payment Screenshot Not Valid Send Again Valid Payment Screenshot..."
            await client.edit_message_media(
                query.message.chat.id,
                query.message.id,
                InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(text=user_message)

