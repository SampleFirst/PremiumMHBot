import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton
from pyrogram import Client, filters
import datetime
import time, os
from database.users_chats_db import db
from info import ADMINS

logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.command("mention_group_broadcast") & filters.user(ADMINS) & filters.reply)
async def mention_group_broadcast(bot, message):
    groups = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text(text='Broadcasting your messages with mentions...')
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done = 0
    failed = ""
    success = 0
    deleted = 0
    async for group in groups:
        pti, sh, ex = await broadcast_messages_group_with_mentions(bot, int(group['id']), b_msg)
        if pti:
            if sh == "Success":
                success += 1
        else:
            if sh == "deleted":
                deleted += 1
                failed += ex
                try:
                    await bot.leave_chat(int(group['id']))
                except Exception as e:
                    logging.error(f"{e} > {group['id']}")
        done += 1
        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}\nDeleted: {deleted}")
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.delete()
    try:
        await message.reply_text(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}\nDeleted: {deleted}\n\nFailed Reason: {failed}")
    except MessageTooLong:
        with open('reason.txt', 'w+') as outfile:
            outfile.write(failed)
        await message.reply_document('reason.txt', caption=f"Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}\nDeleted: {deleted}")
        os.remove("reason.txt")

async def broadcast_messages_group_with_mentions(bot, group_id, message):
    try:
        members = await bot.get_chat_members(group_id)
        mention_text = create_mention_text(members)
        await bot.send_message(group_id, f"{mention_text}\n\n{message.text}")
        return True, "Success", ""
    except (InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid) as e:
        return False, "deleted", str(e)

def create_mention_text(members):
    mention_text = ""
    for member in members:
        if member.user.username:
            mention_text += f"@{member.user.username} "
    return mention_text
