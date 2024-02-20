import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters


@Client.on_message(filters.command("latest"))
async def latest_movies(client, message):
    await message.reply_text("Fetching latest movies...")
    url = "https://skymovieshd.ngo/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")
        movies = soup.find_all('div', class_='Fmvideo')
        movie_list = ""
        for movie in movies:
            movie_list += f"{movie.text} - {url}{movie['href']}\n"

        await message.reply_text(f"Latest Updated Movies:\n{movie_list}")

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

