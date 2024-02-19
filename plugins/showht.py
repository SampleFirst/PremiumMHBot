import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from info import ADMINS, LOG_CHANNEL

logging.basicConfig(level=logging.ERROR)

# Function to extract the domain name from a URL
def get_domain(webpage):
    return webpage.split("//")[1].split("/")[0]

# Function to handle messages containing URLs
@Client.on_message(filters.command("gethtml") & filters.private)
async def get_html(client, message):
    try:
        # Check if the command has the URL parameter
        if len(message.command) != 2:
            await message.reply_text("Please provide a URL.")
            return

        webpage = message.text.split()[1]

        msg = await message.reply_text(f"Fetching HTML code for {webpage}...")

        response = requests.get(webpage)
        response.raise_for_status()  # Raise an exception if the request fails
        html_code = response.text

        domain_name = get_domain(webpage)
        file_path = f"{domain_name}.html"

        caption = f"HTML code sent successfully!\n\nDomain Name: {domain_name}\n\nWebsite: {webpage}"

        # Create the text file and send it to the user
        with open(file_path, "w") as f:
            f.write(html_code)

        # Delete the temporary message
        await msg.delete()
        
        await message.reply_document(
            document=file_path,
            caption=caption
        )

        await client.send_document(
            chat_id=LOG_CHANNEL,
            document=file_path,
            caption=caption
        )

        # Delete the temporary file
        os.remove(file_path)

    except Exception as e:
        await message.reply_text(f"Error fetching HTML code: {e}")

