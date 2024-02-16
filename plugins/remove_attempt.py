from pyrogram import Client, filters



@Client.on_message(filters.command("remove_all_attempts"))
async def remove_all_attempts(client, message):
    # Check if user is admin or has permission to execute this command
    
    # Remove all active attempts
    await db.remove_all_active_attempts()
    
    await message.reply_text("All active attempts have been removed.")

