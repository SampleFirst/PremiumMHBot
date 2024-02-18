import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from io import BytesIO


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
        await search_results.edit_text('Sorry , No Result Found!\nCheck If You Have Misspelled The Movie Name.')


@Client.on_callback_query(filters.regex('^link'))
async def skymovies_result(client, callback_query):
    query = callback_query
    movie_id = query.data
    s = get_movie(url_list[movie_id])
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    await query.message.reply_photo(photo=img, caption=f" {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Download Links :-\n\n{link}"
    await query.message.reply_text(text=caption)
    await query.answer("Sent movie links")


def search_movies(query):
    movies_list = []
    movies_details = {}
    website = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
    if website.status_code == 200:
        website = website.text
        website = BeautifulSoup(website, "html.parser")
        movies = website.find_all("div", {'class': 'movie-poster'})
        for movie in movies:
            if movie:
                movies_details["id"] = f"link{movies.index(movie)}"
                title_tag = movie.find("h4", {'class': 'movie-title'})
                if title_tag:
                    movies_details["title"] = title_tag.text.strip()
                else:
                    movies_details["title"] = "Movie Title Not Available"
                url_list[movies_details["id"]] = movie.find("a")['href']
                movies_list.append(movies_details)
                movies_details = {}
    return movies_list


def get_movie(movie_page_url):
    movie_details = {}
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        title = movie_page_link.find("div", {'class': 'mv-info-box'}).find("h2").text
        movie_details["title"] = title
        img = movie_page_link.find("div", {'class': 'mv-img'})['data-mv-poster']
        movie_details["img"] = img
        links = movie_page_link.find_all("a", {'rel': 'noopener', 'class': 'download-btn'})
        final_links = {}
        for i in links:
            final_links[i.text.strip()] = i['href']
        movie_details["links"] =
