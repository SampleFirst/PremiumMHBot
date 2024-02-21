from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
from io import BytesIO

len_list = {}


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


@Client.on_callback_query(filters.regex('^len'))
async def movie_result(client, callback_query):
    query = callback_query
    movie_id = query.data
    s = get_movie(len_list[movie_id])
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Download Links :-\n\n{link}"
    await query.answer("Sent movie links")
    await query.message.reply_text(text=caption)
    

def search_movies(query):
    movies_list = []
    website = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
    if website.status_code == 200:
        website = website.text
        website = BeautifulSoup(website, "html.parser")
        movies = website.find_all("div", {'class': 'Bolly'})
        for movie in movies:
            movie_details = {}
            movie_link = movie.find("a", href=True)
            if movie_link:
                movie_details["id"] = f"len{movies.index(movie)}"
                movie_details["title"] = movie_link.find("span", {'class': 'mli-info'}).text
                len_list[movie_details["id"]] = movie_link['href']
                movies_list.append(movie_details)
    return movies_list


def get_movie(movie_page_url):
    movie_details = {}
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        
        # Extracting Watch Online link
        watch_online_link = movie_page_link.find("a", href=True, text="WATCH ONLINE")
        if watch_online_link:
            movie_details["Watch Online"] = watch_online_link['href']
        
        # Extracting Download links
        download_links = movie_page_link.find("div", {'class': 'Bolly'}).find_all("a", href=True)
        final_links = {}
        for download in download_links:
            final_links[download.text.strip()] = download['href']
        movie_details["Download Links"] = final_links
    return movie_details


