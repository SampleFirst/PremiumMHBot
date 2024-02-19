import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

logging.basicConfig(level=logging.ERROR)

# Function to extract the domain name from a URL
def get_domain(webpage):
    return webpage.split("//")[1].split("/")[0]


# Function to handle messages containing URLs
@Client.on_message(filters.text & filters.regex(r"https?://\S+"))
async def handle_url_message(client, message):
    webpage = message.text

    # Check if the domain is allowed
    if get_domain(webpage):
        return

    try:
        await message.reply_text(f"Fetching HTML code for {webpage}...")

        response = requests.get(webpage)
        response.raise_for_status()  # Raise an exception if the request fails
        html_code = response.text

        domain_name = get_domain(webpage)
        file_path = f"{domain_name}.html"

        # Create the text file and send it to the user
        with open(file_path, "w") as f:
            f.write(html_code)

        await message.reply_document(document=file_path)  # Send the text file as a document

        await message.edit_text(f"HTML code sent successfully!")
    except Exception as e:
        print(e)
        await message.edit_text(f"Error fetching HTML code: {e}")

