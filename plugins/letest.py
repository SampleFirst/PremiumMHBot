import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters


@Client.on_message(filters.command("popular"))
async def popular_movies(client, message):
    msg = await message.reply_text("Fetching popular movies...")
    url = "https://skymovieshd.ngo/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")
        movies = soup.find_all('div', class_='Let')
        movie_list = ""
        for movie in movies:
            movie_list += f"{movie.text}\n\n"

        await msg.delete()
        await message.reply_text(f"Most Popular Movies:\n\n<code>{movie_list}</code>")

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


@Client.on_message(filters.command("latest"))
async def latest_movies(client, message):
    msg = await message.reply_text("Fetching latest movies...")
    url = "https://skymovieshd.ngo/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extracting only the relevant movie information
        movies = soup.find_all('div', class_='Fmvideo')[3:]  # Start from the fourth Fmvideo div
        movie_list = ""
        for movie in movies:
            movie_list += f"{movie.text}\n\n"
        
        await msg.delete()
        await message.reply_text(f"Latest Updated Movies:\n\n<code>{movie_list}</code>")

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
