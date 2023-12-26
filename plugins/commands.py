import os
import logging
import random
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS
from utils import is_subscribed, temp
from datetime import date, datetime 
from Script import script
import pytz

logger = logging.getLogger(__name__)

PREMIUM_PRICE = 99

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

@Client.on_message(filters.command('total_users') & filters.user(ADMINS))
async def total_users(client, message):
    total_users = await db.total_users_count()
    total_attempts = await db.attempts_col.count_documents({})
    total_cancel_attempts =  await db.total_cancel_count()
    total_premium_users = await db.pre.count_documents({})

    # Calculate total earnings
    total_earnings = total_premium_users * PREMIUM_PRICE

    reply_text = (
        f"Total Users: {total_users}\n"
        f"Total Attempts: {total_attempts}\n"
        f"Total Cancel Attempts: {total_cancel_attempts}\n"
        f"Total Premium Users: {total_premium_users}\n"
        f"Total Earnings: {total_earnings} Rupees\n"
    )

    await message.reply_text(reply_text)

@Client.on_message(filters.command('botstats') & filters.user(ADMINS))
async def bot_stats(client, message):
    total_mbot_premium_users = await db.pre.count_documents({'selected_bot': 'mbot'})
    total_mbot_earnings = total_mbot_premium_users * PREMIUM_PRICE

    total_abot_premium_users = await db.pre.count_documents({'selected_bot': 'abot'})
    total_abot_earnings = total_abot_premium_users * PREMIUM_PRICE

    total_rbot_premium_users = await db.pre.count_documents({'selected_bot': 'rbot'})
    total_rbot_earnings = total_rbot_premium_users * PREMIUM_PRICE

    total_ytbot_premium_users = await db.pre.count_documents({'selected_bot': 'ytbot'})
    total_ytbot_earnings = total_ytbot_premium_users * PREMIUM_PRICE

    reply_text = (
        f"Total Mbot Premium Users: {total_mbot_premium_users}\n"
        f"Total Mbot Earnings: {total_mbot_earnings} Rupees\n\n"
        
        f"Total Abot Premium Users: {total_abot_premium_users}\n"
        f"Total Abot Earnings: {total_abot_earnings} Rupees\n\n"

        f"Total Rbot Premium Users: {total_rbot_premium_users}\n"
        f"Total Rbot Earnings: {total_rbot_earnings} Rupees\n\n"

        f"Total Ytbot Premium Users: {total_ytbot_premium_users}\n"
        f"Total Ytbot Earnings: {total_ytbot_earnings} Rupees\n"
    )

    await message.reply_text(reply_text)

@Client.on_message(filters.command("user_info") & filters.user(ADMINS))
async def user_info_cmd(client, message):
    if len(message.command) != 2:
        await message.reply_text("<b>Use this command as follows: /user_info user_id</b>")
        return

    user_id = int(message.command[1])

    user_data = await db.get_verified(user_id)
    ban_status = await db.get_ban_status(user_id)
    latest_attempt_bot = await db.get_latest_attempt_dot(user_id)
    latest_attempt_db = await db.get_latest_attempt_db(user_id)
    premium_bot = await db.pre.find_one({'user_id': user_id})
    premium_db = await db.pre.find_one({'user_id': user_id})
    
    if not user_data:
        await message.reply_text("<b>User not found in the database.</b>")
        return

    user_info_text = (
        f"<b>User ID:</b> {user_data['id']}\n"
        f"<b>User Name:</b> {user_data['name']}\n\n"
        f"<b>Verification Status:</b>\n"
        f"Date: {user_data['verification_status']['date']}\n"
        f"Time: {user_data['verification_status']['time']}\n\n"
        f"<b>Ban Status:</b> {ban_status['is_banned']} ({ban_status['ban_reason']})\n\n"
    )

    if latest_attempt_bot:
        user_info_text += (
            f"<b>Latest Attempt:</b>\n"
            f"Bot: {latest_attempt['selected_bot']}\n"
            f"Attempt Number: {latest_attempt['attempt_number']}\n"
            f"Date Time: {latest_attempt['current_date_time']}\n"
            f"Validity Date: {latest_attempt['validity_date']}\n\n"
        )

    if latest_attempt_db:
        user_info_text += (
            f"<b>Latest Attempt:</b>\n"
            f"Database: {latest_attempt['selected_db']}\n"
            f"Attempt Number: {latest_attempt['attempt_number']}\n"
            f"Date Time: {latest_attempt['current_date_time']}\n"
            f"Validity Date: {latest_attempt['validity_date']}\n\n"
        )
        
    if premium_info:
        user_info_text += (
            f"<b>Premium Info:</b>\n"
            f"Bot: {premium_info['selected_bot']}\n"
            f"Validity Months: {premium_info['validity_months']}\n"
            f"Expiry Date: {premium_info['expiry_date']}\n\n"
        )

    await message.reply_text(user_info_text, parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("myplan"))
async def my_plan(client, message):
    user_id = message.from_user.id

    user_data = await db.get_verified(user_id)
    ban_status = await db.get_ban_status(user_id)
    latest_attempt_bot = await db.get_latest_attempt_dot(user_id)
    latest_attempt_db = await db.get_latest_attempt_db(user_id)
    premium_info = await db.pre.find_one({'user_id': user_id})

    if not user_data:
        await message.reply_text("<b>User not found in the database.</b>")
        return

    user_info_text = (
        f"<b>Your Info:</b>\n"
        f"Verification Status: {user_data['verification_status']['date']} {user_data['verification_status']['time']}\n"
        f"Ban Status: {ban_status['is_banned']} ({ban_status['ban_reason']})\n\n"
    )

    if latest_attempt_bot:
        user_info_text += (
            f"Latest Attempt:\n"
            f"Bot: {latest_attempt['selected_bot']}\n"
            f"Attempt Number: {latest_attempt['attempt_number']}\n"
            f"Date Time: {latest_attempt['current_date_time']}\n"
            f"Validity Date: {latest_attempt['validity_date']}\n\n"
        )

    if latest_attempt_db:
        user_info_text += (
            f"Latest Attempt:\n"
            f"Bot: {latest_attempt['selected_bot']}\n"
            f"Attempt Number: {latest_attempt['attempt_number']}\n"
            f"Date Time: {latest_attempt['current_date_time']}\n"
            f"Validity Date: {latest_attempt['validity_date']}\n\n"
        )
        
    if premium_info:
        user_info_text += (
            f"Premium Info:\n"
            f"Bot: {premium_info['selected_bot']}\n"
            f"Validity Months: {premium_info['validity_months']}\n"
            f"Expiry Date: {premium_info['expiry_date']}\n\n"
        )

    await message.reply_text(user_info_text, parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Users Saved In DB Are:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Your message has been successfully sent to {user.mention}.</b>")
            else:
                await message.reply_text("<b>This user didn't start this bot yet!</b>")
        except Exception as e:
            await message.reply_text(f"<b>Error: {e}</b>")
    else:
        await message.reply_text("<b>Use this command as a reply to any message using the target chat ID. For example: /send user_id</b>")
