from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup

@Client.on_message(filters.command("popular"))
async def most_popular_movies(client, message):
    url = "https://skymovieshd.ngo/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        popular_movies = soup.find('div', class_='Robiul').next_sibling.find_all('div', class_='Let')
        movies_list = '\n'.join([movie.text.strip() for movie in popular_movies])
        update.message.reply_text("Most Popular Movies:\n" + movies_list)
    else:
        update.message.reply_text("Failed to fetch data from the website.")

@Client.on_message(filters.command("letest"))
async def latest_updated_movies(client, message):
    url = "https://skymovieshd.ngo/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        latest_movies = soup.find('div', class_='Robiul').next_sibling.next_sibling.find_all('div', class_='Fmvideo')
        movies_list = '\n'.join([movie.text.strip() for movie in latest_movies])
        update.message.reply_text("Latest Updated Movies:\n" + movies_list)
    else:
        update.message.reply_text("Failed to fetch data from the website.")

