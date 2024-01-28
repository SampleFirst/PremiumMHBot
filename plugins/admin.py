import os
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

@Client.on_message(filters.private & filters.command("warn"))
async def warn(client, message):
    if user_id in ADMINS:
        if len(message.command) >= 3:
            try:
                user_id = message.text.split(' ', 2)[1]
                reason = message.text.split(' ', 2)[2]
                await message.reply_text("User Notified Successfully")
                await client.send_message(chat_id=int(user_id), text=reason)
            except:
                await message.reply_text("User Not Notified Successfully 😔")
    else:
        await client.send_message(message.chat.id, "Unauthorized access")

@Client.on_message(filters.private & filters.command("addpremium"))
async def buypremium(bot, message):
    if user_id in ADMINS:
        buttons = [
            InlineKeyboardButton("1 Month", callback_data="vip1"),
            InlineKeyboardButton("2 Month", callback_data="vip2"),
            InlineKeyboardButton("3 Month", callback_data="vip3")
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            caption="Select Plan...\n\nPlan 1 = 99₹\n\nPlan 2 = 149₹\n\nPlan 3 = 249",
            reply_markup=reply_markup,
            quote=True
        )
    else:
        await client.send_message(message.chat.id, "Unauthorized access")

@Client.on_callback_query(filters.regex('vip1'))
async def vip1(bot, update):
    id = update.message.reply_to_message.text.split("/addpremium")
    user_id = id[1].replace(" ", "")

    await update.message.edit_text("Added successfully To Premium ")
    await bot.send_message(user_id, "Hey You're Upgraded To VIP 1 check your plan here /myplan")
    await bot.send_message(LOG_CHANNEL, "Added successfully To Premium ")

@Client.on_callback_query(filters.regex('vip2'))
async def vip2(bot, update):
    id = update.message.reply_to_message.text.split("/addpremium")
    user_id = id[1].replace(" ", "")

    await update.message.edit_text("Added successfully To Premium ")
    await bot.send_message(user_id, "Hey You're Upgraded To VIP 2 check your plan here /myplan")
    await bot.send_message(LOG_CHANNEL, "Added successfully To Premium ")

@Client.on_callback_query(filters.regex('vip3'))
async def vip3(bot, update):
    id = update.message.reply_to_message.text.split("/addpremium")
    user_id = id[1].replace(" ", "")

    await update.message.edit_text("Added successfully To Premium ")
    await bot.send_message(user_id, "Hey You're Upgraded To VIP 3 check your plan here /myplan")
    await bot.send_message(LOG_CHANNEL, "Added successfully To Premium ")
