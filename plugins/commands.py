import os
import logging
import random
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, PREMIUM_PRICE
from utils import is_subscribed, temp
from datetime import date, datetime 
from Script import script
import pytz

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('Bots Premium', callback_data="bots"),
                InlineKeyboardButton('Database Premium', callback_data="database")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await asyncio.sleep(2) 
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(a=message.chat.title, b=message.chat.id, c=message.chat.username, d=total, f=client.mention, e="Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title, message.chat.username)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention, message.from_user.username, temp.U_NAME))
    if len(message.command) != 2:
        buttons = [
            [
                InlineKeyboardButton('Bots Premium', callback_data="bots"),
                InlineKeyboardButton('Database Premium', callback_data="database")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(user=message.from_user.mention, bot=temp.B_LINK),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            quote=True
        )
        return

    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        btn = [[InlineKeyboardButton("❆ Join Our Back-Up Channel ❆", url=invite_link.invite_link)]]

        await client.send_message(
            chat_id=message.from_user.id,
            text=f"**Hello {message.from_user.mention}, Due to overload only my channel subscribers can use me.\n\nPlease join my channel and then start me again!...**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True
        )
        return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [
            [
                InlineKeyboardButton('Bots Premium', callback_data="bots"),
                InlineKeyboardButton('Database Premium', callback_data="database")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(user=message.from_user.mention, bot=temp.B_LINK),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            quote=True
        )

@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('total'))
async def total_users(bot, message):
    try:
        total_users = await db.total_users_count()
        total_attempts = await db.total_attempts()
        total_confirms = await db.total_confirm()
        total_premiums = await db.total_premium()

        response = f"Total Users: {total_users}\nTotal Attempts: {total_attempts}\nTotal Confirms: {total_confirms}\nTotal Premiums: {total_premiums}"

        # For specific bot data
        bot_names = []  
        for bot_name in bot_names:
            total_attempts_bot = await db.total_attempts(bot_name=bot_name)
            total_confirms_bot = await db.total_confirm(bot_name=bot_name)
            total_premiums_bot = await db.total_premium(bot_name=bot_name)

            response += f"\n\n{bot_name}:\nTotal Attempts: {total_attempts_bot}\nTotal Confirms: {total_confirms_bot}\nTotal Premiums: {total_premiums_bot}"

        await message.reply_text(response)

    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command("monthly_attempts"))
async def monthly_attempts_command(client, message):
    monthly_attempts = await db.get_this_month_attempts()
    await message.reply(f"Monthly attempts: {monthly_attempts}")

@Client.on_message(filters.command("today_attempts"))
async def today_attempts_command(client, message):
    today_attempts = await db.get_today_attempts()
    await message.reply(f"Attempts for today: {today_attempts}")

@Client.on_message(filters.command("user_attempts"))
async def user_attempts_command(client, message):
    user_id = message.from_user.id
    user_attempts = await db.get_user_attempts(user_id)
    
    if user_attempts:
        response = "Your attempts:\n"
        for attempt in user_attempts:
            response += (
                f"Bot: {attempt.get('bot_name', 'N/A')},"
                f"Date: {attempt['date']} {attempt['time']},"
                f"Validity: {attempt['validity']}\n"
            )
    else:
        response = "You have no attempts yet."

    

