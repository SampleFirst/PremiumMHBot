# premium.py

import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL


logger = logging.getLogger(__name__)


@Client.on_message(filters.command('totalpremium'))
async def total_premium_users(bot, message):
    """Get total premium users data (only for ADMINS)"""
    try:
        if message.from_user.id in ADMINS:
            total_premium_users = await db.total_premium()
            total_active_premium_users = await db.total_active_premium()
            today_premium_users = await db.total_premium_sorted(interval='daily')
            today_active_premium_users = await db.total_active_premium_sorted(interval='daily')
            month_premium_users = await db.total_premium_sorted(interval='monthly')
            month_active_premium_users = await db.total_active_premium_sorted(interval='monthly')
            year_premium_users = await db.total_premium_sorted(interval='yearly')
            year_active_premium_users = await db.total_active_premium_sorted(interval='yearly')

            response = f"Total Premium Users:\n\n{total_premium_users}\nTotal Active Premium Users: {total_active_premium_users}"
            response += f"\nToday's Premium Users: {today_premium_users}\nToday's Active Premium Users: {today_active_premium_users}"
            response += f"\nThis Month's Premium Users: {month_premium_users}\nThis Month's Active Premium Users: {month_active_premium_users}"
            response += f"\nThis Year's Premium Users: {year_premium_users}\nThis Year's Active Premium Users: {year_active_premium_users}"
            
            await message.reply_text(response)
        else:
            await message.reply_text("This command only for an ADMINS.")
    except Exception as e:
        await message.reply(str(e))
        
@Client.on_message(filters.command('todaypremium') & filters.user(ADMINS))
async def today_premium_users(bot, message):
    """Get total premium users for today (only for ADMINS)"""
    try:
        if message.from_user.id in ADMINS:
            today_premium_users = await db.total_premium_sorted(interval='daily')
            today_active_premium_users = await db.total_active_premium_sorted(interval='daily')
    
            response = f"Today's Premium Users: {today_premium_users}\nToday's Active Premium Users: {today_active_premium_users}"
            
            await message.reply_text(response)
        else:
            await message.reply_text("This command only for an ADMINS.")
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('monthpremium') & filters.user(ADMINS))
async def month_premium_users(bot, message):
    """Get total premium users for this month (only for ADMINS)"""
    try:
        if message.from_user.id in ADMINS:
            month_premium_users = await db.total_premium_sorted(interval='monthly')
            month_active_premium_users = await db.total_active_premium_sorted(interval='monthly')
    
            response = f"This Month's Premium Users: {month_premium_users}\nThis Month's Active Premium Users: {month_active_premium_users}"
            
            await message.reply_text(response)
        else:
            await message.reply_text("This command only for an ADMINS.")
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('yearpremium') & filters.user(ADMINS))
async def year_premium_users(bot, message):
    """Get total premium users for this year (only for ADMINS)"""
    try:
        if message.from_user.id in ADMINS:
            year_premium_users = await db.total_premium_sorted(interval='yearly')
            year_active_premium_users = await db.total_active_premium_sorted(interval='yearly')
    
            response = f"This Year's Premium Users: {year_premium_users}\nThis Year's Active Premium Users: {year_active_premium_users}"
            
            await message.reply_text(response)
        else:
            await message.reply_text("This command only for an ADMINS.")
    except Exception as e:
        await message.reply(str(e))
        
