from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests


@Client.on_message(filters.command("showhtml"))
async def show_html(client, message):
    try:
        url = message.text.split(" ", 1)[1]  # Extract the URL from the message
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request fails
        html_code = response.text

        await message.reply_text(f"HTML code for {url}:\n`html\n{html_code}\n`")
    except requests.exceptions.RequestException as e:
        await message.reply_text(f"Error fetching HTML code: {e}")
