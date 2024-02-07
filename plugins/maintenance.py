from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS

MAINTENANCE_MODE = False

@Client.on_message(filters.command("maintenance") & filters.user(ADMINS))
async def maintenance(client, message):
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("OFF" if MAINTENANCE_MODE else "ON", callback_data="set_mode")
        ]]
    )

    await message.reply_text("Maintenance mode options:", reply_markup=keyboard, quote=True)


@Client.on_callback_query(filters.regex(r'^set_mode') & filters.user(ADMINS))
async def maintenance_toggle(client, callback_query):
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("OFF" if MAINTENANCE_MODE else "ON", callback_data="set_mode")
        ]]
    )

    await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    await callback_query.answer("Maintenance mode is " + ("OFF" if MAINTENANCE_MODE else "ON"), show_alert=True)

@Client.on_callback_query(filters.regex(r'^maintenance_mode') & filters.user(ADMINS))
async def maintenance_mode(client, callback_query):
    await callback_query.answer(
            text="This feature is for enabling maintenance mode. If the bot is under construction, enable MAINTENANCE_MODE as True. Then, if a user sends a message or command in private or a group, show a maintenance message.",
            show_alert=True
        )

@Client.on_message(filters.text & (filters.command | filters.group | filters.private))
async def maintenance_mode_handler(client, message):
    global MAINTENANCE_MODE
    user_id = message.from_user.id

    if MAINTENANCE_MODE and user_id not in ADMINS:
        await message.reply_text("♻️ Maintenance mode is enabled.", quote=True)
        
