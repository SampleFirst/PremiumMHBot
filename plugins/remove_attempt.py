import time
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL

# Command to remove all active attempts
@Client.on_message(filters.command("remove_attempts", "ra") & filters.user(ADMINS))
async def remove_attempts_active(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply("You must be an admin to execute this command.")
        return
    
    # Start processing message
    processing_msg = await message.reply("Processing...")
    
    # Get total active attempts count before removal
    total_active_attempts_before = await db.total_attempts_count(att_name=None, att_type=None)
    
    # Remove all active attempts
    await db.remove_attempt_active()
    await processing_msg.edit_text(f"Removing attempts...\nTotal Active Attempts: {total_active_attempts_before - await db.total_attempts_count(att_name=None, att_type=None)}")
    await asyncio.sleep(1)
    
    # Get total active attempts count after removal
    total_active_attempts_after = await db.total_attempts_count(att_name=None, att_type=None)
    
    # Delete processing message and send update message
    await processing_msg.delete()
    update_msg = await message.reply(f"Total Active Attempts: {total_active_attempts_before} -> {total_active_attempts_after}\nTime: {time.time() - message.date}\nAll attempts have been deactivated.")
    
    # Log the action
    await client.send_message(LOG_CHANNEL, f"Admin {ADMINS} removed all active attempts.")
