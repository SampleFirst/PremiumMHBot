# extract.py
from pyrogram import Client, filters
from bs4 import BeautifulSoup
import requests


# Define a command handler
@Client.on_message(filters.command("extract"))
async def extract_links(client, message):
    try:
        query = message.text.split(maxsplit=1)
        if len(query) == 1:
            await message.reply_text("Please provide a Webpage.")
            return
        query = query[1]
        msg = await message.reply_text("Processing...")
        response = requests.get(query)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            download_links = soup.find_all('a', href=lambda href: href and ('howblogs' in href or 'doodstream' in href))
            extracted_links = "\n".join([link['href'] for link in download_links])
            await message.reply_text(f"Extracted links:\n{extracted_links}")
        else:
            await message.reply_text("Failed to fetch webpage")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

