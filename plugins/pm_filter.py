7# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import random
import logging
lock = asyncio.Lock()
from datetime import date, datetime
import datetime
import pytz
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid

from info import (
    ADMINS, PICS, MSG_ALRT
)
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.gfilters_mdb import find_gfilter, get_gfilters, del_allg

from Script import script
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, send_all, check_verification, get_token

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@Client.on_message(filters.photo & filters.private)
async def payment_screenshot_received(client, message):
    user = message.from_user.username  # Get the username of the user
    
    # Send message to user and admin about payment screenshot received
    if user:
        user_notification = "Payment screenshot received. ADMINS will check the payment."
        admin_notification = f"{user}'s payment screenshot has been received. Checking the payment..."
        await message.reply_text(user_notification)
        await client.send_message("ADMINS", admin_notification)
    else:
        # If user sends anything other than a photo
        await message.reply_text("Process cancelled!")
        await message.reply_text("Process cancelled!")
        await client.send_message("ADMINS", "Process cancelled for user who tried to buy premium plan.")
        

@Client.on_callback_query(filters.regex("upgrade_silver|upgrade_gold|upgrade_diamond|upgrade_platinum"))
async def upgrade_callback(client, callback_query):
    plan_type = callback_query.data.split('_')[1] # Extract 'silver' or 'gold'

    prices = []
    duration = "1 Month" if "1_month" in callback_data_parts[1] else "2 Months"

    # Determine plan amount based on plan_type and duration
    if duration == "1 Month":
        if plan_type == "silver":
            plan_amount = "39 ₹"
        elif plan_type == "gold":
            plan_amount = "60 ₹"
        elif plan_type == "diamond":
            plan_amount = "99 ₹"
        elif plan_type == "platinum":
            plan_amount = "199 ₹"
    else:  # 2 Months
        if plan_type == "silver":
            plan_amount = "69 ₹"
        elif plan_type == "gold":
            plan_amount = "109 ₹"
        elif plan_type == "diamond":
            plan_amount = "179 ₹"
        elif plan_type == "platinum":
            plan_amount = "369 ₹"

    # Calculate the validity date (30 days from today for 1-month plan, 60 days for 2-month plan)
    days_validity = 30 if "1_month" in callback_query.data else 60
    validity_date = datetime.datetime.now() + datetime.timedelta(days=days_validity)
    validity_formatted = validity_date.strftime("%B %d, %Y")

    payment_message = f"**Payment Process**\n\n"
    payment_message += f"* Plan: {plan_type.capitalize()} Plan\n"
    payment_message += f"* Duration: {duration}\n"
    payment_message += f"* Amount: {plan_amount}\n"
    payment_message += f"* Validity till: {validity_formatted}"

    # Update the buttons based on the chosen plan type and duration
    upgrade_buttons = []
    if plan_type == "silver" and duration == "1 Month":
        upgrade_buttons.append(
            [InlineKeyboardButton("Upgrade Now (39 ₹)", callback_data="upgrade_1_month_silver_now")]
        )
    elif plan_type == "silver" and duration == "2 Months":
        upgrade_buttons.append(
            [InlineKeyboardButton("Upgrade Now (69 ₹)", callback_data="upgrade_2_months_silver_now")]
        )
    elif plan_type == "gold" and duration == "1 Month":
        upgrade_buttons.append(
            [InlineKeyboardButton("Upgrade Now (60 ₹)", callback_data="upgrade_1_month_gold_now")]
        )
    elif plan_type == "gold" and duration == "2 Months":
        upgrade_buttons.append(
            [InlineKeyboardButton("Upgrade Now (109 ₹)", callback_data="upgrade_2_months_gold_now")]
        )
    elif plan_type == "diamond" and duration == "1 Month":
        upgrade_buttons.append(
            [InlineKeyboardButton("Upgrade Now (99 ₹)", callback_data="upgrade_1_month_diamond_now")]
        )
    elif plan_type == "diamond" and duration == "2 Months":
        upgrade_buttons.append(
            [InlineKeyboardButton("Upgrade Now (179 ₹)", callback_data="upgrade_2_months_diamond_now")]
        )
    elif plan_type == "platinum" and duration == "1 Month":
        upgrade_buttons.append(
            [InlineKeyboardButton("Upgrade Now (199 ₹)", callback_data="upgrade_1_month_platinum_now")]
        )
    elif plan_type == "platinum" and duration == "2 Months":
        upgrade_buttons.append(
            [InlineKeyboardButton("Upgrade Now (369 ₹)", callback_data="upgrade_2_months_platinum_now")]
        )
    else:
        upgrade_buttons = []

    # Additional buttons for back and cancel
    upgrade_buttons.append([InlineKeyboardButton("Back", callback_data="back")]


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    is_admin = query.from_user.id in ADMINS
    if query.data == "close_data":
        await query.message.delete()

    
    elif query.data == "premium_plans":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
        await query.answer()
        await query.message.edit_text(text=plans_message, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Silver Plan", callback_data="silver_plan"),
                    InlineKeyboardButton("Gold Plan", callback_data="gold_plan"),
                ],
                [
                    InlineKeyboardButton("Diamond Plan", callback_data="diamond_plan"),
                    InlineKeyboardButton("Platinum Plan", callback_data="platinum_plan"),
                ]
            ]
        )
    )
    
    elif query.data == "silver_plan":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
        await query.answer()
        await query.message.edit_text(text=plans_message, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Upgrade To Silver", callback_data="upgrade_silver"),
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="cancel_plan")
                ]
            ]
        )
    )
    
    elif query.data == "gold_plan":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
        await query.answer()
        await query.message.edit_text(text=plans_message, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Upgrade To Gold", callback_data="upgrade_gold"),
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="cancel_plan")
                ]
            ]
        )
    )
    
    elif query.data == "diamond_plan":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
        await query.answer()
        await query.message.edit_text(text=plans_message, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Upgrade To Diamond", callback_data="upgrade_diamond"),
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="cancel_plan")
                ]
            ]
        )
    )
    elif query.data == "platinum_plan":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
        await query.answer()
        await query.message.edit_text(text=plans_message, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Upgrade To Platinum", callback_data="upgrade_platinum"),
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="cancel_plan")
                ]
            ]
        )
    )
    
    
    elif query.data == "confirmed_payment":
        user = callback_query.from_user.username  # Get the username of the user
        
        # Send confirmation message to the user
        confirmation_message = "Confirm Payment\n\nSend here your successful payment screenshot."
        await query.answer()
        await query.message.edit_text(text=confirmation_message)
    
        # Notify user to send payment screenshot
        user_notification = "Please send your payment screenshot now."
        await client.send_message(user, user_notification)
        
    
    elif query.data == "start":
        if is_admin:
            admin_buttons = [
                [
                    InlineKeyboardButton('➕ Add Me To Your Group ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],
                [
                    InlineKeyboardButton('🔒 Admin Settings', callback_data='admin_settings')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(admin_buttons)
            tz = pytz.timezone('Asia/Kolkata')
            now = datetime.now(tz)
            current_time = now.strftime('%Y-%m-%d %I:%M:%S %p')  # Update time to show date and time
            caption = script.ADMIN_START_TXT.format(
                admin=query.from_user.mention,
                bot=temp.B_LINK,
                total_users=await db.total_users_count(),
                total_chat=await db.total_chat_count(),
                daily_users=await db.daily_users_count(datetime.now().date()),
                daily_chats=await db.daily_chats_count(datetime.now().date()),
                current_time=current_time
            )
        else:
            regular_buttons = [
                [
                    InlineKeyboardButton('Premium List', callback_data="list"),
                    InlineKeyboardButton("Premium Plans", callback_data="premium_plans")
                ],
                [
                    InlineKeyboardButton('Bots Premium', callback_data="bots"),
                    InlineKeyboardButton('Database Premium', callback_data="database")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(regular_buttons)
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
        await query.answer(MSG_ALRT)

    
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
            text=script.ALL_FILTERS.format(query.from_user.mention),
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
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "list":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='filters')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "mbot":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buym'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "abot":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buya'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rbot":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buyr'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "yibot":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buyyi'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "mdb":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buymdb'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "adb":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buyadb'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tvsdb":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buytvsdb'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    
