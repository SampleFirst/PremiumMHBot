# maintenance.py 
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
from database.users_chats_db import db

@Client.on_message(filters.command("mode") & filters.user(ADMINS))
async def maintenance(client, message):
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="mode_info"),
            InlineKeyboardButton("ON" if await db.get_maintenance_mode() else "OFF", callback_data="set_mode")
        ]]
    )

    await message.reply_text("Maintenance mode options:", reply_markup=keyboard, quote=True)


@Client.on_callback_query(filters.regex(r'^set_mode') & filters.user(ADMINS))
async def set_maintenance(client, callback_query):
    current_mode = await db.get_maintenance_mode()
    await db.set_maintenance_mode(not current_mode)

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="mode_info"),
            InlineKeyboardButton("ON" if await db.get_maintenance_mode() else "OFF", callback_data="set_mode")
        ]]
    )

    await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    await callback_query.answer("Maintenance mode is " + ("ON" if await db.get_maintenance_mode() else "OFF"), show_alert=True)

@Client.on_callback_query(filters.regex(r'^mode_info') & filters.user(ADMINS))
async def maintenance_mode(client, callback_query):
    await callback_query.answer(
            text="This feature is for enabling maintenance mode. If the bot is under construction, enable MAINTENANCE_MODE as True. Then, if a user sends a message or command in private or a group, show a maintenance message.",
            show_alert=True
        )

@Client.on_message(filters.text & filters.command)
async def maintenance_mode_handler(client, message):
    if await db.get_maintenance_mode() and message.from_user.id not in ADMINS:
        await message.reply_text("♻️ Maintenance mode is enabled.", quote=True)
