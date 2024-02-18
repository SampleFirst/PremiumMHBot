from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
from io import BytesIO

url_list = {}
api_key = "3269bf2096dd8aec64d201398176d3db93ce68db"

@Client.on_message(filters.command("skymovies"))
def find_skymovie(client, message):
    query = message.text.split(maxsplit=1)
    if len(query) == 1:
        message.reply_text("Please provide a movie name to search.")
        return
    query = query[1]
    search_results = message.reply_text("Processing...")
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')

@Client.on_callback_query()
def movie_result(client, callback_query):
    query = callback_query
    s = get_movie(query.data)
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Fast Download Links :-\n\n{link}"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x+4095])
    else:
        query.message.reply_text(text=caption)

def search_movies(query):
    movies_list = []
    movies_details = {}
    response = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        movies = soup.find_all("div", class_="movie-box")
        for movie in movies:
            title = movie.find("a", class_="movie-title").text.strip()
            download_link = movie.find("a", class_="download-link")["href"]
            movies_list.append({
                "title": title,
                "id": download_link,  # Use the download link as the movie ID
            })
    return movies_list

def get_movie(query):
    movie_details = {}
    movie_page_link = requests.get(f"{url_list[query]}")
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
        movie_details["title"] = title
        img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
        movie_details["img"] = img
        links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
        final_links = {}
        for i in links:
            url = f"https://urlshortx.com/api?api={api_key}&url={i['href']}"
            response = requests.get(url)
            link = response.json()
            final_links[f"{i.text}"] = link['shortenedUrl']
        movie_details["links"] = final_links
    return movie_details
