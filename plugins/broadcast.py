from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages
import asyncio

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_command(_, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text('Broadcasting your messages.')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0
    async for user in users:
        result, status = await broadcast_message(int(user['id']), b_msg)
        if result:
            success += 1
        elif status == "Blocked":
            blocked += 1
        elif status == "Deleted":
            deleted += 1
        else:
            failed += 1
        done += 1
        dots = "." * (done % 4 + 1)  # Generates dots based on the progress
        await sts.edit(f"Broadcasting your messages{dots}")
        if done % 20 == 0:
            await sts.edit(f"Broadcast in progress:\n\nTotal Users: {total_users}\nCompleted: {done}/{total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
    time_taken = timedelta(seconds=int(time.time() - start_time))
    await sts.delete()
    await message.reply_text(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done}/{total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_messages_to_chats(bot, message):
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text(text='📢 Broadcasting your messages...')
    start_time = time.time()
    total_chats = await db.total_chat_count()
    done = 0
    failed = 0
    success = 0

    async for chat in chats:
        pti, sh = await broadcast_messages(int(chat['id']), b_msg)
        if pti:
            success += 1
        elif pti == False:
            if sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        await asyncio.sleep(2)
        if not done % 20:
            await sts.edit(f"📢 Broadcast in progress:\n\nTotal Chats: {total_chats}\nCompleted: {done}/{total_chats}\nSuccess: {success}\nFailed: {failed}")
    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"🎉 Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Chats: {total_chats}\nCompleted: {done}/{total_chats}\nSuccess: {success}\nFailed: {failed}")
    
