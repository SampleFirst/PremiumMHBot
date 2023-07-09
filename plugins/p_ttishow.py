from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import datetime
from datetime import date, timedelta
import time
import pytz

from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS, MELCOW_IMG, CHNL_LNK, GRP_LNK
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired
import asyncio
import logging
import os

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
    keyboard = [
        [
            InlineKeyboardButton("Yesterday", callback_data="yesterday"),
            InlineKeyboardButton("Last 7 Days", callback_data="last_7_days"),
        ],
        [
            InlineKeyboardButton("Last 30 Days", callback_data="last_30_days"),
            InlineKeyboardButton("This Year", callback_data="this_year"),
        ],
        [
            InlineKeyboardButton("Weekly", callback_data="every_7_days_total_count"),
            InlineKeyboardButton("Monthly", callback_data="every_30_days_total_count"),
        ],
        [
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    today = date.today()
    report_date = today.strftime('%d %B, %Y')
    report = f"Report for {report_date}:\n\n"

    total_users = await db.daily_users_count(today)
    total_chats = await db.daily_chats_count(today)
    report += f"{today.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    await message.reply_text(report, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("yesterday"))
async def report_yesterday(bot, callback_query):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    start_date = yesterday
    end_date = yesterday

    current_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    total_users = await db.daily_users_count(current_datetime)
    total_chats = await db.daily_chats_count(current_datetime)

    yesterday_report = f"Yesterday's Report:\n{current_datetime.strftime('%Y-%m-%d')}\n\n"
    yesterday_report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    file_name = f"Report.txt"
    with open(file_name, "w") as file:
        file.write(yesterday_report)

    caption = f"Report for {start_date.strftime('%Y-%m-%d')}"

    # Create the 'Download' button
    download_button = InlineKeyboardButton("Download", callback_data="download_report")

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Home", callback_data="report"),
                download_button,  # Add the 'Download' button to the markup
                InlineKeyboardButton("Cancel", callback_data="report_cancel")
            ],
        ]
    )

    await callback_query.message.edit_text(
        text=yesterday_report,
        reply_markup=reply_markup
    )

    os.remove(file_name)


@Client.on_callback_query(filters.regex("download_report"))
async def download_report(bot, callback_query):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    start_date = yesterday
    end_date = yesterday

    current_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    total_users = await db.daily_users_count(current_datetime)
    total_chats = await db.daily_chats_count(current_datetime)

    yesterday_report = f"Yesterday's Report:\n{current_datetime.strftime('%Y-%m-%d')}\n\n"
    yesterday_report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    file_name = f"Report.txt"
    with open(file_name, "w") as file:
        file.write(yesterday_report)

    caption = f"Report for {start_date.strftime('%Y-%m-%d')}"
    await bot.send_document(LOG_CHANNEL, document=open(file_name, "rb"), caption=caption)

    await callback_query.answer("❤Report File Send In Log Channe❤l")
    
    os.remove(file_name)
    
@Client.on_callback_query(filters.regex("last_7_days"))
async def report_last_7_days(client, callback_query):
    today = date.today()
    past_days = 7
    start_date = today - timedelta(days=6)
    end_date = today

    report = "Last 7 Days' Report:\n\n"

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
    
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Home", callback_data="report"),
                InlineKeyboardButton("Cancel", callback_data="report_cancel")
            ],
            [
                InlineKeyboardButton("Download", callback_data="download_yesterday")
            ]
        ]
    )

    await callback_query.edit_message_text(
        text=report,
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex("last_30_days"))
async def report_last_30_days(client, callback_query):
    today = date.today()
    past_days = 30
    start_date = today - timedelta(days=past_days - 1)
    end_date = today

    report = "Last 30 Days' Report:\n\n"

    page_str = callback_query.data.split("_")[-1]  # Get the page number as a string
    if page_str.isdigit():  # Check if the page number is a valid integer
        page = int(page_str)
    else:
        page = 1  # Set the default page to 1

    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    for i in range(start_index, end_index):
        if i >= past_days:
            break
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    keyboard_buttons = [
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_last_30_days")
        ]
    ]

    if page > 1:  # If it's not the first page
        keyboard_buttons.append([
            InlineKeyboardButton("<< Prev", callback_data="last_30_days_{}".format(page - 1))
        ])

    if end_index < past_days:  # If there is a next page
        keyboard_buttons.append([
            InlineKeyboardButton("Next >>", callback_data="last_30_days_{}".format(page + 1))
        ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await callback_query.edit_message_text(
        text=report,
        reply_markup=keyboard
    )


    
@Client.on_callback_query(filters.regex("this_year"))
async def report_this_year(client, callback_query):
    # Calculate the start and end dates for this year
    today = date.today()
    start_date = date(today.year, 1, 1)
    end_date = today

    report = "This Year's Report:\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date
    count = 0

    while current_date <= end_date:
        if count >= start_index:
            current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
            total_users = await db.daily_users_count(current_datetime)
            total_chats = await db.daily_chats_count(current_datetime)
            report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=1)
        count += 1

    keyboard_buttons = [
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_this_year")
        ]
    ]

    if count > end_index:  # If there is a next page
        keyboard_buttons.append([
            InlineKeyboardButton("Next >>", callback_data="this_year_{}".format(page + 1))
        ])

    if page > 1:  # If it's not the first page
        keyboard_buttons.append([
            InlineKeyboardButton("<< Prev", callback_data="this_year_{}".format(page - 1))
        ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await callback_query.edit_message_text(
        text=report,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("every_7_days_total_count"))
async def report_every_7_days_total_count(client, callback_query):
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today

    report = "Weekly Report (Last 12 Months):\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date + timedelta(days=start_index * 7)
    for i in range(start_index, end_index):
        if current_date > end_date:
            break
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=7)

    keyboard_buttons = [
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_every_7_days_total_count")
        ]
    ]

    if current_date <= end_date:  # If there is a next page
        keyboard_buttons.append([
            InlineKeyboardButton("Next >>", callback_data="every_7_days_total_count_{}".format(page + 1))
        ])

    if page > 1:  # If it's not the first page
        keyboard_buttons.append([
            InlineKeyboardButton("<< Prev", callback_data="every_7_days_total_count_{}".format(page - 1))
        ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await callback_query.edit_message_text(
        text=report,
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex("every_30_days_total_count"))
async def report_every_30_days_total_count(client, callback_query):
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today

    report = "Monthly Report: (Last 12 Months):\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date + timedelta(days=start_index * 30)
    for i in range(start_index, end_index):
        if current_date > end_date:
            break
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=30)

    keyboard_buttons = [
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_every_30_days_total_count")
        ]
    ]

    if current_date <= end_date:  # If there is a next page
        keyboard_buttons.append([
            InlineKeyboardButton("Next >>", callback_data="every_30_days_total_count_{}".format(page + 1))
        ])

    if page > 1:  # If it's not the first page
        keyboard_buttons.append([
            InlineKeyboardButton("<< Prev", callback_data="every_30_days_total_count_{}".format(page - 1))
        ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await callback_query.edit_message_text(
        text=report,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("cancel"))
async def cancel_report(client, callback_query):
    # Handle cancel button action
    await callback_query.edit_message_text("Report canceled.")

        





@Client.on_callback_query(filters.regex("download_last_7_days"))
async def download_report_last_7_days(client, callback_query):
    today = date.today()
    past_days = 7
    start_date = today - timedelta(days=6)
    end_date = today

    report = "Last 7 Days' Report:\n\n"

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    file_name = "report_last_7_days.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_last_30_days"))
async def download_report_last_30_days(client, callback_query):
    today = date.today()
    past_days = 30
    start_date = today - timedelta(days=past_days - 1)
    end_date = today

    report = "Last 30 Days' Report:\n\n"

    for i in range(past_days):
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    file_name = "report_last_30_days.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_this_year"))
async def download_report_this_year(client, callback_query):
    today = date.today()
    start_date = date(today.year, 1, 1)
    end_date = today

    report = "This Year's Report:\n\n"

    current_date = start_date
    while current_date <= end_date:
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=1)

    file_name = "report_this_year.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_every_7_days_total_count"))
async def download_report_every_7_days_total_count(client, callback_query):
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today

    report = "Weekly Report (Last 12 Months):\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date + timedelta(days=start_index * 7)
    for i in range(start_index, end_index):
        if current_date > end_date:
            break
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=7)

    file_name = "weekly_report.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_every_30_days_total_count"))
async def download_report_every_30_days_total_count(client, callback_query):
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today

    report = "Monthly Report (Last 12 Months):\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date + timedelta(days=start_index * 30)
    for i in range(start_index, end_index):
        if current_date > end_date:
            break
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=30)

    file_name = "monthly_report.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)
    

