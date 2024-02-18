from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def extract_movies(query):
    url = f"https://skymovieshd.ngo/search.php?search={query}&cat=All"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find_all('div', class_='movie-title')
    movies = []
    for result in results:
        title = result.find('a').text.strip()
        link = result.find('a')['href']
        movies.append({'title': title, 'link': link})
    return movies


@Client.on_message(filters.command(['search_movies']))
def search_movies(client, message):
    query = message.text.split(' ', 1)[1]
    movies = extract_movies(query)
    if movies:
        buttons = [
            [client.build_inline_keyboard_button(movie['title'], url=movie['link'])] 
            for movie in movies
        ]
        message.reply_text("Here are the search results:", reply_markup=Client.inline_keyboards(buttons))
    else:
        message.reply_text("No movies found for your query.")


