from pyrogram import Client, filters
from bs4 import BeautifulSoup
import requests

# Function to scrape the latest updated movies list
def get_latest_movies():
    url = "https://skymovieshd.ngo/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    movies = soup.find_all('div', class_='Fmvideo')
    latest_movies = []
    for movie in movies:
        title = movie.find('a').text.strip()
        link = url + movie.find('a')['href']
        latest_movies.append((title, link))
    return latest_movies


@Client.on_message(filters.command("latest"))
async def latest_movies(client, message):
    movies = get_latest_movies()
    if movies:
        response = "Latest Updated Movies:\n\n"
        for title, link in movies:
            response += f"{title}\n{link}\n\n"
        await message.reply_text(response)
    else:
        await message.reply_text("Sorry, couldn't fetch the latest movies at the moment.")

