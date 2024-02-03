from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import ADMINS 
from database.users_chats_db import db

@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium(client, message):
    if message.from_user.id in ADMINS:
        if len(message.command) == 2:
            user_id = int(message.command[1])
            if db.is_user_exist(user_id):
                markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Movies Bot", callback_data="movies_bot"),
                            InlineKeyboardButton("Anime Bot", callback_data="anime_bot"),
                        ],
                        [
                            InlineKeyboardButton("Rename Bot", callback_data="rename_bot"),
                            InlineKeyboardButton("TV Series Bot", callback_data="tv_series_bot"),
                        ],
                        [
                            InlineKeyboardButton("Cancel", callback_data="cancel"),
                        ],
                    ]
                )
                await message.reply_text(f"Choose a Premium Type for {user_id}:\n\nPremium Bots:\nPremium Database:\n", reply_markup=markup)
            else:
                await message.reply_text("User not found in db")
        else:
            await message.reply_text("To add a premium user, use the following command:\n\n/addpremium {userid}")
    else:
        await message.reply_text("You are not authorized to use this command.")
