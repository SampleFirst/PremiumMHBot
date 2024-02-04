import os
from pyrogram import Client, filters
from info import ADMINS, LOG_CHANNEL, PAYMENT_CHAT
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from database.users_chats_db import db

async def pre_bot_name(query_data):
    try:
        if query_data == "pre1_m":
            return "Movies Bot"
        elif query_data == "pre1_a":
            return "Anime Bot"
        elif query_data == "pre1_r":
            return "Rename Bot"
        elif query_data == "pre1_tv":
            return "YouTube Downloader Bot"
    except Exception as e:
        print(f"Error in pre_bot_name: {e}")
        return None

async def pre_db_name(query_data):
    try:
        if query_data == "pre2_md":
            return "Movies Database"
        elif query_data == "pre2_ad":
            return "Anime Database"
        elif query_data == "pre2_abd":
            return "Audio Book Database"
        elif query_data == "pre2_tvd":
            return "Tv Series Database"
    except Exception as e:
        print(f"Error in pre_db_name: {e}")
        return None

async def premium_validity(query_data):
    try:
        today_date = datetime.now()
        if query_data == "pre1_1" or query_data == "pre2_1":
            pre_validity = today_date + timedelta(days=30)
            pre_month = "1 Month"
        elif query_data == "pre1_2" or query_data == "pre2_2":
            pre_validity = today_date + timedelta(days=60)
            pre_month = "2 Months"
        elif query_data == "pre1_3" or query_data == "pre2_3":
            pre_validity = today_date + timedelta(days=90)
            pre_month = "3 Months"
        return pre_validity.strftime("%Y-%m-%d %H:%M:%S"), pre_month
    except Exception as e:
        print(f"Error in premium_validity: {e}")
        return None, None

async def payment_command(query_data, client, user_id):
    try:
        if query_data == "pre1_m":
            await client.send_message(PAYMENT_CHAT, f"/add {user_id}")
        elif query_data == "pre1_a":
            await client.send_message(PAYMENT_CHAT, f"/pre {user_id}")
        elif query_data == "pre1_r":
            await client.send_message(PAYMENT_CHAT, f"/try {user_id}")
        elif query_data == "pre1_tv":
            await client.send_message(PAYMENT_CHAT, f"/pro {user_id}")
    except Exception as e:
        print(f"Error in payment_command: {e}")



@Client.on_message(filters.private & filters.command("addpremium") & filters.user(ADMINS))
async def addpremium(bot, message):
    try:
        if message.from_user.id in ADMINS:
            command_args = message.command[1:]
            if command_args:
                user_id = command_args[0]
                buttons = [
                    [
                        InlineKeyboardButton("Premium Bots", callback_data=f"pre1|{user_id}"),
                        InlineKeyboardButton("Premium Database", callback_data=f"pre2|{user_id}")
                    ],
                    [
                        InlineKeyboardButton("Cancel", callback_data=f"cancel_premium|{user_id}")
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
        print(f"Error in addpremium: {e}")

@Client.on_callback_query(filters.regex(r'^pre1\|\d+$'))
async def premium_bots(client, callback_query):
    try: 
        user_id = int(callback_query.data.split("|")[1])
        buttons = [
            [
                InlineKeyboardButton("Movies Bot", callback_data=f"pre1_m|{user_id}"),
                InlineKeyboardButton("Anime Bot", callback_data=f"pre1_a|{user_id}")
            ],
            [
                InlineKeyboardButton("Rename Bot", callback_data=f"pre1_r|{user_id}"),
                InlineKeyboardButton("TV Series Bot", callback_data=f"pre1_tv|{user_id}")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data=f"cancel_premium|{user_id}")
            ]
        ]
        await callback_query.edit_message_text(
            text="Select Premium Bot:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    except Exception as e:
        print(f"Error in premium bots: {e}")

@Client.on_callback_query(filters.regex(r'^pre2\|\d+$'))
async def premium_database(client, callback_query):
    try:
        user_id = int(callback_query.data.split("|")[1])
        buttons = [
            [
                InlineKeyboardButton("Movies Database", callback_data=f"pre2_md|{user_id}"),
                InlineKeyboardButton("Anime Database", callback_data=f"pre2_ad|{user_id}")
            ],
            [
                InlineKeyboardButton("Audio Book Database", callback_data=f"pre2_abd|{user_id}"),
                InlineKeyboardButton("TV Series Database", callback_data=f"pre2_tvd|{user_id}")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data=f"cancel_premium|{user_id}")
            ]
        ]
        await callback_query.edit_message_text(
            text="Select Premium Database:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    except Exception as e:
        print(f"Error in premium database: {e}")

@Client.on_callback_query(filters.regex('pre1_m_|pre1_a_|pre1_r_|pre1_tv_'))
async def premium_bot_durations(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        buttons = [
            [
                InlineKeyboardButton("1 Month", callback_data="pre1_1_{user_id}"),
                InlineKeyboardButton("2 Months", callback_data="pre1_2_{user_id}"),
            ],
            [
                InlineKeyboardButton("3 Months", callback_data="pre1_3_{user_id}"),
                InlineKeyboardButton("Cancel", callback_data="cancel_premium_{user_id}")
            ]
        ]
        await callback_query.edit_message_text(
            text="Select Premium Plan Duration:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    except Exception as e:
        print(f"Error in premium bot month: {e}")
        
@Client.on_callback_query(filters.regex('pre2_md_|pre2_ad_|pre2_abd_|pre2_tvd_'))
async def premium_database_durations(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        buttons = [
            [
                InlineKeyboardButton("1 Month", callback_data="pre2_1_{user_id}"),
                InlineKeyboardButton("2 Months", callback_data="pre2_2_{user_id}"),
            ],
            [
                InlineKeyboardButton("3 Months", callback_data="pre2_3_{user_id}"),
                InlineKeyboardButton("Cancel", callback_data="cancel_premium_{user_id}")
            ]
        ]
        await callback_query.edit_message_text(
            text="Select Premium Plan Duration:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    except Exception as e:
        print(f"Error in premium database month: {e}")
        
@Client.on_callback_query(filters.regex('pre1_1_|pre1_2_|pre1_3_'))
async def premium_bot_receipt(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        username = callback_query.from_user.username
        bot_name = pre_bot_name(callback_query.data)
        pre_validity, pre_month = premium_validity(callback_query.data)
    
        receipt_message = (
            f"Premium Receipt\n\n"
            f"User id = {user_id}\n"
            f"Username = {username}\n"
            f"Premium Bot = {bot_name}\n"
            f"Premium Duration = {pre_month}\n"
            f"Premium Validity = {pre_validity}"
        )
    
        # Add Premium and Cancel Premium buttons
        buttons = [
            [
                InlineKeyboardButton("Add Premium", callback_data="bot_premium_{user_id}"),
                InlineKeyboardButton("Cancel Premium", callback_data="cancel_premium_{user_id}")
            ]
        ]
    
        await callback_query.edit_message_text(
            text=receipt_message,
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    except Exception as e:
        print(f"Error in premium bot month: {e}")
        
@Client.on_callback_query(filters.regex('pre2_1_|pre2_2_|pre2_3_'))
async def premium_bot_receipt(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        username = callback_query.from_user.username
        database_name = pre_db_name(callback_query.data)
        pre_validity, pre_month = premium_validity(callback_query.data)
    
        receipt_message = (
            f"Premium Receipt\n\n"
            f"User id = {user_id}\n"
            f"Username = {username}\n\n"
            f"Premium Database = {database_name}\n"
            f"Premium Duration = {pre_month}\n"
            f"Premium Validity = {pre_validity}"
        )
    
        # Add Premium and Cancel Premium buttons
        buttons = [
            [
                InlineKeyboardButton("Add Premium", callback_data="db_premium_{user_id}"),
                InlineKeyboardButton("Cancel Premium", callback_data="cancel_premium_{user_id}")
            ]
        ]
    
        await callback_query.edit_message_text(
            text=receipt_message,
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    except Exception as e:
        print(f"Error in premium database month: {e}")
        
@Client.on_callback_query(filters.regex('bot_premium_'))
async def confirm_bot_premium(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        username = callback_query.from_user.username
        bot_name = await pre_bot_name(callback_query.data)
        pre_validity, pre_month = await premium_validity(callback_query.data)

        # Execute payment command
        await payment_command(callback_query.data, client, user_id)

        # Add premium data to the database
        db.add_premium(id=user_id, bot_name=bot_name, file_id=None, premium_date=datetime.now(), premium_validity=pre_validity)

        # Send confirmation message to the user
        confirmation_message = (
            f"Successfully Added {username} as Premium For {pre_month} in {bot_name}\n"
            f"Plan Expires on {pre_validity}"
        )

        await callback_query.edit_message_text(
            text=confirmation_message,
            quote=True
        )

        # Send a message to the user
        user_message = (
            f"Hey {username},\n"
            f"You are now a Premium User! in {bot_name}\n"
            f"Added you to Premium Users for {pre_month}.\n"
            f"Your plan will expire on {pre_validity}."
        )

        await client.send_message(user_id, user_message)
    except Exception as e:
        print(f"Error in bot premium: {e}")
        
@Client.on_callback_query(filters.regex('db_premium_'))
async def confirm_db_premium(client, callback_query):
    try:
        user_id = int(callback_query.data.split("_")[1])
        username = callback_query.from_user.username
        db_name = await pre_bot_name(callback_query.data)
        pre_validity, pre_month = await premium_validity(callback_query.data)
    
        # Add premium data to the database
        db.add_premium(id=user_id, db_name=db_name, file_id=None, premium_date=datetime.now(), premium_validity=pre_validity)
    
        # Send confirmation message to the user
        confirmation_message = (
            f"Successfully Added {username} as Premium For {pre_month} in {db_name}\n"
            f"Plan Expires on {pre_validity}"
        )
    
        await callback_query.edit_message_text(
            text=confirmation_message,
            quote=True
        )
    
        # Send a message to the user
        user_message = (
            f"Hey {username},\n"
            f"You are now a Premium User! in {db_name}\n"
            f"Added you to Premium Users for {pre_month}.\n"
            f"Your plan will expire on {pre_validity}."
        )
    
        await client.send_message(user_id, user_message)
    except Exception as e:
        print(f"Error in database premium: {e}")
        
@Client.on_callback_query(filters.regex('cancel_premium_'))
async def cancel_premium(client, callback_query):
    await callback_query.answer("You clicked on 'Cancel Premium'")
    
