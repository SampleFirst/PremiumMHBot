from pyrogram import Client, filters
from database.users_chats_db import db

# Define the command handlers
@Client.on_message(filters.command("update_user_attempts") & filters.private)
async def update_user_attempts_command(client, message):
    # Call the update_user_attempts method from the database
    await db.update_user_attempts(user_id=message.from_user.id)
    await message.reply("User attempts data updated successfully.")

@Client.on_message(filters.command("update_all_attempts") & filters.private)
async def update_all_attempts_command(client, message):
    # Call the update_all_attempts method from the database
    await db.update_all_attempts()
    await message.reply("All attempts data updated successfully.")

