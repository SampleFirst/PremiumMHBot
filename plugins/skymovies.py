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


@Client.on_callback_query(filters.regex('^link'))
async def movie_result(client, callback_query):
    query = callback_query
    movie_id = query.data
    s = get_movie(url_list[movie_id])
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Download Links :-\n\n{link}"
    await query.message.reply_text(text=caption)
    await query.answer("Sent movie links")


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


def get_movie(movie_page_url):
    movie_details = {}
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        soup = BeautifulSoup(movie_page_link.text, "html.parser")
        links = soup.find_all("div", class_="Bolly")
        final_links = {}
        for i in links:
            if i.has_attr('href'):
                final_links[f"{i.text}"] = i['href']
        movie_details["links"] = final_links
    return movie_details
