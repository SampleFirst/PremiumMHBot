from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
from io import BytesIO

url_list = {}
api_key = "3269bf2096dd8aec64d201398176d3db93ce68db"

@Client.on_message(filters.command("skymovieshd"))
def skymovieshd(client, message):
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
    # Change this part to use skymovieshd.ngo instead of mkvcinemas.dev 
    website = requests.get(f"https://skymovieshd.ngo/search.php?search={query}&cat=All")
    if website.status_code == 200:
        website = website.text
        website = BeautifulSoup(website, "html.parser")
        movies = website.find_all("div", {'class': 'list-item'})
        for movie in movies:
            if movie:
                movies_details["id"] = f"link{movies.index(movie)}"
                movies_details["title"] = movie.find("div", {'class': 'item-head'}).text
                url_list[movies_details["id"]] = movie.find("a", {'class': 'item-head'})['href']
            movies_list.append(movies_details)
            movies_details = {}
    return movies_list

def get_movie(query):
    movie_details = {}
    movie_page_link = requests.get(f"{url_list[query]}")
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        title = movie_page_link.find("div", {'class': 'post-title'}).h1.text
        movie_details["title"] = title
        img = movie_page_link.find("div", {'class': 'post-thumbnail'})['style'].split("'")[1]
        movie_details["img"] = img
        links = movie_page_link.find_all("a", {'class': 'btn btn-success'})
        final_links = {}
        for i in links:
            url = f"https://urlshortx.com/api?api={api_key}&url={i['href']}"
            response = requests.get(url)
            link = response.json()
            final_links[f"{i.text}"] = link['shortenedUrl']
        movie_details["links"] = final_links
    return movie_details
