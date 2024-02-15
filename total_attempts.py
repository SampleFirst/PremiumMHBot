from datetime import datetime
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS 

# Define the bot names and database names
bot_names = ["Movies Bot", "Anime Bot", "Rename Bot", "YouTube Downloader Bot"]
db_names = ["Movies Database", "Anime Database", "TV Series Database", "Audio Book Database"]



# Command to show total attempts count
@Client.on_message(filters.command("total_attempts", ) & filters.user(ADMINS))
async def total_attempts_count(_, message):
    calculation_msg = await message.reply("Calculating total attempts...")
    response = ""
    for name in bot_names:
        total_count = await db.total_attempts_count(att_name=name)
        response += f"Total attempts for {name}: {total_count}\n"
    for name in db_names:
        total_count = await db.total_attempts_count(att_name=name)
        response += f"Total attempts for {name}: {total_count}\n"
    await calculation_msg.delete()
    await message.reply(response)

# Command to show daily total attempts count
@Client.on_message(filters.command("daily_attempts", ) & filters.user(ADMINS))
async def daily_attempts_count(_, message):
    calculation_msg = await message.reply("Calculating daily attempts...")
    response = ""
    today = datetime.now().date()
    for name in bot_names:
        daily_count = await db.daily_attempts_count(today, att_name=name)
        response += f"Daily attempts for {name}: {daily_count}\n"
    for name in db_names:
        daily_count = await db.daily_attempts_count(today, att_name=name)
        response += f"Daily attempts for {name}: {daily_count}\n"
    await calculation_msg.delete()
    await message.reply(response)

# Command to show monthly total attempts count
@Client.on_message(filters.command("monthly_attempts", ) & filters.user(ADMINS))
async def monthly_attempts_count(_, message):
    calculation_msg = await message.reply("Calculating monthly attempts...")
    response = ""
    month = datetime.now().month
    year = datetime.now().year
    for name in bot_names:
        monthly_count = await db.monthly_attempts_count(month, year, att_name=name)
        response += f"Monthly attempts for {name}: {monthly_count}\n"
    for name in db_names:
        monthly_count = await db.monthly_attempts_count(month, year, att_name=name)
        response += f"Monthly attempts for {name}: {monthly_count}\n"
    await calculation_msg.delete()
    await message.reply(response)

# Command to get all data
@Client.on_message(filters.command("all_attempts", ) & filters.user(ADMINS))
async def all_attempts(_, message):
    calculation_msg = await message.reply("Calculating all attempts...")
    response = "All data:\n"
    
    # Total attempts count
    response += "\nTotal Attempts Count:\n"
    for name in bot_names:
        total_count = await db.total_attempts_count(att_name=name)
        response += f"Total attempts for {name}: {total_count}\n"
    for name in db_names:
        total_count = await db.total_attempts_count(att_name=name)
        response += f"Total attempts for {name}: {total_count}\n"
    
    # Daily attempts count
    response += "\nDaily Attempts Count:\n"
    today = datetime.now().date()
    for name in bot_names:
        daily_count = await db.daily_attempts_count(today, att_name=name)
        response += f"Daily attempts for {name}: {daily_count}\n"
    for name in db_names:
        daily_count = await db.daily_attempts_count(today, att_name=name)
        response += f"Daily attempts for {name}: {daily_count}\n"
    
    # Monthly attempts count
    response += "\nMonthly Attempts Count:\n"
    month = datetime.now().month
    year = datetime.now().year
    for name in bot_names:
        monthly_count = await db.monthly_attempts_count(month, year, att_name=name)
        response += f"Monthly attempts for {name}: {monthly_count}\n"
    for name in db_names:
        monthly_count = await db.monthly_attempts_count(month, year, att_name=name)
        response += f"Monthly attempts for {name}: {monthly_count}\n"
    
    await calculation_msg.delete()
    await message.reply(response)
