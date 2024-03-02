import os
import io
import logging
import asyncio
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command(["get_audio", "ga"]))
async def get_audio(client, message):
    try:
        book_name = message.command[1]
    except IndexError:
        await message.reply("Please provide a book name.")
        return

    website_url = f"https://www.greatideasgreatlife.com/book/{book_name.replace(' ', '-')}/"
    logger.info(f"Fetching webpage: {website_url}")
    
    website = requests.get(website_url)
    if website.status_code != 200:
        await message.reply("Failed to fetch the webpage.")
        return
    
    website = BeautifulSoup(website.text, "html.parser")
    audio_links = []

    for audio in website.find_all("audio"):
        source = audio.find("source")
        if source:
            audio_links.append(urljoin(website_url, source["src"]))

    if not audio_links:
        await message.reply("No audio files found on the webpage.")
        return

    for audio_link in audio_links:
        try:
            audio_filename = os.path.basename(audio_link)
            audio_file = io.BytesIO(requests.get(audio_link).content)
            await message.reply_audio(audio_file, filename=audio_filename)
        except FloodWait as e:
            logger.warning(f"FloodWait exception: {e}")
            await asyncio.sleep(e.x)
        except RPCError as e:
            logger.error(f"RPCError exception: {e}")
            continue

    await message.reply("All audio files sent.")
