import asyncio
import logging
import re
from datetime import datetime

from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import (
    ChannelInvalid,
    ChatAdminRequired,
    UsernameInvalid,
    UsernameNotModified,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from utils import temp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'❌ Your submission for indexing {chat} has been declined by our moderators.',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('⌛ Please wait until the previous process is completed.', show_alert=True)
    msg = query.message

    await query.answer('Processing...⏳', show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'✅ Your submission for indexing {chat} has been accepted by our moderators and will be added soon.',
                               reply_to_message_id=int(lst_msg_id))
    await msg.edit(
        "🔍 Starting indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('❌ Cancel', callback_data='index_cancel')]]
        )
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('❌ Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('❌ This may be a private channel/group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('❌ Invalid link specified.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'❌ Error: {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('❌ Make sure that I am an admin in the channel (if it is private).')
    if k.empty:
        return await message.reply('❌ This may be a group, and I am not an admin of the group.')

    if message.from_user.id in ADMINS:
        buttons = [
            [
                InlineKeyboardButton('✅ Yes',
                                     callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
            ],
            [
                InlineKeyboardButton('❌ Close', callback_data='close_data'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        skip_info = f"\nSkip Number: <code>{temp.CURRENT}</code>" if temp.CURRENT else ""
        return await message.reply(
            f'Do you want to index this channel/group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>{skip_info}',
            reply_markup=reply_markup)

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('❌ Make sure I am an admin in the chat and have permission to invite users.')
    else:
        link = f"@{message.forward_from_chat.username}"
    buttons = [
        [
            InlineKeyboardButton('✅ Accept Index',
                                 callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
        ],
        [
            InlineKeyboardButton('❌ Reject Index',
                                 callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    skip_info = f"\nSkip Number: <code>{temp.CURRENT}</code>" if temp.CURRENT else ""
    await bot.send_message(LOG_CHANNEL,
                           f'📥 #IndexRequest\n\nBy: {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\nInvite Link: {link}{skip_info}',
                           reply_markup=reply_markup)
    await message.reply('Thank you for the contribution! Please wait for our moderators to verify the files.')


@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply("❌ Skip number should be an integer.")
        await message.reply(f"✅ Successfully set SKIP number as {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("❌ Please provide a skip number.")


@Client.on_message(filters.command('removesetskip') & filters.user(ADMINS))
async def remove_set_skip(bot, message):
    temp.CURRENT = 0
    await message.reply("✅ Successfully removed the SKIP number.")


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    await msg.edit(f"❌ Indexing cancelled!\n\nSaved <code>{total_files}</code> files to the database.\nDuplicate files skipped: <code>{duplicate}</code>\nDeleted messages skipped: <code>{deleted}</code>\nNon-media messages skipped: <code>{no_media + unsupported}</code> (Unsupported media: `{unsupported}`)\nErrors occurred: <code>{errors}</code}")
                    break
                current += 1
                if current % 20 == 0:
                    can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                    reply = InlineKeyboardMarkup(can)
                    await msg.edit_text(
                        text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nDuplicate files skipped: <code>{duplicate}</code>\nDeleted messages skipped: <code>{deleted}</code>\nNon-media messages skipped: <code>{no_media + unsupported}</code> (Unsupported media: `{unsupported}`)\nErrors occurred: <code>{errors}</code}",
                        reply_markup=reply)
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                media.caption = message.caption
                aynav, vnay = await save_file(media)
                if aynav:
                    total_files += 1
                elif vnay == 0:
                    duplicate += 1
                elif vnay == 2:
                    errors += 1
        except Exception as e:
            logger.exception(e)
            await msg.edit(f'❌ Error: {e}')
        else:
            await msg.edit(f'✅ Successfully saved <code>{total_files}</code> files to the database!\nDuplicate files skipped: <code>{duplicate}</code>\nDeleted messages skipped: <code>{deleted}</code>\nNon-media messages skipped: <code>{no_media + unsupported}</code> (Unsupported media: `{unsupported}`)\nErrors occurred: <code>{errors}</code>')
            # Send log in LOG_CHANNEL
            channel_info = await bot.get_chat(chat)
            members_count = channel_info.members_count if channel_info.type in ("supergroup", "channel") else channel_info.subscribers_count
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"✅ Channel/Group indexed\nChat ID/Username: <code>{chat}</code>\nTotal files indexed: <code>{total_files}</code>\nMembers/Subscribers count: <code>{members_count}</code>\nDate and Time: <code>{current_datetime}</code>"
            await bot.send_message(LOG_CHANNEL, log_message)


