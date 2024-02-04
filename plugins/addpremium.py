import os
from pyrogram import Client, filters
from info import ADMINS, LOG_CHANNEL, PAYMENT_CHAT
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from database.users_chats_db import db

        
async def pre_bot_name(query_data):
    try:
        if query_data == "botm":
            return "Movies Bot"
        elif query_data == "bota":
            return "Anime Bot"
        elif query_data == "botr":
            return "Rename Bot"
        elif query_data == "botv":
            return "YouTube Downloader Bot"
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await bot.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")
        return None

async def pre_db_name(query_data):
    try:
        if query_data == "dbm":
            return "Movies Database"
        elif query_data == "dba":
            return "Anime Database"
        elif query_data == "dbab":
            return "Audio Book Database"
        elif query_data == "dbtv":
            return "TV Series Database"
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await bot.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")
        return None

async def premium_validity(query_data):
    try:
        today_date = datetime.now()
        if query_data == "1bm" or query_data == "1dbm":
            pre_validity = today_date + timedelta(days=30)
            pre_month = "1 Month"
        elif query_data == "2bm" or query_data == "2dbm":
            pre_validity = today_date + timedelta(days=60)
            pre_month = "2 Months"
        elif query_data == "3bm" or query_data == "3dbm":
            pre_validity = today_date + timedelta(days=90)
            pre_month = "3 Months"
        return pre_validity.strftime("%Y-%m-%d %H:%M:%S"), pre_month
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await bot.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")
        return None, None

async def payment_command(query_data, client, user_id):
    try:
        if query_data == "botm":
            await client.send_message(PAYMENT_CHAT, f"/add {user_id}")
        elif query_data == "bota":
            await client.send_message(PAYMENT_CHAT, f"/pre {user_id}")
        elif query_data == "botr":
            await client.send_message(PAYMENT_CHAT, f"/try {user_id}")
        elif query_data == "bottv":
            await client.send_message(PAYMENT_CHAT, f"/pro {user_id}")
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await bot.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

    
@Client.on_message(filters.private & filters.command("addpremium") & filters.user(ADMINS))
async def addpremium(bot, message):
    try:
        if message.from_user.id in ADMINS:
            command_args = message.command[1:]  # Extract arguments after the command
            if command_args:
                user_id = command_args[0]
                buttons = [
                    [
                        InlineKeyboardButton("Premium Bots", callback_data=f"bot_{user_id}"),
                        InlineKeyboardButton("Premium Database", callback_data=f"db_{user_id}")
                    ],
                    [
                        InlineKeyboardButton("Cancel", callback_data=f"cp_{user_id}")
                    ]
                ]
                await message.reply_text(
                    text="Select Premium Plan Type..",
                    reply_markup=InlineKeyboardMarkup(buttons),
                    quote=True
                )
            else:
                await message.reply_text("To add a premium user, use the following command:\n\n/addpremium {userid}")
        else:
            await message.reply_text("You are not authorized to use this command.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
        await bot.send_message(LOG_CHANNEL, f"Error in add_premium: {e}")

@Client.on_callback_query(filters.regex('bot_'))
async def premium_bots(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        buttons = [
            [
                InlineKeyboardButton("Movies Bot", callback_data=f"botm_{user_id}"),
                InlineKeyboardButton("Anime Bot", callback_data=f"bota_{user_id}")
            ],
            [
                InlineKeyboardButton("Rename Bot", callback_data=f"botr_{user_id}"),
                InlineKeyboardButton("TV Series Bot", callback_data=f"botv_{user_id}")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data=f"cp_{user_id}")
            ]
        ]
        await callback_query.edit_message_text(
            text="Select Premium Bot:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await client.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

@Client.on_callback_query(filters.regex('db_'))
async def premium_database(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        buttons = [
            [
                InlineKeyboardButton("Movies Database", callback_data=f"dbm_{user_id}"),
                InlineKeyboardButton("Anime Database", callback_data=f"dba_{user_id}")
            ],
            [
                InlineKeyboardButton("Audio Book Database", callback_data=f"dbab_{user_id}"),
                InlineKeyboardButton("TV Series Database", callback_data=f"dbtv_{user_id}")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data=f"cp_{user_id}")
            ]
        ]
        await callback_query.edit_message_text(
            text="Select Premium Database:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await client.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

@Client.on_callback_query(filters.regex('botm_|bota_|botr_|bottv_'))
async def premium_bot_durations(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        buttons = [
            [
                InlineKeyboardButton("1 Month", callback_data=f"1bm_{user_id}"),
                InlineKeyboardButton("2 Months", callback_data=f"2bm_{user_id}"),
            ],
            [
                InlineKeyboardButton("3 Months", callback_data=f"3bm_{user_id}"),
                InlineKeyboardButton("Cancel", callback_data=f"cp_{user_id}")
            ]
        ]
        await callback_query.edit_message_text(
            text="Select Premium Plan Duration:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await client.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

@Client.on_callback_query(filters.regex('dbm_|dba_|dbab_|dbtb_'))
async def premium_database_durations(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        buttons = [
            [
                InlineKeyboardButton("1 Month", callback_data=f"1dbm_{user_id}"),
                InlineKeyboardButton("2 Months", callback_data=f"2dbm_{user_id}"),
            ],
            [
                InlineKeyboardButton("3 Months", callback_data=f"3dbm_{user_id}"),
                InlineKeyboardButton("Cancel", callback_data=f"cp_{user_id}")
            ]
        ]
        await callback_query.edit_message_text(
            text="Select Premium Plan Duration:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await client.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

@Client.on_callback_query(filters.regex('1bm_|2bm_|3bm_'))
async def premium_bot_receipt(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        username = callback_query.from_user.username
        bot_name = await pre_bot_name(callback_query.data)
        pre_validity, pre_month = await premium_validity(callback_query.data)

        receipt_message = (
            f"Premium Receipt\n\n"
            f"User id = {user_id}\n"
            f"Username = {username}\n"
            f"Premium Bot = {bot_name}\n"
            f"Premium Duration = {pre_month}\n"
            f"Premium Validity = {pre_validity}"
        )

        buttons = [
            [
                InlineKeyboardButton("Add Premium", callback_data=f"adb_{user_id}"),
                InlineKeyboardButton("Cancel Premium", callback_data=f"cp_{user_id}")
            ]
        ]

        await callback_query.edit_message_text(
            text=receipt_message,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await client.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

@Client.on_callback_query(filters.regex('1dbm_|2dbm_|3dbm_'))
async def premium_db_receipt(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        username = callback_query.from_user.username
        database_name = await pre_db_name(callback_query.data)
        pre_validity, pre_month = await premium_validity(callback_query.data)

        receipt_message = (
            f"Premium Receipt\n\n"
            f"User id = {user_id}\n"
            f"Username = {username}\n\n"
            f"Premium Database = {database_name}\n"
            f"Premium Duration = {pre_month}\n"
            f"Premium Validity = {pre_validity}"
        )

        buttons = [
            [
                InlineKeyboardButton("Add Premium", callback_data=f"addb_{user_id}"),
                InlineKeyboardButton("Cancel Premium", callback_data=f"cp_{user_id}")
            ]
        ]

        await callback_query.edit_message_text(
            text=receipt_message,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await client.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

@Client.on_callback_query(filters.regex('adb_'))
async def confirm_bot_premium(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        username = callback_query.from_user.username
        bot_name = await pre_bot_name(callback_query.data)
        pre_validity, pre_month = await premium_validity(callback_query.data)

        await payment_command(callback_query.data, client, user_id)

        db.add_premium(id=user_id, bot_name=bot_name, file_id=None, premium_date=datetime.now(), premium_validity=pre_validity)

        confirmation_message = (
            f"Successfully Added {username} as Premium For {pre_month} in {bot_name}\n"
            f"Plan Expires on {pre_validity}"
        )

        await callback_query.edit_message_text(
            text=confirmation_message
        )

        user_message = (
            f"Hey {username},\n"
            f"You are now a Premium User! in {bot_name}\n"
            f"Added you to Premium Users for {pre_month}.\n"
            f"Your plan will expire on {pre_validity}."
        )

        await client.send_message(user_id, user_message)
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await client.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

@Client.on_callback_query(filters.regex('addb_'))
async def confirm_db_premium(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        username = callback_query.from_user.username
        db_name = await pre_bot_name(callback_query.data)
        pre_validity, pre_month = await premium_validity(callback_query.data)

        db.add_premium(id=user_id, db_name=db_name, file_id=None, premium_date=datetime.now(), premium_validity=pre_validity)

        confirmation_message = (
            f"Successfully Added {username} as Premium For {pre_month} in {db_name}\n"
            f"Plan Expires on {pre_validity}"
        )

        await callback_query.edit_message_text(
            text=confirmation_message
        )

        user_message = (
            f"Hey {username},\n"
            f"You are now a Premium User! in {db_name}\n"
            f"Added you to Premium Users for {pre_month}.\n"
            f"Your plan will expire on {pre_validity}."
        )

        await client.send_message(user_id, user_message)
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        await client.send_message(LOG_CHANNEL, f"Error in premium_bots: {e}")

@Client.on_callback_query(filters.regex('cp_'))
async def premium_cancel(client, callback_query):
    await callback_query.edit_message_text(
            text="Cancel Premium"
        )
        
