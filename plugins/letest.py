from pyrogram import Client
from bs4 import BeautifulSoup
import requests

# Function to extract movie names from HTML
def extract_movie_names(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    movie_names = []
    for div in soup.find_all('div', class_='Fmvideo'):
        movie_name = div.find('a').text.strip()
        movie_names.append(movie_name)
    return movie_names


# Command handler
@Client.on_message(filters.command(["latest"]))
def latest_movies(client, message):
    url = "https://skymovieshd.ngo/"
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        movie_names = extract_movie_names(html_content)
        if movie_names:
            movie_list = "\n".join(movie_names)
            message.reply_text(f"Latest Updated Movies:\n{movie_list}")
        else:
            message.reply_text("No latest movies found.")
    else:
        message.reply_text("Failed to fetch website content.")

