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

@Client.on_message(filters.command("total_attempts"))
async def total_attempts(client, message):
    try:
        monthly_total = await db.get_monthly_attempts_dot()
        daily_total = await db.get_daily_attempts_dot()
        all_time_total = await db.get_total_attempts_dot()

        # Get data for specific bots if mentioned
        bot_names = message.command[1:]
        if bot_names:
            bot_data = []
            for bot_name in bot_names:
                bot_monthly = await db.get_monthly_attempts_dot(bot_name)
                bot_daily = await db.get_daily_attempts_dot(bot_name)
                bot_all_time = await db.get_total_attempts_dot(bot_name)
                bot_data.append(
                    f"**{bot_name.capitalize()}:**\n"
                    f"  - Monthly: {bot_monthly}\n"
                    f"  - Daily: {bot_daily}\n"
                    f"  - All Time: {bot_all_time}\n"
                )

            response = "\n".join(bot_data)
        else:
            response = (
                f"**Subscription Data:**\n"
                f"  - Monthly Total: {monthly_total}\n"
                f"  - Daily Total: {daily_total}\n"
                f"  - All Time Total: {all_time_total}"
            )

        await message.reply_text(response)
    except Exception as e:
        logger.error(f"Error fetching subscription data: {e}")
        await message.reply_text("An error occurred while retrieving subscription data. Please try again later.")


@Client.on_message(filters.command("get_attempts"))
async def get_attempts_data(client, message):
    try:
        # Check if the command has a specified bot name
        if len(message.command) > 1:
            selected_bot = message.command[1]
            total_attempts = await db.get_total_attempts_dot(selected_bot=selected_bot)
            response_text = f"Total attempts for {selected_bot}: {total_attempts}"
        else:
            # If no bot name specified, get total attempts for all bots
            total_attempts = await db.get_total_attempts_dot()
            response_text = f"Total attempts for all bots: {total_attempts}"

        await message.reply_text(response_text)

    except Exception as e:
        print(f"An error occurred: {e}")
        await message.reply_text("An error occurred while processing the command.")

@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total_users(client, message):
    total_users_count = await db.total_users_count()
    total_attempts_bot = await db.get_total_attempts_dot()
    total_cancel_bot = await db.get_total_cancels_dot()
    total_premium_users_bot = await db.get_total_premium_dot()
    total_earnings_bot = await db.get_total_earnings_dot()

    total_attempts_db = await db.get_total_attempts_db()
    total_cancel_db = await db.get_total_cancels_db()
    total_premium_users_db = await db.get_total_premium_db()
    total_earnings_db = await db.get_total_earnings_db()

    reply_text = (
        f"#TOTAL_STATS\n\n"
        f"Total Bot Stats\n"
        f"Total Users: {total_users_count}\n"
        f"Total Attempts (Bot): {total_attempts_bot}\n"
        f"Total Cancel (Bot): {total_cancel_bot}\n"
        f"Total Premium Users (Bot): {total_premium_users_bot}\n"
        f"Total Earnings From (Bot): {total_earnings_bot} Rupees\n\n"
        f"Total DB Stats\n"
        f"Total Attempts (DB): {total_attempts_db}\n"
        f"Total Cancel (DB): {total_cancel_db}\n"
        f"Total Premium Users (DB): {total_premium_users_db}\n"
        f"Total Earnings From (DB): {total_earnings_db} Rupees"
    )

    await message.reply_text(reply_text)

@Client.on_message(filters.command("user_id") & filters.user(ADMINS))
async def user_info(client, message):
    user_id = message.from_user.id

    # Check if the sender is an admin
    if user_id not in ADMINS:
        await message.reply_text("You are not authorized to use this command.")
        return

    # Get user information
    user_info = await db.get_verified(user_id)
    ban_status = await db.get_ban_status(user_id)
    total_bot_premium = await db.get_user_total_premium_dot(user_id)
    total_db_premium = await db.get_user_total_premium_db(user_id)

    # Prepare the response message
    response_message = f"User Information for {user_id}:\n\n"
    
    response_message += f"Verification Status: {user_info['date']} {user_info['time']}\n"
    
    if ban_status['is_banned']:
        response_message += f"Banned: Yes\nReason: {ban_status['ban_reason']}\n"
    else:
        response_message += "Banned: No\n"

    # Display information about bot premium plans
    if total_bot_premium > 0:
        response_message += "\nBot Premium Plans:\n"
        bot_premium_info = await db.get_user_premium_active_dot(user_id)
        for plan in bot_premium_info:
            response_message += f"- Bot: {plan['selected_bot']}, Expires on {plan['expiry_date']}\n"
        response_message += f"Total Bot Premium Plans: {total_bot_premium}\n"
        response_message += "Total Payment User For (Bot):{}\n"

    # Display information about database premium plans
    if total_db_premium > 0:
        response_message += "\nDB Premium Plans:\n"
        db_premium_info = await db.get_user_premium_active_db(user_id)
        for plan in db_premium_info:
            response_message += f"- DB: {plan['selected_db']}, Expires on {plan['expiry_date']}\n"
        response_message += f"Total DB Premium Plans: {total_db_premium}\n"
        response_message += "Total Payment User For (DB):{}\n"

    # Send the response message
    await message.reply_text(response_message)

@Client.on_message(filters.command("user_info") & filters.user(ADMINS))
async def user_info_cmd(client, message):
    if len(message.command) != 2:
        await message.reply_text("<b>Use this command as follows: /user_info user_id</b>", parse_mode="html")
        return

    user_id = int(message.command[1])

    user_data = await db.col.find_one({'id': user_id})
    if not user_data:
        await message.reply_text("<b>User not found in the database.</b>")
        return

    ban_status = await db.get_ban_status(user_id)
    latest_attempt_bot = await db.get_latest_attempt_dot(user_id)
    premium_info_bot = await db.get_user_premium_active_dot(user_id)
    total_payment_bot = await db.get_user_total_payments_dot(user_id)
    
    latest_attempt_db = await db.get_latest_attempt_db(user_id)
    premium_info_db = await db.get_user_premium_active_db(user_id)
    total_payment_db = await db.get_user_total_payments_db(user_id)

    user_info_text = (
        f"<b>User ID:</b> {user_data['id']}\n"
        f"<b>User Name:</b> {user_data['name']}\n\n"
        f"<b>Ban Status:</b> {ban_status['is_banned']} ({ban_status['ban_reason']})\n\n"
    )

    if latest_attempt_bot:
        user_info_text += (
            f"<b>Latest Attempt (Bot):</b>\n"
            f"Bot: {latest_attempt_bot['selected_bot']}\n"
            f"Attempt Number: {latest_attempt_bot['attempt_number']}\n"
            f"Date Time: {latest_attempt_bot['current_date_time']}\n"
            f"Validity Date: {latest_attempt_bot['validity_date']}\n\n"
        )

    if latest_attempt_db:
        user_info_text += (
            f"<b>Latest Attempt (DB):</b>\n"
            f"Database: {latest_attempt_db['selected_db']}\n"
            f"Attempt Number: {latest_attempt_db['attempt_number']}\n"
            f"Date Time: {latest_attempt_db['current_date_time']}\n"
            f"Validity Date: {latest_attempt_db['validity_date']}\n\n"
        )

    if premium_info_bot:
        user_info_text += (
            f"<b>Premium Info (Bot):</b>\n"
            f"Bot: {premium_info_bot['selected_bot']}\n"
            f"Validity Months: {premium_info_bot['validity_months']}\n"
            f"Expiry Date: {premium_info_bot['expiry_date']}\n"
            f"Total Pay For Premium: {total_payment_bot}\n\n"
        )
    
    if premium_info_db:
        user_info_text += (
            f"<b>Premium Info (DB):</b>\n"
            f"Database: {premium_info_db['selected_db']}\n"
            f"Validity Months: {premium_info_db['validity_months']}\n"
            f"Expiry Date: {premium_info_db['expiry_date']}\n"
            f"Total Pay For Premium: {total_payment_db}\n\n"
        )

    await message.reply_text(user_info_text)

@Client.on_message(filters.command("my_plan"))
async def my_plan(client, message):
    user_id = message.from_user.id

    # Get premium plan details for bots
    bot_premium_info = await db.get_user_premium_active_dot(user_id)
    bot_premium_count = await db.get_user_total_premium_dot(user_id)
    bot_total_payments = await db.get_user_total_payments_dot(user_id)

    # Get premium plan details for databases
    db_premium_info = await db.get_user_premium_active_db(user_id)
    db_premium_count = await db.get_user_total_premium_db(user_id)
    db_total_payments = await db.get_user_total_payments_db(user_id)

    # Format the expiry dates
    bot_expiry_dates = [datetime.strftime(plan['expiry_date'], "%Y-%m-%d %H:%M:%S") for plan in bot_premium_info]
    db_expiry_dates = [datetime.strftime(plan['expiry_date'], "%Y-%m-%d %H:%M:%S") for plan in db_premium_info]

    # Prepare the response message
    response_message = f"Your Premium Plans:\n\n"

    if bot_premium_count > 0:
        response_message += "Bot Premium Plans:\n"
        for i in range(bot_premium_count):
            response_message += f"- Plan {i + 1}: Expires on {bot_expiry_dates[i]}\n"
        response_message += f"Total Payments for Bot Premium Plans: {bot_total_payments}\n\n"

    if db_premium_count > 0:
        response_message += "DB Premium Plans:\n"
        for i in range(db_premium_count):
            response_message += f"- Plan {i + 1}: Expires on {db_expiry_dates[i]}\n"
        response_message += f"Total Payments for DB Premium Plans: {db_total_payments}\n\n"

    if bot_premium_count == 0 and db_premium_count == 0:
        response_message += "You don't have any active premium plans."

    # Send the response message
    await message.reply_text(response_message)
