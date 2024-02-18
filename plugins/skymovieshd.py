import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Command to search for movies
@Client.on_message(filters.command("skymovies"))
async def search_command(client, message):
    # Extract query from command
    query = message.text.split(" ", 1)[1]
    link = f"https://skymovieshd.ngo/search.php?search={query}&cat=All"

    try:
        response = requests.get(link)
        response.raise_for_status()  

        soup = BeautifulSoup(response.content, "html.parser")
        file_links = [item.a["href"] for item in soup.find_all("div", class_="item") if item.a]

        buttons = []
        for file_link in file_links:
            buttons.append([InlineKeyboardButton(text=file_link.split("/")[-1], callback_data=file_link)])

        await message.reply("Choose a file:", reply_markup=InlineKeyboardMarkup(buttons))

    except requests.exceptions.RequestException as e:
        await message.reply(f"Error fetching results: {e}")

# Callback query handler
@Client.on_callback_query()
async def callback_query_handler(client, callback_query):
    file_link = callback_query.data

    try:
        response = requests.get(file_link)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        drive_link_element = soup.find("a", text="Google Drive Direct Links")
        drive_link = drive_link_element["href"] if drive_link_element else None

        if drive_link:
            try:
                drive_response = requests.get(drive_link)
                drive_response.raise_for_status()

                drive_soup = BeautifulSoup(drive_response.content, "html.parser")
                download_links = [item.a["href"] for item in drive_soup.find_all("div", class_="download") if item.a]

                buttons = []
                for download_link in download_links:
                    buttons.append([InlineKeyboardButton(text="Download", url=download_link)])

                await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

            except requests.exceptions.RequestException as e:
                await callback_query.answer(f"Error fetching drive links: {e}")
        else:
            await callback_query.answer("Drive links not found.")

    except requests.exceptions.RequestException as e:
        await callback_query.answer(f"Error opening file: {e}")

