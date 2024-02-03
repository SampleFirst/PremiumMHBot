import asyncio
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS


@Client.on_message(filters.command("userupdate") & filters.user(ADMINS))
async def user_update(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply("You don't have permission to use this command.")
        return

    args = message.get_args().split()
    if len(args) != 1:
        await message.reply("Usage: /latestupdate <user_id>")
        return

    user_id = int(args[0])
    if user_update = await db.get_latest_user_update(user_id):
        await message.reply(f"Latest update for user {user_id}:\n{user_update}")
    else:
        await message.reply(f"No user found with ID {user_id}")


@Client.on_message(filters.command("myupdate"))
async def my_update(client, message):
    if user_update = await db.get_latest_user_update(message.from_user.id):
        await message.reply(f"Your latest update:\n{user_update}")
    else:
        await message.reply("No update data found for your user ID.")
