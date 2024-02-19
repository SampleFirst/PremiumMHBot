import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Function to extract the domain name from a URL
def get_domain(webpage):
    return webpage.split("//")[1].split("/")[0]

# Function to handle inline keyboard button presses
@Client.on_callback_query()
async def handle_callback_query(Client, callback_query):
    webpage = callback_query.data
    await callback_query.message.edit_text(
        f"Fetching HTML code for {webpage}...", reply_markup=InlineKeyboardMarkup()
    )

    try:
        response = requests.get(webpage)
        response.raise_for_status()  # Raise an exception if the request fails
        html_code = response.text

        # Replace domain_name with the actual domain extracted from the URL
        file_path = f"html_code_{domain_name}.txt"
        with open(file_path, "w") as f:
            f.write(html_code)

        await callback_query.message.edit_text(
            f"HTML code fetched successfully! Saved to: {file_path}\nFeel free to send another website link or press /start to restart."
        )

    except requests.exceptions.RequestException as e:
        await callback_query.message.edit_text(f"Error fetching HTML code: {e}")

# Function to handle messages containing URLs
@Client.on_message(filters.text & filters.regex(r"https?://\S+"))
async def handle_url_message(Client, message):
    webpage = message.text

    # Check if the domain is allowed (add any restrictions as needed)
    if get_domain(webpage) not in ("https://skymovieshd.ngo"):  # Adjust this list as required
        await message.reply_text(
            "This website is not currently allowed. Please send a link from a supported website."
        )
        return

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Fetch HTML", callback_data=webpage)]]
    )

    await message.reply_text(
        f"Detected website link: {webpage}\nPress the button below to fetch the HTML code:",
        reply_markup=keyboard,
    )

