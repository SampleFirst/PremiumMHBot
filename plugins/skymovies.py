from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup

url_list = {}

@Client.on_message(filters.command("skymovies"))
async def skymovies(client, message):
    query = message.text.split(maxsplit=1)
    if len(query) == 1:
        await message.reply_text("Please provide a movie name to search.")
        return
    query = query[1]
    search_results = await message.reply_text("Processing...")
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = [InlineKeyboardButton(movie["title"], callback_data=movie["id"])]
            keyboards.append(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboards)
        await search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        await search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')

def search_movies(query):
    movies_list = []
    website = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
    if website.status_code == 200:
        soup = BeautifulSoup(website.text, "html.parser")
        movies = soup.find_all("div", class_="L")
        for movie in movies:
            link = movie.find("a")
            if link:
                movie_details = {}
                movie_details["id"] = f"link{movies.index(movie)}"
                movie_details["title"] = link.text.strip()
                url_list[movie_details["id"]] = link['href']
                movies_list.append(movie_details)
    return movies_list

@Client.on_callback_query()
async def callback_query(client, query):
    movie_id = query.data
    download_links = get_download_links(movie_id)
    if download_links:
        keyboards = []
        for download in download_links:
            keyboard = [InlineKeyboardButton(download["title"], callback_data=download["url"])]
            keyboards.append(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboards)
        await query.message.edit_text('Download Links...', reply_markup=reply_markup)
    else:
        await query.message.edit_text('Sorry 🙏, No download links found for this movie.')

def get_download_links(movie_id):
    movie_link = url_list.get(movie_id)
    download_links = []
    if movie_link:
        website = requests.get(movie_link)
        if website.status_code == 200:
            soup = BeautifulSoup(website.text, "html.parser")
            downloads = soup.find_all("div", class_="Bolly")
            for download in downloads:
                link = download.find("a")
                if link:
                    download_details = {}
                    download_details["url"] = link['href']
                    download_details["title"] = link.text.strip()
                    download_links.append(download_details)
    return download_links
