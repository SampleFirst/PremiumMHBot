import asyncio
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from info import LOG_CHANNEL 

@Client.on_message(filters.command("popular"))
async def popular_movies(client, message):
    msg = await message.reply_text("Fetching popular movies...", quote=True)
    url = "https://skymovieshd.ngo/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")
        movies = soup.find_all('div', class_='Let')
        movie_list = ""
        for movie in movies:
            movie_list += f"<code>{movie.text.strip()}</code>\n\n"  # Remove leading and trailing whitespace

        await msg.delete()
        main = await message.reply_text(f"Most Popular Movies:\n\n{movie_list}", quote=True)
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"Latest Updated Movies:\n\n{movie_list}"
        )
        
        await asyncio.sleep(15)
        await main.delete()
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


@Client.on_message(filters.command("latest"))
async def latest_movies(client, message):
    msg = await message.reply_text("Fetching latest movies...", quote=True)
    url = "https://skymovieshd.ngo/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extracting only the relevant movie information
        movies = soup.find_all('div', class_='Fmvideo')[3:]  # Start from the fourth Fmvideo div
        movie_list = ""
        for movie in movies:
            movie_list += f"<code>{movie.text.strip()}</code>\n\n"  # Remove leading and trailing whitespace
        
        await msg.delete()
        main = await message.reply_text(f"Latest Updated Movies:\n\n{movie_list}", quote=True)
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"Latest Updated Movies:\n\n{movie_list}"
        )
        
        await asyncio.sleep(15)
        await main.delete()
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
