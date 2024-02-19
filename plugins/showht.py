import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

logging.basicConfig(level=logging.ERROR)

# Dictionary to store URL mappings
url_mapping = {}

# Function to extract the domain name from a URL
def get_domain(webpage):
    return webpage.split("//")[1].split("/")[0]

# Function to generate a unique identifier for a URL
def generate_identifier(webpage):
    return hash(webpage)

# Function to handle inline keyboard button presses
@Client.on_callback_query(filters.regex('webpage'))
async def handle_webpage_query(client, callback_query):
    try:
        identifier = callback_query.data
        webpage = url_mapping.get(identifier)

        await callback_query.message.edit_text(
            f"Fetching HTML code for {webpage}...")
    
        response = requests.get(webpage)
        response.raise_for_status()  # Raise an exception if the request fails
        html_code = response.text

        # Replace domain_name with the actual domain extracted from the URL
        domain_name = get_domain(webpage)
        file_path = f"html_code_{domain_name}.txt"
        with open(file_path, "w") as f:
            f.write(html_code)

        await callback_query.message.edit_text(
            f"HTML code fetched successfully! Saved to: {file_path}")
    except Exception as e:
        print(e)
        await callback_query.message.edit_text(f"Error fetching HTML code: {e}")

# Function to handle messages containing URLs
@Client.on_message(filters.text & filters.regex(r"https?://\S+"))
async def handle_url_message(client, message):
    webpage = message.text

    # Check if the domain is allowed (add any restrictions as needed)
    if get_domain(webpage) not in ("skymovieshd.ngo"):  # Adjust this list as required
        await message.reply_text(
            "This website is not currently allowed. Please send a link from a supported website."
        )
        return

    identifier = generate_identifier(webpage)
    url_mapping[identifier] = webpage

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Fetch HTML", callback_data=identifier)
            ]
        ]
    )

    await message.reply_text(
        f"Detected website link: {webpage}\nPress the button below to fetch the HTML code:",
        reply_markup=keyboard,
    )
