import os
import re
import json
import logging
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from urllib.parse import urljoin


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



@Client.on_message(filters.command(["get_audio", "ga"]))
async def get_audio(client, message):
    try:
        book_name = message.text.split(" ")[1]
    except IndexError:
        await message.reply("Please provide a book name.")
        return

    url = f"https://www.greatideasgreatlife.com/book/{book_name}/"
    LOGGER.info(f"Fetching webpage: {url}")

    try:
        response = requests.get(url)
    except Exception as e:
        LOGGER.error(f"Error fetching webpage: {str(e)}")
        await message.reply("An error occurred while fetching the webpage.")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    audio_links = []

    for audio in soup.find_all("audio"):
        source = audio.find("source")
        if source:
            audio_links.append(source["src"])

    if not audio_links:
        await message.reply("No audio files found on the webpage.")
        return

    for link in audio_links:
        try:
            audio_response = requests.get(link)
        except Exception as e:
            LOGGER.error(f"Error fetching audio: {str(e)}")
            continue

        audio_filename = os.path.basename(link)
        audio_file = io.BytesIO(audio_response.content)

        try:
            await message.reply_audio(audio_file, filename=audio_filename)
        except FloodWait as e:
            LOGGER.warning(f"FloodWait exception: {e}")
            await asyncio.sleep(e.x)
        except RPCError as e:
            LOGGER.error(f"RPCError exception: {e}")
            continue

    await message.reply("All audio files sent.")
    
    
