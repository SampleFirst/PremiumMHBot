import logging
import asyncio
import datetime
import os
import time

from pyrogram import Client, filters
from pyrogram.errors import (
    InputUserDeactivated,
    UserNotParticipant,
    FloodWait,
    UserIsBlocked,
    PeerIdInvalid,
)
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.types import InlineKeyboardButton, Message

from database.users_chats_db import db
from info import ADMINS


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text('Broadcasting your messages...')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    async for user in users:
        try:
            await broadcast_messages(int(user['id']), b_msg)
            done += 1
        except PeerIdInvalid:
            await db.delete_user(int(user['id']))
            logging.info(f"{user['id']} - PeerIdInvalid")
            failed += 1
        except Exception as e:
            logging.error(f"{user['id']} - {str(e)}")
            failed += 1

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(
            f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {done - blocked - deleted - failed}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}\n\nTime Elapsed: {time_taken}"
        )
    await sts.delete()
    await bot.send_message(
        message.chat.id,
        f"Broadcast Completed:\nCompleted in {time_taken}.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {done - blocked - deleted - failed}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}",
    )


@Client.on_message(filters.command("clear_junk") & filters.user(ADMINS))
async def remove_junkuser__db(bot, message):
    users = await db.get_all_users()
    b_msg = message
    sts = await message.reply_text('In progress...')
    start_time = time.time()
    total_users = await db.total_users_count()
    blocked = 0
    deleted = 0
    failed = 0
    done = 0
    async for user in users:
        try:
            await clear_junk(int(user['id']), b_msg)
            done += 1
        except PeerIdInvalid:
            await db.delete_user(int(user['id']))
            logging.info(f"{user['id']} - PeerIdInvalid")
            failed += 1
        except Exception as e:
            logging.error(f"{user['id']} - {str(e)}")
            failed += 1

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(
            f"In progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}\n\nTime Elapsed: {time_taken}"
        )
    await sts.delete()
    await bot.send_message(
        message.chat.id,
        f"Completed:\nCompleted in {time_taken}.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}",
    )


@Client.on_message(filters.command("group_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_group(bot, message):
    groups = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text(text='Broadcasting your messages to groups...')
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done = 0
    failed = ""
    success = 0
    deleted = 0
    async for group in groups:
        try:
            await broadcast_messages_group(int(group['id']), b_msg)
            done += 1
            success += 1
        except PeerIdInvalid:
            await db.delete_chat(int(group['id']))
            logging.info(f"{group['id']} - PeerIdInvalid")
            deleted += 1
            failed += f"Group ID: {group['id']}\n"
        except Exception as e:
            logging.error(f"{group['id']} - {str(e)}")
            failed += f"Group ID: {group['id']}\n{str(e)}\n"

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(
            f"Broadcast in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}\nDeleted: {deleted}\n\nFailed Reason: {failed}\n\nTime Elapsed: {time_taken}"
        )
    await sts.delete()
    if failed:
        with open('reason.txt', 'w+') as outfile:
            outfile.write(failed)
        await message.reply_document(
            'reason.txt',
            caption=f"Completed:\nCompleted in {time_taken}.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}\nDeleted: {deleted}",
        )
        os.remove("reason.txt")
    else:
        await message.reply_text(
            f"Broadcast Completed:\nCompleted in {time_taken}.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}\nDeleted: {deleted}\n\nFailed Reason: {failed}",
        )


@Client.on_message(filters.command(["junk_group", "clear_junk_group"]) & filters.user(ADMINS))
async def junk_clear_group(bot, message):
    groups = await db.get_all_chats()
    b_msg = message
    sts = await message.reply_text(text='In progress...')
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done = 0
    failed = ""
    deleted = 0
    async for group in groups:
        try:
            await junk_group(int(group['id']), b_msg)
            done += 1
        except PeerIdInvalid:
            await db.delete_chat(int(group['id']))
            logging.info(f"{group['id']} - PeerIdInvalid")
            deleted += 1
            failed += f"Group ID: {group['id']}\n"
        except Exception as e:
            logging.error(f"{group['id']} - {str(e)}")
            failed += f"Group ID: {group['id']}\n{str(e)}\n"

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(
            f"In progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}\n\nFailed Reason: {failed}\n\nTime Elapsed: {time_taken}"
        )
    await sts.delete()
    if failed:
        with open('junk.txt', 'w+') as outfile:
            outfile.write(failed)
        await message.reply_document(
            'junk.txt',
            caption=f"Completed:\nCompleted in {time_taken}.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}",
        )
        os.remove("junk.txt")
    else:
        await bot.send_message(
            message.chat.id,
            f"Completed:\nCompleted in {time_taken}.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}\n\nFailed Reason: {failed}",
        )


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
        pti, sh, ex = await broadcast_messages_group_with_mentions(int(group['id']), b_msg)
        if pti == True:
            if sh == "Success":
                success += 1
        elif pti == False:
            if sh == "deleted":
                deleted += 1
                failed += ex
                try:
                    await bot.leave_chat(int(group['id']))
                except Exception as e:
                    print(f"{e} > {group['id']}")
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

async def broadcast_messages_group_with_mentions(group_id, message):
    try:
        group = await bot.get_chat(group_id)
        mention_text = create_mention_text(group)
        await bot.send_message(group_id, f"{mention_text}\n\n{message.text}")
        return True, "Success", ""
    except (InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid) as e:
        return False, "deleted", str(e)

def create_mention_text(group):
    mention_text = ""
    for member in group.members:
        if member.user.username:
            mention_text += f"@{member.user.username} "
    return mention_text

async def broadcast_messages_group(chat_id, message):
    try:
        await message.copy(chat_id=chat_id)
    except PeerIdInvalid:
        raise PeerIdInvalid
    except Exception as e:
        raise Exception(str(e))


async def junk_group(chat_id, message):
    try:
        kk = await message.copy(chat_id=chat_id)
        await kk.delete(True)
    except PeerIdInvalid:
        raise PeerIdInvalid
    except Exception as e:
        raise Exception(str(e))


async def clear_junk(user_id, message):
    try:
        key = await message.copy(chat_id=user_id)
        await key.delete(True)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Removed from Database, since the account is deleted.")
    except UserIsBlocked:
        logging.info(f"{user_id} - Blocked the bot.")
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
    except Exception as e:
        raise Exception(str(e))


async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Removed from Database, since the account is deleted.")
    except UserIsBlocked:
        logging.info(f"{user_id} - Blocked the bot.")
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
    except Exception as e:
        raise Exception(str(e))
