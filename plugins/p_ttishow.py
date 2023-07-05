from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
from datetime import timedelta, date
import pytz

from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS, MELCOW_IMG, CHNL_LNK, GRP_LNK
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired
import asyncio

@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await bot.get_chat_members_count(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            total_chat = await db.total_chat_count()
            r_j = message.from_user.mention if message.from_user else "Anonymous"
            tz = pytz.timezone('Asia/Kolkata')
            today = date.today()
            now = datetime.now(tz)
            time = now.strftime('%I:%M:%S %p')
            daily_chats = await db.daily_chats_count(today)
            log_text = script.LOG_TEXT_G.format(a=message.chat.title, b=message.chat.id, c=message.chat.username, d=total, e=total_chat, f=str(today), g=time, h=daily_chats, j=r_j, i=temp.B_LINK)
            await bot.send_message(LOG_CHANNEL, log_text)
            await db.add_chat(message.chat.id, message.chat.title, message.chat.username)
   

        if message.chat.id in temp.BANNED_CHATS:
            buttons = [
                [InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! If you want to know more about it, contact support.</b>',
                reply_markup=reply_markup,
            )

            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return

        buttons = [
            [
                InlineKeyboardButton('Support Group', url=GRP_LNK),
                InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
            ],
            [
                InlineKeyboardButton("⚡ How to Download ⚡", url="https://t.me/How_To_Verify_PMH/2")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>Thank you for adding me to {message.chat.title}!\n\nIf you have any questions or doubts about using me, please check the '⚡ How to Download ⚡' button.</b>",
            reply_markup=reply_markup
        )
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if temp.MELCOW.get('welcome') is not None:
                    try:
                        await temp.MELCOW['welcome'].delete()
                    except:
                        pass
                temp.MELCOW['welcome'] = await message.reply_photo(
                    photo=MELCOW_IMG,
                    caption=script.MELCOW_ENG.format(u.mention, message.chat.title),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('Support Group', url=GRP_LNK),
                                InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
                            ],
                            [
                                InlineKeyboardButton("⚡ How to Download ⚡", url="https://t.me/How_To_Verify_PMH/2")
                            ]
                        ]
                    ),
                    parse_mode=enums.ParseMode.HTML
                )

        if settings["auto_delete"]:
            await asyncio.sleep(600)
            await temp.MELCOW['welcome'].delete()


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat ID')
    
    chat = message.command[1]
    
    try:
        chat = int(chat)
    except:
        chat = chat
    
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await bot.send_message(
            chat_id=chat,
            text='<b>Hello friends, \nMy admin has told me to leave the group, so I am leaving! If you want to add me again, please contact my support group.</b>',
            reply_markup=reply_markup
        )

        await bot.leave_chat(chat)
        await message.reply(f"Left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'Error - {e}')


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat ID')
    
    r = message.text.split(None)
    
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided"
    
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give me a valid chat ID')
    
    cha_t = await db.get_chat(int(chat_))
    
    if not cha_t:
        return await message.reply("Chat not found in the database")
    
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason - <code>{cha_t['reason']}</code>")
    
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat successfully disabled')
    
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>Hello friends, \nMy admin has told me to leave the group, so I am leaving! If you want to add me again, please contact my support group.</b>\nReason: <code>{reason}</code>',
            reply_markup=reply_markup
        )
        
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat ID')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give me a valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat not found in the database!")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat successfully re-enabled.")


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_stats(bot, message):
    rju = await message.reply('Fetching stats...')
    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    await rju.edit(f"📊 *Statistics* 📊\n\nTotal Users: {total_users}\nTotal Chats: {total_chats}\nTotal Files: {files}\nDatabase Size: {size}\nFree Space: {free}")


@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat ID')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give me a valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("Failed to generate invite link. I do not have sufficient rights.")
    except Exception as e:
        return await message.reply(f'Error: {e}')
    await message.reply(f'Here is your Invite Link: {link.invite_link}')


@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user ID or username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user. Make sure I have interacted with them before.")
    except IndexError:
        return await message.reply("This might be a channel. Make sure it's a user.")
    except Exception as e:
        return await message.reply(f'Error: {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned.\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user ID or username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user. Make sure I have interacted with them before.")
    except IndexError:
        return await message.reply("This might be a channel. Make sure it's a user.")
    except Exception as e:
        return await message.reply(f'Error: {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    raju = await message.reply('Fetching list of users...')
    users = await db.get_all_users()
    out = "👥 Users Saved in DB 👥\n\n"
    async for user in users:
        out += f"👤 <a href='tg://user?id={user['id']}'>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += ' (Banned User)'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List of Users")


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Fetching list of chats...')
    chats = await db.get_all_chats()
    out = "🗣️ Chats Saved in DB 🗣️\n\n"
    async for chat in chats:
        out += f"👥 **Title:** `{chat['title']}`\n   **- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += ' (Disabled Chat)'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List of Chats")
        
@Client.on_message(filters.command("report") & filters.user(ADMINS))
async def get_report(client, message):
    # Calculate the start and end dates for the past 7 days
    today = date.today()
    past_days = 7  # You can adjust the number of past days as per your requirement
    start_date = today - timedelta(days=past_days-1)
    end_date = today

    report = "Report:\n\n"

    for i in range(past_days):
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')  # Convert current_date to string
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    await message.reply(report)

