import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL

@Client.on_message(filters.command('myplan'))
async def my_plan(client, message):
    user_id = message.from_user.id

    try:
        user = await db.get_user_status(user_id)

        if user:
            if user['premium_status']['premium_active']:
                plan_details = (
                    f"User ID: {user['id']}\n"
                    f"User Name: {user['name']}\n\n"
                    f"Plan: Active\n"
                    f"Bot Name: {user['premium_status']['bot_name']}\n"
                    f"Premium Date: {user['premium_status']['premium_date']}\n"
                    f"Validity: {user['premium_status']['premium_validity']}\n"
                )
                await message.reply_text(plan_details)
            else:
                # If the user doesn't have a premium plan, show buttons for options
                btn = [
                    [
                        InlineKeyboardButton("Buy Subscription", callback_data="buy_premium")
                    ],
                    [
                        InlineKeyboardButton("Cancel", callback_data="cancel"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(btn)
                sticker_message = await message.reply_sticker("CAACAgIAAxkBAAIBTGVjQbHuhOiboQsDm35brLGyLQ28AAJ-GgACglXYSXgCrotQHjibHgQ")
                await message.reply_text("**😢 You Don't Have Any Premium Subscription.\n\nCheck Out Our Premium /plans**", reply_markup=reply_markup)
                await asyncio.sleep(2)
                await sticker_message.delete()
        else:
            await message.reply_text("User not found in the database.")

    except Exception as e:
        await message.reply_text(str(e))
